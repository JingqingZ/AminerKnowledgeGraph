# Get the basic information about ../results/publication_simplified.data
# output is saved in ../results/publication.info

class PublicationInfo(object):
    """docstring for PublicationInfo"""
    def __init__(self):
        super(PublicationInfo, self).__init__()
        self.year_count = dict()
        self.author_count = dict()
        self.have_key_count = 0
        self.have_author_count = 0
        self.invalid_paper_count = 0

    def readin(self):
        content = open('../results/publication_simplified.data', 'r').readlines()
        counter = 0
        for i in content:
            # this is the line of year
            if counter % 3 == 0:
                which_year = int(i)
                if which_year not in self.year_count:
                    self.year_count[which_year] = 1
                else:
                    self.year_count[which_year] += 1
            # this is the line of author
            elif counter % 3 == 1:
                if len(i) >= 2:
                    self.have_author_count += 1
                li = i.strip().split('!')
                li = [j.lower() for j in li]
                for j in li:
                    if j not in self.author_count:
                        self.author_count[j] = 1
                    else:
                        self.author_count[j] += 1
            # this is the line of keyword
            else:
                if len(i) >= 2:
                    self.have_key_count += 1
            counter = counter + 1
    
    def count_invalid(self):
        content = open('../results/publication_simplified.data', 'r').readlines()
        counter = 0
        year = 0
        author = ''
        keyword = ''
        for i in content:
            # this is about the year
            if counter % 3 == 0:
                year = int(i)
            # this is about the author
            elif counter % 3 == 1:
                author = i
            # this is about the keyword
            elif counter % 3 == 2:
                keyword = i
                if (not (year >= 1900 and year <= 2014)) or len(author) < 2 or len(keyword) < 2:
                    self.invalid_paper_count += 1
            counter += 1
        output = open('../results/publication.info', 'a')
        output.write(repr(self.invalid_paper_count) + ' invalid paper\n')
        output.write(repr(126444-self.invalid_paper_count) + ' valid paper\n')
        output.close()

    def show(self):
        output = open('../results/publication.info', 'w')
        output.write('----------------------------------------------------\n')
        li = list(self.year_count.items())
        li = sorted(li, key = lambda asd:asd[0], reverse=False)
        counter = 0
        for i in li:
            if i[0] >= 1900 and i[0] <= 2014:
                counter += i[1]
                output.write(repr(i[0]) + '\t' + repr(i[1]) + '\n')
        output.write('\n')
        output.write('total\t' + repr(counter) + ' paper with reasonable year\n')
        output.write('----------------------------------------------------\n')
        li = list(self.author_count.items())
        li = sorted(li, key = lambda asd:asd[1], reverse=True)
        for i in range(1, 100):
            output.write(li[i][0] + '\t' + repr(li[i][1]) + '\n')
        output.write('\n')
        output.write('total %d papers with author\n' % (self.have_author_count))
        output.write('----------------------------------------------------\n')
        output.write('total %d papers with keyword\n' % (self.have_key_count))
        output.write('----------------------------------------------------\n')
        output.close()

def main():
    pi = PublicationInfo()
    pi.readin()
    pi.show()
    pi.count_invalid()

if __name__ == '__main__':
    main()