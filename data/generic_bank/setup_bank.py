#!/usr/bin/env python

"""
Generate data for a generic bank:

 - regions
 - branch/branch manager
 - bankers
 - clients
 - accounts
 - transaction counterparties
 - transactions
 - recommendations
"""

import numpy as np
import pandas as pd
import itertools
import datetime
import faker
from schema_mapper import (generate_schema, mapper)

import config
from schema_config import data_dict

try:
    from dbio import connectors
except ImportError: print("No module named 'dbio', so can't use write_db()")

fake = faker.Faker()
db = './generic_bank.db'
cobj = connectors.SQLite(database=db)

def regions(n):
    '''Return n distinct regions and regional managers'''
    x = np.arange(1, n+1, 1)
    df = pd.DataFrame(np.array([x,x]).T, columns=['Region_Number', 'Regional_Manager'])
    reg_nm = config.l_regions_sel
    df = df.assign(Region_Name = reg_nm)
    return df


def branches(n):
   '''Return n distinct branches and branch managers'''
   x = np.arange(1, n+1, 1)
   return pd.DataFrame(np.array([x, x]).T, columns=['Branch_Number', 'Branch_Manager'])


def regions_and_branches(n_regions, n_branches):
    '''Name n_regions regions each with n_branches branches
    Todo: allow different regions to have different number of branches
    '''
    regions_ = regions(n_regions)
    df = branches(n_branches)
    df = regions_.merge(df, how='cross')

    df.Branch_Number = range(1, df.shape[0]+1, 1)
    df.Branch_Manager = range(1, df.shape[0]+1, 1)

    return df

    
def assign_personnel_to_branches(df):
    '''
    Calculates bankers per each branch. Returns to dataframes:
    1. branch-level table with headcount and number of bankers per category
    2. banker-level table with unique banker id per each banker
    '''
    headcount_per_branch = np.random.normal(config.HEADCOUNT_AVG,
        config.HEADCOUNT_STD, size=df.shape[0]).astype(int)

    df = df.assign(Headcount = headcount_per_branch)
    # TODO make `astype(int)`
    df = df.assign(N_deposit_ofcr = lambda x: config.f_deposit_ofcr * x.Headcount)
    df = df.assign(N_loan_ofcr = lambda x: config.f_loan_ofcr * x.Headcount)
    df = df.assign(N_wealth_ofcr = lambda x: config.f_wealth_ofcr * x.Headcount)

    df = df.round(0)

    # make dataframe of bankers at each branch
    banker_df = pd.DataFrame()
    for idx, row in df.iterrows():
        n_dep = int(row.N_deposit_ofcr)
        n_rm = int(row.N_loan_ofcr)
        n_wa = int(row.N_wealth_ofcr)
        br = row.Branch_Number
        rgn = row.Region_Name
        n = int(row.Headcount)

        data_dict = {'Branch_Number': n*[br],
                     'Region': n*[rgn],
                     'Banker_Type': n_dep*['Deposits'] + n_rm*['Loans'] + n_wa*['Wealth'],
                     'Banker_ID': range(1,n+1,1),
                     'Banker_Name': [fake.first_name() + ' ' + fake.last_name() for _ in range(n)],
                     }

        row_df = pd.DataFrame(data_dict)

        banker_df = pd.concat([banker_df, row_df])

    # unique banker id
    banker_df.Banker_ID = range(1,banker_df.shape[0]+1,1)
    # login
    banker_df['Login'] = banker_df['Banker_Name'].str.split(" ", n=1).str[0].str[0].str.lower() + \
                              banker_df['Banker_Name'].str.split(" ", n=1).str[1].str.lower().replace(" ", "")

    return df, banker_df


