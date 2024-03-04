import datetime

# set bank size
n_regions = 2
n_branches = 2
n_clients = 1e4

# define default list of regions
l_regions = ['West', 'East', 'North', 'South']

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
p_nonfin_business = 0.125
p_nonprofit = 0.05
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

# NAICS level 3 codes
# TODO add names
naics3 = [111, 112, 113, 114, 115, 211, 212, 213, 221, 236, 237, 238, 311, 312, 313, 314, 315, 316, 
          321, 322, 323, 324, 325, 326, 327, 331, 332, 333, 334, 335, 336, 337, 339, 
          411, 412, 413, 414, 415, 416, 417, 418, 419, 441, 442, 443, 444, 445, 446, 447, 448, 
          451, 452, 453, 454, 481, 482, 483, 484, 485, 486, 487, 488, 491, 492, 493, 
          511, 512, 515, 517, 518, 519, 521, 522, 523, 524, 526, 531, 532, 533, 541, 551, 561, 562, 
          611, 621, 622, 623, 624, 711, 712, 713, 721, 722, 811, 812, 813, 814]
