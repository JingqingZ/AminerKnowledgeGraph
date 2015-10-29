import numpy
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

        self.diff_threshold = 10
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

    def output_for_FGM(self, diff_list, filename):
        factor_result = dict()
        for i in self.topic_dict:
            self.topic_dict[i]['paper_list'] = set(self.topic_dict[i]['paper_list'])
            self.topic_dict[i]['author_list'] = set(self.topic_dict[i]['author_list'])

        for i in diff_list:
            if (i[0] not in self.topic_dict) or (i[1] not in self.topic_dict):
                continue

            if i not in factor_result:
                factor_result[i] = dict()

            info0 = self.topic_dict[ i[0] ]
            info1 = self.topic_dict[ i[1] ]
            # calculate the distance between two topics
            factor_result[i]['paper_peak_year'] = info0['paper_peak_year'] \
                                                    - info1['paper_peak_year']
            factor_result[i]['paper_peak_num'] = info0['paper_peak_num'] \
                                                    - info1['paper_peak_num']
            factor_result[i]['paper_soar_year'] = info0['paper_soar_year'] \
                                                    - info1['paper_soar_year']
            factor_result[i]['paper_soar_num'] = info0['paper_soar_num'] \
                                                    - info1['paper_soar_num']
            factor_result[i]['voc_dist'] = [ info0['voc_dist'][it] \
                                             - info1['voc_dist'][it] for it in range(0, self.w2v_length)]
            factor_result[i]['paper_list_cnt'] = len( info0['paper_list'] & info1['paper_list'] )
            factor_result[i]['author_list_cnt'] = len( info0['author_list'] & info1['author_list'] )
            factor_result[i]['trend_sim'] = 1 - distance.cosine(info0['paper_trend'], info1['paper_trend'])

            # here should load the label from human labeling
            factor_result[i]['label'] = '1'

        output = open(filename, 'w')
        for i in factor_result:
            output.write('+' + factor_result[i]['label'])
            output.write(' 1:' + repr(factor_result[i]['paper_peak_year']))
            output.write(' 2:' + repr(factor_result[i]['paper_peak_num']))
            output.write(' 3:' + repr(factor_result[i]['paper_soar_year']))
            output.write(' 4:' + repr(factor_result[i]['paper_soar_num']))
            output.write(' 5:' + repr(factor_result[i]['paper_list_cnt']))
            output.write(' 6:' + repr(factor_result[i]['author_list_cnt']))
            output.write(' 7:' + repr(factor_result[i]['trend_sim']))
            start = 8
            for attr_num in range(0, self.w2v_length):
                output.write(' %d:' % (attr_num + start))
                output.write( repr(factor_result[i]['voc_dist'][attr_num]) )
            output.write('\n')
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
    diff_list = ga.load_diff_list('../results/diff_data_mining.list')
    ga.output_for_FGM(diff_list, '../results/FGM_data_mining.txt')

if __name__ == '__main__':
    main()