def clients(n):
    '''
    Allocate clients of several types (person, finance, non-finance business, nonprofit)
    according to probabilities set in config.

    Return several datapoints:
        - Client_ID
        - Client_Type
        - Product_Mix
        - Name
        - SSN (for people) / EIN (for orgs)
        - Employer (generated randomly)
        - NAICS code (level 2, assigned randomly to companies)
        - Title (assigned randomly vs empoyer and wealth tier)
        - Street_Address (generate state/city later to be consistent with region)
        - Birthday (for people)
        - Start date / End date
        - Wealth status
    '''

    n = int(n)
    # random_values = np.random.randint(1,100+1, size=n)/100  # decimal probs
    client_type = np.random.choice(
        ['Person', 'Business - Finance', 'Business - Other', 'School/Non-Profit'],
        p=[config.p_person, config.p_fin_business, config.p_nonfin_business, config.p_nonprofit],
        size=n
        )
    product_mix = np.random.choice(config.product_mix, size=n)  # decimal probs
    wealth_tier = np.random.choice(list(config.p_wealth_tiers.keys()), p=list(config.p_wealth_tiers.values()), size=n)  # currently no indiv/org split

    # client_name/address
    name, first_name, last_name, ssn, employer, client_naics, client_title, address, client_region, birthday, \
        client_start_date = n*[''], n*[''], n*[''], n*[''], n*[''], n*[''], n*[''], n*[''], n*[''], n*[''], n*['']
    for i in range(n):
        if client_type[i] == 'Person':
            # TODO use first_name / last_name generators for names to avoid odd entries
            name[i] = fake.name()
            first_name[i] = name[i].split(" ", 1)[0]
            last_name[i] = name[i].split(" ", 1)[1]
            client_naics[i] = pd.NA
            ssn[i] = fake.ssn()
            # employer random generated for each client 
            # TODO create a list of employers and draw from that list 
            employer[i] = fake.company()
            # currently no check for consistency between wealth tier and generated title
            # TODO create list of tiltes (esp. for high tier) and draw from those
            client_title[i] = fake.job()
            bday = fake.date_between(datetime.datetime(1945,1,1), pd.to_datetime('today').date())
            birthday[i] = bday.strftime('%Y-%m-%d')
        elif client_type[i].find('Business') != -1:
            name[i] = fake.company()
            first_name[i] = np.nan
            last_name[i] = np.nan
            if client_type[i] == 'Business - Finance':
                client_naics[i] = 52  ## 'Finance and Insurance'
            elif client_type[i] == 'Business - Other':
                while client_naics[i] == '' or client_naics[i] == 52:
                    client_naics[i] = np.random.choice(config.naics2_cd, p=config.naics2_p)
            ssn[i] = fake.ein()
            employer[i] = np.nan
            client_title[i] = np.nan
            birthday[i] = np.nan
        else:
            name[i] = fake.last_name() + ' School'
            first_name[i] = np.nan
            last_name[i] = np.nan
            client_naics[i] = 61  ## 'Educational Services'
            ssn[i] = fake.ein()
            employer[i] = np.nan
            client_title[i] = np.nan
            birthday[i] = np.nan
        
        address[i] = fake.street_address()  # just street address, apply region later
        client_region[i] = np.random.choice(config.l_regions_sel)
        client_start_date[i] = fake.date_between(datetime.datetime(2005,1,1), pd.to_datetime('today').date())

    # initialize derived / empty fields
    client_cat, client_end_date, is_current = n*[None], n*[pd.NaT], n*[pd.NA]
    # create dataframe
    df = pd.DataFrame(np.array([range(1,n+1, 1), client_cat, client_type, product_mix, name, first_name, last_name, 
                                client_naics, ssn, employer, client_title, address, client_region, birthday, 
                                client_start_date, client_end_date, is_current, wealth_tier]).T, 
                      columns=['Client_ID', 'Client_Category', 'Client_Type', 'Product_Mix', 'Name', 'First_Name', 'Last_Name', 
                               'NAICS_CD', 'SSN', 'Employer', 'Title', 'Street_Address', 'Region', 'Birthday', 
                               'Start_Date', 'End_Date', 'Is_Current', 'Wealth_Tier'])
    df['Client_Category'] = df['Client_Type'].map({'Person': 'Person'}).fillna('Organization')
    df['Is_Current'] = np.where(pd.isna(df['End_Date']), 1, 0).astype(int)

    df = df.astype({
        'Client_ID': int,
        'NAICS_CD': 'Int64',  # Allows for integers with NaNs
    })

    #df['Start_Date'] = pd.to_datetime(df['Start_Date'], errors='coerce')
    #df['End_Date'] = pd.to_datetime(df['End_Date'], errors='coerce') 
    #df['Birthday'] = pd.to_datetime(df['Birthday'], errors='coerce')
    #df['Birthday'] = df['Birthday'].dt.strftime('%Y-%m-%d').replace('NaT', None)
    return df


