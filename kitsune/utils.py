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
