import os
import subprocess
import time
import datetime
import threading
import tweepy
import pytz
import re
from pathlib import Path

# Configuration
STREAM = os.environ.get('STREAM')                               # 'https://www.youtube.com/watch?v=mhJRzQsLZGg'
SNAPSHOT_INTERVAL = int(os.environ.get('SNAPSHOT_INTERVAL'))    # seconds
DAILY_VIDEO_TIME = os.environ.get('DAILY_VIDEO_TIME')           # 8:00 AM Central Time
DIR = Path(os.environ.get('DIR'))
IMAGE_DIR = str(DIR / "data/images")                            # 'C:/Users/JaydenL/Documents/WhetuPulse/data/images'
VIDEO_OUTPUT = str(DIR / "data/video.mp4")                      # 'C:/Users/JaydenL/Documents/WhetuPulse/data/video.mp4'
LIST_FILE = str(DIR / 'data/file_list.txt')
TWITTER_CREDENTIALS = {
    'consumer_key': os.environ.get('consumer_key'),
    'consumer_secret': os.environ.get('consumer_secret'),
    'token': os.environ.get('token'),                           #access key
    'token_secret': os.environ.get('token_secret'),             #access secret
    'bearer_token': os.environ.get('bearer_token')
}

central_tz = pytz.timezone(os.environ.get("TZ"))
home_tz = pytz.timezone("Pacific/Auckland")

def format_short(dt):
        hour = dt.strftime('%I').lstrip('0')
        ampm = dt.strftime('%p').lower()
        return f"{dt.strftime('%b %d')} {hour}{ampm}"

def extract_datetime_from_filename(filename):
    pattern = re.compile(r"snapshot_(\d{8})_(\d{6})\.jpg")
    match = pattern.match(filename)
    if match:
        date_str, time_str = match.groups()
        datetim = datetime.datetime.strptime(date_str + time_str, "%Y%m%d%H%M%S")
        return central_tz.localize(datetim)
    return None

def log(string):
    current_time = datetime.datetime.now(central_tz).strftime('%H:%M')
    log_time = datetime.datetime.now(home_tz).strftime("%Y-%m-%d %H:%M:%S")
    print(log_time,"NZT,", current_time,"CT,",string)

