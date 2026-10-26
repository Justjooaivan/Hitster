"""Perhekartta: näyttää iCloudin (iPhone) ja Googlen (Android) sijainnit samalla kartalla.

Käynnistys:  python app.py
Asetukset:   config.json (katso config.example.json)
"""

import json
import secrets
import threading
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

from flask import (
    Flask,
    jsonify,
    redirect,
    request,
    send_from_directory,
    session,
    url_for,
)

BASE_DIR = Path(__file__).resolve().parent
CONFIG_FILE = BASE_DIR / "config.json"
ICLOUD_SESSION_DIR = BASE_DIR / "icloud_session"
MIN_REFRESH_SECONDS = 15  # ei kuormiteta Applea ja Googlea turhaan

app = Flask(__name__, static_folder=str(BASE_DIR / "static"))


def _secret_key():
    """Kirjautumiseväste allekirjoitetaan tällä avaimella (luodaan ensimmäisellä käynnistyksellä)."""
    key_file = BASE_DIR / "secret_key.txt"
    if not key_file.exists():
        key_file.write_text(secrets.token_hex(32))
    return key_file.read_text().strip()


app.secret_key = _secret_key()
app.permanent_session_lifetime = timedelta(days=365)


def load_config():
    if not CONFIG_FILE.exists():
        raise SystemExit(
            "config.json puuttuu. Kopioi config.example.json -> config.json ja täytä tiedot."
        )
    return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))


CONFIG = load_config()


# ---------------------------------------------------------------- iCloud ----

_icloud_api = None


def _icloud():
    """Palauttaa kirjautuneen iCloud-yhteyden (luodaan kerran, käyttää tallennettua istuntoa)."""
    global _icloud_api
    if _icloud_api is None:
        from pyicloud import PyiCloudService

        cfg = CONFIG["icloud"]
        api = PyiCloudService(
            cfg["apple_id"],
            cfg.get("password") or None,
            cookie_directory=str(ICLOUD_SESSION_DIR),
            with_family=True,
            refresh_interval=None,  # haetaan itse silloin kun sivu pyytää
        )
        if api.requires_2fa or api.requires_2sa:
            raise RuntimeError(
                "iCloud pyytää kaksivaiheista tunnistusta. Aja ensin: python setup_icloud.py"
            )
        _icloud_api = api
    return _icloud_api


def fetch_icloud():
    global _icloud_api
    cfg = CONFIG.get("icloud")
    if not cfg or not cfg.get("apple_id"):
        return []
    wanted = cfg.get("devices") or {}

    try:
        devices = _icloud().devices
        devices.refresh(locate=True)  # pyytää laitteita kertomaan tuoreen sijainnin
    except Exception:
        _icloud_api = None  # yritetään seuraavalla kerralla kirjautua uudelleen
        raise

    people = []
    for device in devices:
        if wanted and device.name not in wanted:
            continue
        loc = device.location
        if not loc or loc.get("latitude") is None:
            continue
        battery = device.data.get("batteryLevel")
        ts = loc.get("timeStamp")
        people.append(
            {
                "name": wanted.get(device.name, device.name),
                "source": "iCloud",
                "device": device.name,
                "lat": loc["latitude"],
                "lon": loc["longitude"],
                "accuracy": loc.get("horizontalAccuracy"),
                "timestamp": (
                    datetime.fromtimestamp(ts / 1000, tz=timezone.utc).isoformat()
                    if ts
                    else None
                ),
                "battery": round(battery * 100) if battery else None,
                "address": None,
            }
        )
    return people


# ---------------------------------------------------------------- Google ----

# Selain pitää Google-kirjautumisen voimassa kierrättämällä evästettä
# __Secure-1PSIDTS muutaman minuutin välein. Perhekartta tekee saman, jotta
# kerran viedyt evästeet eivät vanhene.
GOOGLE_ROTATE_URL = "https://accounts.google.com/RotateCookies"
GOOGLE_ROTATE_SECONDS = 540
_google_cookie_lock = threading.Lock()


def _google_cookie_file():
    cfg = CONFIG.get("google") or {}
    if not cfg.get("account"):
        return None
    return BASE_DIR / cfg.get("cookies_file", "google_cookies.txt")


def rotate_google_cookies():
    """Pyytää Googlelta uuden kirjautumisevästeen ja tallentaa sen tiedostoon."""
    from locationsharinglib import Service

    path = _google_cookie_file()
    if path is None or not path.exists():
        return False
    with _google_cookie_lock:
        session = Service._get_session_from_cookie_file(path.read_text(encoding="utf-8"))
        response = session.post(
            GOOGLE_ROTATE_URL,
            headers={"Content-Type": "application/json"},
            data='[000,"-0000000000000000000"]',
            timeout=30,
        )
        if response.status_code == 401:
            app.logger.warning("Googlen evästeet ovat vanhentuneet, kierrätys ei onnistu.")
            return False
        response.raise_for_status()
        _save_google_cookies(session.cookies, path)
    return True


def _google_keepalive():
    while True:
        try:
            rotate_google_cookies()
        except Exception as exc:  # verkkokatko tms., yritetään uudelleen myöhemmin
            app.logger.warning("Googlen evästeiden kierrätys epäonnistui: %s", exc)
        time.sleep(GOOGLE_ROTATE_SECONDS)


