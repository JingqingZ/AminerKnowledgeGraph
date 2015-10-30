import numpy
import shutil
from scipy.spatial import distance

class GetTopicFactor(object):
    """docstring for GetTopicFactor"""

    def __init__(self):
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

        self.diff_threshold = 27
        self.w2v_length = 200

    def init_topic_dict(self, infile_topic):
        infile = open(infile_topic)
        curline = 0
        for line in infile:
            if curline >= self.topic_num:
                break
            content = line.split("\t")
            topic = content[0]
            self.topic_dict[topic] = {}
            # initialize factors
            paper_trend = []
            for year in range(self.year_begin, self.year_end):
                paper_trend.append(0)
            self.topic_dict[topic]["paper_trend"] = paper_trend
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
            self.topic_dict[self.topic]["paper_soar_year"] = self.soar_max_year
            self.topic_dict[self.topic]["paper_soar_num"] = self.soar_max
            self.soar_max = -1
            self.soar_max_year = 0

    def get_paper_number(self, infile_pub_dist):
        # range of year: [1980, 2015)
        # get the year when the number of
        #   papers that have a certain topic reaches the peak
        # get the year when the number of
        #   papers that have a certain topic grows fastest
        # get the trend of a certain topic
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
                self.topic = content[0]
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

    def get_paper_author_list(self, infile_paper_simp):
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

    def get_voc_dist(self, infile_voc_dist):
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
            topic = content[0]
            if topic not in self.topic_dict:
                continue
            content = content[1: len(content) - 1]
            for i in range(0, len(content)):
                content[i] = float(content[i])
            assert(len(content) == vocsize)
            assert(len(self.topic_dict[topic]["voc_dist"]) == 0)
            self.topic_dict[topic]["voc_dist"] = content
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

    def output_topic_dict(self, outfilename):
        # output
        outfile = open(outfilename, "w")
        outfile.write(repr(self.topic_dict))
        outfile.close()

    def load_diff_list(self, filename):
        diff_list = list()
        content = open(filename).readlines()
        for i in content:
            li = i.strip().split(' ')
            if int(li[4]) < self.diff_threshold:
                continue
            else:
                diff_list.append((li[0], li[1]))
        return diff_list

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

    def output_for_FGM(self, file_label, file_unlabel, file_mark_label, file_mark_unlabel):
        diff_list = self.load_diff_list('../results/diff_data_mining.list')
        evolution_set, non_evolution_set = self.load_human_labeling('../views/label/label.txt')

        for i in self.topic_dict:
            self.topic_dict[i]['paper_list'] = set(self.topic_dict[i]['paper_list'])
            self.topic_dict[i]['author_list'] = set(self.topic_dict[i]['author_list'])

        output_label = open(file_label, 'w')
        output_unlabel = open(file_unlabel, 'w')
        output_mark_label = open(file_mark_label, 'w')
        output_mark_unlabel = open(file_mark_unlabel, 'w')
        for i in diff_list:
            if (i[0] not in self.topic_dict) or (i[1] not in self.topic_dict):
                continue

            info0 = self.topic_dict[ i[0] ]
            info1 = self.topic_dict[ i[1] ]
            # calculate the distance between two topics
            paper_peak_year = info0['paper_peak_year'] \
                                - info1['paper_peak_year']
            paper_peak_num = info0['paper_peak_num'] \
                                - info1['paper_peak_num']
            paper_soar_year = info0['paper_soar_year'] \
                                - info1['paper_soar_year']
            paper_soar_num = info0['paper_soar_num'] \
                                - info1['paper_soar_num']

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
                output_mark.write(repr(i) + '\n')
            elif i in non_evolution_set:
                output.write('+0')
                output_mark.write(repr(i) + '\n')
            else:
                # if the label is unknown, there is no difference between ?0 and ?1
                output = output_unlabel
                output_mark = output_mark_unlabel
                output.write('?0')
                output_mark.write(repr(i) + '\n')
            output.write(' 1:' + repr(paper_peak_year) )
            output.write(' 2:' + repr(paper_peak_num) )
            output.write(' 3:' + repr(paper_soar_year) )
            output.write(' 4:' + repr(paper_soar_num) )
            output.write(' 5:' + repr(trend_sim) )
            output.write(' 6:' + repr(voc_dist) )
            output.write(' 7:' + repr(paper_list_rate) )
            output.write(' 8:' + repr(author_list_rate) )
            output.write('\n')
        output_label.close()
        output_unlabel.close()
        output_mark_label.close()
        output_mark_unlabel.close()

    def gen_FGM_train_test(self, file_label, file_unlabel, mark_label, mark_unlabel,
                            file_train, file_test, mark_train, mark_test):
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
    ga = GetTopicFactor()
    ga.init_topic_dict("../results/pub_data_mining.keywords")
    ga.get_paper_number("../results/pub_data_mining.dist")
    # ga.output_topic_dict("../results/topic_factor_data_mining_paper_num.txt")
    ga.get_paper_author_list("../results/pub_data_mining.simp")
    ga.get_voc_dist("../results/vec_data_mining.txt")
    ga.check_factor()
    ga.output_topic_dict("../results/topic_factor_data_mining.txt")

    ga.output_for_FGM('../results/FGM_label_data_mining.txt', '../results/FGM_unlabel_data_mining.txt',
                        '../results/FGM_label_data_mining.mark', '../results/FGM_unlabel_data_mining.mark')

    ga.gen_FGM_train_test('../results/FGM_label_data_mining.txt', '../results/FGM_unlabel_data_mining.txt', 
                            '../results/FGM_label_data_mining.mark', '../results/FGM_unlabel_data_mining.mark',
                            '../results/train.txt', '../results/test.txt', 
                            '../results/train.mark', '../results/test.mark')

if __name__ == '__main__':
    main()
