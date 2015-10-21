data_dir = '../data/'

import ast

infilelist = []

dict = {}
outfile = open(data_dir + 'all.data', "w")
overlapfile = open(data_dir + 'overlap.data', "w")
for query in infilelist:
    filename = data_dir + 'pub_' + query + '.data'
    infile = open(filename, 'r')
    for line in infile:
        publication = ast.literal_eval(line)
        id = publication["id"]
        if id not in dict:
            dict[id] = 1
            outfile.write(line)
        else:
            overlapfile.write(line)
    infile.close()
outfile.close()
overlapfile.close()
