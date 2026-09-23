"""Minimal client for OpenAI-compatible /chat/completions and /images/generations.
Every call takes the calling agent's AgentConfig, so each role can use its own
provider, model and settings, and an optional `log` callable (usage.CallLogger)
that receives the full request and response of every call, failed ones included."""
import base64
import http.client
import json
import socket
import threading
import time
import urllib.error
import urllib.request

DROPPED_TRIES = 3       # a provider that cuts the body mid-response gets this many attempts
DROPPED_WAIT = 2        # seconds between them


class LLMError(Exception):
    def __init__(self, status, body):
        super().__init__(f"request failed ({status}): {body[:500]}")
        self.status = status
        self.body = body


def _cut(resp):
    """The watchdog: shut the socket under a read that has gone on too long. Not close():
    the buffered reader holds its lock while read() blocks, and close() would wait for it."""
    try:
        sock = resp.fp.raw._sock            # HTTPResponse -> BufferedReader -> SocketIO -> socket
        sock.shutdown(socket.SHUT_RDWR)
    except Exception:       # noqa: BLE001 - a socket that is already gone is fine
        pass


def _post(url, api_key, body, timeout, log=None, kind="chat"):
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers=headers, method="POST")
    start = time.time()
    status, response, error = 0, None, None
    try:
        # A provider can answer 200 and then cut the connection part-way through the body
        # (http.client raises IncompleteRead, which is not an OSError and would otherwise
        # escape this function and kill the whole round). Nothing was returned, so asking
        # again is safe.
        for attempt in range(DROPPED_TRIES):
            try:
                with urllib.request.urlopen(req, timeout=timeout) as resp:
                    status = resp.status
                    # `timeout` above is per socket read. OpenRouter keeps a slow call alive
                    # with ": OPENROUTER PROCESSING" comments, so that alone never fires; the
                    # watchdog makes it a wall-clock limit on the whole reply as well.
                    watchdog = threading.Timer(timeout, _cut, args=(resp,))
                    watchdog.daemon = True
                    watchdog.start()
                    try:
                        raw = resp.read().decode(errors="replace")
                    finally:
                        if not watchdog.is_alive():
                            raise TimeoutError(f"no complete reply after {timeout:g}s")
                        watchdog.cancel()
                break
            except (http.client.IncompleteRead, ConnectionResetError) as e:
                if attempt == DROPPED_TRIES - 1:
                    error = LLMError(status or 0, f"the provider cut the response short "
                                                  f"({type(e).__name__}) {DROPPED_TRIES} times")
                    raise error from None
                time.sleep(DROPPED_WAIT)
        try:
            response = json.loads(raw)
        except json.JSONDecodeError:
            response = raw
            error = LLMError(status, f"response was not JSON: {raw}")
            raise error from None
        return response
    except urllib.error.HTTPError as e:
        status = e.code
        text = e.read().decode(errors="replace")
        try:
            response = json.loads(text)
        except json.JSONDecodeError:
            response = text
        error = LLMError(e.code, text)
        raise error from None
    except LLMError:
        raise
    except (urllib.error.URLError, TimeoutError, OSError, http.client.HTTPException) as e:
        error = LLMError(0, str(getattr(e, "reason", e)) or type(e).__name__)
        raise error from None
    finally:
        if log:
            log(kind, url, body, response, status, time.time() - start, error)


def _download(url, timeout):
    if url.startswith("data:"):
        return base64.b64decode(url.split(",", 1)[1])
    with urllib.request.urlopen(url, timeout=timeout) as resp:
        return resp.read()


def chat(cfg, messages, tools=None, log=None, max_tokens=None):
    """Send one chat request and return the assistant message dict.

    `max_tokens` overrides the agent's own budget for this one call: parallel calls each write
    a whole file, so one file's output must not eat another's allowance."""
    body = {"model": cfg.model, "messages": messages, **cfg.extra}
    if cfg.temperature is not None:
        body["temperature"] = cfg.temperature
    if max_tokens or cfg.max_tokens:
        body["max_tokens"] = max_tokens or cfg.max_tokens
    if cfg.thinking_budget is not None:
        _thinking(body, cfg.base_url, cfg.thinking_budget)
    if tools:
        body["tools"] = tools
    model_key = (cfg.base_url, cfg.model)
    for fix in _LEARNED.get(model_key, ()):
        _apply(body, fix)
    for attempt in range(3):
        try:
            data = _post(cfg.base_url + "/chat/completions", cfg.api_key, body, cfg.timeout, log, "chat")
            failed = _error_inside(data)
            if not failed:
                break
            if attempt == 2:
                raise LLMError(failed.get("code") or 502, json.dumps(failed))
            time.sleep(20 if failed.get("code") == 429 else 5)      # rate limit, upstream timeout: wait and retry
        except LLMError as e:
            if e.status == 0 and "no complete reply" in str(e) and attempt == 0:
                continue                    # one more try after a wall-clock timeout: the provider may have stalled
            fix = _relax(body, e.body) if e.status == 400 and attempt < 2 else None
            if not fix:
                raise
            _LEARNED.setdefault(model_key, set()).add(fix)
    try:
        message = dict(data["choices"][0]["message"])
    except (KeyError, IndexError, TypeError):
        raise LLMError(200, json.dumps(data)) from None
    message["finish_reason"] = data["choices"][0].get("finish_reason")   # e.g. "length": cut off
    return message


