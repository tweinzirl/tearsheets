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
product_mix = 6*['D'] + 3*['DL'] + 2*['DLW'] + ['L'] + ['LW'] + 2*['W']

# household parmaters
hh_size_distribution = 6*[1] + [2,2,3,4]

# account frequencies for individuals
# TODO use only one dict for both indiv and org
f_indiv_accts = {'Deposits': {'CHK': 0.60, 'SV': .15, 'CD': .25}, 
                 'Loans': {'SFR': 0.80, 'HELOC': 0.15, 'MF': 0, 'CRE': 0.05, 'LOC': 0},
                 'Wealth': {'FRIM': 0.70, 'FRS': 0.30}}
# TODO use a loop for the asserts
assert round(sum(f_indiv_accts['Deposits'].values()), 1) == 1
assert round(sum(f_indiv_accts['Loans'].values()), 1) == 1
assert round(sum(f_indiv_accts['Wealth'].values()), 1) == 1

# account frequencies for organizations
f_org_accts = {'Deposits': {'CHK': 0.70, 'SV': .20, 'CD': .10}, 
               'Loans': {'SFR': 0.15, 'HELOC': 0, 'MF': 0.25, 'CRE': 0.55, 'LOC': 0.05}, 
               'Wealth': {'FRIM': 0.70, 'FRS': 0.30}
              }
assert round(sum(f_org_accts['Deposits'].values()), 1) == 1
assert round(sum(f_org_accts['Loans'].values()), 1) == 1
assert round(sum(f_org_accts['Wealth'].values()), 1) == 1
