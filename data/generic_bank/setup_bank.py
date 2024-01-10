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
        n = int(row.Headcount)

        data_dict = {'Branch_Number': n*[br],
                     'Banker_Type': n_dep*['deposit'] + n_rm*['loan'] + n_wa*['wealth'],
                     'Banker_ID': range(1,n+1,1)
                     }

        row_df = pd.DataFrame(data_dict)

        banker_df = pd.concat([banker_df, row_df])

    # unique banker id
    banker_df.Banker_ID = range(1,banker_df.shape[0]+1,1)

    return df.astype(int), banker_df


def clients(n):
    '''
    Allocate clients of several types (person, finance, non-finance business, nonprofit)
    according to probabilities set in config.
    '''

    n = int(n)
    client_type = n*['']
    product_mix = n*['']
    random_values = np.random.randint(1,100+1, size=n)/100  # decimal probs
    random_mixes = np.random.choice(config.product_mix, size=n)  # decimal probs

    for idx, rv in enumerate(random_values):
        if rv <= config.p_person:  # person
            client_type[idx] = 'Person'
        elif config.p_person < rv <= (config.p_person + config.p_fin_business):
            client_type[idx] = 'Business - Finance'
        elif (config.p_person + config.p_fin_business) < rv <= (config.p_person + config.p_fin_business + config.p_nonfin_business):
            client_type[idx] = 'Business - Other'
        else:
            client_type[idx] = 'School/Non-Profit'

        product_mix[idx] = random_mixes[idx]

    df = pd.DataFrame(np.array([range(1,n+1, 1), client_type, product_mix]).T, columns=['Client_ID', 'Client_Type', 'Product_Mix'])

    return df.astype({'Client_ID': int})


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


if __name__ == '__main__':
    import setup_bank as m

    n_regions, n_branches, n_clients = 1, 1, 1e3

    # assign branches in two passes:
    # first pass: branches and regions
    # second pass: headcount per branch
    branches_df = m.regions_and_branches(n_regions, n_branches)
    branches_df, bankers_df = m.assign_personnel_to_branches(branches_df)

    # allocate clients
    clients_df = m.clients(n_clients)

    # group into households
    households_df = m.households(clients_df)

    # links
    links_df = m.links(clients_df, households_df)
