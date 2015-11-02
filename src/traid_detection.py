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

    def load_evolution_file(self, filename):
        # load evolution from one file
        content = open(filename).readlines()
        for i in content:
            li = i.strip().split(' ')
            if int(li[2]) == 0:
                continue
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
        self.gen_num2key()

    def gen_num2key(self):
        self.num2key = [''] * len(self.key2num)
        for i in self.key2num:
            kid = self.key2num[i]
            self.num2key[kid] = i

    def output_traids(self, filename, op0, op3, cp6):
        output = open(filename, 'w')
        output.write('#----------------------------------------------------------------------\n')
        output.write('#open_traid_0\n')
        output.write('#format is (from_node, to_node1, to_node2)\n')
        for i in op0:
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

    def detect_traid(self, filename):
        # (from, to1, to2)
        open_traid_0 = list()
        # (from, to1, to1_to2)
        close_traid_6 = list()
        for i in self.evolution:
            for num1 in self.evolution[i]:
                for num2 in self.evolution[i]:
                    if num1 in self.evolution and num2 in self.evolution[num1]:
                        close_traid_6.append( (i, num1, num2) )
                    elif num2 in self.evolution and num1 in self.evolution[num2]:
                        close_traid_6.append( (i, num2, num1) )
                    else:
                        open_traid_0.append( (i, num1, num2) )

        # (from1, from2, to)
        open_traid_3 = list()
        for i in self.evolution_reverse:
            for num1 in self.evolution_reverse[i]:
                for num2 in self.evolution_reverse[i]:
                    if num1 in self.evolution_reverse and num2 in self.evolution_reverse[num1]:
                        continue
                    elif num2 in self.evolution_reverse and num1 in self.evolution_reverse[num2]:
                        continue
                    else:
                        open_traid_3.append( (num1, num2, i) )

        self.output_traids(filename, open_traid_0, open_traid_3, close_traid_6)

def main():
    td = TraidDetect('data mining')
    # the input should be label.txt
    td.load_evolution_file('../views/label/label.txt')
    td.detect_traid('../results/data_mining.traid')


if __name__ == '__main__':
    main()