def households(df):
    '''
    Allocate households given client dataframe `df`. Schools/nonprofits are always in their own household. The remaining clients are grouped together according to the hh_size_distribution in the config (e.g., 60% of households are singletons).
    '''

    # non-profits are automatically separate households
    households = df.query('Client_Type == "School/Non-Profit"')
    households = households.assign(Household_ID = range(1,households.shape[0]+1,1))

    # give people and businesses a change to be grouped
    person_df = df.query('Client_Type == "Person"')
    business_df = df.query('Client_Type in ["Business - Finance", "Business - Other"]')

    hh_sizes = np.random.choice(config.hh_size_distribution, size=df.shape[0])

    def _allocate_hh(client_df, sizes, households):
        '''
        Helper function to allocate client subsets into households.
        '''
        index = 0  # iterate 
        for rv in sizes:  # rv = household size
            if index > client_df.shape[0]:  # end of client list
                break

            if len(households) == 0:
                next_id = 1  # case when p_nonprofit = 0
            else:
                next_id = households.Household_ID.max() + 1  # next Household_ID
            
            next_hh = client_df.iloc[index:index+rv]
            next_hh = next_hh.assign(Household_ID = next_id)  # apply Household_ID

            households = pd.concat([households, next_hh])
            index += rv  # increment index by household size

        return households

    # Person clients
    households = _allocate_hh(person_df, hh_sizes, households)

    # Business clients
    households = _allocate_hh(business_df, hh_sizes[::-1], households)
    
    return households

  
def links(clients_df, households_df):
    '''
    Generate links between household members:
      - 'Person' households with >1 member get Spouse and/or Parent-Child links. The first pair of clients are the spouses: only one Spouse link is made per household. The remaining members are linked as parent-child. These links are designated without reference to client age or gender fields.
      - 'Business' households with >1 member get 'Same Business' links.
      - 'Person' and 'Business' households can be connected with 'Business Owner' links.
    '''
    hh_size = households_df.groupby('Household_ID').size()  # hh_size
    hh_members = households_df.groupby('Household_ID')['Client_ID'].unique()  # hh members
    client_types = households_df.groupby('Household_ID')['Client_Type'].apply(lambda x: ', '.join(np.unique(x)))  # client types

    links_df = pd.DataFrame()

    # person_hh
    for hh in households_df.Household_ID.unique():
        if hh_size[hh] == 1: continue
        link_id_pairs = np.array( list(itertools.combinations(hh_members[hh], 2)), dtype='int' )

        # link_type: first link is spouse, other links are Parent-Child
        if client_types[hh] == "Person":
            link_type = ['Spouse'] + (link_id_pairs.shape[0]-1)*['Parent-Child']
        else:
            link_type = link_id_pairs.shape[0]*['Same Business']

        # dataframe
        dict_ = {'Link_ID': range(0, link_id_pairs.shape[0]),
            'Household_ID': link_id_pairs.shape[0]*[hh],
            'Client_1': link_id_pairs[:,0], 'Client_2': link_id_pairs[:,1],
            'Link_Type': link_type
            }
        df_ = pd.DataFrame(dict_)
        links_df = pd.concat([links_df, df_], ignore_index=True)

    # add 'Business Owner' links
    hh_sizes_and_types = pd.concat([hh_size, client_types], axis=1)
    hh_sizes_and_types.columns = ['HH_size', 'Client_Type']

    # Link subset of Person and Business - Other households
    n_business_owner_links = int(config.f_business_owner_link * clients_df.shape[0])  # 5% of customers
    person_id = hh_sizes_and_types.query('HH_size == 1 & Client_Type == "Person"').index[:n_business_owner_links]
    bus_id = hh_sizes_and_types.query('HH_size == 1 & Client_Type == "Business - Other"').index[:n_business_owner_links]

    for person_, bus_ in zip(person_id, bus_id):
        dict_ = {'Link_ID': [1],
            'Household_ID': [-1],
            'Client_1': [person_], 'Client_2': [bus_],
            'Link_Type': ['Business Owner'] 
            }
        df_ = pd.DataFrame(dict_)
        links_df = pd.concat([links_df, df_], ignore_index=True)
        

    # set Link_ID
    links_df.Link_ID = range(0, links_df.shape[0], 1)

    return links_df


def account_types():
    '''
    Table of account categories (DLW) and account types. Frequencies for individuals and organizations are defined in config.py.
    '''
    # TODO create this table from config dict instead
    data_dict = {'Account_Category': 3*['Deposits'] + 5*['Loans'] + 2*['Wealth'],
                 'Account_Type': ['CHK', 'SV', 'CD'] + ['SFR', 'PLOC', 'PLN', 'CRE', 'COMM'] + ['PM', 'BKG'],
                 'Account_Description': ['Checking', 'Savings', 'Certificate of Deposit'] +
                                        ['Consumer Mortgage', 'Consumer Line of Credit', 'Consumer Loan',
                                         'Commercial Mortgage', 'Commercial Loan'] +
                                        ['Portfolio Management', 'Brokerage']
                }

    acct_types_df = pd.DataFrame(data_dict)
    return acct_types_df


