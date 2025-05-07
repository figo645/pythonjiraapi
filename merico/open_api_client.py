import hashlib
import json
from typing import Dict
import requests


class Client:
    def __init__(self, endpoint: str, app_id: str, secret: str):
        self.endpoint = endpoint
        self.app_id = app_id
        self.secret = secret

    def get_sign(self, body: Dict):
        kvs = []
        for key, value in body.items():
            if value is not None and key != "sign":
                kvs.append(key + '=' + (value if type(value) ==
                           str else json.dumps(value, ensure_ascii=False, separators=(',', ':'))))
        to_encode_str = "&".join(sorted(kvs))
        to_encode_str = to_encode_str + '&key=' + self.secret
        # print(f"to_encode_str = {to_encode_str}")
        m = hashlib.md5()
        m.update(to_encode_str.encode("utf-8"))
        return m.hexdigest().upper()

    # def request(self, path: str, data: Dict, nonce_str: str = '1593359464730'):
    #     data['appid'] = self.app_id
    #     data['nonce_str'] = nonce_str
    #     data['sign'] = self.get_sign(data)

    #     url = f'{self.endpoint}/{path.lstrip("/")}'
    #     # if path == '/developer/tech-tag':
    #     print(f"\n")
    #     print(f"*********************************一次调用开始*********************************")
    #     print(f"url = {url}")
    #     print(f"data = {data}")
    #     print(f"*********************************一次调用结束*********************************")
    #     print(f"\n")

    #     response = requests.post(url, json=data)
    #     if response.status_code != 200:
    #         raise Exception(f"request got a error: {response}")
    #         print(f"response = {response}")
    #     result = response.json()
    #     return result['code'], result['message'], result.get('data', None)


    def request(self, path: str, data: Dict, nonce_str: str = '1593359464730'):
        data['appid'] = self.app_id
        data['nonce_str'] = nonce_str
        data['sign'] = self.get_sign(data)

        url = f'{self.endpoint}/{path.lstrip("/")}'
        print(f"*********************************一次调用开始*********************************")
        # print(f"url = {url}")
        # print(f"data = {data}")
        try:
            response = requests.post(url, json=data)
            response.raise_for_status()  # 检查 HTTP 状态码
        except requests.exceptions.RequestException as e:
            # 打印详细的错误信息
            # print("Error occurred during request.")
            print(f"Response Status Code: {response.status_code if 'response' in locals() else 'No Response'}")
            # print(f"Response Headers: {response.headers if 'response' in locals() else 'No Headers'}")
            try:
                print(f"Response Content: {response.json() if 'response' in locals() else 'No Content'}")
            except Exception:
                print(f"Response Text: {response.text if 'response' in locals() else 'No Text'}")
            # print(f"Exception: {e}")

            print(f"*********************************一次调用结束*********************************")
            # 返回一个标准化的错误响应而不是抛出异常
            return -1, f"Request failed: {str(e)}", response.json().get('data', response.json())

        # 正常处理响应
        result  = response.json()
        code    = result.get('code', 200)
        message = result.get('message', 'success')
        data    = result.get('data', result)
        print(f"*********************************一次调用结束*********************************")

        return code, message, data

