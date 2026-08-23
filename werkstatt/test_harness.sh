#!/usr/bin/env bash
# Test harness for "Die Kommandozeilen-Morde II" (SPOILER-HEFTIG — nur fuer die Werkstatt!)
# Usage: ./test_harness.sh
set -u
cd "$(dirname "$0")/.."

PASS=0; FAIL=0
ok()  { PASS=$((PASS+1)); echo "  OK   $1"; }
bad() { FAIL=$((FAIL+1)); echo "  FAIL $1"; }

META="werkstatt/meta.json"
[ -f "$META" ] || { echo "meta.json fehlt"; exit 1; }
jget() { python3 -c "import json,sys;m=json.load(open('$META'));print(eval('m'+sys.argv[1]))" "$1"; }

HASHER="$(command -v md5 || command -v md5sum)"
SHA256() { if command -v shasum >/dev/null 2>&1; then shasum -a 256 | awk '{print $1}'; else sha256sum | awk '{print $1}'; fi; }

echo "=== 1. Loesungskette ==="
TAETERIN="$(jget "['taeterin']")"
H=$(printf '%s' "$TAETERIN" | "$HASHER" | awk '{print $NF}')
grep -qi "^$H$" kodiert && ok "md5('$TAETERIN') in kodiert" || bad "md5 nicht in kodiert"

CAM="$(jget "['verify']['camera_line']")"
grep -qF "$CAM" fall/protokolle/kameras-giessergasse.log && ok "Kamera-Zeile 02:12:41 vorhanden" || bad "Kamera-Zeile fehlt"

GK="$(jget "['verify']['gate_k']")"
GB="$(jget "['verify']['gate_b']")"
GR="$(jget "['verify']['gate_r']")"
grep -qF "$GK" fall/protokolle/ubahn-drehkreuze.log && ok "Drehkreuz CHIP-8842 Gruenplatz" || bad "CHIP-8842 fehlt"
grep -qF "$GB" fall/protokolle/ubahn-drehkreuze.log && ok "Drehkreuz CHIP-6609 Gruenplatz (Decoy B)" || bad "CHIP-6609 fehlt"
grep -qF "$GR" fall/protokolle/ubahn-drehkreuze.log && ok "Drehkreuz CHIP-5177 Nordhafen (Decoy A)" || bad "CHIP-5177 fehlt"

N_CAND=$(grep -E "^2026-03-14 02:(1[5-9]|[23][0-9]|4[0-5]):" fall/protokolle/ubahn-drehkreuze.log \
  | grep "GRUENPLATZ | AUSGANG" | grep -oE "CHIP-[0-9]+" | sort -u \
  | while read -r ch; do grep "^$ch," fall/protokolle/chip-zuordnung.csv; done \
  | awk -F, '{print $2"|"$3}' | sort -u \
  | comm -12 - <(tail -n +4 fall/mitgliedschaften/Kuriere_der_Nacht | sed '/^$/d' | sed 's/, /|/' | sort -u) \
  | wc -l | tr -d ' ')
[ "$N_CAND" = "2" ] && ok "Club n Transitfenster == genau 2 Kandidaten" || bad "Kandidaten nach F2: $N_CAND (erwartet 2)"

AB1="$(jget "['verify']['alibi_b1']")"
AB2="$(jget "['verify']['alibi_b2']")"
NUM_B=$(grep ",Baranowski,Ivo$" fall/protokolle/telefonbuch.csv | cut -d, -f1)
HITS=$(grep " $NUM_B " fall/protokolle/funkzellen.log | grep -cE "^2026-03-14 02:(10|22)" || true)
[ "$HITS" = "2" ] && ok "Alibi Decoy B: 2 Funkzellen-Treffer im Fenster" || bad "Alibi B Treffer=$HITS"

echo "=== 2. Verschluesselung ==="
NOTE_H=$(openssl base64 -d -in fall/verschluesselt/notiz-am-zaun.txt 2>/dev/null | tr 'A-Za-z' 'N-ZA-Mn-za-m' | SHA256)
WANT_NOTE=$(jget "['verify']['note_rot13_b64_sha256']")
[ "$NOTE_H" = "$WANT_NOTE" ] && ok "rot13+b64 Notiz roundtrip" || bad "Notiz-Inhalt falsch ($NOTE_H)"

MAIL=$(openssl enc -d -aes-256-cbc -a -pbkdf2 -iter 10000 -in fall/verschluesselt/auftraggeber.eml.aes -pass pass:WESPE 2>/dev/null)
echo "$MAIL" | grep -q "$(jget "['verify']['mail_contains']")" && ok "AES-Mail entschluesselt mit WESPE" || bad "AES-Mail kaputt"

EPI=$(openssl enc -d -aes-256-cbc -a -pbkdf2 -iter 10000 -in fall/verschluesselt/epilog.aes -pass pass:WESPE 2>/dev/null)
echo "$EPI" | grep -qi "Fall 47/II" && ok "Epilog entschluesselt" || bad "Epilog kaputt"