def assign_accounts_to_clients_and_bankers(clients_df, bankers_df, debug = False):
    '''
    Use clients(n) as input.
    Assigns accounts to clients based on their product mix. Returns account-level table with unique account id. Use account frequencies defined in config.py, separate for Individual / Organizations. 
    '''
    # assign inputs
    df = clients_df
    
    # prep frequencies for assigning bankers to accounts (given original branch headcounts)
    l_bankers = dict()
    for i in bankers_df.Banker_Type.unique(): 
        l_bankers[i] = bankers_df.query(f'Banker_Type == "{i}"')['Banker_ID']
    n_bankers = bankers_df[['Banker_Type', 'Banker_ID']].groupby(['Banker_Type']).count().to_dict()['Banker_ID']
    f_bankers = dict()
    for i in n_bankers: 
        f_bankers[i] = n_bankers[i]*[1 / n_bankers[i]]

    # prep accounts data frame
    accounts_df = pd.DataFrame()
    for idx, row in df.iterrows():
        # for debugging
        # if idx != 1227: continue  
        # print(row)

        # identify number of DLW accounts per client
        # TODO assumes 1 acct per category - can randomly select multiple accounts here
        # can sample from distr with mean 2 std 1, threshold of min 1 if acct cat is present
        n_D=0; n_L=0; n_W=0
        if 'D' in row.Product_Mix: n_D+=1
        if 'L' in row.Product_Mix: n_L+=1
        if 'W' in row.Product_Mix: n_W+=1
        cl = row.Client_ID
        clt = row.Client_Type
        clw = row.Wealth_Tier
        n = int(sum([n_D, n_L, n_W]))

        # prep df with one line per account
        data_dict = {'Client_ID': n*[cl],
                     'Client_Type': n*[clt],
                     'Wealth_Tier': n*[clw],
                     'Account_Nr': np.array(range(1,n+1,1), dtype=str),
                     # TODO pull DLW labels from config
                     'Account_Category': n_D*['Deposits'] + n_L*['Loans'] + n_W*['Wealth']
                     }
        row_df = pd.DataFrame(data_dict)

        # select acct type based on mix and frequency defined in config (separate for individuals / orgs)
        # assign opening acct balance based on avg/sd defined in config (separate for individuals / orgs)
        # assign bankers to accounts (equal probabilies per account category, no individual / org split)
        # assign acct open date
        acct_val = []; bal_val = []; banker_val = []; opendt_val = []; client_primary_banker_val = []
        for idx_, row_ in row_df.iterrows():
            # if row_['Wealth_Tier'] != 'mid': 
            #     row_['Wealth_Tier'] = 'mid'
            #     continue  # for debugging
                
            # acct type
            acct_val_sel = np.random.choice(
                list(config.f_accts[row_['Client_Type']][row_['Account_Category']][row_['Wealth_Tier']].keys()), 
                size=1, p=list(config.f_accts[row_['Client_Type']][row_['Account_Category']][row_['Wealth_Tier']].values()))
            # if client has L, then force D to be CHK (this effectively modifies relative freqs defined in the config)
            # assumes config mix L always has corresponding D
            if row_['Account_Category'] == 'Deposits' and n_L == 1 and acct_val_sel[0] != 'CHK': 
                acct_val_sel[0] = 'CHK'
            
            # acct balance
            bal_val_sel = round(np.random.normal(loc=config.bal_accts[row_['Client_Type']][row_['Account_Category']][row_['Wealth_Tier']][acct_val_sel[0]][0],
                                           scale=config.bal_accts[row_['Client_Type']][row_['Account_Category']][row_['Wealth_Tier']][acct_val_sel[0]][1], 
                                           size=1)[0], 1)
            
            # guardrails for negative acct balances and min acct balances by pdt type (i.e. left truncate observed distributions)
            # TODO move params to config
            if row_['Account_Category'] == 'Deposits':
                if acct_val_sel == ['CHK']:
                    if bal_val_sel < -200: bal_val_sel = round(np.random.uniform(-200, 0), 1)
                    elif bal_val_sel >= -200 and bal_val_sel < 0: bal_val_sel = 0
                if acct_val_sel == ['SV']:
                    if bal_val_sel < 0: bal_val_sel = 0
                if acct_val_sel == ['CD']:
                    if bal_val_sel < 0: bal_val_sel = 10e3
            elif row_['Account_Category'] == 'Loans':
                if acct_val_sel == ['SFR']:
                    if bal_val_sel < 250e3: bal_val_sel = round(np.random.uniform(250e3, 300e3), 1)
                if acct_val_sel == ['PLOC']:
                    if bal_val_sel < 0: bal_val_sel = 0
                if acct_val_sel == ['PLN']:
                    if bal_val_sel < 10e3: bal_val_sel = round(np.random.uniform(10e3, 30e3), 1)
                if acct_val_sel == ['CRE']:
                    if bal_val_sel < 500e3: bal_val_sel = round(np.random.uniform(500e3, 600e3), 1)
                if acct_val_sel == ['COMM']:
                    if bal_val_sel < 250e3: bal_val_sel = round(np.random.uniform(250e3, 300e3), 1)
            elif row_['Account_Category'] == 'Wealth':
                if acct_val_sel == ['PM']:
                    if bal_val_sel < 50e3: bal_val_sel = round(np.random.uniform(50e3, 75e3), 1)
                if acct_val_sel == ['BKG']:
                    if bal_val_sel < 50e3: bal_val_sel = round(np.random.uniform(50e3, 75e3), 1)
                        
            # guardrails for min bal for mid/high tiers (left truncate observed distributions, to avoid large overlaps with prev tiers)
            # if bal < avg + 2sd of prev tier, then set to uniform between avg + 2sd and avg + 4sd of prev tier
            prev_tiers = {'mid': 'low', 
                          'high': 'mid'}
            if row_['Wealth_Tier'] in ['mid', 'high']:
                prev_tier_bal_2sd_4sd = []
                for i in [2,4]:
                    # get prev tier avg +2sd and +4sd (if current is 'mid', get avg of 'low' tier; if current is 'high', get avg of 'mid' tier)
                    x = (config.bal_accts[row_['Client_Type']][row_['Account_Category']][prev_tiers[row_['Wealth_Tier']]][acct_val_sel[0]][0] + 
                         i * config.bal_accts[row_['Client_Type']][row_['Account_Category']][prev_tiers[row_['Wealth_Tier']]][acct_val_sel[0]][1])
                    prev_tier_bal_2sd_4sd.append(x)
                if bal_val_sel < prev_tier_bal_2sd_4sd[0]:
                    bal_val_sel = round(np.random.uniform(prev_tier_bal_2sd_4sd[0], prev_tier_bal_2sd_4sd[1]), 1)
            
            # no individual / org split for banker assignment
            # TODO for given client, choose bankers only from one region
            banker_val_sel = np.random.choice(
                list(l_bankers[row_['Account_Category']]),
                size=1, p=f_bankers[row_['Account_Category']])
            # assign primary banker to client relationship (by def: D banker is primary, if no DL then W banker)
            if idx_ == 0 and row_['Account_Category'] == 'Deposits': 
                client_primary_banker_val_sel = True
            elif idx_ == 0 and row_['Account_Category'] == 'Wealth':
                client_primary_banker_val_sel = True
            elif idx_ == 0:
                client_primary_banker_val_sel = True
            else: 
                client_primary_banker_val_sel = False
            # acct open date (assumes D is first in list)
            if idx_ == 0 and row_['Account_Category'] == 'Deposits': 
                ## if client has D, then client opened D acct on join date
                opendt_val_sel = row['Start_Date']
            elif idx_ == 0 and row_['Account_Category'] != 'Deposits':
                ## if client has no D (hence no L), then assume client opened W acct on join date
                ## assumes Deposit acct is 1st in df (for non-CHK accounts, would need to rewrite logic if we can have LW first and D second in the df)
                opendt_val_sel = row['Start_Date']
            else: 
                ## for idx >= 1, choose random date within 2 years from join date (or up to today, whichever comes first)
                # manually handle 2/29 nonsense
                if row['Start_Date'].strftime("%m-%d") == '02-29': 
                    repl_day = row['Start_Date'].day - 1
                else: 
                    repl_day = row['Start_Date'].day
                opendt_val_sel = fake.date_between(row['Start_Date'], 
                                                   min(row['Start_Date'].replace(year=row['Start_Date'].year + 2, day=repl_day), 
                                                       pd.to_datetime('today').date()))
            # collect selections
            acct_val.append(acct_val_sel[0])
            bal_val.append(bal_val_sel)
            banker_val.append(banker_val_sel[0])
            client_primary_banker_val.append(client_primary_banker_val_sel)
            opendt_val.append(opendt_val_sel)
        
        # Init_Balance: Initial Balance e.g. as of 10/1/2023
        row_df = row_df.assign(Account_Type = acct_val, Init_Balance = bal_val, Banker_ID = banker_val, Primary_Banker = client_primary_banker_val,
                               Open_Date = opendt_val)
        accounts_df = pd.concat([accounts_df, row_df])

    # unique account id per acct category (i.e. D#, L#, W#)
    n_acct_cat = accounts_df.groupby('Account_Category').size()
    acct_prefix = ['6','7','8']
    for i, idx_cat in enumerate(accounts_df['Account_Category'].unique()):
        accounts_df.loc[accounts_df.Account_Category == idx_cat, 'Account_Nr'] = [idx_cat[0] + "00" + acct_prefix[i] + f"{k}".zfill(7) for k in range(1, n_acct_cat[idx_cat]+1, 1)]
    
    # close date / is current / status
    accounts_df = accounts_df.assign(Close_Date = pd.NaT)
    accounts_df['Is_Current'] = np.where(pd.isna(accounts_df['Close_Date']), 1, 0).astype(int)
    accounts_df['Status'] = np.where(pd.isna(accounts_df['Close_Date']), 'Active', 'Closed').astype(str)

    accounts_df = accounts_df.reset_index(drop=True)
    
    # assign a primary key 
    len_accounts = accounts_df.shape[0]
    accounts_df.insert(0, "ID", np.arange(1, len_accounts+1, 1))
    
    # normalizing the accounts table: drop columns specific to other tables
    if debug == False:
        accounts_df = accounts_df.drop(columns=["Wealth_Tier", "Client_Type"])
    print("done")

    return(accounts_df.reset_index(drop=True))


