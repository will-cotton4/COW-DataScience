"""
This module imports the cleaned and merged data 
and runs an XGBoost model on it.
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.metrics import accuracy_score
from xgboost import XGBClassifier
from merge import nmc_war_trade_alliance

xgboost_model = XGBClassifier(n_jobs=-1, random_state=42)

leaks = ['warnum', 'conflict', 'outcomea', 'batdtha' ,'batdths', 'StateNme', 'right_censor']

train = nmc_war_trade_alliance[nmc_war_trade_alliance['year'] < 1987]

X_train = train.drop(columns=leaks)
y_train = train['conflict']

test = nmc_war_trade_alliance[(nmc_war_trade_alliance['year'] >= 1987)]

X_test = test.drop(columns=leaks)
y_test = test['conflict']

xgboost_model.fit(X_train, y_train)

predictions = xgboost_model.predict(X_test)
probs = xgboost_model.predict_proba(X_test)