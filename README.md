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
  (status, category,                      (one per channel)
   channel_url, channel_id)                     |
        |                                       |
        |   .----- update_feed.py  ----------.  |
        |   |                                |  |
        |   |  Step 1                        |  |
        |   |  For active channels, fill in  |  |
        |   |  missing channel_ids by        |  |
        |   |  scraping YouTube pages.       |  |
        |   |  Write updates back to         |  |
        |   |  channel_list.csv.             |  |
        |   |                                |  |
        |   |  Step 2                        |  |
        |   |  For each active channel,      |  |
        |   |  fetch the RSS feed and        |  |
        |   |  extract the latest video's    |  |
        |   |  title, id, author, and        |  |
        |   |  publish date.                 |  |
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

### channel_list.csv (edit this)

This is the file to edit when adding, removing, or reorganizing channels.
The script reads it as input and may write back to fill in missing IDs,
but it is primarily a human-maintained artifact.

`status`
: Only channels with the value `active` are fetched and included in the feed.
  Any other value (e.g. `hidden`, `pending`, `test`) causes the channel to be
  skipped. Use the value as a free-text note for why the channel is inactive.

`category`
: The display category used to group videos in the HTML viewer.

`channel_url`
: The channel's vanity URL (e.g. `http://www.youtube.com/@SomeChannel`).
  Can be left blank if `channel_id` is provided; the script will attempt to
  scrape for it.

`channel_id`
: The YouTube channel ID (e.g. `UCxyz...`). Can be left blank if `channel_url`
  is provided; the script will attempt to scrape for it.

### latest_videos.csv / .json (generated, do not edit)

These are generated artifacts produced by `update_feed.py`. They contain one
row per active channel with the latest video's metadata. The JSON is consumed
by the HTML viewer at runtime.

| Column | Description |
|--------|-------------|
| `category` | Copied from `channel_list.csv`. |
| `channel_url` | Copied from `channel_list.csv`. |
| `channel_id` | Copied from `channel_list.csv`. |
| `author` | Channel name as reported by the RSS feed. |
| `title` | Title of the latest video. |
| `video_id` | YouTube video ID. |
| `date` | Publish date in ISO 8601 format. |

### Scripts

| File | What it does |
|------|--------------|
| `update_feed.py` | Reads `channel_list.csv`, fills in missing channel IDs by scraping YouTube, fetches each active channel's RSS feed, extracts the latest video, and writes the output files. |

### Automation

The GitHub Actions workflow (`.github/workflows/build.yaml`) runs on a weekly
schedule, executes `update_feed.py`, and commits the updated CSV, JSON, and
channel list back to `main`.


## Adding channels

Add a row to `channel_list.csv` with `active` as the status, a category name,
and the channel's vanity URL (e.g. `http://www.youtube.com/@SomeChannel`).
The `channel_id` column can be left blank — `update_feed.py` will scrape
YouTube to fill it in on the next run.
