from decimal import Decimal
import pandas as pd




def clean_text(col):
    return col.astype(str).str.replace('\u202f', '').str.strip()


def clean_decimal(col):
    #Nettoie une colonne (espace, caractères spéciaux) et convertit en Decimal
    return col.astype(str).str.replace(' ', '').str.replace('\u202f', '').apply(lambda x: Decimal(x) if x not in ["", "nan", "None"] else None)

def clean_date(col):
    return pd.to_datetime(col, errors="coerce")