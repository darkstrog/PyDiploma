from keyboard import sender
from main import *

for event in bot.longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        request = event.text.lower()
        user_id = str(event.user_id)
        vk_user = bot.get_vk_user(user_id)
        msg = event.text.lower()
        sender(user_id, msg.lower())
        try:
            bot.seen_users = [int(row[0]) for row in select_seen_users()]
        except:
            print("[INFO] не удалось получить данные из базы или преобразовать")
        if request.lower() == 'привет':
            bot.write_msg(user_id, f'Привет, {vk_user.get("first_name")} для начала работы используй кнопки!')
        elif request.lower() == 'начать новый поиск':
            create_database()
            bot.write_msg(user_id, f'Привет, {vk_user.get("first_name")}')
            bot.age_span = int(bot.get_age_span(vk_user))
            bot.find_persons(vk_user, bot.age_span)
            bot.write_msg(event.user_id, f'Нашёл подходящую пару, нажми кнопку "Вперёд" что бы посмотреть')
            bot.get_found_person(vk_user, bot.age_span)

        elif request == 'вперёд':
            bot.get_found_person(vk_user, bot.age_span)

        else:
            bot.write_msg(event.user_id, 'Не понял команду')
