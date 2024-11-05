from urllib.parse import urlparse
import csv

"""
Schema->NameSpace,DSPs
Schema.namesearch
Schema.classsearch

Namespace->nspaces
Namespace->goi
Namespace.URI   a:bをURIに返す
Namespace.addNameSpace

D_Template->name,cls,props
"""


class NameSpace:
    def __init__(self):
        self.namespaces = {
            "dc": "http://purl.org/dc/elements/1.1/",
            "dcterms": "http://purl.org/dc/terms/",
            "foaf": "http://xmlns.com/foaf/0.1/",
            "skos": "http://www.w3.org/2004/02/skos/core#",
            "xl": "http://www.w3.org/2008/05/skos-xl#",
            "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
            "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
            "owl": "http://www.w3.org/2002/07/owl#",
            "xsd": "http://www.w3.org/2001/XMLSchema#",
        }  # 接頭辞と名前空間の対応を保存
        self.goi = {"undefined": 0}  # 使われている全語彙を保存
        for i in self.namespaces.values():
            self.goi[i] = 0

    def checkNameSpace(self, URI):
        # URIをチェックし、新しい語彙のタームならばself.namespaceに保存、namespaceを返す
        parsed = urlparse(URI)
        namespace = ""
        if all([parsed.scheme, parsed.netloc]):  # URIならば
            if "#" in URI:
                namespace = URI.split("#")[0] + "#"
                if namespace not in self.goi:
                    self.goi[namespace] = 1
                else:
                    self.goi[namespace] += 1
            else:
                namespace = "/".join(URI.split("/")[:-1]) + "/"
                if namespace not in self.goi:
                    self.goi[namespace] = 1
                else:
                    self.goi[namespace] += 1
        elif ":" in URI:
            initial = URI.split(":")[0]
            if initial in self.namespaces:
                namespace = self.namespaces[initial]
                self.goi[namespace] += 1
            else:
                namespace = "undefined"
                self.goi["undefined"] += 1
        else:
            namespace = "undefined"
            self.goi["undefined"] += 1
        return namespace

    def URI(self, term):
        # a:bというタームをURIで返す
        if term.split(":")[0] in self.namespaces:
            return self.namespaces[term.split(":")[0]] + term.split(":")[1]
        else:
            return term

    def addNameSpace(self, list):
        self.namespaces[list[0]] = list[1]
        self.goi[list[1]] = 0


class D_Template:
    def __init__(self, name, NameSpace):
        self.name = name
        self.NS = NameSpace
        self.cls = {}
        self.props = []

    def addSentence(self, list):
        namespace = self.NS.checkNameSpace(list[1])
        if list[4] == "ID":
            self.cls["URI"] = list[1]
            self.cls["label"] = (
                list[0]
                if list[0] != ""
                else (
                    list[1]
                    if namespace == "undefined"
                    else list[1].replace[namespace, ""]
                )
            )
            self.cls["namespace"] = namespace
        else:
            newProp = {}
            newProp["URI"] = list[1]
            newProp["label"] = (
                list[0]
                if list[0] != ""
                else (
                    list[1]
                    if namespace == "undefined"
                    else list[1].replace[namespace, ""]
                )
            )
            newProp["namespace"] = namespace
            newProp["range"] = list[5] if list[4] == "構造化" else "other"
            self.props.append(newProp)

    def name(self):
        return self.name

    def cls(self):
        return self.cls

    def props(self):
        return self.props


class Schema:
    def __init__(self, csv):
        blockName = ""
        Dsp = None
        self.goi = NameSpace()
        self.DSPs = []
        for row in csv:
            if "[@NS]" in row[0]:
                blockName = "@NS"
            elif row[0].startswith("[") and row[0].endswith("]"):
                blockName = row[0][1:-1]
                Dsp = D_Template(blockName, self.goi)
                self.DSPs.append(Dsp)
            elif "#" in row[0] or row[0] == "":
                pass
            else:
                if blockName == "@NS":
                    self.goi.addNameSpace(row)
                else:
                    if Dsp:
                        Dsp.addSentence(row)

    def createLinks(self):
        # DSP内にリンクの情報を作る
        return

    def searchDSPwithName(self, name):
        for i in self.DSPs:
            if i.name() == name:
                return i
        return False

    def searchDSPwithClass(self, name):
        if ":" in name:
            if name.split(":")[0] in self.goi.namespaces:
                namespace = self.goi.namespaces[name.split(":")[0]]
                name = namespace + name.split(":")[1]
        for i in self.DSPs:
            if i.cls["URI"] == name:
                return i
        return False


def csvOpener(filename):
    with open(filename, newline="", encoding="utf-8") as csvfile:
        csvreader = csv.reader(csvfile)
        return csvreader
