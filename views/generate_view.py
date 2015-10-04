# generate view

from stemming.porter2 import stem

minyear = 1980
maxyear = 2014
timelinefile = open("../results/pub_high_performances_computing.dist", "r")
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

linkdifffile = open("../results/trend_sim_high_performances_computing.list", "r")
linklist = []
for line in linkdifffile:
    line = line.replace("\n", "").split(" ")
    linklist.append(line)
linkdifffile.close()

htmlfile = open("index.html", "w")
htmlfile.write('<html><head><script src="static/raphael-min.js"></script><script src="static/jquery-1.8.2.min.js"></script><script src="static/morris-0.4.1.min.js"></script><meta charset=utf-8 /><title>Knowledge Trend Check</title></head><body>')
htmlfile.write('<div id="results" style="display: none">\n')
valid = 0
for i in range(0, len(linklist)):
    key0 = stem(linklist[i][0])
    key1 = stem(linklist[i][1])
    if key0 not in dictionary or key1 not in dictionary or float(linklist[i][5]) > 0.5:
        continue
    valid += 1
    if valid > 30:
        break
    htmlfile.write('<p id="link' + repr(i) + '-results">0</p>\n')
htmlfile.write('</div>\n')
htmlfile.write('<p>说明1：请在你认为正确的衍生关系前打勾</p>')
htmlfile.write('<p>说明2：frequency代表发表的论文中有该先后关系的作者数，仅供参考</p>')
htmlfile.write('<p>说明3：趋势图代表该关键词每年在多少篇论文中有出现，仅供参考</p>')
htmlfile.write('<p>说明4：trend similarity代表两个关键词趋势图的相似性，1.0为完全相同</p>')
htmlfile.write('<p  style="margin-top: 100px">----------------------------------------------------------------------------------------------------------------------------------------------------------------</p>')
valid = 0
for i in range(0, len(linklist)):
    key0 = stem(linklist[i][0])
    key1 = stem(linklist[i][1])
    if key0 not in dictionary or key1 not in dictionary or float(linklist[i][5]) > 0.5:
        continue
    valid += 1
    if valid > 30:
        break
    htmlfile.write('<input type="checkbox" id="link' + repr(i) + '-checkbox1"> ' + linklist[i][0].replace("_", " ") + ' --> ' + linklist[i][1].replace("_", " ") + ' (frequency ' + linklist[i][2] + ')<br>')
    htmlfile.write('<input type="checkbox" id="link' + repr(i) + '-checkbox2"> ' + linklist[i][1].replace("_", " ") + ' --> ' + linklist[i][0].replace("_", " ") + ' (frequency ' + linklist[i][3] + ')<br>')
    htmlfile.write('<p> trend similarity ' + linklist[i][5] + ' (注：1.0为完全相同) </p>')
    htmlfile.write('<div id="link' + repr(i) + '" style="height: 200px; width: 50%"></div>')
    htmlfile.write('<script id="jsbin-javascript">')
    htmlfile.write('$("#link' + repr(i) + '-checkbox1").click(function() {')
    htmlfile.write('    if(document.getElementById("link' + repr(i) + '-checkbox1").checked == true) {')
    htmlfile.write('        document.getElementById("link' + repr(i) + '-checkbox2").checked = false;')
    htmlfile.write('        $("#link' + repr(i) + '-results").html("1");')
    htmlfile.write('    } else {')
    htmlfile.write('        $("#link' + repr(i) + '-results").html("0");')
    htmlfile.write('    }')
    htmlfile.write('});')
    htmlfile.write('$("#link' + repr(i) + '-checkbox2").click(function() {')
    htmlfile.write('    if(document.getElementById("link' + repr(i) + '-checkbox2").checked == true) {')
    htmlfile.write('        document.getElementById("link' + repr(i) + '-checkbox1").checked = false;')
    htmlfile.write('        $("#link' + repr(i) + '-results").html("-1");')
    htmlfile.write('    } else {')
    htmlfile.write('        $("#link' + repr(i) + '-results").html("0");')
    htmlfile.write('    }')
    htmlfile.write('});')
    htmlfile.write('Morris.Line({')
    htmlfile.write('  element: "link' + repr(i) + '",')
    htmlfile.write('  data: [')
    for y in range(minyear, maxyear + 1):
        a = 0
        b = 0
        if y in dictionary[key0]:
            a = dictionary[key0][y]
        if y in dictionary[key1]:
            b = dictionary[key1][y]
        htmlfile.write('    { y: "' + repr(y) + '", a: ' + repr(a) + ', b: ' + repr(b) + ' },')
    htmlfile.write('  ],')
    htmlfile.write('  xkey: "y",')
    htmlfile.write('  ykeys: ["a", "b"],')
    htmlfile.write('  labels: ["' + linklist[i][0].replace("_", " ") + '", "' + linklist[i][1].replace("_", " ") + '"]')
    htmlfile.write('});')
    htmlfile.write('</script>')
    htmlfile.write('<p  style="margin-top: 100px">----------------------------------------------------------------------------------------------------------------------------------------------------------------</p>')
htmlfile.write('<h2 style="margin-top: 100px"> Finished! Please press Ctrl+S to save this page, and then send the <font color="red">html</font> file back. Great Thanks!</h2></body></html>')
htmlfile.close()
