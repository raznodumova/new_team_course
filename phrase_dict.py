import bot_func

phrase_dict = dict()

phrase_dict["начать"] = bot_func.BotFunc.user_inf

phrase_dict["вернуться в свой профиль"] = bot_func.BotFunc.user_inf

phrase_dict['следующий'] = bot_func.BotFunc.next_

phrase_dict["к поиску"] = bot_func.BotFunc.next_

phrase_dict["Изменить анкету"] = bot_func.BotFunc.change_user_inf

phrase_dict["изменить критерии поиска"] = bot_func.BotFunc.change_user_prompt

phrase_dict["выход"] = bot_func.BotFunc.first_visit

phrase_dict["да"] = bot_func.BotFunc.next_

phrase_dict["лайк"] = bot_func.BotFunc.like

phrase_dict["бан"] = bot_func.BotFunc.ban

phrase_dict["избранные"] = bot_func.BotFunc.liked_people

phrase_dict["посмотреть всех"] = bot_func.BotFunc.see_all_liked_people

phrase_dict["посмотреть лучшего"] = bot_func.BotFunc.best

phrase_dict["вернуться в профиль"] = bot_func.BotFunc.user_inf

phrase_dict["мой профиль"] = bot_func.BotFunc.user_inf
