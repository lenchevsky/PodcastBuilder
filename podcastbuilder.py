import yaml, sys, os
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

# Create Podcast object
podcast_object = Podcast(
       name=CONFIG['podcast_name'],
       description=CONFIG['podcast_description'],
       website=CONFIG['podcast_website'],
       explicit=False,
       image=CONFIG['podcast_image'] 
    )

youtube_pl = Playlist(CONFIG['youtube_play_list'])
podcast = Query()

for link in youtube_pl.parse_links():
    if not db.contains(podcast.link == link):
        podcast_filename = 'podcast_%s' % link[9:]
        video = YouTube('http://youtube.com%s' % link)
        print('Parsing %s at http://youtube.com%s' % (video.title, link))
        video.streams.filter(only_audio=True).all()[0].download(output_path=CONFIG['data_path'], filename=podcast_filename)
        file_local_path =  '%s/%s.mp4' % (CONFIG['data_path'], podcast_filename)
        media_path = "%s/%s.mp4" % (CONFIG['podcast_media_server'],podcast_filename)
        db.insert({'link': link, 'filename': file_local_path})
        podcast_object.add_episode(Episode(title=video.title, media=Media(media_path, os.stat(file_local_path).st_size, type="audio/mpeg")))

# Generating RSS
podcast_object.rss_file('rss.xml',  minimize=True)
    

    
