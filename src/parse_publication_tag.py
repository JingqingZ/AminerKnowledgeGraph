# parse keywords from publication information from Aminer
# extract stem of each keyword,
# 	so that tags like "Distributed Databases"
# 	and "Distributed Database" will be taken as a same keyword
# keyword_dict are used to compute each keyword's number
# stem_keyword_dict are used to link a stemmed keyword to its origin keyword
# output: keywords sorted by their number
import ast
import operator
from stemming.porter2 import stem

class PublicationTagParser(object):
    """docstring for PublicationTagParser"""
    def __init__(self):
        super(PublicationTagParser, self).__init__()
        
    def parse_publication_tag(self, publication_data_file, output_keyword_file, query_string):
        keyword_dict = {}
        stem_keyword_dict = {}
        infile = open(publication_data_file, 'r')
        cur = 0
        for line in infile:
            if cur % 1000 == 0:
                print(cur)
            publication = ast.literal_eval(line)
            keywords = publication["keywords"]
            unique_dict = {}
            for k in keywords:
                k = k.lower()
                keyword_stem = stem(k)
                if keyword_stem in unique_dict:
                    continue
                # link stemmed tag to its origin
                stem_keyword_dict[keyword_stem] = k
                # computer number
                if keyword_stem not in keyword_dict:
                    keyword_dict[keyword_stem] = 1
                else:
                    keyword_dict[keyword_stem] += 1
                unique_dict[keyword_stem] = 1
            cur += 1
        # sort
        sorted_keyword_dict = sorted(keyword_dict.items(), key=operator.itemgetter(1))
        infile.close()
        outfile = open(output_keyword_file, 'w')
        for i in range(len(sorted_keyword_dict) - 1, -1, -1):
            key = stem_keyword_dict[sorted_keyword_dict[i][0]]
            # remove query_string from keywords
            if key == query_string:
                continue
            outfile.write(key.replace(" ", "_") +
                        "\t" + repr(sorted_keyword_dict[i][1]) + '\n')
        outfile.close()


def main():
    ptp = PublicationTagParser()
    ptp.parse_publication_tag('../results/publication.data', '../results/publication.keywords', 'data mining')

if __name__ == '__main__':
    main()
