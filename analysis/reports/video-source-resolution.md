# Video source resolution

The canonical completed regular-season schedule provides one VOD candidate for each of the 27 transcript broadcast dates and associates all 72 completed series with those dates. Candidate IDs and series mappings are stored in [`analysis/sources/source-manifest.json`](../sources/source-manifest.json).

**A schedule URL is not a verified source identity.** The local resolver must confirm that the YouTube title identifies the expected MPL ID S18 week/day and that the channel is MPL Indonesia. Timestamp links require a further one-to-one alignment of every raw transcript line with official timed captions.

At the last committed snapshot, 2 of 27 sources have completed metadata verification and timed-caption alignment. The other 25 are candidates pending verification, not verified sources.

Run `python tools/resolve_and_align_sources.py` on the local machine containing the Git-ignored `analysis/sources/raw-transcripts/` directory. The run is resumable. It records errors instead of guessing or marking a partial alignment successful.

Broadcast-date mapping does not establish the exact start time of each series or game within a multi-hour VOD.
