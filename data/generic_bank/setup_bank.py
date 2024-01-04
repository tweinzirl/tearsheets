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
    branches_ = branches(n_branches)
    branches_ = regions_.merge(branches_, how='cross')

    branches_.Branch_Number = range(1, branches_.shape[0]+1, 1)
    branches_.Branch_Manager = range(1, branches_.shape[0]+1, 1)

    return branches_
    
