import os, sqlite3, re, sys

dpath = os.path.dirname(__file__)

def __resultsToATC__(results, debugTitle=""):
    atcPtn = re.compile(r"\{\{(?P<atc>ATC\|[A-Za-z0-9]+\|[A-Za-z0-9]+)")
    # atcPtn = re.compile(r"\{\{(?P<atc>ATC\|[A-Z]{1}[0-9]{2}\|[A-Z]{2}[0-9]{2})\}\}")
    def extractATC(entry):
        r_t = entry["title"]
        r_c = entry["content"]
        # parse content for ATC patterns    
        matches = atcPtn.findall(r_c)
        if matches is None or len(matches) == 0:
            print("No ATC codes were found at: {}".format(r_t), file=sys.stderr)
        # remove initial ATC and |-chars
        return [ "".join(m.upper().split("|")[1:]) for m in matches ]

    atcCodes = {}
    for r in results:
        ATCs = extractATC(r)
        # add ATC codes to global ATC codes
        for code in ATCs:
            if code in atcCodes:
                atcCodes[code].append(r["title"])
            else:
                atcCodes[code] = [r["title"]]

    return atcCodes


def lookupATCen():
    db = sqlite3.connect(os.path.join(dpath,"enwiki.sqlite"))
    cur = db.cursor()
    # en-specific query
    query_result = cur.execute("SELECT title, content FROM content WHERE content LIKE \"%{{ATC|%\" COLLATE NOCASE;").fetchall()

    results = list(query_result)
    results = [ {"title":t, "content": c } for t,c in results ]

    return __resultsToATC__(results)


def lookupATCde():
    db = sqlite3.connect(os.path.join(dpath,"dewiki.sqlite"))
    cur = db.cursor()
    # de-specific query
    query_result = cur.execute("SELECT title, content FROM content WHERE content LIKE \"%{{ATC|%\" COLLATE NOCASE;").fetchall()

    results = list(query_result)
    results = [ {"title":t, "content": c } for t,c in results ]

    return __resultsToATC__(results)


if __name__ == "__main__":
    print("Look for ATC codes (en) ...")
    en_lookup = lookupATCen()
    atc_out_en = os.path.join(dpath, "ATCen.txt")
    atc_out_en_vals = os.path.join(dpath, "ATCen_values.txt")
    with open(atc_out_en, "w", encoding="utf-8") as f:
        f.write("\n".join(en_lookup.keys()))
    with open(atc_out_en_vals, "w", encoding="utf-8") as f:
        f.write("\n".join(["\n".join(v) for v in en_lookup.values()]))

    print("Look for ATC codes (de) ...")
    de_lookup = lookupATCde()
    atc_out_de = os.path.join(dpath, "ATCde.txt")
    atc_out_de_vals = os.path.join(dpath, "ATCde_values.txt")
    with open(atc_out_de, "w", encoding="utf-8") as f:
        f.write("\n".join(de_lookup.keys()))
    with open(atc_out_de_vals, "w", encoding="utf-8") as f:
        f.write("\n".join(["\n".join(v) for v in de_lookup.values()]))

