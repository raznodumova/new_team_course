from vk_api.keyboard import VkKeyboard, VkKeyboardColor

keyb_for_start = VkKeyboard(one_time=True, inline=False)
keyb_for_search = VkKeyboard(one_time=True, inline=False)
keyb_user_profile = VkKeyboard(one_time=True, inline=False)
keyb_gender_choise = VkKeyboard(one_time=True, inline=False)
keyb_go = VkKeyboard(one_time=True, inline=False)
keyb_lets_search = VkKeyboard(one_time=False)
keyb_for_city = VkKeyboard(one_time=True, inline=False)
keyb_for_likes = VkKeyboard(one_time=True, inline=False)
empty_keybord = VkKeyboard.get_empty_keyboard()

keyb_for_likes.add_button("Посмотреть всех", color=VkKeyboardColor.POSITIVE)
keyb_for_likes.add_button("Посмотреть лучшего", color=VkKeyboardColor.PRIMARY)
keyb_for_likes.add_line()
keyb_for_likes.add_button("Мой профиль", color=VkKeyboardColor.SECONDARY)

keyb_for_city.add_button("Москва", color=VkKeyboardColor.POSITIVE)
keyb_for_city.add_button("Сызрань", color=VkKeyboardColor.POSITIVE)
keyb_for_city.add_line()
keyb_for_city.add_button("Саратов", color=VkKeyboardColor.POSITIVE)

keyb_lets_search.add_button("К поиску", color=VkKeyboardColor.POSITIVE)

keyb_gender_choise.add_button("С парнем", color=VkKeyboardColor.PRIMARY)
keyb_gender_choise.add_button("С девушкой", color=VkKeyboardColor.PRIMARY)

keyb_user_profile.add_button("К поиску", color=VkKeyboardColor.POSITIVE)
keyb_user_profile.add_button("Изменения", color=VkKeyboardColor.PRIMARY)
keyb_user_profile.add_button("Избранные", color=VkKeyboardColor.PRIMARY)
keyb_user_profile.add_line()
keyb_user_profile.add_button("Удалить анкету", color=VkKeyboardColor.NEGATIVE)

keyb_for_start.add_button('Мой профиль', color=VkKeyboardColor.PRIMARY)
keyb_for_start.add_button("Выход", color=VkKeyboardColor.SECONDARY)

keyb_go.add_button("ДА", color=VkKeyboardColor.POSITIVE)

keyb_for_search.add_button('Следующий', color=VkKeyboardColor.PRIMARY)
keyb_for_search.add_button('Лайк', color=VkKeyboardColor.POSITIVE)
keyb_for_search.add_line()
keyb_for_search.add_button('Бан', color=VkKeyboardColor.NEGATIVE)
# keyb_for_search.add_button('Убрать лайк', color=VkKeyboardColor.SECONDARY)
keyb_for_search.add_button('Мой профиль', color=VkKeyboardColor.SECONDARY)
