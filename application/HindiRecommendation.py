# helper class to send the argument to context

class HindiRecommendation:
    def __init__(self, artist, title, language = "hindi", album_image_url = "", recommendations = {}):
        self.artist = artist
        self.song_title = title
        self.language = language
        self.recommendations = recommendations
        self.album_image_url = album_image_url

    def get_recommendations(self):
        return self.recommendations
    def get_artist(self):
        return self.artist
    def get_song_title(self):
        return self.song_title
    def get_language(self):
        return self.language
    def get_album_image_url(self):
        return self.album_image_url
    
