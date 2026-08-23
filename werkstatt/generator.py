#!/usr/bin/env python3
import json
import hashlib
import os
import random
import re
import shutil
import subprocess
import sys
import unicodedata
from datetime import datetime, timedelta
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
GAME = REPO
FALL_DIR = GAME / "fall"
ASSETS = Path(__file__).resolve().parent / "assets"

rng = random.Random(20260314)

OPFER_VORNAME = "Viktor"
OPFER_NACHNAME = "Salomon"
OPFER_NAME = "Viktor Salomon"
TAETERIN_VORNAME = "Marlene"
TAETERIN_NACHNAME = "Kowalczyk"
TAETERIN_NAME = "Marlene Kowalczyk"
CODENAME = "WESPE"
AUFTRAGGEBER = "René Falkenberg"
CHIP_ID = "CHIP-8842"
AUSWEIS_NR = "TC-COURIER-8842"
DECOY_A = ("Tobias", "Renner", "CHIP-5177")
DECOY_B = ("Ivo", "Baranowski", "CHIP-6609")
CLUB_KURIERE = "Kuriere_der_Nacht"
UEBERGABE = "Güterhalle Tor 4"

VORNAME_W = [
    "Anna","Bertha","Clara","Dora","Elisabeth","Franziska","Greta","Hanna","Ines","Johanna",
    "Katharina","Leonie","Martina","Nadja","Ottilie","Petra","Rosa","Sabine","Tanja","Ulrike",
    "Verena","Wanda","Yvonne","Zoe","Amelie","Britta","Cecilia","Dagmar","Emilia","Frieda",
    "Gesine","Henriette","Ida","Josephine","Karoline","Luise","Mathilde","Nicole","Odalys","Pauline",
    "Ronja","Stefanie","Theresa","Uta","Valentina","Wilhelmine","Xenia","Yasmin","Zaida","Almut",
    "Marlene","Serpil","Aylin","Kemina","Fatima","Giulia","Noor","Selma","Leyla","Aisha",
]
VORNAME_M = [
    "Aaron","Bruno","Christian","Dieter","Emil","Falk","Gustav","Heinrich","Ignatz","Jonas",
    "Klaus","Ludwig","Martin","Norbert","Otto","Paul","Reinhold","Stefan","Theodor","Uwe",
    "Vincent","Wolfgang","Xaver","Yusuf","Zacharias","Anton","Boris","Cornelius","Detlef","Emanuel",
    "Florian","Georg","Hendrik","Ivo","Jakob","Konrad","Lorenz","Matthias","Nikolaus","Oskar",
    "Pascal","Quirin","Rasmus","Sebastian","Tobias","Ulf","Veit","Werner","Zeno","Anselm",
    "René","Emiliano","Darius","Milan","Tarik","Joost","Kenan","Ruben","Ilja","Neo",
]
NACHNAMEN = [
    "Ackermann","Baumann","Brandt","Czerwinski","Dahlmann","Ehlers","Falkenberg","Gerber","Grünwald","Hartmann",
    "Ivanov","Jensen","Kowalczyk","Lindqvist","Meixner","Neumann","Ostermann","Petrov","Quandt","Richter",
    "Salomon","Schneider","Sommerfeld","Trapp","Uhlmann","Vogler","Weidner","Zabel","Adler","Bergmann",
    "Conradi","Dietrich","Engel","Fricke","Glockner","Hansen","Ibsen","Junker","Kalckreuth","Lorenzen",
    "Mohr","Nissen","Ohlsen","Pietsch","Renner","Sander","Thiel","Ufer","Visser","Wendland",
    "Yildirim","Ziervogel","Baranowski","Aydin","Duarte","Novak","Horvath","Kovacs","Larsen","Meier",
    "Berger","Hofer","Steiner","Wagner","Zimmerer","Reiter","Fuchs","Jäger","Wolf","Hirsch",
    "Krämer","Bäcker","Lehmann","Schulz","Fischer","Weber","Becker","Hoffmann","Schäfer","Koch",
    "Bauer","Richter","Klein","Wolf","Schröder","Neubauer","Brandner","Eichhorn","Feldmann","Grunert",
    "Halm","Isele","Jost","Kirchner","Laux","Moser","Nagel","Ott","Preuß","Roth",
    "Simon","Turk","Usinger","Vollmer","Wallner","Zorn","Amthor","Bock","Creutz","Deckert",
    "Ebert","Fendt","Glatz","Huber","Irmer","Jahn","Karg","Lutz","Michel","Noll",
]
STRASSEN = [
    "Finsterstraße","Gießergasse","Rabensteinplatz","Lindenpromenade","Grünplatz","Hafenkante",
    "Nordhaufenweg","Alter_Steg","Kupferdreh","Schmiedegasse","Wachtelweg","Donnerberg",
    "Silberblick","Nebelstieg","Rabenhorst","Eichenwall","Mühlendamm","Fischmarkt",
    "Laterntwete","Sternwarte","Kesselbrink","Dunkelmünde","Windhorst","Habichtsfeld",
    "Bruchsalier Weg","Karpfensteig","Amselgrund","Zinnwalder Promenade","Feuerrad","Grauhof",
    "Spinnwebgasse","Turmschneise","Moosbruch","Kaltental","Bibernellweg","Steinhuder Ring",
]
CLUBS = {
    "Kuriere_der_Nacht": 46,
    "Eisen_Tempel_Fitness": 380,
    "Sammlerverein_Muenzen_und_More": 120,
    "Terminal_City_Library": 410,
    "Museum_fuer_Bash_Geschichte": 95,
    "Segelklub_Blauer_Pier": 150,
    "Schachclub_Zugzwang": 88,
    "Angelverein_Der_Karpfen": 130,
}
MARKEN = ["Opel","Ford","Volkswagen","Toyota","Skoda","Fiat","Volvo","Renault","Peugeot","Seat"]
FARBEN = ["Blau","Rot","Gruen","Schwarz","Weiss","Silber","Grau","Gelb","Mintgruen","Braun"]

ZEUGEN = [
    {"nr": 22019, "vorname": "Bruno", "nachname": "Kalckreuth", "beruf": "Nachtwächter", "alter": 61},
    {"nr": 30177, "vorname": "Serpil", "nachname": "Aydin", "beruf": "Bäckerin", "alter": 44},
    {"nr": 28456, "vorname": "Emil", "nachname": "Duarte", "beruf": "Taxifahrer", "alter": 58},
]

def norm(s: str) -> str:
    s = s.upper()
    s = (s.replace("Ä", "AE").replace("Ö", "OE").replace("Ü", "UE")
           .replace("ß", "SS").replace("É", "E").replace("È", "E").replace("Ê", "E")
           .replace("Á", "A").replace("À", "A").replace("Í", "I").replace("Ó", "O")
           .replace("Ú", "U").replace("Ø", "OE").replace("Å", "AA"))
    return "".join(c for c in s if c.isalnum())

def sha(s: str) -> str:
    return hashlib.sha256(norm(s).encode()).hexdigest()

def md5hex(s: str) -> str:
    return hashlib.md5(s.encode()).hexdigest()

def load_alice_lines():
    txt = (ASSETS / "alice_de.txt").read_text(encoding="utf-8")
    txt = re.sub(r"\s+", " ", txt)
    words = [w.strip(",.;:!?()[]\"'*_") for w in txt.split()]
    words = [w for w in words if len(w) > 2 and not any(ch.isdigit() for ch in w)]
    return words

ALICE_WORDS = load_alice_lines()

def noise_sentence(min_w=8, max_w=16) -> str:
    n = rng.randint(min_w, max_w)
    sent = " ".join(rng.choice(ALICE_WORDS) for _ in range(n))
    return sent.capitalize() + "."

