import configparser
import os
import FirebaseConnect
import requests
import globals
from dotenv import load_dotenv

load_dotenv()

weatherToken = os.getenv('WEATHER_API_TOKEN')
config = configparser.ConfigParser()
config.read(['region.ini', 'weather.ini'])

def getWeatherInfo(spotAddress):
    url = 'https://opendata.cwb.gov.tw/api/v1/rest/datastore/{dataId}?Authorization={authorization}'

    city = spotAddress[0:3]
    cityDataId = config['city.forecast.twoday'][city]
    regionList = config['city'][city].split(',')
    region = [oneRegion for oneRegion in regionList if spotAddress.find(oneRegion) != -1]
    locationName = None
    if len(region) != 0:
        locationName = min(region)

    postUrl = url.format(dataId=cityDataId, authorization=weatherToken)
    postUrl += '&elementName=Wx,WeatherDescription,AT'
    if locationName is not None:
        postUrl += '&locationName={locationName}'.format(locationName=locationName)

    requestRes = requests.get(postUrl)
    requestData = requestRes.json()
    data = None
    # get weather api response
    if requestData.get('success', 'false') == 'true':
        records = requestData['records']['locations'][0]['location'][0]
        for recordData in records['weatherElement']:
            if recordData['elementName'] == 'Wx':
                # 天氣現象
                weatherDataText = recordData['time'][0]['elementValue'][0]['value']
                weatherDataClassify = recordData['time'][0]['elementValue'][1]['value']
            elif recordData['elementName'] == 'WeatherDescription':
                # 天氣預報綜合描述
                weatherDataDescription = recordData['time'][0]['elementValue'][0]['value']
            elif recordData['elementName'] == 'AT':
                temperature = recordData['time'][0]['elementValue'][0]['value'] + "℃"
        
        data = {
            "city": city,
            "locationName": locationName,
            "weather": {
                "description": weatherDataDescription,
                "temperature": temperature,
                "short_text": weatherDataText,
                "classify": int(weatherDataClassify)
            }
        }
    
    return data
