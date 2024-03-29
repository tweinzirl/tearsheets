import setup_bank as m
import config
from schema_config import data_dict
from importlib import reload
from schema_mapper import (generate_schema, mapper)
import numpy as np
import pandas as pd

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
    config_df = pd.read_csv("config.csv")
    accounts_df = pd.merge(accounts_df, clients_df, how='inner', on="Client_ID")
    transactions_df = pd.merge(config_df, accounts_df,  how='inner', on="Client_Type,Account_Category,Wealth_Tier,Account_Type".split(","))

    transactions_df['curr_bal'] = transactions_df.Init_Balance
    transactions_df['init_bal'] = transactions_df.curr_bal
    transactions_df['asof']     = 0
    transactions_df['tran_amt'] = 0
    outputs = "Account_Nr asof init_bal tran_amt curr_bal".split()
    transactions_df[outputs].head(0).to_csv("transaction.csv", index=False)

    for dt in m.daterange(date(2023, 12, 1), date(2024, 1, 1)):
        print(dt)
        transactions_df['asof']     = int(str(dt).replace('-',''))
        transactions_df['init_bal'] = transactions_df.curr_bal
        transactions_df['tran_amt'] = transactions_df.apply(m.balance_func, axis=1)
        transactions_df['curr_bal'] = round(transactions_df.init_bal + transactions_df.tran_amt,2)
        transactions_df[outputs].to_csv('transaction.csv', mode='a', index=False, header=False)

    transactions_df = pd.read_csv("transaction.csv")

    # write database
    df_dict = {'accounts': accounts_df,
                'clients': clients_df,
                'bankers': bankers_df,
                'links': links_df,
                'transactions': transactions_df,
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
    # bankers table - (x) add login user
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
