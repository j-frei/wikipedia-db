import os, sqlite3, re, sys

dpath = os.path.dirname(__file__)

def lookupATCen():
    db = sqlite3.connect(os.path.join(dpath,"enwiki.sqlite"))
    cur = db.cursor()
    # en-specific query
    query_result = cur.execute("SELECT title, content FROM content WHERE content LIKE \"%{{ATC|%\" OR content LIKE \"%{{ATCvet|%\" OR content LIKE \"%ATCCode_prefix%\" OR content LIKE \"%ATC_prefix%\"  COLLATE NOCASE;").fetchall()

    results = list(query_result)
    results = [ {"title":t, "content": c } for t,c in results ]

    # en specific search
    atcPtn1 = re.compile(r"\{\{(?P<atc>atcv?e?t?\|[A-Za-z0-9\|]+)",  re.IGNORECASE)
    # atcPtn = re.compile(r"\{\{(?P<atc>ATC\|[A-Z]{1}[0-9]{2}\|[A-Z]{2}[0-9]{2})\}\}")
    def extractATC1(entry):
        r_t = entry["title"]
        r_c = entry["content"]
        # parse content for ATC patterns
        matches = atcPtn1.findall(r_c)
        # remove initial ATC and |-chars
        return [ "".join(m.upper().split("|")[1:]) for m in matches ]

    atcPtn2_prefix = re.compile(r"ATCC?o?d?e?\_prefix\s*=\s*(?P<prefix>[A-Za-z0-9]+)",  re.IGNORECASE)
    atcPtn2_suffix = re.compile(r"ATCC?o?d?e?\_suffix\s*=\s*(?P<suffix>[A-Za-z0-9]+)",  re.IGNORECASE)
    def extractATC2(entry):
        r_t = entry["title"]
        r_c = entry["content"]
        # parse content for ATC patterns
        matches_prefix = atcPtn2_prefix.findall(r_c)
        matches_suffix = atcPtn2_suffix.findall(r_c)
        if len(matches_prefix) != len(matches_suffix):
            print("Mismatch in prefix/suffix findings: {}".format(r_t), file=sys.stderr)
            return []
        else:
            # remove initial ATC and |-chars
            res = [ "{}{}".format(m_pre,m_suf) for m_pre,m_suf in zip(matches_prefix,matches_suffix) ]
            return res

    atcCodes = {}
    for r in results:
        ATCs = extractATC1(r) + extractATC2(r)
        if len(ATCs) == 0:
            print("No codes found for: {}".format(r["title"]), file=sys.stderr)
        # add ATC codes to global ATC codes
        for code in ATCs:
            if len(code) == 7 or (len(code) == 8 and code.startswith("Q")):
                if code in atcCodes:
                    atcCodes[code].append(r["title"])
                else:
                    atcCodes[code] = [r["title"]]
            else:
                print("Unknown code: {} from title {}".format(code, r["title"]))

    return atcCodes


def lookupATCde():
    db = sqlite3.connect(os.path.join(dpath,"dewiki.sqlite"))
    cur = db.cursor()
    # de-specific query
    query_result = cur.execute("SELECT title, content FROM content WHERE content LIKE \"%{{ATC|%\" or content LIKE \"%{{ATCvet|%\" COLLATE NOCASE;").fetchall()

    results = list(query_result)
    results = [ {"title":t, "content": c } for t,c in results ]

    # de specific search
    atcPtn = re.compile(r"\{\{(?P<atc>atcv?e?t?\|[A-Za-z0-9\|]+)",  re.IGNORECASE)
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
            if len(code) == 7 or (len(code) == 8 and code.startswith("Q")):
                if code in atcCodes:
                    atcCodes[code].append(r["title"])
                else:
                    atcCodes[code] = [r["title"]]
            else:
                print("Unknown code: {} from title {}".format(code, r["title"]))

    return atcCodes


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

