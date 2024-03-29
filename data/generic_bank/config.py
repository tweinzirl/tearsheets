import datetime

# set bank size & parameters
n_regions = 2
n_branches = 2
n_clients = 1e4
founding_date = datetime.datetime(2005,1,1)  # established date

# define default list of regions
l_regions = ['West', 'East', 'North', 'South']
assert n_regions <= len(l_regions), "nr of regions cannot exceed nr of region names defined in config"
# regions selection
l_regions_sel = l_regions[0:n_regions]

# distribution of headcount per branch
HEADCOUNT_AVG = 14
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

# account frequencies (individuals, nonfinorgs, finorgs)
f_accts = {'Person':  ## Individual
               {'Deposits': {'low': {'CHK': 0.65, 'SV': .25, 'CD': .10},
                             'mid': {'CHK': 0.60, 'SV': .20, 'CD': .20},
                             'high': {'CHK': 0.55, 'SV': .15, 'CD': .30}
                             }, 
                'Loans':    {'low': {'SFR': 0.40, 'PLOC': 0.50, 'PLN': 0.10, 'CRE': 0, 'COMM': 0},
                             'mid': {'SFR': 0.60, 'PLOC': 0.30, 'PLN': 0.10, 'CRE': 0, 'COMM': 0},
                             'high': {'SFR': 0.80, 'PLOC': 0.15, 'PLN': 0.05, 'CRE': 0, 'COMM': 0}
                             },
                'Wealth':   {'low': {'PM': 0.60, 'BKG': 0.40},
                             'mid': {'PM': 0.65, 'BKG': 0.35},
                             'high': {'PM': 0.70, 'BKG': 0.30}
                             }
                },
           'Business - Other':  ## NonFinOrg
               {'Deposits': {'low': {'CHK': 0.75, 'SV': .20, 'CD': .05},
                             'mid': {'CHK': 0.70, 'SV': .20, 'CD': .10},
                             'high': {'CHK': 0.65, 'SV': .20, 'CD': .15}
                             },
                'Loans':    {'low': {'SFR': 0.35, 'PLOC': 0, 'PLN': 0, 'CRE': 0.30, 'COMM': 0.35},
                             'mid': {'SFR': 0.25, 'PLOC': 0, 'PLN': 0, 'CRE': 0.50, 'COMM': 0.25},
                             'high': {'SFR': 0.15, 'PLOC': 0, 'PLN': 0, 'CRE': 0.70, 'COMM': 0.15}
                             },
                'Wealth':   {'low': {'PM': 0.65, 'BKG': 0.35},
                             'mid': {'PM': 0.70, 'BKG': 0.30},
                             'high': {'PM': 0.75, 'BKG': 0.25}
                             }
                },
           'Business - Finance':  ## FinOrg 
               {'Deposits': {'low': {'CHK': 0.75, 'SV': .20, 'CD': .05},
                             'mid': {'CHK': 0.70, 'SV': .20, 'CD': .10},
                             'high': {'CHK': 0.65, 'SV': .20, 'CD': .15}
                             }, 
                'Loans':    {'low': {'SFR': 0.10, 'PLOC': 0, 'PLN': 0, 'CRE': 0.15, 'COMM': 0.75},
                             'mid': {'SFR': 0.10, 'PLOC': 0, 'PLN': 0, 'CRE': 0.20, 'COMM': 0.70},
                             'high': {'SFR': 0.10, 'PLOC': 0, 'PLN': 0, 'CRE': 0.25, 'COMM': 0.65}
                             },
                'Wealth':   {'low': {'PM': 0.65, 'BKG': 0.35},
                             'mid': {'PM': 0.70, 'BKG': 0.30},
                             'high': {'PM': 0.75, 'BKG': 0.25}
                             }
                }
            }
# check proportions add up to 1 and products are consistent for each segment
# TODO add checks for str at each level of list
for cl in f_accts: 
    for ln in f_accts[cl]: 
        for tr in f_accts[cl][ln]:
            assert round(sum(f_accts[cl][ln][tr].values()), 2) ==  1
            assert list(f_accts[cl]['Deposits'][tr].keys()) == ['CHK', 'SV', 'CD'], f_accts[cl]['Deposits'][tr].keys()
            assert list(f_accts[cl]['Loans'][tr].keys()) == ['SFR', 'PLOC', 'PLN', 'CRE', 'COMM'], f_accts[cl]['Loans'][tr].keys()
            assert list(f_accts[cl]['Wealth'][tr].keys()) == ['PM', 'BKG'], f_accts[cl]['Wealth'][tr].keys()

