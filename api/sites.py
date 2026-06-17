"""Popular clothing sites that expose the public Shopify /products.json endpoint."""

SITES = [
    # (domain, brand)
    ("www.allbirds.com", "Allbirds"),
    ("www.aloyoga.com", "Alo Yoga"),
    ("www.taylorstitch.com", "Taylor Stitch"),
    ("www.cotopaxi.com", "Cotopaxi"),
    ("www.tentree.com", "Tentree"),
    ("kith.com", "Kith"),
    ("www.marinelayer.com", "Marine Layer"),
    ("fahertybrand.com", "Faherty"),
    ("www.outerknown.com", "Outerknown"),
    ("girlfriend.com", "Girlfriend Collective"),
    ("www.ministryofsupply.com", "Ministry of Supply"),
    ("www.trueclassictees.com", "True Classic"),
    ("unboundmerino.com", "Unbound Merino"),
    ("www.stance.com", "Stance"),
    ("www.aviatornation.com", "Aviator Nation"),
    ("ridgemerino.com", "Ridge Merino"),
    # alternates / additional brands
    ("www.chubbies.com", "Chubbies"),
    ("www.mackweldon.com", "Mack Weldon"),
    ("www.tracksmith.com", "Tracksmith"),
    ("www.janji.com", "Janji"),
    ("www.publicrec.com", "Public Rec"),
    ("www.birddogs.com", "Birddogs"),
    ("huckberry.com", "Huckberry"),
    ("www.toadandco.com", "Toad&Co"),
    ("shop.ibex.com", "Ibex"),
    ("woolx.com", "WoolX"),
    ("www.spiritualgangster.com", "Spiritual Gangster"),
    ("3sixteen.com", "3sixteen"),
    ("freenotecloth.com", "Freenote Cloth"),
    ("www.oliversapparel.com", "Olivers"),
]

# product types that are clearly not clothing
SKIP_TITLE_KEYWORDS = ["gift card", "giftcard", "e-gift", "donation"]