def transactions(accounts_df, adults, households_df):
    '''
    Generate transactions from helper functions:
        - transactions_1: loan payments
        - transactions_2: transactions and direct deposits for People
        - transaction_3: transactions between households
    '''

    df_1 = transactions_1(accounts_df)
    df_2 = transactions_2(accounts_df, adults)
    df_3 = transactions_3(accounts_df, households_df)

    transactions = pd.concat([df_1, df_2.astype(df_1.dtypes)])  # standardize datetime units
    transactions = pd.concat([transactions, df_3.astype(df_1.dtypes)], ignore_index=True)  # standardize datetime units

    return transactions.reset_index(names='Transaction_ID')


def transactions_1(accounts_df):
    '''
    Transactions on non-LOC loans: Generate original loan balances and assume
    payments are a fixed percent of the original balance. Make corresponding
    transaction for the checking account (if any). Otherwise say payment from
    internal account.
    '''

    first_month, last_month = config.tran_min_date.month, config.tran_max_date.month
    date_range = [datetime.datetime(2023, m, config.payment_day) for m in range(first_month, last_month+1, 1)]

    ### part 1: loan payments for non-LOC loans
    loans_df = accounts_df.query('Account_Category=="Loans" & Account_Type.str.contains("LOC")==False')

    # checking accounts for loan clients
    chk_df = (accounts_df
              .query('Account_Type=="CHK"')
              .filter(items=['Client_ID', 'Account_Nr'])
              .rename({'Account_Nr': 'Autodebit_Acct'}, axis=1)
              )

    # clients with checking
    clients_with_chk = accounts_df.query('Account_Type=="CHK"').Client_ID.unique()

    # add in autodebit deposit account
    loans_df = loans_df.merge(chk_df, how='left', on='Client_ID')

    # 'Open_balance' is the balance on 9/30/2023. Assume current balance is 20-80% of the original balance. Infer the original balance.
    loans_df = loans_df.assign(Payoff_Pct=np.random.randint(20,80, size=loans_df.shape[0]))
    loans_df = loans_df.assign(Original_Bal=lambda x: (100*x.Init_Balance/x.Payoff_Pct).astype(int))

    # iterate loans and generate transactions
    transactions_df = pd.DataFrame()
    for idx, row in loans_df.iterrows():
        for d in date_range:

            From_Account_Nr = row.Autodebit_Acct if not pd.isnull(row.Autodebit_Acct) else 'NULL'
            To_Account_Nr = row.Account_Nr
            Amount = 0.0028*row.Original_Bal  # payment is 0.28%, or 1/(30*12)

            tran_dict = {'Date': [d],
                         'Description': [f'Loan payment from {From_Account_Nr}'],
                         'From_Account_Nr': [From_Account_Nr],
                         'To_Account_Nr': [To_Account_Nr],
                         'Amount': [-Amount]
                         }

            # add transaction for checking account if internal account
            if not pd.isnull(row.Autodebit_Acct):
                tran_dict['Date'] += [d]
                tran_dict['Description'] += ['Loan Payment from external account']
                tran_dict['From_Account_Nr'] += [To_Account_Nr]
                tran_dict['To_Account_Nr'] += [From_Account_Nr]
                tran_dict['Amount'] += [-Amount]

            tran_df = pd.DataFrame(tran_dict)
            transactions_df = pd.concat([transactions_df, tran_df], ignore_index=True)

    return transactions_df


