SPICKZETTEL — DIE KOMMANDOZEILEN-MORDE II
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
  Verschlüsseln:  openssl enc -aes-256-cbc -salt -pbkdf2 -iter 10000 -a \
                    -in klar.txt -out geheim.aes -pass pass:PASSWORT
  Entschlüsseln:  openssl enc -d -aes-256-cbc -a -pbkdf2 -iter 10000 \
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
