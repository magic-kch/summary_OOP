import requests
import json
from tqdm import tqdm
from datetime import datetime


class YADISKAPIClient:
	API_BASE_URL = "https://cloud-api.yandex.net/v1/disk/resources"

	def __init__(self, token, user_id):
		self.token = token
		self.user_id = user_id
		self.upload_path = f"Backup_VK_{self.user_id}_foto"

	def get_common_params(self):
		return {"Authorization": self.token}
	
	def mk_dir(self):
		params = {"path": self.upload_path}
		response = requests.put(self.API_BASE_URL, params=params, headers=self.get_common_params())

	def upload_foto(self, url_foto, file_name_upload):
		params = {"url": url_foto, "path": f"{self.upload_path}/{file_name_upload}"}
		response = requests.post(f"{self.API_BASE_URL}/upload", params=params, headers=self.get_common_params())


class VKAPIClient:
	API_BASE_URL = "https://api.vk.ru/method"
	
	def __init__(self, token, user_id, album_id):
		self.token = token
		self.user_id = user_id
		self.album_id = album_id

	def get_common_params(self):
		return {
			"access_token": self.token,
			"v": "5.199"
				}

	def get_foto(self):
		params = self.get_common_params()
		params.update({"owner_id": self.user_id, "album_id": self.album_id, "extended": "1"})
		response = requests.get(f"{self.API_BASE_URL}/photos.get", params=params)
		return response.json()

if __name__ == '__main__':
	with open("tokens.json") as file:
		json_data = json.load(file)
		token_ya = json_data['access_token_ya']
		token_vk = json_data['access_token_vk']
		
	user_id = input("Введите ID пользователя VK: ")

	source_foto = {"1": "profile", "2": "wall"}
	album_id = input("Выбирите альбом из которого необходимо сохранить фотографии\n1 - Фотографии профиля\n2 - Фотографии стены\n")

	# ~ #35064934 2112115

	vk_client = VKAPIClient(token_vk, user_id, source_foto[album_id])
	prof_photo_resp = vk_client.get_foto()

	print(f"Всего доступно для скачивания {len(prof_photo_resp['response']['items'])} фотографий")
	count_foto = input("Введите количество фотографий для скачивания(по умолчанию 5) ")
	count_foto = 5 if not count_foto else count_foto

	ya_client = YADISKAPIClient(token_ya, user_id)
	ya_client.mk_dir()

	res_dict = {}

	for i in tqdm(prof_photo_resp["response"]["items"][:int(count_foto)]):
		value = datetime.fromtimestamp(i['date'])
		print(f"Загружаю фото {i['id']} фото имеет {i['likes']['count']} лайков")

		url_foto = i['sizes'][-1]['url']


		if f"{i['likes']['count']}.jpg" not in res_dict.keys():
			file_name_upload = f"{i['likes']['count']}.jpg"
		else:
			file_name_upload = f"{i['likes']['count']}_{value.strftime('%Y-%m-%d_%H-%M-%S')}.jpg"

		res_dict[file_name_upload] = i['sizes'][-1]['type']

		ya_client.upload_foto(url_foto, file_name_upload)

	res_list = []
	for key, val in res_dict.items():
		res_list.append({"file_name": key, "size": val})
	with open("result.json", "w") as f:
		json.dump(res_list, f, ensure_ascii=False, indent=4) 

	print(f"Загрузка завершена, всего загружено {count_foto} фотографий, данные о фотография сохранены в файле result.json")
