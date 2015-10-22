from stemming.porter2 import stem
import ast
import re
import string
import os
import sys

class ConvertAbstract(object):
    """docstring for ConvertAbstract"""
    def __init__(self, q):
        super(ConvertAbstract, self).__init__()
        self.query = q.replace(' ', '_')
        self.keyword_dict = dict()

    def parse_publication_abstract(self):
        publication_file = '../data/pub_' + self.query + '.data'
        output_file = '../results/pub_' + self.query + '.abs'
        
        infile = open(publication_file, 'r')
        output = open(output_file, 'w')
        cur = 0
        for line in infile:
            if cur % 1000 == 0:
                print (cur)
            publication = ast.literal_eval(line)
            abstract = publication['abstract']
            if len(abstract) < 5:
                continue
            output.write(abstract + '\n')
            cur += 1
        output.close()

    def load_keywords(self):
        content = open('../results/pub_' + self.query + '.keywords').readlines()
        print ('loading keywords')
        for i in content:
            key = i.split('\t')[0]
            words = key.split('_')
            if len(words) == 2:
                if words[0] in self.keyword_dict:
                    self.keyword_dict[ words[0] ].add(stem(words[1]))
                else:
                    self.keyword_dict[ words[0] ] = { stem(words[1]) }
        print ('load keywords complete')

    def parse_abstract(self, doclength):
        content = open('../results/pub_' + self.query + '.abs').readlines()
        output = open('../results/pub_' + self.query + '.w2v', 'w')
        cnt = 0
        for i in content:
            line = re.sub(r'\n|[{}]+'.format(string.punctuation), ' ', i).lower()
            cnt = cnt + 1
            if cnt % 1000 == 0:
                print (cnt)
            if cnt == doclength:
                break
            li = line.split(' ')
            j = 0
            while j < len(li):
                if (j+1) < len(li) and li[j] in self.keyword_dict and stem(li[j+1]) in self.keyword_dict[ li[j] ]:
                    output.write(li[j] + '_' + li[j+1] + ' ')
                    j += 2
                else:
                    output.write(li[j] + ' ')
                    j += 1
            output.write('\n')
        output.close()
        # overwrite the previous abstract file
        os.rename('../results/pub_' + self.query + '.w2v', '../results/pub_' + self.query + '.abs')

def main():
    ca = ConvertAbstract(sys.argv[1])
    ca.parse_publication_abstract()
    ca.load_keywords()
    ca.parse_abstract(100000)

if __name__ == '__main__':
    main()
