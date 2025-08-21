from sepaxml import SepaDD
import datetime
import pandas as pd
import tomllib
import argparse

parser = argparse.ArgumentParser(
    prog='Mitgliedsbeiträge XML',
    description='Erstellt eine XML Datei zum Einzug von Vereinsmitgliedsbeiträgen auf Grundlage einer Mitgliederliste.',)

parser.add_argument('filename', default="mitgliederliste.ods", help="Mitgliederliste als .ods oder .xlsx", required=True)
parser.add_argument('-c', '--configfile', "config.toml", help="Konfigurationsdatei im TOML Format")

args = parser.parse_args()

months = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", 
          "August", "September", "Oktober", "November", "Dezember"]

with open(args.configfile, "rb") as f:
    config_data = tomllib.load(f)

config = {
    "name": config_data["verein_name"],
    "IBAN": config_data["verein_iban"],
    "BIC": config_data["verein_bic"],
    "batch": True,
    "creditor_id": config_data["verein_creditor_id"],
    "instrument": "CORE",
    "currency": "EUR",
}
print(config)

sepa = SepaDD(config, schema="pain.008.001.02", clean=True)

members = pd.read_excel(args.filename)
members = members[~members["Aktiv"].isnull()]

print(f"Aktive Mitglieder: {len(members)}")

collection_date = (datetime.date.today().replace(day=1) + datetime.timedelta(days=32)).replace(day=1) # first of next month
if collection_date - datetime.date.today() < datetime.timedelta(days=10):
    collection_date = datetime.date.today() + datetime.timedelte(days=10)

total_amount = 0

for i, m in members.iterrow():

    payment = {
        "name": m["Kontoinhaber"],
        "IBAN": m["IBAN"],
        "BIC": m["BLZ"],
        "amount": m["Beitrag"]*100, # in cents
        "type": "RCUR", # FRST, RCUR, OOFF, FNAL
        "collection_date": collection_date,
        "mandate_id": m["Mandatsreferenz"],
        "mandate_date": m["Datum SEPA Mandat"],
        "description": f"{config_data["sepa_description"] {months[collection_date.month-1} {collection_date.year}}",
    }

    sepa.add_payment(payment)
    total_amount += m["Beitrag"]*100

print(sepa.export(validate=True))
