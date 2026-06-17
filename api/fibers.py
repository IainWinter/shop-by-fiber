"""Fiber composition parsing and inference.

Parses explicit compositions like "95% Cotton, 5% Spandex" from product text.
When no explicit composition exists, infers likely fibers from domain knowledge:
e.g. machine-washable wool is generally superwash, "stretch" implies spandex,
"sport"/"performance" implies polyester.
"""

import re
import html as html_lib

# canonical fiber name -> aliases (lowercase)
FIBER_ALIASES = {
    "cotton": ["cotton", "organic cotton", "recycled cotton", "pima cotton", "supima cotton", "supima"],
    "polyester": ["polyester", "recycled polyester", "poly", "repreve"],
    "nylon": ["nylon", "polyamide", "recycled nylon", "cordura"],
    "spandex": ["spandex", "elastane", "lycra", "elasterell"],
    "merino wool": ["merino", "merino wool"],
    "wool": ["wool", "lambswool", "lambs wool", "virgin wool", "shetland wool", "yak wool"],
    "cashmere": ["cashmere"],
    "alpaca": ["alpaca"],
    "mohair": ["mohair"],
    "silk": ["silk"],
    "linen": ["linen", "flax"],
    "hemp": ["hemp"],
    "viscose": ["viscose", "rayon", "bamboo viscose", "bamboo rayon", "bamboo"],
    "modal": ["modal", "micromodal"],
    "lyocell": ["lyocell", "tencel"],
    "acrylic": ["acrylic"],
    "polypropylene": ["polypropylene"],
    "cupro": ["cupro"],
    "acetate": ["acetate", "triacetate"],
    "down": ["down", "duck down", "goose down"],
    "leather": ["leather"],
    "ramie": ["ramie"],
}

ALIAS_TO_FIBER = {}
for canon, aliases in FIBER_ALIASES.items():
    for a in aliases:
        ALIAS_TO_FIBER[a] = canon

# longest aliases first so "merino wool" beats "wool"
_SORTED_ALIASES = sorted(ALIAS_TO_FIBER, key=len, reverse=True)
_ALIAS_PATTERN = "|".join(re.escape(a) for a in _SORTED_ALIASES)

# "95% cotton" / "95 % organic cotton"
_PCT_FIRST = re.compile(
    r"(\d{1,3}(?:\.\d+)?)\s*%\s*(?:recycled |organic |virgin |brushed |combed |ringspun |ring-spun )*(" + _ALIAS_PATTERN + r")\b",
    re.IGNORECASE,
)
# "cotton 95%" / "Cotton: 95%"
_FIBER_FIRST = re.compile(
    r"\b(" + _ALIAS_PATTERN + r")\s*[:\-]?\s*(\d{1,3}(?:\.\d+)?)\s*%",
    re.IGNORECASE,
)

_TAG_RE = re.compile(r"<[^>]+>")


def strip_html(text: str) -> str:
    if not text:
        return ""
    return html_lib.unescape(_TAG_RE.sub(" ", text))


def parse_composition(text: str):
    """Extract explicit fiber percentages. Returns list of {fiber, pct}."""
    found = {}
    for m in _PCT_FIRST.finditer(text):
        pct, name = float(m.group(1)), m.group(2).lower()
        fiber = ALIAS_TO_FIBER.get(name)
        if fiber and 0 < pct <= 100:
            found.setdefault(fiber, pct)
    for m in _FIBER_FIRST.finditer(text):
        name, pct = m.group(1).lower(), float(m.group(2))
        fiber = ALIAS_TO_FIBER.get(name)
        if fiber and 0 < pct <= 100 and fiber not in found:
            found[fiber] = pct
    return [{"fiber": f, "pct": p} for f, p in sorted(found.items(), key=lambda kv: -kv[1])]


# Inference rules: (regex over full text, fibers implied, reason)
INFERENCE_RULES = [
    (re.compile(r"\b(stretch|stretchy|4-way|four-way)\b", re.I), ["polyester", "spandex"], "stretch implies polyester/spandex"),
    (re.compile(r"\b(sport|performance|athletic|training|workout|gym|running|active)\b", re.I), ["polyester"], "sport/performance implies polyester"),
    (re.compile(r"\b(fleece|sherpa)\b", re.I), ["polyester"], "fleece is typically polyester"),
    (re.compile(r"\b(moisture[- ]wicking|quick[- ]dry(?:ing)?|sweat[- ]wicking)\b", re.I), ["polyester"], "wicking fabrics are typically polyester"),
    (re.compile(r"\b(denim|jeans?|chino|oxford|t-?shirts?|tee)\b", re.I), ["cotton"], "denim/chino/tee is typically cotton"),
    (re.compile(r"\b(swim|board\s?shorts?|bikini)\b", re.I), ["polyester", "spandex"], "swimwear is typically polyester/spandex"),
    (re.compile(r"\b(waterproof|rain\s?(jacket|coat|shell)|windbreaker)\b", re.I), ["nylon"], "rain/wind shells are typically nylon"),
    (re.compile(r"\b(puffer|down\s+(jacket|vest|parka))\b", re.I), ["down", "nylon"], "puffers are typically down with nylon shell"),
]

# fiber names mentioned without a percent still tell us composition
_MENTION_RE = re.compile(r"\b(" + _ALIAS_PATTERN + r")\b", re.IGNORECASE)

_MACHINE_WASH_RE = re.compile(r"\bmachine[- ]wash", re.I)


def infer_fibers(text: str):
    """Infer fibers from keywords when no explicit composition. Returns (fibers, reasons)."""
    fibers, reasons = [], []

    # direct fiber mentions without percentages (e.g. "merino wool tee")
    mentioned = []
    for m in _MENTION_RE.finditer(text):
        fiber = ALIAS_TO_FIBER.get(m.group(1).lower())
        if fiber and fiber not in mentioned:
            mentioned.append(fiber)
    if mentioned:
        fibers.extend(mentioned)
        reasons.append("fiber named in description")

    for pattern, implied, reason in INFERENCE_RULES:
        if pattern.search(text):
            added = [f for f in implied if f not in fibers]
            if added:
                fibers.extend(added)
                reasons.append(reason)

    return [{"fiber": f, "pct": None} for f in fibers], reasons


def annotate(fibers, text):
    """Apply knowledge-based annotations, e.g. machine-washable wool => superwash."""
    if _MACHINE_WASH_RE.search(text):
        for f in fibers:
            if f["fiber"] in ("wool", "merino wool"):
                f["note"] = "machine washable, likely superwash"
    return fibers


def analyze(title: str, body_html: str, tags, product_type: str):
    """Full analysis. Returns (fibers, source, summary)."""
    tag_text = " ".join(tags) if isinstance(tags, list) else str(tags or "")
    text = " ".join([title or "", strip_html(body_html or ""), tag_text, product_type or ""])

    fibers = parse_composition(text)
    if fibers:
        fibers = annotate(fibers, text)
        source = "parsed"
        summary = ", ".join(
            f"{f['pct']:g}% {f['fiber']}" + (f" ({f['note']})" if f.get("note") else "")
            for f in fibers
        )
        return fibers, source, summary

    fibers, reasons = infer_fibers(text)
    if fibers:
        fibers = annotate(fibers, text)
        summary = ", ".join(
            f["fiber"] + (f" ({f['note']})" if f.get("note") else "") for f in fibers
        ) + " (inferred: " + "; ".join(reasons) + ")"
        return fibers, "inferred", summary

    return [], "unknown", "unknown"
