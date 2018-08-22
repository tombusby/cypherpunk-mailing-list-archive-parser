+ ~~PPE timezone I've assumed is the same as PST due to the fact that none of the posts with it are during daylight savings (Oct-Dec 92), and some of the posters (i.e. T. C. May) are based in CA.~~ Upon comparison with Ryan Lackey's Structured Archive for [Oct 1992](https://cypherpunks.venona.com/date/1992/10), I can confirm that the PPE timezone is inconsistent. I will have to find a way to manually fix the 70 or so of these that exist by comparing them. I've set PPE to be roughly in the middle of the variety of offsets that do occur.
+ There are some posts dated Tue Sep 07 12:36-57 that crop up in 92-96. These all have the same message-ID (one that indicates the message ID isn't found). As such I'll be categorising them in as "messages with unknown date/time" in the year whose archive they're from.
+ There are some posts from the first few days of Jan 1999 in the 1998 archive. I believe these are genuinely dated and will archive them as such.
+ There appear to be messages from the Extropians@gnu.ai.mit.edu / extropians@extropy.org mailing list mixed in too, but they all appear relevant to the cypherpunk mailing list, so I'll be leaving them in place.
+ I used `for f in raw_messages/199*/*.txt; do iconv -f utf-8 -t utf-8 -c $f > $f-2; mv $f-2 $f; done` to clean up the encoding issues before using `./make_markdown_files.py`

TODO:

+ Throw away prototype scripts and build a proper, deterministic start-to-finish program which will can take the .txt archives to the directory-strucuted JSON files without any intervention.
+ Take the 2000-2016 archives and parse them into the same format.
