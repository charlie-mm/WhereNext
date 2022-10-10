# data_gen.py - Functions for generating simulated user data

# Imports
import os
import sys
sys.path.insert(1, os.path.join(sys.path[0], '..'))
import config
import pandas as pd
import random
import numpy as np
from os.path import exists

# Read in features csv file
features = pd.read_csv('lib/data/features.csv')

# User generation function
def generate_visitors(iterations, probability, context):
    ratings = [None] * iterations
    # For each user to be generated
    for i in range(iterations):
        user = [None] * len(config.RATINGS_HEADER)
        # For each location
        for j in range(len(config.RATINGS_HEADER) - len(config.FEATURES_HEADER)):
            chance = random.uniform(0, 1)
            # Decide if user has visited according to probability
            if chance <= probability[j]:
                # Rate high or low based on if their type matches the location type
                if features[context][j]:
                    user[j] = random.randint(4,5)
                else:
                    user[j] = random.randint(1,3)
        # Add user type to column at end of row
        # 1 if user is of that type, 0 if not
        for type in range(len(config.FEATURES_HEADER)):
            user[len(config.RATINGS_HEADER) - len(config.FEATURES_HEADER) + type] = int(context == config.FEATURES_HEADER[type])
        ratings[i] = user

    # Compile all generated users into a dataframe
    df = pd.DataFrame(ratings,columns=config.RATINGS_HEADER)
    df = df.fillna(value=np.nan)
    return df

# Add generated data to csv
def add_to_csv(data):
    if not exists('lib/data/ratings.csv'):
        data.to_csv('lib/data/ratings.csv', mode='a', header=True)
    else:
        data.to_csv('lib/data/ratings.csv', mode='a', header=False)

# Activity user
p = [0.9, 0.8, 0.1, 0.2, 0.1, 0.8, 0.3, 0.2, 0.2, 0.1, 0.6, 0.4, 0.4, 0.5, 0.3, 0.1, 0.8, 0.4, 0.1, 0.4]
generated_ratings = generate_visitors(2000, p, 'activity')

# Walk user
p = [0.4, 0.1, 0.7, 0.8, 0.2, 0.1, 0.7, 0.1, 0.4, 0.2, 0.2, 0.6, 0.6, 0.8, 0.7, 0.2, 0.1, 0.8, 0.1, 0.7]
walk_r = generate_visitors(2000, p, 'walk')

# Nature user
p = [0.6, 0.1, 0.6, 0.8, 0.1, 0.1, 0.7, 0.1, 0.3, 0.1, 0.7, 0.6, 0.6, 0.7, 0.7, 0.1, 0.1, 0.8, 0.1, 0.7]
nat_r = generate_visitors(2000, p, 'nature')

# Museum user
p = [0.1, 0.1, 0.7, 0.8, 0.7, 0.1, 0.2, 0.8, 0.7, 0.8, 0.3, 0.2, 0.2, 0.2, 0.3, 0.5, 0.2, 0.1, 0.8, 0.7]
mus_r = generate_visitors(2000, p, 'museum')

# Historical user
p = [0.2, 0.1, 0.8, 0.9, 0.7, 0.1, 0.2, 0.3, 0.7, 0.6, 0.3, 0.1, 0.1, 0.1, 0.2, 0.7, 0.3, 0.1, 0.5, 0.9]
his_r = generate_visitors(2000, p, 'historical')

# Tour user
p = [0.6, 0.1, 0.4, 0.8, 0.6, 0.1, 0.1, 0.5, 0.6, 0.5, 0.7, 0.1, 0.1, 0.1, 0.3, 0.4, 0.4, 0.2, 0.6, 0.9]
tour_r = generate_visitors(2000, p, 'tour')

# Sports user
p = [0.9, 0.5, 0.2, 0.4, 0.1, 0.7, 0.6, 0.1, 0.1, 0.1, 0.2, 0.6, 0.6, 0.6, 0.3, 0.1, 0.3, 0.8, 0.1, 0.4]
sport_r = generate_visitors(2000, p, 'sports')

# Combine all generated users into a dataframe and add to csv
generated_ratings = pd.DataFrame(np.concatenate([generated_ratings.values, walk_r.values, nat_r.values, mus_r.values, his_r.values, tour_r.values, sport_r.values]), columns=generated_ratings.columns)
print(generated_ratings)
add_to_csv(generated_ratings)