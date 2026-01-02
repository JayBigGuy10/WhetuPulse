import os
import subprocess
import time
import datetime
import tweepy
import pytz
import re

# Configuration
global STREAM_URL
STREAM_URL = 'https://manifest.googlevideo.com/api/manifest/hls_playlist/'  #'https://manifest.googlevideo.com/api/manifest/hls_playlist/expire/1743142595/ei/Y-rlZ7n0CsLM4t4PhvqboAU/ip/192.107.171.34/id/mhJRzQsLZGg.11/itag/96/source/yt_live_broadcast/requiressl/yes/ratebypass/yes/live/1/sgoap/gir%3Dyes%3Bitag%3D140/sgovp/gir%3Dyes%3Bitag%3D137/rqh/1/hls_chunk_host/rr1---sn-ntqe6n76.googlevideo.com/xpc/EgVo2aDSNQ%3D%3D/playlist_duration/30/manifest_duration/30/bui/AccgBcOKPZN946bTZEQJApa_HVIrV1AI8G2IHpcfRzVHK5XOCnawybLg8aBmupj_pfIpzQmvnE-KJEtc/spc/_S3wKnhLmz2ulz6-sA7_wo8pb62AGD84CKzb6LaxmGzjdSn6_9X8ex6dE-pjSozXRKdhiVI/vprv/1/playlist_type/DVR/initcwndbps/5292500/met/1743120998,/mh/3F/mm/44/mn/sn-ntqe6n76/ms/lva/mv/m/mvi/1/pl/24/rms/lva,lva/dover/11/pacing/0/keepalive/yes/fexp/51355912,51435733/mt/1743120520/sparams/expire,ei,ip,id,itag,source,requiressl,ratebypass,live,sgoap,sgovp,rqh,xpc,playlist_duration,manifest_duration,bui,spc,vprv,playlist_type/sig/AJfQdSswRQIgAOlDMcBu45dmQAeBVi-vTv7jIptacJqZP1i8VPs2wagCIQCExBMyjuU6E2-HZnm9BpAZPdsBkbKnMIxhzgPB0hje7w%3D%3D/lsparams/hls_chunk_host,initcwndbps,met,mh,mm,mn,ms,mv,mvi,pl,rms/lsig/AFVRHeAwRQIhANSNPCxQ9x76dPa0kkM_jog7ZCwswRppMPPeHvc2PGzyAiBE1XsCw1_BsTZ-h7GuexvdntqQOZx0WnonrhGkA6BFWg%3D%3D/playlist/index.m3u8'
STREAM = os.environ.get('STREAM')                                           #'https://www.youtube.com/watch?v=mhJRzQsLZGg'

SNAPSHOT_INTERVAL = int(os.environ.get('SNAPSHOT_INTERVAL'))  # seconds
DAILY_VIDEO_TIME = os.environ.get('DAILY_VIDEO_TIME')    # 8:00 AM Central Time

IMAGE_DIR = os.environ.get('DIR')+"/images"               #'C:/Users/JaydenL/Documents/WhetuPulse/images'
VIDEO_OUTPUT = os.environ.get('DIR')+"/output/video.mp4"  #'C:/Users/JaydenL/Documents/WhetuPulse/output/video.mp4'

TWITTER_CREDENTIALS = {
    'consumer_key': os.environ.get('consumer_key'),
    'consumer_secret': os.environ.get('consumer_secret'),
    'token': os.environ.get('token'),#access key
    'token_secret': os.environ.get('token_secret'),#access secret
    'bearer_token': os.environ.get('bearer_token')
}

central_tz = pytz.timezone(os.environ.get("TZ"))

home_tz = pytz.timezone("Pacific/Auckland")

def capture_snapshot():
    """Captures a snapshot from the live stream."""
    global STREAM_URL

    direct_url = STREAM_URL

    timestamp = datetime.datetime.now(central_tz).strftime('%Y%m%d_%H%M%S')
    image_path = os.path.join(IMAGE_DIR, f'snapshot_{timestamp}.jpg')

    # Capture a frame from the stream
    ffmpeg_command = [
        'ffmpeg',
        '-headers', "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        '-i', direct_url,
        '-frames:v', '1',
        image_path
    ]
    ffmpeg_result = subprocess.run(ffmpeg_command, text=True, capture_output=True)

    if "http error 403 forbidden" in ffmpeg_result.stderr.lower() or "error opening input" in ffmpeg_result.stderr.lower():
        log("FFmpeg stdout: "+ffmpeg_result.stdout)
        log("FFmpeg stderr: "+ffmpeg_result.stderr)
        log("UPDATING STEAM URL")
        update_stream_url()

