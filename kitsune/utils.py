from urllib.parse import urlparse
from datetime import datetime, timezone


def dedent(text: str) -> str:
    lines = text.split("\n")

    if lines and lines[0].strip() == "":
        lines.pop(0)
    if lines and lines[-1].strip() == "":
        lines.pop()

    non_empty = [line for line in lines if line.strip()]
    if not non_empty:
        return ""

    indent = min(len(line) - len(line.lstrip()) for line in non_empty)
    return "\n".join(line[indent:] for line in lines)


def prose(text: str) -> str:
    return dedent(text).replace("\n", " ")


def is_public_url(url: str) -> bool:
    try:
        parsed = urlparse(url)

        if parsed.scheme not in ("http", "https"):
            return False

        h = parsed.hostname
        if not h:
            return False

        if (
            h == "localhost"
            or h in ("[::1]", "::1")
            or h.startswith("127.")
            or h.startswith("10.")
            or h.startswith("192.168.")
            or h.startswith("0.")
            or h == "169.254.169.254"
        ):
            return False

        if h.startswith("172."):
            parts = h.split(".")
            try:
                octet = int(parts[1]) if len(parts) > 1 else -1
            except ValueError:
                octet = -1
            if 16 <= octet <= 31:
                return False

        return True
    except Exception:
        return False


def get_current_datetime(date: datetime | None = None) -> str:
    if date is None:
        date = datetime.now()

    day_names = [
        "Sunday",
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
    ]
    day_of_week = day_names[(date.weekday() + 1) % 7]
    day = date.day

    month_names = [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ]
    month = month_names[date.month - 1]
    year = date.year

    hours = date.hour
    minutes = str(date.minute).zfill(2)
    ampm = "PM" if hours >= 12 else "AM"

    hours = hours % 12
    hours = hours if hours else 12

    return f"{day_of_week} {day} {month} {year} {hours}:{minutes} {ampm}"


def get_current_date(date: datetime | None = None) -> str:
    if date is None:
        date = datetime.now(timezone.utc)
    elif date.tzinfo is None:
        date = date.replace(tzinfo=timezone.utc)
    else:
        date = date.astimezone(timezone.utc)

    return f"Current date (UTC): {date.date().isoformat()}"
