from threading import Thread
from typing import Dict
from vk_api.longpoll import VkLongPoll, VkEventType
from session import vk_group
from command import search, search_parameters, change_search_parameters, abort, user_verification, \
    change_parameters, command_to_check_changes_in_search_parameters

InfoPeoplesDB = Dict[str, Dict[int, dict]]


class ChatBotLogic:
    def __init__(self):
        self.command_button = {'🔍 искать': {'command': search, 'params': {}},
                               '⚙ параметры поиска': {'command': search_parameters, 'params': {}},
                               '🛠 изменить': {'command': change_search_parameters, 'params': {}},
                               '🚫 прервать': {'command': abort, 'params': {}}
                               }

    def read_message_new(self, event_):
        text = event_.text.lower()
        user_id = event_.user_id
        user_bool = user_verification(user_id)
        if user_bool and text in self.command_button:
            self.command_button[text]['command'](user_id, **self.command_button[text]['params'])
        elif hasattr(event_, 'payload'):
            change_parameters(user_id, text, parameter=event_.payload)
        else:
            previous_message_payload = vk_group.read_the_previous_message(user_id)['items'][0].get('payload')
            command_to_check_changes_in_search_parameters(user_id, text, previous_message_payload)


def main():
    vk_group_session = vk_group.vk_session
    longpoll = VkLongPoll(vk_group_session)
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            chat_bot = ChatBotLogic()
            th = Thread(target=chat_bot.read_message_new, args=(event,))
            th.start()


if __name__ == '__main__':
    main()
