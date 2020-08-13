from datetime import datetime as dt

import requests

from settings import URL_WEATHER_API, CITY, LANGUAGE, UNITS, TEXT_ERROR_CITY_NOT_EXISTS


class WeatherForecaster:
    def __init__(self):
        self.__forming_url_weather_api(CITY, LANGUAGE, UNITS)
        self.__test_forecaster()

        self.response = {}

    def __forming_url_weather_api(self, city: str, lang: str, units: str):
        self.URL_WEATHER_API = URL_WEATHER_API.format(city, lang, units)

    def __test_forecaster(self):
        status_code = requests.get(self.URL_WEATHER_API).status_code
        # fixme logging
        if status_code == 200:
            print('ok')
        else:
            pass

    def get_forecast(self, city: str, lang: str = 'ru', units: str = 'metric') -> (str, str):
        self.__forming_url_weather_api(city=city, lang=lang, units=units)
        self.response = requests.get(self.URL_WEATHER_API).json()
        if self.__checking_response_code:
            return self.__convert_dict_to_str_response(response=self.response), \
                   self.response['name']
        else:
            return self.__convert_dict_to_str_response(response={'err': TEXT_ERROR_CITY_NOT_EXISTS}), \
                   ''

    @property
    def __checking_response_code(self) -> bool:
        # fixme logging
        return True if self.response.get('cod') == 200 else False

    @staticmethod
    def __convert_dict_to_str_response(response: dict) -> str:
        err = response.get('err')
        if err:
            return err
        else:
            return WeatherForecaster.__get_response_string(response)

    @staticmethod
    def __get_response_string(response: dict) -> str:
        city = response['name']
        weather = response['weather'][0]['description'].capitalize()
        params_weather = response['main']
        temperature = round(params_weather['temp'], 1)
        degree_sign = '\N{DEGREE SIGN}'
        pressure = int(params_weather['pressure'] / 1.33)
        dt_response = dt.fromtimestamp(response['dt']).strftime('%d-%m-%Y %H:%M:%S')
        response_string = f"Город: {city}\n" \
                          f"{weather}\n" \
                          f"Температура: {temperature}{degree_sign}C\n" \
                          f"Давление: {pressure} мм рт.ст.\n" \
                          f"Скорость ветра: {response['wind']['speed']} м/с\n" \
                          f"Дата: {dt_response}"
        return response_string

    # fixme for the future
    def get_picture_weather(self):
        picture_name = self.response['weather'][0]['icon']
        pic_response = requests.get(f'http://openweathermap.org/img/wn/{picture_name}.png')
        return pic_response.content