# account balances in $, by wealth tiers (low, mid, high)
# for each acct type: [avg, std] pairs for use with gaussian dist
bal_accts = {'Person':  ## Individual
               {'Deposits': {'low': {'CHK': [10e3, 10e3], 'SV': [5e3, 5e3], 'CD': [15e3, 15e3]},
                             'mid': {'CHK': [100e3, 75e3], 'SV': [125e3, 100e3], 'CD': [150e3, 125e3]},
                             'high': {'CHK': [1.5e6, 1e6], 'SV': [2e6, 1.5e6], 'CD': [3e6, 2e6]}
                             }, 
                'Loans':    {'low': {'SFR': [700e3, 350e3], 'PLOC': [100e3, 100e3], 'PLN': [150e3, 150e3], 'CRE': [0, 0], 'COMM': [0, 0]},
                             'mid': {'SFR': [1.5e6, 750e3], 'PLOC': [500e3, 500e3], 'PLN': [750e3, 750e3], 'CRE': [0, 0], 'COMM': [0, 0]},
                             'high': {'SFR': [5e6, 2.5e6], 'PLOC': [4e6, 4e6], 'PLN': [6e6, 6e6], 'CRE': [0, 0], 'COMM': [0, 0]}
                             },
                'Wealth':   {'low': {'PM': [100e3, 100e3], 'BKG': [100e3, 100e3]},
                             'mid': {'PM': [500e3, 500e3], 'BKG': [500e3, 500e3]},
                             'high': {'PM': [5e6, 20e6], 'BKG': [5e6, 20e6]}
                             }
                },
           'Business - Other':  ## NonFinOrg 
               {'Deposits': {'low': {'CHK': [20e3, 40e3], 'SV': [25e3, 50e3], 'CD': [30e3, 30e3]},
                             'mid': {'CHK': [250e3, 500e3], 'SV': [300e3, 600e3], 'CD': [250e3, 500e3]},
                             'high': {'CHK': [5e6, 10e6], 'SV': [10e6, 20e6], 'CD': [2.5e6, 5e6]}
                             }, 
                'Loans':    {'low': {'SFR': [700e3, 350e3], 'PLOC': [0, 0], 'PLN': [0, 0], 'CRE': [1e6, 500e3], 'COMM': [500e3, 500e3]},
                             'mid': {'SFR': [2.5e6, 2e6], 'PLOC': [0, 0], 'PLN': [0, 0], 'CRE': [3e6, 1.5e6], 'COMM': [3e6, 3e6]},
                             'high': {'SFR': [15e6, 7.5e6], 'PLOC': [0, 0], 'PLN': [0, 0], 'CRE': [20e6, 10e6], 'COMM': [15e6, 15e6]}
                             },
                'Wealth':   {'low': {'PM': [500e3, 500e3], 'BKG': [250e3, 250e3]},
                             'mid': {'PM': [2e6, 2e6], 'BKG': [1.5e6, 1.5e6]},
                             'high': {'PM': [20e6, 40e6], 'BKG': [15e6, 30e6]}
                             }
                },
           'Business - Finance':  ## FinOrg 
               {'Deposits': {'low': {'CHK': [30e3, 60e3], 'SV': [30e3, 60e3], 'CD': [40e3, 80e3]},
                             'mid': {'CHK': [500e3, 1e6], 'SV': [600e3, 1.2e6], 'CD': [400e3, 400e3]},
                             'high': {'CHK': [10e6, 20e6], 'SV': [20e6, 40e6], 'CD': [7.5e6, 15e6]}
                             }, 
                'Loans':    {'low': {'SFR': [700e3, 350e3], 'PLOC': [0, 0], 'PLN': [0, 0], 'CRE': [1e6, 500e3], 'COMM': [500e3, 500e3]},
                             'mid': {'SFR': [2.5e6, 2e6], 'PLOC': [0, 0], 'PLN': [0, 0], 'CRE': [3e6, 1.5e6], 'COMM': [5e6, 5e6]},
                             'high': {'SFR': [15e6, 7.5e6], 'PLOC': [0, 0], 'PLN': [0, 0], 'CRE': [15e6, 7.5e6], 'COMM': [20e6, 20e6]}
                             },
                'Wealth':   {'low': {'PM': [500e3, 500e3], 'BKG': [250e3, 250e3]},
                             'mid': {'PM': [2.5e6, 5e6], 'BKG': [2e6, 4e6]},
                             'high': {'PM': [25e6, 50e6], 'BKG': [20e6, 40e6]}
                             }
                }
          }
# check products are consistent for each segment
for cl in bal_accts: 
    for ln in bal_accts[cl]: 
        for tr in bal_accts[cl][ln]:
            # assert round(sum(bal_accts[cl][ln][tr].values()), 2) ==  1
            assert list(bal_accts[cl]['Deposits'][tr].keys()) == ['CHK', 'SV', 'CD'], bal_accts[cl]['Deposits'][tr].keys()
            assert list(bal_accts[cl]['Loans'][tr].keys()) == ['SFR', 'PLOC', 'PLN', 'CRE', 'COMM'], bal_accts[cl]['Loans'][tr].keys()
            assert list(bal_accts[cl]['Wealth'][tr].keys()) == ['PM', 'BKG'], bal_accts[cl]['Wealth'][tr].keys()

# guardrails for negative acct balances and min acct balances
# TODO move params to config


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
