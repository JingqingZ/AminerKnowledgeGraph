import math
import sys
from scipy.spatial import distance
import sys

# detect the traid in topic evolution
# according to TKDE15-Traid Closure Pattern Analysis and Prediction
# There are two kinds of open Traid, and 1 kind of close Traid
class TraidDetect(object):
    """docstring for TraidDetect"""
    def __init__(self, q):
        super(TraidDetect, self).__init__()
        self.query = q.replace(' ', '_')
        self.key2num = dict()
        self.num2key = list()
        self.counter = 0
        # build two graphs:
        # self.evolution: check son using parent
        # self.evolution_reverse: check parent using son
        self.evolution = dict()
        self.evolution_reverse = dict()

    def add_line(self, li):
        if li[0] not in self.key2num:
            self.key2num[ li[0] ] = self.counter
            self.counter += 1
        if li[1] not in self.key2num:
            self.key2num[ li[1] ] = self.counter
            self.counter += 1
        num1 = self.key2num[ li[0] ]
        num2 = self.key2num[ li[1] ]
        if num1 not in self.evolution:
            self.evolution[num1] = [ num2 ]
        else:
            self.evolution[num1].append(num2)
        if num2 not in self.evolution_reverse:
            self.evolution_reverse[num2] = [ num1 ]
        else:
            self.evolution_reverse[num2].append(num1)

    def load_labeled_file(self, skip_char):
        filename = '../views/label/label_' + self.query + '.txt'
        # load evolution from one file
        content = open(filename).readlines()
        for i in content:
            li = i.strip().split(' ')
            if li[2] == skip_char:
                continue
            self.add_line(li)
        self.gen_num2key()

    def load_unlabeled_file(self, filename):
        content = open(filename).readlines()
        for i in content:
            li = i.strip().split(' ')
            self.add_line(li)
        self.gen_num2key()

    def gen_num2key(self):
        self.num2key = [''] * len(self.key2num)
        for i in self.key2num:
            kid = self.key2num[i]
            self.num2key[kid] = i

    def output_traids(self, skip_char, op0, op1, op3, cp6):
        if skip_char == '0':
            filename = '../results/' + self.query + '.traid'
            print ('detect traid: %d op0, %d op1, %d op3, %d cp6' % (len(op0), len(op1), len(op3), len(cp6)) )
        elif skip_char == '1':
            filename = '../results/' + self.query + '.utraid'
            print ('detect untraid: %d op0, %d op1, %d op3, %d cp6' % (len(op0), len(op1), len(op3), len(cp6)) )
        output = open(filename, 'w')
        output.write('#----------------------------------------------------------------------\n')
        output.write('#open_traid_0\n')
        output.write('#format is (from_node, to_node1, to_node2)\n')
        for i in op0:
            output.write('%s %s %s \n' % (self.num2key[i[0]], self.num2key[i[1]], self.num2key[i[2]]) )

        output.write('\n\n\n#----------------------------------------------------------------------\n')
        output.write('#open_traid_1\n')
        output.write('#format is (first_node, second_node, thrid_node)\n')
        for i in op1:
            output.write('%s %s %s \n' % (self.num2key[i[0]], self.num2key[i[1]], self.num2key[i[2]]) )

        output.write('\n\n\n#----------------------------------------------------------------------\n')
        output.write('#open_traid_3\n')
        output.write('#format is (from_node1, from_node2, to_node)\n')
        for i in op3:
            output.write('%s %s %s \n' % (self.num2key[i[0]], self.num2key[i[1]], self.num2key[i[2]]) )

        output.write('\n\n\n#----------------------------------------------------------------------\n')
        output.write('#close_traid_6\n')
        output.write('#format is (from_node, to_node1, to_node1_to_node2)\n')
        for i in cp6:
            output.write('%s %s %s \n' % (self.num2key[i[0]], self.num2key[i[1]], self.num2key[i[2]]) )

        output.close()

    def detect_traid(self):
        # (from, to1, to2)
        open_traid_0 = list()
        # (from, to1, to1_to2)
        close_traid_6 = list()
        for i in self.evolution:
            for num1 in self.evolution[i]:
                for num2 in self.evolution[i]:
                    if num1 in self.evolution and num2 in self.evolution[num1]:
                        close_traid_6.append( (i, num1, num2) )
                    elif num1 > num2:
                        open_traid_0.append( (i, num1, num2) )

        # (first, second, thrid)
        open_traid_1 = list()
        # (A->B->C->A)
        # just for debug, should not occur in evolution
        close_traid_7 = list()
        for first in self.evolution:
            for second in self.evolution[first]:
                if second in self.evolution:
                    for third in self.evolution[second]:
                        if third not in self.evolution[first]:
                            open_traid_1.append( (first, second, third) )
                        if third in self.evolution and first in self.evolution[third]:
                            close_traid_7.append( (first, second, third) )
        if len(close_traid_7) != 0:
            print ('cyclic evolution detected')
            for i in close_traid_7:
                print ('(%s, %s, %s)' % (self.num2key[i[0]], self.num2key[i[1]], self.num2key[i[2]]) )

        # (from1, from2, to)
        open_traid_3 = list()
        for i in self.evolution_reverse:
            for num1 in self.evolution_reverse[i]:
                for num2 in self.evolution_reverse[i]:
                    if num1 in self.evolution_reverse and num2 in self.evolution_reverse[num1]:
                        continue
                    elif num2 in self.evolution_reverse and num1 in self.evolution_reverse[num2]:
                        continue
                    elif num1 > num2:
                        open_traid_3.append( (num1, num2, i) )

        return open_traid_0, open_traid_1, open_traid_3, close_traid_6

    def load_factor_file(self, filename, factor):
        content = open(filename).readlines()
        for i in content:
            li = i.strip().split(' ')
            fli = list()
            for i in range(1, len(li)):
                fli.append( float(li[i].split(':')[1]) )
            factor.append(fli)

    def load_factor(self):
        factor = list()
        filename = '../results/FGM_label_' + self.query + '.txt'
        self.load_factor_file(filename, factor)
        filename = '../results/FGM_unlabel_' + self.query + '.txt'
        self.load_factor_file(filename, factor)
        return factor

    def load_mark_file(self, filename, mark):
        counter = len(mark)
        content = open(filename).readlines()
        for i in content:
            mark[ i.strip() ] = counter
            counter += 1
        
    def load_mark(self):
        mark = dict()
        filename = '../results/FGM_label_' + self.query + '.mark'
        load_mark_file(filename, mark)
        filename = '../results/FGM_unlabel_' + self.query + '.mark'
        load_mark_file(filename, mark)
        return mark

    def output_edge(self, open_traid_0, open_traid_1, open_traid_3, infile, outfile):
        output = open(outfile, 'w')
        mark = dict()
        self.load_mark_file(infile, mark)
        for i in open_traid_0:
            edge1 = '%s %s' % (self.num2key[ i[0] ], self.num2key[ i[1] ])
            edge2 = '%s %s' % (self.num2key[ i[0] ], self.num2key[ i[2] ])
            if edge1 in mark and edge2 in mark:
                output.write('#edge %d %d %d\n' % (mark[edge1], mark[edge2], 1) )

        for i in open_traid_1:
            edge1 = '%s %s' % (self.num2key[ i[0] ], self.num2key[ i[1] ])
            edge2 = '%s %s' % (self.num2key[ i[1] ], self.num2key[ i[2] ])
            if edge1 in mark and edge2 in mark:
                output.write('#edge %d %d %d\n' % (mark[edge1], mark[edge2], 2))

        for i in open_traid_3:
            edge1 = '%s %s' % (self.num2key[ i[0] ], self.num2key[ i[2] ])
            edge2 = '%s %s' % (self.num2key[ i[1] ], self.num2key[ i[2] ])
            if edge1 in mark and edge2 in mark:
                output.write('#edge %d %d %d\n' % (mark[edge1], mark[edge2], 3))
        output.close()

    def output_triangle(self, close_traid_6, infile, outfile):
        output = open(outfile, 'w')
        mark = dict()
        self.load_mark_file(infile, mark)
        for i in close_traid_6:
            edge1 = '%s %s' % (self.num2key[ i[0] ], self.num2key[ i[1] ])
            edge2 = '%s %s' % (self.num2key[ i[0] ], self.num2key[ i[2] ])
            edge3 = '%s %s' % (self.num2key[ i[1] ], self.num2key[ i[2] ])
            if edge1 in mark and edge2 in mark and edge3 in mark:
                output.write('#triangle %d %d %d %d\n' % (mark[edge1], mark[edge2], mark[edge3], 1) )
        output.close()

    def calc_similarity(self, open_traid_0, open_traid_3):
        factor = self.load_factor()

        pair_dict = dict()
        counter = 0
        filename = '../results/FGM_label_' + self.query + '.mark'
        content = open(filename).readlines()
        for i in content:
            pair_dict[i.strip()] = factor[counter]
            counter += 1
        filename = '../results/FGM_unlabel_' + self.query + '.mark'
        content = open(filename).readlines()
        for i in content:
            pair_dict[i.strip()] = factor[counter]
            counter += 1

        pair_list = list()
        for i in open_traid_0:
            pair_list.append( '%s %s' % (self.num2key[ i[1] ], self.num2key[ i[2] ] ) )
        for i in open_traid_3:
            pair_list.append( '%s %s' % (self.num2key[ i[0] ], self.num2key[ i[1] ] ) )

        length = len(factor[0])
        accumulator = [0.0] * length
        counter = 0
        for i in pair_list:
            if i in pair_dict:
                for j in range(0, length):
                    accumulator[j] += pair_dict[i][j]
                counter += 1
        for i in range(0, length):
            accumulator[i] /= counter

        print (accumulator)
        return accumulator

