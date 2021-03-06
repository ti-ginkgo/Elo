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

PREF = 'f305'

KEY = 'card_id'

stats = ['nunique', 'sum', 'mean', 'std']

# =============================================================================
#
# =============================================================================
PATH = os.path.join('..', 'data')

merchants = pd.read_csv(os.path.join(PATH, 'merchants.csv'))
historical_transactions = pd.read_csv(os.path.join(PATH, 'historical_transactions.csv'), usecols=['card_id', 'merchant_id'])

merchants = merchants.drop_duplicates(subset=['merchant_id'], keep='first').reset_index(drop=True) # TODO: change first
historical_transactions = pd.merge(historical_transactions, merchants, on='merchant_id', how='left')

del merchants
gc.collect()

# =============================================================================
#
# =============================================================================
def aggregate(args):
    prefix, key, num_aggregations = args['prefix'], args['key'], args['num_aggregations']

    agg = historical_transactions.groupby(key).agg(num_aggregations).reset_index()
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
            'prefix': 'merchants_',
            'key': ['card_id'],
            'num_aggregations': {
                'most_recent_sales_range': ['nunique'], 
                'most_recent_purchases_range': ['nunique'], 
                'avg_sales_lag3': stats,
                'avg_purchases_lag3': stats,
                'active_months_lag3': stats,
                'avg_sales_lag6': stats,
                'avg_purchases_lag6': stats,
                'active_months_lag6': stats,
                'avg_sales_lag12': stats,
                'avg_purchases_lag12': stats,
                'active_months_lag12': stats
            }
        }
    ]

    pool = Pool(NTHREAD)
    callback = pool.map(aggregate, argss)
    pool.close()

#==============================================================================
utils.end(__file__)
