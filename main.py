import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard
from threading import *
import requests
import random
from db.plush_init import plush_init
from db.plush_skip_lessons_count import skip_lessons, show_skipped_lessons, show_all_skipped_lessons
from db.plush_timetable import pin_timetable, get_url_id
from timetable_parser import *
from db.plush_config import configure
from db.plush_qr import pin_qr, get_qr, unpin_qr, get_all_qr
from db.plush_homework import pin_homework, get_homework, get_subjects, unpin_homework
import datetime


vk = vk_api.VkApi(token="b632fd1e9490f1b9223c9a6963fd2292d5930c6ab2c01203bc43d78a3c1aef78b9ae8fba064e0a37b2e82")
vk._auth_token()
vk.get_api()
group_id = 208963311
longpoll = VkBotLongPoll(vk, group_id)


def reform_attachments(attachments):
    attachment_arr = ''
    if attachments.__len__() > 0:
        for attachment in attachments:
            if attachment['type'] == 'photo':
                attachment_arr += (str(attachment[u'type'] + str(attachment[attachment[u'type']][u'owner_id']) + '_'
                                       + str(attachment[attachment[u'type']][u'id']) + '_' + attachment[attachment[u'type']][u'access_key'])) + ','
            else:
                doc_url = attachment[attachment['type']]['url'].split('?')[0]
                attachment_arr += doc_url + ','

    if attachment_arr:
        return attachment_arr[:-1]
    else:
        return None


def create_keyboard(text, inline=True, msg=True):
    if inline:
        keyboard = VkKeyboard(inline=True)
    else:
        keyboard = VkKeyboard(inline=False, one_time=False)
    count = 0
    length = len(text)
    for button in text:
        count += 1
        if count != length:
            keyboard.add_button(button)
            keyboard.add_line()
        else:
            keyboard.add_button(button)

    return keyboard.get_keyboard()


def send_message(peer_id, text, keyboard=None, attachment=None):
    vk.method("messages.send", {"peer_id": peer_id, "message": text,
                                "random_id": random.randint(-9223372036854775807, 9223372036854775807),
                                "keyboard": keyboard,
                                "attachment": attachment})


def get_users(peer_id):
    return vk.method("messages.getConversationMembers", {"peer_id": peer_id})['items']


def is_admin(msg_info):
    list_admin = []
    user_list = get_users(msg_info['peer_id'])
    for user in user_list:
        try:
            if user['is_admin']:
                list_admin.append(user['member_id'])
        except:
            pass
    if msg_info['from_id'] in list_admin:
        return True
    return False