def adult_people(clients_df, links_df, households_df):
    '''
    Return Client_ID of adults (married and single) as an array.
    '''

    # infer adult people
    married_adults = (links_df
                      .query('Link_Type=="Spouse"')
                      .filter(items=['Client_1', 'Client_2'])
                      .values.flatten()
                      )

    # single adults
    hh_size = households_df.Household_ID.value_counts().to_frame('HH_Size')
    households_df = households_df.merge(hh_size, left_on='Household_ID', right_index=True)
    singletons = households_df.query('HH_Size==1').Client_ID.values
    single_adults = (clients_df

                     ##### this part wrong, need to apply client_iD in the singleon
                     .query('Client_Type=="Person" & Client_ID in @singletons')
                     .Client_ID.values
                     )

    return np.append(married_adults, single_adults)


def transactions_2(accounts_df, adults):
    '''
    Transactions for adult People, including outgoing POS/POP transations and incoming
    direct deposits from employers.
    '''

    # checking accounts - where the transactions happen
    chk_df = accounts_df.query('Account_Type=="CHK" & Client_ID in @adults').set_index('Client_ID')

    # data storage
    transactions_df = pd.DataFrame()

    # generate transactions per day
    for d in pd.date_range(config.tran_min_date, config.tran_max_date, freq='D', unit='us'):
        # random sample clients who have transactions
        transactors = np.random.choice(adults, int(0.1*adults.shape[0]), replace=False)

        # Build transactions in vectorized way per each day
        tran_df = chk_df.query('Client_ID in @transactors')

        # generate one outbound payment per selected client
        tran_df = tran_df.assign(
            Date=d,
            root=np.random.choice(config.transactor_root, size=tran_df.shape[0]), 
            suffix = np.random.choice(config.transactor_suffix, size=tran_df.shape[0]),
            Description=lambda x: 'POS ' + x.root + ' ' + x.suffix,
            From_Account_Nr=lambda x: x.Account_Nr,
            To_Account_Nr='NULL',
            Amount=lambda x: -0.01*x.Init_Balance,
            )

        # record daily transactions
        transactions_df = pd.concat([transactions_df,
            tran_df.filter(items=['Date', 'Description', 'From_Account_Nr', 'To_Account_Nr', 'Amount'])], ignore_index=True)

    # inbound direct deposits from unnamed employer on payment_day of each month
    tran_df = chk_df.copy()
    first_month, last_month = config.tran_min_date.month, config.tran_max_date.month
    date_range = [datetime.datetime(2023, m, config.payment_day) for m in range(first_month, last_month+1, 1)]
    # working adults
    payees = np.random.choice(adults, int(0.9*adults.shape[0]), replace=False)
    for d in date_range:
        tran_df = chk_df.query('Client_ID in @payees')

        # generate one outbound payment per selected client
        tran_df = tran_df.assign(
            Date=d,
            Description='Direct Deposit From Employer',
            From_Account_Nr='NULL',
            To_Account_Nr=lambda x: x.Account_Nr,
            Amount=lambda x: 0.25*x.Init_Balance,
            )

        # record daily transactions
        transactions_df = pd.concat([transactions_df,
            tran_df.filter(items=['Date', 'Description', 'From_Account_Nr', 'To_Account_Nr', 'Amount'])], ignore_index=True)


    return transactions_df