def noise_paragraph(lines=4) -> str:
    return "\n".join(noise_sentence() for _ in range(lines))

def build_streets():
    d = FALL_DIR / "strassen"
    d.mkdir(parents=True, exist_ok=True)
    for s in STRASSEN:
        fname = s.replace(" ", "_") + ".txt"
        with open(d / fname, "w", encoding="utf-8") as f:
            for _ in range(300):
                f.write(noise_sentence(9, 18) + "\n")

def fmt_addr(street: str, line: int) -> str:
    return f"{street.replace('_', ' ')}, Zeile {line}"

PEOPLE = []

RESERVED_NACHNAMEN = {"Kowalczyk", "Renner", "Baranowski", "Salomon", "Falkenberg",
                      "Kalckreuth", "Aydin", "Duarte"}

def make_person(vorname=None, nachname=None, geschlecht=None, alter=None, street=None):
    g = geschlecht or rng.choice(["M", "W", "W", "M", "D"])
    if vorname is None or nachname is None:
        vorname, nachname = unique_name(g)
    else:
        assert (vorname, nachname) not in NAMES_TAKEN, f"Duplikat: {vorname} {nachname}"
        NAMES_TAKEN.add((vorname, nachname))
    vn, nn = vorname, nachname
    st = street or rng.choice(STRASSEN)
    zeile = rng.randint(1, 300)
    p = {"vorname": vn, "nachname": nn, "geschlecht": g, "alter": alter or rng.randint(16, 90),
         "strasse": st, "zeile": zeile}
    PEOPLE.append(p)
    return p

NAMES_TAKEN = set()

def unique_name(geschlecht):
    while True:
        vn = rng.choice(VORNAME_M if geschlecht == "M" else VORNAME_W)
        nn = rng.choice(NACHNAMEN)
        if nn in RESERVED_NACHNAMEN:
            continue
        if (vn, nn) in NAMES_TAKEN:
            continue
        NAMES_TAKEN.add((vn, nn))
        return vn, nn

def find_person(nn, vn=None):
    for p in PEOPLE:
        if p["nachname"] == nn and (vn is None or p["vorname"] == vn):
            return p
    return None

def build_people():
    for _ in range(6490):
        make_person()
    taeterin = make_person(TAETERIN_VORNAME, TAETERIN_NACHNAME, "W", 31, "Rabensteinplatz")
    taeterin["zeile"] = 214
    opfer = make_person(OPFER_VORNAME, OPFER_NACHNAME, "M", 54, "Finsterstraße")
    opfer["zeile"] = 96
    make_person(ZEUGEN[0]["vorname"], ZEUGEN[0]["nachname"], "M", 61, "Gießergasse")["zeile"] = 12
    make_person(ZEUGEN[1]["vorname"], ZEUGEN[1]["nachname"], "W", 44, "Kesselbrink")["zeile"] = 51
    make_person(ZEUGEN[2]["vorname"], ZEUGEN[2]["nachname"], "M", 58, "Fischmarkt")["zeile"] = 8
    decoy_a = make_person(DECOY_A[0], DECOY_A[1], "M", 26, "Nordhaufenweg")
    decoy_a["zeile"] = 77
    decoy_b = make_person(DECOY_B[0], DECOY_B[1], "M", 29, "Hafenkante")
    decoy_b["zeile"] = 133
    make_person("René", "Falkenberg", "M", 49, "Silberblick")["zeile"] = 42
    for vn_, nn_ in [(TAETERIN_VORNAME, TAETERIN_NACHNAME), (OPFER_VORNAME, OPFER_NACHNAME),
                     (ZEUGEN[0]["vorname"], ZEUGEN[0]["nachname"]),
                     (ZEUGEN[1]["vorname"], ZEUGEN[1]["nachname"]),
                     (ZEUGEN[2]["vorname"], ZEUGEN[2]["nachname"]),
                     (DECOY_A[0], DECOY_A[1]), (DECOY_B[0], DECOY_B[1]),
                     ("René", "Falkenberg")]:
        assert (vn_, nn_) in NAMES_TAKEN
    rng.shuffle(PEOPLE)
    pre = """***************
Um zur Straße zu gelangen, in der jemand wohnt, benutze die Datei
für diesen Straßennamen im Unterverzeichnis 'strassen'.
Um an der Tür zu klopfen und zu ermitteln, lies die Zeilennummer,
in der die Person wohnt, aus dieser Datei.  Sieht eine Zeile wie Kauderwelsch aus, bist du am falschen Haus.
***************

NAME\tGESCHLECHT\tALTER\tADRESSE"""
    lines = [pre]
    for p in PEOPLE:
        lines.append(f"{p['vorname']} {p['nachname']}\t{p['geschlecht']}\t{p['alter']}\t{fmt_addr(p['strasse'], p['zeile'])}")
    (FALL_DIR / "personen").write_text("\n".join(lines) + "\n", encoding="utf-8")

def build_vehicles():
    lines = ["KENNZEICHEN\tMARKE\tFARBE\tJAHR\tBESITZER"]
    used_plates = set()
    def plate():
        while True:
            pl = f"TC-{rng.randint(100,999)}-{chr(rng.randint(65,90))}{chr(rng.randint(65,90))}"
            if pl not in used_plates:
                used_plates.add(pl)
                return pl
    for _ in range(2400):
        owner = rng.choice(PEOPLE)
        lines.append(f"{plate()}\t{rng.choice(MARKEN)}\t{rng.choice(FARBEN)}\t{rng.randint(1998, 2026)}\t{owner['vorname']} {owner['nachname']}")
    t = find_person(TAETERIN_NACHNAME, TAETERIN_VORNAME)
    lines.append(f"TC-{rng.randint(100,999)}-WK\tSimson\tMintgruen\t1987\t{TAETERIN_VORNAME} {TAETERIN_NACHNAME}")
    (FALL_DIR / "fahrzeuge").write_text("\n".join(lines) + "\n", encoding="utf-8")

KURIERE = []

def build_memberships():
    d = FALL_DIR / "mitgliedschaften"
    d.mkdir(parents=True, exist_ok=True)
    pool = PEOPLE[:]
    rng.shuffle(pool)
    idx = 0
    for club, size in CLUBS.items():
        members = []
        while len(members) < size and idx < len(pool):
            p = pool[idx]; idx += 1
            members.append(p)
        if club == CLUB_KURIERE:
            for name in [(TAETERIN_VORNAME, TAETERIN_NACHNAME), (DECOY_A[0], DECOY_A[1]), (DECOY_B[0], DECOY_B[1])]:
                p = find_person(name[1], name[0])
                if p not in members:
                    members.append(p)
                    size += 1
            CLUBS[club] = len(members)
            KURIERE.clear()
            KURIERE.extend(members)
        with open(d / club, "w", encoding="utf-8") as f:
            f.write(f"Mitgliederliste {club.replace('_', ' ')}\nStand: 01.03.2026\n\n")
            for m in sorted(members, key=lambda x: x["nachname"]):
                f.write(f"{m['nachname']}, {m['vorname']}\n")

