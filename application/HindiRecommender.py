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
import requests
import json
import spotipy

from spotipy.oauth2 import SpotifyClientCredentials # Recommendation Generator
from .HindiRecommendation import *

class HindiRecommender:
    def __init__(self):
        sns.set(rc={'figure.figsize':(10,7)})
        pd.set_option('max_colwidth', 400)
        self.df = pd.read_csv(os.path.join(os.getcwd(), 'data/transliterated_data.csv'))
        self.df.drop(['Unnamed: 0'] , axis = 1, inplace = True)
        self.df.drop(['level_0'] , axis = 1, inplace = True)
        print(self.df.columns)
        self.df = self.df.drop_duplicates(subset='artist', keep='first')
        self.df = self.df.reset_index(level=0)
        self.df.rename(columns = {'Song name'  : 'song_name'}, inplace = True)

        self.train()

    # Calculating cosine similarities from lyrics and storing similar song results in results dict

    def train(self):
        self.tf = TfidfVectorizer(analyzer='word', min_df=0, max_features= 100 , lowercase=True)
        self.tfidf_matrix = self.tf.fit_transform(self.df['lyrics'])

        self.cosine_similarities = linear_kernel(self.tfidf_matrix, self.tfidf_matrix)
        self.results = {}

        for idx, row in self.df.iterrows():
            similar_indices = self.cosine_similarities[idx].argsort()[:-100:-1]
            similar_items = [(self.cosine_similarities[idx][i], self.df['id'][i]) for i in similar_indices]
            self.results[row['id']] = similar_items[1:]



    def item(self,id):
        return self.df.loc[self.df['id'] == id]['song_name']
        
    def get_musixmatch_api_url(self, url):
            return 'http://api.musixmatch.com/ws/1.1/{}&format=json&apikey={}'.format(url, \
            os.getenv("MUSIX_API_KEY"))
    def find_track_info(self, artist, title):
        url = 'matcher.track.get?q_track={}&q_artist={}'.format(title,artist)
        matched_res = requests.get(self.get_musixmatch_api_url(url))
        matched_data = json.loads(matched_res.text)

        if matched_data["message"]["header"]["status_code"] == 200:
            #Get initial Musixmatch information
            print(matched_data["message"]["body"])
            artist = matched_data["message"]["body"]["track"]["artist_name"]
            title = matched_data["message"]["body"]["track"]["track_name"]
            track_id = matched_data["message"]["body"]["track"]["track_id"]

            #Access Spotify API
            client_credentials_manager = SpotifyClientCredentials(\
            client_id=os.getenv("SPOTIFY_CLIENT_ID"), \
            client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"))
            spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

            #Get album art and a preview url from Spotify  
            results = spotify.search(q='id:'+str(track_id))
            out = {"artist" : artist, "name" : title, "spotify_id" : track_id}
            print(out)
            try:
                track = results['tracks']['items'][0]

                out["image_url"] = track["album"]["images"][1]["url"]
                out["preview_url"] = track["preview_url"]
                out["spotify_id"] = track['external_urls']['spotify']
                return out
            except Exception as e:
                print("Error : ", e)
                return False

    def recommend(self, artist, song_name, num):
        # filter df to find id of the song with name and artist
        song = self.df.query('song_name == @song_name and artist == @artist')
        # if doesnt exist, return False for now TODO : change this..
        # if exists, return the recommendations
        if(not song.empty):
            id = song['id']
            id = id.item()
            recs = self.results[id][:num]
            i=0
            newHindiRecommendation = HindiRecommendation(artist, song_name)
            trackInfo = self.find_track_info(artist, song_name)
            print("Track info  : " ,trackInfo)
            if(trackInfo):
                newHindiRecommendation.album_image_url = trackInfo["image_url"]
            else:
                newHindiRecommendation.album_image_url = "https://i.imgur.com/8QZQY4r.png"
            recommendations = []
            for rec in recs:
                track = self.df.query('id==@rec[1]')
                artist = str(track["artist"].values[0]) 
                track =str(track["song_name"].values[0])
                newRecommendation = self.find_track_info(artist, track)
                if(newRecommendation):
                    recommendations.append(newRecommendation)
                else:
                    continue
            newHindiRecommendation.recommendations = recommendations

            return(newHindiRecommendation)
        else:
            print("Song not found")
            False

    
    def addRow(self, song_name, type, artist, lyrics):
        id = len(self.df['id'])
        newRow = [0,song_name, type, artist, lyrics, id]
        print(len(self.df.loc[len(self.df['id']) - 1]))
        # add the new song data to the df
        self.df.loc[len(self.df['id'])] = newRow
        #train again
        self.train()