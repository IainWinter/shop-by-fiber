"""Affiliate / referral deep-linking.

HOW IT WORKS
  An affiliate link = the product URL wrapped with YOUR tracking IDs.
  You get those IDs only AFTER a program approves you. Until then, links
  fall through to the plain product URL (site works, just earns nothing).

TO TURN ON A NETWORK
  1. Apply + get approved (see signup URLs in BRANDS below).
  2. From the network dashboard, copy your publisher/affiliate ID into
     PUBLISHER_IDS. ONE id usually lights up EVERY brand on that network.
  3. For some networks you also need each brand's merchant id (mid) — fill
     it in BRANDS. A few you already have from research.

WHAT EARNS RIGHT AWAY ONCE IDs ARE IN
  - AvantLink, Awin, Rakuten, CJ: single deep-link format, fully automated here.
  - Impact, Partnerize, FlexOffers: each brand gives its OWN deep-link/tracking
    template (per-advertiser subdomain). Paste that brand's template into its
    `template` field (use {url} where the encoded product URL goes).

Verified June 2026. ★ = confirmed on the brand's own page; others approximate.
"""

from urllib.parse import quote, urlparse, urlunparse, urlencode, parse_qsl

# ── Your IDs. Fill after approval. Empty string = that network stays off. ──
PUBLISHER_IDS = {
    "avantlink": "",    # AvantLink: your affiliate id  (dashboard → Account → Affiliate ID)
    "awin": "",         # Awin: your publisher id "awinaffid"
    "rakuten": "",      # Rakuten: your LinkSynergy publisher id "id="
    "cj": "",           # CJ: your website/PID
}

# ── Per-network deep-link format. {pub}=your id, {mid}=merchant id, {url}=encoded product url. ──
NETWORK_TEMPLATES = {
    "avantlink": "https://www.avantlink.com/click.php?tt=cl&mi={mid}&pw={pub}&url={url}",
    "awin":      "https://www.awin1.com/cread.php?awinmid={mid}&awinaffid={pub}&ued={url}",
    "rakuten":   "https://click.linksynergy.com/deeplink?id={pub}&mid={mid}&murl={url}",
    "cj":        "https://www.anrdoezrs.net/links/{pub}/type/dlg/{url}",
}