def test(query, skip_char):
    td = TraidDetect(query)
    # the input should be label.txt
    td.load_labeled_file(skip_char)

    open_traid_0, open_traid_1, open_traid_3, close_traid_6 = td.detect_traid()
    td.output_traids(skip_char, open_traid_0, open_traid_1, open_traid_3, close_traid_6)

    return list()

def main():
    '''
    label_avg = test(sys.argv[1], '0')
    unlabel_avg = test(sys.argv[1], '1')
    for i in range(0, len(label_avg)):
        rate = math.fabs(label_avg[i] - unlabel_avg[i]) / math.fabs(label_avg[i] + unlabel_avg[i])
        print (rate)
    '''

    input_file = '../social_tie/results/' + sys.argv[1] + '/' + sys.argv[2] + '.mark'
    output_file = '../social_tie/results/' + sys.argv[1] + '/edges.txt'
    output_triangle_file = '../social_tie/results/' + sys.argv[1] + '/triangles.txt'

    td = TraidDetect(sys.argv[1])
    td.load_unlabeled_file(input_file)
    op0, op1, op3, cp6 = td.detect_traid()
    td.output_edge(op0, op1, op3, input_file, output_file)
    td.output_triangle(cp6, input_file, output_triangle_file)

    append_filename = '../social_tie/results/' + sys.argv[1] + '/' + sys.argv[2] + '.txt'
    append_file = open(append_filename, 'a')
    output = open(output_file, 'r')
    for line in output:
        append_file.write(line)
    append_file.close()
    output.close()

    append_file = open(append_filename, 'a')
    output = open(output_triangle_file, 'r')
    for line in output:
        append_file.write(line)
    append_file.close()
    output.close()
    
if __name__ == '__main__':
    main()
