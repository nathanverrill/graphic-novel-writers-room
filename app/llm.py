"""Minimal client for OpenAI-compatible /chat/completions and /images/generations.
Every call takes the calling agent's AgentConfig, so each role can use its own
provider, model and settings, and an optional `log` callable (usage.CallLogger)
that receives the full request and response of every call, failed ones included."""
import base64
import json
import time
import urllib.error
import urllib.request


class LLMError(Exception):
    def __init__(self, status, body):
        super().__init__(f"request failed ({status}): {body[:500]}")
        self.status = status
        self.body = body


def _post(url, api_key, body, timeout, log=None, kind="chat"):
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers=headers, method="POST")
    start = time.time()
    status, response, error = 0, None, None
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            status = resp.status
            raw = resp.read().decode(errors="replace")
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
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        error = LLMError(0, str(getattr(e, "reason", e)))
        raise error from None
    finally:
        if log:
            log(kind, url, body, response, status, time.time() - start, error)


def _download(url, timeout):
    if url.startswith("data:"):
        return base64.b64decode(url.split(",", 1)[1])
    with urllib.request.urlopen(url, timeout=timeout) as resp:
        return resp.read()


def chat(cfg, messages, tools=None, log=None):
    """Send one chat request and return the assistant message dict."""
    body = {"model": cfg.model, "messages": messages, **cfg.extra}
    if cfg.temperature is not None:
        body["temperature"] = cfg.temperature
    if cfg.max_tokens:
        body["max_tokens"] = cfg.max_tokens
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
            break
        except LLMError as e:
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


_LEARNED = {}   # (base_url, model) -> fixes that model needed, so later calls skip the retry


def _thinking(body, base_url, budget):
    """Cap a reasoning model's thinking, in each provider's own terms. Thinking counts
    against max_tokens, so an uncapped model can spend the whole budget and say nothing."""
    host = base_url.split("//", 1)[-1].split("/", 1)[0]
    if host.endswith("openrouter.ai"):
        body.setdefault("reasoning", {"max_tokens": budget} if budget else {"effort": "low"})
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
