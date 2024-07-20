import subprocess
import sqlite3
from sqlite3 import Error
from youtube_transcript_api import YouTubeTranscriptApi
import yt_dlp
import json
import re



conn = None
try:
    conn = sqlite3.connect('mc_transcripts.db')
    print("db connection ok")
except Error as e:
    print (e)

channel = "https://www.youtube.com/channel/UCN_h_1w3ofp1qMgrwcnaykw"

command = [f"yt-dlp --flat-playlist --print id '{channel}'"]
output_urls = subprocess.run(['yt-dlp', '--flat-playlist', '--print', 'id', f'{channel}'], capture_output=True, text=True)

video_id_list = [line.strip() for line in output_urls.stdout.split('\n')]

count = 0
for video_id in video_id_list:
    count+=1
    # print(f"{count}: https://www.youtube.com/watch?v={url}")
    full_url = f"https://www.youtube.com/watch?v={video_id}"
    processed = conn.execute(f"select count(url) from processed where url='{full_url}'")
    for row in processed:
        if row[0] == 0:
            try:
                ydl_opts = {}
                info = {}
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    full_info = ydl.extract_info(url=full_url, download=False, )
                    info = json.loads(json.dumps(ydl.sanitize_info(full_info)))
                print (f"ID: {video_id} Subtitles: {info.get('subtitles', {})} Languages {info.get('language')}")
                # if (info.get('subtitles', {})) or (info.get('language') is not None and info.get('language') in ["en", "pt", "pt-BR", "en-US"]):
                if (info.get('language') in ["en", "pt", "pt-BR", "en-US"]):
                    # print(json.dumps(ydl.sanitize_info(full_info)))
                    try:
                        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
                        if (transcript_list is not None):
                            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=["en", "pt", "pt-BR", "en-US"])

                            buffer = []
                            first_timestamp = None
                            for i, line in enumerate(transcript):
                                if i % 60 == 0 and buffer:
                                    concatenated_text = " ".join([l["text"] for l in buffer])
                                    url_time = full_url + "&t=" + str(int(first_timestamp))
                                    try:
                                        conn.execute("insert into transcripts (title, url, description) values (?, ?, ?)", 
                                                     (re.sub(r'[\'\"!@#$&]+', '', concatenated_text), url_time, re.sub(r'[\'\"!@#$&]+', '', info['title'])))
                                    except Error as e:
                                        print(e)
                                    buffer = []
                                    # print(info['title'])
                                    # print(url_time)
                                    # print(concatenated_text)
                                
                                if not buffer:
                                    first_timestamp = line["start"]
                                
                                buffer.append(line)
                            
                            if buffer:
                                concatenated_text = " ".join([l["text"] for l in buffer])
                                url_time = full_url + "&t=" + str(int(first_timestamp))
                                try:
                                    conn.execute("insert into transcripts (title, url, description) values (?, ?, ?)", 
                                                 (re.sub(r'[\'\"!@#$&]+', '', concatenated_text), url_time, re.sub(r'[\'\"!@#$&]+', '', info['title'])))
                                except Error as e:
                                    print(e)
                                # print(info['title'])
                                # print(url_time)
                                # print(concatenated_text)

                            try:
                                conn.execute("insert into processed (url) values (?)", (full_url,))
                            except Error as e:
                                print(e)
                            conn.commit()
                    except Error as e:
                        print(e)

            except Error as e:
                print(e)
        # else:
        #     print("video %s already processed" % (full_url))

print ("Records created successfully")
conn.close()

quit()