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

def parse_people_tag(people_data_file, output_people_keyword, query_string):
    tag_dict = {}
    stem_tag_dict = {}
    infile = open(people_data_file, 'r')
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
    outfile = open(output_people_keyword, 'w')
    for i in range(len(sorted_tag_dict) - 1, -1, -1):
        key = stem_tag_dict[sorted_tag_dict[i][0]]
        # remove query string from keywords
        if key == query_string:
            continue
        outfile.write(key.replace(" ", "_") +
                      "\t" + repr(sorted_tag_dict[i][1]) + '\n')
    outfile.close()


def main():
    parse_people_tag('../results/people.data', '../results/people.keywords', 'data mining')

if __name__ == '__main__':
    main()