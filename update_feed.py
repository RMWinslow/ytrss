'''
This script reads channel_list.csv and uses the information therein to do the following tasks:

1. For any channel with a missing channel_id, this script scrapes the youtube page for that channel to find the rss id.

This is the most likely part of the script to break, 
(and will likely break if the url or page structure of youtube changes)
but this only needs to run when new channels are added.
The purpose of this is to save time when adding channels.
The channel url is plainly visible; the channel id takes some inspection.

2. For every channel in the list, this script gets the rss feed and reads the information for the latest video.
(I only want the latest video from each channel.)

3. The info tuples for these videos is written into a format I can read later.
(I don't sort them. Order matches order from input channel_list.csv.)
'''


#%%
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import csv
import time


# Read the channel list from channel_list.csv into a list of dictionaries.
# Each dictionary will have the following keys:
# 'category','channel_url', 'rss_url' ,
with open('channel_list.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    channel_list = list(reader)




#%% Step 1. Populate missing channel IDs.

def scrape_channel_for_id(channel_url):
    print("Scraping channel for id: ", channel_url)

    #load the html for the url
    page = requests.get(channel_url)

    #Find the channel_id
    #It's the last part of a url within a meta tag that looks like the following:
    #<meta property="og:url" content="https://www.youtube.com/channel/UCfBAKxelvdN2XDFBcofx7Dg">
    # There are a few other places it can be found on the page, but this is the easiest to parse, I think.
    soup = BeautifulSoup(page.content, 'html.parser')
    channel_id = soup.find('meta', property='og:url')['content'].split('/')[-1]
    return channel_id

# Iterate through the channels and scrape for the channel_id if it's missing ('' or None)
for channel in channel_list:
    if channel['channel_id'] in ('', None):
        channel['channel_id'] = scrape_channel_for_id(channel['channel_url'])

# Now overwrite the channel_list.csv with the updated channel_list
with open('channel_list.csv', 'w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=channel_list[0].keys())
    writer.writeheader()
    writer.writerows(channel_list)



# %% Step 2. Get the RSS feed for a channel and read the latest video.
# The RSS feed is at https://www.youtube.com/feeds/videos.xml?channel_id=CHANNEL_ID
# For example,  https://www.youtube.com/feeds/videos.xml?channel_id=UCfBAKxelvdN2XDFBcofx7Dg

def get_latest_video_data(channel_id):
    rss_url = f'https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}'
    print("Getting latest video from: ", rss_url)

    #load the xml for the url
    page = requests.get(rss_url)

    #Find the latest video
    soup = BeautifulSoup(page.content, 'xml')
    entry = soup.find('entry')
    title = entry.find('title').text
    video_id = entry.find('videoId').text
    date = entry.find('published').text
    author = entry.find('author').find('name').text
    return (author, title, video_id, date)


# Iterate through the channels and get the latest video info for each.
# Push between each channel to avoid getting rate limiting.
# (I don't think I'll run into issues accessing youtube's rss feeds this way, but better safe than sorry.)
for channel in channel_list:
    author, title, video_id, date = get_latest_video_data(channel['channel_id'])
    channel['author'] = author
    channel['title'] = title
    channel['video_id'] = video_id
    channel['date'] = date
    time.sleep(.1)



# %% Step 3. Write to a format I can read later.

# First, let's just output the result to a csv file.
with open('latest_videos.csv', 'w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=channel_list[0].keys())
    writer.writeheader()
    writer.writerows(channel_list)



# Now let's generate a cute litlte html file with the videos embedded.
# TODO: I need to come back here and figure out the best way to make this work with my blog.
# TODO: Link to fullscreen embed instead of embedding in the page. EG: https://www.youtube.com/embed/YvIMIUYju1w

timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

html = '<html><head></head><body>'
for channel in channel_list:
    html += f'<div class="video"><h2>{channel['title']}</h2><p>{channel['author']} - {channel['date']}</p><iframe width="560" height="315" src="https://www.youtube.com/embed/{channel['video_id']}"></iframe></div>'
html += f'<p>Generated on: {timestamp}</p></body></html>'
with open('latest_videos.html', 'w') as htmlfile:
    htmlfile.write(html)







# %%
