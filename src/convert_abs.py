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
            cur += 1
            if cur % 1000 == 0:
                print (cur)
            publication = ast.literal_eval(line)
            abstract = publication['abstract']
            if len(abstract) < 5:
                continue
            output.write(abstract + '\n')
        output.close()

    def load_keywords(self):
        content = open('../results/pub_' + self.query + '.keywords').readlines()
        print ('loading keywords')
        for i in content:
            key = i.split('\t')[0]
            words = key.split('_')

            if len(words) == 2:
                st1 = stem(words[1])
                if words[0] in self.keyword_dict:
                    if st1 in self.keyword_dict[ words[0] ]:
                        self.keyword_dict[ words[0] ][st1].add(-1)
                    else:
                        self.keyword_dict[ words[0] ][st1] = {-1}
                else:
                    self.keyword_dict[ words[0] ] = { st1 : {-1} }

            if len(words) == 3:
                st2 = stem(words[2])
                if words[0] in self.keyword_dict:
                    if words[1] in self.keyword_dict[ words[0] ]:
                        self.keyword_dict[ words[0] ][ words[1] ].add(st2)
                    else:
                        self.keyword_dict[ words[0] ][ words[1] ] = {st2}
                else:
                    self.keyword_dict[ words[0] ] = { words[1] : {st2} }
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
            li = re.split('\s+', line)
            j = 0
            while j < len(li):
                if li[j] in self.keyword_dict:
                    if (j+2) < len(li) and li[j+1] in self.keyword_dict[ li[j] ] and stem(li[j+2]) in self.keyword_dict[ li[j] ][ li[j+1] ]:
                        output.write(li[j] + '_' + li[j+1] + '_' + li[j+2] + ' ')
                        j += 3
                    elif (j+1) < len(li) and stem(li[j+1]) in self.keyword_dict[ li[j] ] and -1 in self.keyword_dict[ li[j] ][ stem(li[j+1]) ]:
                        output.write(li[j] + '_' + li[j+1] + ' ')
                        j += 2
                    else:
                        output.write(li[j] + ' ')
                        j += 1
                else:
                    output.write(li[j] + ' ')
                    j += 1
            output.write('\n')
        output.close()
        # overwrite the previous abstract file
        os.rename('../results/pub_' + self.query + '.w2v', '../results/pub_' + self.query + '.abs')

    def call_word2vec(self):
        # parameters for word2vec
        window = 5
        size = 200
        train_file = '../results/pub_' + self.query + '.abs'
        bin_file = '../results/vec_' + self.query + '.bin'
        txt_file = '../results/vec_' + self.query + '.txt'

        command1 = 'word2vec -train %s -output %s -size %d -window %d -sample 1e-4 -negative 5 -hs 0 -binary %d -cbow 1 -iter 3' % (train_file, bin_file, size, window, 1)
        command2 = 'word2vec -train %s -output %s -size %d -window %d -sample 1e-4 -negative 5 -hs 0 -binary %d -cbow 1 -iter 3' % (train_file, txt_file, size, window, 0)

        os.system(command1)
        os.system(command2)

def main():
    ca = ConvertAbstract(sys.argv[1])
    ca.parse_publication_abstract()
    ca.load_keywords()
    ca.parse_abstract(100000)
    ca.call_word2vec()

if __name__ == '__main__':
    main()
