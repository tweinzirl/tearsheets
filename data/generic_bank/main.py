import setup_bank as m
import config
from schema_config import data_dict
from importlib import reload
from schema_mapper import (generate_schema, mapper)
import numpy as np
import pandas as pd
from add_personas import get_personas_data

from datetime import timezone, date, timedelta

# set random seed
np.random.seed(42)
m.fake.seed_instance(42)

try:
   from dbio import connectors
except ImportError: 
    print("No module named 'dbio', so can't use write_db()")

db = './generic_bank.db'
cobj = connectors.SQLite(database=db)

if __name__ == "__main__":

    # generate data

    # assign branches in two passes:
    # first pass: branches and regions
    # second pass: headcount per branch
    branches_df = m.regions_and_branches(config.n_regions, config.n_branches)
    branches_df, bankers_df = m.assign_personnel_to_branches(branches_df)

    # allocate clients
    clients_df = m.clients(config.n_clients)

    # group into households
    households_df = m.households(clients_df)

    # links
    links_df = m.links(clients_df, households_df)

    # accounts
    accounts_df = m.assign_accounts_to_clients_and_bankers(clients_df, bankers_df)

    # transactions
    adults = m.adult_people(clients_df, links_df, households_df)
    transactions_df = m.transactions(accounts_df, adults, households_df)

    # account timeseries
    ts_df = m.balance_timeseries(accounts_df, transactions_df, config.snapshot_date)

    # validate output characteristics
    # ?

    # add Household ID to clients table
    clients_df = clients_df.merge(households_df.filter(items=["Client_ID", "Household_ID"]), on="Client_ID")

    # transactions
    transactions_df = m.create_tranxs(accounts_df, clients_df, start_date="2023-12-01", end_date="2024-01-01", transaction_config="config.csv", output_file='transaction.csv')

    # recommendations
    recommendations_df = m.create_recommedations()

    # add fake persona data to the tables:
    # get latest clients IDs
    max_client_id = clients_df["Client_ID"].max()
    pc_df = get_personas_data("clients")
    new_ids = range(max_client_id+1, max_client_id+pc_df.shape[0]+1)
    persona_id_map = dict(zip(pc_df["Client_ID"].to_list(), new_ids))
    pc_df.replace(persona_id_map, inplace=True)
    clients_df = pd.concat([clients_df, pc_df], ignore_index=True)

    # add personas data: accounts table
    table_name = 'accounts'
    df = get_personas_data(table_name)
    df.replace(persona_id_map, inplace=True)
    min_id = (1 if accounts_df["ID"].empty else accounts_df["ID"].max()+1)
    df["ID"] = range(min_id,min_id+df.shape[0])
    accounts_df = pd.concat([accounts_df, df], ignore_index=True)

    # add personas data: recommendations
    table_name = 'recommendations'
    df = get_personas_data(table_name)
    df.replace(persona_id_map, inplace=True)
    min_id = (1 if recommendations_df["ID"].empty else recommendations_df["ID"].max()+1)
    df["ID"] = range(min_id,min_id+df.shape[0])
    recommendations_df = pd.concat([recommendations_df, df], ignore_index=True)
            
    # add personas data: transactions
    table_name = 'transactions'
    df = get_personas_data(table_name)
    min_id = (1 if transactions_df["ID"].empty else transactions_df["ID"].max()+1)
    df["ID"] = range(min_id,min_id+df.shape[0])
    transactions_df = pd.concat([transactions_df, df], ignore_index=True)

    # write database
    df_dict = {'accounts': accounts_df,
                'clients': clients_df,
                'bankers': bankers_df,
                'links': links_df,
                'transactions': transactions_df,
                'recommendations':recommendations_df,
                #'account_fact': ts_df,
                #'branches': branches_df,
                #'households': households_df,
            }

    for table_name, df in df_dict.items():
        df_dict[table_name] = mapper(df, table_name, schema_config=data_dict)

    result = m.write_db(cobj, df_dict)

    sql = generate_schema(cobj=cobj, schema_config=data_dict, save=True)
    print("finished")
    # clients
    # distribution of client join dates by month
    # print(clients_df['Start_Date'].groupby(pd.to_datetime(clients_df['Start_Date']).dt.strftime('%Y-%m')).agg('count').to_string())


    # todo:
    # bankers table - (x) add login user, ensure banker start / end dates consistente with account start / end dates
    # clients table - (x) add join date, (x) add 'wealth' flag (low, mid, high) tiers, (x) assign primary banker, (x) add NAICS and (x) is_Current
    #    fix birthday to be birthdate (might need to check consistency with HH)
    # accounts table - (x) add account open date (ensure CHK opened before Loan acct),
    #    (x) rename pdt_types (e.g. have pdt_code and pdt_label), add int rates,
    #    get the wealth tiers working when assign balances,
    #    assign bankers to accounts by region (i.e. client has only accounts in one region)
    # x faker data - address, first name, last name, date of birth, banker names
    # x counterparties - (only for consumer transactions)
    # x transactions - oct through december
        # - loans - infer original balance and make fixed payments, treat loc differently
        # - counterparties - outbound transactions - add mart car, etc to names or manually set names and sample
        # - counterparties - employers, fixed direct deposits
        # - transfers between households in/out when hh_size > 1
    # accounts timeseries table, show account number and balance over all dates, Oct 1 to Dec 31
    # write db and evaluate size
    # converge schema to current schema used by LLM
    # host on hugging face
    # add myportfolio queries with aggregates by region, banker, etc.
    # add recommendations with logic based on generic bank data
