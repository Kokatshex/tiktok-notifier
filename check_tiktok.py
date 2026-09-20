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
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/122.0.0.0 Safari/537.36",
        "Referer": "https://www.tikwm.com/",
    }
    r = requests.get(url, params=params, headers=headers, timeout=15)

    if r.status_code != 200:
        print(f"Bad status code: {r.status_code}")
        print(f"Response text: {r.text[:500]}")
        return None

    try:
        data = r.json()
    except requests.exceptions.JSONDecodeError:
        print("Response was not valid JSON. Raw response below:")
        print(r.text[:500])
        return None

    videos = data.get('data', {}).get('videos', [])
    if not videos:
        print(f"No videos found in response: {data}")
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
