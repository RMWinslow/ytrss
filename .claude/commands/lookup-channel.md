Look up a YouTube channel and summarize its recent content for tag assignment.

The argument is a channel ID (e.g. UCVpankR4HtoAVtYnFDUieYA) or a vanity URL (e.g. http://www.youtube.com/@zefrank).

Spawn a general-purpose Agent to perform the lookup. The agent prompt should include:

1. If the argument is a URL, use WebFetch to fetch the URL and extract the channel ID from the og:url meta tag.

2. Use WebFetch to fetch the RSS feed at:
   https://www.youtube.com/feeds/videos.xml?channel_id=CHANNEL_ID
   Extract the channel name and all video titles with their dates.

3. Read the tag vocabulary from the Tag vocabulary section of C:/Users/rober/git/ytrss/README.md (around line 96-125).

4. Present the results:
   - Channel name
   - Channel ID
   - All recent video titles with dates
   - The current topic and style vocabularies
   - A suggested topic and style based on the video titles, with brief reasoning

The user and the main agent will evaluate the suggestion — do not treat it as final.

Argument: $ARGUMENTS
