#!/usr/bin/env bash
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
  printf '\n== PRUEFPUNKT %s ==\n%s\n> ' "$nr" "$frage"
  read -r antwort
  h="$(printf '%s' "$(norm "$antwort")" | SHA256 | awk '{print $1}')"
  ok=0
  local ALT
  for ALT in ${korrekt//,/ }; do
    [ "$h" = "$ALT" ] && ok=1
  done
  if [ "$ok" = "1" ]; then
    echo "  >> RICHTIG. +$punkte Punkte"
    grep -q "^$nr " "$FORT" 2>/dev/null || printf '%s %s\n' "$nr" "$punkte" >> "$FORT"
  else
    echo "  >> Leider nicht. (Aktenzeichen bleibt offen.)"
  fi
}

ART='
 ____________________
|  T E R M I N A L   |
|  C I T Y   I I     |
|____________________|
   \^~~^/  TCPD
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

ask 1 "Wie lautete der vollständige Name des Opfers?" "131b5ec744541f6394ab27b6f72f5491c03d25d139547442943fe38391375241,b13638382a8a937c5faa04706f856c847363989c16f9ce57c6cef649ca9bb420" 20
ask 2 "Welcher Club lieferte die entscheidende erste Spur? (Name wie im Verzeichnis)" "da35925396a8f5c51d3fac6afb146cba888e5af6bfd4affa67f537c3dbbd67ca,da35925396a8f5c51d3fac6afb146cba888e5af6bfd4affa67f537c3dbbd67ca" 20
ask 3 "Welcher Codename tauchte in Route 7 als Fahrer auf?" "41f00ba454c942bebc24374d73871549ec6022c8d57bb65b071d6bcef8eabce8" 20
ask 4 "Wie lautet der vollständige Name der Tätern/Täters?" "69bf16e2406693677245affa1d81ff381648472e0f4c127529fa9dd033579e9f" 20
ask 5 "Wo und wann sollte die Übergabe stattfinden? (Ort)" "d44f82f61f2790f63404e2256f2d5a0a0446a913fdadb98ff076446720fbd231,deaced20094055d4ac64167b9ec2b157fb44e942cfadd245101ccef4081a12bb,852a8b058467adec84ac38363ee30c20cb9c7607ceba1443d7fdb1a788d39306,b77101d7ba01921f462ac55930760b218ca390d832c381ef429a0524b8260483" 20

GESAMT=$(awk '{s+=$2} END{print s+0}' "$FORT" 2>/dev/null)
GESAMT=${GESAMT:-0}
echo
echo "== ZWISCHENSTAND: $GESAMT / 100 Punkte =="

if [ "$GESAMT" = "100" ]; then
cat <<'EOF'

      _____
     |A .  |-----.
     | /.\ |c)   |   FALL 47/II GELÖST!
     |(_._)| /\/ |
     |  |  |-----'
     |___V_|
EOF
echo "Bravo, Detective. Reiche deinen Bericht bei loesung ein."
fi
exit 0
