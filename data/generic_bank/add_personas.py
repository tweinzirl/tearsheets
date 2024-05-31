import pandas as pd
import numpy as np
import os
from schema_config import data_dict
from config import bal_accts
from datetime import date, timedelta
import random

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

def personas_transaction_table(df_dict, start_date="2023-12-01", end_date="2024-01-01"):

    def parse_date_input(date_string):
        try:
            year, month, day = map(int, date_string.split('-'))
            return date(year, month, day)
        except ValueError:
            raise ValueError(f"Invalid date format for '{date_string}'. Please use YYYY-MM-DD.")

    start_date = parse_date_input(start_date)
    end_date = parse_date_input(end_date)
    if end_date <= start_date:
        raise ValueError("End date must be after start date.")
    delta_days = (end_date - start_date).days

    tranx_table_columns = [k for k in data_dict["transactions"]["column_mapping"].keys()]
    account = df_dict["account"]
    tranx = df_dict["transactions"].rename(
        columns={
            "Balance": "curr_bal", 
            "Transaction_Amount": "tran_amt",
            "Transaction_Type": "tran_type",
            "Transaction_Purpose": "tran_purpose",
            "Transaction_Description": "tran_desc",
            }
        )
    tranx["init_bal"] = tranx["curr_bal"] - tranx["tran_amt"]

    # map dates in the orig tranx table to specified range
    date_ids = sorted(tranx["Date_ID"].unique().tolist())
    num_days = len(date_ids)

    # Generate as many unique random dates as possible within the specified range
    unique_dates_set = set()
    while len(unique_dates_set) < num_days and len(unique_dates_set) <= delta_days:
        unique_dates_set.add(start_date + timedelta(days=random.randint(0, delta_days)))

    unique_dates_list = list(unique_dates_set)
    
    # If there are not enough unique dates, generate additional random dates
    additional_dates_needed = num_days - len(unique_dates_list)
    additional_dates = [start_date + timedelta(days=random.randint(0, delta_days)) for _ in range(additional_dates_needed)]

    all_dates = unique_dates_list + additional_dates
    all_dates = sorted(all_dates)

    date_keys = [int(dt.strftime('%Y%m%d')) for dt in all_dates]
    date_assigment = dict(zip(date_ids, date_keys))

    mrgd = tranx.merge(account[["ID", "Account_Nr"]], left_on="Account_ID", right_on="ID", how="left")
    
    df = pd.DataFrame()
    for col in tranx_table_columns:
        if col in mrgd.columns:
            df[col] = mrgd[col]
        elif col == "asof":
            df[col] = mrgd["Date_ID"].replace(date_assigment)
        else:
            df[col] = pd.NA
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
    if table_name == "transactions":
        return personas_transaction_table(df_dict)
    raise Exception(f"{table_name} does not exsist for personas")

if __name__ == "__main__":
    dft = get_personas_data("transactions")
    dfc = get_personas_data("clients")
    dfa = get_personas_data("accounts")
    dfr = get_personas_data("recommendations")