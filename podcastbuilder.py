import yaml, sys, os
from urllib.error import HTTPError
from pytube import YouTube, Playlist
from tinydb import TinyDB, Query
from podgen import Podcast, Episode, Media

# Loading configuration from config.yaml
print('Loading configuration...')
try:
        with open('config.yml', 'r') as stream:
                CONFIG = yaml.load(stream)

except Exception as exc:
        print('Cannot load configuration: %s' % str(exc))
        sys.exit(1)

# Loading database
db = TinyDB('podcastdb.json')

# Parse YouTube Playlist and download mp4 files
youtube_pl = Playlist(CONFIG['youtube_play_list'])
podcast = Query()

for link in youtube_pl.parse_links():
    if not db.contains(podcast.link == link):
        try:
            podcast_filename = 'podcast_%s' % link[9:]
            video = YouTube('http://youtube.com%s' % link)
            print('Parsing %s at http://youtube.com%s' % (video.title, link))
            video.streams.filter(only_audio=True).all()[0].download(output_path=CONFIG['data_path'], filename=podcast_filename)
            file_local_path =  '%s/%s.mp4' % (CONFIG['data_path'], podcast_filename)
            db.insert({'link': link, 'filename': file_local_path, 'name': video.title})
        except HTTPError as err:
            print('Can not parse this video bacause of HTTPError.')


# Create Podcast object and fill it with episodes
podcast_object = Podcast(
       name=CONFIG['podcast_name'],
       description=CONFIG['podcast_description'],
       website=CONFIG['podcast_website'],
       explicit=False,
       image=CONFIG['podcast_image'] 
    )

for item in db:
    web_media_path = "%s/podcast_%s.mp4" % (CONFIG['podcast_media_server'],item['link'][9:])
    podcast_object.add_episode(Episode(title=item['name'], media=Media(web_media_path, os.stat(item['filename']).st_size, type="audio/mpeg")))

# Generating RSS
podcast_object.rss_file('rss.xml',  minimize=True)
    

    
