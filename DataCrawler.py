from bs4 import BeautifulSoup
import FirebaseConnect
import requests
import json
import re

url = "/m1.aspx?sNo=0000064&keyString=%5e%5e%5e"
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
        spotHref = domain + "/" + spotLink['href']
        htmlInfo = requests.get(spotHref)
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

        # get image url & gps info
        infoElement = min(soupInfo.select("dl.info-table"))
        infoSide = soupInfo.find(class_='infoside')
        if len(infoSide.find_next_siblings('p')) == 0:
            description = "尚無資訊"
        else:
            description = infoSide.find_next_siblings('p')[0].get_text()

        album = min(soupInfo.select('ul.album'))
        imageData = album.select('a.album-link > img')
        imageList = [oneImg['data-src'] for oneImg in imageData]
        if not imageList:
            thumbnailUrl = "https://www.taiwan.net.tw/images/noPic.jpg"
        else:
            thumbnailUrl = min(imageList)

        address = min(infoElement.select('a.address'))
        gps = min(infoElement.find_all("dt", string="經度/緯度："))
        gpsInfo = min(gps.find_next_sibling("dd")).split('/')
        
        # insert data to firebase
        spotData = {
            "link": spotHref,
            "description": description[0:100].replace('\r\n',''),
            "thumbnailUrl": thumbnailUrl,
            "imgList": imageList,
            "viewer": viewNum,
            "address": address.text,
            "long": gpsInfo[0],
            "lat": gpsInfo[1],
        }
        firebasePath = '/spotInform/' + spotLink['title'].replace('/', '\\')
        FirebaseConnect.insertDataFirebase(firebasePath, spotData)