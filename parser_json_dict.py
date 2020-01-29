import json
import pprint


class ParserJsonDict:

    # создаем конструктор класса
    def __init__(self, json_file_name, request_text):
        self._json_file_name = json_file_name
        self._request_text = request_text
        self._vacancies_dict = {
                    'vacancy_text': self.request_text,
                    'vacancies_count': 0,
                    'vacancy_avg_salary': 0,
                    'vacancies_skills': {}
                    }

    # создаем функцию для доступа к переменной self._json_file_name
    @property
    def json_file_name(self):
        return self._json_file_name

    # создаем функцию для доступа к переменной self._request_text
    @property
    def request_text(self):
        return self._request_text

    # создаем функцию для доступа к переменной self._vacancies_dict
    @property
    def vacancies_dict(self):
        return self._vacancies_dict

    # создаем функцию для открытия файла json-формата
    @property
    def loaded_dict(self):
        with open(self.json_file_name, 'r') as dict_json:
            loaded_dict = json.load(dict_json)
        return loaded_dict

    """
    создаем функцию для заполнения словаря с полями:
    - текст запроса вакансии;
    - кол-во вакансий с запрошенным текстом;
    - средния зарплана вакансии с запрошенным текстом (только для вакансий с "непустой" зарплатой);
    - требования к навыкам в вакансии:
                            - имя первого из требуемых навыков:
                                    - кол-во вакансий в котором есть требование к этому навыку;
                                    - процент вакансий в котором есть требование к этому навыку;
                            ...
                            - имя n-го из требуемых навыков:
                                    - кол-во вакансий в котором есть требование к этому навыку;
                                    - процент вакансий в котором есть требование к этому навыку.
    """
    @property
    def fill_dict(self):

        # создаем пустой словарь на основе переменной self.vacancies_dict
        dict_for_parser = self.vacancies_dict

        # записываем в словарь общее кол-во вакансий с текстом запроса
        dict_for_parser['vacancies_count'] = len(self.loaded_dict)

        # создаем цикл для заполнения поля словаря с требуемыми навыками
        for element in self.loaded_dict.values():

            # в загруженном файле перебираем в цикле все навыки
            for skill_list in element['skills']:

                # если навыка еще нет в словаре dict_for_parser и он есть в требованиях вакансии, добавляем его
                # и устанавливаем счетчик кол-ва данного навыка = 1
                # процент требования данного навыка по отношению ко всем вакансиями пока оставляем равным 0
                if skill_list['name'] not in dict_for_parser['vacancies_skills']:
                    dict_for_parser['vacancies_skills'][skill_list['name']] = {
                                                                        'skill_count': 1,
                                                                        'skill_percent': 0
                                                                     }
                # если навык в словаре dict_for_parser уже есть, увеличиваем счетчик кол-ва данного навыка на 1
                # процент требования данного навыка по отношению ко всем вакансиями пока оставляем равным 0
                if skill_list['name'] in dict_for_parser['vacancies_skills']:
                    current_skill_count_value = dict_for_parser['vacancies_skills'][skill_list['name']]['skill_count']
                    dict_for_parser['vacancies_skills'][skill_list['name']]['skill_count'] = current_skill_count_value + 1

        # для каждого навыка, записанного в словарь dict_for_parser
        # считаем процент его востребованности по отношению к общему кол-ву вакансий
        for element in dict_for_parser['vacancies_skills'].values():
            element['skill_percent'] = round(element['skill_count'] * 100 / dict_for_parser['vacancies_count'], 1)

        # создаем переменную для расчета средней зарплаты
        avg_salary = 0

        # создаем переменную счетчик для подсчета вакансий с "непустой" запрлатой
        vacancies_count_with_salary = 0

        # в цикле перебираем все вакансии
        for element in self.loaded_dict.values():

            # если поле element['salary'] не пустое
            if element['salary'] is not None:

                # а также зарплата в рублях и поле element['salary']['from'] не пустое
                if element['salary']['from'] is not None and element['salary']['currency'] == 'RUR':

                    # считаем сумму зарплаты по всем вакансиям
                    avg_salary += element['salary']['from']

                    # считаем кол-во вакансий, удовлетворяющих условиям
                    vacancies_count_with_salary += 1

        # вычисляем среднюю зарплату, делим сумму зарплат по вакансиям
        # с "непустой" зарплатой на кол-во таких вакансий
        avg_salary = round(avg_salary / vacancies_count_with_salary)

        # заполняем поле средней зарплаты в словаре dict_for_parser
        dict_for_parser['vacancy_avg_salary'] = avg_salary

        # сохраняем заполненный словарь dict_for_parser в файл
        with open('vacancies_with_top_skills', 'w') as final_dict:
            final_dict = json.dump(dict_for_parser, final_dict)

        # возвращаем заполненный словарь
        return dict_for_parser


if __name__ == '__main__':
    test = ParserJsonDict('vacancies_dict', 'python')
    pprint.pprint(test.fill_dict)