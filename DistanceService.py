import math
import FirebaseConnect
FirebaseConnect.initFirebase()
def getDistance(distA, distB):
    ra = 6378140
    rb = 6356755

    flatten = (ra - rb) / ra
    
    # change angle to radians
    radLatA = math.radians(distA['lat'])
    radLonA = math.radians(distA['long'])
    radLatB = math.radians(distB['lat'])
    radLonB = math.radians(distB['long'])

    pA = math.atan(rb / ra * math.tan(radLatA))  
    pB = math.atan(rb / ra * math.tan(radLatB))  
    x = math.acos(math.sin(pA) * math.sin(pB) + math.cos(pA) * math.cos(pB) * math.cos(radLonA - radLonB))  
    c1 = (math.sin(x) - x) * (math.sin(pA) + math.sin(pB))**2 / math.cos(x / 2)**2  
    c2 = (math.sin(x) + x) * (math.sin(pA) - math.sin(pB))**2 / math.sin(x / 2)**2  
    dr = flatten / 8 * (c1 - c2)  
    distance = 0.001 * ra * (x + dr)  
    return distance  

def recommendSpot(currentPosition):
    spotList = FirebaseConnect.getDataFirebase()

    recommendList = []
    for oneSpot, spotInfo in spotList.items():
        if 'imgUrl' in spotInfo:
                thumbnailUrl = spotInfo['imgUrl']
        else:
            thumbnailUrl = 'https://www.taiwan.net.tw/images/noPic.jpg'

        distLocation = {
            "lat": float(spotInfo['lat']),
            "long": float(spotInfo['long']),
        } 
        distance = getDistance(currentPosition, distLocation)
        if distance <= 20:
            recommendList += [{
                'title': oneSpot,
                'distance': distance,
                'address': spotInfo['address'],
                'viewer': int(spotInfo['viewer']),
                'thumbnailUrl': thumbnailUrl
            }]

    recommendList.sort(key=lambda k: (k.get('viewer', 0)), reverse=True)

    return recommendList