def update_stream_url():
    """Updates the live stream URL using youtube-dl."""

    global STREAM_URL

    command = [
        'yt-dlp',
        '-g', STREAM
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    
    STREAM_URL = result.stdout.strip()

    log("STREAM: "+STREAM)
    log("STREAM_URL: "+STREAM_URL)

def extract_datetime_from_filename(filename):
    pattern = re.compile(r"snapshot_(\d{8})_(\d{6})\.jpg")
    match = pattern.match(filename)
    if match:
        date_str, time_str = match.groups()
        datetim = datetime.datetime.strptime(date_str + time_str, "%Y%m%d%H%M%S")
        return central_tz.localize(datetim)
    return None

def clear_old_images():
    """Deletes images older than 24 hours."""
    now = datetime.datetime.now(central_tz)
    for filename in os.listdir(IMAGE_DIR):
        file_path = os.path.join(IMAGE_DIR, filename)

            # Extract datetime from filename
        file_datetime = extract_datetime_from_filename(filename)
    
        # Check if file matches the pattern and is older than 24 hours
        if file_datetime is not None and (now - file_datetime).total_seconds() > 86400:
            try:
                os.remove(file_path)
                log(f"Deleted: {filename}")
            except Exception as e:
                log(f"Error deleting {filename}: {e}")

def create_timelapse():
    """Creates a timelapse video from the collected images using a file list instead of glob."""
    list_file = os.path.join(IMAGE_DIR, 'file_list.txt')

    log("Step 1, file list")
    # Step 1: Generate a list of image filenames
    with open(list_file, 'w') as f:
        for filename in sorted(os.listdir(IMAGE_DIR)):  # Sort ensures time order
            if filename.endswith(".jpg"):
                f.write(f"file '{os.path.join(IMAGE_DIR, filename)}'\n")

    # Step 2: Use FFmpeg with the list file
    command = [
        'ffmpeg',
        '-y', #overwrite existing file
        '-f', 'concat',  
        '-safe', '0',     # Allow unsafe paths
        '-i', list_file, # Read from the list file
        '-framerate', '30',
        '-c:v', 'libx264',
        '-pix_fmt', 'yuv420p',
        VIDEO_OUTPUT
    ]

    log("Step 2, ffmpeg")
    ffmpeg_result = subprocess.run(command, text=True, capture_output=True)

    log("FFmpeg stdout: "+ffmpeg_result.stdout)
    log("FFmpeg stderr: "+ffmpeg_result.stderr)


def post_to_twitter():
    """Posts the generated video to Twitter."""
    # Authenticate to Twitter
    auth = tweepy.OAuthHandler(TWITTER_CREDENTIALS['consumer_key'], TWITTER_CREDENTIALS['consumer_secret'])
    auth.set_access_token(
        TWITTER_CREDENTIALS['token'],
        TWITTER_CREDENTIALS['token_secret'],
    )
    # this is the syntax for twitter API 2.0. It uses the client credentials that we created
    newapi = tweepy.Client(
        bearer_token=TWITTER_CREDENTIALS['bearer_token'],
        access_token=TWITTER_CREDENTIALS['token'],
        access_token_secret=TWITTER_CREDENTIALS['token_secret'],
        consumer_key=TWITTER_CREDENTIALS['consumer_key'],
        consumer_secret=TWITTER_CREDENTIALS['consumer_secret'],
    )
    # Create API object using the old twitter APIv1.1
    api = tweepy.API(auth)

    # Get today's date in short format
    today = datetime.datetime.now(central_tz)
    today_short = today.strftime('%b %d')  # 'Feb 01'

    # Get yesterday's date
    yesterday = today - datetime.timedelta(days=1)
    yesterday_short = yesterday.strftime('%b %d')  # 'Jan 31' (for example)

    # Determine whether we have a full set of images. If fewer than 3000 images, mark tweet as incomplete.
    try:
        num_images = sum(1 for f in os.listdir(IMAGE_DIR) if f.lower().endswith('.jpg'))
    except Exception as e:
        log(f"Error counting images: {e}")
        num_images = 0

    prefix = "Incomplete " if num_images < 2500 else ""
    log(f"Number of images: {num_images}. Tweet prefix: '{prefix.strip()}'")

    # If fewer than 3000 images, show the number of images instead of '24 hour'
    if num_images < 2500:
        timespan_text = f"{num_images} image"
    else:
        timespan_text = "24 hour"

    log(f"Timespan text for tweet: {timespan_text}")

    #TODO get this from somewhere dynamic
    sampletweet = f"{prefix} Morning to Morning {timespan_text} timelapse ({yesterday_short} through {today_short}) of the @NASASpaceflight Starbase Live camera at nsf.live/starbase \n\n #SpaceX #Starship"

    # upload the media using the old api
    log("Uploading Media")
    media = api.media_upload(filename=VIDEO_OUTPUT,media_category="tweet_video",additional_owners="1905372596826505218",chunk_size=(5 * 1024 * 1024)) #Chunk size to avoid some funky api limits
    log("Upload Complete, media: "+str(media))
    time.sleep(10)
    log("Posting Tweet")
    # create the tweet using the new api. Mention the image uploaded via the old api
    post_result = newapi.create_tweet(text=sampletweet, media_ids=[media.media_id_string], media_tagged_user_ids=[1905372596826505218])
    # the following line prints the response that you receive from the API. You can save it or process it in anyway u want. I am just printing it.
    log(str(post_result))

    #https://developer.x.com/en/docs/x-api/v1/media/upload-media/uploading-media/media-best-practices

def log(string):
    current_time = datetime.datetime.now(central_tz).strftime('%H:%M')
    log_time = datetime.datetime.now(home_tz).strftime("%Y-%m-%d %H:%M:%S")
    print(log_time,"NZT,", current_time,"CT,",string )

def main():
    """Main function to orchestrate the timelapse creation and posting."""

    while True:
        current_time = datetime.datetime.now(central_tz).strftime('%H:%M')
        
        if current_time == DAILY_VIDEO_TIME:

            log("Clearing Images")
            clear_old_images()
            log("Creating Timelapse")
            create_timelapse()
            log("Posting to Twitter")
            post_to_twitter()

            time.sleep(60)  # Wait a minute to avoid multiple triggers
        else:
            log("Snapshot Capture")
            capture_snapshot()
            time.sleep(SNAPSHOT_INTERVAL)


if __name__ == '__main__':
    while True:
        try:
            main()
        except KeyboardInterrupt:
            log("Stopping")
            break
        except Exception as e:
            log(f"Error: {e}")
        
        log("Restart in 60s")
        time.sleep(60)
        log("Restarting")
