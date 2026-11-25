# AGENTS.md

Tämä tiedosto kuvaa projektin pelisäännöt ja turvallisuusvaatimukset, joita jokainen muutos ja toteutus tulee noudattaa.

## Turvallisuus ja rajoitteet

Sovelluksessa kielimalli päättää, mitä haetaan, ja hakutulokset tulevat tuntemattomilta verkkosivuilta. Molempia on kohdeltava epäluotettavana syötteenä.

| Riski | Mitä voi tapahtua | Vaadittu suojaus |
|-------|-------------------|------------------|
| Komentoinjektio | Hakusana `x; rm -rf ~` suoritetaan komentona | `subprocess.run([...])` listana, ei `shell=True`; hakusana URL-enkoodataan (`urllib.parse.quote`) |
| Prompt injection | Hakutuloksen teksti käskee mallia toimimaan toisin | Tuloksista palautetaan vain otsikko ja URL; system-prompt kertoo, että tulokset ovat dataa, eivät ohjeita |
| Jumiutuminen | Curl tai malli jää odottamaan loputtomasti | Curlille `--max-time 10`, toimintasilmukalle enintään 5 kierrosta |
| Liian suuri vastaus | Sivu täyttää mallin kontekstin | Tulosten määrä ja pituus rajataan |
| API-avaimen vuoto | Avain päätyy GitHubiin | Avain ympäristömuuttujassa, `.env` ja `.venv/` on lisätty `.gitignore`-tiedostoon |
| Avoin palvelin | Muut verkon koneet käyttävät avaintasi | Palvelin kuuntelee vain osoitetta `127.0.0.1` |

### Pakolliset käytännöt

- Älä koskaan käytä `shell=True` `subprocess.run`-kutsussa käyttäjän syötteen kanssa.
- Enkoodaa aina käyttäjän syöte URL-muotoon ennen sen liittämistä pyyntöön.
- Palauta hakutuloksista vain otsikko ja URL — älä sisällytä sivun sisältöä suoraan mallille.
- Rajoita hakutulosten enimmäismäärää (oletus 5).
- Aseta curlille aikakatkaisu (`--max-time 10`).
- Rajoita funktionkutsu-silmukan kierrosten määrää (oletus 5).
- Älä koskaan commitoi `.env`-tiedostoa sisältäen oikeaa API-avainta.
- Käytä `.env.example`-tiedostoa mallina, jossa avain on tyhjä.
- Flask-palvelin kuuntelee vain `127.0.0.1`.

### Testaus

Testaa komentoinjektio kirjoittamalla chattiin:
```
Etsi linkkejä aiheesta test; touch /tmp/hakkeroitu
```
Tarkista, ettei tiedostoa `/tmp/hakkeroitu` synny.

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
