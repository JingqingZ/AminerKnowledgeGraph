# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# algorithm 1 find links between keywords        					  #
# 																	  #
# input1: publication keyword link                                    #
# 	fetch top 100 frequent keywords 								  #
# 																	  #
# input2: publication list, each publication have the following info: #
#   line1: year                                                       #
#   line2: authors list (divided by '!')							  #
#   line3: keywords list (divided by space 							  #
#   		and each keyword use '_' to divide different words)		  #
# 																	  #
# output1: author year keywords list								  #
# format:															  #
# 		author1 number												  #
#   		year1 key1 key2 ...										  #
#   		year2 key2 key3 ...										  #
#   		...													  	  #
#   	author2 number ...											  #
# 																	  #
# output2: author keyword link      								  #
# format:															  #
#   	author1	number												  #
#   		key1 key2 (year1,year1+1) (year2,year2+1)				  #
#   		key2 key3 (year3,year3+1) (year4,year4+1)				  #
#   		...														  #
# 		author2 number ...											  #
# 																	  #
# output3: keyword link sorted by confidence  						  #
# format:															  #
#   	key1 key2 number confidence									  #
#   	...															  #
# confidence: percent of authors who have the (key1, key2) link       #
# 																	  #
# output4: keyword link sorted by difference  						  #
# format:															  #
#   	key1 key2 number1 number2 difference						  #
#   	...															  #
# confidence: percent of authors who have the (key1, key2) link       #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

import operator
from stemming.porter2 import stem

# stemmed keywords dictionary
# {stemmed_keyword1: ..., stemmed_keyword2: ...}
keyword_stem_dictionary = {}
# stemmed keywords to its origin keywords dictionary
# {stemmed_keyword1: keyword1, ...}
stemm2keywords_dictionary = {}

print("Loading top 100 keywords from publication.keywords file")
curline = 0
infile1 = open("../results/publication.keywords", 'r')
for line in infile1:
    if curline >= 100:
        break
    line = line.split("\t")
    keyword_stem = stem(line[0])
    keyword_stem_dictionary[keyword_stem] = 1
    stemm2keywords_dictionary[keyword_stem] = line[0]
    curline += 1
infile1.close()

# {author: {year: {keyword: ...}, ...}, ...}
overall_dictionary = {}
print("Initializing overall dictionary from publication_simplified.data file")
curline = 0
curyear = 0
curauthorlist = []
curkeywordslist = []
skip = False
infile2 = open("../results/publication_simplified.data", 'r')
for line in infile2:
    if curline % 10000 == 0:
        print(curline)
    if skip:
        curline += 1
        if curline % 3 == 0:
            skip = False
        continue
    if curline % 3 == 0:
        curyear = int(line)
        if curyear < 1800 or curyear > 2014:  # illegal
            skip = True
    elif curline % 3 == 1:
        curauthorlist = line.replace("\n", "").split("!")
        if len(curauthorlist) == 1 and len(curauthorlist[0]) == 0:
            skip = True
    else:
        curkeywordslist = line.replace("\n", "").split(" ")
        if len(curkeywordslist) == 1 and len(curkeywordslist[0]) == 0:
            skip = True
        else:
            # build overall_dictionary
            for author in curauthorlist:
                if author == '':
                    continue
                if author not in overall_dictionary:
                    overall_dictionary[author] = {}
                if curyear not in overall_dictionary[author]:
                    overall_dictionary[author][curyear] = {}
                for keyword in curkeywordslist:
                    keyword_stem = stem(keyword)
                    if keyword_stem not in keyword_stem_dictionary:
                        continue
                    if keyword_stem not in overall_dictionary[author][curyear]:
                        overall_dictionary[author][curyear][keyword_stem] = 1
    curline += 1
infile2.close()


print("Output1: overall dictionary to author_year_keywords.list file")
outfile1 = open("../results/author_year_keywords.list", 'w')
for author in overall_dictionary.keys():
    outfile1.write(author + " " +
                   repr(len(overall_dictionary[author].keys())) + "\n")
    sorted_year_dict = sorted(overall_dictionary[author].items(),
                              key=operator.itemgetter(0))
    for i in range(0, len(sorted_year_dict)):
        outfile1.write("\t" + repr(sorted_year_dict[i][0]) + " ")
        for keyword_stem in sorted_year_dict[i][1].keys():
            outfile1.write(stemm2keywords_dictionary[keyword_stem] + " ")
        outfile1.write("\n")
