# merge pub
# import json
import ast

infile1 = open("pub.data", 'r')
infile2 = open("pub2.data", 'r')
outfile = open("publication.data", 'w')
error = open("err.txt", "w")
cur = 0
for line in infile2:
    if cur % 1000 == 0:
        print(cur)
    cur += 1
    try:
        results = ast.literal_eval(line)
        outfile.write(line)
    except Exception as err:
        error.write(repr(cur) + '\n')
        error.write(line + '\n')
        error.write(repr(err) + '\n')
        continue
for line in infile1:
    if cur % 1000 == 0:
        print(cur)
    cur += 1
    try:
        results = ast.literal_eval(line)
        outfile.write(line)
    except Exception as err:
        error.write(repr(cur) + '\n')
        error.write(line + '\n')
        error.write(repr(err) + '\n')
        continue
outfile.close()
error.close()
