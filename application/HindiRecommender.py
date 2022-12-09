import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
from inltk.inltk import setup
from inltk.inltk import tokenize
from collections import Counter
import pandas as pd
import re
from langdetect import detect
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from collections import Counter
import seaborn as sns
import os

sns.set(rc={'figure.figsize':(10,7)})
pd.set_option('max_colwidth', 400)

df = pd.read_csv(os.path.join(os.getcwd(), 'data/hindi_data.csv'))
df = df.drop_duplicates(subset='artist', keep='first')
df = df.reset_index(level=0)
df['id'] = df['index']
df = df.drop(['index'], axis=1)

# Calculating cosine similarities from lyrics and storing similar song results in results dict
tf = TfidfVectorizer(analyzer='word', min_df=0, max_features= 100 , lowercase=True)
tfidf_matrix = tf.fit_transform(df['lyrics'])

cosine_similarities = linear_kernel(tfidf_matrix, tfidf_matrix)
results = {}

for idx, row in df.iterrows():
    similar_indices = cosine_similarities[idx].argsort()[:-100:-1]
    similar_items = [(cosine_similarities[idx][i], df['id'][i]) for i in similar_indices]
    results[row['id']] = similar_items[1:]


def item(id):
    return df.loc[df['id'] == id]['Song name']

def recommend(id, num):
    print("Recommending " + str(num) + " songs similar to " + item(id))
    recs = results[id][:num]
    i=0
    for rec in recs:
        print("We recommend : " + item(rec[1]) + " (score:" + str(rec[0]) + ")")