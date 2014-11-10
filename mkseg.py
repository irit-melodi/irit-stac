#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function

import argparse
import codecs
from collections import namedtuple

from educe.stac.util.context import\
    Context, sorted_first_widest
from educe.stac.annotation import\
    is_edu, is_resource, turn_id
from educe.stac.util.args import\
    add_usual_output_args, get_output_dir, announce_output_dir
from educe.stac.util.output import\
    mk_parent_dirs, output_path_stub
import educe.util

"""
This is an educified version of the code/UNUSED/guapi/PredArg.py
script
"""

class ResourceInfo(namedtuple("ResourceInfo",
                              ["resources", "anaphora", "several"])):
    """
    All resources, anaphora, etc in a document
    """
    pass


UNKNOWN_RESOURCE_STATUSES = ["Please choose...", "?"]

KNOWN_RESOURCE_STATUSES =\
    ["Givable", "Not givable",
     "Receivable", "Not receivable",
     "Possessed", "Not possessed"]

def resource_snippet(resource):
    "output fragment for a resource"

    features = resource.features
    status_feat = features["Status"]

    if status_feat in UNKNOWN_RESOURCE_STATUSES:
        status = "Unknown"
    elif status_feat in KNOWN_RESOURCE_STATUSES:
        status = status_feat
    else:
        raise Exception("Unexpected resource status: ", status_feat)
    template = " {status} ({kind}, {quantity})"
    return template.format(status=status,
                           kind=features["Kind"],
                           quantity=features["Quantity"])


def link_snippet(left, right):
    "output fragment for an anaphoric link"
    template = " #Anaphora Link:({left}, {right})"
    return template.format(left=left.Text,
                           right=right.Text)


def anaphor_snippet(left, right, anaphora):
    "output fragment for anaphoric links"

    result = ""
    if left.Kind == "Anaphoric":
        for anaphor in anaphora:
            if anaphor.Left_argument == left.ID:
                result += link_snippet(anaphor.Full_Left_argument,
                                        anaphor.Full_Right_argument)
            if anaphor.Right_argument == right.ID:
                result += link_snippet(anaphor.Full_Right_argument,
                                        anaphor.Full_Left_argument)
    return result


# TODO: anaphora and several_resources
def all_resources_snippet(edu, rstuff):
    "turn resource annotations for an edu into a segpair fragment"

    resources = [x for x in rstuff.resources if edu.encloses(x)]

    if resources:
        result = "#   Resource: "
        for resource in resources:
            result += resource_snippet(resource)
        return result
#        for j in seg0.Resources:
#            if several_ressource_text != []:
#                if isinstance(j, Several_resources):
#                    resource = j.Resources[0]
#                    result += resource_snippet(resource)
#                    result += anaphor_snippet(resource, j, anaphors_detail)
#                else:
#                    if j.Text.split()[0] not in several_ressource_text[0]:
#                        result += resource_snippet(j)
#                        result += anaphor_snippet(j, j, anaphors_detail)
#            #pas de schéma on traite les ressources normalement"
#            else:
#                result += resource_snippet(j)
#                result += anaphor_snippet(j, j, anaphors_detail)
    else:
        return ""


def edu_to_segpair(doc, context, rstuff, edu):
    """
    output corresponding to a single EDU

    :: ... -> (Int, String)
    """

    turn = context[edu].turn
    tid = turn_id(turn)

    template = "{dialogue_act} "+\
        "[ Turn_ID: {turn_id} "+\
        "#    EDU_Span: {text}" +\
        "#   Speaker: {speaker}" +\
        "#  Surface_Act: {surface_act}"

    surface_act = edu.features.get("Surface_Act", "?")
    result = template.format(dialogue_act=edu.type,
                             turn_id=tid,
                             text=doc.text(edu.text_span()),
                             speaker=turn.features["Emitter"],
                             surface_act=surface_act)

    addressees = set(x.strip()
                     for x in edu.features["Addressee"].split(";"))
    if "Please choose..." in addressees:
        addressees = set("?")
    for addressee in sorted(addressees):
        result += "#   Addressee: " + addressee

    result += all_resources_snippet(edu, rstuff)
    result += "]"
    return (tid, result)


def segpairs_to_string(segpairs):
    """
    massage segpairs into output: organise a list of
    (turn id, segline) pairs, and
    insert a marker whenever turns are more than 1 apart

    :: [(Int, String)] -> String
    """
    result = []
    prev_turn = None
    for turn, segment in sorted(segpairs):
        if prev_turn is not None and turn - prev_turn > 1:
            result.append("*******END TURN************")
        result.append(segment)
        result.append("") # empty line
        prev_turn = turn
    return "\n".join(result)


def process_document(corpus, key, output_dir):
    """
    Read the document and write an equivalent .seg file in the output
    path
    """
    doc = corpus[key]
    rstuff = ResourceInfo(resources=[x for x in doc.units
                                     if educe.stac.is_resource(x)],
                          anaphora=[x for x in doc.relations
                                    if x.type == "Anaphora"],
                          several=[x for x in doc.schemas
                                   if x.type == "Several_resources"])

    output_filename = output_path_stub(output_dir, key) + ".seg"
    mk_parent_dirs(output_filename)
    context = Context.for_edus(doc)

    segpairs = [edu_to_segpair(doc, context, rstuff, edu)
                for edu in sorted_first_widest(context)]

    with codecs.open(output_filename, 'w', 'utf-8') as fout:
        print(segpairs_to_string(segpairs), file=fout)


def read_corpus_at_stage(args, stage, verbose=True):
    """
    Read the section of the corpus specified in the command line arguments.
    """
    is_interesting0 = educe.util.mk_is_interesting(args)
    is_interesting = lambda k: is_interesting0(k) and k.stage == stage
    reader = educe.stac.Reader(args.corpus)
    anno_files = reader.filter(reader.files(), is_interesting)
    return reader.slurp(anno_files, verbose)


def mk_argparser():
    """
    Command line parser for this script
    """
    psr = argparse.ArgumentParser(description='.seg intermediary file writer')

    psr.add_argument('corpus', metavar='DIR', help='corpus dir')
    # don't allow stage control; must be units
    educe.util.add_corpus_filters(psr,
                                  fields=['doc', 'subdoc', 'annotator'])
    add_usual_output_args(psr)
    return psr


def main():
    "create a .seg file for every file in the corpus"
    args = mk_argparser().parse_args()
    corpus = read_corpus_at_stage(args, 'units')
    output_dir = get_output_dir(args)
    for key in corpus:
        process_document(corpus, key, output_dir)
    announce_output_dir(output_dir)

if __name__ == "__main__":
    main()
