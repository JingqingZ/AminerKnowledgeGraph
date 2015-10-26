import ast
import numpy
from scipy.spatial.distance import cosine


class GetLinkFactor(object):
    """docstring for GetLinkFactor"""

    def __init__(self):
        super(GetLinkFactor, self).__init__()
        self.link_dict = {}
        self.topic_dict = {}

    def read_topic(self, infilename):
        infile = open(infilename, "r")
        line = infile.readline()
        self.topic_dict = ast.literal_eval(line)
        infile.close()
        for topic in self.topic_dict.keys():
            self.topic_dict[topic]["valid"] = self.check_topic(topic)

    def check_topic(self, topic):
        if topic not in self.topic_dict:
            print("Error! Topic: " + topic + " , not in topic dict!")
            return False
        if self.topic_dict[topic]["paper_peak_year"] <= 0:
            print("Error! Topic: " + topic + " , paper_peak_year <= 0")
            return False
        if self.topic_dict[topic]["paper_peak_num"] <= 0:
            print("Error! Topic: " + topic + " , paper_peak_num <= 0")
            return False
        if self.topic_dict[topic]["paper_soar_year"] <= 0:
            print("Error! Topic: " + topic + " , paper_soar_year <= 0")
            return False
        if self.topic_dict[topic]["paper_soar_num"] <= 0:
            print("Error! Topic: " + topic + " , paper_soar_num <= 0")
            return False
        if len(self.topic_dict[topic]["paper_list"]) == 0:
            print("Error! Topic: " + topic + " , paper_list empty")
            return False
        if len(self.topic_dict[topic]["author_list"].keys()) == 0:
            print("Error! Topic: " + topic + " , author_list empty")
            return False
        if len(self.topic_dict[topic]["voc_dist"]) == 0:
            print("Error! Topic: " + topic + " , voc_dist empty")
            return False
        if numpy.sum(self.topic_dict[topic]["paper_trend"]) == 0:
            print("Error! Topic: " + topic + " , paper_trend empty")
            return False
        return True

    def trend_sim(self, topic1, topic2):
        # 1 same
        vec1 = self.topic_dict[topic1]["paper_trend"]
        vec2 = self.topic_dict[topic2]["paper_trend"]
        return 1 - cosine(vec1, vec2)

    def paper_both(self, topic1, topic2):
        # compute rate of papers that have both topics
        overlap = 0
        for paper in self.topic_dict[topic1]["paper_list"].keys():
            if paper in self.topic_dict[topic2]["paper_list"]:
                overlap += 1
        total = len(self.topic_dict[topic1]["paper_list"].keys()) + \
            len(self.topic_dict[topic2]["paper_list"].keys()) - \
            overlap
        return overlap / total

    def author_both(self, topic1, topic2):
        # compute rate of authors that write both topics
        overlap = 0
        for author in self.topic_dict[topic1]["author_list"].keys():
            if author in self.topic_dict[topic2]["author_list"]:
                overlap += 1
        total = len(self.topic_dict[topic1]["author_list"].keys()) + \
            len(self.topic_dict[topic2]["author_list"].keys()) - \
            overlap
        return overlap / total

    def voc_dist_sim(self, topic1, topic2):
        # compute vocabulary distribution similarity
        vec1 = self.topic_dict[topic1]["voc_dist"]
        vec2 = self.topic_dict[topic2]["voc_dist"]
        return 1 - cosine(vec1, vec2)

    def read_link(self, infilename):
        NUM = 300
        curline = 0
        infile = open(infilename, "r")
        for line in infile:
            if curline >= NUM:
                break
            content = line.split(" ")
            assert(len(content) == 5)
            link = content[0] + "!" + content[1]
            assert(link not in self.link_dict)
            self.link_dict[link] = {}
            self.link_dict[link]["valid"] = \
                self.topic_dict[content[0]]["valid"] and \
                self.topic_dict[content[1]]["valid"]
            if self.link_dict[link]["valid"] is False:
                continue
            self.link_dict[link]["topic1_2_freq"] = int(content[2])
            self.link_dict[link]["topic2_1_freq"] = int(content[3])
            self.link_dict[link]["paper_peak_year_diff"] = \
                self.topic_dict[content[1]]["paper_peak_year"] - \
                self.topic_dict[content[0]]["paper_peak_year"]
            self.link_dict[link]["paper_soar_year_diff"] = \
                self.topic_dict[content[1]]["paper_soar_year"] - \
                self.topic_dict[content[0]]["paper_soar_year"]
            self.link_dict[link]["paper_trend_sim"] = self.trend_sim(content[0], content[1])
            self.link_dict[link]["paper_both_rate"] = self.paper_both(content[0], content[1])
            self.link_dict[link]["author_both_rate"] = self.author_both(content[0], content[1])
            self.link_dict[link]["voc_distribution_sim"] = self.voc_dist_sim(content[0], content[1])
            curline += 1
        infile.close()

    def output(self, outfilename):
        # output
        outfile = open(outfilename, "w")
        outfile.write(repr(self.link_dict))
        outfile.close()


def main():
    ga = GetLinkFactor()
    print("topic initializing")
    ga.read_topic("../results/topic_factor_data_mining.txt")
    print("link initializing")
    ga.read_link("../results/diff_data_mining.list")
    print("outputing")
    ga.output("../results/link_factor_data_mining.txt")


if __name__ == '__main__':
    main()
