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
    if tools:
        body["tools"] = tools
    data = _post(cfg.base_url + "/chat/completions", cfg.api_key, body, cfg.timeout, log, "chat")
    try:
        return data["choices"][0]["message"]
    except (KeyError, IndexError, TypeError):
        raise LLMError(200, json.dumps(data)) from None


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
