#!/usr/bin/python
# -*- coding: utf-8 -*-
# We should be doing it bottom up, from the most detailed classes to the most "enclosing" ones!

from object_crawler import *

u_annot_file = "./pilot03_1_stac_u_06062012.aa"
d_annot_file = "./pilot03_1_stac_d_06062012.aa"
text_file = "./pilot03_1.ac"

objcrawl = Object_crawler(u_annot_file, d_annot_file, text_file)

game =  objcrawl.get_edus()

discourse_structures = objcrawl.get_discourse()

print game.Dialogues[2].Turns[2].Segments[1].Text

print discourse_structures[2].Full_Discourse_units[-1].Text


