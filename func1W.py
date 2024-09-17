from SPARQLWrapper import SPARQLWrapper, JSON
import requests
import csv
from string import Template
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
    print(list)
else:
    print(f"Error: {response.status_code}")


# 取得したエンティティの子エンティティ(instance of)が持つプロパティのIDとそのラベルを取得(このcodeのスコープ)
# できることなら、そのエンティティと同じプロパティを取得し、それが構造化で使われる例も集める
def count(label):
    query = Template(
        """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT (COUNT(?subject) AS ?c)
    WHERE {
    ?subject ?predicate ?object .
    FILTER(
        (?predicate = rdfs:label || ?predicate = rdfs:description) &&
        CONTAINS(LCASE(STR(?object)), "${label}")
    )
    }
    """
    )
    sparql = SPARQLWrapper(utils.LOV, returnFormat=JSON)
    sparql.setQuery(query.substitute(label=label))
    num = sparql.query().convert()["results"]["bindings"][0]["c"]["value"]
    return num


wdquery = Template(
    utils.PREFIXs
    + """
    select distinct ?pLabel where{
     ?s wdt:P31 wd:${id}.
     ?s ?p ?o.
    SERVICE wikibase:label {
        bd:serviceParam wikibase:language "en" .
    }
    }limit 100
    """
)
rslt = []
sparql = SPARQLWrapper(utils.WD, returnFormat=JSON)
for i in list:
    sparql.setQuery(wdquery.substitute(id=i[0]))
    rlist = sparql.query().convert()["results"]["bindings"]
    for r in rlist:
        label = r["pLabel"]["value"]
        if label not in rslt:
            num = count(label)
            if num != 0:
                rslt.append([label, num])

with open("rslt/" + nodeName + "WD.csv", "w", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Wikidata"])
    writer.writerow(["label", "num"])
    writer.writerows(rslt)
