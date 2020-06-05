import os, sys

if __name__ == "__main__":
    # read files
    with open("ATCen.txt", "r", encoding="utf-8") as f:
        enATC = f.read().splitlines() 
    with open("ATCde.txt", "r", encoding="utf-8") as f:
        deATC = f.read().splitlines()

    deATC = set(deATC)
    enATC = set(enATC)

    onlyDE = deATC.difference(enATC)
    onlyEN = enATC.difference(deATC)

    with open("onlyATCde.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(list(onlyDE)))

    with open("onlyATCen.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(list(onlyEN)))