def build_interviews():
    d = FALL_DIR / "befragungen"
    d.mkdir(parents=True, exist_ok=True)
    stmts = [
        "Ich habe nichts gesehen. Ich war die ganze Nacht über meinem Buch.",
        "Wer? Ich? Um diese Zeit schlafe ich. Fragen Sie meinen Arzt.",
        "Ich habe nur eine Katze gehört. Oder war es ein Moped?",
        "Gehen Sie mir aus dem Weg, ich bin spät dran.",
        "Gelbe Regenmäntel sieht man hier ständig. Das ist nichts Besonderes.",
        "Mein Nachbar hatte Besuch. Mehr sage ich nicht ohne Anwalt.",
        "Ich wohne erst seit gestern hier. Keine Ahnung von irgendwas.",
        "Haben Sie mal an den Mülltonnen geriechen müssen? Nein? Dann verstehen Sie nichts.",
    ]
    for i in range(450):
        nr = rng.randint(10000, 99999)
        while (d / f"befragung-{nr}").exists():
            nr = rng.randint(10000, 99999)
        body = noise_paragraph(3) + "\n\n" + rng.choice(stmts) + "\n\n" + noise_paragraph(2) + "\n"
        (d / f"befragung-{nr}").write_text(body, encoding="utf-8")

    z = ZEUGEN
    (d / f"befragung-{z[0]['nr']}").write_text(
        f"AUSSAGE {z[0]['vorname']} {z[0]['nachname']}, {z[0]['beruf']}, {z[0]['alter']}:\n\n"
        "  .--.\n"
        " (o_o )  <- Skizze des Wachpostens\n"
        " /|_|\\\n"
        "  d b\n\n"
        "Ich saß in meiner Hütte am Dienstausgang, Gießergasse 3. Kurz nach halb zwei\n"
        "hatte ich Radio gehört, gegen 02:12 Uhr ging ich eine Runde. Da kam eine Person\n"
        "aus dem Hof der Bank auf mich zu: heller REGENMANTEL, dunkler FAHRRADHELM,\n"
        "einen Rucksack dabei. Sie lief schnell Richtung NORDEN, da wo die U-BAHN\n"
        "GRUENPLATZ ist. Ich habe nur den Rücken gesehen. Die Person war schlank,\n"
        "mittelgroß. Mehr nicht.\n", encoding="utf-8")

    (d / f"befragung-{z[1]['nr']}").write_text(
        f"AUSSAGE {z[1]['vorname']} {z[1]['nachname']}, {z[1]['beruf']}, {z[1]['alter']}:\n\n"
        "Meine Bäckerei liegt direkt an der Gießergasse. Ich musste um 3 backen und war\n"
        "schon früher wach. Gegen 02:04 hörte ich im Hinterhof der Bank STIMMEN, erst\n"
        "flüstern, dann streiten. Als ich aus dem Fenster schaute, rannte eine Person\n"
        "los: FAHRRADHELM, und auf dem RUCKSACK stand in großen Buchstaben\n"
        "'NACHTSCHICHT'. So heißt doch dieser Fahrradkurierladen, oder?\n", encoding="utf-8")

    (d / f"befragung-{z[2]['nr']}").write_text(
        f"AUSSAGE {z[2]['vorname']} {z[2]['nachname']}, {z[2]['beruf']}, {z[2]['alter']}:\n\n"
        "Um 02:26 Uhr nahm ich am GRUENPLATZ eine Fahrgäste... äh, einen Fahrgast mit:\n"
        "Regenmantel um die Hüfte gebunden, Helm unterm Arm. wollte zum 24h-\n"
        "EISEN-TEMPEL an der Lindenpromenade. Bezahlt hat knapp, aber ordentlich.\n"
        "Unterwegs hat die Person dreimal aufs Handy geschaut, aber NICHT telefoniert.\n", encoding="utf-8")

def ts(y=2026, mo=3, d=14, h=0, mi=0, se=0):
    return f"{y:04d}-{mo:02d}-{d:02d} {h:02d}:{mi:02d}:{se:02d}"

def build_protokolle():
    d = FALL_DIR / "protokolle"
    d.mkdir(parents=True, exist_ok=True)

    used_chips = {8842, 5177, 6609}
    def new_chip():
        while True:
            c = rng.randint(1000, 9999)
            if c not in used_chips:
                used_chips.add(c)
                return c

    courier_chip = {}
    for p in KURIERE:
        key = (p["nachname"], p["vorname"])
        courier_chip[key] = {(TAETERIN_NACHNAME, TAETERIN_VORNAME): 8842,
                             (DECOY_A[1], DECOY_A[0]): 5177,
                             (DECOY_B[1], DECOY_B[0]): 6609}.get(key, new_chip())

    noncourier_chips = [new_chip() for _ in range(950)]

    cam = ["# KAMERA-KIOSK PROTOKOLL — GIESSERGASSE, DIENSTAUSGANG BANKHOF",
           "# Format: ZEITSTEMPEL | KAMERA | BESCHREIBUNG | RICHTUNG",
           "# Zeitzone: Terminal City Lokalzeit"]
    for _ in range(60):
        h = rng.choice([21, 22, 23])
        t = ts(2026, 3, 13, h, rng.randint(0, 59), rng.randint(0, 59))
        cam.append(f"{t} | KAM-11 | {noise_sentence(4,7)} | {'NORD' if rng.random()<.5 else 'SUED'}")
    cam.append("2026-03-14 00:31:07 | KAM-11 | Person mit Hund, laterne flackert | SUED")
    cam.append("2026-03-14 01:12:22 | KAM-11 | Person, dunkler Fahrradhelm, heller Regenmantel | NORD")
    cam.append("2026-03-14 01:44:50 | KAM-11 | Lieferwagen, Kennzeichen verdeckt | SUED")
    cam.append("2026-03-14 02:12:41 | KAM-11 | Person, dunkler Fahrradhelm, heller Regenmantel, Rucksack | NORD")
    for _ in range(12):
        t = ts(2026, 3, 14, 2, rng.choice([1, 5, 27, 33, 40, 52]), rng.randint(0, 59))
        cam.append(f"{t} | KAM-11 | {noise_sentence(4,7)} | {'NORD' if rng.random()<.5 else 'SUED'}")
    (d / "kameras-giessergasse.log").write_text("\n".join(cam) + "\n", encoding="utf-8")

    gates = ["# U-BAHN TERMINAL CITY — Drehkreuz-Protokoll (anonymisierte Chips)",
             "# Format: ZEITSTEMPEL | STATION | RICHTUNG | CHIP-ID",
             "# Zuordnung Chip-ID zu Personen: chip-zuordnung.csv"]
    stations = ["GRUENPLATZ", "HAFENKANTE", "NORDHAFEN", "KUPFERDREH", "DONNERBERG", "KESSELBRINK"]
    for _ in range(700):
        h = rng.randint(18, 28) % 24
        day = 13 if h >= 18 else 14
        gates.append(ts(2026, 3, day, h, rng.randint(0, 59), rng.randint(0, 59)) +
                     f" | {rng.choice(stations)} | {'EINGANG' if rng.random()<.5 else 'AUSGANG'} | CHIP-{rng.choice(noncourier_chips)}")
    gates.append("2026-03-14 02:23:45 | GRUENPLATZ | AUSGANG | CHIP-8842")
    gates.append("2026-03-14 02:36:12 | GRUENPLATZ | AUSGANG | CHIP-6609")
    gates.append("2026-03-14 02:44:02 | NORDHAFEN | AUSGANG | CHIP-5177")
    gates.append("2026-03-14 23:41:33 | HAFENKANTE | AUSGANG | CHIP-6609")
    gates.sort()
    (d / "ubahn-drehkreuze.log").write_text("\n".join(gates) + "\n", encoding="utf-8")

    chips = ["# CHIP-REGISTRY DER VERKEHRSBETRIEBE (Ausweis-Chips)",
             "# Format: CHIP-ID,NACHNAME,VORNAME,GESCHLECHT"]
    chip_people = rng.sample([p for p in PEOPLE if p not in KURIERE], 850)
    for ch, p in zip(noncourier_chips[:850], chip_people):
        chips.append(f"CHIP-{ch},{p['nachname']},{p['vorname']},{p['geschlecht']}")
    for p in KURIERE:
        chips.append(f"CHIP-{courier_chip[(p['nachname'], p['vorname'])]},{p['nachname']},{p['vorname']},{p['geschlecht']}")
    (d / "chip-zuordnung.csv").write_text("\n".join(chips) + "\n", encoding="utf-8")

    tel = ["# TELEFONBUCH DER STADT (Auszug)", "# Format: NUMMER,NACHNAME,VORNAME"]
    telmap = {}
    telpeople = rng.sample(PEOPLE, 1095)
    for keyname in [(DECOY_A[0], DECOY_A[1]), (TAETERIN_VORNAME, TAETERIN_NACHNAME),
                    ("René", "Falkenberg"), (DECOY_B[0], DECOY_B[1])]:
        p = find_person(keyname[1], keyname[0])
        if p is not None and p not in telpeople:
            telpeople.append(p)
    for p in telpeople:
        num = f"0176-{rng.randint(1000000,9999999)}"
        telmap[f"{p['nachname']},{p['vorname']}"] = num
        tel.append(f"{num},{p['nachname']},{p['vorname']}")
    (d / "telefonbuch.csv").write_text("\n".join(tel) + "\n", encoding="utf-8")

    calls = ["# FUNKZELLEN-PROTOKOLL MOBILEFUNK — NACHT 13./14. MAERZ",
             "# Format: ZEITSTEMPEL | RUFNUMMER_A | RUFNUMMER_B | DAUER_S | FUNKZELLE"]
    nums = [ln.split(",")[0] for ln in tel[2:]]
    for _ in range(600):
        h = rng.randint(18, 28) % 24
        day = 13 if h >= 18 else 14
        calls.append(ts(2026, 3, day, h, rng.randint(0, 59), rng.randint(0, 59)) +
                     f" | {rng.choice(nums)} | {rng.choice(nums)} | {rng.randint(5, 900)} | {rng.choice(['NORDHAFEN','GRUENPLATZ','ZENTRUM','HAFENKANTE','SUEDVORSTADT'])}")
    rn = telmap.get(f"{DECOY_A[1]},{DECOY_A[0]}")
    if rn:
        calls.append(f"2026-03-14 02:01:37 | {rn} | 030-5550192 | 840 | NORDHAFEN")
    rn_k = telmap.get(f"{TAETERIN_NACHNAME},{TAETERIN_VORNAME}")
    if rn_k:
        calls.append(f"2026-03-14 02:33:12 | {rn_k} | 030-5550192 | 41 | SUEDVORSTADT")
    rn_b = telmap.get(f"{DECOY_B[1]},{DECOY_B[0]}")
    if rn_b:
        calls.append(f"2026-03-14 02:10:55 | {rn_b} | 0176-4455661 | 180 | NORDHAFEN")
        calls.append(f"2026-03-14 02:22:40 | {rn_b} | 030-1120094 | 95 | NORDHAFEN")
    calls.sort()
    (d / "funkzellen.log").write_text("\n".join(calls) + "\n", encoding="utf-8")

