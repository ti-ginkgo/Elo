#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 29 2018

@author: toshiki.ishikawa
"""

import os
import sys
import gc
import utils
import numpy as np
import pandas as pd

from tqdm import tqdm
from datetime import datetime, date
from sklearn.preprocessing import LabelEncoder
from multiprocessing import cpu_count, Pool


utils.start(__file__)
#==============================================================================
NTHREAD = cpu_count()

PREF = 'f304'

KEY = 'card_id'

stats = ['sum', 'mean', 'std']

# =============================================================================
#
# =============================================================================
PATH = os.path.join('..', 'data')

merchants = pd.read_csv(os.path.join(PATH, 'merchants.csv'))
new_merchant_transactions = pd.read_csv(os.path.join(PATH, 'new_merchant_transactions.csv'), usecols=['card_id', 'merchant_id'])

merchants = merchants.drop_duplicates(subset=['merchant_id'], keep='first').reset_index(drop=True) # TODO: change first
new_merchant_transactions = pd.merge(new_merchant_transactions, merchants, on='merchant_id', how='left')
new_merchant_transactions = new_merchant_transactions.fillna(0)

del merchants
gc.collect()
# =============================================================================
#
# =============================================================================
def aggregate(args):
    prefix, key, num_aggregations = args['prefix'], args['key'], args['num_aggregations']
    
    agg = new_merchant_transactions.groupby(key).agg(num_aggregations).reset_index()
    agg.columns = [f'{c[0]}_{c[1]}'.strip('_') for c in agg.columns]
    agg = agg.add_prefix(prefix)
    agg = agg.rename(columns={prefix+KEY:KEY})

    agg.to_pickle(f'../feature/{PREF}.pkl')

    return

# =============================================================================
#
# =============================================================================
if __name__ == '__main__':
    argss = [
        {
            'prefix': 'new_merchants_',
            'key': ['card_id'],
            'num_aggregations': {
                # 'merchant_group_id': ['nunique'],
                # 'merchant_category_id': ['nunique'],
                # 'subsector_id': ['nunique'],
                # 'state_id': ['nunique'],
                'numerical_1': ['sum', 'mean'],
                'numerical_2': ['sum', 'mean'],
                'category_1': ['sum', 'mean'], # 0, 1
                # 'category_2': ['mean'], # 1, 2, 3, 4, 5
                'category_4': ['sum', 'mean'], # 0, 1
            }
        }
    ]

    pool = Pool(NTHREAD)
    callback = pool.map(aggregate, argss)
    pool.close()

#==============================================================================
utils.end(__file__)
