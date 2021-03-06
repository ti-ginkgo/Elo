# =============================================================================
# 000 initializer
# =============================================================================
# python -u 001_preprocess.py
# python -u 002_init.py

# =============================================================================
# 100 historical
# =============================================================================
# python -u 101_init.py

# python -u 102_aggregate.py
# python -u 103_aggregate_special_days.py
# python -u 104_category.py
# python -u 105_category_target_encoding.py
# python -u 106_installments_exception.py
# python -u 107_count_encoding.py
# python -u 108_count_minus_one.py

python -u 111_authorized_aggregate.py

# python -u 121_authorized_rate.py
# python -u 122_repurchase_rate.py
# python -u 123_rank_k.py
# python -u 124_rank_k_with_fractions.py

# python -u 131_pivot_table_purchase_amount.py
# python -u 132_pivot_table_installments.py

# python -u 141_LinearRegression.py

# =============================================================================
# 200 new_merchant
# =============================================================================
# python -u 201_init.py

python -u 202_aggregate.py
# python -u 203_aggregate_special_days.py
# python -u 204_category.py
python -u 205_category_target_encoding.py
# python -u 206_installmetns_exception.py
# python -u 207_count_encoding.py
# python -u 208_count_minus_one.py

# python -u 211_authorized_aggregate.py
# python -u 212_authorized_aggregate_per_month.py

# python -u 221_rank_k.py

# python -u 231_pivot_table_purchase_amount.py
# python -u 232_pivot_table_installments.py

# =============================================================================
# 300 merchants
# =============================================================================
# python -u 301_init.py
# python -u 302_merchants_score.py
# python -u 303_historical_aggregate.py
# python -u 304_new_aggregate.py
# python -u 305_unique_aggregate.py

# =============================================================================
# 400 union
# =============================================================================
# python -u 401_init.py

# python -u 402_aggregate.py
# python -u 403_aggregate_per_month.py

# python -u 411_authorized_aggregate.py
# python -u 412_authorized_aggregate_per_month.py

# python -u 421_authorized_rate.py
# python -u 422_repurchase_rate.py

# =============================================================================
# 600 CV
# =============================================================================
python -u 601_preprocess.py

# =============================================================================
# 700 CV
# =============================================================================
# python -u 701_lgb_cv.py