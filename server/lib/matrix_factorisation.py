# matrix_factorization.py - Matrix factorization related functions

# Imports
import os
import sys
sys.path.insert(1, os.path.join(sys.path[0], '..'))
import config
import pandas as pd
from matrix_factorization import BaselineModel, KernelMF
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split

# Constants
mf_data_header = ['user_id', 'item_id', 'rating']
num_users = 14000

# Transforms data for use with matrix factorization library
def transform_data(data):
    users = data['Unnamed: 0'].tolist()
    ratings = data.iloc[:, 1:config.NUM_LOC + 1]
    ratings = ratings.where(pd.notnull(ratings), 0)
    ratings = ratings.to_numpy()
    ratings = [[int(float(j)) for j in i] for i in ratings]

    # Create three columns, with one rating in each row
    u_col = []
    item_col = []
    rat_col = []

    for u in users:
        for i in range(config.NUM_LOC):
            if ratings[u][i] != 0:
                u_col.append(u)
                item_col.append(i)
                rat_col.append(ratings[u][i])

    # Recombine into three column dataframe
    mf_data = pd.DataFrame(list(zip(u_col, item_col, rat_col)),columns=mf_data_header)
    return mf_data

# Compares performance of various matrix factorization algorithms
def algo_comparison(data, epochs, info_toggle):
    X = data[["user_id", "item_id"]]
    y = data["rating"]

    # Prepare data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

    # Simple model
    global_mean = y_train.mean()
    pred = [global_mean for _ in range(y_test.shape[0])]
    rmse = mean_squared_error(y_test, pred, squared = False)
    print(f'\nSimple Model Test RMSE: {rmse:4f}')

    # Baseline SGD model
    baseline_model = BaselineModel(method='sgd', n_epochs = epochs, reg = 0.005, lr = 0.01, verbose=info_toggle)
    baseline_model.fit(X_train, y_train)
    pred = baseline_model.predict(X_test)
    rmse = mean_squared_error(y_test, pred, squared = False)
    print(f'\nSGD Test RMSE: {rmse:.4f}')

    # Baseline ALS
    baseline_model = BaselineModel(method='als', n_epochs = epochs, reg = 0.5, verbose=info_toggle)
    baseline_model.fit(X_train, y_train)
    pred = baseline_model.predict(X_test)
    rmse = mean_squared_error(y_test, pred, squared = False)
    print(f'\nALS Test RMSE: {rmse:.4f}')

    # Matrix factorization
    matrix_fact = KernelMF(n_epochs = epochs, n_factors = 20, verbose = info_toggle, lr = 0.001, reg = 0.005)
    matrix_fact.fit(X_train, y_train)
    pred = matrix_fact.predict(X_test)
    rmse = mean_squared_error(y_test, pred, squared = False)
    print(f'\nMF Linear Kernel Test RMSE: {rmse:.4f}')

    # Sigmoid kernel
    matrix_fact = KernelMF(n_epochs = epochs, n_factors = 20, verbose = info_toggle, lr = 0.01, reg = 0.005, kernel='sigmoid')
    matrix_fact.fit(X_train, y_train)
    pred = matrix_fact.predict(X_test)
    print(f'\nMF Sigmoid Kernel Test RMSE: {rmse:.4f}')
    
    # RBF kernel
    matrix_fact = KernelMF(n_epochs = epochs, n_factors = 20, verbose = info_toggle, lr = 0.5, reg = 0.005, kernel='rbf')
    matrix_fact.fit(X_train, y_train)
    pred = matrix_fact.predict(X_test)
    rmse = mean_squared_error(y_test, pred, squared = False)
    print(f'\nMF RBF Kernel Test RMSE: {rmse:.4f}')

# Perform matrix factorization on sparse matrix and save to csv
def save_mf_table(mf_data, orig_data, epochs, info_toggle):
    X = mf_data[["user_id", "item_id"]]
    y = mf_data["rating"]

    # Perform matrix factorization to generate predicted ratings
    matrix_fact = KernelMF(n_epochs = epochs, n_factors = 20, verbose = info_toggle, lr = 0.5, reg = 0.005, kernel='rbf')
    matrix_fact.fit(X, y)

    full_users = []
    full_items = []

    # Reformat matrix factorization output to 14000 x 27 matrix
    # Gather all users and locations corresponding to each rating
    for u in range(num_users):
        for i in range(config.NUM_LOC):
            full_users.append(u)
            full_items.append(i)
    X_full = pd.DataFrame(list(zip(full_users, full_items)),columns=['user_id', 'item_id'])
    pred = matrix_fact.predict(X_full)

    mf_table = [None] * num_users

    # For each user, add their predicted rating for each location
    for u in range(num_users):
        user = [None] * config.NUM_LOC
        for i in range(config.NUM_LOC):
            user[i] = round(pred[(u * config.NUM_LOC) + i],2)
        mf_table[u] = user

    # Add data to csv after formatting
    df = pd.DataFrame(mf_table, columns=config.ATTRACTIONS_HEADER)
    user_types = orig_data[config.FEATURES_HEADER]
    new_ratings = pd.concat([df, user_types], axis=1)
    print(new_ratings)
    
    new_ratings.to_csv("lib/data/mf_ratings.csv", mode='w', header=True)

ratings = pd.read_csv('lib/data/ratings.csv')
mf_data = transform_data(ratings)
algo_comparison(mf_data, 20, 0)
