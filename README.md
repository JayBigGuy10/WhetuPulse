# NOTES

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

Starbase Pulse
The Starbase Pulse bot watches NASA Spaceflight‘s incredible Starbase Live feed and generates a 24-hour timelapse that becomes a fun way to check the pulse of Boca Chica by compressing a day of spacecraft construction and testing down to a couple minutes.

From sunrise to sunrise, you can see the frantic activity that NSF’s team of hard working folks have been documenting day in and out.

How it works
deltaYeet’s servers watch the stream using ffmpeg and save a snapshot every 30 seconds via a cron job.

Every 30 minutes, they update the URL for the stream (which changes periodically) to keep it live using youtube-dl.

Every few hours, a maintenance script clears out pictures more than 24 hours old after The Incident where the @StarbasePulse took down all of the deltaYeet bots by using up all of the server’s disk space. In my defense, I forgot hard drives were finite.

At 8:00 AM Central, a render script uses a different part of ffmpeg (is there anything it can’t do?) to take the ~2,880 images and compile them together as a 30fps MP4.

It passes it to a posting function that uses abraham/twitteroauth to post it to twitter on the @StarbasePulse feed and then the cycle of life continues.

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