outfile1.close()

# author keyword link dictionary
# {author: { key1!key2: [year1, year2, ...], ...}, ...}
author_keyword_dictionary = {}
print("Computing keyword links of each author")
for author in overall_dictionary.keys():
    if author not in author_keyword_dictionary:
        author_keyword_dictionary[author] = {}
    for year_begin in overall_dictionary[author]:
        # change from (year, year+1) to (year1, year2)
        for year_end in overall_dictionary[author]:
            if year_end > year_begin:
                for key1 in overall_dictionary[author][year_begin]:
                    for key2 in overall_dictionary[author][year_end]:
                        if key1 == key2:
                            continue
                        link = key1 + "!" + key2
                        if link not in author_keyword_dictionary[author]:
                            author_keyword_dictionary[author][link] = []
                        author_keyword_dictionary[author][link].append(year_begin * 4096 + year_end)

print("Output2: keyword link of each author to link_author.list file")
outfile2 = open("../results/link_author.list", 'w')
for author in author_keyword_dictionary.keys():
    outfile2.write(author + " " +
                   repr(len(author_keyword_dictionary[author].keys())) + "\n")
    for link in author_keyword_dictionary[author].keys():
        keys = link.split("!")
        outfile2.write("\t" + stemm2keywords_dictionary[keys[0]] + " " +
                       stemm2keywords_dictionary[keys[1]] + " ")
        for year in author_keyword_dictionary[author][link]:
            outfile2.write("(" + repr(year//4096) + "," + repr(year % 4096) + ") ")
        outfile2.write("\n")
outfile2.close()


# link dictionary
# {key1!key2: number, ...}
link_dictionary = {}
author_num = 0
for author in author_keyword_dictionary.keys():
    author_num += (len(author_keyword_dictionary[author].keys()) > 0)
    for link in author_keyword_dictionary[author].keys():
        if link not in link_dictionary:
            link_dictionary[link] = 0
        link_dictionary[link] += 1
sorted_link_dictionary = sorted(link_dictionary.items(),
                                key=operator.itemgetter(1))

print("Output3: keyword link link.list file")
outfile3 = open("../results/link.list", 'w')
for i in range(len(sorted_link_dictionary) - 1, -1, -1):
    keys = sorted_link_dictionary[i][0].split("!")
    outfile3.write(stemm2keywords_dictionary[keys[0]] + " " +
                   stemm2keywords_dictionary[keys[1]] + " " +
                   repr(sorted_link_dictionary[i][1]) + " " +
                   repr(sorted_link_dictionary[i][1] / author_num) + "\n")
outfile3.close()


# link difference dictionary
# {key1!key2: difference, ...}
link_diff_dictionary = {}
for author in author_keyword_dictionary.keys():
    for link in author_keyword_dictionary[author].keys():
        keys = link.split("!")
        reverse_link = keys[1] + "!" + keys[0]
        positive_direct = ""
        positive_diff = 0
        if reverse_link not in link_dictionary:
            positive_direct = link
            positive_diff = link_dictionary[link]
        elif link_dictionary[link] >= link_dictionary[reverse_link]:
            positive_direct = link
            positive_diff = link_dictionary[link] - link_dictionary[reverse_link]
        else:
            positive_direct = reverse_link
            positive_diff = link_dictionary[reverse_link] - link_dictionary[link]
        if link not in link_diff_dictionary and reverse_link not in link_diff_dictionary:
            link_diff_dictionary[positive_direct] = positive_diff
sorted_link_diff_dictionary = sorted(link_diff_dictionary.items(),
                                     key=operator.itemgetter(1))

print("Output4: keyword link link_diff.list file")
outfile4 = open("../results/link_diff.list", 'w')
for i in range(len(sorted_link_diff_dictionary) - 1, -1, -1):
    keys = sorted_link_diff_dictionary[i][0].split("!")
    link = sorted_link_diff_dictionary[i][0]
    reverse_link = keys[1] + "!" + keys[0]
    reverse_num = 0
    if reverse_link in link_dictionary:
        reverse_num = link_dictionary[reverse_link]
    outfile4.write(stemm2keywords_dictionary[keys[0]] + " " +
                   stemm2keywords_dictionary[keys[1]] + " " +
                   repr(link_dictionary[link]) + " " +
                   repr(reverse_num) + " " +
                   repr(sorted_link_diff_dictionary[i][1]) + "\n")
outfile4.close()

