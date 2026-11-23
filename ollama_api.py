import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


DEFAULT_HOST = "http://localhost:11434"


class OllamaAPIError(RuntimeError):
    """Ein lesbarer Fehler der lokalen Ollama-API oder ihrer Antwort."""


def generate_content(model, contents, system_prompt=None):
    if not isinstance(model, str) or not model.strip():
        raise OllamaAPIError("Bitte einen lokalen Ollama-Modellnamen eingeben.")

    host = DEFAULT_HOST

    messages = [{
        "role": "system",
        "content": system_prompt or "Du bist eine freundliche Desktop-Begleiterin.",
    }]
    for turn in contents:
        role = "assistant" if turn.get("role") in ("model", "assistant") else "user"
        text_parts = []
        images = []
        for part in turn.get("parts", []):
            text = part.get("text")
            if isinstance(text, str):
                text_parts.append(text)
            image = part.get("inline_data")
            if isinstance(image, dict) and isinstance(image.get("data"), str):
                images.append(image["data"])
        message = {"role": role, "content": "\n".join(text_parts)}
        if images:
            message["images"] = images
        if text_parts or images:
            messages.append(message)

    request = Request(
        host + "/api/chat",
        data=json.dumps({
            "model": model.strip(),
            "messages": messages,
            "stream": False,
        }, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urlopen(request, timeout=180) as response:
            response_data = response.read()
    except HTTPError as error:
        try:
            error_body = json.loads(error.read().decode("utf-8"))
            detail = error_body.get("error", "") if isinstance(error_body, dict) else ""
        except (UnicodeDecodeError, json.JSONDecodeError):
            detail = ""
        detail = str(detail or error.reason or "Unbekannter Fehler")
        raise OllamaAPIError(f"Ollama-Fehler ({error.code}): {detail}") from error
    except (URLError, TimeoutError, OSError) as error:
        raise OllamaAPIError(
            f"Ollama ist unter {host} nicht erreichbar. Starte Ollama und lade das Modell: {error}"
        ) from error

    try:
        result = json.loads(response_data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise OllamaAPIError("Ollama hat eine ungültige Antwort geliefert.") from error

    if not isinstance(result, dict):
        raise OllamaAPIError("Ollama hat eine ungültige Antwort geliefert.")
    if result.get("error"):
        raise OllamaAPIError(f"Ollama-Fehler: {result['error']}")
    message = result.get("message", {})
    content = message.get("content") if isinstance(message, dict) else None
    if not isinstance(content, str) or not content.strip():
        raise OllamaAPIError("Ollama hat keinen Text zurückgegeben.")
    return content.strip()
