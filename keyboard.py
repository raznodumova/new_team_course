from vk_api.keyboard import VkKeyboard, VkKeyboardColor

keyb = VkKeyboard(one_time=False)

keyb.add_button('Начать', color=VkKeyboardColor.PRIMARY)
keyb.add_button('Следующий', color=VkKeyboardColor.PRIMARY)
keyb.add_button('Добавить в ЧС', color=VkKeyboardColor.NEGATIVE)
keyb.add_line()
keyb.add_button('Добавить в избранное', color=VkKeyboardColor.POSITIVE)
keyb.add_button('Убрать лайк', color=VkKeyboardColor.SECONDARY)
keyb.add_button('Выйти', color=VkKeyboardColor.SECONDARY)