import chardet
import io
import pandas as pd


def read_csv_with_encoding(file):
    raw = file.read()
    encoding = chardet.detect(raw)["encoding"] or "utf-8"
    return pd.read_csv(io.BytesIO(raw), encoding=encoding)


def map_columns(df, header_map):
    new_columns = {}
    for col in df.columns:
        for key, possible_names in header_map.items():
            if str(col).strip() in possible_names:
                new_columns[col] = key
                break
    return df.rename(columns=new_columns)


def coerce_types(df):
    if "transaction_date" in df.columns:
        df["transaction_date"] = pd.to_datetime(
            df["transaction_date"], errors="coerce", dayfirst=True
        ).dt.strftime("%d.%m.%Y")

    if "currency" in df.columns:
        df["currency"] = df["currency"].fillna("KZT").replace({"₸": "KZT"})

    df = df.where(pd.notnull(df), None)
    return df
