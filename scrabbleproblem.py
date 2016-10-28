#!/usr/bin/env python
#
# Quick and dirty solution for the 538 Riddler Express about scrabble
# http://fivethirtyeight.com/features/this-challenge-will-boggle-your-mind/
#
# Written by Matthew Beckler, released into the Public Domain. Have fun!

import urllib

def anyin(haystack, needle):
    for h in haystack:
        if h in needle:
            return True


urllib.urlretrieve("https://storage.googleapis.com/google-code-archive-downloads/v2/code.google.com/dotnetperls-controls/enable1.txt", "enable1.txt")

legalwords = map(lambda x: x.strip(), file("enable1.txt").readlines())

puzzlewords = filter(lambda x: len(x) == 2, legalwords)

while True:
    print "----------------------------"
    print "puzzlewords:", len(puzzlewords)
    print " ".join(puzzlewords)

    maxlen = max(map(lambda x: len(x), puzzlewords))
    print "max len:", maxlen

    longerwords = filter(lambda x: len(x) == maxlen + 1, legalwords)
    print "longerwords:", len(longerwords)

    # want to find words in longerwords that contain a word from puzzlewords
    new = filter(lambda x: anyin(puzzlewords, x), longerwords)

    if len(new) == 0:
        print "No longer words found"
        break

    puzzlewords = new




