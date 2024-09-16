# 候補として出したいのは、
# 1.[プロパティリスト、クラス名]->単一プロパティ
# 2.[プロパティリスト,クラス名]->[プロパティのリスト]
# 3.[クラスリスト]->クラスを繋ぐ単一プロパティ
# 4.[クラスリスト]->クラスを繋ぐクラスとプロパティ
# ここでは１,2の候補となりそうな単語群をやる

from SPARQLWrapper import SPARQLWrapper, JSON
from string import Template
import os
import sys
import requests
import csv

sys.path.append(os.pardir)
from package import utils

nodeName = input()


def searchFromCN(nodeName):
    node = requests.get("https://api.conceptnet.io/query?node=/c/en/" + nodeName).json()
    rslt1 = []
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

    for edge in node["edges"]:
        end = edge["end"] if edge["end"]["label"] != nodeName else edge["start"]
        sparql.setQuery(query.substitute(label=end["label"]))
        num = sparql.query().convert()["results"]["bindings"][0]["c"]["value"]
        if num != 0:
            # LOVでのカウント0の単語を消す
            rslt1.append(end["label"], [edge["rel"]["label"], num])
    rsltCN = sorted(rslt1, reverse=True, key=lambda x: x[2])
    return rsltCN


with open(nodeName + "CN.csv", "w", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["ConceptNet"])
    writer.writerow(["end", "rel", "count"])
    writer.writerows(searchFromCN(nodeName))
    print("done ConNet")
