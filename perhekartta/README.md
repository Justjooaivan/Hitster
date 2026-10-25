# Perhekartta

Näyttää molempien tyttärien sijainnit **samalla kartalla**:

- **iPhone** → haetaan iCloudin Find My -palvelusta (sama kuin icloud.com/find)
- **Android** → haetaan Googlen sijainninjaosta (sama kuin Google Mapsin "Sijainnin jakaminen")

Puhelimessa Perhekartta näkyy omana sovelluksenaan. Sijainnit hakee pieni
palvelin, joka pyörii **omalla koneellasi** (esim. kotikone tai Raspberry Pi),
joten Apple- ja Google-tunnuksesi eivät lähde minnekään muualle.

## Mitä tarvitset ensin

1. **iPhone-tytär on Perhejaossa** ja hänen sijaintinsa näkyy sinulle, kun
   avaat icloud.com/find. Jos näet hänen puhelimensa siellä, se toimii myös tässä.
2. **Android-tytär jakaa sijaintinsa sinulle Google Mapsissa.**
   Googlen Family Linkillä ei ole rajapintaa, jota omat sovellukset voisivat
   lukea. Siksi tytön puhelimessa avataan Google Maps → profiilikuva →
   *Sijainnin jakaminen* → *Jaa sijainti* → valitse oma Google-tilisi → *Kunnes poistat tämän*.
   Tarkista omasta Google Mapsistasi, että hän näkyy kartalla.
3. Python 3.10 tai uudempi.

## Asennus

```bash
cd perhekartta
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp config.example.json config.json
```

Täytä `config.json`:

| Kohta | Mitä siihen |
|---|---|
| `icloud.apple_id`, `icloud.password` | Oma Apple ID ja salasana |
| `icloud.devices` | Tytön puhelimen nimi → nimi kartalla (nimen saat seuraavasta vaiheesta) |
| `google.account` | Oma Gmail-osoitteesi |
| `google.people` | Tytön nimi Googlessa → nimi kartalla |
| `app_password` | Oma salasana, jolla kirjaudut sovellukseen puhelimella |

Jos jätät `devices`- tai `people`-kohdan tyhjäksi (`{}`), kaikki näkyvät henkilöt/laitteet näytetään.

### 1. iCloud-kirjautuminen (kerran)

```bash
python setup_icloud.py
```

Apple lähettää koodin puhelimeesi. Syötä se. Skripti listaa Find My -laitteet:
kopioi tyttären puhelimen nimi `config.json`in kohtaan `icloud.devices`.
Apple vanhentaa istunnon ajoittain (yleensä viikkojen tai kuukausien välein).
Kun kartalla lukee virhe iCloudista, aja tämä komento uudelleen.

### 2. Google-evästeet (kerran, ja uudelleen jos vanhenevat)

Google ei salli kirjautumista ohjelmalla, joten sovellus käyttää selaimesi kirjautumista:

1. Asenna tietokoneen Chromeen/Firefoxiin laajennus **"Get cookies.txt LOCALLY"**.
2. Kirjaudu omalla Google-tililläsi ja avaa https://www.google.com/maps
3. Avaa laajennus ja vie evästeet (*Export*, Netscape-muoto).
4. Tallenna tiedosto nimellä `google_cookies.txt` tähän `perhekartta`-kansioon.

Evästeet ovat käytännössä Google-tilisi avain, joten älä jaa tiedostoa kenellekään
(`.gitignore` estää sen päätymisen GitHubiin).

### 3. Käynnistys

```bash
python app.py
```

Kone, jolla sovellus pyörii, pitää olla päällä aina, kun haluat katsoa karttaa.
Pieni Raspberry Pi tai vanha läppäri, joka on jatkuvasti päällä, sopii tähän hyvin.

### 4. Sovellus Android-puhelimeen

Chrome asentaa Perhekartan oikeaksi sovellukseksi (oma kuvake, avautuu koko
näytölle ilman selainta), mutta se vaatii **https-osoitteen**. Helpoin tapa saada
se, ja samalla pääsy kartalle myös kodin ulkopuolelta, on ilmainen
[Tailscale](https://tailscale.com):

1. Asenna Tailscale koneelle, jolla `app.py` pyörii, ja kirjaudu sisään
   (esim. Google-tililläsi).
2. Asenna **Tailscale**-sovellus Play Kaupasta omaan puhelimeesi ja kirjaudu samalla tilillä.
3. Aja koneella kerran:
   ```bash
   tailscale serve --bg 8080
   ```
   Komento tulostaa osoitteen, esim. `https://kotikone.tail1234.ts.net`.
   (Jos se pyytää ottamaan HTTPS:n käyttöön Tailscalen hallintasivulla, tee niin.)
4. Avaa osoite puhelimen **Chromessa** ja kirjaudu `app_password`-salasanalla.
5. Chrome → ⋮ → **Asenna sovellus** (tai *Lisää aloitusnäyttöön → Asenna*).

Nyt kotinäytöllä on Perhekartta-kuvake. Kirjautuminen säilyy vuoden.
Kartta ei näy kenellekään muulle, koska Tailscale-osoitteeseen pääsevät vain
omat laitteesi. **Älä avaa porttia suoraan internetiin.**

Kotiverkossa voi kokeilla myös ilman Tailscalea osoitteella `http://<koneen-ip>:8080`,
mutta silloin Chrome tekee vain pikakuvakkeen, joka avaa sivun selaimeen.

## Miten sovellus toimii

- Kartta päivittyy itsestään `refresh_seconds` välein (oletus 60 s) ja aina kun palaat sivulle.
- *Päivitä*-nappi pyytää iPhonea kertomaan tuoreen sijainnin heti.
- Kortissa näkyy, milloin sijainti on viimeksi saatu, tarkkuus metreinä ja akun varaus.
  Oranssi aika = sijainti yli 30 min vanha.
- Jos iCloud tai Google ei vastaa, toinen näkyy silti ja kartalle tulee virheviesti.

## Hyvä tietää

- Sekä iCloud- että Google-yhteys käyttää **epävirallisia** rajapintoja
  ([pyicloud](https://github.com/timlaing/pyicloud), [locationsharinglib](https://github.com/costastf/locationsharinglib)).
  Samoja kirjastoja käyttää myös Home Assistant. Ne toimivat hyvin, mutta Apple tai
  Google voi muuttaa jotain. Tällöin kirjastot yleensä päivittyvät:
  `pip install -U -r requirements.txt`.
- Jos haluat joskus täysin omasta palvelusta riippumattoman ratkaisun, molempiin puhelimiin
  voi asentaa [OwnTracks](https://owntracks.org)-sovelluksen, joka lähettää sijainnin suoraan omalle palvelimelle.
