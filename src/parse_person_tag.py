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

class PersonTagParser(object):
    """docstring for PersonTagParser"""
    def __init__(self):
        super(PersonTagParser, self).__init__()
        
    def parse_person_tag(self, person_data_file, output_person_keyword):
        tag_dict = {}
        stem_tag_dict = {}
        infile = open(person_data_file, 'r')
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
        outfile = open(output_person_keyword, 'w')
        for i in range(len(sorted_tag_dict) - 1, -1, -1):
            key = stem_tag_dict[sorted_tag_dict[i][0]]
            outfile.write(key.replace(" ", "_").replace('-', '_') +
                          "\t" + repr(sorted_tag_dict[i][1]) + '\n')
        outfile.close()


def main():
    ptp = PersonTagParser()
    ptp.parse_person_tag('../data/person_artificial_intelligence.data', '../results/person_artificial_intelligence.keywords')

if __name__ == '__main__':
    main()