#!/usr/bin/python
# -*- coding: utf-8 -*-

'''Function to "prettify" XML: courtesy of http://www.doughellmann.com/PyMOTW/xml/etree/ElementTree/create.html
'''

from xml.etree import ElementTree
from xml.dom import minidom
import sys

def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ElementTree.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string.replace('\n', ''))
    return reparsed.toprettyxml(indent="")

if __name__ == '__main__':
    tree = ElementTree.parse(sys.argv[1])
    root = tree.getroot()
    print prettify(root)
