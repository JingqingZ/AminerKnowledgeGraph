# merge keywords with same meaning
from stemming.porter2 import stem
import os

class MergeKeywords(object):
    """docstring for MergeKeywords"""
    def __init__(self):
        super(MergeKeywords, self).__init__()
        self.suffix = [ '.', '_algorithms', '_algorithm', '_theory', '_mining',
                        '_analysis', '_module', '_techniques', '_technique'
                        '_model', '_processing', '_tools', '_tool', 
                        '_applications', '_application', '_systems', '_system']
        self.matching = dict()
        self.keywords = dict()
        self.simword = dict()

    def readin(self, origin_keyword_file):
        # load original keyword
        content = open(origin_keyword_file).readlines()
        for i in content:
            li = i.strip().split('\t')
            if len(li) != 2:
                print ( ('keywords format error : %s') % (i.strip()) )
                continue
            self.keywords[li[0]] = int(li[1])

        # load similar keyword dictionary
        filename = 'simword.txt'
        if os.path.exists(filename):
            content = open(filename).readlines()
            for i in content:
                li = i.strip().split('\t')
                self.simword[li[0]] = li[1]

    def save_file(self, simword_output):
        print ('saving similar keywords file')
        output = open(simword_output, 'w')
        for i in self.matching:
            output.write(i + '\t' + self.matching[i] + '\n')
        output.close()

    def process_keywords(self, new_keyword_file, query_string):
        # check the suffix for keywords
        print ('checking suffix for all keywords')
        for i in self.keywords:
            # in this step we remove the suffix for all the keywords
            flag = False
            for j in self.suffix:
                if i.endswith(j):
                    where = i.rfind(j)
                    self.matching[i] = i[:where]
                    flag = True
                    break
            if flag == False:
                self.matching[i] = i

        # check simword.txt
        for i in self.matching:
            if i in self.simword:
                self.matching[i] = self.simword[i]

        # this step find the most common keywords for each keyword without suffix
        print ('find most common keywords after removing suffix')
        keywords_stem = dict()
        for i in self.matching:
            s = stem(self.matching[i])
            if s in keywords_stem:
                count1 = self.keywords[i]
                count2 = keywords_stem[s][1]
                if count1 > count2:
                    keywords_stem[s] = (i, count1)
            else:
                keywords_stem[s] = (i, self.keywords[i])

        # this step finally merge the keywords together
        print ('similar keywords matching')
        for i in self.matching:
            s = stem(self.matching[i])
            self.matching[i] = keywords_stem[s][0]

        for i in self.matching:
            if self.matching[i] in self.simword:
                new = self.simword[self.matching[i]]
                self.matching[i] = new

        # change '-' to '_' for all keywords
        for i in self.matching:
            self.matching[i] = self.matching[i].replace('-', '_')

        print ('merging keywords')
        new_key = dict()
        for i in self.matching:
            if self.matching[i] in new_key:
                new_key[ self.matching[i] ] += self.keywords[i]
            else:
                new_key[ self.matching[i] ] = self.keywords[i]
        ans = sorted(new_key.items(), key = lambda asd:asd[1], reverse=True)
        output = open(new_keyword_file, 'w')
        query_string_repl = query_string.replace(' ', '_')
        for i in ans:
            if i[0].startswith(query_string_repl):
                continue
            output.write(i[0] + '\t' + repr(i[1]) + '\n')
        output.close()

    def process_publication(self, origin_publication_file, new_publication_file):
        print ('merging publications')
        counter = 0
        output = open(new_publication_file, 'w')
        content = open(origin_publication_file).readlines()
        for i in content:
            if counter % 4 == 3:
                li = i.strip().split(' ')
                for j in li:
                    if j in self.matching:
                        output.write(self.matching[j] + ' ')
                    else:
                        output.write(j + ' ')
                output.write('\n')
            else:
                output.write(i)
            counter += 1
        output.close()

def main():
    mk = MergeKeywords()
    mk.readin('../results/pub_data_mining.keywords')
    mk.process_keywords('../results/pub_data_mining.merged', 'data mining')
    
    mk.process_publication('../results/pub_data_mining.simp', '../results/pub_data_mining.ttt')

if __name__ == '__main__':
    main()
