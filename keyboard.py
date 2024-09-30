from vk_api.keyboard import VkKeyboard, VkKeyboardColor

keyb_for_start = VkKeyboard(one_time=False)
keyb_for_search = VkKeyboard(one_time=False)
keyb_for_main = VkKeyboard(one_time=False)

keyb_for_start.add_button('Начать', color=VkKeyboardColor.PRIMARY)
keyb_for_start.add_button('Поиск', color=VkKeyboardColor.PRIMARY)

keyb_for_search.add_button('Следующий', color=VkKeyboardColor.PRIMARY)
keyb_for_search.add_button('Добавить в ЧС', color=VkKeyboardColor.NEGATIVE)
keyb_for_search.add_line()
keyb_for_search.add_button('Добавить в избранное', color=VkKeyboardColor.POSITIVE)
keyb_for_search.add_button('Убрать лайк', color=VkKeyboardColor.SECONDARY)
keyb_for_search.add_button('Выйти', color=VkKeyboardColor.SECONDARY)