def rot13(s: str) -> str:
    return s.translate(str.maketrans(
        "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
        "NOPQRSTUVWXYZABCDEFGHIJKLMnopqrstuvwxyzabcdefghijklm"))

NOTE_PLAIN = (
    "Schlüssel ist sicher. Übergabe: Mittwoch, 18.03., 03:00 Uhr,\n"
    "alte Güterhalle, Tor 4. Preis wie besprochen, Bezahlung in Moneros.\n"
    "Komme allein. - W.\n")

def build_verschluesselt():
    d = FALL_DIR / "verschluesselt"
    d.mkdir(parents=True, exist_ok=True)
    import base64
    blob = base64.b64encode(rot13(NOTE_PLAIN).encode()).decode()
    wrapped = "\n".join(blob[i:i+64] for i in range(0, len(blob), 64))
    (d / "notiz-am-zaun.txt").write_text(wrapped + "\n", encoding="utf-8")

    mail_plain = (
        "Von: r.falkenberg@tccb-terminalcity.example\n"
        "An: W.\n"
        "Betreff: Termin\n\n"
        "Der Schluessel muss bis Donnerstag funktionieren. Restzahlung nach\n"
        "Testlauf, wie besprochen. Danach verbrennen. - RF\n")
    src = d / "_mail_plain.tmp"
    src.write_text(mail_plain, encoding="utf-8")
    enc = d / "auftraggeber.eml.aes"
    cmd = ["openssl", "enc", "-aes-256-cbc", "-salt", "-pbkdf2", "-iter", "10000",
           "-a", "-in", str(src), "-out", str(enc), "-pass", "pass:" + CODENAME]
    subprocess.run(cmd, check=True, capture_output=True)
    chk = subprocess.run(["openssl", "enc", "-d", "-aes-256-cbc", "-a", "-pbkdf2",
                          "-iter", "10000", "-in", str(enc), "-pass", "pass:" + CODENAME],
                         check=True, capture_output=True)
    assert chk.stdout.decode() == mail_plain, "AES roundtrip fehlgeschlagen"
    src.unlink()

GIT_ENV_BASE = {
    "GIT_AUTHOR_NAME": "ops-nachtschicht",
    "GIT_AUTHOR_EMAIL": "ops@nachtschicht-logistik.example",
    "GIT_COMMITTER_NAME": "ops-nachtschicht",
    "GIT_COMMITTER_EMAIL": "ops@nachtschicht-logistik.example",
}

def git_run(repo: Path, *args, date=None):
    env = dict(os.environ)
    env.update(GIT_ENV_BASE)
    if date:
        iso = date.strftime("%Y-%m-%dT%H:%M:%S +0100")
        env["GIT_AUTHOR_DATE"] = iso
        env["GIT_COMMITTER_DATE"] = iso
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, env=env)

def git_out(repo: Path, *args):
    return subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True,
                          text=True, env=dict(os.environ, **GIT_ENV_BASE)).stdout

ROUTE7_CSV = """# ROUTE 7 — SONDERFAHRT (INTERN)
# Format: ZEIT | STOPP | ANMERKUNG
19:30 | DEPOT LINDENPROMENADE | Tourenbeginn
21:15 | KESSELBRINK 4 | Paket A
23:02 | DONNERBERG 9 | Paket B
01:58 | FINSTERSTRASSE 17 (HINTERHOF) | ABHOLUNG PAKET-OBSIDIAN
02:30 | GRUENPLATZ | Pause
FAHRER(RUFNAME): WESPE
"""

WESPE_TXT = """TEAMAKTE (INTERN)
Codename : WESPE
Bezirk   : OST
Ausweis-Nr: TC-COURIER-8842
Rufkanal : 7
Status   : aktiv
Hinweis  : Ausweis-Nr gilt zugleich als Chip-ID beim Verkehrsverbund.
"""

GECKO_TXT = """TEAMAKTE (INTERN)
Codename : GECKO
Bezirk   : WEST
Ausweis-Nr: TC-COURIER-3311
Rufkanal : 4
Status   : urlaub
"""

UEBERGABE_MD = """# ENTWURF (NICHT SENDEN)
Uebergabe: alte Gueterhalle, Tor 4.
Termin: Mittwoch 03:00.
RF bestaetigt. Rest in Moneros.
"""

