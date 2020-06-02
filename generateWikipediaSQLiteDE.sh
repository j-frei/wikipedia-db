#!/bin/bash

old_cwd=$(pwd)
cd $(dirname "$0")

echo "# # # # # # # # # # # # # # # # # # # #"
echo "# #                                 # #"
echo "# # Wikipedia XML --> SQLite script # #"
echo "# #                                 # #"
echo "# # # # # # # # # # # # # # # # # # # #"
echo

wiki="dewiki-latest-pages-articles.xml"
wiki_bz2="dewiki-latest-pages-articles.xml.bz2"
wiki_link="https://dumps.wikimedia.org/dewiki/latest/dewiki-latest-pages-articles.xml.bz2"
sqlite_file="dewiki.sqlite"

need_download=0
need_extract=0
need_convert=0

if [ -f "${sqlite_file}" ]; then
    echo "Wikipedia SQLite file does exist: $(pwd)/${sqlite_file}"
else
    # SQLite file is missing
    echo "Wikipedia SQLite file needs to be generated."
    need_convert=1
fi

if [ "$need_convert" -eq "1" ]; then
    if [ ! -f "$wiki" ]; then
        echo "Therefor we need to extract the wiki bz2 archive."
        need_extract=1
    fi
fi

if [ "$need_extract" -eq "1" ]; then
    if [ ! -f "$wiki" ]; then
        echo "Therefor we need to download the wiki dump."
        need_download=1
    fi
fi

if [ "$need_download" -eq "1" ]; then
    echo "Downloading wiki dump from ${wiki_link}"
    curl $wiki_link -O $wiki_bz2
fi

if [ "$need_extract" -eq "1" ]; then
    echo "Extracting wiki bz2 archive"
    bzip2 -d $wiki_bz2
fi

if [ "$need_convert" -eq "1" ]; then
    echo "Convert wiki XML to SQLite (takes ~1h)"
    python3 prepareWikiDB.py $wiki $sqlite_file
fi

echo "Done"

cd $old_cwd
