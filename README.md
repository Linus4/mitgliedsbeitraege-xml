# mitgliedsbeitraege-xml

Erstellt eine XML Datei zum Einzug von Mitgliedsbeiträgen für den kommenden 
Monat aus einer Tabelle der Vereinsmitglieder.

> Ich benutze das (noch) nicht wirklich im Verein, sondern habe es eher
> geschrieben, um zu sehen, ob das umsetzbar ist und welche Probleme dabei
> auftreten.

## Installation

Zunächst müssen Git und Python (mindestens Version 3.11) installiert werden. 

Dann:

```
git clone https://github.com/Linus4/mitgliedsbeitraege-xml.git
cd mitgliedsbeitraege-xml
python -m venv venv # oder python3
source venv/bin/activate
pip install -r requirements.txt
```

## Konfiguration

Kopiere `config.toml.example` und nenne die Datei `config.toml`. Passe die Werte 
darin für deinen Verein entsprechend an.

### Beispiel

```
verein_name = "Name des Vereins"
verein_iban = "IBAN des Vereins"
verein_bic = "BIC des Vereins"
verein_creditor_id = "Gläubiger ID des Vereins"
sepa_description = "Verwendungszweck"
```

## Eingabetabelle

Die .ods oder .xlsx Datei, die dem Program als Eingabe gegeben wird, muss ein
Tabellenblat mit dem Namen `Mitglieder` enthalten.

Eine Spalte `Aktiv` muss vorhanden sein. Leere Zellen werden ignoriert (inaktives
Mitglied) und Zellen mit beliebigem Inhalt werden weiterverarbeitet (aktives Mitglied).

Eine Spalte `Datum SEPA Mandat` mit einem Datum im ISO Format (z.B. `2025-08-21`) 
muss vorhanden sein und nicht leer sein.

Die Spalten `IBAN`, `BIC` und `Kontoinhaber` müssen existieren und nicht leer sein.

Eine Spalte `Mandatsreferenz` muss existieren und nicht leer sein. Dies kann ein
bis zu 35 Zeichen langer String sein, der aus Buchstaben, Zahlen und Bindestrichen
besteht und pro SEPA Lastschriftmandat vom Verein festgelegt wird. Besser nochmal 
nachlesen.

Eine Spalte `Beitrag` muss existieren und einen monatlichen Beitrag in **Cent** 
(ganze Zahl) enthalten.

### Beispiel

| Nachname | Vorname | Aktiv | Datum SEPA Mandat | IBAN | BIC | Kontoinhaber | Beitrag | Mandatsreferenz | [weitere Spalten] |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Silie | Petra | x | 2020-05-28 | DE02120300000000202051 | BYLADEM1001 | Petra Silie | 500 | MX00001-00001 | ... |
| Racho | Volker |  | 2020-05-28 | DE02600501010002034304 | SOLADEST600 | Volker Racho | 1000 | MX00002-00001 | ... |

## Ausführen

Vor dem Ausführen muss die virtuelle Umgebung mit `source venv/bin/activate` 
aktiviert werden. Vor dem Prompt sollte in Klammern der Name der Umgebung 
erscheinen.

```
usage: mitgliedsbeitraege-xml.py [-h] [-c CONFIGFILE] [-o OUTPUT] [-p | --print | --no-print] [-d DELTA] [-f FDATE]
                                 filename

Erstellt eine XML Datei zum Einzug von Mitgliedsbeiträgen für den kommenden Monat aus einer Tabelle der
Vereinsmitglieder.

positional arguments:
  filename              Mitgliedertabelle als .ods oder .xlsx

options:
  -h, --help            show this help message and exit
  -c CONFIGFILE, --configfile CONFIGFILE
                        Konfigurationsdatei im TOML Format. (default: config.toml)
  -o OUTPUT, --output OUTPUT
                        Ausgabe XML Datei für Sammelauftrag. (default: sammelauftrag-{aktuelles-datum}.xml)
  -p, --print, --no-print
                        Flag gibt an dass das XML auch auf dem Terminal ausgegeben werden soll.
  -d DELTA, --delta DELTA
                        Tage die mindestens zwischen jetzt und dem Fälligkeitsdatum der Lastschrift liegen sollen.
                        (default: 10)
  -f FDATE, --fdate FDATE
                        Fälligkeitsdatum, an dem die Lastschrift eingezogen wird. Im ISO Format (z.B. 2025-09-02).
                        Überschreibt --delta.
```

### Beispiel

```
python mitgliedsbeitraege-xml.py mitgliedertabelle.ods
```

Nimmt die Konfigurationsdatei `config.toml` und schreibt in die XML Datei
`sammelauftrag-{aktuelles-datum}.xml`.
