"""Chấm đáp án, chấp nhận nhiều cách viết."""
import re
from generators import Item, MONTHS, WEEKDAYS


def _flat(s: str) -> str:
    return re.sub(r"[\s\-,._]", "", s).lower()


def _num(s: str):
    try:
        return float(s.replace(",", ""))
    except ValueError:
        return None


def _parse_date(s: str):
    t = s.lower()
    for w in WEEKDAYS:
        t = t.replace(w.lower(), " ")
    m = re.search(r"(\d{1,2})\s*[/\-.]\s*(\d{1,2})", t)
    if m:
        return int(m.group(1)), int(m.group(2))
    month = None
    for i, name in enumerate(MONTHS, 1):
        if name.lower() in t or re.search(rf"\b{name[:3].lower()}\b", t):
            month = i
            break
    d = re.search(r"\d{1,2}", t)
    if month and d:
        return int(d.group()), month
    return None


def check(item: Item, user: str) -> bool:
    user = user.strip()
    if not user:
        return False
    k = item.kind
    if k in ("phone", "text"):
        return _flat(user) == _flat(item.answer)
    if k == "number":
        return _flat(user) == _flat(item.answer)
    if k == "date":
        return _parse_date(user) == (item.extra["day"], item.extra["month"])
    if k == "ordinal":
        m = re.fullmatch(r"(\d+)\s*(st|nd|rd|th)?", user.lower())
        return bool(m) and int(m.group(1)) == item.extra["n"]
    if k == "money":
        u = user.lower().replace(" ", "")
        sym = item.extra["sym"]
        if sym not in u:
            return False
        rest = u.replace(sym, "")
        if sym == "$" or sym == "£" or sym == "€":
            pass
        val = _num(rest)
        return val is not None and abs(val - item.extra["value"]) < 0.005
    if k == "measure":
        m = re.fullmatch(r"\s*([\d.,]+)\s*(.*)", user)
        if not m:
            return False
        val = _num(m.group(1))
        unit = re.sub(r"[\s.]", "", m.group(2).lower())
        return (val is not None and abs(val - item.extra["value"]) < 1e-9
                and unit in item.extra["aliases"])
    return False
