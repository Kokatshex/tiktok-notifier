import os
import json
import requests

WEBHOOK_URL = os.environ['DISCORD_WEBHOOK_URL']
TIKTOK_USERNAME = os.environ['TIKTOK_USERNAME']  # no @ symbol
STATE_FILE = 'last_video.json'


def load_last_id():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f).get('last_id')
    return None


def save_last_id(vid):
    with open(STATE_FILE, 'w') as f:
        json.dump({'last_id': vid}, f)


def get_latest_video():
    url = "https://www.tikwm.com/api/user/posts"
    params = {"unique_id": TIKTOK_USERNAME, "count": 1}
    r = requests.get(url, params=params, timeout=15)
    data = r.json()
    videos = data.get('data', {}).get('videos', [])
    if not videos:
        return None
    v = videos[0]
    return {
        'id': v['video_id'],
        'title': v.get('title') or 'New TikTok video',
        'url': f"https://www.tiktok.com/@{TIKTOK_USERNAME}/video/{v['video_id']}"
    }


def send_discord_notification(video):
    payload = {
        "content": f"🎥 New TikTok from **{TIKTOK_USERNAME}**!\n{video['title']}\n{video['url']}"
    }
    requests.post(WEBHOOK_URL, json=payload, timeout=15)


def main():
    last_id = load_last_id()
    video = get_latest_video()
    if video is None:
        print("Could not fetch videos (account may be private or username wrong).")
        return
    if video['id'] != last_id:
        send_discord_notification(video)
        save_last_id(video['id'])
        print(f"Notified Discord: {video['id']}")
    else:
        print("No new video.")


if __name__ == "__main__":
    main()
