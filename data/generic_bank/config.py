import datetime

# set bank size
n_regions = 2
n_branches = 2
n_clients = 1e4

# define default list of regions
l_regions = ['West', 'East', 'North', 'South']
assert n_regions <= len(l_regions), "nr of regions cannot exceed nr of region names defined in config"
l_regions_sel = l_regions[0:n_regions]  # regions selection

# distribution of headcount per branch
HEADCOUNT_AVG = 10
HEADCOUNT_STD = 2

# breakdown of banker types per branch, must add to 1
f_deposit_ofcr = 0.5
f_loan_ofcr = 0.3
f_wealth_ofcr = 0.2
assert (f_deposit_ofcr + f_loan_ofcr + f_wealth_ofcr) == 1

# client types
p_person = 0.75
p_fin_business = 0.075
p_nonfin_business = 0.175
p_nonprofit = 0
assert (p_person + p_fin_business + p_nonfin_business + p_nonprofit) == 1

# client product mix - currently no dependency on client type
# for 'DL' will need to ensure D is CHK
product_mix = 6*['D'] + 4*['DL'] + 2*['DLW'] + 0*['L'] + 0*['LW'] + 3*['W']

# client wealth tiers
p_wealth_tiers = {'low': 0.50, 
                  'mid': 0.45, 
                  'high': 0.05
                 }

# household parmaters
hh_size_distribution = 6*[1] + [2,2,3,4]

# linking paramaters
f_business_owner_link = 0.05

# account frequencies for individuals
f_indiv_accts = {'Deposits': {'CHK': 0.60, 'SV': .15, 'CD': .25}, 
                 'Loans': {'SFR': 0.75, 'PLOC': 0.15, 'PLN': 0.05, 'CRE': 0.05, 'BLOC': 0},
                 'Wealth': {'FRIM': 0.70, 'BKG': 0.30}
                }
# TODO use a loop for the asserts
# TODO add check that all acct dicts have the same structure (use .keys() and loop over dict)
assert round(sum(f_indiv_accts['Deposits'].values()), 1) == 1
assert round(sum(f_indiv_accts['Loans'].values()), 1) == 1
assert round(sum(f_indiv_accts['Wealth'].values()), 1) == 1

# account frequencies for organizations
f_org_accts = {'Deposits': {'CHK': 0.70, 'SV': .20, 'CD': .10}, 
               'Loans': {'SFR': 0.15, 'PLOC': 0, 'PLN': 0, 'CRE': 0.80, 'BLOC': 0.05}, 
               'Wealth': {'FRIM': 0.70, 'BKG': 0.30}
              }
assert round(sum(f_org_accts['Deposits'].values()), 1) == 1
assert round(sum(f_org_accts['Loans'].values()), 1) == 1
assert round(sum(f_org_accts['Wealth'].values()), 1) == 1

# account balances (for each acct type: [avg, std] pairs for use with gaussian dist)
# TODO def avg bal assumptions by wealth tiers (high, mid, low) (e.g. <100K in dep, >100K and < 1M, >1M ; or alt use percentiles e.g. 50%, 90%)
#      add another nested dict to product code: {'low': [20, 20/5], 'mid': [100, 100/5], 'high': [5000, 5000/5]}
bal_indiv_accts = {'Deposits': {'CHK': [100, 100/5], 'SV': [200, 200/5], 'CD': [300, 300/5]}, 
                   'Loans': {'SFR': [1500, 1500/5], 'PLOC': [500, 500/5], 'PLN': [300, 300/5], 'CRE': [2000, 2000/5], 'BLOC': [0, 0/5]},
                   'Wealth': {'FRIM': [2000, 2000/5], 'BKG': [1000, 1000/5]}
                  }

bal_org_accts = {'Deposits': {'CHK': [500, 500/5], 'SV': [2000, 2000/5], 'CD': [3000, 3000/5]}, 
                 'Loans': {'SFR': [1500, 1500/5], 'PLOC': [0, 0/5], 'PLN': [0, 0/5], 'CRE': [5000, 5000/5], 'BLOC': [1000, 1000/5]},
                 'Wealth': {'FRIM': [3000, 3000/5], 'BKG': [4000, 4000/5]}
                }

# transactions
payment_day = 15  # date of direct deposits and loan_payments
tran_min_date, tran_max_date = datetime.datetime(2023,10,1), datetime.datetime(2023,12,31)
transactor_root = ['DYI', 'Kost', 'Toys', 'Games', 'Books', 'Adult\'s', 'Movies', 'Food', 'Sundries', 'Clothes', 'Vice', 'Spice']
transactor_suffix = ['Store', 'Mart', 'R US', '& Co', 'And More', 'Village', 'For All', 'Discounted']

# timeseries
snapshot_date = datetime.datetime(2023, 9, 30)  # date of Init_Balance

# NAICS level 2 codes
naics2_cd = [11,21,22,23,31,42,44,48,51,52,53,54,55,56,61,62,71,72,81,92]
naics2_nm = ['Agriculture','Mining','Utilities','Construction','Manufacturing','Wholesale Trade','Retail Trade',
             'Transportation and Warehousing','Information','Finance and Insurance','Real Estate',
             'Professional Services','Management of Companies','Administrative Services','Educational Services',
             'Health Care','Arts and Entertainment','Accommodation Services','Other Services','Public Administration']
naics2_p = [0.0206,0.0018,0.0029,0.0858,0.0366,0.0395,0.1039,0.0402,0.0212,0.0442,0.0519,
            0.1413,0.0054,0.0900,0.0241,0.0946,0.0218,0.0509,0.1090,0.0143]
assert len(naics2_cd) == len(naics2_nm)
assert len(naics2_cd) == len(naics2_p)
