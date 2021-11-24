import requests
from bs4 import BeautifulSoup


HEADERS = {'user-agent':
           'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36',
           'accept': '*/*'}


def get_html(url, params=None):
    r = requests.get(url, headers=HEADERS, params=params)
    return r


def get_content(html):
    html = html.text
    soup = BeautifulSoup(html, 'html.parser')
    return soup


def parse(url):
    html = get_html(url)
    if html.status_code == 200:
        content = get_content(html)
        return content
    else:
        return 'ERROR'


def parse_day(day_content):
    count = 0
    day_lessons = []
    for lesson in day_content:
        if count == 0:
            day_name = lesson.text[:-5]
        else:
            day_lessons.append(lesson)
        count += 1

    return day_name, day_lessons


def create_answer_view(weeks_content, slicer_1, slicer_2):
    week_content = weeks_content[slicer_1:slicer_2]
    week = {}

    for day in week_content:
        day_name, day_lessons = parse_day(day)
        week[day_name] = day_lessons

    answer = ''
    count = 1
    for day in week:
        answer += '\n' + '-' * 10 + '\n' + f'{day}' + '\n' + '-' * 10 + '\n'
        for lesson in week[day]:
            lesson_room = lesson.find('div', class_='lesson-room')
            lesson_name = lesson.find('div', class_='lesson-name')
            lesson_type = lesson.find('div', class_='lesson-type')
            lesson_hour = lesson.find('div', class_='lesson-hour')
            if lesson_room and lesson_type and lesson_name and lesson_hour:
                try:
                    answer += f'{count}. {lesson_hour.text[:-1]}|{lesson_name.text}{lesson_type.text}|{lesson_room.text.split("/")[0]} Корпус|{lesson_room.text.split("/")[1][:1]} Этаж|{lesson_room.text.split("/")[1]} Кабинет' + '\n'
                except:
                    answer += f'{count}. {lesson_hour.text[:-1]}|{lesson_name.text}{lesson_type.text}|{lesson_room.text} Кабинет' + '\n'
            else:
                answer += f'{count}. ~~~' + '\n'
            count += 1
        count = 1
    return answer


def parse_weeks(url, colour_of_week):
    content = parse(url)
    weeks_content = content.find_all('div', class_='day')
    if colour_of_week == 'this':
        slicer_1 = 1
        slicer_2 = 7
        return create_answer_view(weeks_content, slicer_1, slicer_2)

    if colour_of_week == 'next':
        slicer_1 = 8
        slicer_2 = 14
        return create_answer_view(weeks_content, slicer_1, slicer_2)


def parse_current_day(url):
    content = parse(url)
    day_content = content.find_all('div', class_='day day-current')[0]
    day_name, day_lessons = parse_day(day_content)
    answer = '\n' + '-' * 10 + '\n' + f'{day_name}' + '\n' + '-' * 10 + '\n'
    count = 1
    no_lessons_count = 0
    for lesson in day_lessons:
        lesson_room = lesson.find('div', class_='lesson-room')
        lesson_name = lesson.find('div', class_='lesson-name')
        lesson_type = lesson.find('div', class_='lesson-type')
        lesson_hour = lesson.find('div', class_='lesson-hour')
        if lesson_room and lesson_type and lesson_name and lesson_hour:
            try:
                answer += f'{count}. {lesson_hour.text[:-1]}|{lesson_name.text}{lesson_type.text}|{lesson_room.text.split("/")[0]} Корпус|{lesson_room.text.split("/")[1][:1]} Этаж|{lesson_room.text.split("/")[1]} Кабинет' + '\n'
            except:
                answer += f'{count}. {lesson_hour.text[:-1]}|{lesson_name.text}{lesson_type.text}|{lesson_room.text} Кабинет' + '\n'
        else:
            answer += f'{count}. ~~~' + '\n'
            no_lessons_count += 1
        count += 1
    if no_lessons_count == len(day_lessons):
        answer = 'Сегодня у тебя нет уроков'
    return answer


