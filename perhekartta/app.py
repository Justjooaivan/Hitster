"""Perhekartta: näyttää iCloudin (iPhone) ja Googlen (Android) sijainnit samalla kartalla.

Käynnistys:  python app.py
Asetukset:   config.json (katso config.example.json)
"""

import json
import secrets
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, Response, jsonify, request, send_from_directory

BASE_DIR = Path(__file__).resolve().parent
CONFIG_FILE = BASE_DIR / "config.json"
ICLOUD_SESSION_DIR = BASE_DIR / "icloud_session"
MIN_REFRESH_SECONDS = 15  # ei kuormiteta Applea ja Googlea turhaan

app = Flask(__name__, static_folder=str(BASE_DIR / "static"))


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


def fetch_google():
    cfg = CONFIG.get("google")
    if not cfg or not cfg.get("account"):
        return []
    from locationsharinglib import Service

    cookies = BASE_DIR / cfg.get("cookies_file", "google_cookies.txt")
    if not cookies.exists():
        raise RuntimeError(f"Google-evästetiedostoa ei löydy: {cookies.name}")
    service = Service(cookies_file=str(cookies), authenticating_account=cfg["account"])
    wanted = cfg.get("people") or {}

    people = []
    for person in service.get_shared_people():
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


@app.before_request
def require_password():
    password = CONFIG.get("app_password")
    if not password:
        return None
    auth = request.authorization
    if auth and secrets.compare_digest(
        (auth.password or "").encode(), password.encode()
    ):
        return None
    return Response(
        "Kirjaudu sisään", 401, {"WWW-Authenticate": 'Basic realm="Perhekartta"'}
    )


@app.get("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.get("/api/locations")
def api_locations():
    return jsonify(get_locations(force=request.args.get("refresh") == "1"))


if __name__ == "__main__":
    host = CONFIG.get("host", "127.0.0.1")
    if host != "127.0.0.1" and not CONFIG.get("app_password"):
        raise SystemExit(
            "Aseta config.jsoniin app_password ennen kuin avaat sovelluksen muille laitteille."
        )
    app.run(host=host, port=int(CONFIG.get("port", 8080)))
