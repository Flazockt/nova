import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


MODEL = "gemini-4-hydrogen"
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"


class GeminiAPIError(RuntimeError):
    """Ein lesbarer Fehler der Gemini-API oder ihrer Antwort."""


def generate_content(api_key, contents, system_prompt=None):
    request_body = {
        "systemInstruction": {
            "parts": [{
                "text": system_prompt or (
                    "Du bist eine freundliche Desktop-Begleiterin. "
                    "Antworte auf Deutsch, klar und eher kurz."
                )
            }]
        },
        "contents": contents,
        "generationConfig": {"maxOutputTokens": 512},
    }
    request = Request(
        API_URL,
        data=json.dumps(request_body, ensure_ascii=False).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": api_key,
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
        raise GeminiAPIError(f"Gemini API-Fehler ({error.code}): {detail}") from error
    except (URLError, TimeoutError, OSError) as error:
        raise GeminiAPIError(f"Gemini ist nicht erreichbar: {error}") from error

    try:
        result = json.loads(response_data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise GeminiAPIError("Gemini hat eine ungültige Antwort geliefert.") from error

    candidates = result.get("candidates", [])
    if not candidates:
        reason = result.get("promptFeedback", {}).get("blockReason", "")
        detail = f"Anfrage wurde blockiert ({reason})." if reason else "Keine Antwort erhalten."
        raise GeminiAPIError(detail)

    parts = candidates[0].get("content", {}).get("parts", [])
    text = "\n".join(
        part["text"] for part in parts
        if isinstance(part, dict) and isinstance(part.get("text"), str)
    )
    if not text.strip():
        raise GeminiAPIError("Gemini hat keinen Text zurückgegeben.")
    return text.strip()
