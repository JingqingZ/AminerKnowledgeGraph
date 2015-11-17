import numpy
import shutil
from scipy.spatial import distance
from stemming.porter2 import stem
import sys
import math
from os import path

# initialize the first topic_num topics, remove those without enough factor
# initialize link with diff > threshold, remove those not in topic_dict
class GetTopicFactor(object):
    """docstring for GetTopicFactor"""

    def __init__(self, q, threshold):
        super(GetTopicFactor, self).__init__()
        self.year_begin = 1980
        self.year_end = 2015
        self.topic_num = 100
        self.topic_dict = {}
        self.numb_max = -1
        self.numb_max_year = -1
        self.soar_max = -1
        self.soar_max_year = -1
        self.topic = ""
        self.stem2keyword = {}

        # self.diff_threshold = threshold
        self.num_threshold = threshold
        self.w2v_length = 200
        self.query = q.replace(' ', '_')

    def keyword2stem(self, keyword, record=False):
        keylist = keyword.split("_")
        stemmed = ""
        for i in range(0, len(keylist)):
            stemmed += stem(keylist[i]) + "_"
        stemmed = stemmed[:-1]
        if record:
            self.stem2keyword[stemmed] = keyword
        return stemmed

    def init_topic_dict(self):
        # load from person keyword
        infile_topic = '../results/person_' + self.query + '.keywords'
        #infile_topic = '../results/pub_' + self.query + '.keywords'
        infile = open(infile_topic)
        curline = 0
        for line in infile:
            if curline >= self.topic_num:
                break
            content = line.split("\t")
            topic = self.keyword2stem(content[0], record=True)
            self.topic_dict[topic] = {}
            # initialize factors
            paper_trend = []
            for year in range(self.year_begin, self.year_end):
                paper_trend.append(0)
            self.topic_dict[topic]["paper_trend"] = paper_trend
            self.topic_dict[topic]["first_paper_year"] = -1
            self.topic_dict[topic]["paper_peak_year"] = -1
            self.topic_dict[topic]["paper_peak_num"] = -1
            self.topic_dict[topic]["paper_soar_year"] = -1
            self.topic_dict[topic]["paper_soar_num"] = -1
            self.topic_dict[topic]["paper_list"] = {}
            self.topic_dict[topic]["author_list"] = {}
            self.topic_dict[topic]["voc_dist"] = []
            curline += 1
        infile.close()

    def update_paper_info(self):
        # update peak info and soar info
        if self.topic != "":
            # update and initialize peak info
            self.topic_dict[self.topic]["paper_peak_year"] = self.numb_max_year
            self.topic_dict[self.topic]["paper_peak_num"] = self.numb_max
            self.numb_max = -1
            self.numb_max_year = 0
            # update and initialize soar info
            for year in range(self.year_begin + 1, self.year_end):
                growth = self.topic_dict[self.topic]["paper_trend"][year - self.year_begin] - \
                    self.topic_dict[self.topic]["paper_trend"][year - 1 - self.year_begin]
                if growth > self.soar_max:
                    self.soar_max = growth
                    self.soar_max_year = year
            self.topic_dict[self.topic]["first_paper_year"] = self.year_end
            for i in range(0, self.year_end - self.year_begin):
                if self.topic_dict[self.topic]["paper_trend"][i] > 0:
                    self.topic_dict[self.topic]["first_paper_year"] = i + self.year_begin
                    break
            self.topic_dict[self.topic]["paper_soar_year"] = self.soar_max_year
            self.topic_dict[self.topic]["paper_soar_num"] = self.soar_max
            self.soar_max = -1
            self.soar_max_year = 0

    def get_paper_number(self):
        # range of year: [1980, 2015)
        # get the year when the number of
        #   papers that have a certain topic reaches the peak
        # get the year when the number of
        #   papers that have a certain topic grows fastest
        # get the trend of a certain topic
        infile_pub_dist = '../results/pub_' + self.query + '.dist'
        infile = open(infile_pub_dist, "r")
        self.topic = ""
        self.numb_max = -1
        self.numb_max_year = -1
        self.soar_max = -1
        self.soar_max_year = -1
        for line in infile:
            content = line.replace("\n", "").split("\t")
            if len(content) == 1:   # topic
                self.update_paper_info()
                # update and initial new topic factors
                self.topic = self.keyword2stem(content[0])
                print(self.topic)
                assert(self.topic in self.topic_dict)
            else:  # topic distribution
                assert(len(content) == 3)
                year = int(content[1])
                numb = int(content[2])
                # if year is illegal
                if year < self.year_begin or year >= self.year_end:
                    continue
                # update trend info
                self.topic_dict[self.topic]["paper_trend"][year - self.year_begin] = numb
                # update peak info
                if numb > self.numb_max:
                    self.numb_max = numb
                    self.numb_max_year = year
        self.update_paper_info()
        infile.close()

    def get_paper_author_list(self):
        infile_paper_simp = '../results/pub_' + self.query + '.simp'
        infile_paper = open(infile_paper_simp, "r")
        paper_id = ""
        author_list = []
        curline = 0
        for line in infile_paper:
            line = line.replace("\n", "")
            if curline % 4 == 0:
                paper_id = line
            elif curline % 4 == 2:
                author_list = line.split("!")
            elif curline % 4 == 3:
                topiclist = line.split(" ")
                for topic in topiclist:
                    topic = self.keyword2stem(topic)
                    if topic not in self.topic_dict:
                        continue
                    self.topic_dict[topic]["paper_list"][paper_id] = 1
                    for author in author_list:
                        if len(author) <= 0:
                            continue
                        if author not in self.topic_dict[topic]["author_list"]:
                            self.topic_dict[topic]["author_list"][author] = 0
                        self.topic_dict[topic]["author_list"][author] += 1
            curline += 1

    def get_voc_dist(self):
        infile_voc_dist = '../results/vec_' + self.query + '.txt'
        infile = open(infile_voc_dist, 'r')
        line = infile.readline()
        content = line.replace("\n", "").split(" ")
        assert(len(content) == 2)
        linenum = int(content[0])
        vocsize = int(content[1])
        self.w2v_length = vocsize
        for i in range(0, linenum):
            line = infile.readline()
            content = line.replace("\n", "").split(" ")
            topic = self.keyword2stem(content[0])
            if topic not in self.topic_dict:
                continue
            content = content[1: len(content) - 1]
            for i in range(0, len(content)):
                content[i] = float(content[i])
            assert(len(content) == vocsize)
            if len(self.topic_dict[topic]["voc_dist"]) == 0:
                self.topic_dict[topic]["voc_dist"] = content
            else:
                for i in range(0, len(content)):
                    self.topic_dict[topic]["voc_dist"][i] += content[i]
        infile.close()

    def check_factor(self):
        num = 0
        invalid_topics = list()
        for topic in self.topic_dict.keys():
            checked = 1
            if self.topic_dict[topic]["paper_peak_year"] <= 0:
                print("Error! Topic: " + topic + " , paper_peak_year <= 0")
                checked = 0
            if self.topic_dict[topic]["paper_peak_num"] <= 0:
                print("Error! Topic: " + topic + " , paper_peak_num <= 0")
                checked = 0
            if self.topic_dict[topic]["paper_soar_year"] <= 0:
                print("Error! Topic: " + topic + " , paper_soar_year <= 0")
                checked = 0
            if self.topic_dict[topic]["paper_soar_num"] <= 0:
                print("Error! Topic: " + topic + " , paper_soar_num <= 0")
                checked = 0
            if len(self.topic_dict[topic]["paper_list"]) == 0:
                print("Error! Topic: " + topic + " , paper_list empty")
                checked = 0
            if len(self.topic_dict[topic]["author_list"].keys()) == 0:
                print("Error! Topic: " + topic + " , author_list empty")
                checked = 0
            if len(self.topic_dict[topic]["voc_dist"]) == 0:
                print("Error! Topic: " + topic + " , voc_dist empty")
                num += 1
                checked = 0
            if numpy.sum(self.topic_dict[topic]["paper_trend"]) == 0:
                print("Error! Topic: " + topic + " , paper_trend empty")
                checked = 0
            if checked == 0:
                invalid_topics.append(topic)
        print(repr(num) + "/" + repr(len(self.topic_dict.keys())))
        for i in invalid_topics:
            del(self.topic_dict[i])

    def output_topic_dict(self):
        # output
        outfilename = '../results/topic_factor_' + self.query + '.txt'
        outfile = open(outfilename, "w")
        origin_topic_dict = dict()
        for key in self.topic_dict:
            origin_topic_dict[self.stem2keyword[key]] = self.topic_dict[key]
        outfile.write(repr(origin_topic_dict))
        outfile.close()

    def load_diff_list(self, filename):
        diff_list = list()
        freq_list = list()
        content = open(filename).readlines()
        curnum = 0
        for i in content:
            li = i.strip().split(' ')
            if curnum >= self.num_threshold:
                break
            curnum += 1
            diff_list.append((li[0], li[1]))
            freq_list.append((int(li[2]), int(li[3]), int(li[4])))
        return diff_list, freq_list

    def load_human_labeling(self, filename):
        content = open(filename).readlines()
        evolution_label = list()
        non_evolution_label = list()
        for i in content:
            li = i.strip().split(' ')
            if int(li[2]) == 1:
                evolution_label.append((li[0], li[1]))
            elif int(li[2]) == 0:
                non_evolution_label.append((li[0], li[1]))
        print ('loading complete')
        return set(evolution_label), set(non_evolution_label)


    def output_for_FGM(self):
        file_label = '../social_tie/results/' + self.query + '/label.txt'
        file_unlabel = '../social_tie/results/' + self.query + '/unlabel.txt'
        file_mark_label = '../social_tie/results/' + self.query + '/label.mark'
        file_mark_unlabel = '../social_tie/results/' + self.query + '/unlabel.mark'

        diff_file = '../results/diff_' + self.query + '.list'
        label_file = '../views/label/label_' + self.query + '.txt'

        diff_list, freq_list = self.load_diff_list(diff_file)
        evolution_set, non_evolution_set = self.load_human_labeling(label_file)

        for i in self.topic_dict:
            self.topic_dict[i]['paper_list'] = set(self.topic_dict[i]['paper_list'])
            self.topic_dict[i]['author_list'] = set(self.topic_dict[i]['author_list'])

        output_label = open(file_label, 'w')
        output_unlabel = open(file_unlabel, 'w')
        output_mark_label = open(file_mark_label, 'w')
        output_mark_unlabel = open(file_mark_unlabel, 'w')
        rank = 0
        for i in diff_list:
            i0 = self.keyword2stem(i[0])
            i1 = self.keyword2stem(i[1])
            if (i0 not in self.topic_dict) or (i1 not in self.topic_dict):
                rank += 1
                continue

            info0 = self.topic_dict[ i0 ]
            info1 = self.topic_dict[ i1 ]
            # calculate the distance between two topics
            paper_peak_year = info0['paper_peak_year'] - info1['paper_peak_year']
            paper_peak_num = info0['paper_peak_num'] / info1['paper_peak_num']
            paper_soar_year = info0['paper_soar_year'] - info1['paper_soar_year']
            paper_soar_num = info0['paper_soar_num'] / info1['paper_soar_num']
            topic1_2_freq = freq_list[rank][0]
            topic2_1_freq = freq_list[rank][1]
            topic_freq_diff = freq_list[rank][2]
            first_paper_year_diff = info0['first_paper_year'] - info1['first_paper_year']

            voc_dist = 1 - distance.cosine(info0['voc_dist'], info1['voc_dist'])
            trend_sim = 1 - distance.cosine(info0['paper_trend'], info1['paper_trend'])

            overlap = len( info0['paper_list'] & info1['paper_list'] )
            total = len(info0['paper_list']) + len(info1['paper_list']) - overlap
            paper_list_rate = overlap / total

            overlap = len( info0['author_list'] & info1['author_list'] )
            total = len(info0['author_list']) + len(info1['author_list']) - overlap
            author_list_rate = overlap / total

            output = output_label
            output_mark = output_mark_label
            if i in evolution_set:
                output.write('+1')
                output_mark.write(i[0] + ' ' + i[1] + '\n')
            elif i in non_evolution_set:
                output.write('+0')
                output_mark.write(i[0] + ' ' + i[1] + '\n')
            else:
                # if the label is unknown, there is no difference between ?0 and ?1
                output = output_unlabel
                output_mark = output_mark_unlabel
                output.write('?0')
                output_mark.write(i[0] + ' ' + i[1] + '\n')
            output.write(' 1:' + repr(trend_sim) )
            output.write(' 2:' + repr(voc_dist) )
            output.write(' 3:' + repr(paper_list_rate))
            output.write(' 4:' + repr(author_list_rate))
            output.write(' 5:' + repr(paper_peak_year))
            output.write(' 6:' + repr(paper_soar_year))
            # output.write(' 7:' + repr(paper_peak_num) )
            # output.write(' 8:' + repr(paper_soar_num) )
            # output.write(' 7:' + repr(topic1_2_freq) )
            # output.write(' 8:' + repr(topic2_1_freq) )
            output.write(' 7:' + repr(math.log(topic_freq_diff)))
            output.write(' 8:' + repr(first_paper_year_diff))
            output.write('\n')
            rank += 1
        output_label.close()
        output_unlabel.close()
        output_mark_label.close()
        output_mark_unlabel.close()

    def gen_FGM_train_test(self):

        file_label = '../social_tie/results/' + self.query + '/label.txt'
        file_unlabel = '../social_tie/results/' + self.query + '/unlabel.txt'
        mark_label = '../social_tie/results/' + self.query + '/label.mark'
        mark_unlabel = '../social_tie/results/' + self.query + '/unlabel.mark'

        file_train = '../social_tie/results/' + self.query + '/train.txt'
        file_test = '../social_tie/results/' + self.query + '/test.txt'
        mark_train = '../social_tie/results/' + self.query + '/train.mark'
        mark_test = '../social_tie/results/' + self.query + '/test.mark'
        # unlabel_pred = '../social_tie/results/' + self.query + '/unlabel.txt'

        pos = list()
        neg = list()
        label = open(file_label).readlines()
        mark = open(mark_label).readlines()
        for i in range(0, len(label)):
            if label[i][1] == '1':
                pos.append( (label[i], mark[i]) )
            else:
                neg.append( (label[i], mark[i]) )

        shutil.copyfile(file_unlabel, file_train)
        # shutil.copyfile(file_unlabel, unlabel_pred)
        shutil.copyfile(mark_unlabel, mark_train)

        output = open(file_train, 'a')
        for i in range(0, int(len(pos)/2)):
            output.write(pos[i][0])
        for i in range(0, int(len(neg)/2)):
            output.write(neg[i][0])
        output.close()
        
        output = open(file_test, 'w')
        for i in range(int(len(pos)/2), len(pos)):
            output.write(pos[i][0])
        for i in range(int(len(neg)/2), len(neg)):
            output.write(neg[i][0])
        output.close()

        output = open(mark_train, 'a')
        for i in range(0, int(len(pos)/2)):
            output.write(pos[i][1])
        for i in range(0, int(len(neg)/2)):
            output.write(neg[i][1])
        output.close()
        
        output = open(mark_test, 'w')
        for i in range(int(len(pos)/2), len(pos)):
            output.write(pos[i][1])
        for i in range(int(len(neg)/2), len(neg)):
            output.write(neg[i][1])
        output.close()
        

def main():
    # the second parameter is the difff threshold
    ga = GetTopicFactor(sys.argv[1], 100)
    print("init topic")
    ga.init_topic_dict()
    print("paper number")
    ga.get_paper_number()
    # ga.output_topic_dict("../results/topic_factor_data_mining_paper_num.txt")
    print("author list")
    ga.get_paper_author_list()
    print("voc dist")
    ga.get_voc_dist()
    print("check")
    ga.check_factor()
    print("output dict")
    ga.output_topic_dict()
    print("output fgm")
    ga.output_for_FGM()
    print("output tran test")
    ga.gen_FGM_train_test()

if __name__ == '__main__':
    main()
