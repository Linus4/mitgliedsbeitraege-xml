# mitgliedsbeitraege-xml
Erstellt eine XML Datei zum Einzug von Vereinsmitgliedsbeiträgen auf Grundlage einer Mitgliederliste.

## Installation

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Konfiguration

Kopiere `config.toml.example` und nenne die Datei `config.toml`. Passe die Werte darin an.

## Ausführen

Die .ods oder .xlsx Datei, die dem Program als Eingabe gegeben wird, muss ein
Tabellenblat mit dem Namen "Mitglieder" enthalten.

Eine Spalte "Aktiv" muss vorhanden sein. Leere Zellen werden ignoriert (inaktives
Mitglied) und Zellen mit beliebigem Inhalt werden verarbeitet (aktives Mitglied).

Eine Spalte "Datum SEPA Mandat" mit einem Datum im ISO Format (z.B. "2025-08-21) 
muss vorhanden sein.

Die Spalten "IBAN", "BLZ", "Kontoinhaber" müssen existieren und nicht leer sein.

Eine Spalte "Mandatsreferenz" muss existieren und nicht leer sein. Dies kann ein
bis zu 35 Zeichen langer String sein, der aus Buchstaben, Zahlen und Bindestrichen
besteht und pro SEPA Lastschriftmandat vom Verein festgelegt wird. Besser nochmal 
nachlesen.

Eine Spalte "Beitrag" muss existieren und einen monatlichen Beitrag in **Cent** 
(ganze Zahl) enthalten.
