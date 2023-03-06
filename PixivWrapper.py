import requests
import json

from bs4 import BeautifulSoup

#from recaptcha import anticaptcha_solver

class PixivWrapper:
    
    def __init__(self, captcha_key = None):
        self.captcha_key = captcha_key
        self.headers = {
            'authority': 'accounts.pixiv.net',
            'accept': 'application/json',
            'accept-language': 'ja-JP,ja;q=0.9',
            'cache-control': 'max-age=0',
            'origin': 'https://accounts.pixiv.net',
            'referer': 'https://pixiv.net/',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="101"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Linux; Android 11; CPH2013) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.40 Mobile Safari/537.36',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
       
        
    def login(self, mail, password):
        session = self.session
        login_page = session.get("https://accounts.pixiv.net/login")
        tt = login_page.text.split("pixivAccount.tt")[-1].split('"')[2]
        
        #captcha = anticaptcha_solver("https://accounts.pixiv.net/login", self.captcha_key, "6LfF1dcZAAAAAOHQX8v16MX5SktDwmQINVD_6mBF")
        data = {
            'login_id': mail,
            'password': password,
            'source': 'accounts',
            'app_ios': '0',
            'ref': '',
            'return_to': 'https://www.pixiv.net/',
            'g_recaptcha_response': '',
            'recaptcha_enterprise_score_token': captcha,
            'tt': tt
        }
           
        response = self.session.post('https://accounts.pixiv.net/ajax/login', data=data)
        print(response.text)
    
    def get_all_images_from_llust(self, illust_id: str):
        url = "https://www.pixiv.net/touch/ajax/illust/details"
        params = {
            "illust_id": illust_id
        }
        
        response = self.session.get(url, params=params)
        response_json = json.loads(json.dumps(response.json(), ensure_ascii=False))
        details = response_json["body"]["illust_details"]
        
        url_list = []
        base_url = details["url"]
        path, path2  = base_url.split("_p0_")
        for page in range(len(details["illust_images"])):
            url_list.append(path + f"_p{str(page)}_" + path2)
            
        return url_list
    
    def search_illust(self, query:str, page: int):
        url = "https://www.pixiv.net/touch/ajax/search/illusts"
        params = {
            "word": query,
            "type": "illust_and_ugoira",
            "s_mode": "s_tag_full",
            "lang": "ja",
            "p": page
        }
        
        response = self.session.get(url, params=params)
        response_json = json.loads(json.dumps(response.json(), ensure_ascii=False))
        body = response_json["body"]
        
        search_result = []
        for illust in body["illusts"]:
            if illust.get("is_ad_container"):
                continue  #ignore advertising
            
            title = illust["title"]
            tag = illust["tags"]
            caption = illust["comment"]
            illust_id = illust["id"]
            image_urls = self.get_all_images_from_llust(illust_id)
            thumbnail = image_urls[0]
            
            author_details = illust["author_details"]
            author_url = "https://pixiv.net/users/" + author_details["user_id"]
            author_name = author_details["user_name"]

            search_result.append({
                "title": title,
                "tag": tag,
                "caption": caption,
                "illust_id": illust_id,
                "image_urls": image_urls,
                "author":{
                    "name": author_name,
                    "url": author_url
                }
            })

        return search_result


if __namr__ == "__main__":
    query = input("Please enter query. >>> ")
    pixiv = PixivWrapper()
    pixiv.search_illust(query, 1)
