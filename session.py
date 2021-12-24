from VK import VkUser, VkGroup
from DataBase import VKinderBase
from auth.auth import token_group, token_user, auth_db


v_kinder_base = VKinderBase(user=auth_db['user'], password=auth_db['password'], database=auth_db['database'])

vk_group = VkGroup(token_group)

vk_user = VkUser(token_user)
