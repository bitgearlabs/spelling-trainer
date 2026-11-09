"""Sinh đề ngẫu nhiên cho 6 dạng bài đánh vần và nghe số."""
import random
import datetime
from dataclasses import dataclass

CATEGORIES = {
    "phone": "Phone Numbers",
    "code": "Postcodes / Codes",
    "name": "Names / Streets",
    "date": "Dates & Ordinals",
    "money": "Currency",
    "measure": "Measurements",
}


@dataclass
class Item:
    category: str   # key trong CATEGORIES
    kind: str       # phone | text | number | date | ordinal | money | measure
    spoken: str     # văn bản đưa cho TTS
    answer: str     # đáp án hiển thị
    hint: str       # gợi ý định dạng
    extra: dict = None


# ---------- số -> chữ ----------
ONES = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine",
        "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen",
        "seventeen", "eighteen", "nineteen"]
TENS = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]
ORD_SPECIAL = {"one": "first", "two": "second", "three": "third", "five": "fifth",
               "eight": "eighth", "nine": "ninth", "twelve": "twelfth"}


def num_words(n: int) -> str:
    if n < 20:
        return ONES[n]
    if n < 100:
        return TENS[n // 10] + ("-" + ONES[n % 10] if n % 10 else "")
    if n < 1000:
        r = n % 100
        return ONES[n // 100] + " hundred" + (" and " + num_words(r) if r else "")
    for div, name in ((1_000_000, "million"), (1000, "thousand")):
        if n >= div:
            r = n % div
            tail = ""
            if r:
                tail = (" and " if r < 100 else " ") + num_words(r)
            return num_words(n // div) + " " + name + tail
    return str(n)


def ordinal_words(n: int) -> str:
    w = num_words(n)
    head, sep, last = w.rpartition("-") if "-" in w.split(" ")[-1] else w.rpartition(" ")
    if last in ORD_SPECIAL:
        last = ORD_SPECIAL[last]
    elif last.endswith("y"):
        last = last[:-1] + "ieth"
    else:
        last += "th"
    return head + sep + last


def ordinal_suffix(n: int) -> str:
    if 10 <= n % 100 <= 20:
        return "th"
    return {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")


def decimal_words(x: float) -> str:
    s = f"{x:g}"
    if "." not in s:
        return num_words(int(s))
    i, d = s.split(".")
    return num_words(int(i)) + " point " + " ".join(ONES[int(c)] for c in d)


# ---------- đánh vần ----------
LETTER = {"A": "ay", "B": "bee", "C": "see", "D": "dee", "E": "ee", "F": "eff", "G": "jee",
          "H": "aitch", "I": "eye", "J": "jay", "K": "kay", "L": "ell", "M": "em", "N": "en",
          "O": "oh", "P": "pee", "Q": "queue", "R": "ar", "S": "ess", "T": "tee", "U": "you",
          "V": "vee", "W": "double you", "X": "ex", "Y": "why", "Z": "zed"}


def speak_chars(s: str, zero_word="zero", use_double=True, zee=False) -> str:
    """Đọc từng ký tự, gộp ký tự lặp thành double/triple, ngăn cách bằng dấu phẩy."""
    out, i = [], 0
    s = s.replace(" ", "")
    while i < len(s):
        c = s[i]
        run = 1
        while use_double and i + run < len(s) and s[i + run] == c and run < 3:
            run += 1
        if c.isdigit():
            word = zero_word if c == "0" else ONES[int(c)]
        else:
            word = "zee" if zee and c.upper() == "Z" else LETTER[c.upper()]
        if run == 2:
            word = "double " + word
        elif run == 3:
            word = "triple " + word
        out.append(word)
        i += run
    return ", ".join(out)


@dataclass
class Opts:
    """Tuỳ chọn đọc: double/triple, oh/zero, hard mode, accent Mỹ (zee)."""
    double: bool = True
    zero: str = "random"   # random | oh | zero
    hard: bool = False     # cho phép chữ O/I trong mã
    us: bool = False

    def zero_word(self) -> str:
        return random.choice(["oh", "zero"]) if self.zero == "random" else self.zero


# ---------- dữ liệu ----------
SURNAMES = ["Beattie", "Kowalski", "Thackeray", "Llewellyn", "Fitzgerald", "Mackenzie", "Bellamy",
            "Pickering", "Wainwright", "Abernathy", "Chatterjee", "Hargreaves", "Nakamura",
            "Cavanagh", "Pemberton", "Ellsworth", "Sutcliffe", "Yarborough", "Zielinski", "Rathbone",
            "Gallagher", "Whitcombe", "Ogilvie", "Dunmore", "Tennyson", "Hollingsworth"]
FIRST = ["Oliver", "Sophie", "Jack", "Amelia", "Harry", "Chloe", "Daniel", "Priya", "Liam", "Fiona"]
STREETS = ["Wolverhampton", "Kensington", "Marlborough", "Cheswick", "Lavender", "Queensbridge",
           "Hawthorne", "Stanmore", "Wellington", "Fairweather", "Penrose", "Oakridge", "Thornbury",
           "Greenwich", "Ashworth", "Bakewell", "Elmhurst", "Sycamore", "Whitechapel", "Ravensdale"]
STREET_TYPES = ["Road", "Street", "Avenue", "Lane", "Close", "Drive", "Gardens", "Crescent"]
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August",
          "September", "October", "November", "December"]
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# (dạng đọc số ít, số nhiều, hiển thị, alias, min, max, số thập phân?)
UNITS = [
    ("kilometre", "kilometres", "km", ["km", "kilometre", "kilometres", "kilometer", "kilometers"], 1, 120, True),
    ("metre", "metres", "m", ["m", "metre", "metres", "meter", "meters"], 2, 900, True),
    ("centimetre", "centimetres", "cm", ["cm", "centimetre", "centimetres", "centimeter", "centimeters"], 5, 250, True),
    ("kilogram", "kilograms", "kg", ["kg", "kilogram", "kilograms", "kilo", "kilos"], 1, 95, True),
    ("gram", "grams", "g", ["g", "gram", "grams"], 20, 900, False),
    ("litre", "litres", "l", ["l", "litre", "litres", "liter", "liters"], 1, 60, True),
    ("millilitre", "millilitres", "ml", ["ml", "millilitre", "millilitres", "milliliter", "milliliters"], 50, 900, False),
    ("mile", "miles", "miles", ["mile", "miles", "mi"], 1, 80, True),
    ("square metre", "square metres", "m²", ["m2", "m²", "sqm", "squaremetre", "squaremetres", "squaremeter", "squaremeters"], 10, 400, False),
    ("degree Celsius", "degrees Celsius", "°C", ["c", "°c", "degreec", "degreesc", "degreecelsius", "degreescelsius", "celsius"], 3, 38, False),
    ("percent", "percent", "%", ["%", "percent", "percentage", "percentage", "percent", "per cent"], 5, 95, False),
]

CURRENCIES = [
    ("£", "pound", "pounds", "pence", ["£"]),
    ("$", "dollar", "dollars", "cents", ["$"]),
    ("€", "euro", "euros", "cents", ["€"]),
    ("A$", "Australian dollar", "Australian dollars", "cents", ["a$"]),
]


# ---------- generators ----------
def gen_phone(o: Opts) -> Item:
    if random.random() < 0.25:  # số lớn thuần túy
        n = random.choice([random.randint(1000, 99999), random.randint(100000, 3_000_000)])
        return Item("phone", "number", num_words(n), f"{n:,}", "Write the number (e.g. 12,500)")
    style = random.choice(["uk_mobile", "uk_land", "au_mobile", "us"])
    if style == "uk_mobile":
        d = "07" + "".join(random.choice("0123456789") for _ in range(9))
        groups = [d[:5], d[5:8], d[8:]]
    elif style == "uk_land":
        d = "01" + "".join(random.choice("0123456789") for _ in range(9))
        groups = [d[:5], d[5:8], d[8:]]
    elif style == "au_mobile":
        d = "04" + "".join(random.choice("0123456789") for _ in range(8))
        groups = [d[:4], d[4:7], d[7:]]
    else:
        d = "".join(random.choice("23456789") for _ in range(3)) + "".join(random.choice("0123456789") for _ in range(7))
        groups = [d[:3], d[3:6], d[6:]]
    zero = o.zero_word()
    spoken = ",, ".join(speak_chars(g, zero_word=zero, use_double=o.double, zee=o.us) for g in groups)
    return Item("phone", "phone", spoken, " ".join(groups), "Write the phone number")


def gen_code(o: Opts) -> Item:
    L = "ABCDEFGHJKLMNPRSTUVWXYZ" + ("OI" if o.hard else "")
    kw = dict(zero_word=o.zero_word(), use_double=o.double, zee=o.us)
    D = "0123456789"
    if random.random() < 0.55:  # UK postcode
        area = "".join(random.choice(L) for _ in range(random.choice([1, 2])))
        out = area + random.choice(D[1:]) + random.choice(["", "", random.choice(D), random.choice("ABCDEFGHJK")])
        inn = random.choice(D) + "".join(random.choice(L) for _ in range(2))
        answer = f"{out} {inn}"
        spoken = f"{speak_chars(out, **kw)},, {speak_chars(inn, **kw)}"
        hint = "Write the UK postcode"
    else:
        letters = "".join(random.choice(L) for _ in range(random.choice([2, 3])))
        digits = "".join(random.choice(D) for _ in range(random.choice([4, 5, 6])))
        answer = random.choice([f"{letters}{digits}", f"{letters}-{digits}"])
        spoken = f"{speak_chars(letters, **kw)},, {speak_chars(digits, **kw)}"
        hint = "Write the reference / booking code"
    return Item("code", "text", spoken, answer, hint)


def gen_name(o: Opts) -> Item:
    kw = dict(use_double=o.double, zee=o.us)
    if random.random() < 0.5:
        name = random.choice(SURNAMES)
        first = random.choice(FIRST)
        spoken = f"The surname is {speak_chars(name, **kw)}"
        return Item("name", "text", spoken, name, f"Write the surname of {first}")
    street = random.choice(STREETS)
    stype = random.choice(STREET_TYPES)
    spoken = f"The street is {speak_chars(street, **kw)},, {stype}"
    return Item("name", "text", spoken, f"{street} {stype}", "Write the street name")


def gen_date(o: Opts = None) -> Item:
    if random.random() < 0.7:
        start = datetime.date(2026, 1, 1)
        dt = start + datetime.timedelta(days=random.randint(0, 364))
        day, month, wd = dt.day, MONTHS[dt.month - 1], WEEKDAYS[dt.weekday()]
        if random.random() < 0.5:
            spoken = f"{wd}, the {ordinal_words(day)} of {month}"
        else:
            spoken = f"{month} the {ordinal_words(day)}"
        return Item("date", "date", spoken, f"{day} {month}", "Write the date (e.g. 22 March)",
                    {"day": day, "month": dt.month})
    n = random.randint(2, 99)
    ctx = random.choice(["the {} floor", "the {} of the month", "the {} edition", "the {} anniversary",
                         "the {} platform", "his {} birthday"])
    spoken = ctx.format(ordinal_words(n))
    return Item("date", "ordinal", spoken, f"{n}{ordinal_suffix(n)}", "Write the ordinal number (e.g. 21st)",
                {"n": n})


def gen_money(o: Opts = None) -> Item:
    sym, sing, plur, minor, _ = random.choice(CURRENCIES)
    r = random.random()
    major = random.choice([random.randint(2, 99), random.randint(100, 999), random.randint(1000, 25000)])
    cents = random.choice([0, 0, 5, 10, 20, 25, 45, 50, 75, 95, 99]) if r < 0.6 else 0
    major_w = num_words(major) + " " + (plur if major != 1 else sing)
    if cents:
        spoken = f"{major_w} and {num_words(cents)} {minor}" if random.random() < 0.5 else f"{major_w} {num_words(cents)}"
        ans = f"{sym}{major:,}.{cents:02d}"
    else:
        spoken = major_w
        ans = f"{sym}{major:,}"
    return Item("money", "money", spoken, ans, "Write the amount with currency symbol (e.g. £45.50)",
                {"sym": sym.lower(), "value": major + cents / 100})


def gen_measure(o: Opts = None) -> Item:
    sing, plur, disp, aliases, lo, hi, dec = random.choice(UNITS)
    v = random.randint(lo, hi)
    if dec and random.random() < 0.45:
        v = round(random.uniform(lo, min(hi, 60)), random.choice([1, 1, 2]))
    spoken_num = decimal_words(v)
    unit = sing if v == 1 else plur
    spoken = f"{spoken_num} {unit}"
    aliases = [a.replace(" ", "") for a in aliases]
    return Item("measure", "measure", spoken, f"{v:g} {disp}", "Write the measurement with unit (e.g. 2.5 km)",
                {"value": float(v), "aliases": aliases})


GENERATORS = {"phone": gen_phone, "code": gen_code, "name": gen_name,
              "date": gen_date, "money": gen_money, "measure": gen_measure}


def generate(category: str, opts: Opts = None) -> Item:
    return GENERATORS[category](opts or Opts())
