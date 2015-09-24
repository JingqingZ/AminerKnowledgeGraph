# fetch people/publication data from Aminer through Aminer API
import requests
import json
# import time


def search(type):
    base_url = "https://api.aminer.org/api/search/" + type + "?"
    static_para = "query=data mining&sort=relevance&"
    offset = 92700
    size = 100
    outfile = open(type + ".data", 'w')
    round = 0
    while(True and round < 2550):
        search_url = base_url + static_para
        search_url += "offset=" + repr(offset) + "&size=" + repr(size)
        print(search_url)
        response = requests.get(search_url)
        content = json.loads(str(response.content.decode("utf-8")))
        results = content["result"]
        total = content["total"]
        for r in results:
            outfile.write(str(r) + '\n')
        offset += size
        if (offset > total):
            break
        # time.sleep()
        round += 1
    outfile.close()

search("pub")
