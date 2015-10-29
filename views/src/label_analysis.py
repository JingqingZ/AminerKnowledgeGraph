from stemming.porter2 import stem
import sys


class LabelAnalysis(object):
    """docstring for LabelAnalysis"""

    def __init__(self, q):
        super(LabelAnalysis, self).__init__()
        self.query = q
        self.topic_table = {}
        self.link_label = {}

    def load_topic_table(self):
        infile = open("../../results/pub_" + self.query + ".dist", "r")
        for line in infile:
            line = line.replace("\n", "").split("\t")
            if len(line) > 1:
                continue
            else:
                keyword = stem(line[0])
                self.topic_table[keyword] = line[0]
        infile.close()

    def load_link_label(self, infilename1, infilename2):
        infile1 = open(infilename1, 'r')
        infile2 = open(infilename2, 'r')
        for line in infile1:
            content = line.replace("\n", "").split(" ")
            assert(len(content) == 3)
            assert(content[0] in self.topic_table)
            assert(content[1] in self.topic_table)
            key0 = self.topic_table[content[0]]
            key1 = self.topic_table[content[1]]
            key = key0 + "!" + key1
            assert(key not in self.link_label)
            self.link_label[key] = {}
            self.link_label[key]["1"] = content[2]
        for line in infile2:
            content = line.replace("\n", "").split(" ")
            assert(len(content) == 3)
            assert(content[0] in self.topic_table)
            assert(content[1] in self.topic_table)
            key0 = self.topic_table[content[0]]
            key1 = self.topic_table[content[1]]
            key = key0 + "!" + key1
            assert(key in self.link_label)
            assert("1" in self.link_label[key])
            self.link_label[key]["2"] = content[2]
        infile1.close()
        infile2.close()

    def output(self, outfilename_sim, outfilename_diff):
        outfile_sim = open(outfilename_sim, 'w')
        outfile_diff = open(outfilename_diff, "w")
        for key in self.link_label.keys():
            assert("1" in self.link_label[key])
            assert("2" in self.link_label[key])
            if self.link_label[key]["1"] == self.link_label[key]["2"]:
                outfile_sim.write(key.replace("!", " ") + " " +
                                  self.link_label[key]["1"] + "\n")
            else:
                outfile_diff.write(key.replace("!", " ") + " " +
                                   self.link_label[key]["1"] + " " +
                                   self.link_label[key]["2"] + "\n")
        outfile_sim.close()
        outfile_diff.close()


def main():
    la = LabelAnalysis(sys.argv[1])
    la.load_topic_table()
    la.load_link_label("../label/TianrunSim.txt", "../label/JingqingSim.txt")
    la.output("../label/sim.txt", "../label/diff.txt")


if __name__ == '__main__':
    main()