def index(msg_info):
    msg_text = msg_info['text']
    msg_peer_id = msg_info['peer_id']

    if 'плюш' in msg_info['text'].lower():

        if 'инит' in msg_text.lower():

            if is_admin(msg_info):
                users = get_users(msg_peer_id)
                for user in users:
                    if user['member_id'] > 0:
                        user_info = vk.method('users.get', {'user_ids': user['member_id']})[0]
                        user['first_name'] = user_info['first_name']
                        user['last_name'] = user_info['last_name']
                plush_init(users, msg_peer_id)
                answer = 'Беседа успешно инициализирована'
                send_message(msg_peer_id, answer, keyboard=create_keyboard(
                text=['Плюш, покажи меню'], inline=False))
            else:
                answer = 'У тебя недостаточно прав для этого действия'
                send_message(msg_peer_id, answer)

        elif 'покажи меню расписания' in msg_text.lower():
            text_for_buttons = ['Плюш, покажи эту неделю',
                                'Плюш, покажи следующую неделю',
                                'Плюш, покажи расписание на сегодня']
            answer = 'Расписания'
            send_message(msg_peer_id, answer, keyboard=create_keyboard(text_for_buttons))

        elif 'покажи меню' in msg_text.lower():
            text_for_buttons = ['Плюш, покажи мой профиль', 'Плюш, покажи меню расписания', 'Плюш, покажи все предметы']
            if is_admin(msg_info):
                text_for_buttons.append('Плюш, покажи админку')
            answer = 'Меню'
            send_message(msg_peer_id, answer, keyboard=create_keyboard(text_for_buttons))

        elif 'покажи мой профиль' in msg_text.lower():
            text_for_buttons = ['Плюш, покажи мой qr', 'Плюш, сколько я пропустил пар']
            answer = 'Твой профиль'
            send_message(msg_peer_id, answer, keyboard=create_keyboard(text_for_buttons))

        elif 'покажи админку' in msg_text.lower():
            if is_admin(msg_info):
                text_for_buttons = ['Плюш, покажи все пропуски', 'Плюш, покажи все qr']
                answer = 'Админка'
                send_message(msg_peer_id, answer, keyboard=create_keyboard(text_for_buttons))

        elif 'закрепи расписание' in msg_text.lower():

            if is_admin(msg_info):
                try:
                    timetable_url = msg_text.split('-')[1].strip()
                except:
                    timetable_url = ''

                if timetable_url.startswith('https://rasp.sstu.ru/rasp/group/'):
                    r = requests.get(timetable_url)
                    if r.status_code == 200:
                        timetable_url_id = timetable_url.split('https://rasp.sstu.ru/rasp/group/')[1]
                        pin_timetable(timetable_url_id, msg_peer_id)
                        answer = 'Расписание успешно закреплено'
                        send_message(msg_peer_id, answer)
                    else:
                        answer = 'Укажи корректную ссылку на расписание своей группы'
                        send_message(msg_peer_id, answer)
                else:
                    answer = 'Укажи корректную ссылку на расписание своей группы'
                    send_message(msg_peer_id, answer)
            else:
                answer = 'У тебя недостаточно прав для этого действия'
                send_message(msg_peer_id, answer)

        elif 'сколько я пропустил пар' in msg_text.lower():
            lessons_count = show_skipped_lessons(msg_info)
            of_skipped = lessons_count[0] * 2
            n_of_skipped = lessons_count[1] * 2
            answer = f'По уважительной причине - {of_skipped} ч.' + '\n' + \
                     f'По неуважительной причине {n_of_skipped} ч.' + '\n' + \
                     f'(Всего {of_skipped + n_of_skipped} ч.)'
            send_message(msg_peer_id, answer)

        elif 'покажи все пропуски' in msg_text.lower():
            if is_admin(msg_info):
                all_skipped_lessons = show_all_skipped_lessons(msg_peer_id)
                answer = 'Количество пропущенных пар (Официально/Неофициально)' + '\n' + '-'*10 + '\n'
                for lesson in all_skipped_lessons:
                    of_skipped = lesson[0]*2
                    n_of_skipped = lesson[1]*2
                    answer += f'[id{lesson[2]}|{lesson[3]} {lesson[4]}] | {of_skipped} / {n_of_skipped} ч. (Всего: {of_skipped+n_of_skipped}ч.)' + '\n'
            else:
                answer = 'У тебя недостаточно прав для этого действия'
            send_message(msg_peer_id, answer)

        elif (('пропустил' in msg_text.lower() or 'пропустила' in msg_text.lower()) or
              ('прогулял' in msg_text.lower() or 'прогуляла' in msg_text.lower())) \
                and 'студент' in msg_text.lower():

            try:
                user_id = msg_text.split('id')[1].split('|')[0]
                count = int(msg_text.split(' ')[-2])
            except:
                user_id = None
                count = None

            if user_id and count:
                if is_admin(msg_info):
                    if 'прогулял' in msg_text.lower() or 'прогуляла' in msg_text.lower():
                        of = False
                    else:
                        of = True
                    skip_lessons(msg_peer_id, user_id, count, of)
                    answer = 'Записано'
                    send_message(msg_peer_id, answer)
                else:
                    answer = 'У тебя недостаточно прав для этого действия'
                    send_message(msg_peer_id, answer)
            else:
                answer = 'Укажи валидные данные'
                send_message(msg_peer_id, answer)

        elif 'покажи' and 'неделю' in msg_text.lower():

            try:
                week_colour = msg_text.lower().split('покажи')[1].split('неделю')[0].strip()
                week_colours = {'эту': 'this', 'следующую': 'next'}
                week_colour = week_colours[week_colour]
                answer = parse_weeks('https://rasp.sstu.ru/rasp/group/' + str(get_url_id(msg_peer_id)), week_colour)
            except:
                answer = 'Что-то пошло не так'
            send_message(msg_peer_id, answer)

        elif 'покажи расписание на сегодня' in msg_text.lower():

            today = datetime.datetime.now()
            if today.weekday() != 6:

                try:
                    answer = parse_current_day('https://rasp.sstu.ru/rasp/group/'+str(get_url_id(msg_peer_id)))
                except:
                    answer = 'Что-то пошло не так...'

            else:
                answer = 'Ты что дурень? Сегодня воскресенье'
            send_message(msg_peer_id, answer)

        elif 'прикрепи qr' in msg_text.lower():

            try:
                if msg_info['attachments']:
                    qr_url = reform_attachments(msg_info['attachments'])
                    if len(qr_url.split(',')) == 1:
                        if qr_url.startswith('photo'):
                            pin_qr(msg_info, qr_url)
                            answer = 'Успешно'
                        else:
                            answer = 'Нужно именно изображение, а не что-либо еще'
                    else:
                        answer = 'Нельзя прикреплять больше одного изображения'
                else:
                    answer = 'Прикрепи свой qr-код к сообщению'
            except:
                answer = 'Что-то пошло не так...'

            send_message(msg_peer_id, answer)

        elif 'открепи qr' in msg_text.lower():
            user_qr = get_qr(msg_info['from_id'], msg_peer_id)
            if user_qr:
                unpin_qr(msg_info)
                answer = 'Готово'
                send_message(msg_peer_id, answer)
            else:
                answer = 'У тебя нет qr кода'
                send_message(msg_peer_id, answer)

        elif 'покажи' in msg_text.lower() and 'qr' in msg_text.lower() and 'все' in msg_text.lower():

            if is_admin(msg_info):
                answer = ''
                qr_list = ''
                all_qr = get_all_qr(msg_peer_id)
                count = 1
                for qr in all_qr:
                    answer += f'{count}. [id{qr[3]}|{qr[1]} {qr[2]}]'
                    if qr[0]:
                        answer += '\n'
                        qr_list += qr[0] + ','
                    else:
                        answer += ' - Нет кода' + '\n'
                    if count % 10 == 0 or count == len(all_qr):
                        send_message(msg_peer_id, answer, attachment=qr_list)
                        answer = ''
                        qr_list = ''
                    count += 1
            else:
                answer = 'У тебя недостаточно прав для этого действия'
                send_message(msg_peer_id, answer)

        elif 'покажи' in msg_text.lower() and 'qr' in msg_text.lower():
            try:
                user_id = msg_text.split('покажи')[1].split('qr')[0].strip()
                if user_id.lower() == 'мой':
                    user_id = msg_info['from_id']
                else:
                    user_id = user_id.split('id')[1].split('|')[0]
            except:
                user_id = None

            if user_id:
                if user_id != msg_info['from_id']:
                    if is_admin(msg_info):
                        qr = get_qr(user_id, msg_peer_id)
                        if qr:
                            answer = f'@id{user_id} qr код'
                        else:
                            answer = f'У пользователя @id{user_id} нет qr кода'
                        send_message(msg_peer_id, answer, attachment=get_qr(user_id, msg_peer_id))
                    else:
                        answer = 'У тебя недостаточно прав для этого действия'
                        send_message(msg_peer_id, answer)
                else:
                    qr = get_qr(user_id, msg_peer_id)
                    if qr:
                        answer = 'Твой qr код'
                        text_for_buttons = ['Плюш, открепи qr']
                        send_message(msg_peer_id, answer, attachment=qr, keyboard=create_keyboard(text_for_buttons))
                    else:
                        answer = 'У тебя нет qr кода'
                        send_message(msg_peer_id, answer)
            else:
                answer = 'А?..'
                send_message(msg_peer_id, answer)

        elif 'закрепи дз' in msg_text.lower() and ':' in msg_text.lower():
            try:
                attach = reform_attachments(msg_info['attachments'])
                name = msg_text.lower().split('закрепи дз')[1].split(':')[0].strip()
                text = msg_text.lower().split('закрепи дз')[1].split(':')[1].strip()
            except:
                name = None

            if name:
                if not text and not attach:
                    answer = 'Для записи нужно хоть 1 параметр'
                    send_message(msg_peer_id, answer)
                else:
                    pin_homework(msg_peer_id, name, text, attach)
                    answer = f'Записано домашнее задание по предмету {name}'
                    send_message(msg_peer_id, answer)
            else:
                answer = 'Что-то пошло не так...'
                send_message(msg_peer_id, answer)

        elif 'открепи дз' in msg_text.lower():
            try:
                name = msg_text.lower().split('открепи дз')[1].strip()
            except:
                name = None

            if name:
                unpin_homework(msg_peer_id, name)
                answer = 'Успешно'
                send_message(msg_peer_id, answer)
            else:
                answer = 'Что-то пошло не так...'
                send_message(msg_peer_id, answer)

        elif 'покажи дз' in msg_text.lower():
            try:
                name = msg_text.lower().split('покажи дз')[1].strip()
            except:
                name = None

            if name:
                homework = get_homework(msg_peer_id, name)
                if homework:
                    answer = f'Предмет: {homework[1]}' + '\n' + f'Текст: {homework[2]}'
                    send_message(msg_peer_id, answer, attachment=homework[3])
                else:
                    answer = 'По этому предмету нет домашнего задания'
                    send_message(msg_peer_id, answer)
            else:
                answer = 'Что-то пошло не так...'
                send_message(msg_peer_id, answer)

        elif 'покажи все предметы' in msg_text.lower():
            subjects = get_subjects(msg_peer_id)

            if subjects:
                answer = 'Названия предметов' + '\n' + '-'*10 + '\n'
                count = 1

                for subject in subjects:
                    answer += f'{count}. {subject[0]}' + '\n'
                    count += 1

            else:
                answer = 'В вашей беседе еще нет закрепленного домашнего задания'
            send_message(msg_peer_id, answer)

        elif 'конфиг' in msg_text.lower():

            try:
                configure()
                answer = 'Плюшка успешно сконфигурирована'
                send_message(msg_peer_id, answer)
            except:
                answer = 'Плюшка уже сконфигурирована!'
                send_message(msg_peer_id, answer)


while True:
    for event in longpoll.listen():
        try:
            if event.type == VkBotEventType.MESSAGE_NEW:
                Thread(target=index, args=(event.object['message'],
                                           ), daemon=True).start()

        except requests.exceptions.ReadTimeout:
            print('ConnectionError')
            continue