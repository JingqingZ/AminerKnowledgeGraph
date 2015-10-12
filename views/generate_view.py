# generate view

from stemming.porter2 import stem
import sys

class HTMLGenerator(object):
    """docstring for HTMLGenerator"""
    def __init__(self, q):
        super(HTMLGenerator, self).__init__()

        self.query = q.replace(" ", "_")
        self.sim_threshold = 0.85
        self.times_threshold = 10
        self.graph_num = 30

        self.minyear = 1980
        self.maxyear = 2014

        self.reciprocal_times_threshold = 1 / self.times_threshold

    def load_files(self):
        timelinefile = open("../results/pub_" + self.query + ".dist", "r")
        self.dictionary = {}
        keyword = ""
        for line in timelinefile:
            line = line.replace("\n", "").split("\t")
            if len(line) > 1:
                year = int(line[1])
                numb = int(line[2])
                if year < self.minyear or year > self.maxyear:
                    continue
                self.dictionary[keyword][year] = numb
            else:
                keyword = stem(line[0])
                self.dictionary[keyword] = {}
        timelinefile.close()
        
        self.keyword_sum = dict()
        for keyword in self.dictionary:
            counter = 0
            for year in self.dictionary[keyword]:
                counter += self.dictionary[keyword][year]
            self.keyword_sum[keyword] = counter
        
        linkdifffile = open("../results/trend_sim_" + self.query + ".list", "r")
        self.linklist = []
        for line in linkdifffile:
            line = line.replace("\n", "").split(" ")
            self.linklist.append(line)
        linkdifffile.close()

    def judge(self, key0, key1, i):
        if key0 not in self.dictionary or key1 not in self.dictionary:
            return False
        if float(self.linklist[i][5]) > self.sim_threshold:
            return False
        ratio = self.keyword_sum[key0] / self.keyword_sum[key1]
        if ratio > self.times_threshold or ratio < self.reciprocal_times_threshold:
            return False
        return True

    def filter(self):
        # do not generate html file, just filter the correct relationships
        correct_list = list()
        for i in range(0, len(self.linklist)):
            key0 = stem(self.linklist[i][0])
            key1 = stem(self.linklist[i][1])
            if self.judge(key0, key1, i) == False:
                continue
            correct_list.append(i)
        return correct_list

    def gen_html(self):
        self.htmlfile = open(self.query + ".html", "w")
        self.htmlfile.write('<html><head>')
        jsfile = open("static/jquery-1.8.2.min.js", 'r')
        self.htmlfile.write('<script>')
        for line in jsfile:
            self.htmlfile.write(line)
        self.htmlfile.write('</script>')
        jsfile.close()
        jsfile = open("static/raphael-min.js", 'r')
        self.htmlfile.write('<script>')
        for line in jsfile:
            self.htmlfile.write(line)
        self.htmlfile.write('</script>')
        jsfile.close()
        jsfile = open("static/morris-0.4.1.min.js", 'r')
        self.htmlfile.write('<script>')
        for line in jsfile:
            self.htmlfile.write(line)
        self.htmlfile.write('</script>')
        jsfile.close()

        self.htmlfile.write('<meta charset=utf-8 /><title>Knowledge Trend Check</title></head><body>')
        self.htmlfile.write('<div id="results" style="display: none">\n')
        valid = 0
        for i in range(0, len(self.linklist)):
            key0 = stem(self.linklist[i][0])
            key1 = stem(self.linklist[i][1])
            if self.judge(key0, key1, i) == False:
                continue
            valid += 1
            if valid > self.graph_num:
                break
            self.htmlfile.write('<p id="link' + repr(i) + '-results">0</p>\n')
        self.htmlfile.write('</div>\n')
        self.htmlfile.write('<p>说明1：请在你认为正确的衍生关系前打勾</p>')
        self.htmlfile.write('<p>说明2：frequency代表发表的论文中有该先后关系的作者数，仅供参考</p>')
        self.htmlfile.write('<p>说明3：趋势图代表该关键词每年在多少篇论文中有出现，仅供参考</p>')
        self.htmlfile.write('<p>说明4：trend similarity代表两个关键词趋势图的相似性，1.0为完全相同</p>')
        self.htmlfile.write('<p  style="margin-top: 100px">----------------------------------------------------------------------------------------------------------------------------------------------------------------</p>')
        valid = 0
        for i in range(0, len(self.linklist)):
            key0 = stem(self.linklist[i][0])
            key1 = stem(self.linklist[i][1])
            if self.judge(key0, key1, i) == False:
                continue
            valid += 1
            if valid > self.graph_num:
                break
            self.htmlfile.write('<input type="checkbox" id="link' + repr(i) + '-checkbox1"> ' + self.linklist[i][0].replace("_", " ") + ' --> ' + self.linklist[i][1].replace("_", " ") + ' (frequency ' + self.linklist[i][2] + ')<br>')
            self.htmlfile.write('<input type="checkbox" id="link' + repr(i) + '-checkbox2"> ' + self.linklist[i][1].replace("_", " ") + ' --> ' + self.linklist[i][0].replace("_", " ") + ' (frequency ' + self.linklist[i][3] + ')<br>')
            self.htmlfile.write('<p> trend similarity ' + self.linklist[i][5] + ' (注：1.0为完全相同) </p>')
            self.htmlfile.write('<div id="link' + repr(i) + '" style="height: 200px; width: 50%"></div>')
            self.htmlfile.write('<script id="jsbin-javascript">')
            self.htmlfile.write('$("#link' + repr(i) + '-checkbox1").click(function() {')
            self.htmlfile.write('if(document.getElementById("link' + repr(i) + '-checkbox1").checked == true) {')
            self.htmlfile.write('document.getElementById("link' + repr(i) + '-checkbox2").checked = false;')
            self.htmlfile.write('$("#link' + repr(i) + '-results").html("1");')
            self.htmlfile.write('} else {')
            self.htmlfile.write('$("#link' + repr(i) + '-results").html("0");')
            self.htmlfile.write('}')
            self.htmlfile.write('});')
            self.htmlfile.write('$("#link' + repr(i) + '-checkbox2").click(function() {')
            self.htmlfile.write('if(document.getElementById("link' + repr(i) + '-checkbox2").checked == true) {')
            self.htmlfile.write('document.getElementById("link' + repr(i) + '-checkbox1").checked = false;')
            self.htmlfile.write('$("#link' + repr(i) + '-results").html("-1");')
            self.htmlfile.write('} else {')
            self.htmlfile.write('$("#link' + repr(i) + '-results").html("0");')
            self.htmlfile.write('}')
            self.htmlfile.write('});')
            self.htmlfile.write('Morris.Line({')
            self.htmlfile.write('element: "link' + repr(i) + '",')
            self.htmlfile.write('data: [')
            for y in range(self.minyear, self.maxyear + 1):
                a = 0
                b = 0
                if y in self.dictionary[key0]:
                    a = self.dictionary[key0][y]
                if y in self.dictionary[key1]:
                    b = self.dictionary[key1][y]
                self.htmlfile.write('    { y: "' + repr(y) + '", a: ' + repr(a) + ', b: ' + repr(b) + ' },')
            self.htmlfile.write('  ],')
            self.htmlfile.write('  xkey: "y",')
            self.htmlfile.write('  ykeys: ["a", "b"],')
            self.htmlfile.write('  labels: ["' + self.linklist[i][0].replace("_", " ") + '", "' + self.linklist[i][1].replace("_", " ") + '"]')
            self.htmlfile.write('});')
            self.htmlfile.write('</script>')
            self.htmlfile.write('<p  style="margin-top: 100px">----------------------------------------------------------------------------------------------------------------------------------------------------------------</p>')
        self.htmlfile.write('<h2 style="margin-top: 100px"> Finished! Please press Ctrl+S to save this page, and then send the <font color="red">html</font> file back. Great Thanks!</h2></body></html>')
        self.htmlfile.close()

def main():
    hg = HTMLGenerator(sys.argv[1])
    hg.load_files()
    result = hg.filter()
    hg.gen_html()

if __name__ == '__main__':
    main()
