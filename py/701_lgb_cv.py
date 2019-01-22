#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 16 2018

@author: toshiki.ishikawa
"""

import os
import gc
import sys
import utils
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from glob import glob
from tqdm import tqdm
from datetime import datetime, date
from collections import defaultdict
from multiprocessing import cpu_count, Pool

from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import StratifiedKFold, KFold
from sklearn.metrics import mean_squared_error

import lightgbm as lgb

import warnings
warnings.simplefilter('ignore')

utils.start(__file__)
#==============================================================================
PATH = os.path.join('..', 'data')

KEY = 'card_id'

SEED = 6
# SEED = np.random.randint(9999)

NTHREAD = cpu_count()

NFOLD = 4

# params = {
#     'objective': 'regression',
#     'metric': 'rmse',
#     'boosting': 'gbdt',
#     'learning_rate': 0.015,
#     'max_depth': 8,
#     'num_leaves': 12,

#     # 'min_child_weight': 5.0,
#     'min_data_in_leaf': 27,
#     # 'reg_alpha': 1.0,
#     # 'reg_lambda': 0.1,
#     'lambda_l1': 0.1,
    
#     'feature_fraction': 0.8,
#     'nthread': NTHREAD,
#     'bagging_freq': 1,
#     'bagging_fraction': 0.8,
#     'verbose': -1,
#     'seed': SEED
# }

params = {
    'num_leaves': 31,
    'min_data_in_leaf': 30, 
    'objective':'regression',
    'max_depth': -1,
    'learning_rate': 0.01,
    'boosting': 'gbdt',
    'feature_fraction': 0.8,
    'bagging_freq': 1,
    'bagging_fraction': 0.8,
    'bagging_seed': 11,
    'metric': 'rmse',
    'lambda_l1': 0.1,
    'verbosity': -1,
    'nthread': NTHREAD,
    'random_state': SEED
}

# =============================================================================
# best feature
# =============================================================================

# features =  ['f103.pkl', 'f105.pkl', 'f109.pkl']
# features += ['f107_N.pkl', 'f107_Y.pkl', 
#              'f108_N.pkl', 'f108_Y.pkl']
# features += ['f203.pkl', 'f205.pkl', 'f209.pkl']
# features += ['f207_N.pkl', 'f207_Y.pkl', 
#              'f208_N.pkl', 'f208_Y.pkl']
# features += ['f302.pkl', 'f303.pkl', 'f304.pkl', 'f305.pkl', 'f306.pkl']
# features += ['f403.pkl', 'f404.pkl', 'f409.pkl', 'f411.pkl']
# features += ['f406_N.pkl', 'f406_Y.pkl', 
#              'f408_N.pkl', 'f408_Y.pkl']

# =============================================================================
# features
# =============================================================================

features =  ['f109.pkl']
features += ['f108_N.pkl', 'f108_Y.pkl',
             'f110_N.pkl', 'f110_Y.pkl']

features += ['f209.pkl']
features += ['f208_N.pkl', 'f208_Y.pkl',
             'f210_N.pkl', 'f210_Y.pkl']

features += ['f302.pkl', 'f303.pkl', 'f304.pkl', 'f305.pkl', 'f306.pkl']

features += ['f404.pkl', 'f409.pkl', 'f411.pkl']
features += ['f407_N.pkl', 'f407_Y.pkl',
             'f408_N.pkl', 'f408_Y.pkl']

# features += ['f501.pkl']

# features = os.listdir('../feature')

# =============================================================================
# read data and features
# =============================================================================
train = pd.read_csv(os.path.join(PATH, 'train.csv'))
test = pd.read_csv(os.path.join(PATH, 'test.csv'))

for f in features:
    print(f'Merge: {f}', end=' ')
    t = pd.read_pickle(os.path.join('..', 'feature', f))
    train = pd.merge(train, t, on=KEY, how='left')
    test = pd.merge(test, t, on=KEY, how='left')
    print('Done!!')

# =============================================================================
# change date to int
# =============================================================================
cols = train.columns.values
for f in [
    'hist_purchase_date_max', 'hist_purchase_date_min', 
    'N_hist_auth_purchase_date_max', 'N_hist_auth_purchase_date_min', 
    'Y_hist_auth_purchase_date_max', 'Y_hist_auth_purchase_date_min', 
    'new_purchase_date_max', 'new_purchase_date_min', 
    'N_new_auth_purchase_date_max', 'N_new_auth_purchase_date_min',
    'Y_new_auth_purchase_date_max', 'Y_new_auth_purchase_date_min', 
    'union_purchase_date_max', 'union_purchase_date_min', 
    'N_union_auth_purchase_date_max', 'N_union_auth_purchase_date_min',
    'Y_union_auth_purchase_date_max', 'Y_union_auth_purchase_date_min'
    'new_purchase_date_max_y', 'new_purchase_date_min_y', 
    'union_purchase_date_max_y', 'union_purchase_date_min_y',
    ]:
    if f in cols:
        train[f] = train[f].astype(np.int64) * 1e-9
        test[f] = test[f].astype(np.int64) * 1e-9

# =============================================================================
# drop same values
# =============================================================================
drop_cols = pd.read_csv('duplicated_columns.csv')

for d in drop_cols['duplicated_columns'].values:
    if d in cols:
        train.drop(d, axis=1, inplace=True)
        test.drop(d, axis=1, inplace=True)

# =============================================================================
# preprocess
# =============================================================================

for col in train.columns:
    if train[col].isna().any():
        train[col] = train[col].fillna(0)

for col in test.columns:
    if test[col].isna().any():
        test[col] = test[col].fillna(0)

train['nan_count'] = train.isnull().sum(axis=1)
test['nan_count'] = test.isnull().sum(axis=1)

y = train['target']

col_not_to_use = ['first_active_month', 'card_id', 'target']
col_to_use = [c for c in train.columns if c not in col_not_to_use]

train = train[col_to_use]
test = test[col_to_use]

train['feature_3'] = train['feature_3'].astype(int)
test['feature_3'] = test['feature_3'].astype(int)

categorical_features = ['feature_1', 'feature_2', 'feature_3']

for col in categorical_features:
    lbl = LabelEncoder()
    lbl.fit(list(train[col].values.astype('str')) + list(test[col].values.astype('str')))
    train[col] = lbl.transform(list(train[col].values.astype('str')))
    test[col] = lbl.transform(list(test[col].values.astype('str')))

gc.collect()

# =============================================================================
# feature selection
# =============================================================================
# feature = pd.read_csv('IMP_csv/20190115_IMP.csv')
# g = feature.groupby(['feature'])['importance'].mean().reset_index()
# g = g.sort_values('importance', ascending=False).reset_index(drop=True)
# g = g[g.importance > 0]
# g = g.feature.values

# X = train[g]
# X_test = test[g]

X = train
X_test = test

# ========= ====================================================================
# cv
# =============================================================================
folds = KFold(n_splits=NFOLD, shuffle=True, random_state=SEED)

oof = np.zeros(len(X))
prediction = np.zeros(len(X_test))

scores = []

feature_importance = pd.DataFrame()

for fold_n, (train_index, valid_index) in enumerate(folds.split(X)):
    dtrain = lgb.Dataset(X.iloc[train_index], label=y.iloc[train_index])
    dvalid = lgb.Dataset(X.iloc[valid_index], label=y.iloc[valid_index])

    model = lgb.train(
        params,
        dtrain,
        20000,          
        valid_sets=[dtrain, dvalid],
        verbose_eval=2000,
        early_stopping_rounds=100)
    
    y_pred_valid = model.predict(X.iloc[valid_index], num_iteration=model.best_iteration)
    y_pred = model.predict(X_test, num_iteration=model.best_iteration)
    
    oof[valid_index] = y_pred_valid.reshape(-1,)
    scores.append(np.sqrt(mean_squared_error(y.iloc[valid_index], y_pred_valid)))
    
    prediction += y_pred / folds.n_splits   

    fold_importance = pd.DataFrame()
    fold_importance['feature'] = X.columns
    fold_importance['importance'] = model.feature_importance()
    fold_importance['fold'] = fold_n + 1
    feature_importance = pd.concat([feature_importance, fold_importance], axis=0)

np.save(os.path.join('stacking', '{}_oof_lgb'.format(str(date.today()).replace('-', ''))), oof)
np.save(os.path.join('stacking', '{}_prediction_lgb'.format(str(date.today()).replace('-', ''))), prediction)

print('shape:', X.shape)
print('CV mean score: {0:.4f}, std: {1:.4f}.'.format(np.mean(scores), np.std(scores)))
print(features)

submission = pd.read_csv(os.path.join('..', 'input', 'sample_submission.csv'))
submission['target'] = prediction
submission.to_csv(os.path.join('..', 'submission', 'lightgbm_{}.csv'.format(str(date.today()).replace('-', ''))), index=False)

feature_importance['importance'] /= NFOLD
cols = feature_importance[['feature', 'importance']].groupby('feature').mean().sort_values(by='importance', ascending=False)[:50].index

best_features = feature_importance.loc[feature_importance.feature.isin(cols)]
best_features = best_features.sort_values(by='importance', ascending=False)
feature_importance.sort_values(by='importance', ascending=False).to_csv('./IMP_csv/{}_IMP.csv'.format(str(date.today()).replace('-', '')), index=False)

plt.figure(figsize=(14, 25))
plt.title('LGB Features (avg over folds)')
plot = sns.barplot(x='importance', y='feature', data=best_features)
fig = plot.get_figure()
fig.savefig('./IMP_png/{}_IMP.png'.format(str(date.today()).replace('-', '')), bbox_inches='tight')

#==============================================================================
utils.end(__file__)