from flask import Flask, request, jsonify, render_template
import requests

app = Flask(__name__)

API_KEY = 'cJ5Oaed2PCAGmwf7PsrDNG1nYKGCCFay'

def get_location_key(city_name):
    if not city_name:
        raise Exception("Город не задан")
    url = f'http://dataservice.accuweather.com/locations/v1/cities/search?apikey={API_KEY}&q={city_name}'
    response = requests.get(url)
    if response.status_code == 200:
        res = response.json()
        return res[0]['Key']
    else:
        return None

def get_weather(location_key):
    if not location_key:
        raise Exception("location_key не задан")
    # Получение данных о погоде
    url = f'https://dataservice.accuweather.com/forecasts/v1/daily/5day/{location_key}?apikey={API_KEY}&metric=true&details=true' 
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def check_bad_weather(temperature_max, temperature_min, wind_speed, rain_probability):
    if (temperature_min < 0 or temperature_max > 35) or (wind_speed > 50) or (rain_probability > 70):
        return "Плохие погодные условия"
    return "Хорошие погодные условия"

@app.route('/')
def index():
    # Главная страница
    return render_template("form.html")

@app.route('/forecast', methods=['POST'])
def forecast():
    if request.method != 'POST':
        return "Ошибка: ожидается POST запрос", 400
    
    start_city = request.form.get('start')
    end_city = request.form.get('end')

    try:
        key_start_city = get_location_key(start_city)
        weather_start = weather(key_start_city)
    except IndexError:
        return 'Ошибка обработки начальной точки маршрута, проверьте введённые данные'
    except Exception as e:
        return 'Ошибка обработки запроса, свяжитесь с администратором'

    try:
        key_end_city = get_location_key(end_city)
        weather_end = weather(key_end_city)
    except IndexError:
        return 'Ошибка обработки конечной точки маршрута, проверьте введённые данные'
    except Exception as e:
        return 'Ошибка обработки запроса, свяжитесь с администратором'

    return render_template("forecast.html",
        start_city = start_city,
        end_city = end_city,
        start_forecast = weather_start['weather_condition'],
        end_forecast = weather_end['weather_condition'])


@app.route('/location_key/<city_name>')
def location_key(city_name):
    return get_location_key(city_name)


@app.route('/weather/<location_key>', methods=['GET'])
def weather(location_key):
    # Получение прогноза погоды по ключу местоположения
    data = get_weather(location_key)
    if data:
        # Извлечение ключевых параметров прогноза погоды
        forecast = data['DailyForecasts'][0]
        day = data['DailyForecasts'][0]['Day']

        temperature_max = forecast['Temperature']['Maximum']['Value']
        temperature_min = forecast['Temperature']['Minimum']['Value']
        wind_speed = day['Wind']['Speed']['Value'] # скорость ветра
        rain_probability = day['RainProbability'] # вероятность дождя
        humidity = day['RelativeHumidity']['Average'] # средняя влажность

        weather_condition = check_bad_weather(temperature_max, temperature_min, wind_speed, rain_probability)

        result = {
            'date': forecast['Date'],
            'temperature_max': temperature_max,
            'temperature_min': temperature_min,
            'wind_speed': wind_speed,
            'rain_probability': rain_probability, 
            'humidity': humidity,
            'weather_condition': weather_condition
        }

        return jsonify(result)
    else:
        return jsonify({'error': 'Не удалось получить данные о погоде'}), 500
    
@app.route('/weather_map/<start_location>/<end_location>', methods=['GET'])
def weather_route():
    start_location = request.args.get('start')
    end_location = request.args.get('end')
    
    # Здесь вы можете добавить логику для получения данных о погоде
    # Например, вызов функции get_weather() с использованием ключей местоположения
    
    # Пример возврата данных (замените на вашу логику)
    return jsonify({
        'start': start_location,
        'end': end_location,
        'temperature_max': 10,  # Замените на реальные данные
        'wind_speed': 15,       # Замените на реальные данные
        'precipitation_probability': 30,  # Замените на реальные данные
        'weather_condition': 'Хорошие погодные условия'  # Замените на реальные данные
    })

if __name__ == '__main__':
    app.run(debug=True)



api_key = 'cJ5Oaed2PCAGmwf7PsrDNG1nYKGCCFay'