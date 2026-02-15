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