echo "=== 3. Git-Forensik ==="
REPO="fall/repos/nachtschicht-logistik"
C_TEAM=$(jget "['git']['C_TEAM']")
C_ROUTE7=$(jget "['git']['C_ROUTE7']")
DANGLING=$(jget "['git']['DANGLING']")
git -C "$REPO" show "$C_TEAM:team/wespe.txt" | grep -q "$(jget "['verify']['wespe_txt_contains']")" && ok "team/wespe.txt wiederherstellbar" || bad "wespe.txt nicht holbar"
git -C "$REPO" show "$C_ROUTE7:kunden/route-7.csv" | grep -q "$(jget "['verify']['route7_contains']")" && ok "route-7.csv wiederherstellbar" || bad "route-7.csv nicht holbar"
FSCK_OUT=$(LC_ALL=C git -C "$REPO" fsck --dangling 2>/dev/null)
echo "$FSCK_OUT" | grep -q "$DANGLING" && ok "dangling commit auffindbar" || bad "dangling fehlt: $FSCK_OUT"
git -C "$REPO" show "$DANGLING:entwurf/uebergabe.md" | grep -qi "$(jget "['verify']['dangling_contains']")" && ok "Entwurf enthaelt Uebergabeort" || bad "Entwurf-Inhalt falsch"

echo "=== 4. Struktur & Mengen ==="
P_ROWS=$(tail -n +9 fall/personen | wc -l | tr -d ' ')
WANT_P=$(jget "['counts']['personen']")
[ "$P_ROWS" = "$WANT_P" ] && ok "personen rows == $WANT_P" || bad "personen rows=$P_ROWS erwartet $WANT_P"

K_SIZE=$(tail -n +4 fall/mitgliedschaften/Kuriere_der_Nacht | grep -vc '^$')
WANT_K=$(jget "['counts']['kurier_club_size']")
[ "$K_SIZE" = "$WANT_K" ] && ok "Kurierclub == $WANT_K" || bad "Kurierclub=$K_SIZE"

I_CNT=$(ls fall/befragungen | wc -l | tr -d ' ')
WANT_I=$(jget "['counts']['interviews']")
[ "$I_CNT" = "$WANT_I" ] && ok "befragungen == $WANT_I" || bad "befragungen=$I_CNT"

for nr in $(jget "['zeugen']" | tr -d "[]" | tr "," "\n" | tr -d " "); do
  [ -f "fall/befragungen/befragung-$nr" ] && ok "Zeugen-Befragung $nr existiert" || bad "befragung-$nr fehlt"
done

STREET_BAD=0
for f in fall/strassen/*.txt; do
  lc=$(wc -l < "$f" | tr -d ' '); [ "$lc" = "300" ] || STREET_BAD=$((STREET_BAD+1))
done
[ "$STREET_BAD" = "0" ] && ok "alle 36 Strassendateien haben 300 Zeilen" || bad "$STREET_BAD Strassen abweichend"

ADDR_BAD=0
while IFS=$'\t' read -r name gender age address; do
  street=$(echo "$address" | sed -E 's/, Zeile [0-9]+$//'); line=$(echo "$address" | grep -oE '[0-9]+$')
  fname="fall/strassen/${street// /_}.txt"
  if [ -f "$fname" ]; then
    lc=$(wc -l < "$fname" | tr -d ' ')
    [ "$line" -le "$lc" ] || ADDR_BAD=$((ADDR_BAD+1))
  else
    ADDR_BAD=$((ADDR_BAD+1))
  fi
done < <(tail -n +9 fall/personen)
[ "$ADDR_BAD" = "0" ] && ok "alle Adresszeilen innerhalb der Strassendatei (keine Out-of-Range-Haeuser!)" || bad "$ADDR_BAD Adressen out-of-range"

echo "=== 5. Pruefer-Konsistenz ==="
for stage in opfer club code taeterin ort; do
  HASHES=$(jget "['hashes']['${stage}_sha256']" | tr -d "[]'" | tr ',' '\n' | sed 's/ //g')
  FOUND=0
  for h in $HASHES; do
    grep -q "$h" pruefer.sh && FOUND=1
  done
  [ "$FOUND" = "1" ] && ok "pruefer Stage '$stage' Hash abgedeckt" || bad "pruefer Stage '$stage' fehlt"
done

echo "=== 6. Spoiler-Sweep (Master-Dateien duerfen nichts verraten) ==="
SPOIL_OK=1
for pat in "Kowalczyk" "Baranowski" "Renner" "Falkenberg"; do
  HITS=$(grep -rl "$pat" anleitung spickzettel.md README.md LICENSE.md loesung hinweis* pruefer.sh kodiert fall/tatort 2>/dev/null | wc -l | tr -d ' ')
  [ "$HITS" != "0" ] && { SPOIL_OK=0; bad "Spoiler '$pat' in Master-Narrativ-Dateien"; }
done
[ "$SPOIL_OK" = "1" ] && ok "keine Tater/Auftraggeber-Namen im Narrativ"
WESPE_HITS=$(grep -rn "WESPE" anleitung spickzettel.md README.md loesung hinweis* pruefer.sh fall/tatort 2>/dev/null | wc -l | tr -d ' ')
[ "$WESPE_HITS" = "0" ] && ok "Codename WESPE nicht im Klartext (nur verschluesselt/git)" || bad "WESPE im Klartext sichtbar!"

echo ""
echo "=== SUMMARY: $PASS passed, $FAIL failed ==="
[ "$FAIL" = "0" ]
