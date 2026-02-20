# What does WhetuPulse Do?

The bot watches NASA Spaceflight‘s Starbase Live feed and generates a 24-hour timelapse at 30 second intervals

At 8:00 AM Central, a render script uses a different part of ffmpeg (is there anything it can’t do?) to take the ~2,880 images and compile them together as a 30fps MP4 which is then posed to twitter

# NOTES

rename env example to env

https://ilo.so/twitter-id/

https://docs.tweepy.org/en/v3.7.0/api.html

https://gist.githubusercontent.com/ultimatenyx/440b0bb2cd57769d0fb9ec238c6cd698/raw/fea95eb9486bb00814bb27a9c1e2954eb6f2655b/tweeter.py

https://developer.x.com/en/docs/x-api/v1/media/upload-media/uploading-media/media-best-practices

https://devcommunity.x.com/t/your-media-ids-are-invalid/172839

https://x.com/WhetuPulse

https://maoridictionary.co.nz/search?&keywords=whet%C5%AB

https://docs.x.com/resources/fundamentals/authentication/basic-auth

https://github.com/xdevplatform/Twitter-API-v2-sample-code/blob/main/Manage-Tweets/create_tweet.py

https://github.com/xdevplatform/Twitter-API-v2-sample-code/blob/main/Media%20Upload/media_upload_v2.py#L14

https://developer.x.com/en/portal/projects/1905374216821850112/apps/30467958/keys

https://developer.x.com/en/docs/tutorials/how-to-create-a-twitter-bot-with-twitter-api-v2

https://github.com/yt-dlp/yt-dlp

https://deltayeet.net/?page_id=25


https://developer.x.com/en/docs/x-api/v1/media/upload-media/uploading-media/media-best-practices

args
    ARG STREAM
    ARG consumer_key
    ARG consumer_secret
    ARG token
    ARG token_secret
    ARG bearer_token

    ENV consumer_key=$consumer_key
    ENV consumer_secret=$consumer_secret
    ENV token=$token
    ENV token_secret=$token_secret
    ENV bearer_token=$bearer_token

Windows
> docker build -t whetupulse .

> docker run -d -v C:\docker\whetupulse\data\output:/srv/whetupulse/output -v C:\docker\whetupulse\data\images:/srv/whetupulse/images  --env-file .env --name=whetupulse whetupulse


Dev
> .\ffmpeg -headers "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36" -i direct_url -frames:v 1 image_path