def get_stream_url(stream):
    """Updates the live stream URL using youtube-dl."""

    log("Getting stream url for: "+stream)

    command = [
        'ssh', 'linux-labs', '-o', 'StrictHostKeyChecking=no', f'./yt-dlp/yt-dlp -g {stream}'
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    
    result_string = result.stdout.strip()

    if "manifest.googlevideo.com" not in result_string:
        log("Got BAD url: "+result.stdout+" "+result.stderr)
        return ""
    else:
        log("Got GOOD url: "+ result_string)
        return result_string

def capture_snapshot(stream_url):
    """Captures a snapshot from the live stream."""

    timestamp = datetime.datetime.now(central_tz).strftime('%Y%m%d_%H%M%S')
    image_path = os.path.join(IMAGE_DIR, f'snapshot_{timestamp}.jpg')

    # Capture a frame from the stream
    ffmpeg_command = [
        'ffmpeg',
        '-headers', "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        '-i', stream_url,
        '-frames:v', '1',
        image_path
    ]
    ffmpeg_result = subprocess.run(ffmpeg_command, text=True, capture_output=True)

    if "http error 403 forbidden" in ffmpeg_result.stderr.lower() or "error opening input" in ffmpeg_result.stderr.lower():
        log("FFmpeg stdout: "+ffmpeg_result.stdout)
        log("FFmpeg stderr: "+ffmpeg_result.stderr)
        raise Exception("CANT_OPEN_URL")

def create_timelapse():
    """Creates a timelapse video from the collected images using a file list"""

    # Step 1: Generate a list of image filenames
    log("Timelapse: Listing Files")
    sorted_images = sorted(f for f in os.listdir(IMAGE_DIR) if f.lower().endswith('.jpg'))
    if len(sorted_images) == 0:
        log("No images found to timelapse, aborting")
        return
    with open(LIST_FILE, 'w') as f:
        for filename in sorted_images:  # Sort ensures time order
            f.write(f"file '{os.path.join(IMAGE_DIR, filename)}'\n")

    # Step 2: Use FFmpeg to join all of the images named in the file together
    log("Timelapse: Running FFmpeg")
    command = [
        'ffmpeg',
        '-y', #overwrite existing file
        '-f', 'concat',  
        '-safe', '0',     # Allow unsafe paths
        '-i', LIST_FILE, # Read from the list file
        '-framerate', '30',
        '-c:v', 'libx264',
        '-pix_fmt', 'yuv420p',
        VIDEO_OUTPUT
    ]
    ffmpeg_result = subprocess.run(command, text=True, capture_output=True)
    log("FFmpeg stdout: "+ffmpeg_result.stdout)
    log("FFmpeg stderr: "+ffmpeg_result.stderr)

    # Step 3: Create Tweet String
    if sorted_images:
        # Extract dates from first and last image filenames
        previous_dt = extract_datetime_from_filename(sorted_images[0])
        current_dt = extract_datetime_from_filename(sorted_images[-1])
    else:
        # Get today's and yesterdays date
        current_dt = datetime.datetime.now(central_tz)
        previous_dt = current_dt - datetime.timedelta(days=1)

    # Format the dates
    yesterday_short = format_short(previous_dt)
    today_short = format_short(current_dt)
        
    # Determine whether we have a full set of images.
    num_images = len(sorted_images)
    log(f"Number of images: {num_images}")

    if num_images < 2500:
        tweet_text = f"🚀 {yesterday_short} through {today_short} timelapse of Starbase Live \n\n nsf.live/starbase @NASASpaceflight #SpaceX #Starship {num_images}"
    else:
        tweet_text = f"📸 {yesterday_short} through {today_short} timelapse of Starbase Live \n\n nsf.live/starbase @NASASpaceflight #SpaceX #Starship"    

    # Step 4: Authenticate to Twitter and make the post
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
    # upload the media using the old api
    log("Uploading Media")
    media = api.media_upload(filename=VIDEO_OUTPUT,media_category="tweet_video",additional_owners="1905372596826505218",chunk_size=(5 * 1024 * 1024)) #Chunk size to avoid some funky api limits
    log("Upload Complete, media: "+str(media))
    time.sleep(10)
    log("Posting Tweet: "+tweet_text)
    # create the tweet using the new api. Mention the image uploaded via the old api
    post_result = newapi.create_tweet(text=tweet_text, media_ids=[media.media_id_string], media_tagged_user_ids=[1905372596826505218])
    # the following line prints the response that you receive from the API. You can save it or process it in anyway u want. I am just printing it.
    log(str(post_result))

    # Step 5: nuke the files used to make the video
    log("Deleting "+str(len(sorted_images))+" images")
    for filename in sorted_images:
        file_path = os.path.join(IMAGE_DIR, filename)
        try:
            os.remove(file_path)
        except Exception as e:
            log(f"Error deleting {filename}: {e}")

def get_stream_url_with_backoff():
    """Calls get_stream_url with exponential backoff until a valid URL is returned."""
    delay = 5
    max_delay = 1800 # 30 minutes
    while True:
        stream_url = get_stream_url(stream=STREAM)
        if stream_url:
            return stream_url
        log(f"Stream URL empty, retrying in {delay}s")
        time.sleep(delay)
        delay = min(delay * 2, max_delay)

def snapshot_loop():
    """Continuously captures snapshots in a background thread."""
    stream_url = get_stream_url_with_backoff()
    while True:
        log("Snapshot Capture")
        try:
            capture_snapshot(stream_url)
        except Exception as e:
            if str(e) == "CANT_OPEN_URL":
                stream_url = get_stream_url_with_backoff()
        time.sleep(SNAPSHOT_INTERVAL)

def main():
    """Main function to orchestrate the timelapse creation and posting."""

    # Start snapshot capture in a background thread
    snapshot_thread = threading.Thread(target=snapshot_loop, daemon=True)
    snapshot_thread.start()

    while True:
        current_time = datetime.datetime.now(central_tz).strftime('%H:%M')

        if current_time == DAILY_VIDEO_TIME:
            log("Creating Timelapse")
            create_timelapse()
            time.sleep(65)  # Wait a minute to avoid multiple triggers
        else:
            time.sleep(1)

if __name__ == '__main__':
    log("Starting")

    commands = [
        ["chmod", "700", "/root/.ssh"],  # the .ssh directory
        ["chmod", "600", "/root/.ssh/id_rsa", "/root/.ssh/id_ed25519"],  # private keys
        ["chmod", "600", "/root/.ssh/config"],  # ssh config
        ["chmod", "644", "/root/.ssh/known_hosts"],  # known hosts
    ]

    for cmd in commands:
        try:
            subprocess.run(cmd, check=True)
            print(f"Ran: {' '.join(cmd)}")
        except subprocess.CalledProcessError as e:
            print(f"Failed: {' '.join(cmd)}\n{e}")

    while True:
        try:
            main()
        except KeyboardInterrupt:
            log("KeyboardInterrupt: Stopping")
            break
        except Exception as e:
            log(f"Fatal Error: {e}")
        
        log("Restart in 60s")
        time.sleep(60)
        log("Restarting")
