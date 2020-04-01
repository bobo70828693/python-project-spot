import requests
import urllib
import json
import time
from bs4 import BeautifulSoup

end_cursor = ''
tag = urllib.parse.quote("值得二刷")

posts = []
endFlag = 0
while endFlag == 0:
# for i in range(0, page):
    url = "https://www.instagram.com/explore/tags/{0}/?__a=1&max_id={1}".format(tag, end_cursor)
    requestData = requests.get(url)

    if requestData.status_code == 200:
        data = json.loads(requestData.text)

        end_cursor = data['graphql']['hashtag']['edge_hashtag_to_media']['page_info']['end_cursor']
        # list of posts
        edges = data['graphql']['hashtag']['edge_hashtag_to_media']['edges']

        for post in edges:
            posts.append(post['node'])
        time.sleep(2)
    else:
        endFlag = 1

with open('posts.json', 'w') as outfile:
    json.dump(posts, outfile)
    # soup = BeautifulSoup(requestData.text, 'html.parser')

