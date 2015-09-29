# given the number of topics
# get the time distribution of each specific topic
# keyword source is ../results/people_publication.keywords
# data source is ../results/publication_simplified.data
# output data is ../results/publication_time.keywords

from stemming.porter2 import stem

class TopicTime(object):
    """docstring for TopicTime"""
    def __init__(self):
        super(TopicTime, self).__init__()
        self.topic_number = 100
        self.topics = dict()
        self.stemword_dict = dict()

    def read(self, publication_keyword, publication_data):
        words = open(publication_keyword, 'r').readlines()
        for i in range(0, self.topic_number):
            s = stem(words[i].split('\t')[0])
            self.topics[ s ] = dict()
            self.stemword_dict[s] = words[i].split('\t')[0]
        content = open(publication_data, 'r').readlines()
        counter = 0
        year = ''
        for i in content:
            # three line represents a publication
            if counter % 3000 == 0:
                print (counter / 3)
            # record the year of this publication
            if counter % 3 == 0:
                year = int(i.strip())
            # parse the keywords of this publication
            elif counter % 3 == 2:
                keywords = i.strip().split(' ')
                for j in keywords:
                    j = stem(j)
                    if j in self.topics:
                        if year in self.topics[j]:
                            self.topics[j][year] += 1
                        else:
                            self.topics[j][year] = 1
            counter = counter + 1
    
    def show(self, publication_keyword, time_keyword_distribution):
        output = open(time_keyword_distribution, 'w')
        words = open(publication_keyword, 'r').readlines()
        for i in range(0, self.topic_number):
            s = stem(words[i].split('\t')[0])
            output.write(self.stemword_dict[s] + '\n')
            li = list(self.topics[s].items())
            li = sorted(li, key = lambda asd:asd[0], reverse=False)
            for j in li:
                output.write('\t' + repr(j[0]) + '\t' + repr(j[1]) + '\n')
        output.close()

def main():
    tt = TopicTime()
    tt.read('../results/publication.keywords_merge', '../results/publication_simplified.data_merge')
    tt.show('../results/publication.keywords_merge', '../results/time_keyword_distribution.txt')

if __name__ == '__main__':
    main()
