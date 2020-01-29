import sqlite3
from pprint import pprint
import json
from hh_request import HHRequests
#
# test_conn = sqlite3.connect('hm17.db')
#
# test_cursor = test_conn.cursor()
#
# test_cursor.execute('select * from areas_book')
#
# select_for_print = test_cursor.fetchall()
#
# print(select_for_print)

# with open('vacancies_dict', 'r') as dict_all_info:
#     dict_for_print = json.load(dict_all_info)

# pprint(dict_for_print)

# area_name = 'Ростов-на-Дону'
#
# tuple_for_db = (area_name,)
#
# request_text = 'python'


# def check_area(area_name):
#
#     tuple_for_db = (area_name,)
#
#     test_conn = sqlite3.connect('hm17.db')
#
#     test_cursor = test_conn.cursor()
#
#     test_cursor.execute('select count(*) from areas_book where area_name =?', tuple_for_db)
#
#     select_for_print = test_cursor.fetchall()
#
#     return select_for_print[0][0]
#
#
# if check_area(area_name) == 0:
#     test_cursor.execute('insert into areas_book(area_name) values (?)', tuple_for_db)
#     test_conn.commit()
#     print(f'добавлен город {area_name}')
# else:
#     print('город уже существует')

test_hh = HHRequests('python', 'Питер')

test_check_area = test_hh.check_areas_book

test_check_region = test_hh.check_skills_book('python')

print(test_check_area)
print(test_check_region)
