import json
import subprocess
import urllib.parse
from html import unescape


# OpenAI function-calling -työkalmäärittely (yhteensopiva chat_core.py:n kanssa)
search_tool = {
    "type": "function",
    "function": {
        "name": "web_search",
        "description": "Searches the web for information about a given query.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query.",
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of results to return (default 5).",
                },
            },
            "required": ["query"],
            "additionalProperties": False,
        },
    },
}


def _fetch_html(query: str, max_results: int, timeout: int = 15) -> str | None:
    if not query or not query.strip():
        return None

    encoded_query = urllib.parse.quote(query.strip())
    url = f"https://www.google.com/search?q={encoded_query}&num={max_results}"

    try:
        result = subprocess.run(
            ["curl", "--max-time", "10", "-s", "-L", url],
            shell=False,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except (subprocess.TimeoutExpired, OSError):
        return None

    if result.returncode != 0:
        return None

    html = result.stdout
    if not html:
        return None

    return html


def _parse_results(html: str, max_results: int) -> list[dict]:
    results = []
    seen = set()
    start = 0

    while len(results) < max_results:
        link_start = html.find('<a href="', start)
        if link_start == -1:
            break
        href_start = link_start + len('<a href="')
        href_end = html.find('"', href_start)
        if href_end == -1:
            break
        href = html[href_start:href_end]
        start = href_end

        if not href.startswith("http") or "google.com" in href:
            continue

        title_start = html.find(">", href_end)
        if title_start == -1:
            continue
        title_end = html.find("</a>", title_start)
        if title_end == -1:
            continue
        raw_title = html[title_start + 1:title_end]
        title = unescape(raw_title).strip()

        if not title or href in seen:
            continue

        seen.add(href)
        results.append({"title": title, "url": href})

    return results


def web_search(query: str, max_results: int = 5) -> list[dict]:
    """Hakee verkosta tuloksia annetulla kyselyllä.

    Palauttaa listan sanakirjoja avaimilla "title" ja "url".
    Virhetilanteissa (tyhjä kysely, timeout, verkkovirhe, tyhjät tulokset)
    palautetaan tyhjä lista.
    """
    if not query or not query.strip():
        return []

    if max_results is None or max_results < 1:
        max_results = 5

    html = _fetch_html(query.strip(), max_results)
    if html is None:
        return []

    return _parse_results(html, max_results)


def summarize_results(results: list[dict], query: str) -> str:
    """Tiivistää hakutulosten otsikot ja URL:it luettavaan muotoon.

    Käytetty apufunktiona, kun hakutulokset halutaan syöttää eteenpäin
    agentille (esim. chat_core.py) luonnollisen kielen muodossa.
    """
    if not results:
        return f"Ei hakutuloksia haulle: {query}"

    lines = [f"Hakutuloksia haulla '{query}':"]
    for idx, item in enumerate(results, start=1):
        title = item.get("title", "(ei otsikkoa)")
        url = item.get("url", "")
        lines.append(f"{idx}. {title} ({url})")

    return "\n".join(lines)
