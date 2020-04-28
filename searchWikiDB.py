import os, re, sqlite3

dpath = os.path.dirname(__file__)


def checkWiki(input_term):
    db_path = os.path.join(dpath,"wiki.sqlite")
    if not os.path.exists(db_path):
        raise Exception("DB not found: {}".format(db_path))

    db = sqlite3.connect(db_path)

    # find pages that matches the query term
    def candidateSearch(str_input):
        c = db.cursor()
        res = c.execute("SELECT origin,target FROM redirect WHERE origin LIKE (?) COLLATE NOCASE LIMIT 100",("%"+str_input+"%",)).fetchall()
        db_candidates = [ target if target != "<rootnode>" else origin for origin, target in res ]
        unique_candidates = list(set(db_candidates))
        return unique_candidates


    # load content from page with <title>
    def getEntry(title):
        c = db.cursor()
        res = c.execute("SELECT content FROM content WHERE title = (?)",(title,)).fetchall()
        if len(res) != 1:
            if len(res) == 0:
                print("Entry not found")
                return ""
            else:
                print("More than one entry! Using first entry")
                return res[0][0]
        else:
            return res[0][0]

    # check whether page is drug-focused
    def checkPage(page_content):
        return bool(re.search("atc_suffix",page_content,re.IGNORECASE))

    # check candidates
    candidates = candidateSearch(input_term)
    # load entries
    contents = [ getEntry(c) for c in candidates ]

    # count hits in candidate set
    hits = 0
    for content in contents:
        if checkPage(content):
            hits += 1

    # No candidates found -> avoid div by zero
    if len(contents) == 0:
        return False

    return (hits / len(contents)) > 0.05
    

def main():
    import argparse

    parser = argparse.ArgumentParser(description='Check term for medication.')
    parser.add_argument('medTerm', type=str, help='the term that should be checked for medication.')
    args = parser.parse_args()

    medTerm = args.medTerm
    found = checkWiki(medTerm)
    if found:
        print("The term \"{}\" is detected as medication.".format(medTerm))
    else:
        print("The term \"{}\" does not seem to be a medication.".format(medTerm))


if __name__ == "__main__":
    main()