def build_git_repo():
    repo = FALL_DIR / "repos" / "nachtschicht-logistik"
    if repo.exists():
        shutil.rmtree(repo)
    repo.mkdir(parents=True)
    git_run(repo, "init", "-b", "main", date=datetime(2026, 2, 20, 9, 0, 0))
    (repo / "README.md").write_text(
        "# Nachtschicht-Logistik — internes Tourensystem\nNachts ab 19:00 im Einsatz.\n",
        encoding="utf-8")
    (repo / "config" ).mkdir()
    (repo / "config" / "kartenmaterial.txt").write_text(noise_paragraph(6) + "\n", encoding="utf-8")
    git_run(repo, "add", "-A"); git_run(repo, "commit", "-m", "Initiales Routing-Setup",
                                        date=datetime(2026, 2, 20, 9, 12, 0))
    (repo / "kunden").mkdir()
    (repo / "kunden" / "route-3.csv").write_text("# ROUTE 3\n08:15 DEPOT\n09:00 KUNDE-X\n", encoding="utf-8")
    (repo / "kunden" / "route-5.csv").write_text("# ROUTE 5\n20:00 DEPOT\n21:00 KUNDE-Y\n", encoding="utf-8")
    git_run(repo, "add", "-A"); git_run(repo, "commit", "-m", "Route 3 und Route 5 aktualisiert",
                                        date=datetime(2026, 3, 2, 18, 40, 0))
    (repo / "team").mkdir()
    (repo / "team" / "wespe.txt").write_text(WESPE_TXT, encoding="utf-8")
    (repo / "team" / "gecko.txt").write_text(GECKO_TXT, encoding="utf-8")
    git_run(repo, "add", "-A"); git_run(repo, "commit", "-m", "Teamdatei ergänzt",
                                        date=datetime(2026, 3, 6, 17, 5, 0))
    C_TEAM = git_out(repo, "rev-parse", "HEAD").strip()
    (repo / "kunden" / "route-7.csv").write_text(ROUTE7_CSV, encoding="utf-8")
    git_run(repo, "add", "-A"); git_run(repo, "commit", "-m", "Route 7 für Sonderfahrt eingerichtet",
                                        date=datetime(2026, 3, 12, 22, 15, 0))
    C_ROUTE7 = git_out(repo, "rev-parse", "HEAD").strip()
    (repo / "entwurf").mkdir()
    (repo / "entwurf" / "uebergabe.md").write_text(UEBERGABE_MD, encoding="utf-8")
    git_run(repo, "add", "-A"); git_run(repo, "commit", "-m", "Entwurf Übergabenotiz (intern)",
                                        date=datetime(2026, 3, 13, 23, 48, 0))
    DANGLING = git_out(repo, "rev-parse", "HEAD").strip()
    git_run(repo, "reset", "--hard", "HEAD~1")
    (repo / "team" / "wespe.txt").unlink()
    (repo / "team" / "gecko.txt").unlink()
    git_run(repo, "add", "-A"); git_run(repo, "commit", "-m", "Audit: sensible Teamdaten entfernen",
                                        date=datetime(2026, 3, 14, 6, 2, 0))
    (repo / "kunden" / "route-7.csv").unlink()
    git_run(repo, "add", "-A"); git_run(repo, "commit", "-m", "Archivbereinigung: Route 7 entfernt",
                                        date=datetime(2026, 3, 14, 6, 5, 0))
    if (repo / "team").is_dir() and not any((repo / "team").iterdir()):
        (repo / "team").rmdir()
    subprocess.run(["git", "reflog", "expire", "--expire-unreachable=now", "--all"],
                   cwd=repo, check=True, capture_output=True, env=dict(os.environ, **GIT_ENV_BASE))
    fsck = subprocess.run(["git", "fsck", "--dangling"], cwd=repo, capture_output=True,
                          text=True, env=dict(os.environ, **GIT_ENV_BASE)).stdout
    assert DANGLING in fsck, f"dangling commit fehlt: {fsck!r}"

    archiv = repo / ".gitarchiv"
    if archiv.exists():
        shutil.rmtree(archiv)
    shutil.copytree(repo / ".git", archiv)
    starter = repo / "ermittlung-starten.sh"
    starter.write_text(
        "#!/bin/sh\n"
        "# Beschlagnahmtes Server-Image des Kurierdiensts wiederherstellen:\n"
        "set -e\n"
        'DIR="$(cd "$(dirname "$0")" && pwd)"\n'
        'rm -rf "$DIR/.git"\n'
        'cp -R "$DIR/.gitarchiv" "$DIR/.git"\n'
        'echo "Image wiederhergestellt. Ab jetzt: cd in dieses Verzeichnis und git nutzen."\n',
        encoding="utf-8")
    os.chmod(starter, 0o755)
    return {"C_TEAM": C_TEAM, "C_ROUTE7": C_ROUTE7, "DANGLING": DANGLING}

TATORT_TEXT = """AKTE 47/II — DER SCHLUESSEL VON TERMINAL CITY
=============================================

        _______________________
       |  _________________  |
       | | T C C B         | |     TERMINAL CITY CLEARING BANK
       | |_________________| |     FINSTERSTRASSE 17
       |____    ________  __|
       /___/    /______/ \\/      TATNACHT: 13./14. MAERZ 2026
      ___                 ___
     /   \\_______________/   \\
     \\___/               \\___/   SERVERRAUM, ERDGESCHOSS

LAGEBERGICHTE
-------------
Am Morgen des 14. Maerz 2026 wurde DR. VIKTOR SALOMON (54), leitender
Systemarchitekt der Bank, tot im Serverraum aufgefunden. Keine aeusseren
Verletzungen. Auf dem Tisch: ZWEI halbvolle Espressotassen.

Aus dem Tresorraum fehlt der OBSIDIAN-SCHLUESSEL — ein Hardware-
Schluessel, mit dem sich das gesamte Kreditbuch der Stadt manipulieren
laesst. Wer ihn hat, kann Terminal City erpressen.

Keine Spuren von Einbruch. Die Tuer war mit einem echten Schluessel
geoeffnet worden. Der Hinterhofausgang in der GIESSERGASSE 3 war
nicht verriegelt.

Beweisstuecke
-------------
* Am Hinterhofzaun hing eine zusammengeknüllte Notiz (verschlusselt!):
      fall/verschluesselt/notiz-am-zaun.txt
* Auf dem Server: ein verschluesseltes Email:
      fall/verschluesselt/auftraggeber.eml.aes
* Im Zuge der Ermittlungen wurde der Tourenserver des Kurierdiensts
  'Nachtschicht-Logistik' beschlagnahmt. Abbild unter:
      fall/repos/nachtschicht-logistik   (ein echtes Git-Repository!)
* Protokolle der Tatnacht (Kamera, U-Bahn, Mobilfunk):
      fall/protokolle/

Zeugen (Videoaussagen, Nummern beachten!)
-----------------------------------------
AUSSAGE #%(z0)s — %(z0v)s %(z0n)s, Nachtwachter:
   sah gegen 02:12 eine Person mit hellem REGENMANTEL und dunklem
   FAHRRADHELM vom Bankhof Richtung Norden (U-BAHN GRUENPLATZ) davonlaufen.
   Details: fall/befragungen/befragung-%(z0)s

AUSSAGE #%(z1)s — %(z1v)s %(z1n)s, Backerin:
   horchte gegen 02:04 Stimmen im Bankhof; sah eine Person mit
   Rucksack, Aufschrift 'NACHTSCHICHT'.
   Details: fall/befragungen/befragung-%(z1)s

AUSSAGE #%(z2)s — %(z2v)s %(z2n)s, Taxifahrer:
   nahm um 02:26 am GRUENPLATZ einen Fahrgast mit zum
   EISEN-TEMPEL-FITNESS, Lindenpromenade.
   Details: fall/befragungen/befragung-%(z2)s

Das TCPD braucht deinen Bericht: WER steckt dahinter — und wer hat
bestellt? Prufe deine Zwischenergebnisse jederzeit mit ./pruefer.sh
"""

