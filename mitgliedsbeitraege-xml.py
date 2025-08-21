from sepaxml import SepaDD
from sepaxml.validation import ValidationError
import datetime
import pandas as pd
import tomllib
import argparse
import sys
from pathlib import Path

MONTHS = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", 
          "August", "September", "Oktober", "November", "Dezember"]

def validateMember(member):
    requiredColumns = ["Datum SEPA Mandat", "IBAN", "BIC", "Kontoinhaber",
                        "Beitrag", "Mandatsreferenz"]
    for c in requiredColumns:
        if pd.isnull(member[c]):
            raise ValueError(f"CRITICAL: {c} ist leer bei {member['Vorname']} {member['Nachname']}!")

def determineCollectionDate(minDelta: int) -> datetime.date:
    collectionDate = (datetime.date.today().replace(day=1) + datetime.timedelta(days=32)).replace(day=1) # first of next month
    if collectionDate - datetime.date.today() < datetime.timedelta(days=minDelta):
        collectionDate = datetime.date.today() + datetime.timedelte(days=minDelta)
        
    return collectionDate

def validateInput(members):
    requiredColumns = set(["Nachname", "Vorname", "Aktiv", "Datum SEPA Mandat", 
                            "IBAN", "BIC", "Kontoinhaber", "Beitrag", "Mandatsreferenz"])
    missingColumns = requiredColumns - set(members.columns)
    if missingColumns:
        raise ValueError(f"CRITICAL: Der Mitgliedertabelle fehlen die Spalten {missingColumns}!")
    if not members.dtypes["Beitrag"] == "int64":
        raise TypeError(f"CRITICAL: Die Spalte 'Beitrag' muss ganze Zahlen enthalten (Centbeträge).")


if __name__ == '__main__':

    todayStr = datetime.date.today().strftime('%Y-%m-%d')

    parser = argparse.ArgumentParser(
        prog='Mitgliedsbeiträge XML',
        description='Erstellt eine XML Datei zum Einzug von Mitgliedsbeiträgen aus einer Tabelle der Vereinsmitglieder.',)

    parser.add_argument('filename', default="mitgliedertabelle.ods", help="Mitgliedertabelle als .ods oder .xlsx")
    parser.add_argument('-c', '--configfile', default="config.toml", help="Konfigurationsdatei im TOML Format. (default: config.toml)")
    parser.add_argument('-o', '--output', default=f"sammelauftrag-{todayStr}.xml", help="Ausgabe XML Datei für Sammelauftrag. (default: sammelauftrag-{aktuelles-datum}.xml)")
    parser.add_argument('-p', '--print', action=argparse.BooleanOptionalAction, help="Flag gibt an dass das XML auch auf dem Terminal ausgegeben werden soll.")
    parser.add_argument('-d', '--delta', default=10, type=int, help="Tage die mindestens zwischen jetzt und dem Fälligkeitsdatum der Lastschrift liegen sollen. (default: 10)")

    args = parser.parse_args()

    if not Path(args.filename).is_file():
        print(f"CRITICAL: Eingabedatei {args.filename} existiert nicht!")
        sys.exit(1)

    if not Path(args.configfile).is_file():
        print(f"CRITICAL: Konfigurationsdatei {args.configfile} existiert nicht!")
        sys.exit(1)

    with open(args.configfile, "rb") as f:
        config_data = tomllib.load(f)
    print(f"Benutze Konfiguration: {config_data}.\n")

    config = {
        "name": config_data["verein_name"],
        "IBAN": config_data["verein_iban"],
        "BIC": config_data["verein_bic"],
        "batch": True,
        "creditor_id": config_data["verein_creditor_id"],
        "instrument": "CORE",
        "currency": "EUR",
    }

    sepa = SepaDD(config, schema="pain.008.001.02", clean=True)

    try:
        members = pd.read_excel(args.filename, sheet_name="Mitglieder")
        validateInput(members)
    except (ValueError, TypeError) as e:
        print(e)
        sys.exit(1)

    members = members[~members["Aktiv"].isnull()]
    members["Datum SEPA Mandat"] = members["Datum SEPA Mandat"].dt.date

    print(f"Aktive Mitglieder: {len(members)}")

    collectionDate = determineCollectionDate()

    for i, m in members.iterrows():

        try:
            validateMember(m)
        except ValueError as e:
            print(e)
            sys.exit(1)

        payment = {
            "name": m["Kontoinhaber"],
            "IBAN": m["IBAN"].strip(),
            "BIC": m["BIC"].strip(),
            "amount": m["Beitrag"], # in cents
            "type": "RCUR", # FRST, RCUR, OOFF, FNAL, TODO notwendig?
            "collection_date": collectionDate,
            "mandate_id": m["Mandatsreferenz"].strip(),
            "mandate_date": m["Datum SEPA Mandat"],
            "description": f"{config_data['sepa_description']} {MONTHS[collectionDate.month-1]} {collectionDate.year}",
        }

        sepa.add_payment(payment)

    try:
        xml = sepa.export(validate=True, pretty_print=True).decode('utf-8')
    except ValidationError as e:
        print(e.__cause__)
        sys.exit(1)
    except TypeError as e:
        print(e)
        sys.exit(1)

    print(f"Gesamtbetrag: {list(sepa._batch_totals.items())[0][1]/100:.2f} €")

    with open(args.output, "w", encoding='utf-8') as f:
        f.write(xml)
    print(f"XML Ausgabe gespeichert in {args.output}.")

    if args.print:
        print('')
        print(xml)

