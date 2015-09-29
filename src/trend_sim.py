# calculate trend similarity

from scipy.spatial import distance


class TrendSim(object):

    """docstring for TrendSim"""

    def __init__(self):
        super(TrendSim, self).__init__()

    def trend_sim(self, infile1, infile2, outfile):
        minyear = 1980
        maxyear = 2014
        timelinefile = open(infile1, "r")
        dictionary = {}
        keyword = ""
        for line in timelinefile:
            line = line.replace("\n", "").split("\t")
            if len(line) > 1:
                year = int(line[1])
                numb = int(line[2])
                if year < minyear or year > maxyear:
                    continue
                dictionary[keyword][year] = numb
            else:
                keyword = line[0]
                dictionary[keyword] = {}
        timelinefile.close()

        dictlist = {}
        for keyword in dictionary.keys():
            dictlist[keyword] = []
            for year in range(minyear, maxyear + 1):
                if year in dictionary[keyword]:
                    dictlist[keyword].append(dictionary[keyword][year])
                else:
                    dictlist[keyword].append(0)

        linkdifffile = open(infile2, "r")
        linklist = []
        for line in linkdifffile:
            line = line.replace("\n", "").split(" ")
            linklist.append(line)
        linkdifffile.close()

        outputfile = open(outfile, "w")
        for i in range(0, len(linklist)):
            key0 = linklist[i][0]
            key1 = linklist[i][1]
            if key0 not in dictlist:
                print("Error!\t" + key0 + "\tdoes not have timeline info")
                continue
            if key1 not in dictlist:
                print("Error!\t" + key1 + "\tdoes not have timeline info")
                continue
            outputfile.write(linklist[i][0] + " " + linklist[i][1] + " " +
                             linklist[i][2] + " " + linklist[i][3] + " " +
                             linklist[i][4] + " ")
            sim = 1 - distance.cosine(dictlist[key0], dictlist[key1])
            outputfile.write(repr(sim) + '\n')
        outputfile.close()


def main():
    alg1 = TrendSim()
    alg1.trend_sim("../results/publication_time.keywords",
                   "../results/link_diff.list",
                   "../results/link_diff_trend_sim.list")

if __name__ == '__main__':
    main()
