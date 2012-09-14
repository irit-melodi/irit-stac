#!/usr/bin/env python

"""parse soclog file for settlers' pilot study to extract dialogue turns (speaker+text)
"""


test="""2011:10:10:17:46:57:481:+0100:GAME-TEXT-MESSAGE:[game=pilot01|player=Tomm|speaking-queue=[]|clay=0|ore=1|sheep=0|wheat=0|wood=1|unknown=0|knights=1|roads=[69,86,70,71,72,73,90]|settlements=[69,103,107]|cities=[]|dev-cards=1|text=Hey!]"""
 
offer = "2011:10:10:16:37:53:803:+0100:SOCGameTextMsg:game=pilot01|nickname=Server|text=Tomm traded 1 sheep for 1 ore from Dave."


WIKI = True

header = "^Turn^Time^Who^State^Text^Annot^Comment^"
table_format = "|%s|%s|%s|%s|%s| | |"

import sys
import re

trade1 = re.compile(r"Server\|text=(?P<offer>.+made an offer to trade.+$)")
trade2 = re.compile(r"Server\|text=(?P<score>.+(traded|gets|rolled|built).+$)")
#ressource = re.compile(r"Server\|text=(?P<getsit>.+gets.+$)")
#rolls = re.compile(r"Server\|text=(?P<inthehay>.+rolled.+$)")
#built = re.compile(r"Server\|text=(?P<inthehay>.+built.+$)")

regexp=re.compile(r"player=(?P<name>[^|]+)\|speaking-queue=\[\]\|(?P<state>.+)\|text=(?P<text>.+)\]$")


print header
n = 1
for line in open(sys.argv[1]):
    ok = False
    timestamp = line.strip().split(":+",1)[0]
    timestamp = ":".join(timestamp.split(":")[-4:])
    match1 = trade1.search(line.strip())
    if match1: 
        speaker = "Server" 
        text = match1.group("offer")
        state = " "
        ok = True
    else: 
        match2 = trade2.search(line.strip())
        if match2: 
            speaker = "Server" 
            text = match2.group("score")
            state = " "
            ok = True
        else: 
            match3 = regexp.search(line.strip())
            if match3:     
                speaker = match3.group("name")
                text = match3.group("text")
                state = match3.group("state").replace("|",",")
                ok = True
    if ok: 
        print table_format%(n,timestamp,speaker,state,text)
        n = n+1
