import numpy as np
import requests
import json

test_arr = np.random.randn(10, 3, 224, 224)

# 原数据接口
# resp = requests.get("http://localhost:8501/v1/models/model1/metadata")
# print(resp.json())

# 测试bert
input_ids = [[ 101, 5356, 4923, 4384, 1862,  102,    0,    0,    0,    0,    0,    0,
            0,    0,    0,    0]]
token_type_ids = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]
attention_mask = [[1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]

url = "http://localhost:8501/v1/models/albert_binary_cls_pb/versions/1:predict"
headers = {'content-type': 'application/json'}

data = {
    "inputs":{
        "token_type_ids": token_type_ids,
        "attention_mask": attention_mask,
        "input_ids": input_ids
    }
}
# data = json.dumps(data)

r = requests.post(url, json=data, headers=headers)
print(r.status_code)
print(r.text)