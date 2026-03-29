# ytrss

## Project overview

This repo aggregates YouTube RSS feeds into a "one entry per channel" display, inspired by RoyalRoad's subscription feed. The core insight is that showing only the latest video per channel prevents prolific uploaders from drowning out infrequently-updating channels — a simpler alternative to algorithmic feed curation.

The pipeline runs weekly via GitHub Actions: `update_feed.py` fetches RSS feeds for ~193 channels listed in `channel_list.csv`, extracts the latest video from each, and writes the results to CSV, JSON, and an HTML page served at RMWinslow.com/ytrss/latest_videos.html.

## Design principles

- **Weekly update cadence is intentional.** The feed updates once per week to discourage compulsive refreshing. This is a feature, not a limitation.
- **The user-facing endpoint must be entirely static.** No cookies, no user tracking, no server-side state. Everything the viewer sees comes from static files served via GitHub Pages.
- **Visited-link styling serves as the "watched" indicator.** Browsers natively restyle visited links, which is sufficient for tracking what the user has already clicked.
- **Rarely-updating channels should remain visible.** The whole point is to surface channels that post infrequently. Dead channel detection or cleanup would undermine this goal.

## Key files

- `channel_list.csv` — master list of channels (category, channel_url, channel_id)
- `update_feed.py` — main script: fetches RSS, resolves missing channel IDs, writes outputs
- `latest_videos.csv` / `.json` / `.html` — auto-generated outputs (committed by GitHub Actions)
- `.github/workflows/build.yaml` — GitHub Actions workflow (runs Saturdays at 8am UTC)
- `requirements.txt` — Python dependencies (requests, beautifulsoup4, lxml)

## Relationship to the posts repo

The canonical user-facing page is `posts/media/youtube.md` in the posts repo (`C:/Users/rober/git/posts/`). The `latest_videos.html` in this repo is a standalone test page for previewing changes to the JS/CSS applet without rebuilding the Jekyll site.

### Procedure for pushing applet changes to the posts repo

This procedure may need to be revised as the two files evolve.

1. **JS logic:** Copy changes from the `<script>` block in `latest_videos.html` to `posts/media/youtube.md`. Do **not** overwrite the `fetch()` URL — the posts version uses the absolute URL `https://www.rmwinslow.com/ytrss/latest_videos.json`.
2. **CSS rules:** Copy new or changed rules from the `<style>` block. Do **not** copy the `:root` variable definitions — those are test-page fallbacks. The posts page inherits CSS variables from the Jekyll theme.
3. **HTML structure:** Mirror any new `<div>` containers, classes, or structural changes to video block markup. Do **not** touch Jekyll frontmatter, explanatory prose, markdown headers, or HTML comments.
4. **Link format:** The two files currently use different link formats (test page uses `/embed/`, posts uses `/watch?v=` with `target="_blank"`). These stay independent until we deliberately unify them.

## Tag system design

The current single `category` column will be replaced with three structured columns
in `channel_list.csv`:

- **`topic`** — what the channel is about (e.g. `food`, `math`, `animals`). One value per channel. Maps roughly 1:1 from current categories.
- **`style`** — how the content feels (e.g. `chaotic`, `essay`, `documentary`). One value per channel. Can be left blank if non-obvious.
- **`favorite`** — set to `favorite` for top-tier channels, blank otherwise.

These three columns are flattened into a single `tags` list in the output JSON
(e.g. `["food", "chaotic", "favorite"]`). Blanks are simply omitted from the list.
This gives structured, easy-to-edit source data and a simple, filter-friendly output format.

During the transition, the output JSON will also include `category` set equal to `topic`,
so the existing JavaScript viewers continue to work. Once both the test page and the
posts repo viewer are updated to use the new tag-based filtering, `category` will be
removed from the output.

The HTML viewer will default to showing only favorites, with radio buttons to filter
by any tag value. The display is a single flat list sorted by date — no category
grouping headers.

The allowed values for `topic` and `style` are documented in the README. A helper
script can report rows with non-standard values for an LLM or human to review.

## TODOs

- [x] Change the GitHub Actions cron schedule to ~3am Central on Saturday (I already did this ages ago. 8am UTC is either 2 or 3 am, Central Time.)
- [ ] Revamp the tag/categorization system (see design below)
  - [ ] Replace `category` column in channel_list.csv with `topic`, `style`, `favorite`
  - [ ] Update `update_feed.py` to flatten these into a `tags` list in the output JSON, and set `category = topic` for backwards compatibility
  - [ ] Migrate existing channels: map current categories to topics, assign styles and favorites
  - [ ] Build new radio-button-based viewer (default to favorites, filter by any tag, flat list sorted by date)
  - [ ] Deploy new viewer to test page, verify, then push to posts repo
  - [ ] Remove backwards-compat `category` field from output JSON once both viewers are updated
- [ ] Add text search to the HTML page (across titles and channels)
- [ ] Create a tag vocabulary validation script that reports non-standard values
- [ ] Create an import pipeline: an `imports/` folder where YouTube or NewPipe subscription export CSVs can be dropped, with a script that migrates them into `channel_list.csv`
- [ ] Add retry logic for failed RSS fetches instead of silently skipping
- [ ] Extract video duration from the RSS feed's `media:group` and display it
- [ ] Extract short description snippets from the RSS feed
- [ ] Shorts filtering: investigate whether the YouTube RSS feed marks Shorts explicitly, or whether we'd need to filter by duration. If duration-only, consider whether to blacklist all videos under ~60s globally or have a per-channel flag for channels that mix Shorts with regular uploads. The feed currently shows only the latest video per channel, so a Short could mask a real upload.
- [ ] Generate an RSS/Atom feed from the aggregated data so users can subscribe in any reader
- [ ] Add dark mode / theme toggle to the HTML page (CSS variables are already in place)
- [ ] Improve error reporting: log which channels failed and why
- [ ] Expand README with the RoyalRoad inspiration, how to add channels, and how automation works
