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
import json
import re


# Read the channel list from channel_list.csv into a list of dictionaries.
# Each dictionary will have the following keys:
# 'category','channel_url', 'rss_url' ,
with open('channel_list.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    channel_list = list(reader)




#%% Step 1. Populate missing channel IDs and vanity URLs.
# - The vanity url is easy to find by copypasting from the address bar in a browser.
# - The channel_id is what I really need and is what I have for an existing list of channels,
#   but is a random jumble of letters and numbers that means nothing to a human.
# I want the channel list to have both, so here I fill in any blanks.

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

def scrape_channel_for_vanity_url(channel_id):
    print("Scraping channel for vanity url: ", channel_id)
    page = requests.get(f'https://www.youtube.com/channel/{channel_id}')

    # One way to find the vanity url is to search for a substring like 
    #   `"vanityChannelUrl":"http://www.youtube.com/@DimeStoreAdventures"`
    # buried inside some json speghetti deep the page's source.
    # A lot of the other places I'd expect to find it actually change to use whatever url you used to get there.
    # And the canonical url actually uses channel_id.
    pattern = re.compile(r'''
        "vanityChannelUrl":"
        (http://www\.youtube\.com/@[^"]+)  # Capture the URL in a group
        "
        ''', re.VERBOSE)
    match = pattern.search(page.text)
    if match:
        return match.group(1)



# Iterate through the channels and scrape for the channel_id if it's missing ('' or None)
for channel in channel_list:
    if channel['channel_id'] in ('', None):
        try:
            channel['channel_id'] = scrape_channel_for_id(channel['channel_url'])
        except:
            print("Failed to scrape channel_id for: ", channel['channel_url'])
    if channel['channel_url'] in ('', None):
        try:
            channel['channel_url'] = scrape_channel_for_vanity_url(channel['channel_id'])
        except:
            print("Failed to scrape channel_url for: ", channel['channel_id'])

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
# If the scrape fails, remove that channel from the list. That way, I can ignore it later.
for channel in channel_list:
    try:
        author, title, video_id, date = get_latest_video_data(channel['channel_id'])
        channel['author'] = author
        channel['title'] = title
        channel['video_id'] = video_id
        channel['date'] = date
        time.sleep(.1)
    except:
        print("Failed to get latest video for: ", channel['channel_url'], "Removing from list.")
        channel_list.remove(channel)




# %% Step 3. Write to a format I can read later.

# First, let's just output the result to a csv file.
with open('latest_videos.csv', 'w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=channel_list[0].keys())
    writer.writeheader()
    writer.writerows(channel_list)



# Next, let's output to json format using the list of dicts:
with open('latest_videos.json', 'w') as jsonfile:
    json.dump(channel_list, jsonfile, indent=4)











# %%
