# Perhekartta – ohjeet virhetilanteisiin

Kun Perhekartassa näkyy **punainen laatikko**, lue sen ensimmäinen sana:

- **iCloud: …** → katso [Ohje A](#ohje-a-icloud-virhe-emilia-ei-näy)
- **Google: …** → katso [Ohje B](#ohje-b-google-virhe-elsa-ei-näy)
- Sovellus ei aukea ollenkaan tai siinä lukee "Haku epäonnistui" → katso [Ohje C](#ohje-c-sovellus-ei-aukea-ollenkaan)

Kaikki ohjeet alkavat yhteyden avaamisella Raspberry Pi:hin, joten sitä ei tarvitse muistaa erikseen.

---

## Ohje A: iCloud-virhe (Emilia ei näy)

Tarvitset: Windows-koneen ja oman Android-puhelimesi (tekstiviestiä varten).

**1.** Paina Windows-koneella **Windows-näppäintä**, kirjoita **PowerShell** ja paina **Enter**.

**2.** Kirjoita PowerShelliin ja paina **Enter**:
```
ssh ville@Vadelma
```

**3.** Kirjoita **Raspberry Pi:n salasana** ja paina **Enter**. Salasana ei näy ruudulla kirjoittaessa, ja se on normaalia.

✅ Rivi alkaa nyt tekstillä `ville@Vadelma:~ $`.

**4.** Kirjoita ja paina **Enter**:
```
cd ~/hitster/perhekartta
```

✅ Rivi alkaa nyt tekstillä `ville@Vadelma:~/hitster/perhekartta $`.

**5.** Kirjoita ja paina **Enter**:
```
.venv/bin/python setup_icloud.py
```

✅ Ruudulle tulee:
```
Puhelinnumero: +358 ••• •••••47
Apple lähettää koodin tekstiviestinä puhelimeesi.
Syötä 6-numeroinen koodi (tai paina Enter, jos tekstiviestiä ei tullut):
```

**6.** Odota tekstiviestiä Applelta. Kirjoita siinä oleva 6-numeroinen koodi ja paina **Enter**.

- Jos tekstiviestiä ei tule minuutin sisällä, paina pelkkää **Enter**, niin uusi tekstiviesti lähtee.

✅ Ruudulle tulee **Kirjautuminen onnistui!** ja lista laitteista.

**7.** Tarkista listasta, että **`iPhone (17)`** on yhä mukana.

- Jos se puuttuu, Emilia on vaihtanut puhelimensa nimen tai puhelimen. Katso silloin kohta [Emilian puhelimen nimi on muuttunut](#emilian-puhelimen-nimi-on-muuttunut).

**8.** Kirjoita ja paina **Enter**:
```
sudo systemctl restart perhekartta
```
Jos kone kysyy salasanaa, kirjoita Raspberry Pi:n salasana.

**9.** Kirjoita ja paina **Enter**:
```
exit
```
Voit sulkea PowerShell-ikkunan.

**10.** Avaa puhelimessa Perhekartta ja paina **Päivitä**.

✅ Emilia näkyy kartalla, eikä punaista laatikkoa enää ole.

---

## Ohje B: Google-virhe (Elsa ei näy)

Tarvitset: Windows-koneen ja Chromen.

### Osa 1: Uudet evästeet Chromen incognito-ikkunasta

Evästeet viedään **incognito-ikkunasta**, joka suljetaan heti perään. Silloin mikään
selain ei enää käytä samaa kirjautumista, eikä Google vaihda evästeitä niin, että
Raspberry Pi:n kopio vanhenisi.

**Vain ensimmäisellä kerralla:** salli laajennus incognito-ikkunassa.

1. Avaa Windows-koneella **Chrome**.
2. Kirjoita osoiteriville `chrome://extensions` ja paina **Enter**.
3. Etsi **Get cookies.txt LOCALLY** ja paina sen kohdalla **Tiedot**.
4. Laita päälle kytkin **Salli incognito-tilassa**.

**Joka kerta:**

**1.** Poista Windows-koneen **Lataukset**-kansiosta kaikki tiedostot, joiden nimessä on `cookies`.

**2.** Avaa Chromessa incognito-ikkuna painamalla **Ctrl + Shift + N**.

✅ Ikkuna on tumma, ja siinä lukee "Olet incognito-tilassa".

**3.** Kirjoita incognito-ikkunan osoiteriville **google.com/maps** ja paina **Enter**.

**4.** Paina oikeasta yläkulmasta **Kirjaudu** ja kirjaudu omalla Google-tililläsi (ville.rihtamo@…). Hyväksy kirjautuminen puhelimesta, jos Google pyytää sitä.

**5.** Odota, että kartta latautuu.

**6.** Paina incognito-ikkunan oikeasta yläkulmasta **palapelin kuvaa** 🧩.

**7.** Valitse **Get cookies.txt LOCALLY**.

**8.** Paina **Export**.

✅ Lataukset-kansioon tulee tiedosto `www.google.com_cookies.txt`.

**9.** Sulje incognito-ikkuna oikean yläkulman **X**:llä. **Älä paina "Kirjaudu ulos"**, koska se mitätöisi evästeet heti.

### Osa 2: Tiedosto Raspberry Pi:lle

**10.** Paina **Windows-näppäintä**, kirjoita **PowerShell** ja paina **Enter**.

**11.** Kirjoita PowerShelliin yhdelle riville ja paina **Enter**:
```
scp "$env:USERPROFILE\Downloads\www.google.com_cookies.txt" ville@Vadelma:~/hitster/perhekartta/google_cookies.txt
```

**12.** Kirjoita **Raspberry Pi:n salasana** ja paina **Enter**.

✅ Ruudulle tulee rivi, jossa on tiedoston nimi ja `100%`.

### Osa 3: Käynnistä Perhekartta uudelleen

**13.** Kirjoita PowerShelliin ja paina **Enter**:
```
ssh ville@Vadelma
```

**14.** Kirjoita **Raspberry Pi:n salasana** ja paina **Enter**.

**15.** Kirjoita ja paina **Enter**:
```
sudo systemctl restart perhekartta
```
Jos kone kysyy salasanaa, kirjoita Raspberry Pi:n salasana.

**16.** Kirjoita ja paina **Enter**:
```
exit
```
Voit sulkea PowerShell-ikkunan.

**17.** Poista Windows-koneen **Lataukset**-kansiosta tiedosto `www.google.com_cookies.txt`. Se on avain Google-tiliisi, eikä sitä kannata säilyttää.

**18.** Avaa puhelimessa Perhekartta ja paina **Päivitä**.

✅ Elsa näkyy kartalla, eikä punaista laatikkoa enää ole.

Perhekartta tallentaa jatkossa itse Googlen päivittämät evästeet, joten tätä ohjetta ei pitäisi tarvita usein.

---

## Ohje C: Sovellus ei aukea ollenkaan

**1.** Tarkista ensin puhelimesta, että **Tailscale**-sovellus on päällä. Avaa se ja varmista, että yläreunan kytkin on päällä (**Connected**).

**2.** Avaa Perhekartta uudelleen. Jos se toimii nyt, olet valmis.

Jos ei toimi, jatka Windows-koneella:

**3.** Paina **Windows-näppäintä**, kirjoita **PowerShell** ja paina **Enter**.

**4.** Kirjoita ja paina **Enter**:
```
ssh ville@Vadelma
```

- Jos tulee virhe *"Could not resolve hostname"* tai *"Connection timed out"*, Raspberry Pi on sammunut tai irti verkosta. Tarkista, että sen virtajohto ja verkkojohto ovat kiinni, odota 2 minuuttia ja kokeile uudelleen. Perhekartta käynnistyy itsestään, kun Raspberry Pi käynnistyy.

**5.** Kirjoita **Raspberry Pi:n salasana** ja paina **Enter**.

**6.** Kirjoita ja paina **Enter**:
```
systemctl status perhekartta
```

- Jos ruudulla lukee vihreällä **active (running)**, paina **q** ja siirry kohtaan 8.
- Jos ruudulla lukee jotain muuta, paina **q** ja siirry kohtaan 7.

**7.** Kirjoita ja paina **Enter**:
```
sudo systemctl restart perhekartta
```
Odota 10 sekuntia ja tee kohta 6 uudelleen. Jos ruudulla ei vieläkään lue **active (running)**, kirjoita:
```
journalctl -u perhekartta -n 30
```
Ota ruudusta kuva tai kopioi teksti talteen ja pyydä apua.

**8.** Kirjoita ja paina **Enter**:
```
tailscale serve status
```

✅ Ruudulla pitää näkyä:
```
https://vadelma.tailc9692d.ts.net:4443 (tailnet only)
|-- / proxy http://127.0.0.1:8080
```

- Jos tämä kohta puuttuu, kirjoita ja paina **Enter**:
  ```
  sudo tailscale serve --bg --https=4443 8080
  ```

**9.** Kirjoita `exit` ja paina **Enter**.

**10.** Avaa Perhekartta puhelimessa uudelleen.

---

## Emilian puhelimen nimi on muuttunut

Tee tämä, jos Ohjeen A kohdassa 7 listasta puuttui `iPhone (17)`.

**1.** Katso Ohjeen A laitelistasta, millä rivillä on sijainti (numeroita) ja joka näyttää Emilian puhelimelta. Kirjoita sen nimi muistiin täsmälleen, eli kaikki lainausmerkkien välissä oleva.

**2.** Kirjoita ja paina **Enter**:
```
nano config.json
```

**3.** Mene nuolinäppäimillä riville:
```
      "iPhone (17)": "Emilia"
```

**4.** Poista `iPhone (17)` **Backspace**-näppäimellä ja kirjoita tilalle kohdassa 1 muistiin kirjoittamasi nimi. Lainausmerkit jäävät paikalleen.

**5.** Tallenna ja sulje: **Ctrl + O**, **Enter**, **Ctrl + X**.

**6.** Kirjoita ja paina **Enter**:
```
sudo systemctl restart perhekartta
```
