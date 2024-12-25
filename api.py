import requests
from flask import Flask, render_template, request

app = Flask(__name__)

api_url = 'https://dataservice.accuweather.com/'
api_key = 'STbxeZ4RPycial5PSIkzDOljuRPW0WVP'  # 'bAcODVPKMvw2q6VQREVxk3jC9c5WWSip'
city_url = 'locations/v1/cities/search'

now_url = '/currentconditions/v1/'
one_day_url = '/forecasts/v1/daily/1day/'
free_day_url = '/forecasts/v1/daily/5day/'

def find_loc_key(url, data):
    loc_key = requests.get(api_url + url,
                           params={
                               'q': data,
                               'apikey': api_key
                           }).json()
    return loc_key

def weather(loc_key, w_url):
    try:
        r_w = requests.get(api_url + w_url + loc_key, params={'details': 'true',
                                                              'language': 'ru',
                                                              'apikey': api_key,
                                                              'metric': 'true'})
        return {'status': True,
                'data': r_w.json()}
    except:
        return {'status': False,
                'error': r_w.status_code}


def check_city(city, time):
    loc_key = find_loc_key(city_url, city)
    if loc_key == []:
        return {'status': False,
                'error': 'Нет такого города :('}
    loc_key = loc_key[0]['Key']

    if time == 'weather_now':
        w = weather(loc_key, now_url)
        if w['status']:
            d = w['data'][0]
            return {'status': True,
                    'city': city,
                    'data': [{'date': d['LocalObservationDateTime'][:10],
                              'precipitation': d['PrecipitationType'],
                              'temp': d['Temperature']['Metric']['Value'],
                              'humidity': d['RelativeHumidity'],
                              'wind': d['Wind']['Speed']['Metric']['Value']
                              }]
                    }
        return w

    elif time == 'weather_1day':
        w = weather(loc_key, one_day_url)
        if w['status']:
            d = w['data']['DailyForecasts']
            return {'status': True,
                    'city': city,
                    'data': [{'date': d['Date'][:10],
                              'precipitation': (d['Day']['PrecipitationType'] if d['Day']['HasPrecipitation']
                                                else 'Осадков нет'),
                              'temp': (d['Temperature']['Minimum']['Value'] + d['Temperature']['Maximum']['Value']) / 2,
                              'humidity': (d['Day']['RelativeHumidity']['Minimum'] +
                                           d['Day']['RelativeHumidity']['Maximum']) / 2,
                              'wind': d['Day']['Wind']['Speed']['Value']
                              }]
                    }
        return w

    elif time == 'weather_3days':
        w = weather(loc_key, free_day_url)
        if w['status']:
            d = w['data']['DailyForecasts']
            data = list()
            for i in d:
                data.append({'date': i['Date'][:10],
                             'precipitation': (i['Day']['PrecipitationType'] if i['Day']['HasPrecipitation']
                                               else 'Осадков нет'),
                             'temp': (i['Temperature']['Minimum']['Value'] +
                                      i['Temperature']['Maximum']['Value']) / 2,
                             'humidity': (i['Day']['RelativeHumidity']['Minimum'] +
                                          i['Day']['RelativeHumidity']['Maximum']) / 2,
                             'wind': i['Day']['Wind']['Speed']['Value']
                             })
            return {'status': True,
                    'city': city,
                    'data': data}
        return w