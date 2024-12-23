import requests
from flask import Flask, render_template, request

app = Flask(__name__)

api_url = 'https://dataservice.accuweather.com/'
api_key = 'bCd4AScdlmAAkBxbVo9NJqhhGC3wFdF5'
city_url = 'locations/v1/cities/search'

now_url = '/currentconditions/v1/'
one_day_url = '/forecasts/v1/daily/1day/'
five_day_url = '/forecasts/v1/daily/5day/'

def find_loc_key(url, data):
    loc_key = requests.get(api_url + url,
                           params={
                               'q': data,
                               'apikey': api_key
                           }).json()
    return loc_key

def check_bad_weather(temp, wind):
    if 0 <= temp <= 35 and wind <= 50:
        return False
    return True

def weather(loc_key, w_url):
    try:
        r_w = requests.get(api_url + w_url + loc_key, params={'details': 'true',
                                                              'language': 'ru',
                                                              'apikey': api_key,
                                                              'metric': 'true'}).json()
        print(r_w)

        temp = r_w[0]['Temperature']['Metric']['Value']
        humidity = r_w[0]['RelativeHumidity']
        wind = r_w[0]['Wind']['Speed']['Metric']['Value']

        if check_bad_weather(int(temp), int(wind)):
            result = 'Погода плохая!'
        else:
            result = 'Погода хорошая)'

        return {'status': True,
                'temp': temp,
                'humidity': humidity,
                'wind': wind,
                'result': result}
    except:
        return {'status': False,
                'error': r_w.status_code}


def check_city(city, time):
    loc_key = find_loc_key(city_url, city)[0]['Key']
    if time == 'weather_now':
        return weather(loc_key, now_url)
    elif time == 'weather_1day':
        return weather(loc_key, one_day_url)
    elif time == 'weather_5day':
        return weather(loc_key, five_day_url)











'''def request(url, params):
    """Запрос к серверу для получения данных"""

    url = BASE_URL + url
    params['apikey'] = API_KEY
    params['language'] = 'ru'

    try:
        response = requests.get(url, params=params)
    except:
        return {
            'status': 'error',
            'message': 'Ошибка получения погоды'
        }

    # Обработка ошибок

    if response.ok:
        return {
            'status': 'ok',
            'data': response.json()
        }

    if response.status_code == 503 and response.json()[
        'Message'] == 'The allowed number of requests has been exceeded.':
        return {
            'status': 'error',
            'message': 'Превышено количество запросов к API'
        }

    return {
        'status': 'error',
        'message': 'Ошибка получения погоды',
        'status_code': response.status_code,
        'data': response.json()
    }

def get_current_weather(location_key):
    """Получение погоды по `location_key`"""

    url = f'/currentconditions/v1/{location_key}'
    params = {
        'details': 'true'
    }
    return request(url, params)

def get_forecast_1_day(location_key):
    """Получение прогноза погоды на один день по `location_key`"""

    url = f'/forecasts/v1/daily/1day/{location_key}'
    params = {
        'details': 'true',
        'metric': 'true'
    }
    return request(url, params)

def get_forecast_5_day( location_key):
    """Получение прогноза погоды на 5 дней по `location_key`"""

    url = f'/forecasts/v1/daily/5day/{location_key}'
    params = {
        'details': 'true',
        'metric': 'true'
    }
    return request(url, params)'''