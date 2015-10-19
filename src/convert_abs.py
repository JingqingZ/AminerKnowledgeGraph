from stemming.porter2 import stem
import sys

class ConvertAbstract(object):
    """docstring for ConvertAbstract"""
    def __init__(self, q):
        super(ConvertAbstract, self).__init__()
        self.query = q.replace(' ', '_')
        self.keyword_dict = dict()

    def load_keywords(self):
        content = open('../results/pub_' + self.query + '.keywords').readlines()
        for i in content:
            key = i.split('\t')[0]
            words = key.split('_')
            if len(words) == 2:
                if words[0] in self.keyword_dict:
                    self.keyword_dict[ words[0] ].add(stem(words[1]))
                else:
                    self.keyword_dict[ words[0] ] = { stem(words[1]) }

    def parse_abstract(self):
        content = open('../results/pub_' + self.query + '.abs').readlines()
        output = open('../results/output', 'w')
        cnt = 0
        for i in content:
            cnt = cnt + 1
            if cnt % 1000 == 0:
                print (cnt)
            li = i.split(' ')
            for j in range(0, len(li)):
                if li[j] in self.keyword_dict:
                    if (j+1) < len(li) and stem(li[j+1]) in self.keyword_dict[ li[j] ]:
                        output.write(li[j] + '_')
                    else:
                        output.write(li[j] + ' ')
                else:
                    output.write(li[j] + ' ')
        output.close()

def main():
    ca = ConvertAbstract(sys.argv[1])
    ca.load_keywords()
    ca.parse_abstract()

if __name__ == '__main__':
    main()
