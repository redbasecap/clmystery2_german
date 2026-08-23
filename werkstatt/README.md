# Werkstatt (Build-Workspace)

Dieses Verzeichnis liegt NUR auf dem Branch `werkstatt` — nie auf `master`.
`master` ist das reine, spoilerfreie Spiel.

Inhalt
------
* `generator.py`   erzeugt ALLES auf master (fall/, kodiert, Texte, pruefer.sh)
* `meta.json`      Antworten/Hashes/Anker (wird vom Harness gelesen) — SPOILER
* `test_harness.sh` 29 Checks: Loesungskette, Krypto-Roundtrips, Git-Forensik,
                    Struktur, Pruefer-Konsistenz, Spoiler-Sweep
* `pack_evidenz.sh` staged das Kurier-Repo inkl. `.gitarchiv` sauber in master
* `assets/alice_de.txt` Public-Domain-Rauschtext (Gutenberg #19778)

Regenerations-Workflow
----------------------
    python3 generator.py          # schreibt komplettes Spiel in Repo-Root
    bash pack_evidenz.sh          # evidence-repo in den Index (nach jedem Lauf!)
    bash test_harness.sh          # alles gruen?
    git ...                       # master committen, dann Aenderungen hier einpflegen

Wichtig
-------
* `generator.py` und `meta.json` enthalten die LOESUNG. Niemals nach master.
* Nach JEDER Regenerierung `pack_evidenz.sh` ausfuehren (Git-Anker-Shas aendern
  sich, meta.json wird neu geschrieben).
* Der Spieler stellt das Image im Spiel selbst her:
  `sh fall/repos/nachtschicht-logistik/ermittlung-starten.sh`
