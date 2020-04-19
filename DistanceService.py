import math
import FirebaseConnect
import googlemaps
import os
from dotenv import load_dotenv
from collections import OrderedDict

load_dotenv()

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

def RecommendSpot(currentPosition, transportation):
    spotList = FirebaseConnect.getDataFirebase('/spotInform/')

    if transportation == 'driving':
        travelRange = 150
    elif transportation == 'walking':
        travelRange = 30
    elif transportation == 'bicycling':
        travelRange = 60

    recommendList = []
    for oneSpot, spotInfo in spotList.items():
        if 'thumbnailUrl' in spotInfo:
                thumbnailUrl = spotInfo['thumbnailUrl']
        else:
            thumbnailUrl = 'https://www.taiwan.net.tw/images/noPic.jpg'

        distLocation = {
            "lat": float(spotInfo['lat']),
            "long": float(spotInfo['long']),
        } 
        distance = getDistance(currentPosition, distLocation)
        if distance <= travelRange:
            recommendList += [{
                'title': oneSpot,
                'distance': distance,
                'address': spotInfo['address'],
                'viewer': int(spotInfo['viewer']),
                'thumbnailUrl': thumbnailUrl
            }]

    recommendList.sort(key=lambda k: (k.get('viewer', 0)), reverse=True)

    return recommendList

def PopularSpot():
    spotList = FirebaseConnect.getDataFirebase('/spotInform/', 'viewer', 'DESC', 10)
    
    recommendList = []
    for oneSpot, spotInfo in spotList.items():
        if 'thumbnailUrl' in spotInfo:
                thumbnailUrl = spotInfo['thumbnailUrl']
        else:
            thumbnailUrl = 'https://www.taiwan.net.tw/images/noPic.jpg'

        distLocation = {
            "lat": float(spotInfo['lat']),
            "long": float(spotInfo['long']),
        } 
        
        recommendList += [{
            'title': oneSpot,
            'address': spotInfo['address'],
            'viewer': int(spotInfo['viewer']),
            'thumbnailUrl': thumbnailUrl
        }]

    recommendList.sort(key=lambda k: (k.get('viewer', 0)), reverse=True)
    return recommendList

# calculate two places distance and duration
def calPlaceInfo(currentPos, destPos, mode):
    googleMapKey = os.getenv('GOOGLE_MAP_API_KEY')
    gmaps = googlemaps.Client(key=googleMapKey)
    origins = (currentPos['lat'], currentPos['long'])
    destinations = (destPos['lat'], destPos['long'])
    result = gmaps.distance_matrix(origins, destinations, mode)

    return result
