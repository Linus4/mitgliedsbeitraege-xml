from sepaxml import SepaDD
from sepaxml.validation import ValidationError
import datetime
import pandas as pd
import tomllib
import argparse
import sys
from pathlib import Path

def validate_member(member):
    required_columns = ["Datum SEPA Mandat", "IBAN", "BIC", "Kontoinhaber",
                        "Beitrag", "Mandatsreferenz"]
    for c in required_columns:
        if pd.isnull(member[c]):
            print(f"CRITICAL: {c} ist leer bei {member['Vorname']} {member['Nachname']}!")
            sys.exit(1)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        prog='Mitgliedsbeiträge XML',
        description='Erstellt eine XML Datei zum Einzug von Vereinsmitgliedsbeiträgen auf Grundlage einer Mitgliederliste.',)

    parser.add_argument('filename', default="mitgliederliste.ods", help="Mitgliederliste als .ods oder .xlsx")
    parser.add_argument('-c', '--configfile', default="config.toml", help="Konfigurationsdatei im TOML Format")
    parser.add_argument('-o', '--output', default="sammelauftrag.xml", help="Ausgabe XML Datei für Sammelauftrag")

    args = parser.parse_args()

    if not Path(args.filename).is_file():
        print(f"CRITICAL: Eingabedatei {args.filename} existiert nicht!")
        sys.exit(1)

    if not Path(args.configfile).is_file():
        print(f"CRITICAL: Konfigurationsdatei {args.configfile} existiert nicht!")
        sys.exit(1)

    months = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", 
              "August", "September", "Oktober", "November", "Dezember"]

    with open(args.configfile, "rb") as f:
        config_data = tomllib.load(f)
    print(config_data)

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

    members = pd.read_excel(args.filename, sheet_name="Mitglieder")
    members = members[~members["Aktiv"].isnull()]
    members["Datum SEPA Mandat"] = members["Datum SEPA Mandat"].dt.date

    print(f"Aktive Mitglieder: {len(members)}")

    collection_date = (datetime.date.today().replace(day=1) + datetime.timedelta(days=32)).replace(day=1) # first of next month
    if collection_date - datetime.date.today() < datetime.timedelta(days=10):
        collection_date = datetime.date.today() + datetime.timedelte(days=10)

    total_amount = 0

    for i, m in members.iterrows():

        validate_member(m)

        payment = {
            "name": m["Kontoinhaber"],
            "IBAN": m["IBAN"],
            "BIC": m["BIC"],
            "amount": m["Beitrag"], # in cents
            "type": "RCUR", # FRST, RCUR, OOFF, FNAL
            "collection_date": collection_date,
            "mandate_id": m["Mandatsreferenz"],
            "mandate_date": m["Datum SEPA Mandat"],
            "description": f"{config_data['sepa_description']} {months[collection_date.month-1]} {collection_date.year}",
        }

        sepa.add_payment(payment)
        total_amount += m["Beitrag"]

    try:
        xml = sepa.export(validate=True, pretty_print=True).decode('utf-8')
        print(xml)
        with open(args.output, "w", encoding='utf-8') as f:
            f.write(xml)
    except ValidationError as e:
        print(e.__cause__)
        sys.exit(1)

    print(f"Gesamtbetrag: {total_amount/100:.2f} €")
# TODO  AmdmntInd false?
