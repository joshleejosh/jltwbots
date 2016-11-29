@SecretHistBot: https://twitter.com/SecretHistBot

This bot does the following:
- Looks for a random(ish) trend in a random(ish) location;
- Searches tweets and pulls out keywords;
- Assembles the title of a bestselling history book.

Some example tweets:
```
The Secret History of #TravelForGood in Pittsburgh: World, Children, and Help
The Secret History of Lawrence in Washington: Chris, TrippyMorrison, and Pratt
The Secret History of Alexander-Arnold in Swansea: Leeds, Origi, and Ben
The Secret History of #FairCity in Galway: Rocco, Jane, and Oisin
The Secret History of #HULNEW in Glasgow: Diame, 0-1, and Newcastle
The Secret History of #DefineAboriginal in Sydney: Health, Culture, and Hanson
```

----

The process for figuring out which location and trend we should look at is a little tortured and request-heavy, but gets us results with a more local feel:

* Sample a few locations.
* For each location, find its trends.
* Filter out trends that are common among locations.
* Pick a location that has multiple unique local trends to search on.
* Sample a few trends from the location.
* For each trend, count the tweets that will come back in a search.
* Pick the trend with the most tweets.

Once we have a location and trend, we can search for tweets:

* Search for tweets by trend.
* Break down the tweets into separate keywords, throwing away common stopwords and blacklisted words.
* Rank keywords by frequency.
* Pick three of the more common words. (But not the 3 *most* common, as those tend to be rather predictable.)

We now have a location, a trend, and three keywords, which is what we need to build our book title.

