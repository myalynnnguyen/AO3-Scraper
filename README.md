# AO3-Scraper

A program to collect linguistic data from the fiction publishing website archiveofourown.org. You must provide the url of a search query, obtained from creating a search on the AO3 website.

# Frequency List
You can use this command line tool to create a frequency list of ngrams from works matching a certain search query. For example, to analyze the first 50 works in the Harry Potter fandom and collect ngrams of size 3:
```
python3 read_search.py "https://archiveofourown.org/tagsHarry%20Potter%20-%20J*d*%20K*d*%20Rowling/works"
--id_limit=5 --n=3 > frequency.txt
```

# Finding Translations
You can locate pairs of translations and the corresponding translated works within a search query like so. In this example, the program will find 20 translations written in Spanish and return a list of tuples containing the ID of the translation and the original translated work.

This may be useful in creating a parallel corpus.
```
from translations import find_translations

find_translations("https://archiveofourown.org/works/search?work_search%5Bquery%5D=&work_search%5Btitle%5D=&work_search%5Bcreators%5D=&work_search%5Brevised_at%5D=&work_search%5Bcomplete%5D=&work_search%5Bcrossover%5D=&work_search%5Bsingle_chapter%5D=0&work_search%5Bword_count%5D=&work_search%5Blanguage_id%5D=es&work_search%5Bfandom_names%5D=&work_search%5Brating_ids%5D=&work_search%5Bcharacter_names%5D=&work_search%5Brelationship_names%5D=&work_search%5Bfreeform_names%5D=&work_search%5Bhits%5D=&work_search%5Bkudos_count%5D=&work_search%5Bcomments_count%5D=&work_search%5Bbookmarks_count%5D=&work_search%5Bsort_column%5D=_score&work_search%5Bsort_direction%5D=desc&commit=Search",
id_limit=20)
```