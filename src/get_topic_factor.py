class GetTopicFactor(object):
    """docstring for GetTopicFactor"""
    def __init__(self):
        super(GetTopicFactor, self).__init__()
        self.year_begin = 1980
        self.year_end = 2015
        self.topic_num = 100
        self.topic_dict = {}

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
            self.topic_dict[topic]["paper_list"] = []
            self.topic_dict[topic]["author_list"] = {}
            curline += 1
        infile.close()

    def get_paper_number(self, infile_pub_dist):
        # range of year: [1980, 2015)
        # get the year when the number of
        #   papers that have a certain topic reaches the peak
        # get the year when the number of
        #   papers that have a certain topic grows fastest
        # get the trend of a certain topic
        infile = open(infile_pub_dist, "r")
        topic = ""
        numb_max = -1
        numb_max_year = -1
        soar_max = -1
        soar_max_year = -1
        for line in infile:
            content = line.replace("\n", "").split("\t")
            if len(content) == 1:   # topic
                # update peak info and soar info
                if topic != "":
                    # update and initialize peak info
                    self.topic_dict[topic]["paper_peak_year"] = numb_max_year
                    self.topic_dict[topic]["paper_peak_num"] = numb_max
                    numb_max = -1
                    numb_max_year = 0
                    # update and initialize soar info
                    for year in range(self.year_begin + 1, self.year_end):
                        growth = self.topic_dict[topic]["paper_trend"][year - self.year_begin] - \
                            self.topic_dict[topic]["paper_trend"][year - 1 - self.year_begin]
                        if growth > soar_max:
                            soar_max = growth
                            soar_max_year = year
                    self.topic_dict[topic]["paper_soar_year"] = soar_max_year
                    self.topic_dict[topic]["paper_soar_num"] = soar_max
                    soar_max = -1
                    soar_max_year = 0
                # update and initial new topic factors
                topic = content[0]
                print(topic)
                assert(topic in self.topic_dict)
            else:  # topic distribution
                assert(len(content) == 3)
                year = int(content[1])
                numb = int(content[2])
                # if year is illegal
                if year < self.year_begin or year >= self.year_end:
                    continue
                # update trend info
                self.topic_dict[topic]["paper_trend"][year - self.year_begin] = numb
                # update peak info
                if numb > numb_max:
                    numb_max = numb
                    numb_max_year = year
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
                    self.topic_dict[topic]["paper_list"].append(paper_id)
                    for author in author_list:
                        if author not in self.topic_dict[topic]["author_list"]:
                            self.topic_dict[topic]["author_list"][author] = 0
                        self.topic_dict[topic]["author_list"][author] += 1
            curline += 1

    def output_topic_dict(self, outfilename):
        # output
        outfile = open(outfilename, "w")
        outfile.write(repr(self.topic_dict))
        outfile.close()


def main():
    ga = GetTopicFactor()
    ga.init_topic_dict("../results/pub_data_mining.keywords")
    ga.get_paper_number("../results/pub_data_mining.dist")
    # ga.output_topic_dict("../results/topic_factor_data_mining_paper_num.txt")
    ga.get_paper_author_list("../results/pub_data_mining.simp")
    ga.output_topic_dict("../results/topic_factor_data_mining_paper_author_list.txt")

if __name__ == '__main__':
    main()
