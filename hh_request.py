import requests
import pprint
import json
import time
import sys
import sqlite3


class HHRequests:

    # создаем конструктор класса
    def __init__(self, vacancy_text, vacancy_town):
        self._vacancy_text = vacancy_text
        self._vacancy_town = vacancy_town

    # создаем функцию для доступа к переменной self._vacancy_text
    @property
    def vacancy_text(self):
        return self._vacancy_text

    # создаем функцию для доступа к переменной self._vacancy_town
    @property
    def vacancy_town(self):
        return self._vacancy_town

    # создаем функцию для соединения
    @property
    def hh_connector(self):

        # создаем переменную для сайта с api
        hh_url = 'https://api.hh.ru/'

        # создаем переменную для полного пути к вакансиям
        hh_url_vacancies = f'{hh_url}vacancies'

        # создаем переменную для полного пути к справочнику городов
        hh_url_areas = f'{hh_url}suggests/areas'

        # формируем запрос к справочнику городов по условию 'название города'
        hh_area_id_response = requests.get(hh_url_areas,
                                           params={'text': self.vacancy_town}
                                           ).json()

        # из справочника городов по условию 'название города' получаем id этого города
        # 0 - это Россия, пока не реализовал поиск для других стран
        area_id = hh_area_id_response['items'][0]['id']

        # создаем строку параметров для запроса вакансий по условиям 'текст вакансии', 'id города'
        hh_connection_params = {
                                'text': self.vacancy_text,
                                'area': area_id,
                                'page': 1
                                }
        # формируем запрос для запроса информации о вакансиях по условиям 'текст вакансии', 'id города'
        hh_response = requests.get(hh_url_vacancies,
                                   params=hh_connection_params
                                   ).json()
        return hh_response

    # функция для запроса информации о вакансиях и сохранения информации в файл json-формата
    @property
    def hh_get_vacancy_inf(self):

        # соединяемся с api.hh.ru/vacancies
        hh_response = self.hh_connector

        # создаем пустой словарь для сохранения информации о скачанных вакансиях
        vacancies_dict = {}

        # создаем цикл для постраничного скачивания вакансий с api.hh.ru/vacancies и
        # постранично (20 вакансий на странице) скачиваем вакансии
        for page_number in range(0, 2):

            # из-за ограничения api.hh.ru/vacancies, вводим искуственную задержку
            # отсчитываем в терминале 3-х секундные интервалы
            for vacancy in hh_response['items']:

                time.sleep(2)

                # скачиваем информацию о вакансии и сохраняем ее в словарь
                current_response = requests.get(vacancy['url']).json()
                vacancies_dict[vacancy['id']] = {'url': vacancy['alternate_url'],
                                                 'skills': current_response['key_skills'],
                                                 'salary': current_response['salary']
                                                 }
            # выводим в терминал сообщение о скачивании одной страницы с вакансиями (20 шт.)
            sys.stdout.write(f'\nВакансии со страницы {page_number+1} загружены!\n')

            # каждую страницу с вакансиями сохраняем в файл формата json
            with open('vacancies_dict', 'w') as f:
                json.dump(vacancies_dict, f)
        return vacancies_dict

    # функция для соединения с базой sqllite
    @property
    def sql_connection(self):

        # показываем, какой файл бд необходимо использовать для соединения
        db_connection = sqlite3.connect('hm17.db')

        # создаем курсор для запросов к бд
        db_cursor = db_connection.cursor()

        return db_cursor

    # функция для проверки базы данных
    # проверяем есть ли в таблице areas_book значение региона из запроса пользователя
    @property
    def check_areas_book(self):

        # создаем кортеж для передачи имени региона как параметр
        # в запрос к бд
        tuple_for_request = (self.vacancy_town,)

        # создаем курсор к бд на основе соединения,
        # созданного в функции sql_connection
        area_cursor = self.sql_connection

        # отправляем в бд запрос с проверкой, есть ли в таблице areas_book
        # регион в котором пользователь ищет вакансии
        area_cursor.execute('select count(*) from areas_book where area_name =?', tuple_for_request)

        # считываем все строки ответа от бд
        area_check_response = area_cursor.fetchall()

        # возравщаем True or False в зависимости от ответа бд
        if area_check_response[0][0] == 0:
            print('в таблице регионов нет такого региона(города)')
            area_cursor.execute('insert into areas_book(area_name) values (?)', tuple_for_request)
            sqlite3.connect('hm17.db').commit()
            print(f'регион {self.vacancy_town} добавлен в бд')
        else:
            print('в таблице регионов есть такой регион(город)')

    #



    # функция для проверки базы данных
    # проверяем есть ли в таблице skills_book значение навыка
    # из запрошенных пользователем вакансий
    def check_skills_book(self, skill_name):

        # создаем кортеж для передачи имени навыка как параметр
        # в запрос к бд
        tuple_for_request = (skill_name,)

        # создаем курсор к бд на основе соединения,
        # созданного в функции sql_connection
        skill_select_cursor = self.sql_connection

        # отправляем в бд запрос с проверкой, есть ли в таблице skills_book
        # навык который содержится в запрошенных пользователем вакансиях
        skill_select_cursor.execute('select count(*) from areas_book where area_name =?', tuple_for_request)

        # считываем все строки ответа от бд
        skill_check_response = skill_select_cursor.fetchall()

        # возравщаем True or False в зависимости от ответа бд
        if skill_check_response[0][0] == 0:
            print('в таблице навыков нет такого навыка')
            return False
        else:
            print('в таблице навыков есть такой навык')
            return True

    # функция для создания словаря под вывод данных на страницах html
    @property
    def make_dict_for_html(self):

        # создаем словарь с исходными данным используя метод hh_get_vacancy_inf
        # данный словарь содержит информацию с сайта hh.ru по запросу от пользователя
        dict_from_hh = self.hh_get_vacancy_inf

        # создаем пустой словарь для дальнейшего
        # заполнения динамических html страниц
        dict_for_html = {}

        # т.к. в Python словари не имеют индексов
        # создаем список длиной равной длине словаря с информацией из hh.ru
        vacancies_list_for_index = list(dict_from_hh.values())

        # создаем цикл для разбора информации по каждой вакансии
        for each_value in dict_from_hh.values():

            # создаем ключ для вакансии
            vacancy_index = vacancies_list_for_index.index(each_value) + 1

            # в словарь добавляем ключ для вакансии
            dict_for_html[vacancy_index] = {}

            # по добавленному ключу добавляем вложенный словарь
            # ключ - url, значение - http ссылка на вакансию
            dict_for_html[vacancy_index]['url'] = each_value['url']

            # создаем пустую строку для формирования перечня ключевых навыков
            # требуемых для каждой вакансии
            skills_string = ''

            # если ключевые навыки в вакансии указаны
            # передаем их через запятую в skills_string
            if len(each_value['skills']) != 0:
                for each_skill in each_value['skills']:
                    skills_string += '{}, '.format(each_skill['name'])
            # если ключевые навыки не указаны
            # передаем в skills_string сообщение об отсутствии
            else:
                skills_string = 'не указаны  '

            # "отрезаем ',' и пробел в строке после последнего указанного в вакансии навыка
            skills_string = skills_string[:-2]

            # добавляем во вложенный словарь
            # ключ - skills, значение - строка skills_string с перечнем навыков
            dict_for_html[vacancy_index]['skills'] = f'Ключевы навыки: {skills_string}'

            # если зарплата в вакансии указана
            # передаем в salary_string сообщение с указанием зарплаты
            if each_value['salary'] is not None:
                if each_value['salary']['from'] is not None and each_value['salary']['currency'] == 'RUR':
                    salary_string = 'Зарплата - {}'.format(each_value['salary']['from'])
                    # salary_string += f'{salary_string}\n'
            # если зарплата в вакансии не указана
            # передаем в salary_string соответствующее сообщение
                else:
                    salary_string = 'Зарплата в рублях не указана'
            else:
                salary_string = 'Зарплата в рублях не указана'

            # добавляем во вложенный словарь
            # ключ - salary, значение - строка salary_string
            dict_for_html[vacancy_index]['salary'] = salary_string

        with open('vacancies_for_html', 'w') as f:
            json.dump(dict_for_html, f)

        return dict_for_html


if __name__ == '__main__':
    test_connector = HHRequests('python', 'Санкт-Петербург')
    pprint.pprint(test_connector.hh_get_vacancy_inf)