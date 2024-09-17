# ここでは２の構造をwikidataが持つ構造で調べる
import requests
import csv
from package import utils

nodeName = input()
wdAPI = "https://www.wikidata.org/w/api.php"

# パラメータ
params = {
    "action": "wbsearchentities",
    "search": nodeName,
    "language": "en",
    "format": "json",
}
# APIリクエスト
response = requests.get(wdAPI, params=params)

# レスポンスの確認
if response.status_code == 200:
    data = response.json()
    list = [[s["id"], s["display"]["label"]["value"]] for s in data["search"]]
else:
    print(f"Error: {response.status_code}")

# 取得したエンティティの子エンティティ(instance of*)が持つプロパティのIDとそのラベルを取得
# できることなら、そのエンティティと同じプロパティを取得し、それが構造化で使われる例も集める(このcodeのスコープ)
