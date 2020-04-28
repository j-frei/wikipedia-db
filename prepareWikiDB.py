import os, re, sqlite3
from xml.etree import ElementTree

dpath = os.path.dirname(__file__)

# tag extraction helper
tagPtn = re.compile(r"{[^}]+}(?P<tag>..*)$")
def tag(el):
    match = tagPtn.fullmatch(el.tag)
    if match:
        return match.group("tag")
    return el.tag

def prepareDB(db):
    c = db.cursor()
    # create tables
    c.execute("CREATE TABLE content (title text, content text)")
    c.execute("CREATE TABLE redirect (origin text, target text)")
    # add indices for increased query performance
    c.execute("CREATE INDEX idx_content_title on content (title)")
    c.execute("CREATE INDEX idx_redirect_from on redirect (origin)")
    c.execute("CREATE INDEX idx_redirect_to on redirect (target)")

    db.commit()


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
        cursor.execute("INSERT INTO redirect VALUES (?,?)", (title,target))

        # check node for content data
        if "revision" in c:
            rev_c = { tag(rc):rc for rc in c["revision"].getchildren()}
            try:
                # extract content
                article = rev_c["text"].text
                abstract = article[:article.find("\n=")]
                cursor.execute("INSERT INTO content VALUES (?,?)",(title,abstract))
            except:
                import code
                code.interact(local=locals())
    else:
        # skip page
        pass

def parseWiki(wiki_file,sqlite_file,overwrite=False):
    # prepare wiki xml parser
    wiki = open(wiki_file, "r", encoding="utf-8")
    parser = ElementTree.iterparse(wiki,events=("start","end"))

    # prepare sqlite db
    if os.path.exists(sqlite_file) and not overwrite:
        raise Exception("SQLite file exists: {}".format(sqlite_file))

    db = sqlite3.connect(sqlite_file)
    prepareDB(db)
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

def main():
    parseWiki("enwiki-latest-pages-articles.xml","wiki.sqlite")

def main():
    import argparse

    parser = argparse.ArgumentParser(description='Convert Wikipedia XML dump to SQLite')
    parser.add_argument('wiki', type=str, help='the Wikipedia pages articles XML dump file')
    parser.add_argument('sqlite', type=str, help='the SQLite output file path')
    args = parser.parse_args()

    parseWiki(args.wiki,args.sqlite)

if __name__ == "__main__":
    main()
