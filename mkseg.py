#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
This is an educified version of the code/UNUSED/guapi/PredArg.py
script
"""

from __future__ import print_function

import argparse
import codecs
import copy
from collections import namedtuple

from educe.stac.util.context import\
    Context, sorted_first_widest
from educe.stac.annotation import\
    is_resource, turn_id
from educe.stac.util.args import\
    add_usual_output_args,\
    get_output_dir,\
    announce_output_dir,\
    read_corpus
from educe.stac.util.output import\
    mk_parent_dirs, output_path_stub
import educe.util


class ResourceAnnos(namedtuple("ResourceAnnos",
                              ["resources", "anaphora", "several"])):
    """
    All resources, anaphora, etc in a document
    """
    pass


class Config(namedtuple("Config",
                        ["emit_resources",
                         "emit_resource_status",
                         "emit_dialogue_acts",
                         "emit_dialogue_boundaries",
                         "fake_turn_ids"])):
    """
    To specify how we want extraction to be done
    """
    pass


class EduInfo(namedtuple("EduInfo",
                        ["edu",
                         "dialogue_act",
                         "turn_id",
                         "text",
                         "speaker",
                         "surface_act",
                         "addressees",
                         "rstuff"])):
    """
    Representation of some of the data used to build a segpair
    This is a bit incomplete, unfortunately
    """
    pass



STAC_UNSET = "Please choose..."  # sigh

UNKNOWN_RESOURCE_STATUSES = [STAC_UNSET, "?"]

KNOWN_RESOURCE_STATUSES =\
    ["Givable", "Not givable",
     "Receivable", "Not receivable",
     "Possessed", "Not possessed"]

OUTPUT_DIALOGUE_BOUNDARY = "*******END TURN************"


def rewrite_unknown(val):
    """
    replace a string value with 'Unknown' if it represents
    some kind of unknown value in the corpus
    """
    return "Unknown" if val == STAC_UNSET else val


def resource_snippet(config, resource):
    "output fragment for a resource"

    features = resource.features
    status_feat = features["Status"]

    if not config.emit_resource_status:
        status = "Unknown"
    elif status_feat in UNKNOWN_RESOURCE_STATUSES:
        status = "Unknown"
    elif status_feat in KNOWN_RESOURCE_STATUSES:
        status = status_feat
    else:
        raise Exception("Unexpected resource status: ", status_feat)
    template = " {status} ({kind}, {quantity})"

    kind = rewrite_unknown(features["Kind"])
    quantity = rewrite_unknown(features["Quantity"])

    return template.format(status=status,
                           kind=kind,
                           quantity=quantity)


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
def all_resources_snippet(config, edu, rstuff):
    "turn resource annotations for an edu into a segpair fragment"

    resources = [x for x in rstuff.resources if edu.encloses(x)]

    if resources:
        result = "#   Resource: "
        for resource in resources:
            result += resource_snippet(config, resource)
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


def get_eduinfo(config, doc, context, rstuff, edu):
    """
    extract the interesting parst of an EDU

    :: ... -> EduInfo
    """
    turn = context[edu].turn
    surface_act = edu.features.get("Surface_Act", "?")

    if edu.type == "Segment" or not config.emit_dialogue_acts:
        dialogue_act = "?"
    else:
        dialogue_act = edu.type


    addresee_feat = edu.features.get("Addressee", STAC_UNSET)
    addressees = set(x.strip() for x in addresee_feat.split(";"))
    if not addressees or STAC_UNSET in addressees:
        addressees = set("?")

    return EduInfo(edu=edu,
                   turn_id=turn_id(turn),
                   dialogue_act=dialogue_act,
                   text=doc.text(edu.text_span()),
                   surface_act=surface_act,
                   speaker=turn.features["Emitter"],
                   addressees=addressees,
                   rstuff=rstuff)


def eduinfo_set_turn_id(info, tid):
    """
    return a copy of an eduinfo tuple with an updated turn id

    there's probably a more pythonic way of doing this
    """
    return EduInfo(edu=info.edu,
                   turn_id=tid,
                   dialogue_act=info.dialogue_act,
                   text=info.text,
                   surface_act=info.surface_act,
                   speaker=info.speaker,
                   addressees=info.addressees,
                   rstuff=info.rstuff)


def eduinfo_to_string(config, info):
    """
    render a single eduinfo as a a string

    :: EduInfo -> String
    """
    template = "{dialogue_act} "+\
        "[Turn_ID: {turn_id} "+\
        "#    EDU_Span: {text}" +\
        "#   Speaker: {speaker}" +\
        "#  Surface_Act: {surface_act}"

    result = template.format(dialogue_act=info.dialogue_act,
                             turn_id=info.turn_id,
                             text=info.text,
                             speaker=info.speaker,
                             surface_act=info.surface_act)
    for addressee in sorted(info.addressees):
        result += "#   Addressee: " + addressee

    if config.emit_resources:
        result += all_resources_snippet(config, info.edu, info.rstuff)
    result += "]"
    return result


def eduinfo_list_to_string(config, infos):
    """
    massage segpairs into output: organise a list of
    (turn id, segline) pairs, and
    insert a marker whenever turns are more than 1 apart

    :: [EduInfo] -> String
    """
    result = []
    prev_turn = None
    for info in sorted(infos, key=lambda x: x.turn_id):
        if config.emit_dialogue_boundaries and\
            prev_turn is not None and info.turn_id - prev_turn > 1:
            result.append(OUTPUT_DIALOGUE_BOUNDARY)
        result.append(eduinfo_to_string(config, info))
        result.append("") # empty line
        prev_turn = info.turn_id
    if not config.emit_dialogue_boundaries:
        result.append(OUTPUT_DIALOGUE_BOUNDARY)
    return "\n".join(result)


def process_document(config, corpus, key, output_dir):
    """
    Read the document and write an equivalent .seg file in the output
    path
    """
    doc = corpus[key]
    if config.emit_resources:
        rstuff = ResourceAnnos(resources=[x for x in doc.units
                                          if is_resource(x)],
                               anaphora=[x for x in doc.relations
                                         if x.type == "Anaphora"],
                               several=[x for x in doc.schemas
                                        if x.type == "Several_resources"])
    else:
        rstuff = ResourceAnnos(resources=[],
                              anaphora=[],
                              several=[])

    # print(rstuff.anaphora)
    output_filename = output_path_stub(output_dir, key) + ".seg"
    mk_parent_dirs(output_filename)
    context = Context.for_edus(doc)

    infos_ = [get_eduinfo(config, doc, context, rstuff, edu)
              for edu in sorted_first_widest(context)]
    if config.fake_turn_ids:
        infos = [eduinfo_set_turn_id(x, i + 1)
                 for i, x in enumerate(infos_)]
    else:
        infos = [x for x in infos_ if x.turn_id is not None]

    with codecs.open(output_filename, 'w', 'utf-8') as fout:
        print(eduinfo_list_to_string(config, infos), file=fout)


def mk_argparser():
    """
    Command line parser for this script
    """
    psr = argparse.ArgumentParser(description='.seg intermediary file writer')

    psr.add_argument('corpus', metavar='DIR', help='corpus dir')
    # shall we pull resources out of the data?
    psr.add_argument('--no-resources', dest='resources',
                     action='store_false',
                     default=True,
                     help='suppress resource extraction')
    psr.add_argument('--resources',
                     action='store_true',
                     help='allow resource extraction (default)')
    psr.set_defaults(resources=True)
    # if we do grab resources, should we extract their
    # giveble/receivable status or leave it Unknown?
    psr.add_argument('--no-resource-status', dest='resource_status',
                     action='store_false',
                     default=True,
                     help='suppress resource status labels')
    psr.add_argument('--resource-status',
                     action='store_true',
                     help='allow resource status labels (default)')
    psr.set_defaults(resource_status=True)

    # what about dialogue acts?
    # you could also just extract from unannotated, but skipping
    # dialogue acts lets you pull out other stuff that may be in
    # units like the addresees whilst ignoring the dialogue acts
    psr.add_argument('--no-dialogue-acts', dest='dialogue_acts',
                     action='store_false',
                     default=True,
                     help='suppress resource extraction')
    psr.add_argument('--dialogue-acts',
                     action='store_true',
                     help='allow resource extraction (default)')
    psr.set_defaults(dialogue_acts=True)

    # dialogue boundaries
    psr.add_argument('--no-dialogue-boundaries',
                     dest='dialogue_boundaries',
                     action='store_false',
                     default=True,
                     help='suppress dialogue boundaries')
    psr.add_argument('--dialogue-boundaries',
                     action='store_true',
                     help='emit dialogue boundaries (called TURN here)')
    psr.set_defaults(dialogue_boundaries=True)

    psr.add_argument('--fake-turn-ids',
                     action='store_true',
                     help="ignore turn ids; just enumerate")

    psr.add_argument('--pipeline',
                     action='store_true',
                     help="default settings for pipeline use"
                     " (implies --no-dialogue-boundaries, etc)")
    # don't allow stage control; must be units or unannotated
    educe.util.add_corpus_filters(psr,
                                  fields=['doc', 'subdoc', 'annotator'])
    psr.add_argument('--stage',
                     choices=['units', 'unannotated'],
                     default='units',
                     help='which section of the corpus to read')
    add_usual_output_args(psr)
    return psr


def main():
    "create a .seg file for every file in the corpus"
    args = mk_argparser().parse_args()
    corpus = read_corpus(args)
    output_dir = get_output_dir(args)
    if args.pipeline:
        args.resources = True
        args.resource_status = False
        args.dialogue_acts = False
        args.dialogue_boundaries = False
        args.fake_turn_ids = True
    config = Config(emit_resources=args.resources,
                    emit_resource_status=args.resource_status,
                    emit_dialogue_acts=args.dialogue_acts,
                    emit_dialogue_boundaries=args.dialogue_boundaries,
                    fake_turn_ids=args.fake_turn_ids)
    for key in corpus:
        process_document(config, corpus, key, output_dir)
    announce_output_dir(output_dir)

if __name__ == "__main__":
    main()
