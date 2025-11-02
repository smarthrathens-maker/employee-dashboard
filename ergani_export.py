import pandas as pd

def generate_ergani_file(df):
    export_df = df[["Id", "Name_fin", "Stamp Category", "Total Amount (w.o. tips)"]]
    export_df.columns = ["ID", "Όνομα", "Είδος Ενσήμου", "Τζίρος"]
    return export_df.to_csv(index=False, sep=";", encoding="utf-8")
