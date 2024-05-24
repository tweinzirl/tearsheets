import pandas as pd
import numpy as np
import os
from schema_config import data_dict
from config import bal_accts

try:
   from dbio import connectors
except ImportError: 
    print("No module named 'dbio', so can't use write_db()")

db = './generic_bank.db'
cobj = connectors.SQLite(database=db)


def data():
    df_dict = {}
    files_dir = os.path.join(".", "personas")
    files = os.listdir(files_dir)
    for f in files:
        if f.endswith(".csv"):
            name = f.split(".csv")[0]
            file_path = os.path.join(files_dir, f)
            df = pd.read_csv(file_path, index_col=0)
            df_dict[name] = df
    return df_dict

def personas_client_table(df_dict):
    client_table_columns = [k for k in data_dict["clients"]["column_mapping"].keys()]
    assign_region = lambda x: ("West" if x in ("CA", "SD, KY") else "East")

    client = df_dict["client"]
    address = df_dict["address"]
    mrgd = (
        client.merge(address[["ID", "Street_Address", "State"]], left_on = "Address_ID", right_on = "ID", how="inner")
    )

    df = pd.DataFrame()
    for col in client_table_columns:
        if (
            col in mrgd.columns 
            and col not in ("NAICS_CD", "NAICS_CD_DESC", "Client_Type")
        ):
            df[col] = mrgd[col]
        elif col == "Region":
                df[col] = mrgd["State"].apply(assign_region)
        elif col == "Client_Type":
                df[col] = "Person"
        else:
            df[col] = pd.NA
    
    # all clients have deposit type accounts
    df["Product_Mix"] = "D"

    df['Client_ID'] = df['Client_ID'].apply(lambda x: f'p{x}')

    return df

def personas_account_table(df_dict):
    
    account_table_columns = [k for k in data_dict["accounts"]["column_mapping"].keys()]
    
    account = df_dict["account"]
    balance = df_dict["balance"]
    account_fact = df_dict["relationship"]

    min_indices = balance.groupby(["Name", "Account_ID"])["date"].idxmin()
    init_balance = balance.loc[min_indices].rename(columns={"Balance":"Init_Balance"})

    mrgd = (
         account.merge(account_fact[["Account_ID", "Client_ID"]], left_on="ID", right_on="Account_ID")
         .merge(init_balance[["Account_ID", "Init_Balance"]], left_on="Account_ID", right_on="Account_ID", how="left")
    )

    df = pd.DataFrame()
    for col in account_table_columns:
        if col in mrgd.columns:
            df[col] = mrgd[col]
        else:
            df[col] = pd.NA

    df['Client_ID'] = df['Client_ID'].apply(lambda x: f'p{x}')
    return df

def personas_recommendations_table(df_dict):
    recommendations_table_columns = [k for k in data_dict["recommendations"]["column_mapping"].keys()]
    mrgd = df_dict["recommendations"]
    df = pd.DataFrame()
    for col in recommendations_table_columns:
        if col in mrgd.columns:
            df[col] = mrgd[col]
        else:
            df[col] = pd.NA
    df['Client_ID'] = df['Client_ID'].apply(lambda x: f'p{x}')
    return df

def get_personas_data(table_name):
    df_dict = data()
    if table_name == "clients":
        return personas_client_table(df_dict)
    if table_name == "accounts":
        return personas_account_table(df_dict)
    if table_name == "recommendations":
        return personas_recommendations_table(df_dict)
    raise Exception(f"{table_name} does not exsist for personas")

if __name__ == "__main__":
    dfc = get_personas_data("clients")
    dfa = get_personas_data("accounts")
    dfr = get_personas_data("recommendations")