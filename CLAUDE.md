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

## TODOs

- [ ] Change the GitHub Actions cron schedule from 8am UTC Saturday to 3am UTC Saturday
- [ ] Add filtering and search to the HTML page (text search across titles and channels)
- [ ] Revamp the tag/categorization system to support richer filtering
- [ ] Create an import pipeline: an `imports/` folder where YouTube or NewPipe subscription export CSVs can be dropped, with a script that migrates them into `channel_list.csv`
- [ ] Add retry logic for failed RSS fetches instead of silently skipping
- [ ] Extract video duration from the RSS feed's `media:group` and display it
- [ ] Extract short description snippets from the RSS feed
- [ ] Generate an RSS/Atom feed from the aggregated data so users can subscribe in any reader
- [ ] Add dark mode / theme toggle to the HTML page (CSS variables are already in place)
- [ ] Improve error reporting: log which channels failed and why
- [ ] Expand README with the RoyalRoad inspiration, how to add channels, and how automation works
