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

3. The info tuples for these videos are sorted by category and upload date,
and the sorted list is written into a csv or json file to read later.
'''


#%%
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import csv

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



    




# %% Step 3. Sort the videos by category and upload date, and write to a csv or json file.