# ── Brands. mid = merchant id on that network (fill from dashboard if blank). ──
#    template = a full per-brand deep link with {url} (for Impact/Partnerize/FlexOffers).
BRANDS = {
    # AvantLink ----------------------------------------------------------------
    "www.marinelayer.com": {"network": "avantlink", "mid": "", "signup": "https://www.avantlink.com/programs/18549/marine-layer-affiliate-program/", "rate": "8%"},
    "www.outerknown.com":  {"network": "avantlink", "mid": "", "signup": "https://www.avantlink.com/programs/18913/outerknown-affiliate-program/", "rate": "n/s"},
    "ridgemerino.com":     {"network": "avantlink", "mid": "15517", "signup": "https://www.avantlink.com/signup/affiliate/us?merchant=15517", "rate": "8% ★"},
    "shop.ibex.com":       {"network": "avantlink", "mid": "", "signup": "https://ibex.com/pages/affiliate-program", "rate": "~5-10%"},
    "www.janji.com":       {"network": "avantlink", "mid": "", "signup": "https://www.avantlink.com/programs/15989/janji--affiliate-program/", "rate": "14%"},

    # Awin (ex-ShareASale, shut down Oct 2025) ---------------------------------
    "www.ministryofsupply.com": {"network": "awin", "mid": "", "signup": "https://www.awin.com/us/publishers", "rate": "~3%"},
    "www.tracksmith.com":       {"network": "awin", "mid": "", "signup": "https://www.awin.com/us/publishers", "rate": "n/s (24h cookie!)"},
    "www.birddogs.com":         {"network": "awin", "mid": "", "signup": "https://www.awin.com/us/publishers", "rate": "~10%"},

    # Rakuten ------------------------------------------------------------------
    "fahertybrand.com":   {"network": "rakuten", "mid": "48993", "signup": "https://signup.linksynergy.com/publishers/registration/landing?mid=48993", "rate": "~4-7%"},
    "www.mackweldon.com": {"network": "rakuten", "mid": "", "signup": "https://commerce.sovrn.com/merchants/144477/mack-weldon-affiliate-program", "rate": "~2.8% (network unclear)"},

    # CJ -----------------------------------------------------------------------
    "www.stance.com": {"network": "cj", "mid": "", "signup": "https://www.cj.com", "rate": "8%"},

    # Impact — paste each brand's own deep-link template into `template` once joined.
    "www.allbirds.com":     {"network": "impact", "template": "", "signup": "https://app.impact.com/campaign-campaign-info-v2/Allbirds.brand", "rate": "~12%"},
    "www.taylorstitch.com": {"network": "impact", "template": "", "signup": "https://app.impact.com/campaign-mediapartner-signup/Taylor-Stitch.brand", "rate": "~6%"},
    "www.cotopaxi.com":     {"network": "impact", "template": "", "signup": "https://app.impact.com/advertiser-advertiser-info/Cotopaxi.brand", "rate": "up to 14% ★"},
    "unboundmerino.com":    {"network": "impact", "template": "", "signup": "https://app.impact.com/campaign-promo-signup/Unbound-Merino.brand", "rate": "10-12% ★"},
    "www.toadandco.com":    {"network": "impact", "template": "", "signup": "https://www.toadandco.com/pages/affiliate-program", "rate": "n/s"},
    "www.chubbies.com":     {"network": "impact", "template": "", "signup": "https://app.impact.com/ (search Chubbies)", "rate": "~3-10%"},

    # Partnerize ---------------------------------------------------------------
    "huckberry.com": {"network": "partnerize", "template": "", "signup": "https://join.partnerize.com/huckberry/en_us", "rate": "~5-10%"},

    # FlexOffers ---------------------------------------------------------------
    "www.aloyoga.com":        {"network": "flexoffers", "template": "", "signup": "https://www.flexoffers.com/affiliate-programs/alo-yoga-affiliate-program/", "rate": "~14%"},
    "www.oliversapparel.com": {"network": "flexoffers", "template": "", "signup": "https://www.flexoffers.com/ (search Olivers)", "rate": "12%"},

    # Brand-direct / in-house — link format given after you join their portal.
    "www.trueclassictees.com":   {"network": "in-house", "template": "", "signup": "https://www.trueclassictees.com/pages/partners", "rate": "25% new-customer ★"},
    "www.tentree.com":           {"network": "grin",     "template": "", "signup": "https://tentree.grin.live/creators", "rate": "~15%"},
    "girlfriend.com":            {"network": "in-house", "template": "", "signup": "https://girlfriend.com/pages/affiliates", "rate": "~8-10%"},
    "www.spiritualgangster.com": {"network": "in-house", "template": "", "signup": "https://spiritualgangster.com/pages/spiritual-gangster-advocate-application", "rate": "7%"},
    "woolx.com":                 {"network": "in-house", "template": "", "signup": "https://www.woolx.com/pages/become-an-affiliate", "rate": "n/s"},

    # No program found — links stay plain.
    "kith.com":              {"network": None, "note": "no program"},
    "www.aviatornation.com": {"network": None, "note": "no program"},
    "3sixteen.com":          {"network": None, "note": "no program"},
    "freenotecloth.com":     {"network": None, "note": "no program"},
    "www.publicrec.com":     {"network": None, "note": "acquired by NOBULL — dead"},
}


def affiliate_url(url: str) -> str:
    """Wrap a product URL with affiliate tracking, or return it unchanged if the
    brand has no program / IDs aren't filled in yet."""
    if not url:
        return url
    cfg = BRANDS.get(urlparse(url).netloc.lower())
    if not cfg:
        return url

    enc = quote(url, safe="")

    # 1. Brand-specific full template (Impact, Partnerize, FlexOffers, in-house).
    template = cfg.get("template")
    if template:
        return template.replace("{url}", enc)

    # 2. Shared network deep-link (AvantLink, Awin, Rakuten, CJ).
    net = cfg.get("network")
    pub = PUBLISHER_IDS.get(net, "")
    mid = cfg.get("mid", "")
    fmt = NETWORK_TEMPLATES.get(net)
    if fmt and pub and (mid or "{mid}" not in fmt):
        return fmt.format(pub=pub, mid=mid, url=enc)

    # 3. Not configured yet → plain URL.
    return url
