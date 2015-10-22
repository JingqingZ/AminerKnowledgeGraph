import sys
import copy

class GraphSearch(object):
    """docstring for GraphSearch"""
    def __init__(self):
        super(GraphSearch, self).__init__()
        self.root_dir = '../results/'
        self.keynum = 0
        self.edge_counter = 0
        self.min_threshold = 5
        self.p = 0.1

        self.key2num = dict()
        self.num2key = dict()

        # ddv only consists of the neighboring vertices
        self.ddv = dict()
        self.answer = set()

        self.graph = list()
        self.dv = list()
        self.tv = list()

    def load_one_diff_file(self, q):
        query = q.replace(' ', '_')
        filename = self.root_dir + 'diff_' + query + '.list'
        content = open(filename).readlines()
        for line in content:
            li = line.strip().split(' ')
            # remove edges with too little correlation
            if int(li[4]) <= self.min_threshold:
                continue
            if li[0] not in self.key2num:
                self.key2num[ li[0] ] = self.keynum
                self.num2key[self.keynum] = li[0]
                self.keynum += 1
            if li[1] not in self.key2num:
                self.key2num[ li[1] ] = self.keynum
                self.num2key[self.keynum] = li[1]
                self.keynum += 1
            from_num = self.key2num[ li[0] ]
            to_num = self.key2num[ li[1] ]
            # currently use undirected graph
            # (A -> B) and (B -> A)
            if len(self.graph) <= from_num:
                self.graph.append( {to_num} )
            else:
                self.graph[from_num].add( to_num )

            if len(self.graph) <= to_num:
                self.graph.append( {from_num} )
            else:
                self.graph[to_num].add( from_num )
            self.edge_counter += 1

    def load_diff_files(self, file_list):
        for q in file_list:
            self.load_one_diff_file(q)
        print ('load %d vertices, %d edges' % (len(self.graph), self.edge_counter) )
        print ('preprocessing')
        self.tv = [0] * len(self.graph)
        self.dv = [0] * len(self.graph)
        for i in range(0, len(self.graph)):
            self.graph[i] = list(self.graph[i])
            self.dv[i] = len(self.graph[i])

    def update_tv_ddv(self, query_num):
        # update all the neighbor vertices
        for i in self.graph[query_num]:
            if i not in self.answer:
                self.tv[i] += 1
                self.ddv[i] = self.dv[i] - 2 * self.tv[i] - (self.dv[i] - self.tv[i]) * self.tv[i] * self.p
                # or use the original degree discount algorithm:
                #self.ddv[i] = self.dv[i] - self.tv[i]

    def get_max_ddv(self):
        # get the vertix with max ddv, currently do not use fibonacci heap
        # because we are not doing influence maximization on whole graph
        max_deg = -1
        which = -1
        for key in self.ddv:
            if self.ddv[key] > max_deg:
                max_deg = self.ddv[key]
                which = key
        if which != -1:
            del(self.ddv[which])
            return which
        else:
            print ('!!!!!!!!!!!!!!!!!!!!!!error!!!!!!!!!!!!!!!!!!!!!!')
            return -1

    def degree_discount_IC(self, q, k):
        query = q.replace(' ', '_')
        if query not in self.key2num:
            print ('query is not in current graph')
            return

        query_num = self.key2num[query]
        self.answer.add(query_num)

        for num_iter in range(0, k):
            self.update_tv_ddv(query_num)
            query_num = self.get_max_ddv()
            self.answer.add(query_num)
            print ('dv : %d,    tv : %d' % (self.dv[query_num], self.tv[query_num]))
        print (len(self.ddv))
        self.show_answer(q)

    def show_answer(self, q):
        print (q)
        print ('-----------------------------------')
        for i in self.answer:
            print (self.num2key[i])
        print ('-----------------------------------')

def main():
    gs = GraphSearch()
    file_list = ['data mining',
                'database',
                'machine learning']
    gs.load_diff_files(file_list)
    gs.degree_discount_IC(sys.argv[1], 15)

if __name__ == '__main__':
    main()
