# Hitster-harjoitus (aloittelijalle)

Tämä on ensimmäinen toimiva versio Hitster-tyylisestä pelistä:
- satunnainen kappale,
- Spotify-avauslinkki,
- vuosiarvaus,
- 5 kierroksen peli + pisteytys,
- mobiiliystävällinen käyttöliittymä.

## Mitä teet nyt (askel askeleelta, ilman vaikeita termejä)

### Avaa peli nyt (suora linkki)
1. Avaa tämä linkki:
   - **http://127.0.0.1:4173/index.html**
2. Jos sivu ei aukea, käynnistä peli tällä komennolla:
   - `python3 -m http.server 4173`
3. Avaa sama linkki uudelleen.

### Tärkein vastaus ensin
- **Et tarvitse uutta selaimen välilehteä tähän chatiin.**
- Joko:
  - avaat `index.html` tiedoston tiedostoselaimesta, **tai**
  - pyydät minua käynnistämään pelin linkiksi sinulle (helpoin).

### Vaihtoehto A (helpoin): avaa peli linkistä
Klikkaa tätä osoitetta:
- **http://127.0.0.1:4173/index.html**

Jos linkki ei aukea heti, kirjoita minulle:
- **"Avaa peli linkkinä"**

Silloin käynnistän pelin tähän samaan osoitteeseen ja varmistetaan yhdessä, että se aukeaa.

### Vaihtoehto B: avaa `index.html` itse (klik klik -ohje)
1. Katso tämän sivun/ikkunan vasenta reunaa.
2. Etsi kohta nimeltä **Files** (tai tiedostolista).
3. Klikkaa kansiota **workspace**.
4. Klikkaa kansiota **Hitster**.
5. Etsi tiedosto **index.html**.
6. Klikkaa `index.html`.
7. Jos näet painikkeen kuten **Open in Browser** / **Preview**, paina sitä.
8. Peli avautuu.

Jos et näe kohtaa **Files**:
- kirjoita minulle: **"En näe Files-valikkoa"**
- niin annan sinulle juuri tähän näkymään sopivan ohjeen seuraavaksi.

### Kun peli on auki
1. Liitä Client ID kenttään: `191fb613044f4862bc1c7c92f14547ff`
2. Paina **Tallenna Client ID**
3. Paina **Soita satunnainen biisi**
4. Syötä vuosiarvaus
5. Paina **Tarkista**
6. Toista kunnes kierros on 5/5


### Spotify-soitin suoraan pelissä
- Kun CSV:ssä on `spotify_track_id` tai `spotify_url`, biisi avautuu suoraan sivulla olevaan Spotify-soittimeen.
- Kappaleen nimi on piilotettu oletuksena ja näkyy vain, jos painat **Näytä kappaleen nimi**.

### Jos jokin ei toimi
- Päivitä sivu kerran.
- Liitä Client ID uudelleen.
- Paina uudelleen **Tallenna Client ID**.

---

## Missä `index.html` on?
Tässä kehitysympäristössä tiedosto on polussa:
- `/workspace/Hitster/index.html`

GitHubissa sama tiedosto näkyy repojen juuritasolla nimellä `index.html`.

## Tarvitaanko Spotify Family -tunnuksia?
Lyhyt vastaus: **ei tarvita**.

- Tavallinen Spotify-tili riittää yleensä testaukseen.
- Family-tili on hyödyllinen vain, jos useampi käyttäjä kirjautuu eri laitteilla samaan aikaan.

## Missä vaiheessa tarvitsen sinulta Spotify-tunnuksia?
Hyvä kysymys. Etenemme näin:

1. **Nyt (tämä versio):**
   - En tarvitse sinulta salasanaa enkä käyttäjätunnusta.
   - Käytämme valmiita Spotify-hakulinkkejä (`open.spotify.com/search/...`).

2. **Vaihe 2 (aloitettu): Spotify API -valmistelu**
   - Sovelluksessa on nyt kenttä, johon voi tallentaa `Client ID`:n selaimen localStorageen.
   - Tätä käytetään seuraavassa vaiheessa, kun haetaan kappaleita API:sta.

3. **Kun halutaan omat soittolistat ja automaattinen kappalehaku (Spotify API):**
   - Tarvitaan **Spotify Developer App** -tiedot:
     - `Client ID`
     - myöhemmin mahdollisesti `Redirect URI`
   - Näitä käytetään sovelluksen tunnistamiseen, **ei sinun Spotify-salasanaasi**.

4. **Jos tehdään kirjautuminen käyttäjän omaan Spotifyyn:**
   - Tarvitaan OAuth-kirjautuminen (nappi "Kirjaudu Spotifyllä").
   - Silloinkaan et lähetä minulle salasanaa; kirjautuminen tapahtuu Spotifyn omalla sivulla.

> Tärkeä sääntö: **älä koskaan jaa salasanaa chatissa tai koodissa**.

## Käynnistys (todella helppo)
Koska tämä on pelkkä HTML/CSS/JS-versio, voit avata tiedoston suoraan selaimeen:
1. Avaa `index.html`.
2. (Uusi) Lisää halutessasi Client ID asetuksiin ja paina “Tallenna Client ID”.
3. Paina **Soita satunnainen biisi**.
4. Arvaa vuosi ja paina **Tarkista**.
5. Peli kestää 5 kierrosta, jonka jälkeen näet lopputuloksen.

## Pisteytys tässä versiossa
- Täsmälleen oikein: **3 pistettä**
- Enintään 2 vuotta pielessä: **2 pistettä**
- Enintään 5 vuotta pielessä: **1 piste**
- Yli 5 vuotta pielessä: **0 pistettä**

## Seuraavat askeleet
- Kytketään Spotify API:in token-haku (Client Credentials).
- Haetaan kappaleita yhdestä valitusta soittolistasta.
- Lisätään moninpeli.
- Siirretään projekti Next.js-versioon, kun perusidea on testattu.


## Uutta tässä versiossa
- Ulkoasua on parannettu (selkeämpi hero-osa, paremmat kortit, värit ja mobiilinäkymä).
- Kappalekirjastoa on laajennettu eri vuosikymmenille (1930-luvulta 2020-luvulle).
- Spotify-soitin toimii suoraan sivulla, kun CSV-rivillä on `spotify_track_id` tai `spotify_url`.

## CSV-lista käytössä (1930-2025)
Sovellus yrittää ladata ensin `musiikkihitit_1930_2025_spotify.csv` tiedoston projektin juuresta, sitten varalla `musiikkihitit_1930_2025_yhdistetty.csv`, ja lopuksi GitHub RAW -osoitteen samasta CSV:stä.

Jos tiedosto löytyy, peli käyttää sitä. Jos tiedostoa ei löydy tai se on tyhjä, peli käyttää varalistaa.

CSV:n otsikkorivi voi olla esimerkiksi:

```csv
year,artist,title,spotify_query,spotify_url,spotify_track_id
```

- `spotify_track_id` on paras (esim. `4uLU6hMCjMI75M1A2tKUQC`).
- Vaihtoehtoisesti voit antaa `spotify_url` (esim. `https://open.spotify.com/track/...`).
- Tuettuja otsikoita ovat myös suomenkieliset nimet (`vuosi`, `artisti`, `kappale`) sekä puolipiste-erotin (`;`).
