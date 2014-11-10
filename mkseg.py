#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from datetime import date
from pprint import pprint
from os import path as fp

"""
This is an educified version of the code/UNUSED/guapi/PredArg.py
script
"""

RESOURCE_STATUSES =\
    ["Givable", "Not givable",
     "Receivable", "Not receivable",
     "Possessed", "Not possessed"]

def _resource_snippet(resource):
    "output fragment for a resource"

    status = resource.Status

    if resource.Status == "?":
        status = "Unknown"
    elif resource.Status in RESOURCE_STATUSES:
        status = resource.Status
    else:
        raise Exception("Unexpected resource status: ", resource.Status)
    template = " {status} ({kind}, {quantity})"
    return template.format(status=status,
                           kind=resource.Kind,
                           quantity=resource.Quantity)


def _link_snippet(left, right):
    "output fragment for an anaphoric link"
    template = " #Anaphora Link:({left}, {right})"
    return template.format(left=left.Text,
                           right=right.Text)


def _anaphor_snippet(left, right, anaphora):
    "output fragment for anaphoric links"

    result = ""
    if left.Kind == "Anaphoric":
        for anaphor in anaphora:
            if anaphor.Left_argument == left.ID:
                result += _link_snippet(anaphor.Full_Left_argument,
                                        anaphor.Full_Right_argument)
            if anaphor.Right_argument == right.ID:
                result += _link_snippet(anaphor.Full_Right_argument,
                                        anaphor.Full_Left_argument)
    return result


def _segments_to_lines(segments):
    """
    return lines of .seg output

    insert a marker whenever turns are more than 1 apart
    """
    def turn_id(seg):
        ":: Int"
        return int(seg.split()[2])

    sorted_segments = sorted((turn_id(s), s)
                             for s in segments)

    result = []
    prev_turn = None
    for turn, segment in sorted_segments:
        if prev_turn is not None and turn - prev_turn > 1:
            result.append("*******END TURN************")
        result.append(segment)
        prev_turn = turn
    return result


def _all_resources_snippet(seg, anaphors_detail):
    result = ""
    seg0 = seg[0]
    several_ressource_text = []
    if len(seg0.Resources) > 0:
        for i in seg0.Resources:
            if isinstance(i, Several_resources):
                several_ressource_text.append(i.Text)

    if len(seg0.Resources) > 0:
        result = result + "#   Resource: "
        for j in seg0.Resources:
            if several_ressource_text != []:
                if isinstance(j, Several_resources):
                    resource = j.Resources[0]
                    result += _resource_snippet(resource)
                    result += _anaphor_snippet(resource, j, anaphors_detail)
                else:
                    if j.Text.split()[0] not in several_ressource_text[0]:
                        result += _resource_snippet(j)
                        result += _anaphor_snippet(j, j, anaphors_detail)
            #pas de schéma on traite les ressources normalement"
            else:
                result += _resource_snippet(j)
                result += _anaphor_snippet(j, j, anaphors_detail)
    return result


def Create_Unit(Annotator, base_directory, uunits, uiter):
    # find speakers and idTurn


    def get_speaker_idturn(docfile):
        speaker_idturn = dict()
        anaphors=[]
        for j in uunits:
            if fp.basename(j.Docfile)==docfile:
                for i in j.Dialogues:
                    anaphors.append(i.Full_relations)
                    for k in i.Turns:
                        speaker_idturn[k.Shallow_ID]=k.Emitter
                break

        return speaker_idturn, anaphors

    segs = dict()
    for seg in uiter.get_segments():
        fbasename = fp.basename(seg[0].Textfile)
        result = ""
        if fbasename not in segs:
            segs[fbasename] = []
            speaker_idturn, anaphors = get_speaker_idturn(fbasename)
            anaphors_detail = []
            for anaphor in anaphors:
                anaphors_detail.extend((i.ID, i.Left_argument, i.Right_argument)
                                       for i in anaphor)


        speaker = speaker_idturn[seg[0].Turn]
        template = "{dialogue_act} [ Turn_ID: {turn_id} "+\
                   "#    EDU_Span: {span}" +\
                   "#   Speaker: {speaker}" +\
                   "#  Surface_Act: {surface_act}"
        result += template.format(dialogue_act=seg[0],
                                  turn_id=seg[0].Turn,
                                  edu_span=str(seg[0].Text),
                                  speaker=str(speaker),
                                  surface_act=str(seg[0].Surface_act_type))

        for receiver in seg[0].Receivers:
           result += "#   Addressee: {}".format(receiver)

        # appends stuff to result
        result += _all_resources_snippet(seg, anaphors)
        result += "]\n"
        segs[fbasename].append(result)

    for filename, segments in segs.items():
        with open(base_directory + filename + "_"+Annotator+ ".seg", "w") as f:
            print "\n".join(_segments_to_lines(segments))
