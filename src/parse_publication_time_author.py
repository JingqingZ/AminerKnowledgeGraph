# parse time, author and keywords information from Aminer
# extract stem of each keyword,
#   so that tags like "Distributed Databases"
#   and "Distributed Database" will be taken as a same keyword
# output : time, author and keywords as parsed_publication.txt

import ast
import operator
from stemming.porter2 import stem

class Extraction(object):
    """docstring for Extraction"""
    def __init__(self):
        super(Extraction, self).__init__()
        self.time = list()
        self.author = list()
        self.keyword = list()
        self.keyword_dict = dict()

    def extract(self):
        infile = open('../results/publication.data', 'r')
        cur = 0
        for line in infile:
            if cur % 1000 == 0:
                print (cur)
            cur = cur + 1
            publication = ast.literal_eval(line)
            key_origin = publication["keywords"]
            unique_dict = dict()
            keys = list()
            for k in key_origin:
                key_stem = stem(k.lower())
                if key_stem in unique_dict:
                    continue
                unique_dict[key_stem] = 1
                keys.append(key_stem)
                self.keyword_dict[key_stem] = k
            self.keyword.append(keys)
            year = publication["year"]
            self.time.append(year)
            authors_info = publication["authors"]
            li = [i['name'] for i in authors_info]
            self.author.append(li)
            assert( len(self.time) == len(self.author) and len(self.author) == len(self.keyword) )

    def output(self):
        output = open('../results/parsed_publication.txt', 'w')
        for i in range(0, len(self.time)):
            output.write(repr(self.time[i]) + '\n')
            for j in self.author[i]:
                output.write(j + '!')
            output.write('\n')
            for j in self.keyword[i]:
                output.write(self.keyword_dict[j].replace(" ", "_") + ' ')
            output.write('\n')
        output.close()

def main():
    e = Extraction()
    e.extract()
    e.output()

if __name__ == '__main__':
    main()