ANLEITUNG = """ANLEITUNG — DIE KOMMANDOZEILEN-MORDE II
=======================================

Terminal City, zwei Jahre danach: Ein Toter im Serverraum, ein
gestohlener Schlüssel, und eine Spur, die durch Kameras, U-Bahn-
Drehkreuze, verschlüsselte Notizen und ein beschlagnahmtes Git-
Repository führt.

REGELN
------
1. Benutze ausschließlich das Terminal. Keinen Texteditor und keine
   grafischen Tools, um Dateien im Ordner 'fall/' anzusehen.
2. Erlaubt sind: 'cat', 'less', 'head', 'tail', 'grep', 'find',
   'sort', 'uniq', 'cut', 'tr', 'openssl', 'git', 'md5'
   bzw. 'md5sum' und alles, was im SPICKZETTEL steht.
3. Alles, was du brauchst, ist IM Fallordner versteckt. Du musst
   nichts aus dem Internet laden.
4. Steck fest? Die Dateien 'hinweis1' bis 'hinweis10' helfen — aber
   liest sie der Reihe nach und nur, wenn du wirklich nicht weiterweißt.

SO STARTEST DU
--------------
    cat anleitung          <- das hier
    cat spickzettel.md     <- Kommandozeilen-Nachschlagewerk
    ls fall/
    less fall/tatort       <- dein erster echter Lead!

WERKZEUGE
---------
    ./pruefer.sh           <- prüft deine Fortschritte (optional, macht Spaß)

ZIEL
----
Finde heraus, WER den Obsidian-Schlüssel gestohlen hat, WER ihn
beauftragt hat — und bring den Fall mit einem Einzeiler zum Abschluss
(siehe 'loesung').

Viel Erfolg, Detektiv.
"""

HINTS = [
"""HINWEIS 1
=========
Starte mit:  less fall/tatort
Alles Wichtige beginnt dort: Opfer, Ort, Beweisstücke und drei
Zeugen mit BEFRAGUNGS-NUMMERN. Notiere dir die Nummern.""",

"""HINWEIS 2
=========
Die drei Zeugendetails findest du hier:
    ls fall/befragungen
    cat fall/befragungen/befragung-<NUMMER>
Achte auf: Kleidung, Uhrzeit, Richtung, und die Aufschrift auf
einem Rucksack.""",

"""HINWEIS 3
=========
Die Aufschrift 'NACHTSCHICHT' ist ein Firmenname. Mitgliederlisten
liegen in:  fall/mitgliedschaften/
    grep -i nachtschicht fall/mitgliedschaften/* 2>/dev/null
    ls fall/mitgliedschaften | grep -i kurier
Die Liste 'Kuriere_der_Nacht' enthält alle Fahrerinnen und Fahrer.""",

"""HINWEIS 4
=========
Zeitfenster der Tat: ca. 01:55 bis 02:30 Uhr.
Wer fuhr wann wohin?
    ls fall/protokolle/
Jede Datei erklärt ihr eigenes Format in '#' Kommentarzeilen oben.
Filtere z.B.:  grep '02:1' fall/protokolle/kameras-giessergasse.log""",

"""HINWEIS 5
=========
So engst du die Kurierliste ein:
  1) U-Bahn-AUSGANG am GRUENPLATZ zwischen 02:15 und 02:45
     (die Flüchtende lief Richtung Norden!)
  2) Die anonymen Chips auflösen über:
     fall/protokolle/chip-zuordnung.csv
     -> nur wenige Namen bleiben übrig.
  3) Gegencheck per Mobilfunk (fall/protokolle/funkzellen.log +
     telefonbuch.csv): War jede dieser Personen überhaupt in der Lage,
     um 02:12 an der Gießergasse zu sein? Die Kamera bestätigt:
     genau EINE Person mit Helm lief um 02:12:41 nach NORDEN.""",

"""HINWEIS 6
=========
Die Notiz vom Zaun ist doppelt gepackt: erst ROT13, dann BASE64.
Zurück (portabel über openssl):
    openssl base64 -d -in fall/verschluesselt/notiz-am-zaun.txt | tr 'A-Za-z' 'N-ZA-Mn-za-m'
(Auf macOS ginge auch:  base64 -D -i fall/verschluesselt/notiz-am-zaun.txt | tr ...)""",

"""HINWEIS 7
=========
Die Email-Datei ist AES-verschlüsselt (openssl, PBKDF2). Der Befehl:
    openssl enc -d -aes-256-cbc -a -pbkdf2 -iter 10000 \\
      -in fall/verschluesselt/auftraggeber.eml.aes -pass pass:PASSWORT
Das Passwort ist der RUFRUFNAME der Fahrerin aus Route 7 — vier
Buchstaben, ein Insekt. Woher du den bekommst? Siehe Hinweis 8.""",

"""HINWEIS 8
=========
Das beschlagnahmte Repo liegt als Server-IMAGE vor. Stelle es zuerst her:
    sh fall/repos/nachtschicht-logistik/ermittlung-starten.sh
Dann hast du ein ECHTES Git-Repository:
    cd fall/repos/nachtschicht-logistik
    git log --oneline
Gelöschte Dateien leben in alten Commits weiter:
    git show COMMIT:pfad/zur/datei
Und manchmal gibt es sogar VERLORENE Commits:
    git fsck --lost-found
    git show <SHA>
Gesucht: 'team/wespe.txt' und 'kunden/route-7.csv'.""",

"""HINWEIS 9
=========
In 'team/wespe.txt' steht eine AUSWEIS-NUMMER. Die ist zugleich die
CHIP-ID beim Verkehrsverbund:
    grep 8842 fall/protokolle/chip-zuordnung.csv
Damit hast du einen echten Namen. Aber Vorsicht: Erst beweisen!
Der U-Bahn-Auszug und die Kamera müssen zur Person passen.""",

"""HINWEIS 10
===========
Wenn du den Namen hast, ist der Fall gelöst:
    echo -n 'VORNAMEN NACHNAMEN' | md5
    grep -if <HASH> kodiert
Wie man den Bericht abgibt, steht in 'loesung'.
""",
]

SPICKZETTEL = """SPICKZETTEL — DIE KOMMANDOZEILEN-MORDE II
=========================================

NAVIGIEREN
----------
ls                  Verzeichnis auflisten          ls fall/protokolle/
cd                  Verzeichnis wechseln           cd fall/repos
pwd                 Aktueller Pfad
less                Datei bequem lesen             less fall/tatort   (q beendet)
cat                 Datei ausgeben                 cat anleitung
head / tail         Anfang / Ende einer Datei      tail -n 20 datei
wc -l               Zeilen zählen                  wc -l fall/personen
find                Dateien finden                 find fall -name '*route*'

SUCHEN MIT GREP
----------------
grep MUSTER datei           Zeilen mit Treffer
grep -i                     Groß/Klein ignorieren
grep -n                     Zeilennummern anzeigen
grep -c                     Nur Treffer zählen
grep -r ORDNER              Rekursiv suchen
grep -A3 -B3                Kontextzeilen mitliefern
Beispiele:
  grep -i kowalczyk fall/personen
  grep -n "02:1" fall/protokolle/kameras-giessergasse.log

SORTIEREN UND SCHNEIDEN
-----------------------
sort / sort -u              Sortieren / Dubletten weg
uniq                        Nebeneinanderliegende Dubletten weg (nach sort!)
cut -d'|' -f2               Spalten schneiden (Trenner '|')
tr 'a-z' 'A-Z'             Zeichen ersetzen
rev                         Zeile rückwärts

KODIERUNG / VERSCHLUESSELUNG
----------------------------
openssl base64 -in datei        Base64 kodieren (portabel)
openssl base64 -d -in datei     Base64 dekodieren (portabel)
(base64 -d auf Linux, base64 -D auf macOS)
ROT13 (Spielzeugchiffre):
  tr 'A-Za-z' 'N-Za-m...'   -> exakt:  tr 'A-Za-z' 'N-ZA-Mn-za-m'
AES mit openssl (wird im Fall verwendet):
  Verschlüsseln:  openssl enc -aes-256-cbc -salt -pbkdf2 -iter 10000 -a \\
                    -in klar.txt -out geheim.aes -pass pass:PASSWORT
  Entschlüsseln:  openssl enc -d -aes-256-cbc -a -pbkdf2 -iter 10000 \\
                    -in geheim.aes -pass pass:PASSWORT
Prüfsummen (macOS / Linux):
  echo -n 'Text' | md5        bzw.   echo -n 'Text' | md5sum
  shasum -a 256 datei         bzw.   sha256sum datei

GIT-FORENSIK (im beschlagnahmten Repo)
--------------------------------------
cd fall/repos/nachtschicht-logistik
git log --oneline           Historie kompakt
git log -p datei            Historie einer Datei inkl. Änderungen
git show SHA:pfad           Datei-Inhalt aus einem ALTEN Stand holen!
git show --stat SHA         Was wurde in diesem Commit geändert?
git diff SHA1 SHA2          Unterschiede zwischen Ständen
git fsck --lost-found       Verlorene/dangling Objekte finden
git reflog                  Wohin zeigte HEAD wann?

TIPPS FÜR DETEKTIVE
-------------------
* Logdateien dokumentieren sich selbst: lies zuerst die '#'-Zeilen.
* Schnittmengen: Ergebnisse in Dateien schreiben und mit
  'sort datei1 datei2 | uniq -d' vergleichen.
* Niemals raten: Jede Behauptung braucht eine Datei+Zeile als Beleg.
"""

