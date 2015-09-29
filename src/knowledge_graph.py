# Building knowledge graph from AMiner scientific network

import os
from stemming.porter2 import stem

from parse_publication_tag import PublicationTagParser
from parse_publication_time_author import Extraction
from time_keyword_distribution import TopicTime
from merge_keywords import MergeKeywords
from algorithm1 import Algorithm1


def main():
    result_dir = '../results/'
    data_dir = '../data/'

    # change here to change different topic
    q = 'data mining'

    query = q.replace(' ', '_')
    publication_data = data_dir + 'pub_' + query + '.data'
    publication_simplified = result_dir + 'pub_' + query + '.simp'
    publication_keyword = result_dir + 'pub_' + query + '.keywords'
    publication_distribution = result_dir + 'pub_' + query + '.dist'

    # output file name
    list_author_year_keyword = result_dir + 'author_year_' + query + '.list'
    list_author = result_dir + 'link_author_' + query + '.list'
    list_link = result_dir + 'link_' + query + '.list'
    link_diff = result_dir + 'diff_' + query + '.list'

    # extract keywords
    ptp = PublicationTagParser()
    ptp.parse_publication_tag(publication_data, publication_keyword, q)

    # extract author, time
    e = Extraction()
    e.extract(publication_data)
    e.output(publication_simplified)

    # merge keywords
    mk = MergeKeywords()
    mk.readin(publication_keyword)
    mk.process_keywords(publication_keyword + '_merge', q)
    mk.process_publication(publication_simplified, publication_simplified + '_merge')
    # rename the new file after merge keywords 
    os.rename(publication_keyword + '_merge', publication_keyword)
    os.rename(publication_simplified + '_merge', publication_simplified)

    # get the topic time distribution
    tt = TopicTime()
    tt.read(publication_keyword, publication_simplified)
    tt.show(publication_keyword, publication_distribution)

    # use algorithm1 to get link
    alg1 = Algorithm1()
    alg1.algorithm1(publication_keyword, publication_simplified,
                    list_author_year_keyword, list_author,
                    list_link, link_diff)

if __name__ == '__main__':
    main()