def _error_inside(data):
    """A provider's failure delivered as a 200: OpenRouter answers an upstream timeout or rate
    limit with an empty message, finish_reason "error" and the error beside it. Read as a reply,
    that is an agent that said nothing and wrote nothing, and the round carries on without it."""
    try:
        choice = data["choices"][0]
    except (KeyError, IndexError, TypeError):
        return data.get("error") if isinstance(data, dict) else None
    if choice.get("error") or choice.get("finish_reason") == "error":
        return choice.get("error") or {"message": "the provider reported an error with no detail"}
    return None


_LEARNED = {}   # (base_url, model) -> fixes that model needed, so later calls skip the retry


def _thinking(body, base_url, budget):
    """Cap a reasoning model's thinking, in each provider's own terms. Thinking counts
    against max_tokens, so an uncapped model can spend the whole budget and say nothing."""
    host = base_url.split("//", 1)[-1].split("/", 1)[0]
    if host.endswith("openrouter.ai"):
        body.setdefault("reasoning", {"max_tokens": budget} if budget else {"effort": "minimal"})
    elif host.endswith("api.openai.com"):
        body.setdefault("reasoning_effort", "minimal" if budget <= 1024 else "low" if budget <= 4096 else "medium")
    elif host.endswith("api.anthropic.com"):
        if budget >= 1024:
            body.setdefault("thinking", {"type": "enabled", "budget_tokens": budget})


def _apply(body, fix):
    if fix == "drop_temperature":
        body.pop("temperature", None)
    elif fix == "drop_thinking":
        for k in ("reasoning", "reasoning_effort", "thinking"):
            body.pop(k, None)
    elif fix == "max_completion_tokens" and "max_tokens" in body:
        body["max_completion_tokens"] = body.pop("max_tokens")


def _relax(body, error):
    """Adapt to models that reject an optional parameter (e.g. reasoning models and
    temperature / max_tokens). Returns the fix applied, or None."""
    text = (error or "").lower()
    if any(k in body for k in ("reasoning", "reasoning_effort", "thinking")) and (
            "reasoning" in text or "thinking" in text):
        fix = "drop_thinking"
    elif "temperature" in body and "temperature" in text:
        fix = "drop_temperature"
    elif "max_tokens" in body and "max_tokens" in text:
        fix = "max_completion_tokens"
    else:
        return None
    _apply(body, fix)
    return fix


def list_models(cfg, timeout=20):
    """Model ids from the provider's OpenAI-compatible /models endpoint."""
    headers = {"Authorization": f"Bearer {cfg.api_key}"} if cfg.api_key else {}
    req = urllib.request.Request(cfg.base_url + "/models", headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        raise LLMError(e.code, e.read().decode(errors="replace")) from None
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        raise LLMError(0, str(getattr(e, "reason", e))) from None
    items = data.get("data", data.get("models", [])) if isinstance(data, dict) else data
    return sorted({(m.get("id") or m.get("name")) if isinstance(m, dict) else str(m) for m in items} - {None})


def generate_image(cfg, prompt, size=None, log=None):
    """Returns image bytes."""
    body = {"model": cfg.image_model, "prompt": prompt, "n": 1,
            "size": size or cfg.image_size, **cfg.image_extra}
    data = _post(cfg.image_base_url + "/images/generations", cfg.image_api_key, body, cfg.timeout, log, "image")
    try:
        item = data["data"][0]
    except (KeyError, IndexError, TypeError):
        raise LLMError(200, json.dumps(data)) from None
    if item.get("b64_json"):
        return base64.b64decode(item["b64_json"])
    if item.get("url"):
        return _download(item["url"], cfg.timeout)
    raise LLMError(200, json.dumps(data))


def images_in_message(msg, timeout=60):
    """Images a chat model returned alongside its text (e.g. OpenRouter's
    `message.images`, or image parts in `content`)."""
    parts = list(msg.get("images") or [])
    if isinstance(msg.get("content"), list):
        parts += [p for p in msg["content"] if p.get("type") == "image_url"]
    found = []
    for p in parts:
        url = (p.get("image_url") or {}).get("url") if isinstance(p, dict) else None
        if url:
            found.append(_download(url, timeout))
    return found


def text_of(msg):
    c = msg.get("content")
    if isinstance(c, list):
        return "\n".join(p.get("text", "") for p in c if p.get("type") == "text")
    return c or ""
