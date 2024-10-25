import vimeo
import requests
import urllib.parse
import concurrent.futures
import sys

TOKEN = ''
KEY = ''
SECRET = ''

banner = r"""
                :++++++++++++++++++++++++++++:
            =++++++++++++++++++++++++++++++++=
            :++++++++++++++++++++++++++++++++++++:
            -++++++++++++++++++++++++++++++++++++=
            +++++++++++:...:++++++++:......:++++++
            ++++++++=.......:+++++-.........-+++++
            ++++++=..........=+++-..........:+++++
            +++++=::=-.......:++++++=.......-+++++
            ++++++++++=.......++++++=......:++++++
            +++++++++++:......=+++++......:+++++++
            ++++++++++++......:+++=......:++++++++
            ++++++++++++-......:+-......-+++++++++
            ++++++++++++=.............:+++++++++++
            +++++++++++++-...........-++++++++++++
            ++++++++++++++.........:++++++++++++++
            +++++++++++++++:.....-++++++++++++++++
            -++++++++++++++++++++++++++++++++++++=
            :++++++++++++++++++++++++++++++++++++:
            =++++++++++++++++++++++++++++++++=
                :++++++++++++++++++++++++++++:
 __ __  ____  ___ ___    ___   ___                   ____    ___ ______ 
|  |  ||    ||   |   |  /  _] /   \                 /    |  /  _]      |
|  |  | |  | | _   _ | /  [_ |     |     _____     |   __| /  [_|      |
|  |  | |  | |  \_/  ||    _]|  O  |    |     |    |  |  ||    _]_|  |_|
|  :  | |  | |   |   ||   [_ |     |    |_____|    |  |_ ||   [_  |  |  
 \   /  |  | |   |   ||     ||     |               |     ||     | |  |  
  \_/  |____||___|___||_____| \___/                |___,_||_____| |__|  
                                                                        
    """



print(banner)

client = vimeo.VimeoClient(
    token=TOKEN,
    key=KEY,
    secret=SECRET
)

if len(sys.argv) < 2 or not sys.argv[1]:
    print(f"[x] Usage: python vimeo-get.py [user_channel_link] ")
    sys.exit(1) 
username = sys.argv[1].split('/')[-1]

url_user_profile = f"https://api.vimeo.com/users/{username}/videos?per_page=100"
video_links = []
failed_videos = []

print(f"[*] Accesing videos...")
while url_user_profile:
    response = client.get(url_user_profile)

    if response.status_code == 200:
        data = response.json()
        for video in data['data']:
            link = video['link']
            video_links.append(link)

        if 'next' in data['paging']:
            url_user_profile = data['paging']['next']
        else:
            url_user_profile = None
    else:
        print(f"[x] Error in video downloads: {response.status_code}")
        break

print(f"[*] Video links: {str(video_links)}", flush=True)
def download_video(video, vid_counter):
    print(f"[*] Fetching video: {video}")
    url_get_video_creds = 'https://vidburner.com/wp-json/aio-dl/video-data/'
    data = {'url': video}

    headers = {
        'Host': 'vidburner.com',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Content-Length': str(len(f'url={video}'))
    }

    response1 = requests.post(url_get_video_creds, data=data, headers=headers)

    url_get_dowload_video = response1.json()["medias"][-1]["url"]
    title = response1.json()["title"]

    response2 = requests.get(url_get_dowload_video)

    with open(f'{title}.mp4', 'wb') as f:
        f.write(response2.content)
        if len(response2.content) < 43 * 1024:
            print(f"[x] Failed to download video: {video}\n", flush=True)
            failed_videos.append(video)
        else:
            print(f"[+] Downloaded video: {title}\n     Link: {video}\n", flush=True)


# Usar ThreadPoolExecutor para descargar videos concurrentemente
with concurrent.futures.ThreadPoolExecutor() as executor:
    futures = [executor.submit(download_video, video, vid_counter) 
               for vid_counter, video in enumerate(video_links, start=1)]
print("[+] DOWNLOAD FINISHED", flush=True)