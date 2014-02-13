#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Api on discourse markers (lexicon I/O mostly)
"""
try:
    import xml.etree.cElementTree as ET
except:
    import xml.etree.ElementTree as ET
import sys


_table = {
    "1":{"marker":"connecteur","form":"forme"},
    "2":{"marker":"connective","form":"form"}
    }
          

_stopwords = set(u"à et ou pour en".split())


class Marker:
    """wrapper class for discourse marker read from Lexconn, version 1 or 2

    should include at least id, cat (grammatical category)
    version 1 has  type (coord/subord)
    version 2 has grammatical host and lemma
    """
    def __init__(self,elmt,version="2",stop=_stopwords):
         self._forms = [x.text.strip() for x in elmt.findall(".//%s"%_table[version]["form"])]
         self.__dict__.update(elmt.attrib)
         # 
         if version == "2":
             self.relations = [x.attrib["relation"] for x in elmt.findall(".//use")]
         else: 
             self.relations = [x.strip() for x in self.relations.split(",")]
             self.lemma = self.forms[0]
             self.host = None
             
    def get_forms(self):
        return self._forms

    def get_lemma(self):
        return self.lemma

    def get_relations(self):
        return self.relations

class LexConn:

    def __init__(self,infile,version="2",stop=_stopwords):
        """read lexconn file, version is 1 or 2
        """
        lex = ET.parse(infile)
        markers = [Marker(x,version=version) for x in lex.findall(".//%s"%_table[version]["marker"])]
        markers = [x for x in markers if x.get_lemma() not in stop]
        self._markers = dict([(x.id,x) for x in markers]) 

    def __iter__(self):
        return iter(self._markers.values())

    def get_by_id(self,id):
        return self._markers.get(id,None)

    def get_by_form(self,form):
        return [x for x in self._markers.values() if form in x.get_forms()]
    
    def get_by_lemma(self,lemma):
        return [x for x in self._markers.values() if lemma==x.get_lemma()]



# tests
if __name__=="__main__":
    import sys
    
    infile = sys.argv[1]
    lex = LexConn(infile,version=sys.argv[2])
