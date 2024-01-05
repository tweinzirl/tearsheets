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

import config

def regions(n):
   '''Return n distinct regions and regional managers'''
   x = np.arange(1, n+1, 1)
   return pd.DataFrame(np.array([x,x]).T, columns=['Region_Number', 'Regional_Manager'])

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
    df = df.assign(N_RM = lambda x: config.f_RM * x.Headcount)
    df = df.assign(N_Wealth_Advisor = lambda x: config.f_Wealth_Advisor * x.Headcount)

    df = df.round(0)

    # make dataframe of bankers at each branch
    banker_df = pd.DataFrame()
    for idx, row in df.iterrows():
        n_rm = int(row.N_RM)
        n_wa = int(row.N_Wealth_Advisor)
        br = row.Branch_Number
        n = int(row.Headcount)

        data_dict = {'Branch_Number': n*[br],
                     'Banker_Type': n_rm*['RM'] + n_wa*['Wealth Advisor'],
                     'Banker_ID': range(1,n+1,1)
                     }

        row_df = pd.DataFrame(data_dict)

        banker_df = pd.concat([banker_df, row_df])

    # unique banker id
    banker_df.Banker_ID = range(1,banker_df.shape[0]+1,1)

    return df.astype(int), banker_df