def _add_transaction(tran_dict, d, description, from_nr, to_nr, amount):
    '''
    Utility function to add transaction to dictionary
    '''

    tran_dict['Date'] += [d]
    tran_dict['Description'] += [description]
    tran_dict['From_Account_Nr'] += [from_nr]
    tran_dict['To_Account_Nr'] += [to_nr]
    tran_dict['Amount'] += [amount]

    return tran_dict


def transactions_3(accounts_df, households_df):
    '''
    Set up internal transfers between households.
    '''

    # clients with deposits in big household
    clients_per_hh = (households_df
                      .query('Product_Mix.str.contains("D")==True')
                      .groupby('Household_ID')
                      .agg({'Client_Type': 'count', 'Client_ID': list})
                      .rename(columns={'Client_Type': 'HH_Size', 'Client_ID': 'HH_Members'})
                      )
    big_hh_df = (households_df
                 .merge(clients_per_hh, left_on='Household_ID', right_index=True)
                 .query('HH_Size>1')
                 .set_index('Household_ID')
                 )

    # deposit accounts for those households
    dep_df = accounts_df.query('Account_Type!="CD" & Account_Category=="Deposits" & Client_ID in @big_hh_df.Client_ID').set_index('Client_ID')

    transaction_dict = {'Date': [], 'Description': [], 'From_Account_Nr': [],
        'To_Account_Nr': [], 'Amount': []}

    for d in pd.date_range(config.tran_min_date, config.tran_max_date, freq='D', unit='us'):
        #print(d)
        # random sample clients who have transactions
        transactors = np.random.choice(big_hh_df.index, int(0.05*big_hh_df.shape[0]), replace=False)

        for hh in transactors:
            client_1, client_2 = big_hh_df.loc[hh].head(1).HH_Members.values[0][:2]
            try:  # pass if KeyError, e.g., for CD accounts
                amount = np.random.uniform(0.25, 0.5) * dep_df.loc[client_1].Init_Balance

                # outgoing
                transaction_dict = _add_transaction(transaction_dict, d, 'Internal Transfer',
                    dep_df.loc[client_1].Account_Nr, dep_df.loc[client_2].Account_Nr, -amount)

                # incoming
                transaction_dict = _add_transaction(transaction_dict, d, 'Internal Transfer',
                    dep_df.loc[client_2].Account_Nr, dep_df.loc[client_1].Account_Nr, amount)

            except KeyError:
                pass

    return pd.DataFrame(transaction_dict)


