# recommender.py - Functions for generating recommendations for users

# Imports
import numpy as np
import pandas as pd
from sklearn.neighbors import NearestNeighbors
import joblib
import config

# Get recommendations for a user
def get_recommendations(user, context):
    # Read in ratings table and get relevant fields
    df = pd.read_csv("lib/data/mf_ratings.csv")
    ratings = df.iloc[:, 1:config.NUM_LOC + 1]
    ratings = ratings.where(pd.notnull(ratings), 0)

    # Find locations user has rated
    user_rated_ind = []
    for i in range(len(user)):
        if user[i] != 0 and user[i] != -1:
            user_rated_ind.append(i)

    # Get ratings table ratings for locations user has rated
    relevant_ratings = ratings.iloc[:,user_rated_ind]
    ratings = ratings.to_numpy()
    relevant_ratings = relevant_ratings.to_numpy()

    # Create a model for getting recommendations using ratings of locations user has rated
    model = NearestNeighbors(n_neighbors=1, radius=0.4)
    model.fit(relevant_ratings)

    # Get closest matching user in ratings table to current user
    neigh_ind = model.kneighbors([[user[ind] for ind in user_rated_ind]], 1, return_distance=False)
    neigh_ind += 2000 * config.FEATURES_HEADER.index(context)
    neigh_rat = ratings[neigh_ind]

    # Find the top 5 locations that the current user has not yet visited
    neigh_top5 = np.argsort(neigh_rat)[-5:]
    neigh_top5 = np.flip(neigh_top5[0][0])
    recs = []
    for i in neigh_top5:
        if user[i] == 0.0:
            recs.append(i)

    if len(recs) > 5:
        recs = recs[0:5]
    return recs

    
# Indices
# NO LONGER USED
act_i = 0
walk_i = 2000
nat_i = 4000
mus_i = 6000
his_i = 8000
tour_i = 10000
spo_i = 12000

# Create a model for user in recommendations
# NO LONGER USED
def create_model(data, context):
    if context is config.FEATURES_HEADER[0]:
        data = data[act_i:walk_i,:]
    elif context is config.FEATURES_HEADER[1]:
        data = data[walk_i:nat_i,:]
    elif context is config.FEATURES_HEADER[2]:
        data = data[nat_i:mus_i,:]
    elif context is config.FEATURES_HEADER[3]:
        data = data[mus_i:his_i,:]
    elif context is config.FEATURES_HEADER[4]:
        data = data[his_i:tour_i,:]
    elif context is config.FEATURES_HEADER[5]:
        data = data[tour_i:spo_i,:]
    elif context is config.FEATURES_HEADER[6]:
        data = data[spo_i:,:]
    else:
        print("ERROR: Invalid context")
        return None
    recommender = NearestNeighbors(n_neighbors=1, radius=0.4)
    recommender.fit(data)

    return recommender

# Load a recommender model
# NO LONGER USED
def load_model(context):
    file_name = 'lib/models/' + context + '_model.sav'
    model = joblib.load(file_name)
    return model

# Save a recommender model
# NO LONGER USED
def save_model(model, context):
    file_name = 'lib/models/' + context + '_model.sav'
    joblib.dump(model, file_name)
