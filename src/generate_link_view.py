# generate labeled view

import sys


class LabelResultsHTMLGenerate(object):
    """docstring for LabelResultsHTMLGenerate"""
    def __init__(self, q, t):
        super(LabelResultsHTMLGenerate, self).__init__()
        self.query = q.replace(" ", "_")
        self.keydict = dict()
        self.linkdict = dict()
        self.labellist = list()
        self.labeldict = dict()
        self.minyear = 1980
        self.maxyear = 2014
        self.type = ""
        if t == "label":
            self.type = "_label"
        elif t == "pred":
            self.type = "_pred"
        elif t == "all":
            self.type = ""

    def load_files(self):
        timelinefile = open("../results/pub_" + self.query + ".dist", "r")
        self.keydict = {}
        keyword = ""
        for line in timelinefile:
            line = line.replace("\n", "").split("\t")
            if len(line) > 1:
                year = int(line[1])
                numb = int(line[2])
                if year < self.minyear or year > self.maxyear:
                    continue
                self.keydict[keyword][year] = numb
            else:
                keyword = line[0]
                self.keydict[keyword] = {}
        timelinefile.close()

        linkdifffile = open("../results/trend_sim_" + self.query + ".list", "r")
        self.linkdict = {}
        for line in linkdifffile:
            line = line.replace("\n", "").split(" ")
            assert(len(line) == 6)
            link = line[0] + "!" + line[1]
            assert(link not in self.linkdict)
            self.linkdict[link] = {}
            self.linkdict[link]["freq12"] = line[2]
            self.linkdict[link]["freq21"] = line[3]
            self.linkdict[link]["freqdiff"] = line[4]
            self.linkdict[link]["trendsim"] = line[5]
        linkdifffile.close()

        labelfile = open("../views/pattern_analysis/results/" + self.query + "/results" + self.type + ".txt", 'r')
        self.labellist = []
        self.labeldict = {}
        for line in labelfile:
            content = line.replace("\n", "").split(" ")
            assert(content[1] in self.keydict)
            assert(content[2] in self.keydict)
            link = content[1] + "!" + content[2]
            assert(link in self.linkdict)
            assert(link not in self.labeldict)
            self.labeldict[link] = content[3]
            self.labellist.append(link)
        labelfile.close()

    def gen_html(self):
        self.htmlfile = open("../views/pattern_analysis/results/" + self.query + "/views" + self.type + ".html", "w")
        self.htmlfile.write('<html><head>')
        jsfile = open("../views/static/jquery-1.8.2.min.js", 'r')
        self.htmlfile.write('<script>')
        for line in jsfile:
            self.htmlfile.write(line)
        self.htmlfile.write('</script>')
        jsfile.close()
        jsfile = open("../views/static/raphael-min.js", 'r')
        self.htmlfile.write('<script>')
        for line in jsfile:
            self.htmlfile.write(line)
        self.htmlfile.write('</script>')
        jsfile.close()
        jsfile = open("../views/static/morris-0.4.1.min.js", 'r')
        self.htmlfile.write('<script>')
        for line in jsfile:
            self.htmlfile.write(line)
        self.htmlfile.write('</script>')
        jsfile.close()

        self.htmlfile.write('<meta charset=utf-8 /><title>' + sys.argv[1] + '</title></head><body>')
        self.htmlfile.write('<p>说明：手动标注结果展示</p>')
        self.htmlfile.write('<p  style="margin-top: 100px">----------------------------------------------------------------------------------------------------------------------------------------------------------------</p>')
        for i in range(len(self.labellist)):
            link = self.labellist[i]
            key = link.split("!")
            if self.labeldict[link] == '1':
                self.htmlfile.write('<p> !!! ' + key[0] + ' --> ' + key[1] + '</p>')
            elif self.labeldict[link] == '-1':
                tmp = key[0]
                key[0] = key[1]
                key[1] = tmp
                self.htmlfile.write('<p> !!! ' + key[0] + ' --> ' + key[1] + '</p>')
            elif self.labeldict[link] == '0':
                self.htmlfile.write('<p> xxx ' + key[0] + '  ' + key[1] + '</p>')
            self.htmlfile.write('<p> frequency ' + self.linkdict[link]['freq12'] + ' ' + self.linkdict[link]['freq21'] + ' ' + self.linkdict[link]['freqdiff'] + '</p>')
            self.htmlfile.write('<p> trend similarity ' + self.linkdict[link]['trendsim'] + ' (注：1.0为完全相同) </p>')
            self.htmlfile.write('<div id="link_' + link + '" style="height: 200px; width: 80%"></div>')
            self.htmlfile.write('<script id="jsbin-javascript">')
            self.htmlfile.write('Morris.Line({')
            self.htmlfile.write('element: "link_' + link + '",')
            self.htmlfile.write('data: [')
            for y in range(self.minyear, self.maxyear + 1):
                a = 0
                b = 0
                if y in self.keydict[key[0]]:
                    a = self.keydict[key[0]][y]
                if y in self.keydict[key[1]]:
                    b = self.keydict[key[1]][y]
                self.htmlfile.write('    { y: "' + repr(y) + '", a: ' + repr(a) + ', b: ' + repr(b) + ' },')
            self.htmlfile.write('  ],')
            self.htmlfile.write('  xkey: "y",')
            self.htmlfile.write('  ykeys: ["a", "b"],')
            self.htmlfile.write('  labels: ["' + key[0] + '", "' + key[1] + '"]')
            self.htmlfile.write('});')
            self.htmlfile.write('</script>')
            self.htmlfile.write('<p  style="margin-top: 100px">----------------------------------------------------------------------------------------------------------------------------------------------------------------</p>')
        self.htmlfile.close()


def main():
    hg = LabelResultsHTMLGenerate(sys.argv[1], sys.argv[2])
    hg.load_files()
    hg.gen_html()

if __name__ == '__main__':
    main()