def _save_google_cookies(jar, path):
    """Tallentaa Googlen päivittämät evästeet takaisin tiedostoon.

    Google vaihtaa kirjautumisevästeitä ajoittain. Kun uudet arvot tallennetaan,
    kirjautuminen pysyy voimassa pidempään eikä evästeitä tarvitse viedä uudelleen.
    """
    lines = [
        "\t".join(
            [
                c.domain,
                "TRUE" if c.domain.startswith(".") else "FALSE",
                c.path or "/",
                "TRUE" if c.secure else "FALSE",
                str(int(c.expires or 0)),
                c.name,
                c.value or "",
            ]
        )
        for c in jar
        if c.value
    ]
    new_text = "# Netscape HTTP Cookie File\n" + "\n".join(lines) + "\n"
    if path.read_text(encoding="utf-8") == new_text:
        return
    tmp = path.with_suffix(".tmp")
    tmp.write_text(new_text, encoding="utf-8")
    tmp.replace(path)


def fetch_google():
    cfg = CONFIG.get("google")
    if not cfg or not cfg.get("account"):
        return []
    from locationsharinglib import Service
    from locationsharinglib.locationsharinglibexceptions import InvalidCookies

    cookies = _google_cookie_file()
    if not cookies.exists():
        raise RuntimeError(f"Google-evästetiedostoa ei löydy: {cookies.name}")
    with _google_cookie_lock:
        try:
            service = Service(cookies_file=str(cookies), authenticating_account=cfg["account"])
        except InvalidCookies:
            raise RuntimeError(
                "Googlen evästeet ovat vanhentuneet. Vie uudet evästeet "
                "(VIRHETILANTEET.md, Ohje B)."
            ) from None
        shared = service.get_shared_people()
        _save_google_cookies(service._session.cookies, cookies)
    wanted = cfg.get("people") or {}

    people = []
    for person in shared:
        key = next(
            (k for k in (person.full_name, person.nickname) if k and k in wanted), None
        )
        if wanted and key is None:
            continue
        if person.latitude is None:
            continue
        people.append(
            {
                "name": wanted.get(key, person.nickname or person.full_name),
                "source": "Google",
                "device": None,
                "lat": person.latitude,
                "lon": person.longitude,
                "accuracy": person.accuracy,
                "timestamp": person.datetime.isoformat() if person.timestamp else None,
                "battery": person.battery_level,
                "address": person.address,
            }
        )
    return people


# ----------------------------------------------------------- välimuisti ----

_cache = {"data": None, "time": 0.0}
_lock = threading.Lock()


def get_locations(force=False):
    max_age = max(MIN_REFRESH_SECONDS, int(CONFIG.get("refresh_seconds", 60)) - 5)
    if force:
        max_age = MIN_REFRESH_SECONDS
    with _lock:
        if _cache["data"] and time.time() - _cache["time"] < max_age:
            return _cache["data"]

        people, errors = [], []
        for label, fetch in (("iCloud", fetch_icloud), ("Google", fetch_google)):
            try:
                people.extend(fetch())
            except Exception as exc:  # toinen lähde saa toimia vaikka toinen ei
                app.logger.warning("%s-haku epäonnistui: %s", label, exc)
                errors.append({"source": label, "message": str(exc)})

        data = {
            "people": people,
            "errors": errors,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "refresh_seconds": int(CONFIG.get("refresh_seconds", 60)),
        }
        _cache.update(data=data, time=time.time())
        return data


# ----------------------------------------------------------------- web -----


PUBLIC_PATHS = {"/login", "/manifest.webmanifest", "/sw.js"}


@app.before_request
def require_login():
    if not CONFIG.get("app_password") or session.get("ok"):
        return None
    if request.path in PUBLIC_PATHS or request.path.startswith("/static/"):
        return None
    if request.path.startswith("/api/"):
        return jsonify({"error": "login"}), 401
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    error = ""
    if request.method == "POST":
        given = request.form.get("password", "").encode()
        if secrets.compare_digest(given, CONFIG.get("app_password", "").encode()):
            session.permanent = True  # pysyy kirjautuneena vuoden
            session["ok"] = True
            return redirect(url_for("index"))
        time.sleep(1)  # hidastaa arvailua
        error = "Väärä salasana"
    page = (BASE_DIR / "static" / "login.html").read_text(encoding="utf-8")
    return page.replace("{{error}}", error)


@app.get("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.get("/manifest.webmanifest")
def manifest():
    return send_from_directory(
        app.static_folder, "manifest.webmanifest", mimetype="application/manifest+json"
    )


@app.get("/sw.js")
def service_worker():
    # palvellaan juuresta, jotta service worker kattaa koko sovelluksen
    return send_from_directory(app.static_folder, "sw.js", mimetype="text/javascript")


@app.get("/api/locations")
def api_locations():
    return jsonify(get_locations(force=request.args.get("refresh") == "1"))


if __name__ == "__main__":
    host = CONFIG.get("host", "127.0.0.1")
    if host != "127.0.0.1" and not CONFIG.get("app_password"):
        raise SystemExit(
            "Aseta config.jsoniin app_password ennen kuin avaat sovelluksen muille laitteille."
        )
    if _google_cookie_file():
        threading.Thread(target=_google_keepalive, daemon=True).start()
    app.run(host=host, port=int(CONFIG.get("port", 8080)))
