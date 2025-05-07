import requests
import hashlib
import random
import string
import json

APPID = "8335655dae4bc4f9"
APPSECRET = "06c31993a761e4a4d4831a860daf4460"
API_URL = "http://metrics.digitalvolvo.com/openapi/team/list"

def get_nonce_str(length=16):
    """生成随机字符串"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def make_sign(params, appsecret):
    """生成签名
    按照文档要求：
    1. 参数名ASCII码从小到大排序（字典序）
    2. 参数中appid和nonce_str随机码为必输
    3. 参数中如有数组或对象属性，用JSON.stringify()转换字符后参与拼接
    4. 最后拼接上key=appsecret
    """
    # 按参数名ASCII排序
    sorted_items = sorted(params.items())
    
    # 拼接成 key1=value1&key2=value2...
    pairs = []
    for k, v in sorted_items:
        if isinstance(v, (dict, list)):
            # 对象和数组需要JSON化，并确保没有空格
            v = json.dumps(v, separators=(',', ':'))
        pairs.append(f"{k}={v}")
    
    stringA = "&".join(pairs)
    # 拼接 appsecret
    stringSignTemp = f"{stringA}&key={appsecret}"
    print("String to sign:", stringSignTemp)
    # MD5 并大写
    sign = hashlib.md5(stringSignTemp.encode("utf-8")).hexdigest().upper()
    print("Generated sign:", sign)
    return sign

def get_team_list():
    """获取团队列表"""
    # 构造请求参数，严格按照文档要求的参数名
    params = {
        "appid": APPID,  # 使用appid而不是appId
        "nonce_str": get_nonce_str()  # 使用nonce_str而不是nonceStr
    }
    
    # 生成签名
    sign = make_sign(params, APPSECRET)
    params["sign"] = sign

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    print("\nRequest details:")
    print("URL:", API_URL)
    print("Headers:", headers)
    print("Body:", json.dumps(params, indent=2))
    
    try:
        resp = requests.post(API_URL, json=params, headers=headers)
        print("\nResponse details:")
        print("Status:", resp.status_code)
        print("Headers:", dict(resp.headers))
        print("Body:", resp.text)
        
        if resp.status_code == 200:
            return resp.json()
        else:
            print(f"Error: API returned status code {resp.status_code}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")
        return None

if __name__ == "__main__":
    result = get_team_list()
    if result:
        print("\nTeam list retrieved successfully!") 