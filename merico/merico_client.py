import requests
import hashlib
import random
import string
import json

class Client:
    def __init__(self, endpoint, appid, secret):
        self.endpoint = endpoint.rstrip('/')
        self.appid = appid
        self.secret = secret

    def _get_nonce_str(self, length=16):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

    def _make_sign(self, params):
        sorted_items = sorted(params.items())
        pairs = []
        for k, v in sorted_items:
            if isinstance(v, (dict, list)):
                v = json.dumps(v, separators=(',', ':'))
            pairs.append(f"{k}={v}")
        stringA = "&".join(pairs)
        stringSignTemp = f"{stringA}&key={self.secret}"
        return hashlib.md5(stringSignTemp.encode("utf-8")).hexdigest().upper()

    def post(self, path, extra_params=None):
        url = f"{self.endpoint}{path}"
        params = {
            "appid": self.appid,
            "nonce_str": self._get_nonce_str()
        }
        if extra_params:
            params.update(extra_params)
        params["sign"] = self._make_sign(params)
        headers = {"Content-Type": "application/json"}
        resp = requests.post(url, json=params, headers=headers)
        resp.raise_for_status()
        return resp.json() 