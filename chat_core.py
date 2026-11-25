import json
import os
from dotenv import load_dotenv
from openai import OpenAI

from search import search_tool, web_search, summarize_results

load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")
client = None
if API_KEY:
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=API_KEY,
    )

MODEL = "nvidia/nemotron-3.5-super-vl:free"

weather_tool = {
    "type": "function",
    "function": {
        "name": "get_current_temperature",
        "description": "Gets the current temperature for a given location.",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city name, e.g. San Francisco",
                },
            },
            "required": ["location"],
            "additionalProperties": False,
        },
    },
}

TOOLS = [weather_tool, search_tool]

SYSTEM_PROMPT = """Olet hyödyllinen AI-assistentti. Käytössäsi on seuraavat työkalut:

- get_current_temperature: hakee annetun kaupungin nykyisen lämpötilan.
- web_search: etsii tietoa verkosta annetulla hakusanalla.

Käytä työkaluja aina kun se auttaa vastaamaan käyttäjän kysymykseen. Vastaa suomeksi."""


def get_current_temperature(location: str) -> str:
    """Säätyökalun toteutus. Korvaa todellisella sää-API-kutsulla myöhemmin."""
    return f"Säätilaa paikassa {location} ei voida tällä hetkellä hakea (sää-API ei ole konfiguroitu)."


TOOL_FUNCTIONS = {
    "get_current_temperature": get_current_temperature,
    "web_search": web_search,
}


def _execute_tool_call(tool_call) -> dict:
    name = tool_call.function.name
    try:
        args = json.loads(tool_call.function.arguments or "{}")
    except json.JSONDecodeError:
        args = {}

    func = TOOL_FUNCTIONS.get(name)
    if not func:
        return {
            "role": "tool",
            "tool_call_id": tool_call.id,
            "name": name,
            "content": f"Tuntematon työkalu: {name}",
        }

    try:
        result = func(**args)
    except Exception as exc:
        return {
            "role": "tool",
            "tool_call_id": tool_call.id,
            "name": name,
            "content": f"Työkalussa {name} tapahtui virhe: {exc}",
        }

    if name == "web_search":
        content = summarize_results(result, args.get("query", ""))
    else:
        content = str(result)

    return {
        "role": "tool",
        "tool_call_id": tool_call.id,
        "name": name,
        "content": content,
    }


def chat(messages: list[dict], user_message: str | None = None, max_iterations: int = 5) -> str:
    """Käsittelee yhden käyttäjäviestin funktionkutsu-silmukalla.

    Args:
        messages: Keskusteluhistoria (lista rooli/sisältö -sanakirjoja).
        user_message: Uusi käyttäjäviesti, joka lisätään historiaan.
        max_iterations: Maksimimäärä funktionkierroksia ennen lopetusta.

    Returns:
        Mallin lopullinen tekstivastaus.
    """
    if user_message:
        messages.append({"role": "user", "content": user_message})

    if not messages or messages[0].get("role") != "system":
        messages.insert(0, {"role": "system", "content": SYSTEM_PROMPT})

    if not client:
        raise RuntimeError("OPENROUTER_API_KEY ei ole asetettu (.env-tiedosto puuttuu tai on tyhjä)")

    for _ in range(max_iterations):
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=TOOLS,
        )

        message = response.choices[0].message
        messages.append(message.model_dump(exclude_none=True))

        if not message.tool_calls:
            return message.content or ""

        for tool_call in message.tool_calls or []:
            messages.append(_execute_tool_call(tool_call))

    return "Pahoittelut, en pystynyt käsittelemään pyyntöä loppuun asti."


def new_conversation() -> list[dict]:
    """Palauttaa tyhjän keskusteluhistorian."""
    return []
