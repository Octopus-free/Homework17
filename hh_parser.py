import pprint
from hh_request import HHRequests
from parser_json_dict import ParserJsonDict

# запрашиваем в терминале информацию для параметров запроса к api.hh.ru
# текст запроса и город
vacancy_text = input('Какую вакансию вы ищите? ').lower()
vacancy_town = input('В каком городе Вам хотелось бы работать? ').lower()

# создаем экземпляр класса HHRequests для формирования исходного словаря с вакансиями
create_full_vacancies_dict = HHRequests(vacancy_text, vacancy_town)

# создаем экземпляр класса ParserJsonDict для формирования словаря с топ-навыками
full_vacancies_dict = create_full_vacancies_dict.hh_get_vacancy_inf

# вызываем метод fill_dict для заполнения словаря с топ-навыками из класса ParserJsonDict
parser_dict_with_top_skills = ParserJsonDict(full_vacancies_dict, vacancy_text)

# выводим в терминал словарь с топ-навыками
pprint.pprint(parser_dict_with_top_skills.fill_dict)

