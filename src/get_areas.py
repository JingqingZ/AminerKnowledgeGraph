import re
from stemming.porter2 import stem

class GetAreas(object):
    """docstring for GetAreas"""
    def __init__(self):
        super(GetAreas, self).__init__()
        self.area_filename = 'areas.txt'
        self.area_set = set()

    def load_areas(self):
        content = open(self.area_filename).readlines()
        for i in content:
            self.area_set.add(stem(i.strip()))

    def check_areas(self, keyword_file, number):
        content = open(keyword_file).readlines()
        cnt = 0
        for i in range(0, number):
            word = stem(content[i].split('\t')[0])
            if word in self.area_set:
                print (word)
                cnt += 1
        print (cnt)

def main():
    ga = GetAreas()
    ga.load_areas()
    ga.check_areas('../results/pub_data_mining.keywords', 100)

if __name__ == '__main__':
    main()