def balance_timeseries(accounts_df, transactions_df, init_date=datetime.datetime(2023,9,30)):
    '''
    Build timeseries of account balances given accounts, transactions, and the
    date of the initial balance.
    '''

    # initialize timeseries for init_date
    ts_df = (accounts_df
             .filter(items=['Account_Nr', 'Init_Balance'])
             .rename(columns={'Init_Balance':'Balance'})
             .assign(Date=init_date)
             .filter(items=['Date', 'Account_Nr', 'Balance'])
             .astype({'Date':'datetime64[ns]'})
             )

    # prepare transactions for merge
    tran_df = (transactions_df
               .rename(columns={'From_Account_Nr':'Account_Nr'})  # rename
               .groupby(['Date', 'Account_Nr'], as_index=False)  # group by date, account
               .agg({'Amount': 'sum'})  # sum tran amounts
               .rename(columns={'Amount':'Balance'})
               )

    # combine with initial time series and sort by Account_Nr, Date
    ts_df = (pd
             .concat([ts_df, tran_df], ignore_index=True)
             .sort_values(by=['Account_Nr', 'Date'])
             ) 

    # cumulative sum balance over date
    ts = ts_df.groupby(['Account_Nr']).agg({'Balance':'cumsum'})

    # add balance and balance change
    ts_df = ts_df.assign(Net_Change=lambda x: x.Balance)
    ts_df = ts_df.assign(Balance=ts.Balance)

    # index
    ts_df = ts_df.set_index(['Account_Nr', 'Date'])

    # re-index (https://stackoverflow.com/questions/27421256/re-index-dataframe-by-new-range-of-dates)
    account_index = ts_df.index.get_level_values(0).unique()
    date_index = ts_df.index.get_level_values(1).unique()
    multi_index = pd.MultiIndex.from_product([account_index, date_index])

    ts_df = (ts_df
            .reindex(multi_index)
            .sort_index()
            .assign(Balance=lambda x: x.Balance.ffill())  # forward fill NaNs
            .assign(Net_Change=lambda x: x.Net_Change.fillna(0))  # forward fill NaNs
            )

    return ts_df.reset_index()


def write_db(df_dict, db='generic_bank.db'):
    '''
    Write SQLite database from dictionary of dataframes:
        - key = tablename
        - value = dataframe
    '''

    cobj = connectors.SQLite(db)  # database connection
    # write each dataframe to separate table

    for table_, df_ in df_dict.items():
        cobj.write(df_, table_, if_exists='replace', index=False)

    return 'Done'



if __name__ == '__main__':
    import setup_bank as m
    import config
    from importlib import reload

    # set random seed
    np.random.seed(42)
    m.fake.seed_instance(42)

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

    # write database
    df_dict = {'accounts': accounts_df,
               'clients': clients_df,
               'bankers': bankers_df,
               'links': links_df,
               #'transactions': transactions_df,
               #'account_fact': ts_df,
               #'branches': branches_df,
               #'households': households_df,
            }
    
    for table_name, df in df_dict.items():
        df_dict[table_name] = mapper(df, table_name, schema_config=data_dict)

    result = m.write_db(df_dict)

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
