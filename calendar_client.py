
import caldav
from datetime import datetime, date
import re
import time

def add_event(header, text, date_str, calendar_icalendar_server, calendar_user, calendar_pass, calendar_id):#warning - this function is ganerated by AI
    print(f"Přidávám událost: {header} | {date_str}")

    # --- 1. Vyčištění a oprava data ---
    date_str = date_str.strip()

    # Oprava: 2025-03-00 → 2025-03-01
    date_str = re.sub(r'-(\d{2})-00T', r'-\1-01T', date_str)

    # Nahradíme T mezerou (pro fromisoformat)
    date_str = date_str.replace('T', ' ')

    # Pokud není čas, přidáme 00:00
    if ' ' not in date_str and len(date_str) == 10:
        date_str += " 00:00"

    # --- 2. Pokus o parsování ---
    dt = None
    formats = [
        "%Y-%m-%d %H:%M",      # 2025-03-01 23:00
        "%Y-%m-%d %H:%M:%S",    # s vteřinami
        "%Y-%m-%d",            # jen datum
        "%d.%m.%Y %H:%M",      # české
        "%d/%m/%Y %H:%M",
    ]

    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            break
        except ValueError:
            continue

    # --- 3. Fallback: dnešek ---
    if dt is None:
        print(f"Varování: Neplatný formát data '{date_str}', použije se dnešek.")
        dt = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)

    # --- 4. Přidání do kalendáře ---
    try:
        client = caldav.DAVClient(url=calendar_icalendar_server, username=calendar_user, password=calendar_pass)
        principal = client.principal()
        calendar = principal.calendar(cal_id=calendar_id)

        event = calendar.save_event(
            summary=header,
            description=text,
            dtstart=dt,
            dtend=dt.replace(hour=(dt.hour + 1) % 24)  # +1 hodina
        )
        print(f"Událost úspěšně přidána: {header}")
        return event
    except Exception as e:
        print(f"Chyba při přidávání do kalendáře: {e}")
        return None