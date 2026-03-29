# ytrss

This repo aggregates YouTube RSS feeds into a "one entry per channel" display,
inspired by [RoyalRoad's](https://www.royalroad.com/) subscription feed.
Showing only the latest video per channel prevents prolific uploaders
from drowning out channels that post less frequently.

A GitHub Actions workflow runs `update_feed.py` once per week,
commits the updated outputs, and the HTML page is served via GitHub Pages.

One of the outputs should be viewable at
[RMWinslow.com/ytrss/latest_videos](https://www.RMWinslow.com/ytrss/latest_videos.html)

The canonical viewer is the [YouTube Channels](https://www.RMWinslow.com/youtube) page on the posts site.


## Data files and flow

```
  channel_list.csv                        YouTube RSS Feeds
  (category, channel_url, channel_id)     (one per channel)
        |                                       |
        |   .----- update_feed.py  ----------.  |
        |   |                                |  |
        |   |  Step 1                        |  |
        |   |  Fill in missing channel_ids   |  |
        |   |  by scraping YouTube pages.    |  |
        |   |  Write updates back to         |  |
        |   |  channel_list.csv.             |  |
        |   |                                |  |
        |   |  Step 2                        |  |
        |   |  For each channel, fetch the   |  |
        |   |  RSS feed and extract the      |  |
        |   |  latest video's title, id,     |  |
        |   |  author, and publish date.     |  |
        |   |                                |  |
        |   |  Step 3                        |  |
        |   |  Write the combined data to    |  |
        |   |  output files.                 |  |
        |   '--------------------------------'  |
        |                  |                    |
        v                  v                    v
  channel_list.csv   latest_videos.csv   latest_videos.json
  (updated with      (category,          (same data as CSV,
   filled-in ids)     channel_url,        used by the HTML
                      channel_id,         page at runtime)
                      author, title,            |
                      video_id, date)           |
                                                v
                                         latest_videos.html
                                         (static page with JS
                                          that fetches the JSON,
                                          groups by category,
                                          and sorts by date)
```

### Sheets

| File | Columns | Role |
|------|---------|------|
| `channel_list.csv` | `category`, `channel_url`, `channel_id` | Input list of channels to track. Also written back to by the script when it fills in missing IDs. |
| `latest_videos.csv` | `category`, `channel_url`, `channel_id`, `author`, `title`, `video_id`, `date` | Output. One row per channel with the latest video's metadata. Order matches `channel_list.csv`. |
| `latest_videos.json` | Same fields as CSV | Output. Same data in JSON format, consumed by `latest_videos.html` at runtime. |

### Scripts

| File | What it does |
|------|--------------|
| `update_feed.py` | Reads `channel_list.csv`, fills in missing channel IDs by scraping YouTube, fetches each channel's RSS feed, extracts the latest video, and writes all three output files. |

### Automation

The GitHub Actions workflow (`.github/workflows/build.yaml`) runs on a weekly
schedule, executes `update_feed.py`, and commits the updated CSV, JSON, and
channel list back to `main`.


## Adding channels

Add a row to `channel_list.csv` with the category name and the channel's vanity
URL (e.g. `http://www.youtube.com/@SomeChannel`). The `channel_id` column can be
left blank — `update_feed.py` will scrape YouTube to fill it in on the next run.
