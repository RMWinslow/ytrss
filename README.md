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
: Deprecated. Currently set equal to `topic` in the output for backwards
  compatibility with the existing HTML viewer. Will be removed once the
  new tag-based viewer is deployed.

`topic`
: What the channel is about. One value from the topic vocabulary below.
  Can be left blank if no topic fits cleanly.

`style`
: How the content is presented. One value from the style vocabulary below.
  Can be left blank.

`favorite`
: Set to `favorite` for top-tier channels. Left blank otherwise.

`channel_url`
: The channel's vanity URL (e.g. `http://www.youtube.com/@SomeChannel`).
  Can be left blank if `channel_id` is provided; the script will attempt to
  scrape for it.

`channel_id`
: The YouTube channel ID (e.g. `UCxyz...`). Can be left blank if `channel_url`
  is provided; the script will attempt to scrape for it.

### Tag vocabulary

These are the allowed values for `topic` and `style`. A validation script can
report rows with non-standard values for review.

**Topics:**

- `math`
- `physical science`
- `animals and biology`
- `food`
- `media / pop culture`
- `fans`
- `tech`
- `making things`
- `toys and games`
- `comedy`
- `original animation`
- `history / geography`
- `social science`

**Styles:**

- `walkabout` — presenter out in the world, exploring places or things in person
- `talking head` — presenter directly addressing the camera, with cutaways, graphics, or interviews
- `show and tell` — centered on showing a specific object and talking about it
- `chaotic` — wacky, destructive, or comedic experimentation
- `slice of life` — passive observation, no particular thesis or message
- `musical` — music performance or music-driven content
- `review` — evaluating pros and cons to help the viewer decide on something

### latest_videos.csv / .json (generated, do not edit)

These are generated artifacts produced by `update_feed.py`. They contain one
row per active channel with the latest video's metadata. The JSON is consumed
by the HTML viewer at runtime.

| Column | Description |
|--------|-------------|
| `channel_url` | Copied from `channel_list.csv`. |
| `channel_id` | Copied from `channel_list.csv`. |
| `author` | Channel name as reported by the RSS feed. |
| `title` | Title of the latest video. |
| `video_id` | YouTube video ID. |
| `date` | Publish date in ISO 8601 format. |
| `tags` | List of tags flattened from `topic`, `style`, and `favorite`. Array in JSON, semicolon-separated in CSV. |
| `category` | Equal to `topic`. Backwards compatibility, to be deprecated. |

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
