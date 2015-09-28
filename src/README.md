1. use fetch_data.py to get data from AMiner
2. maybe use merge.py to merge data
3. use parse_people_pub_tag.py, parse_people_tag.py, parse_publication_tag.py to get keywords
4. remove data_mining from keywords
4. use parse_publication_time_author.py to get the simplified version of publication
5. use merge_keywords.py to get the keywords after merge
6. use info.py to get the basic information about publication 
7. use topic_time.py to get the time distribution of each topic
8. remove data_mining from keywords again(because it might occur again by merge_keywords.py)
8. use algorithm1 to get the correlation


python parse_publication_tag.py
python parse_publication_time_author.py
python merge_keywords.py
python time_keyword_distribution.py
python algorithm1.py
