"""Kertaluonteinen iCloud-kirjautuminen kaksivaiheisella tunnistuksella.

Aja:  python setup_icloud.py
Apple lähettää vahvistuskoodin puhelimeesi. Kun koodi on syötetty, istunto
tallentuu kansioon icloud_session/ eikä koodia kysytä joka kerta.
Aja tämä uudelleen, jos sovellus joskus ilmoittaa iCloud-tunnistuksen vanhentuneen.
"""

import json
from pathlib import Path

from pyicloud import PyiCloudService
from pyicloud.exceptions import PyiCloudFailedLoginException

BASE_DIR = Path(__file__).resolve().parent
cfg = json.loads((BASE_DIR / "config.json").read_text(encoding="utf-8"))["icloud"]

try:
    api = PyiCloudService(
        cfg["apple_id"],
        cfg.get("password") or None,
        cookie_directory=str(BASE_DIR / "icloud_session"),
        with_family=True,
        refresh_interval=None,
    )
except PyiCloudFailedLoginException:
    raise SystemExit(
        f"Apple ei hyväksynyt tunnusta {cfg['apple_id']!r} ja salasanaa.\n"
        "Tarkista config.jsonista kohdat apple_id ja password (nano config.json)."
    ) from None

if api.requires_2fa:
    # Pyydetään koodi tekstiviestinä. Apple ehdottaa muuten Apple-laitetta,
    # jos tiliin on joskus liitetty sellainen.
    def fetch_phone_number():
        """Kysyy Applelta tiliin liitetyn puhelinnumeron (sama tieto kuin iCloud-sivun
        'Lähetä tekstiviestinä' -valinnassa)."""
        headers = api._get_auth_headers({"Accept": "application/json"})
        try:
            data = api.session.get(api._auth_endpoint, headers=headers).json()
        except Exception as exc:  # Apple voi vastata 409:llä, jolloin tieto on virheen mukana
            try:
                data = exc.response.json()
            except Exception:
                return None
        if not isinstance(data, dict):
            return None
        verification = data.get("phoneNumberVerification") or {}
        numbers = data.get("trustedPhoneNumbers") or verification.get("trustedPhoneNumbers") or []
        phone = (
            data.get("trustedPhoneNumber")
            or verification.get("trustedPhoneNumber")
            or (numbers[0] if numbers else None)
        )
        if not phone:
            print(f"(Applen vastauksessa ei ollut puhelinnumeroa: {sorted(data)})")
            return None
        api._auth_data["trustedPhoneNumber"] = phone
        return phone

    def request_sms():
        if getattr(api, "_trusted_phone_number", lambda: None)() is None:
            phone = fetch_phone_number()
            if phone is None:
                return False
            number = phone.get("numberWithDialCode") or phone.get("obfuscatedNumber")
            if number:
                print(f"Puhelinnumero: {number}")
        api._request_sms_2fa_code()
        return True

    try:
        if request_sms():
            print("Apple lähettää koodin tekstiviestinä puhelimeesi.")
        else:
            api.request_2fa_code()
            print("Apple ei antanut tekstiviestivaihtoehtoa, joten koodi tulee Apple-laitteelle.")
    except Exception as exc:
        print(f"Koodin pyytäminen ei onnistunut ({exc}). Jos sait koodin silti, syötä se.")

    for attempt in range(3):
        code = input("Syötä 6-numeroinen koodi (tai paina Enter, jos tekstiviestiä ei tullut): ")
        code = code.strip().replace(" ", "")
        if not code:
            print("Pyydän uuden tekstiviestin." if request_sms() else "Tekstiviestiä ei voi pyytää.")
            continue
        if api.validate_2fa_code(code):
            break
        print("Koodi ei kelvannut, yritä uudelleen.")
    else:
        raise SystemExit("Koodi ei kelvannut. Aja skripti uudelleen.")
    if not api.is_trusted_session:
        api.trust_session()
elif api.requires_2sa:
    raise SystemExit("Tililläsi on vanha kaksivaiheinen vahvistus (2SA). Ota käyttöön 2FA.")

print("\nKirjautuminen onnistui! Find My -laitteet:")
for device in api.devices:
    loc = device.location
    where = f"{loc['latitude']:.4f}, {loc['longitude']:.4f}" if loc else "ei sijaintia"
    print(f"  - {device.name!r:35} {where}")
print(
    "\nKopioi tyttäresi puhelimen nimi (lainausmerkkien sisältä) config.jsonin"
    ' kohtaan icloud.devices, esim. "Ellan iPhone": "Ella".'
)
