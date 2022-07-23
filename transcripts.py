import sqlite3
from sqlite3 import Error
import youtube_transcript_api
from youtube_transcript_api import YouTubeTranscriptApi
from pytube import YouTube, Channel
import re

conn = None
try:
    conn = sqlite3.connect('mc_transcripts.db')
    print("db connection ok")
except Error as e:
    print (e)

### Configure channel from where it will collect all transcriptions
channel = 'UCN_h_1w3ofp1qMgrwcnaykw'
c = Channel('https://www.youtube.com/channel/'+channel)

for url in c.video_urls:
    yt = YouTube(url)
    print(url)
    if not yt.caption_tracks:
        print("Video %s sem caption" % (url))
        continue

    ## Configure to get langs
    if yt.caption_tracks[0].code == 'a.pt':
        lang_code = 'pt'
    elif yt.caption_tracks[0].code == 'a.en':
        lang_code = 'en'
    else:
        print("Video %s caption found, but not pt or en" % (url))
        continue
    processed = conn.execute("select count(url) from processed where url='"+str(url)+"'")
    for row in processed:
        if row[0] == 0:
            try:
                transcript_list = YouTubeTranscriptApi.list_transcripts(yt.video_id)
                if (transcript_list != None):
                    transcript = YouTubeTranscriptApi.get_transcript(yt.video_id, languages=[lang_code])

                    for line in transcript:
                        print (line)
                        print (yt.title)
                        print (line["text"])
                        print (line["start"])
                        url_time = url + "&t="+str(int(line["start"]))
                        print (url_time)
                        try:
                            conn.execute("insert into transcripts (title, url, description) values ('" + re.sub('[\'\"!@#$&]+','',str(line["text"])) + "','" + str(url_time) + "','" + re.sub('[\'\"!@#$&]+','',str(yt.title)) +"')")
                        except Error as e:
                            print(e)
                    try:
                        conn.execute("insert into processed (url) values ('"+str(url)+"')") 
                    except Error as e:
                        print(e)
                    conn.commit()

            except Error as e:
                print(e)
        else:
            print("video %s already processed" % (url))
print ("Records created successfully")
conn.close()

quit()