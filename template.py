from vk_api.keyboard import VkKeyboardColor
from vk_api.utils import sjson_dumps
from abc import ABCMeta
from typing import Optional, Union, List


MIN_ELEMENTS_IN_CAROUSEL = 1
MAX_ELEMENTS_IN_CAROUSEL = 10
MAX_BUTTONS_IN_CAROUSEL = 3


class Button:
    __metaclass__ = ABCMeta


class ButtonText(Button):
    def __init__(self, label: str, color: VkKeyboardColor = VkKeyboardColor.SECONDARY, payload: str = None):
        self.label = label
        self.color = color
        self.payload = payload

        self.button = {
            'action': {
                'type': "text",
                'label': label,
                'payload': payload
            },
            'color': color.value,
        }


class ButtonOpenLink(Button):
    pass


class ButtonLocation(Button):
    pass


class ButtonVKPay(Button):
    pass


class ButtonVKApps(Button):
    pass


class ButtonCallback(Button):
    pass


class VkTemplate(object):
    """ Класс для созда ния шаблона сообщений для бота (https://vk.com/dev/bots_docs_3)"""


class Carousel(VkTemplate):
    """ Класс для создания шаблона сообщений для бота - Карусель (https://vk.com/dev/bots_docs_3)
    """
    __slots__ = ('title', 'lines', 'keyboard', 'inline')

    class Element(object):

        __slots__ = ('photo_id', 'title', 'description', 'link', 'buttons', 'element', 'type_action')

        button_type = Union[ButtonText, ButtonOpenLink, ButtonLocation, ButtonCallback,
                                     ButtonVKApps, ButtonVKPay]

        def __init__(self, photo_id: Optional[str] = None, title: Optional[str] = None,
                     description: Optional[str] = None, link: Optional[str] = None,
                     buttons: List[Optional[button_type]] = None):
            self.buttons = [button.button for button in buttons] if buttons else []
            self.element = {'buttons': self.buttons}
            if not title and not photo_id:
                raise ValueError(f'There is no required parameter (\'photo_id\' or \'title\')')
            elif title and not description:
                raise ValueError(f'The \'descriptions\' parameter is missing')
            if title:
                self.title = title
                self.element['title'] = self.title
            if description:
                self.description = description
                self.element['description'] = self.description
            if photo_id:
                self.photo_id = photo_id
                self.element['photo_id'] = self.photo_id
            if link:
                self.type_action = 'open_link'
                self.link = link
                self.element['action'] = {'type': self.type_action, 'link': self.link}
            else:
                self.type_action = 'open_photo'
                self.element['action'] = {'type': self.type_action}

        def get_element(self):
            """ Получить json клавиатуры """
            return sjson_dumps(self.element)

        def add_buttons(self, *args: button_type):
            """ Добавить кнопки в элемент."""
            self.buttons += [arg.button for arg in args]
            number_of_buttons = len(self.buttons)
            if number_of_buttons > MAX_BUTTONS_IN_CAROUSEL:
                raise ValueError(f'Max {MAX_BUTTONS_IN_CAROUSEL} buttons in the carousel')

    def __init__(self):
        self.type = "carousel"
        self.elements = []
        self.buttons_in_the_elements = None

        self.carousel = {
            'type': self.type,
            'elements': self.elements
        }

    def get_carousel(self):
        """ Получить json клавиатуры """
        print(self.carousel)
        return sjson_dumps(self.carousel)

    def add_elements(self, *args: Element):
        """ Добавить элементы."""
        print(args)
        self.elements += [arg.element for arg in args]
        print(self.elements)
        number_of_elements = len(self.elements)
        print(number_of_elements)
        if not MIN_ELEMENTS_IN_CAROUSEL <= number_of_elements <= MAX_ELEMENTS_IN_CAROUSEL:
            raise ValueError(f'The added number of elements ({number_of_elements}) is not included in the allowed '
                             f'range ({MIN_ELEMENTS_IN_CAROUSEL}...{MAX_ELEMENTS_IN_CAROUSEL})')
        for element in self.elements:
            print(element['buttons'])
            number_of_buttons = len(element['buttons'])
            if self.buttons_in_the_elements is None:
                self.buttons_in_the_elements = number_of_buttons
            elif self.buttons_in_the_elements != number_of_buttons:
                raise ValueError(f'The condition of the same number of buttons in the elements is violated')


