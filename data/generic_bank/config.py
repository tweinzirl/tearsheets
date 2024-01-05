# distribution of headcount per branch
HEADCOUNT_AVG = 10
HEADCOUNT_STD = 2

# breakdown of banker types per branch, must add to 1
f_RM = 0.8
f_Wealth_Advisor = 0.2

# client types
p_person = 0.75
p_fin_business = 0.075
p_nonfin_business = 0.125
p_nonprofit = 0.05
assert (p_person + p_fin_business + p_nonfin_business + p_nonprofit) == 1

# household parmaters
hh_size_distribution = 6*[1] + [2,2,3,4]