LOESUNG = """LOESUNG — WIE MAN DEN FALL ABSCHLIESST
======================================

Wenn du sicher bist, den Namen der Person zu kennen, die den
Obsidian-Schlüssel gestohlen hat, dann prüfe ihn so (macOS):

    echo -n 'Vorname Nachname' | md5
    grep -if '<DEIN-HASH>' kodiert

Auf Linux heißt es 'md5sum' statt 'md5'. Wenn 'grep' den Hash in
der Datei 'kodiert' findet: Herzlichen Glückwunsch, Detektiv.

Danach wartet das versiegelte EPILOG auf dich (Passwort kennst du,
vier Buchstaben, ein Insekt):

    openssl enc -d -aes-256-cbc -a -pbkdf2 -iter 10000 \\
      -in fall/verschluesselt/epilog.aes -pass pass:PASSWORT

Und mit './pruefer.sh' kannst du deinen Abschlussbericht bewerten.
"""

EPILOG_PLAIN = """EPILOG — VERSIEGELTER BERICHT DES TCPD
======================================
Am Mittwoch, 18.03., 03:00 Uhr nahm das TCPD in der alten Güterhalle,
Tor 4, zwei Personen fest: die Kurierin M. K. und ihren Auftraggeber,
den Bank-Insider R. F. Der Obsidian-Schlüssel wurde unbeschadet
sichergestellt. Dr. Salomons letzte Espressotasse war die zweite:
Er hatte seinem Mörder noch einen Kaffee angeboten.
Fall 47/II: GELÖST.
"""

KODIER_FUELLER = [
    "Alicia Vogt","Benno Krause","Cem Aydin","Dörthe Peters","Emil Brandt",
    "Fenna Holm","Gustav Lehmann","Helga Ruf","Ingolf Bade","Jana Krebs",
    "Kalle Petersen","Lene Maak","Morten Siewert","Nadine Kolb","Otto Waalkes",
    "Pia Dahms","Quentin Tarantino","Rita Heyer","Sven-Ole Frahm","Telse Kruse",
    "Ulvi Alparslan","Vitus Frech","Wanja Slawik","Xenia Marschner","Yilmaz Aygün",
    "Ziska Riemann","Anselm Grunert","Berta Ohlsen","Clemens Usinger","Dagmar Vollmer",
]

def build_kodiert_loesung_epilog():
    hashes = []
    for name in KODIER_FUELLER:
        h = md5hex(name)
        hashes.append(h)
        hashes.append(md5hex(name.lower()))
    hashes.append(md5hex(TAETERIN_NAME))
    hashes.append(md5hex(TAETERIN_NAME.lower()))
    seen = set(); out = []
    for h in hashes:
        if h not in seen:
            seen.add(h); out.append(h)
    rng.shuffle(out)
    (GAME / "kodiert").write_text("\n".join(out) + "\n", encoding="utf-8")

    import base64
    d = FALL_DIR / "verschluesselt"
    src = d / "_epilog.tmp"
    src.write_text(EPILOG_PLAIN, encoding="utf-8")
    subprocess.run(["openssl", "enc", "-aes-256-cbc", "-salt", "-pbkdf2",
                    "-iter", "10000", "-a", "-in", str(src),
                    "-out", str(d / "epilog.aes"), "-pass", "pass:" + CODENAME],
                   check=True, capture_output=True)
    src.unlink()

PRUEFER_TEMPLATE = """#!/usr/bin/env bash
set -u
cd "$(dirname "$0")"

FORT=".fortschritt-pruefer"
HASHER="$(command -v shasum || true)"
SHA256() { if [ -n "$HASHER" ]; then "$HASHER" -a 256; else sha256sum; fi; }

norm() {
  local s="${1^^}"
  s="${s//Ä/AE}"; s="${s//Ö/OE}"; s="${s//Ü/UE}"; s="${s//ß/SS}"
  s="${s//É/E}"; s="${s//È/E}"; s="${s//Ê/E}"; s="${s//É/E}"
  local out="" ch i
  for (( i=0; i<${#s}; i++ )); do
    ch="${s:i:1}"
    [[ "$ch" =~ [A-Z0-9] ]] && out="$out$ch"
  done
  printf '%s' "$out"
}

ask() {
  local nr="$1" frage="$2" korrekt="$3" punkte="$4" antwort h
  printf '\\n== PRUEFPUNKT %s ==\\n%s\\n> ' "$nr" "$frage"
  read -r antwort
  h="$(printf '%s' "$(norm "$antwort")" | SHA256 | awk '{print $1}')"
  ok=0
  local ALT
  for ALT in ${korrekt//,/ }; do
    [ "$h" = "$ALT" ] && ok=1
  done
  if [ "$ok" = "1" ]; then
    echo "  >> RICHTIG. +$punkte Punkte"
    grep -q "^$nr " "$FORT" 2>/dev/null || printf '%s %s\\n' "$nr" "$punkte" >> "$FORT"
  else
    echo "  >> Leider nicht. (Aktenzeichen bleibt offen.)"
  fi
}

ART='
 ____________________
|  T E R M I N A L   |
|  C I T Y   I I     |
|____________________|
   \\^~~^/  TCPD
'

case "${1:-}" in
  --status)
    echo "== Fortschritt =="; cat "$FORT" 2>/dev/null || echo "(noch keine Prüfpunkte)"
    exit 0 ;;
  --reset)
    rm -f "$FORT"; echo "Fortschritt zurückgesetzt."; exit 0 ;;
esac

echo "$ART"
echo "PRUEFER DES TCPD — AKTE 47/II"
echo "(Antworten: normale Schreibweise, Groß-/Kleinschreibung egal)"
echo

[ "${2:-}" = "--force" ] && rm -f "$FORT"

ask 1 "Wie lautete der vollständige Name des Opfers?" "@H_OPFER@" 20
ask 2 "Welcher Club lieferte die entscheidende erste Spur? (Name wie im Verzeichnis)" "@H_CLUB@" 20
ask 3 "Welcher Codename tauchte in Route 7 als Fahrer auf?" "@H_CODE@" 20
ask 4 "Wie lautet der vollständige Name der Tätern/Täters?" "@H_TATER@" 20
ask 5 "Wo und wann sollte die Übergabe stattfinden? (Ort)" "@H_ORT@" 20

GESAMT=$(awk '{s+=$2} END{print s+0}' "$FORT" 2>/dev/null)
GESAMT=${GESAMT:-0}
echo
echo "== ZWISCHENSTAND: $GESAMT / 100 Punkte =="

if [ "$GESAMT" = "100" ]; then
cat <<'EOF'

      _____
     |A .  |-----.
     | /.\\ |c)   |   FALL 47/II GELÖST!
     |(_._)| /\\/ |
     |  |  |-----'
     |___V_|
EOF
echo "Bravo, Detective. Reiche deinen Bericht bei loesung ein."
fi
exit 0
"""

