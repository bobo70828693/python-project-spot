from bs4 import BeautifulSoup
import FirebaseConnect
import requests
import json
import re

FirebaseConnect.initFirebase()

url = "/m1.aspx?sNo=0000064&keyString=%5e%5e%5e&page=16"
domain = "https://www.taiwan.net.tw"

endFlag = 0
while endFlag == 0:
    spotList = []
    requestText = requests.get(domain + url)
    soup = BeautifulSoup(requestText.text, 'html.parser')
    if len(soup.select('a.next-page')) == 0:
        nextPageStr = 0
        endFlag = 1
    else:    
        nextPage = min(soup.select('a.next-page'))
        pos = nextPage['href'].find("&page=")
        nextPageStr = nextPage['href'][pos+6:]
        url = nextPage['href']

    print("now page is : " + min(soup.select('a.current')).text)
    data = soup.select('div.card-wrap')
    for oneSpot in data:
        spotLink = min(oneSpot.select('a.card-link'))
        viewer = min(oneSpot.select('p.target.target-like')).text
        pos = viewer.find("瀏覽人次：")
        viewNum = int(viewer[pos+5:])

        # get spot info
        htmlInfo = requests.get(domain + "/" + spotLink['href'])
        soupInfo = BeautifulSoup(htmlInfo.text, 'html.parser')
        print(spotLink['title'])
        # get instagram viewer count
        tags = spotLink['title'].split("/")
        for tag in tags:
            instagramUrl = "https://www.instagram.com/explore/tags/{0}/?__a=1&max_id=".format(re.sub("[^\u4E00-\u9FFF]", "", tag))
            instagramRequest = requests.get(instagramUrl)
            if instagramRequest.status_code == 200:
                instagramData = json.loads(instagramRequest.text)
                viewNum += int(instagramData['graphql']['hashtag']['edge_hashtag_to_media']['count'])

        infoElement = min(soupInfo.select("dl.info-table"))
        if not soupInfo.select('a#cntPicA0 > img'):
            imgUrl = "https://www.taiwan.net.tw/images/noPic.jpg"
        else:
            imgUrl = min(soupInfo.select('a#cntPicA0 > img'))['data-src']
        address = min(infoElement.select('a.address'))
        gps = min(infoElement.find_all("dt", string="經度/緯度："))
        gpsInfo = min(gps.find_next_sibling("dd")).split('/')
        spotList += [
            {
                "title": spotLink['title'].replace('/', '\\'),
                "href": domain + spotLink['href'],
                "thumbnailUrl": imgUrl,
                "viewer": viewNum,
                "address": address.text,
                "long": gpsInfo[0],
                "lat": gpsInfo[1],

            }
        ]
    
    # update to Firebase
    FirebaseConnect.insertDataFirebase(spotList)