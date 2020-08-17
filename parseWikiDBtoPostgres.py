import psycopg2
import os, sys, re
from xml.etree import ElementTree

dpath = os.path.dirname(__file__)

# tag extraction helper
tagPtn = re.compile(r"{[^}]+}(?P<tag>..*)$")
def tag(el):
    match = tagPtn.fullmatch(el.tag)
    if match:
        return match.group("tag")
    return el.tag

skip_page = ["Wikipedia","Portal","Template","Category","Draft", \
             "Module","File", "MediaWiki", "TimedText"]
ptnStart = re.compile(r"({}):..+$".format("|".join(skip_page)))
def processPage(el,cursor):
    c = { tag(e):e for e in el.getchildren()}
    title = c["title"].text

    # check for skippable page
    pfx_match = ptnStart.fullmatch(title)
    if not pfx_match:
        # does not start with Portal:..., etc
        # write redirect link or mark as rootnode
        target = c["redirect"].attrib["title"] if "redirect" in c else "<rootnode>"
        cursor.execute("INSERT INTO deredirect VALUES (%(title)s,%(target)s)", {"title":title,"target":target})

        # check node for content data
        if "revision" in c:
            rev_c = { tag(rc):rc for rc in c["revision"].getchildren()}
            try:
                # extract content
                article = rev_c["text"].text
                cursor.execute("INSERT INTO decontent VALUES (%(title)s,%(article)s)",{"title":title,"article":article})
            except:
                print("Found empty entry. Skipping...")
    else:
        # skip page
        pass

def parseWiki(wiki_file,db):
    # prepare wiki xml parser
    wiki = open(wiki_file, "r", encoding="utf-8")
    parser = ElementTree.iterparse(wiki,events=("start","end"))

    c = db.cursor()

    # do parsing
    inNode = False
    for ev, el in parser:
        # enter page section
        if tag(el) == "page" and ev == "start":
            inNode=True
        # reached end of page section: process data and clear nodes
        if tag(el) == "page" and ev == "end":
            processPage(el,c)
            inNode=False
        if not inNode:
            el.clear()

    db.commit()
    wiki.close()

def getPostgresCredentials():
    return {
        "user": "wiki",
        "password": "wiki",
        "host": "vm198-misit.informatik.uni-augsburg.de",
        "port": "5432",
        "database": "wiki"
    }

def pre_parsing(db):
    #try:
    #    c = db.cursor()
    #    c.execute("DROP TABLE decontent;")
    #    c.execute("DROP TABLE deredirect;")
    #    c.close()
    #except:
    #    pass

    c = db.cursor()
    # create tables
    c.execute("CREATE TABLE decontent (item text, content text);")
    c.execute("CREATE TABLE deredirect (origin text, target text);")
    db.commit()

def post_parsing(db):
    c = db.cursor()
    c.execute("CREATE INDEX decontent_item_idx ON decontent (item);")
    c.execute("CREATE INDEX deredirect_item_idx ON deredirect (origin, target);")
    db.commit()

def main():
    dewiki = os.path.join(dpath, "dewiki-latest-pages-articles.xml")

    postgres_creds = getPostgresCredentials()
    postgres_db = psycopg2.connect(**postgres_creds)
    pre_parsing(postgres_db)
    parseWiki(dewiki,postgres_db)
    post_parsing(postgres_db)

if __name__ == "__main__":
    main()