README = """DIE KOMMANDOZEILEN-MORDE II
===========================

      .______________________________________.
      |  ____  ____  ____  ____  ____  ____   |
      | ||T ||||E ||||R ||||M ||||I ||||N ||  |
      | ||__||||__||||__||||__||||__||||__||  |
      | |/==\\||/==\\||/==\\||/==\\||/==\\||/==\\|  |
      |  CITY  II   -   DER SCHLUESSEL        |
      |______________________________________|

Ein Mord in Terminal City — und diesmal führen die Spuren durch
Logdateien, verschlüsselte Notizen und ein beschlagnahmtes Git-
Repository.

Schnellstart
------------
    git clone <dieses-repo>
    cd <repo-name>
    cat anleitung
    less fall/tatort

Du brauchst nur ein Terminal (macOS oder Linux) mit `git`,
`openssl` und `base64`. Keine Installation, keine Anmeldung,
kein Internet während des Spiens.

Für Einsteiger: `cat spickzettel.md`
Fortschritt prüfen: `./pruefer.sh`

Über dieses Projekt
-------------------
Fortsetzung des Klassikers "The Command Line Murders" von
Noah Veltman (github.com/veltman/clmystery) in der Tradition der
deutschen Übersetzung von redbasecap. Diese Geschichte, alle Daten
und Figuren sind frei erfunden. Der Rauschen-Text stammt aus
"Alice's Abenteuer im Wunderland" (Übersetzung Antonie Zimmermann,
1869, Public Domain, Project Gutenberg #19778).

Lizenz: MIT — siehe LICENSE.md
"""

LICENSE = """MIT License

Copyright (c) 2026 Die Kommandozeilen-Morde II Autoren
Konzept-Tradition: "The Command Line Murders" (c) Noah Veltman, MIT

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

def main():
    if FALL_DIR.exists():
        shutil.rmtree(FALL_DIR)
    FALL_DIR.mkdir(parents=True)
    for name in ["kodiert", "anleitung", "spickzettel.md", "loesung", "README.md", "LICENSE.md"]:
        p = GAME / name
        if p.exists():
            p.unlink()
    for i in range(1, 11):
        p = GAME / f"hinweis{i}"
        if p.exists():
            p.unlink()

    build_streets()
    build_people()
    build_vehicles()
    build_memberships()
    build_interviews()
    build_protokolle()
    build_verschluesselt()
    gitmeta = build_git_repo()
    build_kodiert_loesung_epilog()

    z = ZEUGEN
    (FALL_DIR / "tatort").write_text(TATORT_TEXT % {
        "z0": z[0]["nr"], "z0v": z[0]["vorname"], "z0n": z[0]["nachname"],
        "z1": z[1]["nr"], "z1v": z[1]["vorname"], "z1n": z[1]["nachname"],
        "z2": z[2]["nr"], "z2v": z[2]["vorname"], "z2n": z[2]["nachname"],
    }, encoding="utf-8")
    (GAME / "anleitung").write_text(ANLEITUNG, encoding="utf-8")
    (GAME / "spickzettel.md").write_text(SPICKZETTEL, encoding="utf-8")
    (GAME / "loesung").write_text(LOESUNG, encoding="utf-8")
    (GAME / "README.md").write_text(README, encoding="utf-8")
    (GAME / "LICENSE.md").write_text(LICENSE, encoding="utf-8")
    for i, h in enumerate(HINTS, start=1):
        (GAME / f"hinweis{i}").write_text(h, encoding="utf-8")

    def hs(*variants):
        return ",".join(sha(v) for v in variants)
    ort_variants = hs(UEBERGABE, "alte " + UEBERGABE,
                      UEBERGABE + ", 18.03. 03:00",
                      "alte " + UEBERGABE + ", 18.03. 03:00")
    pruefer = (PRUEFER_TEMPLATE
        .replace("@H_OPFER@", hs(OPFER_NAME, "Dr. " + OPFER_NAME))
        .replace("@H_CLUB@", hs(CLUB_KURIERE.replace("_", " "), CLUB_KURIERE))
        .replace("@H_CODE@", sha(CODENAME))
        .replace("@H_TATER@", sha(TAETERIN_NAME))
        .replace("@H_ORT@", ort_variants))
    p = GAME / "pruefer.sh"
    p.write_text(pruefer, encoding="utf-8")
    os.chmod(p, 0o755)

    meta = {
        "opfer": OPFER_NAME, "taeterin": TAETERIN_NAME, "codename": CODENAME,
        "auftraggeber": AUFTRAGGEBER, "chip": CHIP_ID, "ausweis": AUSWEIS_NR,
        "club": CLUB_KURIERE, "uebergabe": UEBERGABE,
        "zeugen": [z_["nr"] for z_ in z],
        "decoys": {"a": DECOY_A, "b": DECOY_B},
        "hashes": {
            "opfer_sha256": sorted([sha(OPFER_NAME), sha("Dr. " + OPFER_NAME)]),
            "club_sha256": sorted([sha(CLUB_KURIERE.replace("_", " ")), sha(CLUB_KURIERE)]),
            "code_sha256": sha(CODENAME),
            "taeterin_sha256": sha(TAETERIN_NAME),
            "ort_sha256": sorted([sha(v) for v in
                [UEBERGABE, "alte " + UEBERGABE, UEBERGABE + ", 18.03. 03:00",
                 "alte " + UEBERGABE + ", 18.03. 03:00"]]),
            "taeterin_md5": md5hex(TAETERIN_NAME),
        },
        "counts": {
            "personen": len(PEOPLE),
            "kurier_club_size": CLUBS[CLUB_KURIERE],
            "interviews": len(list((FALL_DIR / "befragungen").iterdir())),
            "strassen": len(STRASSEN),
        },
        "git": gitmeta,
        "verify": {
            "note_rot13_b64_sha256": __import__("hashlib").sha256(NOTE_PLAIN.encode()).hexdigest(),
            "mail_contains": "r.falkenberg",
            "route7_contains": "PAKET-OBSIDIAN",
            "wespe_txt_contains": AUSWEIS_NR,
            "dangling_contains": "Gueterhalle",
            "camera_line": "2026-03-14 02:12:41 | KAM-11",
            "gate_k": "2026-03-14 02:23:45 | GRUENPLATZ | AUSGANG | CHIP-8842",
            "gate_b": "2026-03-14 02:36:12 | GRUENPLATZ | AUSGANG | CHIP-6609",
            "gate_r": "2026-03-14 02:44:02 | NORDHAFEN | AUSGANG | CHIP-5177",
            "alibi_a": "02:01:37",
            "alibi_b1": "02:10:55",
            "alibi_b2": "02:22:40",
        },
    }
    (Path(__file__).resolve().parent / "meta.json").write_text(
        json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")

    print("OK generiert:", GAME)
    print("Kurierinnen/Kuriere:", CLUBS[CLUB_KURIERE])
    print("Git-Anker:", gitmeta)

if __name__ == "__main__":
    main()
