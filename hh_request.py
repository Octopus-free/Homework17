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

        # # создаем курсор для запросов к бд
        # db_cursor = db_connection.cursor()

        return db_connection

    # функция для проверки базы данных
    # проверяем есть ли в таблице areas_book значение региона из запроса пользователя

    def check_areas_book(self, id_from_hh):

        # создаем кортеж для передачи имени региона как параметр
        # в запрос к бд
        tuple_for_request = (id_from_hh,)

        # создаем курсор к бд на основе соединения,
        # созданного в функции sql_connection
        area_connection = self.sql_connection
        area_cursor = area_connection.cursor()

        # отправляем в бд запрос с проверкой, есть ли в таблице areas_book
        # регион в котором пользователь ищет вакансии
        area_cursor.execute('select count(*) from areas_book where id_from_hh =?', tuple_for_request)

        # считываем все строки ответа от бд
        area_check_response = area_cursor.fetchall()

        # возравщаем True or False в зависимости от ответа бд
        if area_check_response[0][0] == 0:
            return 0
        else:
            return 1

    #

    # функция для проверки базы данных
    # проверяем есть ли в таблице skills_book значение навыка
    # из запрошенных пользователем вакансий
    def check_skills_book(self, id_from_hh):

        # создаем кортеж для передачи имени навыка как параметр
        # в запрос к бд
        tuple_for_request = (id_from_hh,)

        # создаем курсор к бд на основе соединения,
        # созданного в функции sql_connection
        skill_connection = self.sql_connection
        skill_cursor = skill_connection.cursor()

        # отправляем в бд запрос с проверкой, есть ли в таблице skills_book
        # навык который содержится в запрошенных пользователем вакансиях
        skill_cursor.execute('select count(*) from skills_book where id_from_hh =?', tuple_for_request)

        # считываем все строки ответа от бд
        skill_check_response = skill_cursor.fetchall()

        # возравщаем True or False в зависимости от ответа бд
        if skill_check_response[0][0] == 0:
            return 0
        else:
            return 1

    # функция для проверки базы данных
    # проверяем есть ли в таблице vacancies данные о вакансии
    # из запрошенных пользователем вакансий
    def check_vacancies(self, id_from_hh):

        # создаем кортеж для передачи имени навыка как параметр
        # в запрос к бд
        tuple_for_request = (id_from_hh,)

        # создаем курсор к бд на основе соединения,
        # созданного в функции sql_connection
        vacancies_connection = self.sql_connection
        vacancies_cursor = vacancies_connection.cursor()

        # отправляем в бд запрос с проверкой, есть ли в таблице skills_book
        # навык который содержится в запрошенных пользователем вакансиях
        vacancies_cursor.execute('select count(*) from vacancies where id_from_hh =?', tuple_for_request)

        # считываем все строки ответа от бд
        vacancies_check_response = vacancies_cursor.fetchall()

        # возравщаем True or False в зависимости от ответа бд
        if vacancies_check_response[0][0] == 0:
            return 0
        else:
            return 1

    # функция для сохранения информации в бд
    @property
    def save_inf_into_db(self):

        # создаем курсор к бд на основе соединения,
        # созданного в функции sql_connection
        db_connection = self.sql_connection
        db_cursor = db_connection.cursor()

        db_cursor.execute('delete from vacancies')
        db_cursor.execute('delete from areas_book')
        db_cursor.execute('delete from skills_book')

        db_connection.commit()

        # создаем словарь с исходными данным используя метод hh_get_vacancy_inf
        # данный словарь содержит информацию с сайта hh.ru по запросу от пользователя
        dict_from_hh = self.hh_get_vacancy_inf

        # создаем цикл для разбора информации по каждой вакансии
        for each_key, each_value in dict_from_hh.items():

            id_for_save_into_db = each_key
            url_for_save_into_db = each_value['url']

            if each_value['salary'] is not None:
                if each_value['salary']['from'] is not None and each_value['salary']['currency'] == 'RUR':
                    salary_for_save_into_db = 'Зарплата - {}'.format(each_value['salary']['from'])

            # если зарплата в вакансии не указана
            # передаем в salary_string соответствующее сообщение
                else:
                    salary_for_save_into_db = 'Зарплата в рублях не указана'
            else:
                salary_for_save_into_db = 'Зарплата в рублях не указана'

            tuple_for_save_into_vacancies = (url_for_save_into_db, id_for_save_into_db, salary_for_save_into_db,)
            if self.check_vacancies(id_for_save_into_db) == 0:
                db_cursor.execute('insert into vacancies(vacancy_url, id_from_hh, salary) values(?, ?, ?)',
                                  tuple_for_save_into_vacancies)

            db_connection.commit()

            tuple_for_save_into_areas_book = (self.vacancy_town, id_for_save_into_db)

            if self.check_areas_book(id_for_save_into_db) == 0:
                db_cursor.execute('insert into areas_book(area_name, id_from_hh) values (?, ?)',
                                  tuple_for_save_into_areas_book)

            # если ключевые навыки в вакансии указаны
            # передаем их через запятую в skills_string
            if len(each_value['skills']) != 0:
                for each_skill in each_value['skills']:
                    skills_for_save_into_db = each_skill['name']
                    tuple_for_save_into_skills_book = (skills_for_save_into_db, id_for_save_into_db,)
                    if self.check_skills_book(id_for_save_into_db) == 0:
                        db_cursor.execute('insert into skills_book(skill_name, id_from_hh) values (?, ?)',
                                          tuple_for_save_into_skills_book)
                    # print(f'навык {skills_for_save_into_db}, добавлен в таблицу skill_book '
                    #       f'для вакансии {id_for_save_into_db}')

            db_connection.commit()

    # функция для создания словаря под вывод данных на страницах html
    @property
    def make_dict_for_html(self):

        # создаем пустой словарь для дальнейшего
        # заполнения динамических html страниц
        dict_for_html = {}


        db_connection = self.sql_connection

        db_cursor = db_connection.cursor()

        db_cursor.execute('select count(*) from vacancies')

        # count_vacancies_in_db = db_cursor.fetchall()[0][0]

        # т.к. в Python словари не имеют индексов
        # создаем список длиной равной длине словаря с информацией из hh.ru
        # vacancies_list_for_index = list(count_vacancies_in_db)

        db_cursor.execute('select id_from_hh from vacancies')
        list_from_db = db_cursor.fetchall()

        list_vacancies_id = []
        for element in list_from_db:
            list_vacancies_id.append(element[0])

        # создаем цикл для разбора информации по каждой вакансии
        for element in list_vacancies_id:

            # создаем ключ для вакансии
            vacancy_index = list_vacancies_id.index(element) + 1

            # в словарь добавляем ключ для вакансии
            dict_for_html[vacancy_index] = {}

            # создаем кортеж для передачи его как параметр
            # в запрос к бд, в кортеж передаем id вакансии с hh.ru
            tuple_for_db = (element,)

            # создаем запрос к бд для получения url,
            # соответствующего id вакансии с hh.ru
            db_cursor.execute('select vacancy_url from vacancies '
                              'where id_from_hh = ?', tuple_for_db)

            # получаем url из бд
            url_from_db = db_cursor.fetchall()

            # по добавленному ключу добавляем вложенный словарь
            # ключ - url, значение - http ссылка на вакансию
            dict_for_html[vacancy_index]['url'] = url_from_db[0][0]

            # создаем пустую строку для формирования перечня ключевых навыков
            # требуемых для каждой вакансии
            skill_string = ''

            # создаем запрос к бд для получения перечня навыков,
            # соответствующего id вакансии с hh.ru
            db_cursor.execute('select b.skill_name from vacancies a, skills_book b '
                              'where a.id_from_hh = b.id_from_hh '
                              'and a.id_from_hh = ?', tuple_for_db)

            # получаем лист с навыками из бд
            # по каждой вакансии
            skills_from_db = db_cursor.fetchall()

            for skill_name in skills_from_db:
                skill_string += '{}, '.format(skill_name[0])

            skill_string = skill_string[:-2]

            # добавляем во вложенный словарь
            # ключ - skills, значение - строка skills_string с перечнем навыков
            dict_for_html[vacancy_index]['skills'] = f'Ключевые навыки: {skill_string}'

            # создаем запрос к бд для получения salary,
            # соответствующего id вакансии с hh.ru
            db_cursor.execute('select salary from vacancies '
                              'where id_from_hh = ?', tuple_for_db)

            # получаем salary из бд
            salary_from_db = db_cursor.fetchall()

            # добавляем во вложенный словарь
            # ключ - salary, значение - строка salary_string
            dict_for_html[vacancy_index]['salary'] = salary_from_db[0][0]

        with open('vacancies_for_html', 'w') as f:
            json.dump(dict_for_html, f)

        return dict_for_html


if __name__ == '__main__':
    test_connector = HHRequests('python', 'Санкт-Петербург')
    pprint.pprint(test_connector.hh_get_vacancy_inf)