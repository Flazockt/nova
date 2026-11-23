import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


MODEL = "gpt-4o-mini"
API_URL = "https://api.openai.com/v1/chat/completions"


class OpenAIAPIError(RuntimeError):
    """Ein lesbarer Fehler der OpenAI-API oder ihrer Antwort."""


def generate_content(api_key, contents, api_url=API_URL, model=MODEL, service_name="OpenAI",
                     system_prompt=None):
    if not isinstance(api_key, str) or not api_key.strip():
        raise OpenAIAPIError(f"Bitte zuerst einen {service_name} API-Key eingeben.")

    messages = [{
        "role": "system",
        "content": system_prompt or (
            "Du bist eine freundliche Desktop-Begleiterin. "
            "Antworte auf Deutsch, klar und eher kurz."
        ),
    }]
    for turn in contents:
        role = "assistant" if turn.get("role") == "model" else "user"
        parts = []
        for part in turn.get("parts", []):
            text = part.get("text")
            if isinstance(text, str):
                parts.append({"type": "text", "text": text})
            image = part.get("inline_data")
            if isinstance(image, dict):
                mime_type = image.get("mime_type", "image/png")
                data = image.get("data")
                if isinstance(data, str):
                    parts.append({
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{mime_type};base64,{data}",
                        },
                    })
        if parts:
            content = parts[0]["text"] if len(parts) == 1 and parts[0]["type"] == "text" else parts
            messages.append({"role": role, "content": content})

    request = Request(
        api_url,
        data=json.dumps({
            "model": model,
            "messages": messages,
            "max_tokens": 512,
        }, ensure_ascii=False).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )

    try:
        with urlopen(request, timeout=60) as response:
            response_data = response.read()
    except HTTPError as error:
        try:
            error_body = json.loads(error.read().decode("utf-8"))
            detail = error_body.get("error", {}).get("message", "")
        except (UnicodeDecodeError, json.JSONDecodeError):
            detail = ""
        detail = str(detail or error.reason or "Unbekannter Fehler")
        raise OpenAIAPIError(
            f"{service_name} API-Fehler ({error.code}): {detail}"
        ) from error
    except (URLError, TimeoutError, OSError) as error:
        raise OpenAIAPIError(f"{service_name} ist nicht erreichbar: {error}") from error

    try:
        result = json.loads(response_data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise OpenAIAPIError(f"{service_name} hat eine ungültige Antwort geliefert.") from error

    if not isinstance(result, dict):
        raise OpenAIAPIError(f"{service_name} hat eine ungültige Antwort geliefert.")
    choices = result.get("choices", [])
    if not isinstance(choices, list) or not choices or not isinstance(choices[0], dict):
        raise OpenAIAPIError(f"{service_name} hat keine Antwort zurückgegeben.")
    message = choices[0].get("message", {})
    content = message.get("content") if isinstance(message, dict) else None
    if isinstance(content, str) and content.strip():
        return content.strip()
    if isinstance(content, list):
        text = "\n".join(
            item["text"] for item in content
            if isinstance(item, dict) and isinstance(item.get("text"), str)
        )
        if text.strip():
            return text.strip()
    raise OpenAIAPIError(f"{service_name} hat keinen Text zurückgegeben.")
