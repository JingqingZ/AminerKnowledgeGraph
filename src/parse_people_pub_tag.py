# input1: keywords extracted from professors' profiles
# input2: publications json list containing keywords information
# output: keywords extracted from profiles &
# 	sorted by their frequency in publications

import ast
import operator
from stemming.porter2 import stem

infile = open("people.keywords", 'r')
keywords_dict = {}
stem_keywords_dict = {}
for line in infile:
    line = line.split("\t")
    stem_keyword = stem(line[0])
    keywords_dict[stem_keyword] = 0
    stem_keywords_dict[stem_keyword] = line[0]
infile.close()

infile = open("publication.data", 'r')
cur = 0
for line in infile:
    if cur % 1000 == 0:
        print(cur)
    publication = ast.literal_eval(line)
    keywords = publication["keywords"]
    unique_dict = {}
    for k in keywords:
        k = k.lower()
        keyword_stem = stem(k).replace(" ", "_")
        if keyword_stem in unique_dict:
            continue
        # computer number
        if keyword_stem in keywords_dict:
            keywords_dict[keyword_stem] += 1
        unique_dict[keyword_stem] = 1
    cur += 1
# sort
sorted_keyword_dict = sorted(keywords_dict.items(), key=operator.itemgetter(1))
infile.close()

outfile = open("people_publication.keywords", 'w')
for i in range(len(sorted_keyword_dict) - 1, -1, -1):
    outfile.write(stem_keywords_dict[sorted_keyword_dict[i][0]] + "\t" +
                  repr(sorted_keyword_dict[i][1]) + '\n')
outfile.close()
