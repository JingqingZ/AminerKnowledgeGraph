# calculate trend similarity

from stemming.porter2 import stem
from scipy.spatial import distance

minyear = 1990
maxyear = 2014
timelinefile = open("../results/publication_time.keywords", "r")
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
        keyword = stem(line[0])
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

linkdifffile = open("../results/link_diff.list", "r")
linklist = []
for line in linkdifffile:
    line = line.replace("\n", "").split(" ")
    linklist.append(line)
linkdifffile.close()

outputfile = open("../results/link_diff_trend_sim.list", "w")
for i in range(0, len(linklist)):
    key0 = stem(linklist[i][0])
    key1 = stem(linklist[i][1])
    if key0 not in dictlist:
        print(key0 + "\tdoes not have timeline info")
        continue
    if key1 not in dictlist:
        print(key1 + "\tdoes not have timeline info")
        continue
    outputfile.write(linklist[i][0] + " " + linklist[i][1] + " " +
                     linklist[i][2] + " " + linklist[i][3] + " " +
                     linklist[i][4] + " ")
    sim = 1 - distance.cosine(dictlist[key0], dictlist[key1])
    outputfile.write(repr(sim) + '\n')
outputfile.close()
