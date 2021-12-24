from vk_api.keyboard import VkKeyboard, VkKeyboardColor


# Создаём клавиатуру "Поиск, Параметры поиска"
keyboard_main = VkKeyboard(one_time=False, inline=False)
keyboard_main.add_button(label='🔍 Искать', color=VkKeyboardColor.POSITIVE)
keyboard_main.add_button(label='⚙ Параметры поиска', color=VkKeyboardColor.PRIMARY)

# Создаём клавиатуру выводимую после просмотра "Параметры поиска"
keyboard_parameters = VkKeyboard(one_time=False, inline=False)
keyboard_parameters.add_button(label='🛠 Изменить', color=VkKeyboardColor.POSITIVE)
keyboard_parameters.add_button(label='🚫 Прервать', color=VkKeyboardColor.NEGATIVE)

# Создаём клавиатуру выводимую после просмотра "Изменить параметры поиска"
keyboard_search_parameters = VkKeyboard(one_time=False, inline=False)
keyboard_search_parameters.add_button(label='🏡 город', color=VkKeyboardColor.POSITIVE,
                                      payload={'command': '🏡 город'})
keyboard_search_parameters.add_button(label='🌏 страна', color=VkKeyboardColor.POSITIVE,
                                      payload={'command': '🌏 страна'})
keyboard_search_parameters.add_line()
keyboard_search_parameters.add_button(label='👫 пол', color=VkKeyboardColor.POSITIVE,
                                      payload={'command': '👫 пол'})
keyboard_search_parameters.add_button(label='👶 возраст от', color=VkKeyboardColor.POSITIVE,
                                      payload={'command': '👶 возраст от'})
keyboard_search_parameters.add_button(label='🧓 возраст до', color=VkKeyboardColor.POSITIVE,
                                      payload={'command': '🧓 возраст до'})
keyboard_search_parameters.add_line()
keyboard_search_parameters.add_button(label='👥 статус', color=VkKeyboardColor.POSITIVE,
                                      payload={'command': '👥 статус'})
keyboard_search_parameters.add_button(label='🎨 увлечения', color=VkKeyboardColor.POSITIVE,
                                      payload={'command': '🎨 увлечения'})
keyboard_search_parameters.add_button(label='🎤 музыка', color=VkKeyboardColor.POSITIVE,
                                      payload={'command': '🎤 музыка'})
keyboard_search_parameters.add_line()
keyboard_search_parameters.add_button(label='🎥 фильмы', color=VkKeyboardColor.POSITIVE,
                                      payload={'command': '🎥 фильмы'})
keyboard_search_parameters.add_button(label='📺 ТВ', color=VkKeyboardColor.POSITIVE,
                                      payload={'command': '📺 ТВ'})
keyboard_search_parameters.add_button(label='📖 книги', color=VkKeyboardColor.POSITIVE,
                                      payload={'command': '📖 книги'})
keyboard_search_parameters.add_line()
keyboard_search_parameters.add_button(label='🚫 Прервать', color=VkKeyboardColor.NEGATIVE,
                                      payload={'command': '🚫 Прервать'})


def interface_main():
    return keyboard_main.get_keyboard()


def interface_parameters():
    return keyboard_parameters.get_keyboard()


def interface_search_parameters():
    return keyboard_search_parameters.get_keyboard()


def interface_change_parameters(command):
    keyboard_change_parameters = VkKeyboard(one_time=False, inline=False)
    if command == '👫 пол':
        payload_men = {'command': command, 'params': '2'}
        payload_women = {'command': command, 'params': '1'}
        payload_not_set = {'command': command, 'params': '0'}
        keyboard_change_parameters.add_button(label='👨 мужчин', color=VkKeyboardColor.POSITIVE,
                                              payload=payload_men)
        keyboard_change_parameters.add_button(label='👩 женщин', color=VkKeyboardColor.POSITIVE,
                                              payload=payload_women)
        keyboard_change_parameters.add_button(label='👤 незадано', color=VkKeyboardColor.POSITIVE,
                                              payload=payload_not_set)
        keyboard_change_parameters.add_line()
    payload = {'command': command, 'params': 'сбросить'}
    keyboard_change_parameters.add_button(label='❎ сбросить_значение_параметра', color=VkKeyboardColor.PRIMARY,
                                          payload=payload)
    keyboard_change_parameters.add_button(label='🚫 Прервать', color=VkKeyboardColor.NEGATIVE)
    return keyboard_change_parameters.get_keyboard()


def interface_search_result_photo(link):
    keyboard_search_result_photo = VkKeyboard(one_time=False, inline=True)
    keyboard_search_result_photo.add_openlink_button(label='Открыть', link=link)
    return keyboard_search_result_photo.get_keyboard()


def interface_button_open_blacklist(people_id: int):
    keyboard_button_open_blacklist = VkKeyboard(one_time=False, inline=True)
    link = f'https://vk.com/id{people_id}'
    keyboard_button_open_blacklist.add_openlink_button(label='Открыть страницу профиля', link=link)
    payload = {'command': '🚷 чёрный список', 'params': people_id}
    keyboard_button_open_blacklist.add_button(label='🚷 Чёрный список', color=VkKeyboardColor.NEGATIVE, payload=payload)
    return keyboard_button_open_blacklist.get_keyboard()
