# Wikipedia SQLite Extraction Tool

## How to Use
Run the script `generateWikipediaSQLite.sh`. This script performs the following steps:  
 - Downloading the latest Wikipedia dump (in English) from the internet
 - Extracting the obtained data
 - Convert the XML file into a SQLite file.

## Remarks
The data only contains the first abstract of all Wikipedia pages.  

The SQLite database maintains two DB tables:  
 - `redirect` with columns `origin`, `target` that stores the redirection links to their targets. Root pages are represented as `<page_title>`->`<rootnode>`. "<rootnode>" is a keyword.
 - `content` with columns `title`, `content` that maps each title to the abstract of its page.


`searchWikiDB.py` implements a simple lookup check that determines whether a term is associated with a medication.

