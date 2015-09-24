# parse tags from people information from Aminer
# extract stem of each tag,
# 	so that tags like "Distributed Databases"
# 	and "Distributed Database" will be taken as a same tag
# tag_dict are used to compute each tag's number
# stem_tag_dict are used to link a stemmed tag to its origin tag
# output: tags sorted by their number
import ast
import operator
from stemming.porter2 import stem

tag_dict = {}
stem_tag_dict = {}
infile = open("people.data", 'r')
for line in infile:
    person = ast.literal_eval(line)
    tags = person["tags"]
    unique_dict = {}
    for t in tags:
        t = t.lower()
        tag_stem = stem(t)
        if tag_stem in unique_dict:
            continue
        # link stemmed tag to its origin
        stem_tag_dict[tag_stem] = t
        # computer number
        if tag_stem not in tag_dict:
            tag_dict[tag_stem] = 1
        else:
            tag_dict[tag_stem] += 1
        unique_dict[tag_stem] = 1
# sort
sorted_tag_dict = sorted(tag_dict.items(), key=operator.itemgetter(1))
infile.close()
outfile = open("people.keywords", 'w')
for i in range(len(sorted_tag_dict) - 1, -1, -1):
    outfile.write(stem_tag_dict[sorted_tag_dict[i][0]].replace(" ", "_") +
                  "\t" + repr(sorted_tag_dict[i][1]) + '\n')
outfile.close()
