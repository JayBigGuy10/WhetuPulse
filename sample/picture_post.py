import tweepy
# the below import is for calculating date. Not needed for you but I needed it.
from datetime import date

# take these from developer.twitter.com
ACCESS_KEY = ""
ACCESS_SECRET = ""
CONSUMER_KEY = ""
CONSUMER_SECRET = ""
BEARER_TOKEN = ""

# Authenticate to Twitter
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(
    ACCESS_KEY,
    ACCESS_SECRET,
)
# this is the syntax for twitter API 2.0. It uses the client credentials that we created
newapi = tweepy.Client(
    bearer_token=BEARER_TOKEN,
    access_token=ACCESS_KEY,
    access_token_secret=ACCESS_SECRET,
    consumer_key=CONSUMER_KEY,
    consumer_secret=CONSUMER_SECRET,
)

# Create API object using the old twitter APIv1.1
api = tweepy.API(auth)

sampletweet = "Hi"

# upload the media using the old api
media = api.media_upload(filename="C:/Users/JaydenL/Documents/WhetuPulse/output/video3.mp4",media_category="tweet_video",additional_owners="1905372596826505218")
print("media: ",media)
# create the tweet using the new api. Mention the image uploaded via the old api
post_result = newapi.create_tweet(text=sampletweet, media_ids=[media.media_id_string], media_tagged_user_ids=[1905372596826505218])
# the following line prints the response that you receive from the API. You can save it or process it in anyway u want. I am just printing it.
print(post_result)
