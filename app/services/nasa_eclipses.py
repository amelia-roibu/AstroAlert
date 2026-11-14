from datetime import date, time, datetime, timedelta
from bs4 import BeautifulSoup
import re

MONTHS = {
    "Jan": 1,
    "Feb": 2,
    "Mar": 3,
    "Apr": 4,
    "May": 5,
    "Jun": 6,
    "Jul": 7,
    "Aug": 8,
    "Sep": 9,
    "Oct": 10,
    "Nov": 11,
    "Dec": 12
}

def parse_nasa_eclipses(html: str, eclipse_type: str) -> list[dict]:
    if eclipse_type not in ("solar", "lunar"):
        raise ValueError("Eclipse type must be solar or lunar")

    soup = BeautifulSoup(html, "html.parser")
    tables = soup.find_all("table")

    if not tables:
        raise ValueError("NASA catalog contains no tables")

    rows = tables[0].find_all("tr")

    normalized = []

    for row in rows:
        cells = row.find_all("td")
        if len(cells) != 7:
            continue

        values = [cell.get_text(" ", strip=True) for cell in cells]
        date_text, time_text, subtype, saros, magnitude, duration, visibility = values

        if not re.fullmatch(r"\d{4} [A-Z][a-z]{2} \d{2}", date_text):
            continue

        date_parts = date_text.split()

        if len(date_parts) != 3:
            raise ValueError(f"Invalid NASA date: {date_text}")

        year = int(date_parts[0])
        month = MONTHS[date_parts[1]]
        day = int(date_parts[2])

        event_date = date(year, month, day)

        hour, minute, second = map(int, time_text.split(":"))
        if second == 60:
            greatest_eclipse_td = (datetime.combine(event_date, time(hour, minute)) + timedelta(minutes=1)).time()
        else:
            greatest_eclipse_td = time(hour, minute, second)

        normalized.append({"id": f"NASA-{eclipse_type.upper()}-{event_date.isoformat()}",
                            "name": f"{subtype} {eclipse_type.capitalize()} Eclipse of {date_text}",
                            "event_date": event_date,
                            "source": "NASA",
                            "eclipse_type": eclipse_type,
                            "eclipse_subtype": subtype.lower(),
                            "greatest_eclipse_td": greatest_eclipse_td,
                            "magnitude": float(magnitude),
                            "saros_number": int(saros),
                            "duration": duration if duration != "-" else None,
                            "visibility_regions": visibility})

    return normalized