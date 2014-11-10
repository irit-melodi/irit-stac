#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from datetime import date
from pprint import pprint

"""
This is an educified version of the code/UNUSED/guapi/PredArg.py
script
"""

def Create_Unit(Annotator,base_directory, uunits, uiter):
    # find speakers and idTurn


    def get_speaker_idturn(docfile):
        speaker_idturn = dict()
        anaphors=[]
        for j in uunits:
            if basename(j.Docfile)==docfile:
                for i in j.Dialogues:
                    anaphors.append(i.Full_relations)
                    for k in i.Turns:
                        speaker_idturn[k.Shallow_ID]=k.Emitter
                break

        return speaker_idturn, anaphors

    def get_ressource(seg,several_ressource_text,anaphors_detail,  result):
         if len(seg[0].Resources) > 0:
               for i in seg[0].Resources:
                   if isinstance(i,Several_resources)==True:
                       several_ressource_text.append(i.Text)


         if len(seg[0].Resources) > 0:
                    result = result + '#' +'   Resource: '
                    for j in seg[0].Resources:

                      if several_ressource_text!=[]:
                          if isinstance(j,Several_resources)==True:
                              #Je traite les scheméas a part avec les opérateurs
                              if j.Resources[0].Status=="Givable":
                                result = result + ' Givable '
                              if j.Resources[0].Status=="Not givable":
                                result = result + ' Not givable '
                              if j.Resources[0].Status=="Receivable":
                                result = result + ' Receivable '
                              if j.Resources[0].Status=="Not receivable":
                                result = result + ' Not receivable'
                              if j.Resources[0].Status=="Possessed":
                                result = result  + ' Possessed'
                              if j.Resources[0].Status=="Not possessed":
                                result = result  + ' Not Possessed '
                              if j.Resources[0].Status=="?":
                                result = result  + ' Unknown '

                              result = result + '(' + j.Resources[0].Kind + ', ' + j.Resources[0].Quantity + ')'  + j.Operator +  '(' + j.Resources[1].Kind + ', ' + j.Resources[1].Quantity + ')'

                              if j.Resources[0].Kind=="Anaphoric":
                                 for anaph in anaphors_detail:
                                     if anaph!=[]:
                                         for a in anaph:
                                             if a.Left_argument==j.Resources[0].ID:
                                                 result=result+ ' #' + 'Anaphora Link:(' + str(a.Full_Left_argument.Text) + ' , ' + str(a.Full_Right_argument.Text) + ' )'
                                             if a.Right_argument==j.ID:
                                                 result=result+ ' #' + 'Anaphora Link:(' + str(a.Full_Right_argument.Text) + ' , ' + str(a.Full_Left_argument.Text) + ' )'

                          else:
                              if j.Text.split()[0] not in several_ressource_text[0]:

                                if j.Status=="Givable":
                                  result = result + ' Givable '
                                if j.Status=="Not givable":
                                  result = result + ' Not givable '
                                if j.Status=="Receivable":
                                  result = result + ' Receivable '
                                if j.Status=="Not receivable":
                                  result = result + ' Not receivable '
                                if j.Status=="Possessed":
                                  result = result  + ' Possessed '
                                if j.Status==" Not possessed":
                                  result = result  + ' Not Possessed '
                                if j.Status=="?":
                                  result = result  + ' Unknown '

                                result = result + '(' + j.Kind
                                result = result + ', ' + j.Quantity + ') '
                                if j.Kind=="Anaphoric":
                                 for anaph in anaphors_detail:
                                     if anaph!=[]:
                                         for a in anaph:
                                             if a.Left_argument==j.ID:
                                                 result=result+ ' #' + 'Anaphora Link:(' + str(a.Full_Left_argument.Text) + ' , ' + str(a.Full_Right_argument.Text) + ' )'
                                             if a.Right_argument==j.ID:
                                                 result=result+ ' #' + 'Anaphora Link:(' + str(a.Full_Right_argument.Text) + ' , ' + str(a.Full_Left_argument.Text) + ' )'

                      #pas de schéma on traite les ressources normalement"
                      else:
                        if j.Status=="Givable":
                              result = result + ' Givable '
                        if j.Status=="Not givable":
                              result = result + ' Not givable '
                        if j.Status=="Receivable":
                              result = result + ' Receivable '
                        if j.Status=="Not receivable":
                              result = result + ' Not receivable '
                        if j.Status=="Possessed":
                              result = result  + ' Possessed '
                        if j.Status==" Not possessed":
                              result = result  + ' Not Possessed '
                        if j.Status=="?":
                              result = result  + ' Unknown '
                        result = result + '(' + j.Kind
                        result = result + ', ' + j.Quantity + ') '

                        if j.Kind=="Anaphoric":
                                 for anaph in anaphors_detail:
                                     if anaph!=[]:
                                         for a in anaph:
                                             if a.Left_argument==j.ID:
                                                 result=result+ ' #' + 'Anaphora Link:(' + str(a.Full_Left_argument.Text) + ' , ' + str(a.Full_Right_argument.Text) + ' )'
                                             if a.Right_argument==j.ID:
                                                 result=result+ ' #' + 'Anaphora Link:(' + str(a.Full_Right_argument.Text) + ' , ' + str(a.Full_Left_argument.Text) + ' )'
         return result


    segs = dict()

    try:
        for seg in uiter.get_segments():
            result=''
            if not basename(seg[0].Textfile) in segs:
                segs[basename(seg[0].Textfile)] = []
                speaker_idturn, anaphors=get_speaker_idturn(basename(seg[0].Textfile))
                anaphors_detail=[]
                for a in anaphors:
                    if a!=[]:
                       for i in a:
                          anaphors_detail.append((i.ID,i.Left_argument,i.Right_argument))



            speaker=speaker_idturn[seg[0].Turn]
            result = result + str(seg[0]) + ' [' + 'Turn_ID: ' + str(seg[0].Turn) +  ' #' + '    EDU_Span: '+ str(seg[0].Text) + '#' +'   Speaker: '  + str(speaker) +  '#' +'  Surface_Act: ' + str(seg[0].Surface_act_type)


            for receiver in seg[0].Receivers:
               result = result + '#' +'   Addressee: ' + receiver


            #Traitement spécial pour les ressources multiples
            #Recup la liste des ressources dans several ressources
            several_ressource_text=[]
            result=get_ressource(seg,several_ressource_text,anaphors, result)

            result=result + ']' + '\n'

            segs[basename(seg[0].Textfile)].append(result)


    except TypeError:
        pass



    for (filename, segments) in segs.items() :
        f = open(base_directory + filename + "_"+Annotator+ ".seg", "w")
        segments_sorted=[]
        #sort results by ID Turn
        for seg in segments :

            segments_sorted.append((seg.split()[2],seg))

        '''print filename
        print segments_sorted
        x=raw_input("hkjhkj")'''
        sorted_key=sorted(segments_sorted, key=lambda Turn_ID: int(Turn_ID[0]))
        j=0
        for seg in sorted_key:
            if j>1:
                if int(seg[0])-int(sorted_key[j-1][0])>1:
                    f.write("*******END TURN************\n")
            f.write(seg[1] + "\n")
            j=j+1
        f.close()
