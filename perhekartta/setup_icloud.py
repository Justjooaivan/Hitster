"""Kertaluonteinen iCloud-kirjautuminen kaksivaiheisella tunnistuksella.

Aja:  python setup_icloud.py
Apple lähettää vahvistuskoodin puhelimeesi. Kun koodi on syötetty, istunto
tallentuu kansioon icloud_session/ eikä koodia kysytä joka kerta.
Aja tämä uudelleen, jos sovellus joskus ilmoittaa iCloud-tunnistuksen vanhentuneen.
"""

import json
from pathlib import Path

from pyicloud import PyiCloudService

BASE_DIR = Path(__file__).resolve().parent
cfg = json.loads((BASE_DIR / "config.json").read_text(encoding="utf-8"))["icloud"]

api = PyiCloudService(
    cfg["apple_id"],
    cfg.get("password") or None,
    cookie_directory=str(BASE_DIR / "icloud_session"),
    with_family=True,
    refresh_interval=None,
)

if api.requires_2fa:
    # pyydetään Applea lähettämään koodi (tekstiviesti tai Apple-laitteen ilmoitus)
    try:
        api.request_2fa_code()
    except Exception as exc:
        print(f"Koodin pyytäminen ei onnistunut ({exc}). Jos sait koodin silti, syötä se.")
    if api.two_factor_delivery_method == "sms":
        print("Apple lähettää koodin tekstiviestinä puhelimeesi.")
    else:
        print("Apple lähettää koodin Apple-laitteellesi.")

    for attempt in range(3):
        code = input("Syötä 6-numeroinen koodi: ").strip().replace(" ", "")
        if api.validate_2fa_code(code):
            break
        print("Koodi ei kelvannut, yritä uudelleen.")
    else:
        raise SystemExit("Koodi ei kelvannut kolmella yrityksellä. Aja skripti uudelleen.")
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
