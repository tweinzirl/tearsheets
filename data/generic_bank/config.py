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
f_dep_acct_indiv = {'CHK': 0.60, 'SV': .15, 'CD': .25}
f_loan_acct_indiv = {'SFR': 0.80, 'HELOC': 0.15, 'MF': 0, 'CRE': 0.05, 'LOC': 0}
f_wealth_acct_indiv = {'FRIM': 0.70, 'FRS': 0.30}
assert round(sum(f_dep_acct_indiv.values()), 1) == 1
assert round(sum(f_loan_acct_indiv.values()), 1) == 1
assert round(sum(f_wealth_acct_indiv.values()), 1) == 1

# account frequencies for organizations
f_dep_acct_org = {'CHK': 0.70, 'SV': .20, 'CD': .10}
f_loan_acct_org = {'SFR': 0.15, 'HELOC': 0, 'MF': 0.25, 'CRE': 0.55, 'LOC': 0.05}
f_wealth_acct_org = {'FRIM': 0.70, 'FRS': 0.30}
assert round(sum(f_dep_acct_org.values()), 1) == 1
assert round(sum(f_loan_acct_org.values()), 1) == 1
assert round(sum(f_wealth_acct_org.values()), 1) == 1
