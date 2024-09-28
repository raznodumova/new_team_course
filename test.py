
import vk_api
import configparser


config = configparser.ConfigParser()
config.read('config.ini')
#
# hz = vk_api.VkApi(token=config['VK']['user_token'])
# hz2 = hz.get_api()
# search_results = hz2.users.search(
#         sex=1,
#         age_from=25,
#         age_to=27,
#         hometown="москва",
#         count=10)
# for person in search_results["items"]:
#     print(person.values)
