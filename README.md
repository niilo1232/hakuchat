# Hakuchat

Henkilökohtainen chat-sovellus, jossa agentti voi käyttää verkkoa ja säätä työkaluinaan OpenRouterin kautta.

## Arkkitehtuuri

```
index.html
    |
    v
app.py (Flask)
    |
    v
chat_core.py
    |
    +---- OpenRouter API
    |
    +---- search.py (web_search)
    |
    +---- weather.py (get_current_temperature - placeholder)
```

## Asennus

1. Kloonaa repositorio:
   ```bash
   git clone https://github.com/niilo1232/hakuchat.git
   cd hakuchat
   ```

2. Luo virtuaaliympäristö ja asenna riippuvuudet:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. Luo `.env`-tiedosto mallin pohjalta ja lisää OpenRouter API-avain:
   ```bash
   cp .env.example .env
   ```
   Muokkaa `.env`-tiedostoa:
   ```
   OPENROUTER_API_KEY=oma_api_avain
   FLASK_SECRET_KEY=vaihda-tuotannossa
   ```

   > **Älä commitoi `.env`-tiedostoa**, jos se sisältää oikean API-avaimen. Se on jo lisätty `.gitignore`-tiedostoon.

## Käyttö

Käynnistä palvelin:
```bash
python app.py
```

Avaa selaimessa osoite: http://127.0.0.1:5000

Sovellus kuuntelee vain osoitetta `127.0.0.1` (ei ulkoista verkkoa).

## Käytettävissä olevat toiminnot

- Tavallinen keskustelu agentin kanssa
- Säätiedustelu (työkalu `get_current_temperature`, tällä hetkellä placeholder)
- Verkkohaku (työkalu `web_search`)
- Keskusteluhistorian nollaus: `POST /api/reset`

## Turvallisuus

Katso tarkemmat turvallisuusvaatimukset tiedostosta `AGENTS.md`.

Keskeiset suojaukset:
- Komentoinjektio estetty: `subprocess.run` listana ilman `shell=True`, syöte URL-enkoodataan
- Palautetaan vain otsikko ja URL hakutuloksista
- Curlille aikakatkaisu 10 sekuntia
- Toimintasilmukka enintään 5 kierrosta
- API-avain ympäristömuuttujassa, ei koodissa
- Palvelin vain localhostissa
