# fetch people/publication data from Aminer through Aminer API
import requests
import json
# import time


def search(type, query):
    base_url = "https://api.aminer.org/api/search/" + type + "?"
    static_para = 'query=' + query + '&sort=relevance&'
    offset = 0
    size = 100
    limit = 150000
    outfile = open(type + '_' + query.replace(' ', '_') + ".data", 'w')
    round = 0
    while(True):
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
        print ('%d %d' % (offset, total))
        if (offset > total):
            break
        if (offset > limit):
            break
        # time.sleep()
        round += 1
    outfile.close()

def main():
    search('pub', 'software engineering')

if __name__ == '__main__':
    main()
