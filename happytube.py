# Importera nödvändiga bibliotek
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime, timezone
import time
import json

# Ange din API-nyckel och en lista med kanal-id:n att övervaka
api_key = "DIN_API_NYCKEL_HÄR"
channel_ids = ["KANAL_ID_1", "KANAL_ID_2", "KANAL_ID_3"]

# Skapa ett anslutningsobjekt för YouTube API med API-nyckeln
youtube = build('youtube', 'v3', developerKey=api_key)

# Läs senaste videoid:t för varje kanal från filen "latest_videos.json" (om filen finns)
try:
    with open('latest_videos.json', 'r') as f:
        latest_videos = json.load(f)
except FileNotFoundError:
    latest_videos = {channel_id: {'video_id': None, 'published_at': None} for channel_id in channel_ids}

# Loopa över kanalerna och hämta nya videor var 15:e sekund
while True:
    for channel_id in channel_ids:
        try:
            video_search = youtube.search().list(channelId=channel_id, type='video', part='id,snippet', maxResults=1).execute()
            if video_search['items']:
                video_id = video_search['items'][0]['id']['videoId']
                video_published_at = video_search['items'][0]['snippet']['publishedAt']
                video_datetime = datetime.fromisoformat(video_published_at.replace('Z', '+00:00'))
                now_datetime = datetime.now(timezone.utc)
                elapsed_time = now_datetime - video_datetime
                if latest_videos[channel_id]['video_id'] != video_id and elapsed_time.days == 0 and elapsed_time.seconds < 82800:
                    latest_videos[channel_id]['video_id'] = video_id
                    latest_videos[channel_id]['published_at'] = video_published_at
                    video_url = f"https://www.youtube.com/watch?v={video_id}"
                    channel_search = youtube.channels().list(id=channel_id, part='snippet').execute()
                    channel_title = channel_search['items'][0]['snippet']['title']
                    print(f"Den senaste videon från {channel_title} ({video_published_at}):")
                    print(video_url)
        except HttpError as error:
            print(f"Ett HTTP-fel uppstod: {error}")
        except Exception as error:
            print(f"Ett fel uppstod: {error}")

    # Skriv senaste videoid:t och publiceringsdatum för varje kanal till filen "latest_videos.json"
    with open('latest_videos.json', 'w') as f:
        json.dump(latest_videos, f)

    # Vänta 15 sekunder innan nästa iteration av loopen
    time.sleep(15)
