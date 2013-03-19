#!/bin/bash
set -ev

# ======================================================================
# junk files
# duplicates, autosav detritus, etc
# ======================================================================

git rm -rf data/pilot/pilot02/glozz_preannotation/pilot02-2011-10-12-13-38-43-+0100.aa || :
git rm -rf data/pilot/pilot02/glozz_preannotation/pilot02-2011-10-12-13-38-43-+0100.ac || :
git rm -rf data/pilot/pilot01/glozz_annotations/ResultUnit || :
git rm -rf ./data/pilot/pilot01/glozz_annotations/hjoseph/units/pilot01_11_joseph_u_0312.aa.autosav || :
git rm -rf ./data/pilot/pilot03/glozz_annotations/lpetersen/discourse/pilot03_8_petersen_d_28112012.aa.autosav || :
git rm -rf ./glozz_tool/pilot01-2011-10-10-15-28-56-+0100.aam || :
git rm -rf ./glozz_tool/pilot02-2011-10-12-13-38-43-+0100.aam || :
git rm -rf ./glozz_tool/pilot03-2011-10-19-16-30-51-+0100.aam || :
git rm -rf ./glozz_tool/pilot04-2011-10-19-15-52-57-+0100.aam || :
git rm -rf ./glozz_tool/pilot14-2011-10-25-09-54-06-+0100.aam || :
git rm -rf ./glozz_tool/pilot20-2011-10-31-16-16-29-+0000.aam || :
git rm -rf ./glozz_tool/pilot21-2011-10-31-15-58-38-+0000.aam || :

# ======================================================================
# truncations
# want uniform names in annotation files
# ======================================================================


git mv ./data/pilot/pilot01/glozz_annotations/hjoseph/discourse/pilot01_10_joseph_d_0212.aa ./data/pilot/pilot01/glozz_annotations/hjoseph/discourse/pilot01_10.aa
git mv ./data/pilot/pilot01/glozz_annotations/hjoseph/discourse/pilot01_11_joseph_d_0412.aa ./data/pilot/pilot01/glozz_annotations/hjoseph/discourse/pilot01_11.aa
git mv ./data/pilot/pilot01/glozz_annotations/hjoseph/discourse/pilot01_12_joseph_d_0612.aa ./data/pilot/pilot01/glozz_annotations/hjoseph/discourse/pilot01_12.aa
git mv ./data/pilot/pilot01/glozz_annotations/hjoseph/discourse/pilot01_1_joseph_d_2806.aa ./data/pilot/pilot01/glozz_annotations/hjoseph/discourse/pilot01_01.aa
git mv ./data/pilot/pilot01/glozz_annotations/hjoseph/discourse/pilot01_2_joseph_d_2906.aa ./data/pilot/pilot01/glozz_annotations/hjoseph/discourse/pilot01_02.aa
git mv ./data/pilot/pilot01/glozz_annotations/hjoseph/discourse/pilot01_3_joseph_d_281012.aa ./data/pilot/pilot01/glozz_annotations/hjoseph/discourse/pilot01_03.aa
git mv ./data/pilot/pilot01/glozz_annotations/hjoseph/discourse/pilot01_4_joseph_d_241012.aa ./data/pilot/pilot01/glozz_annotations/hjoseph/discourse/pilot01_04.aa
git mv ./data/pilot/pilot01/glozz_annotations/hjoseph/discourse/pilot01_5_joseph_d_12112012.aa ./data/pilot/pilot01/glozz_annotations/hjoseph/discourse/pilot01_05.aa
git mv ./data/pilot/pilot01/glozz_annotations/hjoseph/discourse/pilot01_6_joseph_d_191012.aa ./data/pilot/pilot01/glozz_annotations/hjoseph/discourse/pilot01_06.aa
git mv ./data/pilot/pilot01/glozz_annotations/hjoseph/discourse/pilot01_7_joseph_d_221012.aa ./data/pilot/pilot01/glozz_annotations/hjoseph/discourse/pilot01_07.aa
git mv ./data/pilot/pilot01/glozz_annotations/hjoseph/discourse/pilot01_8_joseph_d_2611.aa ./data/pilot/pilot01/glozz_annotations/hjoseph/discourse/pilot01_08.aa
git mv ./data/pilot/pilot01/glozz_annotations/hjoseph/discourse/pilot01_9_joseph_d_0212.aa ./data/pilot/pilot01/glozz_annotations/hjoseph/discourse/pilot01_09.aa

git mv ./data/pilot/pilot01/glozz_annotations/hjoseph/units/pilot01_10_joseph_u_0212.aa ./data/pilot/pilot01/glozz_annotations/hjoseph/units/pilot01_10.aa
git mv ./data/pilot/pilot01/glozz_annotations/hjoseph/units/pilot01_11_joseph_u_0312.aa ./data/pilot/pilot01/glozz_annotations/hjoseph/units/pilot01_11.aa
git mv ./data/pilot/pilot01/glozz_annotations/hjoseph/units/pilot01_12_joseph_u_0412.aa ./data/pilot/pilot01/glozz_annotations/hjoseph/units/pilot01_12.aa
git mv ./data/pilot/pilot01/glozz_annotations/hjoseph/units/pilot01_1_joseph_u_2806.aa ./data/pilot/pilot01/glozz_annotations/hjoseph/units/pilot01_01.aa
git mv ./data/pilot/pilot01/glozz_annotations/hjoseph/units/pilot01_2_joseph_u_0110.aa ./data/pilot/pilot01/glozz_annotations/hjoseph/units/pilot01_02.aa
git mv ./data/pilot/pilot01/glozz_annotations/hjoseph/units/pilot01_3_joseph_u_2510012.aa ./data/pilot/pilot01/glozz_annotations/hjoseph/units/pilot01_03.aa
git mv ./data/pilot/pilot01/glozz_annotations/hjoseph/units/pilot01_4_joseph_u_10122012.aa ./data/pilot/pilot01/glozz_annotations/hjoseph/units/pilot01_04.aa
git mv ./data/pilot/pilot01/glozz_annotations/hjoseph/units/pilot01_5_joseph_u_191012.aa ./data/pilot/pilot01/glozz_annotations/hjoseph/units/pilot01_05.aa
git mv ./data/pilot/pilot01/glozz_annotations/hjoseph/units/pilot01_6_joseph_u_221012.aa ./data/pilot/pilot01/glozz_annotations/hjoseph/units/pilot01_06.aa
git mv ./data/pilot/pilot01/glozz_annotations/hjoseph/units/pilot01_7_joseph_u_221012.aa ./data/pilot/pilot01/glozz_annotations/hjoseph/units/pilot01_07.aa
git mv ./data/pilot/pilot01/glozz_annotations/hjoseph/units/pilot01_8_joseph_u_2611.aa ./data/pilot/pilot01/glozz_annotations/hjoseph/units/pilot01_08.aa
git mv ./data/pilot/pilot01/glozz_annotations/hjoseph/units/pilot01_9_joseph_u_0212.aa ./data/pilot/pilot01/glozz_annotations/hjoseph/units/pilot01_09.aa

git mv ./data/pilot/pilot01/glozz_annotations/jhall/discourse/pilot01_1.ac ./data/pilot/pilot01/glozz_annotations/jhall/discourse/pilot01_01.ac
git mv ./data/pilot/pilot01/glozz_annotations/jhall/discourse/pilot01_1_hall_d__28062012.aa ./data/pilot/pilot01/glozz_annotations/jhall/discourse/pilot01_01.aa
git mv ./data/pilot/pilot01/glozz_annotations/jhall/discourse/pilot01_2.ac ./data/pilot/pilot01/glozz_annotations/jhall/discourse/pilot01_02.ac
git mv ./data/pilot/pilot01/glozz_annotations/jhall/discourse/pilot01_2_hall_d__29062012.aa ./data/pilot/pilot01/glozz_annotations/jhall/discourse/pilot01_02.aa
git mv ./data/pilot/pilot01/glozz_annotations/jhall/discourse/pilot01_3.ac ./data/pilot/pilot01/glozz_annotations/jhall/discourse/pilot01_03.ac
git mv ./data/pilot/pilot01/glozz_annotations/jhall/discourse/pilot01_3_hall_d__02072012.aa ./data/pilot/pilot01/glozz_annotations/jhall/discourse/pilot01_03.aa

git mv ./data/pilot/pilot01/glozz_annotations/jhall/units/pilot01_1.ac ./data/pilot/pilot01/glozz_annotations/jhall/units/pilot01_01.ac
git mv ./data/pilot/pilot01/glozz_annotations/jhall/units/pilot01_1_hall_u__28062012.aa ./data/pilot/pilot01/glozz_annotations/jhall/units/pilot01_01.aa
git mv ./data/pilot/pilot01/glozz_annotations/jhall/units/pilot01_2.ac ./data/pilot/pilot01/glozz_annotations/jhall/units/pilot01_02.ac
git mv ./data/pilot/pilot01/glozz_annotations/jhall/units/pilot01_2_hall_u__29062012.aa ./data/pilot/pilot01/glozz_annotations/jhall/units/pilot01_02.aa
git mv ./data/pilot/pilot01/glozz_annotations/jhall/units/pilot01_3.ac ./data/pilot/pilot01/glozz_annotations/jhall/units/pilot01_03.ac
git mv ./data/pilot/pilot01/glozz_annotations/jhall/units/pilot01_3_hall_u__02072012.aa ./data/pilot/pilot01/glozz_annotations/jhall/units/pilot01_03.aa

git mv ./data/pilot/pilot01/glozz_annotations/lpetersen/discourse/pilot01_10_petersen_d_23112012.aa ./data/pilot/pilot01/glozz_annotations/lpetersen/discourse/pilot01_10.aa
git mv ./data/pilot/pilot01/glozz_annotations/lpetersen/discourse/pilot01_11_petersen_d_23112012.aa ./data/pilot/pilot01/glozz_annotations/lpetersen/discourse/pilot01_11.aa
git mv ./data/pilot/pilot01/glozz_annotations/lpetersen/discourse/pilot01_12_petersen_d_23112012.aa ./data/pilot/pilot01/glozz_annotations/lpetersen/discourse/pilot01_12.aa
git mv ./data/pilot/pilot01/glozz_annotations/lpetersen/discourse/pilot01_2_petersen_d_18102012.aa ./data/pilot/pilot01/glozz_annotations/lpetersen/discourse/pilot01_02.aa
git mv ./data/pilot/pilot01/glozz_annotations/lpetersen/discourse/pilot01_3_petersen_d_18102012.aa ./data/pilot/pilot01/glozz_annotations/lpetersen/discourse/pilot01_03.aa
git mv ./data/pilot/pilot01/glozz_annotations/lpetersen/discourse/pilot01_4_petersen_d_18102012.aa ./data/pilot/pilot01/glozz_annotations/lpetersen/discourse/pilot01_04.aa
git mv ./data/pilot/pilot01/glozz_annotations/lpetersen/discourse/pilot01_5_petersen_d_19102012.aa ./data/pilot/pilot01/glozz_annotations/lpetersen/discourse/pilot01_05.aa
git mv ./data/pilot/pilot01/glozz_annotations/lpetersen/discourse/pilot01_6_petersen_d_19102012.aa ./data/pilot/pilot01/glozz_annotations/lpetersen/discourse/pilot01_06.aa
git mv ./data/pilot/pilot01/glozz_annotations/lpetersen/discourse/pilot01_7_petersen_d_19102012.aa ./data/pilot/pilot01/glozz_annotations/lpetersen/discourse/pilot01_07.aa
git mv ./data/pilot/pilot01/glozz_annotations/lpetersen/discourse/pilot01_8_petersen_d_23112012.aa ./data/pilot/pilot01/glozz_annotations/lpetersen/discourse/pilot01_08.aa
git mv ./data/pilot/pilot01/glozz_annotations/lpetersen/discourse/pilot01_9_petersen_d_23112012.aa ./data/pilot/pilot01/glozz_annotations/lpetersen/discourse/pilot01_09.aa

git mv ./data/pilot/pilot01/glozz_annotations/lpetersen/units/pilot01_10_petersen_u_22112012.aa ./data/pilot/pilot01/glozz_annotations/lpetersen/units/pilot01_10.aa
git mv ./data/pilot/pilot01/glozz_annotations/lpetersen/units/pilot01_11_petersen_u_22112012.aa ./data/pilot/pilot01/glozz_annotations/lpetersen/units/pilot01_11.aa
git mv ./data/pilot/pilot01/glozz_annotations/lpetersen/units/pilot01_12_petersen_u_22112012.aa ./data/pilot/pilot01/glozz_annotations/lpetersen/units/pilot01_12.aa
git mv ./data/pilot/pilot01/glozz_annotations/lpetersen/units/pilot01_1_petersen_u_03102012.aa ./data/pilot/pilot01/glozz_annotations/lpetersen/units/pilot01_01.aa
git mv ./data/pilot/pilot01/glozz_annotations/lpetersen/units/pilot01_2_petersen_u_17102012.aa ./data/pilot/pilot01/glozz_annotations/lpetersen/units/pilot01_02.aa
git mv ./data/pilot/pilot01/glozz_annotations/lpetersen/units/pilot01_3_petersen_u_17102012.aa ./data/pilot/pilot01/glozz_annotations/lpetersen/units/pilot01_03.aa
git mv ./data/pilot/pilot01/glozz_annotations/lpetersen/units/pilot01_4_petersen_u_17102012.aa ./data/pilot/pilot01/glozz_annotations/lpetersen/units/pilot01_04.aa
git mv ./data/pilot/pilot01/glozz_annotations/lpetersen/units/pilot01_5_petersen_u_19102012.aa ./data/pilot/pilot01/glozz_annotations/lpetersen/units/pilot01_05.aa
git mv ./data/pilot/pilot01/glozz_annotations/lpetersen/units/pilot01_6_petersen_u_19102012.aa ./data/pilot/pilot01/glozz_annotations/lpetersen/units/pilot01_06.aa
git mv ./data/pilot/pilot01/glozz_annotations/lpetersen/units/pilot01_7_petersen_u_18102012.aa ./data/pilot/pilot01/glozz_annotations/lpetersen/units/pilot01_07.aa
git mv ./data/pilot/pilot01/glozz_annotations/lpetersen/units/pilot01_8_petersen_u_21112012.aa ./data/pilot/pilot01/glozz_annotations/lpetersen/units/pilot01_08.aa
git mv ./data/pilot/pilot01/glozz_annotations/lpetersen/units/pilot01_9_petersen_u_22112012.aa ./data/pilot/pilot01/glozz_annotations/lpetersen/units/pilot01_09.aa

git mv ./data/pilot/pilot01/glozz_annotations/mhunt/discourse/pilot01_1.ac ./data/pilot/pilot01/glozz_annotations/mhunt/discourse/pilot01_01.ac
git mv ./data/pilot/pilot01/glozz_annotations/mhunt/discourse/pilot01_2.ac ./data/pilot/pilot01/glozz_annotations/mhunt/discourse/pilot01_02.ac
git mv ./data/pilot/pilot01/glozz_annotations/mhunt/discourse/pilot01_2_martha_d_23102012.aa ./data/pilot/pilot01/glozz_annotations/mhunt/discourse/pilot01_02.aa
git mv ./data/pilot/pilot01/glozz_annotations/mhunt/discourse/pilot01_3.ac ./data/pilot/pilot01/glozz_annotations/mhunt/discourse/pilot01_03.ac
git mv ./data/pilot/pilot01/glozz_annotations/mhunt/discourse/pilot01_4.ac ./data/pilot/pilot01/glozz_annotations/mhunt/discourse/pilot01_04.ac
git mv ./data/pilot/pilot01/glozz_annotations/mhunt/discourse/pilot01_5.ac ./data/pilot/pilot01/glozz_annotations/mhunt/discourse/pilot01_05.ac
git mv ./data/pilot/pilot01/glozz_annotations/mhunt/discourse/pilot01_5_martha_d_22102012.aa ./data/pilot/pilot01/glozz_annotations/mhunt/discourse/pilot01_05.aa
git mv ./data/pilot/pilot01/glozz_annotations/mhunt/discourse/pilot01_6.ac ./data/pilot/pilot01/glozz_annotations/mhunt/discourse/pilot01_06.ac
git mv ./data/pilot/pilot01/glozz_annotations/mhunt/discourse/pilot01_6_martha_d_22102012.aa ./data/pilot/pilot01/glozz_annotations/mhunt/discourse/pilot01_06.aa
git mv ./data/pilot/pilot01/glozz_annotations/mhunt/discourse/pilot01_7.ac ./data/pilot/pilot01/glozz_annotations/mhunt/discourse/pilot01_07.ac
git mv ./data/pilot/pilot01/glozz_annotations/mhunt/discourse/pilot01_7_martha_d_22102012.aa ./data/pilot/pilot01/glozz_annotations/mhunt/discourse/pilot01_07.aa
git mv ./data/pilot/pilot01/glozz_annotations/mhunt/discourse/pilot03_3_martha_d_20121008.aa ./data/pilot/pilot01/glozz_annotations/mhunt/discourse/pilot03_03.aa
git mv ./data/pilot/pilot01/glozz_annotations/mhunt/discourse/pilot03_4_martha_d_20121008.aa ./data/pilot/pilot01/glozz_annotations/mhunt/discourse/pilot03_04.aa

git mv ./data/pilot/pilot01/glozz_annotations/mhunt/units/pilot01_1.ac ./data/pilot/pilot01/glozz_annotations/mhunt/units/pilot01_01.ac
git mv ./data/pilot/pilot01/glozz_annotations/mhunt/units/pilot01_1_martha_u_20121008.aa ./data/pilot/pilot01/glozz_annotations/mhunt/units/pilot01_01.aa
git mv ./data/pilot/pilot01/glozz_annotations/mhunt/units/pilot01_2.ac ./data/pilot/pilot01/glozz_annotations/mhunt/units/pilot01_02.ac
git mv ./data/pilot/pilot01/glozz_annotations/mhunt/units/pilot01_2_martha_u_20121008.aa ./data/pilot/pilot01/glozz_annotations/mhunt/units/pilot01_02.aa
git mv ./data/pilot/pilot01/glozz_annotations/mhunt/units/pilot01_3.ac ./data/pilot/pilot01/glozz_annotations/mhunt/units/pilot01_03.ac
git mv ./data/pilot/pilot01/glozz_annotations/mhunt/units/pilot01_3_martha_u_20121008.aa ./data/pilot/pilot01/glozz_annotations/mhunt/units/pilot01_03.aa
git mv ./data/pilot/pilot01/glozz_annotations/mhunt/units/pilot01_4.ac ./data/pilot/pilot01/glozz_annotations/mhunt/units/pilot01_04.ac
git mv ./data/pilot/pilot01/glozz_annotations/mhunt/units/pilot01_4_martha_u_20121008.aa ./data/pilot/pilot01/glozz_annotations/mhunt/units/pilot01_04.aa
git mv ./data/pilot/pilot01/glozz_annotations/mhunt/units/pilot01_5.ac ./data/pilot/pilot01/glozz_annotations/mhunt/units/pilot01_05.ac
git mv ./data/pilot/pilot01/glozz_annotations/mhunt/units/pilot01_5_martha_u_22102012.aa ./data/pilot/pilot01/glozz_annotations/mhunt/units/pilot01_05.aa

git mv ./data/pilot/pilot01/glozz_preannotation/pilot01_1.ac ./data/pilot/pilot01/glozz_preannotation/pilot01_01.ac
#git mv ./data/pilot/pilot01/glozz_preannotation/pilot01_10.aa ./data/pilot/pilot01/glozz_preannotation/pilot01_10.aa
#git mv ./data/pilot/pilot01/glozz_preannotation/pilot01_10.ac ./data/pilot/pilot01/glozz_preannotation/pilot01_10.ac
#git mv ./data/pilot/pilot01/glozz_preannotation/pilot01_11.aa ./data/pilot/pilot01/glozz_preannotation/pilot01_11.aa
#git mv ./data/pilot/pilot01/glozz_preannotation/pilot01_11.ac ./data/pilot/pilot01/glozz_preannotation/pilot01_11.ac
#git mv ./data/pilot/pilot01/glozz_preannotation/pilot01_12.aa ./data/pilot/pilot01/glozz_preannotation/pilot01_12.aa
#git mv ./data/pilot/pilot01/glozz_preannotation/pilot01_12.ac ./data/pilot/pilot01/glozz_preannotation/pilot01_12.ac
git mv ./data/pilot/pilot01/glozz_preannotation/pilot01_2.ac ./data/pilot/pilot01/glozz_preannotation/pilot01_02.ac
git mv ./data/pilot/pilot01/glozz_preannotation/pilot01_3.ac ./data/pilot/pilot01/glozz_preannotation/pilot01_03.ac
git mv ./data/pilot/pilot01/glozz_preannotation/pilot01_4.ac ./data/pilot/pilot01/glozz_preannotation/pilot01_04.ac
git mv ./data/pilot/pilot01/glozz_preannotation/pilot01_5.ac ./data/pilot/pilot01/glozz_preannotation/pilot01_05.ac
git mv ./data/pilot/pilot01/glozz_preannotation/pilot01_6.ac ./data/pilot/pilot01/glozz_preannotation/pilot01_06.ac
git mv ./data/pilot/pilot01/glozz_preannotation/pilot01_7.ac ./data/pilot/pilot01/glozz_preannotation/pilot01_07.ac
git mv ./data/pilot/pilot01/glozz_preannotation/pilot01_8.aa ./data/pilot/pilot01/glozz_preannotation/pilot01_08.aa
git mv ./data/pilot/pilot01/glozz_preannotation/pilot01_8.ac ./data/pilot/pilot01/glozz_preannotation/pilot01_08.ac
git mv ./data/pilot/pilot01/glozz_preannotation/pilot01_9.aa ./data/pilot/pilot01/glozz_preannotation/pilot01_09.aa
git mv ./data/pilot/pilot01/glozz_preannotation/pilot01_9.ac ./data/pilot/pilot01/glozz_preannotation/pilot01_09.ac

git mv ./data/pilot/pilot01/Gold/Unit/pilot01_10_petersen_u_22112012.aa ./data/pilot/pilot01/Gold/Unit/pilot01_10.aa
git mv ./data/pilot/pilot01/Gold/Unit/pilot01_11_petersen_u_22112012.aa ./data/pilot/pilot01/Gold/Unit/pilot01_11.aa
git mv ./data/pilot/pilot01/Gold/Unit/pilot01_12_petersen_u_22112012.aa ./data/pilot/pilot01/Gold/Unit/pilot01_12.aa
git mv ./data/pilot/pilot01/Gold/Unit/pilot01_1_petersen_u_03102012.aa ./data/pilot/pilot01/Gold/Unit/pilot01_01.aa
git mv ./data/pilot/pilot01/Gold/Unit/pilot01_2_petersen_u_17102012.aa ./data/pilot/pilot01/Gold/Unit/pilot01_02.aa
git mv ./data/pilot/pilot01/Gold/Unit/pilot01_3_petersen_u_17102012.aa ./data/pilot/pilot01/Gold/Unit/pilot01_03.aa
git mv ./data/pilot/pilot01/Gold/Unit/pilot01_4_petersen_u_17102012.aa ./data/pilot/pilot01/Gold/Unit/pilot01_04.aa
git mv ./data/pilot/pilot01/Gold/Unit/pilot01_5_petersen_u_19102012.aa ./data/pilot/pilot01/Gold/Unit/pilot01_05.aa
git mv ./data/pilot/pilot01/Gold/Unit/pilot01_6_petersen_u_19102012.aa ./data/pilot/pilot01/Gold/Unit/pilot01_06.aa
git mv ./data/pilot/pilot01/Gold/Unit/pilot01_7_joseph_u_221012.aa ./data/pilot/pilot01/Gold/Unit/pilot01_07.aa
git mv ./data/pilot/pilot01/Gold/Unit/pilot01_8_petersen_u_21112012.aa ./data/pilot/pilot01/Gold/Unit/pilot01_08.aa
git mv ./data/pilot/pilot01/Gold/Unit/pilot01_9_petersen_u_22112012.aa ./data/pilot/pilot01/Gold/Unit/pilot01_09.aa

git mv ./data/pilot/pilot01/Gold/Unit_pred_arg/pilot01_1.ac_petersen.seg ./data/pilot/pilot01/Gold/Unit_pred_arg/pilot01_01.ac.seg
git mv ./data/pilot/pilot01/Gold/Unit_pred_arg/pilot01_10.ac_petersen.seg ./data/pilot/pilot01/Gold/Unit_pred_arg/pilot01_10.ac.seg
git mv ./data/pilot/pilot01/Gold/Unit_pred_arg/pilot01_11.ac_petersen.seg ./data/pilot/pilot01/Gold/Unit_pred_arg/pilot01_11.ac.seg
git mv ./data/pilot/pilot01/Gold/Unit_pred_arg/pilot01_12.ac_petersen.seg ./data/pilot/pilot01/Gold/Unit_pred_arg/pilot01_12.ac.seg
git mv ./data/pilot/pilot01/Gold/Unit_pred_arg/pilot01_2.ac_petersen.seg ./data/pilot/pilot01/Gold/Unit_pred_arg/pilot01_02.ac.seg
git mv ./data/pilot/pilot01/Gold/Unit_pred_arg/pilot01_3.ac_petersen.seg ./data/pilot/pilot01/Gold/Unit_pred_arg/pilot01_03.ac.seg
git mv ./data/pilot/pilot01/Gold/Unit_pred_arg/pilot01_4.ac_petersen.seg ./data/pilot/pilot01/Gold/Unit_pred_arg/pilot01_04.ac.seg
git mv ./data/pilot/pilot01/Gold/Unit_pred_arg/pilot01_5.ac_petersen.seg ./data/pilot/pilot01/Gold/Unit_pred_arg/pilot01_05.ac.seg
git mv ./data/pilot/pilot01/Gold/Unit_pred_arg/pilot01_6.ac_petersen.seg ./data/pilot/pilot01/Gold/Unit_pred_arg/pilot01_06.ac.seg
git mv ./data/pilot/pilot01/Gold/Unit_pred_arg/pilot01_7.ac_petersen.seg ./data/pilot/pilot01/Gold/Unit_pred_arg/pilot01_07.ac.seg
git mv ./data/pilot/pilot01/Gold/Unit_pred_arg/pilot01_8.ac_petersen.seg ./data/pilot/pilot01/Gold/Unit_pred_arg/pilot01_08.ac.seg
git mv ./data/pilot/pilot01/Gold/Unit_pred_arg/pilot01_9.ac_petersen.seg ./data/pilot/pilot01/Gold/Unit_pred_arg/pilot01_09.ac.seg

git mv ./data/pilot/pilot01/pred_arg_annotations/joseph/discourse/pilot01_1.ac_joseph.rel ./data/pilot/pilot01/pred_arg_annotations/joseph/discourse/pilot01_01.ac.rel
git mv ./data/pilot/pilot01/pred_arg_annotations/joseph/discourse/pilot01_10.ac_joseph.rel ./data/pilot/pilot01/pred_arg_annotations/joseph/discourse/pilot01_10.ac.rel
git mv ./data/pilot/pilot01/pred_arg_annotations/joseph/discourse/pilot01_11.ac_joseph.rel ./data/pilot/pilot01/pred_arg_annotations/joseph/discourse/pilot01_11.ac.rel
git mv ./data/pilot/pilot01/pred_arg_annotations/joseph/discourse/pilot01_12.ac_joseph.rel ./data/pilot/pilot01/pred_arg_annotations/joseph/discourse/pilot01_12.ac.rel
git mv ./data/pilot/pilot01/pred_arg_annotations/joseph/discourse/pilot01_2.ac_joseph.rel ./data/pilot/pilot01/pred_arg_annotations/joseph/discourse/pilot01_02.ac.rel
git mv ./data/pilot/pilot01/pred_arg_annotations/joseph/discourse/pilot01_3.ac_joseph.rel ./data/pilot/pilot01/pred_arg_annotations/joseph/discourse/pilot01_03.ac.rel
git mv ./data/pilot/pilot01/pred_arg_annotations/joseph/discourse/pilot01_4.ac_joseph.rel ./data/pilot/pilot01/pred_arg_annotations/joseph/discourse/pilot01_04.ac.rel
git mv ./data/pilot/pilot01/pred_arg_annotations/joseph/discourse/pilot01_5.ac_joseph.rel ./data/pilot/pilot01/pred_arg_annotations/joseph/discourse/pilot01_05.ac.rel
git mv ./data/pilot/pilot01/pred_arg_annotations/joseph/discourse/pilot01_6.ac_joseph.rel ./data/pilot/pilot01/pred_arg_annotations/joseph/discourse/pilot01_06.ac.rel
git mv ./data/pilot/pilot01/pred_arg_annotations/joseph/discourse/pilot01_7.ac_joseph.rel ./data/pilot/pilot01/pred_arg_annotations/joseph/discourse/pilot01_07.ac.rel
git mv ./data/pilot/pilot01/pred_arg_annotations/joseph/discourse/pilot01_8.ac_joseph.rel ./data/pilot/pilot01/pred_arg_annotations/joseph/discourse/pilot01_08.ac.rel
git mv ./data/pilot/pilot01/pred_arg_annotations/joseph/discourse/pilot01_9.ac_joseph.rel ./data/pilot/pilot01/pred_arg_annotations/joseph/discourse/pilot01_09.ac.rel

git mv ./data/pilot/pilot01/pred_arg_annotations/joseph/unit/pilot01_1.ac_joseph.seg ./data/pilot/pilot01/pred_arg_annotations/joseph/unit/pilot01_01.ac.seg
git mv ./data/pilot/pilot01/pred_arg_annotations/joseph/unit/pilot01_10.ac_joseph.seg ./data/pilot/pilot01/pred_arg_annotations/joseph/unit/pilot01_10.ac.seg
git mv ./data/pilot/pilot01/pred_arg_annotations/joseph/unit/pilot01_11.ac_joseph.seg ./data/pilot/pilot01/pred_arg_annotations/joseph/unit/pilot01_11.ac.seg
git mv ./data/pilot/pilot01/pred_arg_annotations/joseph/unit/pilot01_12.ac_joseph.seg ./data/pilot/pilot01/pred_arg_annotations/joseph/unit/pilot01_12.ac.seg
git mv ./data/pilot/pilot01/pred_arg_annotations/joseph/unit/pilot01_2.ac_joseph.seg ./data/pilot/pilot01/pred_arg_annotations/joseph/unit/pilot01_02.ac.seg
git mv ./data/pilot/pilot01/pred_arg_annotations/joseph/unit/pilot01_4.ac_joseph.seg ./data/pilot/pilot01/pred_arg_annotations/joseph/unit/pilot01_04.ac.seg
git mv ./data/pilot/pilot01/pred_arg_annotations/joseph/unit/pilot01_5.ac_joseph.seg ./data/pilot/pilot01/pred_arg_annotations/joseph/unit/pilot01_05.ac.seg
git mv ./data/pilot/pilot01/pred_arg_annotations/joseph/unit/pilot01_6.ac_joseph.seg ./data/pilot/pilot01/pred_arg_annotations/joseph/unit/pilot01_06.ac.seg
git mv ./data/pilot/pilot01/pred_arg_annotations/joseph/unit/pilot01_7.ac_joseph.seg ./data/pilot/pilot01/pred_arg_annotations/joseph/unit/pilot01_07.ac.seg
git mv ./data/pilot/pilot01/pred_arg_annotations/joseph/unit/pilot01_8.ac_joseph.seg ./data/pilot/pilot01/pred_arg_annotations/joseph/unit/pilot01_08.ac.seg
git mv ./data/pilot/pilot01/pred_arg_annotations/joseph/unit/pilot01_9.ac_joseph.seg ./data/pilot/pilot01/pred_arg_annotations/joseph/unit/pilot01_09.ac.seg

git mv ./data/pilot/pilot01/pred_arg_annotations/lpetersen/discourse/pilot01_10.ac_petersen.rel ./data/pilot/pilot01/pred_arg_annotations/lpetersen/discourse/pilot01_10.ac.rel
git mv ./data/pilot/pilot01/pred_arg_annotations/lpetersen/discourse/pilot01_11.ac_petersen.rel ./data/pilot/pilot01/pred_arg_annotations/lpetersen/discourse/pilot01_11.ac.rel
git mv ./data/pilot/pilot01/pred_arg_annotations/lpetersen/discourse/pilot01_12.ac_petersen.rel ./data/pilot/pilot01/pred_arg_annotations/lpetersen/discourse/pilot01_12.ac.rel
git mv ./data/pilot/pilot01/pred_arg_annotations/lpetersen/discourse/pilot01_2.ac_petersen.rel ./data/pilot/pilot01/pred_arg_annotations/lpetersen/discourse/pilot01_02.ac.rel
git mv ./data/pilot/pilot01/pred_arg_annotations/lpetersen/discourse/pilot01_3.ac_petersen.rel ./data/pilot/pilot01/pred_arg_annotations/lpetersen/discourse/pilot01_03.ac.rel
git mv ./data/pilot/pilot01/pred_arg_annotations/lpetersen/discourse/pilot01_4.ac_petersen.rel ./data/pilot/pilot01/pred_arg_annotations/lpetersen/discourse/pilot01_04.ac.rel
git mv ./data/pilot/pilot01/pred_arg_annotations/lpetersen/discourse/pilot01_5.ac_petersen.rel ./data/pilot/pilot01/pred_arg_annotations/lpetersen/discourse/pilot01_05.ac.rel
git mv ./data/pilot/pilot01/pred_arg_annotations/lpetersen/discourse/pilot01_6.ac_petersen.rel ./data/pilot/pilot01/pred_arg_annotations/lpetersen/discourse/pilot01_06.ac.rel
git mv ./data/pilot/pilot01/pred_arg_annotations/lpetersen/discourse/pilot01_7.ac_petersen.rel ./data/pilot/pilot01/pred_arg_annotations/lpetersen/discourse/pilot01_07.ac.rel
git mv ./data/pilot/pilot01/pred_arg_annotations/lpetersen/discourse/pilot01_8.ac_petersen.rel ./data/pilot/pilot01/pred_arg_annotations/lpetersen/discourse/pilot01_08.ac.rel
git mv ./data/pilot/pilot01/pred_arg_annotations/lpetersen/discourse/pilot01_9.ac_petersen.rel ./data/pilot/pilot01/pred_arg_annotations/lpetersen/discourse/pilot01_09.ac.rel

git mv ./data/pilot/pilot01/pred_arg_annotations/lpetersen/unit/pilot01_1.ac_petersen.seg ./data/pilot/pilot01/pred_arg_annotations/lpetersen/unit/pilot01_01.ac.seg
git mv ./data/pilot/pilot01/pred_arg_annotations/lpetersen/unit/pilot01_10.ac_petersen.seg ./data/pilot/pilot01/pred_arg_annotations/lpetersen/unit/pilot01_10.ac.seg
git mv ./data/pilot/pilot01/pred_arg_annotations/lpetersen/unit/pilot01_11.ac_petersen.seg ./data/pilot/pilot01/pred_arg_annotations/lpetersen/unit/pilot01_11.ac.seg
git mv ./data/pilot/pilot01/pred_arg_annotations/lpetersen/unit/pilot01_12.ac_petersen.seg ./data/pilot/pilot01/pred_arg_annotations/lpetersen/unit/pilot01_12.ac.seg
git mv ./data/pilot/pilot01/pred_arg_annotations/lpetersen/unit/pilot01_2.ac_petersen.seg ./data/pilot/pilot01/pred_arg_annotations/lpetersen/unit/pilot01_02.ac.seg
git mv ./data/pilot/pilot01/pred_arg_annotations/lpetersen/unit/pilot01_3.ac_petersen.seg ./data/pilot/pilot01/pred_arg_annotations/lpetersen/unit/pilot01_03.ac.seg
git mv ./data/pilot/pilot01/pred_arg_annotations/lpetersen/unit/pilot01_4.ac_petersen.seg ./data/pilot/pilot01/pred_arg_annotations/lpetersen/unit/pilot01_04.ac.seg
git mv ./data/pilot/pilot01/pred_arg_annotations/lpetersen/unit/pilot01_5.ac_petersen.seg ./data/pilot/pilot01/pred_arg_annotations/lpetersen/unit/pilot01_05.ac.seg
git mv ./data/pilot/pilot01/pred_arg_annotations/lpetersen/unit/pilot01_6.ac_petersen.seg ./data/pilot/pilot01/pred_arg_annotations/lpetersen/unit/pilot01_06.ac.seg
git mv ./data/pilot/pilot01/pred_arg_annotations/lpetersen/unit/pilot01_7.ac_petersen.seg ./data/pilot/pilot01/pred_arg_annotations/lpetersen/unit/pilot01_07.ac.seg
git mv ./data/pilot/pilot01/pred_arg_annotations/lpetersen/unit/pilot01_8.ac_petersen.seg ./data/pilot/pilot01/pred_arg_annotations/lpetersen/unit/pilot01_08.ac.seg
git mv ./data/pilot/pilot01/pred_arg_annotations/lpetersen/unit/pilot01_9.ac_petersen.seg ./data/pilot/pilot01/pred_arg_annotations/lpetersen/unit/pilot01_09.ac.seg

git mv ./data/pilot/pilot02/glozz_annotations/hjoseph/discourse/pilot02_1_joseph_d_3101.aa ./data/pilot/pilot02/glozz_annotations/hjoseph/discourse/pilot02_01.aa
git mv ./data/pilot/pilot02/glozz_annotations/hjoseph/discourse/pilot02_2_joseph_d_0402.aa ./data/pilot/pilot02/glozz_annotations/hjoseph/discourse/pilot02_02.aa
git mv ./data/pilot/pilot02/glozz_annotations/hjoseph/discourse/pilot02_3_joseph_d_0702.aa ./data/pilot/pilot02/glozz_annotations/hjoseph/discourse/pilot02_03.aa
git mv ./data/pilot/pilot02/glozz_annotations/hjoseph/discourse/pilot02_4_joseph_d_0702.aa ./data/pilot/pilot02/glozz_annotations/hjoseph/discourse/pilot02_04.aa
git mv ./data/pilot/pilot02/glozz_annotations/hjoseph/discourse/pilot02_5_joseph_d_0702.aa ./data/pilot/pilot02/glozz_annotations/hjoseph/discourse/pilot02_05.aa
git mv ./data/pilot/pilot02/glozz_annotations/hjoseph/discourse/pilot02_6_joseph_d_0702.aa ./data/pilot/pilot02/glozz_annotations/hjoseph/discourse/pilot02_06.aa

git mv ./data/pilot/pilot02/glozz_annotations/hjoseph/units/pilot02_1_joseph_u_3101.aa ./data/pilot/pilot02/glozz_annotations/hjoseph/units/pilot02_01.aa
git mv ./data/pilot/pilot02/glozz_annotations/hjoseph/units/pilot02_2_joseph_u_3101.aa ./data/pilot/pilot02/glozz_annotations/hjoseph/units/pilot02_02.aa
git mv ./data/pilot/pilot02/glozz_annotations/hjoseph/units/pilot02_3_joseph_u_0402.aa ./data/pilot/pilot02/glozz_annotations/hjoseph/units/pilot02_03.aa
git mv ./data/pilot/pilot02/glozz_annotations/hjoseph/units/pilot02_4_joseph_u_0702.aa ./data/pilot/pilot02/glozz_annotations/hjoseph/units/pilot02_04.aa
git mv ./data/pilot/pilot02/glozz_annotations/hjoseph/units/pilot02_5_joseph_u_0702.aa ./data/pilot/pilot02/glozz_annotations/hjoseph/units/pilot02_05.aa
git mv ./data/pilot/pilot02/glozz_annotations/hjoseph/units/pilot02_6_joseph_u_0702.aa ./data/pilot/pilot02/glozz_annotations/hjoseph/units/pilot02_06.aa

git mv ./data/pilot/pilot02/glozz_annotations/lpetersen/discourse/pilot02_10_petersen_d_25012013.aa ./data/pilot/pilot02/glozz_annotations/lpetersen/discourse/pilot02_10.aa
git mv ./data/pilot/pilot02/glozz_annotations/lpetersen/discourse/pilot02_11_petersen_d_25012013.aa ./data/pilot/pilot02/glozz_annotations/lpetersen/discourse/pilot02_11.aa
git mv ./data/pilot/pilot02/glozz_annotations/lpetersen/discourse/pilot02_12_petersen_d_25012013.aa ./data/pilot/pilot02/glozz_annotations/lpetersen/discourse/pilot02_12.aa
git mv ./data/pilot/pilot02/glozz_annotations/lpetersen/discourse/pilot02_7_petersen_d_25012013.aa ./data/pilot/pilot02/glozz_annotations/lpetersen/discourse/pilot02_07.aa
git mv ./data/pilot/pilot02/glozz_annotations/lpetersen/discourse/pilot02_8_petersen_d_25012013.aa ./data/pilot/pilot02/glozz_annotations/lpetersen/discourse/pilot02_08.aa
git mv ./data/pilot/pilot02/glozz_annotations/lpetersen/discourse/pilot02_9_petersen_d_25012013.aa ./data/pilot/pilot02/glozz_annotations/lpetersen/discourse/pilot02_09.aa

git mv ./data/pilot/pilot02/glozz_annotations/lpetersen/units/pilot02_10_petersen_u_23012013.aa ./data/pilot/pilot02/glozz_annotations/lpetersen/units/pilot02_10.aa
git mv ./data/pilot/pilot02/glozz_annotations/lpetersen/units/pilot02_11_petersen_u_24012013.aa ./data/pilot/pilot02/glozz_annotations/lpetersen/units/pilot02_11.aa
git mv ./data/pilot/pilot02/glozz_annotations/lpetersen/units/pilot02_12_petersen_u_24012013.aa ./data/pilot/pilot02/glozz_annotations/lpetersen/units/pilot02_12.aa
git mv ./data/pilot/pilot02/glozz_annotations/lpetersen/units/pilot02_7_petersen_u_22012012.aa ./data/pilot/pilot02/glozz_annotations/lpetersen/units/pilot02_07.aa
git mv ./data/pilot/pilot02/glozz_annotations/lpetersen/units/pilot02_8_petersen_u_22012012.aa ./data/pilot/pilot02/glozz_annotations/lpetersen/units/pilot02_08.aa
git mv ./data/pilot/pilot02/glozz_annotations/lpetersen/units/pilot02_9_petersen_u_23012013.aa ./data/pilot/pilot02/glozz_annotations/lpetersen/units/pilot02_09.aa

#git mv ./data/pilot/pilot02/glozz_preannotation/pilot02-2011-10-12-13-38-43-+0100.aa ./data/pilot/pilot02/glozz_preannotation/pilot02-2011-10-12-13-38-43-+0100.aa
#git mv ./data/pilot/pilot02/glozz_preannotation/pilot02-2011-10-12-13-38-43-+0100.ac ./data/pilot/pilot02/glozz_preannotation/pilot02-2011-10-12-13-38-43-+0100.ac
git mv ./data/pilot/pilot02/glozz_preannotation/pilot02_1.aa ./data/pilot/pilot02/glozz_preannotation/pilot02_01.aa
git mv ./data/pilot/pilot02/glozz_preannotation/pilot02_1.ac ./data/pilot/pilot02/glozz_preannotation/pilot02_01.ac
#git mv ./data/pilot/pilot02/glozz_preannotation/pilot02_10.aa ./data/pilot/pilot02/glozz_preannotation/pilot02_10.aa
#git mv ./data/pilot/pilot02/glozz_preannotation/pilot02_10.ac ./data/pilot/pilot02/glozz_preannotation/pilot02_10.ac
#git mv ./data/pilot/pilot02/glozz_preannotation/pilot02_11.aa ./data/pilot/pilot02/glozz_preannotation/pilot02_11.aa
#git mv ./data/pilot/pilot02/glozz_preannotation/pilot02_11.ac ./data/pilot/pilot02/glozz_preannotation/pilot02_11.ac
#git mv ./data/pilot/pilot02/glozz_preannotation/pilot02_12.aa ./data/pilot/pilot02/glozz_preannotation/pilot02_12.aa
#git mv ./data/pilot/pilot02/glozz_preannotation/pilot02_12.ac ./data/pilot/pilot02/glozz_preannotation/pilot02_12.ac
git mv ./data/pilot/pilot02/glozz_preannotation/pilot02_2.aa ./data/pilot/pilot02/glozz_preannotation/pilot02_02.aa
git mv ./data/pilot/pilot02/glozz_preannotation/pilot02_2.ac ./data/pilot/pilot02/glozz_preannotation/pilot02_02.ac
git mv ./data/pilot/pilot02/glozz_preannotation/pilot02_3.aa ./data/pilot/pilot02/glozz_preannotation/pilot02_03.aa
git mv ./data/pilot/pilot02/glozz_preannotation/pilot02_3.ac ./data/pilot/pilot02/glozz_preannotation/pilot02_03.ac
git mv ./data/pilot/pilot02/glozz_preannotation/pilot02_4.aa ./data/pilot/pilot02/glozz_preannotation/pilot02_04.aa
git mv ./data/pilot/pilot02/glozz_preannotation/pilot02_4.ac ./data/pilot/pilot02/glozz_preannotation/pilot02_04.ac
git mv ./data/pilot/pilot02/glozz_preannotation/pilot02_5.aa ./data/pilot/pilot02/glozz_preannotation/pilot02_05.aa
git mv ./data/pilot/pilot02/glozz_preannotation/pilot02_5.ac ./data/pilot/pilot02/glozz_preannotation/pilot02_05.ac
git mv ./data/pilot/pilot02/glozz_preannotation/pilot02_6.aa ./data/pilot/pilot02/glozz_preannotation/pilot02_06.aa
git mv ./data/pilot/pilot02/glozz_preannotation/pilot02_6.ac ./data/pilot/pilot02/glozz_preannotation/pilot02_06.ac
git mv ./data/pilot/pilot02/glozz_preannotation/pilot02_7.aa ./data/pilot/pilot02/glozz_preannotation/pilot02_07.aa
git mv ./data/pilot/pilot02/glozz_preannotation/pilot02_7.ac ./data/pilot/pilot02/glozz_preannotation/pilot02_07.ac
git mv ./data/pilot/pilot02/glozz_preannotation/pilot02_8.aa ./data/pilot/pilot02/glozz_preannotation/pilot02_08.aa
git mv ./data/pilot/pilot02/glozz_preannotation/pilot02_8.ac ./data/pilot/pilot02/glozz_preannotation/pilot02_08.ac
git mv ./data/pilot/pilot02/glozz_preannotation/pilot02_9.aa ./data/pilot/pilot02/glozz_preannotation/pilot02_09.aa
git mv ./data/pilot/pilot02/glozz_preannotation/pilot02_9.ac ./data/pilot/pilot02/glozz_preannotation/pilot02_09.ac

git mv ./data/pilot/pilot02/Gold/Unit_Pred_Arg/pilot02_10.ac_petersen.seg ./data/pilot/pilot02/Gold/Unit_Pred_Arg/pilot02_10.ac.seg
git mv ./data/pilot/pilot02/Gold/Unit_Pred_Arg/pilot02_11.ac_petersen.seg ./data/pilot/pilot02/Gold/Unit_Pred_Arg/pilot02_11.ac.seg
git mv ./data/pilot/pilot02/Gold/Unit_Pred_Arg/pilot02_12.ac_petersen.seg ./data/pilot/pilot02/Gold/Unit_Pred_Arg/pilot02_12.ac.seg
git mv ./data/pilot/pilot02/Gold/Unit_Pred_Arg/pilot02_7.ac_petersen.seg ./data/pilot/pilot02/Gold/Unit_Pred_Arg/pilot02_07.ac.seg
git mv ./data/pilot/pilot02/Gold/Unit_Pred_Arg/pilot02_8.ac_petersen.seg ./data/pilot/pilot02/Gold/Unit_Pred_Arg/pilot02_08.ac.seg
git mv ./data/pilot/pilot02/Gold/Unit_Pred_Arg/pilot02_9.ac_petersen.seg ./data/pilot/pilot02/Gold/Unit_Pred_Arg/pilot02_09.ac.seg

git mv ./data/pilot/pilot02/Gold/Units/pilot02_10_petersen_u_23012013.aa ./data/pilot/pilot02/Gold/Units/pilot02_10.aa
git mv ./data/pilot/pilot02/Gold/Units/pilot02_11_petersen_u_24012013.aa ./data/pilot/pilot02/Gold/Units/pilot02_11.aa
git mv ./data/pilot/pilot02/Gold/Units/pilot02_12_petersen_u_24012013.aa ./data/pilot/pilot02/Gold/Units/pilot02_12.aa
git mv ./data/pilot/pilot02/Gold/Units/pilot02_7_petersen_u_22012012.aa ./data/pilot/pilot02/Gold/Units/pilot02_07.aa
git mv ./data/pilot/pilot02/Gold/Units/pilot02_8_petersen_u_22012012.aa ./data/pilot/pilot02/Gold/Units/pilot02_08.aa
git mv ./data/pilot/pilot02/Gold/Units/pilot02_9_petersen_u_23012013.aa ./data/pilot/pilot02/Gold/Units/pilot02_09.aa

git mv ./data/pilot/pilot03/glozz_annotations/hjoseph/discourse/pilot03_10_joseph_d_1112.aa ./data/pilot/pilot03/glozz_annotations/hjoseph/discourse/pilot03_10.aa
git mv ./data/pilot/pilot03/glozz_annotations/hjoseph/discourse/pilot03_11_joseph_d_1012.aa ./data/pilot/pilot03/glozz_annotations/hjoseph/discourse/pilot03_11.aa
git mv ./data/pilot/pilot03/glozz_annotations/hjoseph/discourse/pilot03_12_joseph_d_1012.aa ./data/pilot/pilot03/glozz_annotations/hjoseph/discourse/pilot03_12.aa
git mv ./data/pilot/pilot03/glozz_annotations/hjoseph/discourse/pilot03_1_joseph_d_juin12.aa ./data/pilot/pilot03/glozz_annotations/hjoseph/discourse/pilot03_01.aa
git mv ./data/pilot/pilot03/glozz_annotations/hjoseph/discourse/pilot03_2_joseph_d_juin12.aa ./data/pilot/pilot03/glozz_annotations/hjoseph/discourse/pilot03_02.aa
git mv ./data/pilot/pilot03/glozz_annotations/hjoseph/discourse/pilot03_3_joseph_d_Oct.aa ./data/pilot/pilot03/glozz_annotations/hjoseph/discourse/pilot03_03.aa
git mv ./data/pilot/pilot03/glozz_annotations/hjoseph/discourse/pilot03_4_joseph_d_Oct.aa ./data/pilot/pilot03/glozz_annotations/hjoseph/discourse/pilot03_04.aa
git mv ./data/pilot/pilot03/glozz_annotations/hjoseph/discourse/pilot03_6_joseph_d_0612.aa ./data/pilot/pilot03/glozz_annotations/hjoseph/discourse/pilot03_06.aa
git mv ./data/pilot/pilot03/glozz_annotations/hjoseph/discourse/pilot03_7_joseph_d_0712.aa ./data/pilot/pilot03/glozz_annotations/hjoseph/discourse/pilot03_07.aa
git mv ./data/pilot/pilot03/glozz_annotations/hjoseph/discourse/pilot03_8_joseph_d_0912.aa ./data/pilot/pilot03/glozz_annotations/hjoseph/discourse/pilot03_08.aa
git mv ./data/pilot/pilot03/glozz_annotations/hjoseph/discourse/pilot03_9_joseph_d_0912.aa ./data/pilot/pilot03/glozz_annotations/hjoseph/discourse/pilot03_09.aa

git mv ./data/pilot/pilot03/glozz_annotations/hjoseph/units/pilot03_10_joseph_u_1112.aa ./data/pilot/pilot03/glozz_annotations/hjoseph/units/pilot03_10.aa
git mv ./data/pilot/pilot03/glozz_annotations/hjoseph/units/pilot03_11_joseph_u_1112.aa ./data/pilot/pilot03/glozz_annotations/hjoseph/units/pilot03_11.aa
git mv ./data/pilot/pilot03/glozz_annotations/hjoseph/units/pilot03_12_joseph_u_1012.aa ./data/pilot/pilot03/glozz_annotations/hjoseph/units/pilot03_12.aa
git mv ./data/pilot/pilot03/glozz_annotations/hjoseph/units/pilot03_1_joseph_u_juin12.aa ./data/pilot/pilot03/glozz_annotations/hjoseph/units/pilot03_01.aa
git mv ./data/pilot/pilot03/glozz_annotations/hjoseph/units/pilot03_2_joseph_u_juin12.aa ./data/pilot/pilot03/glozz_annotations/hjoseph/units/pilot03_02.aa
git mv ./data/pilot/pilot03/glozz_annotations/hjoseph/units/pilot03_3_joseph_u_juin12.aa ./data/pilot/pilot03/glozz_annotations/hjoseph/units/pilot03_03.aa
git mv ./data/pilot/pilot03/glozz_annotations/hjoseph/units/pilot03_4_joseph_u_juin12.aa ./data/pilot/pilot03/glozz_annotations/hjoseph/units/pilot03_04.aa
git mv ./data/pilot/pilot03/glozz_annotations/hjoseph/units/pilot03_5_joseph_u_juin12.aa ./data/pilot/pilot03/glozz_annotations/hjoseph/units/pilot03_05.aa
git mv ./data/pilot/pilot03/glozz_annotations/hjoseph/units/pilot03_6_joseph_u_0612.aa ./data/pilot/pilot03/glozz_annotations/hjoseph/units/pilot03_06.aa
git mv ./data/pilot/pilot03/glozz_annotations/hjoseph/units/pilot03_7_joseph_u_0612.aa ./data/pilot/pilot03/glozz_annotations/hjoseph/units/pilot03_07.aa
git mv ./data/pilot/pilot03/glozz_annotations/hjoseph/units/pilot03_8_joseph_u_0712.aa ./data/pilot/pilot03/glozz_annotations/hjoseph/units/pilot03_08.aa
git mv ./data/pilot/pilot03/glozz_annotations/hjoseph/units/pilot03_9_joseph_u_0912.aa ./data/pilot/pilot03/glozz_annotations/hjoseph/units/pilot03_09.aa

git mv ./data/pilot/pilot03/glozz_annotations/jhall/discourse/pilot03_1.ac ./data/pilot/pilot03/glozz_annotations/jhall/discourse/pilot03_01.ac
#git mv ./data/pilot/pilot03/glozz_annotations/jhall/discourse/pilot03_10.ac ./data/pilot/pilot03/glozz_annotations/jhall/discourse/pilot03_10.ac
git mv ./data/pilot/pilot03/glozz_annotations/jhall/discourse/pilot03_10_hall_d__16062012.aa ./data/pilot/pilot03/glozz_annotations/jhall/discourse/pilot03_10.aa
#git mv ./data/pilot/pilot03/glozz_annotations/jhall/discourse/pilot03_11.ac ./data/pilot/pilot03/glozz_annotations/jhall/discourse/pilot03_11.ac
git mv ./data/pilot/pilot03/glozz_annotations/jhall/discourse/pilot03_11_hall_d__16062012.aa ./data/pilot/pilot03/glozz_annotations/jhall/discourse/pilot03_11.aa
#git mv ./data/pilot/pilot03/glozz_annotations/jhall/discourse/pilot03_12.ac ./data/pilot/pilot03/glozz_annotations/jhall/discourse/pilot03_12.ac
git mv ./data/pilot/pilot03/glozz_annotations/jhall/discourse/pilot03_12_hall_d__16062012.aa ./data/pilot/pilot03/glozz_annotations/jhall/discourse/pilot03_12.aa
git mv ./data/pilot/pilot03/glozz_annotations/jhall/discourse/pilot03_2.ac ./data/pilot/pilot03/glozz_annotations/jhall/discourse/pilot03_02.ac
git mv ./data/pilot/pilot03/glozz_annotations/jhall/discourse/pilot03_2_hall_d__07062012.aa ./data/pilot/pilot03/glozz_annotations/jhall/discourse/pilot03_02.aa
git mv ./data/pilot/pilot03/glozz_annotations/jhall/discourse/pilot03_3.ac ./data/pilot/pilot03/glozz_annotations/jhall/discourse/pilot03_03.ac
git mv ./data/pilot/pilot03/glozz_annotations/jhall/discourse/pilot03_3_hall_d__11062012.aa ./data/pilot/pilot03/glozz_annotations/jhall/discourse/pilot03_03.aa
git mv ./data/pilot/pilot03/glozz_annotations/jhall/discourse/pilot03_4.ac ./data/pilot/pilot03/glozz_annotations/jhall/discourse/pilot03_04.ac
git mv ./data/pilot/pilot03/glozz_annotations/jhall/discourse/pilot03_4_hall_d__13062012.aa ./data/pilot/pilot03/glozz_annotations/jhall/discourse/pilot03_04.aa
git mv ./data/pilot/pilot03/glozz_annotations/jhall/discourse/pilot03_5.ac ./data/pilot/pilot03/glozz_annotations/jhall/discourse/pilot03_05.ac
git mv ./data/pilot/pilot03/glozz_annotations/jhall/discourse/pilot03_5_hall_d__14062012.aa ./data/pilot/pilot03/glozz_annotations/jhall/discourse/pilot03_05.aa
git mv ./data/pilot/pilot03/glozz_annotations/jhall/discourse/pilot03_6.ac ./data/pilot/pilot03/glozz_annotations/jhall/discourse/pilot03_06.ac
git mv ./data/pilot/pilot03/glozz_annotations/jhall/discourse/pilot03_6_hall_d__14062012.aa ./data/pilot/pilot03/glozz_annotations/jhall/discourse/pilot03_06.aa
git mv ./data/pilot/pilot03/glozz_annotations/jhall/discourse/pilot03_7.ac ./data/pilot/pilot03/glozz_annotations/jhall/discourse/pilot03_07.ac
git mv ./data/pilot/pilot03/glozz_annotations/jhall/discourse/pilot03_7_hall_d__14062012.aa ./data/pilot/pilot03/glozz_annotations/jhall/discourse/pilot03_07.aa
git mv ./data/pilot/pilot03/glozz_annotations/jhall/discourse/pilot03_8.ac ./data/pilot/pilot03/glozz_annotations/jhall/discourse/pilot03_08.ac
git mv ./data/pilot/pilot03/glozz_annotations/jhall/discourse/pilot03_8_hall_d__15062012.aa ./data/pilot/pilot03/glozz_annotations/jhall/discourse/pilot03_08.aa
git mv ./data/pilot/pilot03/glozz_annotations/jhall/discourse/pilot03_9.ac ./data/pilot/pilot03/glozz_annotations/jhall/discourse/pilot03_09.ac
git mv ./data/pilot/pilot03/glozz_annotations/jhall/discourse/pilot03_9_hall_d__15062012.aa ./data/pilot/pilot03/glozz_annotations/jhall/discourse/pilot03_09.aa

git mv ./data/pilot/pilot03/glozz_annotations/jhall/units/pilot03_1.ac ./data/pilot/pilot03/glozz_annotations/jhall/units/pilot03_01.ac
#git mv ./data/pilot/pilot03/glozz_annotations/jhall/units/pilot03_10.ac ./data/pilot/pilot03/glozz_annotations/jhall/units/pilot03_10.ac
git mv ./data/pilot/pilot03/glozz_annotations/jhall/units/pilot03_10_hall_u__17062012.aa ./data/pilot/pilot03/glozz_annotations/jhall/units/pilot03_10.aa
#git mv ./data/pilot/pilot03/glozz_annotations/jhall/units/pilot03_11.ac ./data/pilot/pilot03/glozz_annotations/jhall/units/pilot03_11.ac
git mv ./data/pilot/pilot03/glozz_annotations/jhall/units/pilot03_11_hall_u__172012.aa ./data/pilot/pilot03/glozz_annotations/jhall/units/pilot03_11.aa
#git mv ./data/pilot/pilot03/glozz_annotations/jhall/units/pilot03_12.ac ./data/pilot/pilot03/glozz_annotations/jhall/units/pilot03_12.ac
git mv ./data/pilot/pilot03/glozz_annotations/jhall/units/pilot03_12_hall_u__172012.aa ./data/pilot/pilot03/glozz_annotations/jhall/units/pilot03_12.aa
git mv ./data/pilot/pilot03/glozz_annotations/jhall/units/pilot03_2.ac ./data/pilot/pilot03/glozz_annotations/jhall/units/pilot03_02.ac
git mv ./data/pilot/pilot03/glozz_annotations/jhall/units/pilot03_2_hall_u__17062012.aa ./data/pilot/pilot03/glozz_annotations/jhall/units/pilot03_02.aa
git mv ./data/pilot/pilot03/glozz_annotations/jhall/units/pilot03_3.ac ./data/pilot/pilot03/glozz_annotations/jhall/units/pilot03_03.ac
git mv ./data/pilot/pilot03/glozz_annotations/jhall/units/pilot03_3_hall_u__17062012.aa ./data/pilot/pilot03/glozz_annotations/jhall/units/pilot03_03.aa
git mv ./data/pilot/pilot03/glozz_annotations/jhall/units/pilot03_4.ac ./data/pilot/pilot03/glozz_annotations/jhall/units/pilot03_04.ac
git mv ./data/pilot/pilot03/glozz_annotations/jhall/units/pilot03_4_hall_u__17062012.aa ./data/pilot/pilot03/glozz_annotations/jhall/units/pilot03_04.aa
git mv ./data/pilot/pilot03/glozz_annotations/jhall/units/pilot03_5.ac ./data/pilot/pilot03/glozz_annotations/jhall/units/pilot03_05.ac
git mv ./data/pilot/pilot03/glozz_annotations/jhall/units/pilot03_5_hall_u__17062012.aa ./data/pilot/pilot03/glozz_annotations/jhall/units/pilot03_05.aa
git mv ./data/pilot/pilot03/glozz_annotations/jhall/units/pilot03_6.ac ./data/pilot/pilot03/glozz_annotations/jhall/units/pilot03_06.ac
git mv ./data/pilot/pilot03/glozz_annotations/jhall/units/pilot03_6_hall_u__2-17062012.aa ./data/pilot/pilot03/glozz_annotations/jhall/units/pilot03_06.aa
git mv ./data/pilot/pilot03/glozz_annotations/jhall/units/pilot03_7.ac ./data/pilot/pilot03/glozz_annotations/jhall/units/pilot03_07.ac
git mv ./data/pilot/pilot03/glozz_annotations/jhall/units/pilot03_7_hall_u__17062012.aa ./data/pilot/pilot03/glozz_annotations/jhall/units/pilot03_07.aa
git mv ./data/pilot/pilot03/glozz_annotations/jhall/units/pilot03_8.ac ./data/pilot/pilot03/glozz_annotations/jhall/units/pilot03_08.ac
git mv ./data/pilot/pilot03/glozz_annotations/jhall/units/pilot03_8_hall_u__172012.aa ./data/pilot/pilot03/glozz_annotations/jhall/units/pilot03_08.aa
git mv ./data/pilot/pilot03/glozz_annotations/jhall/units/pilot03_9.ac ./data/pilot/pilot03/glozz_annotations/jhall/units/pilot03_09.ac
git mv ./data/pilot/pilot03/glozz_annotations/jhall/units/pilot03_9_hall_u__172012.aa ./data/pilot/pilot03/glozz_annotations/jhall/units/pilot03_09.aa

git mv ./data/pilot/pilot03/glozz_annotations/lpetersen/discourse/pilot03_10_petersen_d_28112012.aa ./data/pilot/pilot03/glozz_annotations/lpetersen/discourse/pilot03_10.aa
git mv ./data/pilot/pilot03/glozz_annotations/lpetersen/discourse/pilot03_11_petersen_d_28112012.aa ./data/pilot/pilot03/glozz_annotations/lpetersen/discourse/pilot03_11.aa
git mv ./data/pilot/pilot03/glozz_annotations/lpetersen/discourse/pilot03_12_petersen_d_28112012.aa ./data/pilot/pilot03/glozz_annotations/lpetersen/discourse/pilot03_12.aa
git mv ./data/pilot/pilot03/glozz_annotations/lpetersen/discourse/pilot03_1_petersen_d_05062012.aa ./data/pilot/pilot03/glozz_annotations/lpetersen/discourse/pilot03_01.aa
git mv ./data/pilot/pilot03/glozz_annotations/lpetersen/discourse/pilot03_2_petersen_d_06062012.aa ./data/pilot/pilot03/glozz_annotations/lpetersen/discourse/pilot03_02.aa
git mv ./data/pilot/pilot03/glozz_annotations/lpetersen/discourse/pilot03_3_petersen_d_05102012.aa ./data/pilot/pilot03/glozz_annotations/lpetersen/discourse/pilot03_03.aa
git mv ./data/pilot/pilot03/glozz_annotations/lpetersen/discourse/pilot03_4_petersen_d_05102012.aa ./data/pilot/pilot03/glozz_annotations/lpetersen/discourse/pilot03_04.aa
git mv ./data/pilot/pilot03/glozz_annotations/lpetersen/discourse/pilot03_5_petersen_d_26112012.aa ./data/pilot/pilot03/glozz_annotations/lpetersen/discourse/pilot03_05.aa
git mv ./data/pilot/pilot03/glozz_annotations/lpetersen/discourse/pilot03_6_petersen_d_26112012.aa ./data/pilot/pilot03/glozz_annotations/lpetersen/discourse/pilot03_06.aa
git mv ./data/pilot/pilot03/glozz_annotations/lpetersen/discourse/pilot03_7_petersen_d_27112012.aa ./data/pilot/pilot03/glozz_annotations/lpetersen/discourse/pilot03_07.aa
git mv ./data/pilot/pilot03/glozz_annotations/lpetersen/discourse/pilot03_9_petersen_d_28112012.aa ./data/pilot/pilot03/glozz_annotations/lpetersen/discourse/pilot03_09.aa

git mv ./data/pilot/pilot03/glozz_annotations/lpetersen/units/pilot03_10_petersen_u_21092012.aa ./data/pilot/pilot03/glozz_annotations/lpetersen/units/pilot03_10.aa
git mv ./data/pilot/pilot03/glozz_annotations/lpetersen/units/pilot03_11_petersen_u_21092012.aa ./data/pilot/pilot03/glozz_annotations/lpetersen/units/pilot03_11.aa
git mv ./data/pilot/pilot03/glozz_annotations/lpetersen/units/pilot03_12_petersen_u_21092012.aa ./data/pilot/pilot03/glozz_annotations/lpetersen/units/pilot03_12.aa
git mv ./data/pilot/pilot03/glozz_annotations/lpetersen/units/pilot03_1_petersen_u_20092012.aa ./data/pilot/pilot03/glozz_annotations/lpetersen/units/pilot03_01.aa
git mv ./data/pilot/pilot03/glozz_annotations/lpetersen/units/pilot03_2_petersen_u_20092012.aa ./data/pilot/pilot03/glozz_annotations/lpetersen/units/pilot03_02.aa
git mv ./data/pilot/pilot03/glozz_annotations/lpetersen/units/pilot03_3_petersen_u_21092012.aa ./data/pilot/pilot03/glozz_annotations/lpetersen/units/pilot03_03.aa
git mv ./data/pilot/pilot03/glozz_annotations/lpetersen/units/pilot03_4_petersen_u_21092012.aa ./data/pilot/pilot03/glozz_annotations/lpetersen/units/pilot03_04.aa
git mv ./data/pilot/pilot03/glozz_annotations/lpetersen/units/pilot03_5_petersen_u_21092012.aa ./data/pilot/pilot03/glozz_annotations/lpetersen/units/pilot03_05.aa
git mv ./data/pilot/pilot03/glozz_annotations/lpetersen/units/pilot03_6_petersen_u_21092012.aa ./data/pilot/pilot03/glozz_annotations/lpetersen/units/pilot03_06.aa
git mv ./data/pilot/pilot03/glozz_annotations/lpetersen/units/pilot03_7_petersen_u_21092012.aa ./data/pilot/pilot03/glozz_annotations/lpetersen/units/pilot03_07.aa
git mv ./data/pilot/pilot03/glozz_annotations/lpetersen/units/pilot03_8_petersen_u_21092012.aa ./data/pilot/pilot03/glozz_annotations/lpetersen/units/pilot03_08.aa
git mv ./data/pilot/pilot03/glozz_annotations/lpetersen/units/pilot03_9_petersen_u_21092012.aa ./data/pilot/pilot03/glozz_annotations/lpetersen/units/pilot03_09.aa

git mv ./data/pilot/pilot03/glozz_annotations/mhunt/discourse/pilot03_1.ac ./data/pilot/pilot03/glozz_annotations/mhunt/discourse/pilot03_01.ac
#git mv ./data/pilot/pilot03/glozz_annotations/mhunt/discourse/pilot03_10.ac ./data/pilot/pilot03/glozz_annotations/mhunt/discourse/pilot03_10.ac
#git mv ./data/pilot/pilot03/glozz_annotations/mhunt/discourse/pilot03_11.ac ./data/pilot/pilot03/glozz_annotations/mhunt/discourse/pilot03_11.ac
#git mv ./data/pilot/pilot03/glozz_annotations/mhunt/discourse/pilot03_12.ac ./data/pilot/pilot03/glozz_annotations/mhunt/discourse/pilot03_12.ac
git mv ./data/pilot/pilot03/glozz_annotations/mhunt/discourse/pilot03_2.ac ./data/pilot/pilot03/glozz_annotations/mhunt/discourse/pilot03_02.ac
git mv ./data/pilot/pilot03/glozz_annotations/mhunt/discourse/pilot03_2_martha_d_20121008.aa ./data/pilot/pilot03/glozz_annotations/mhunt/discourse/pilot03_02.aa
git mv ./data/pilot/pilot03/glozz_annotations/mhunt/discourse/pilot03_3.ac ./data/pilot/pilot03/glozz_annotations/mhunt/discourse/pilot03_03.ac
git mv ./data/pilot/pilot03/glozz_annotations/mhunt/discourse/pilot03_3_martha_d_20121008.aa ./data/pilot/pilot03/glozz_annotations/mhunt/discourse/pilot03_03.aa
git mv ./data/pilot/pilot03/glozz_annotations/mhunt/discourse/pilot03_4.ac ./data/pilot/pilot03/glozz_annotations/mhunt/discourse/pilot03_04.ac
git mv ./data/pilot/pilot03/glozz_annotations/mhunt/discourse/pilot03_4_martha_d_20121008.aa ./data/pilot/pilot03/glozz_annotations/mhunt/discourse/pilot03_04.aa
git mv ./data/pilot/pilot03/glozz_annotations/mhunt/discourse/pilot03_5.ac ./data/pilot/pilot03/glozz_annotations/mhunt/discourse/pilot03_05.ac
git mv ./data/pilot/pilot03/glozz_annotations/mhunt/discourse/pilot03_6.ac ./data/pilot/pilot03/glozz_annotations/mhunt/discourse/pilot03_06.ac
git mv ./data/pilot/pilot03/glozz_annotations/mhunt/discourse/pilot03_7.ac ./data/pilot/pilot03/glozz_annotations/mhunt/discourse/pilot03_07.ac
git mv ./data/pilot/pilot03/glozz_annotations/mhunt/discourse/pilot03_8.ac ./data/pilot/pilot03/glozz_annotations/mhunt/discourse/pilot03_08.ac
git mv ./data/pilot/pilot03/glozz_annotations/mhunt/discourse/pilot03_9.ac ./data/pilot/pilot03/glozz_annotations/mhunt/discourse/pilot03_09.ac

git mv ./data/pilot/pilot03/glozz_annotations/mhunt/units/pilot03_1.ac ./data/pilot/pilot03/glozz_annotations/mhunt/units/pilot03_01.ac
#git mv ./data/pilot/pilot03/glozz_annotations/mhunt/units/pilot03_10.ac ./data/pilot/pilot03/glozz_annotations/mhunt/units/pilot03_10.ac
#git mv ./data/pilot/pilot03/glozz_annotations/mhunt/units/pilot03_11.ac ./data/pilot/pilot03/glozz_annotations/mhunt/units/pilot03_11.ac
#git mv ./data/pilot/pilot03/glozz_annotations/mhunt/units/pilot03_12.ac ./data/pilot/pilot03/glozz_annotations/mhunt/units/pilot03_12.ac
git mv ./data/pilot/pilot03/glozz_annotations/mhunt/units/pilot03_2.ac ./data/pilot/pilot03/glozz_annotations/mhunt/units/pilot03_02.ac
git mv ./data/pilot/pilot03/glozz_annotations/mhunt/units/pilot03_3.ac ./data/pilot/pilot03/glozz_annotations/mhunt/units/pilot03_03.ac
git mv ./data/pilot/pilot03/glozz_annotations/mhunt/units/pilot03_4.ac ./data/pilot/pilot03/glozz_annotations/mhunt/units/pilot03_04.ac
git mv ./data/pilot/pilot03/glozz_annotations/mhunt/units/pilot03_5.ac ./data/pilot/pilot03/glozz_annotations/mhunt/units/pilot03_05.ac
git mv ./data/pilot/pilot03/glozz_annotations/mhunt/units/pilot03_6.ac ./data/pilot/pilot03/glozz_annotations/mhunt/units/pilot03_06.ac
git mv ./data/pilot/pilot03/glozz_annotations/mhunt/units/pilot03_7.ac ./data/pilot/pilot03/glozz_annotations/mhunt/units/pilot03_07.ac
git mv ./data/pilot/pilot03/glozz_annotations/mhunt/units/pilot03_8.ac ./data/pilot/pilot03/glozz_annotations/mhunt/units/pilot03_08.ac
git mv ./data/pilot/pilot03/glozz_annotations/mhunt/units/pilot03_9.ac ./data/pilot/pilot03/glozz_annotations/mhunt/units/pilot03_09.ac

git mv ./data/pilot/pilot03/glozz_preannotation/pilot03_1.aa ./data/pilot/pilot03/glozz_preannotation/pilot03_01.aa
git mv ./data/pilot/pilot03/glozz_preannotation/pilot03_1.ac ./data/pilot/pilot03/glozz_preannotation/pilot03_01.ac
#git mv ./data/pilot/pilot03/glozz_preannotation/pilot03_10.aa ./data/pilot/pilot03/glozz_preannotation/pilot03_10.aa
#git mv ./data/pilot/pilot03/glozz_preannotation/pilot03_10.ac ./data/pilot/pilot03/glozz_preannotation/pilot03_10.ac
#git mv ./data/pilot/pilot03/glozz_preannotation/pilot03_11.aa ./data/pilot/pilot03/glozz_preannotation/pilot03_11.aa
#git mv ./data/pilot/pilot03/glozz_preannotation/pilot03_11.ac ./data/pilot/pilot03/glozz_preannotation/pilot03_11.ac
#git mv ./data/pilot/pilot03/glozz_preannotation/pilot03_12.aa ./data/pilot/pilot03/glozz_preannotation/pilot03_12.aa
#git mv ./data/pilot/pilot03/glozz_preannotation/pilot03_12.ac ./data/pilot/pilot03/glozz_preannotation/pilot03_12.ac
git mv ./data/pilot/pilot03/glozz_preannotation/pilot03_2.aa ./data/pilot/pilot03/glozz_preannotation/pilot03_02.aa
git mv ./data/pilot/pilot03/glozz_preannotation/pilot03_2.ac ./data/pilot/pilot03/glozz_preannotation/pilot03_02.ac
git mv ./data/pilot/pilot03/glozz_preannotation/pilot03_3.aa ./data/pilot/pilot03/glozz_preannotation/pilot03_03.aa
git mv ./data/pilot/pilot03/glozz_preannotation/pilot03_3.ac ./data/pilot/pilot03/glozz_preannotation/pilot03_03.ac
git mv ./data/pilot/pilot03/glozz_preannotation/pilot03_4.aa ./data/pilot/pilot03/glozz_preannotation/pilot03_04.aa
git mv ./data/pilot/pilot03/glozz_preannotation/pilot03_4.ac ./data/pilot/pilot03/glozz_preannotation/pilot03_04.ac
git mv ./data/pilot/pilot03/glozz_preannotation/pilot03_5.aa ./data/pilot/pilot03/glozz_preannotation/pilot03_05.aa
git mv ./data/pilot/pilot03/glozz_preannotation/pilot03_5.ac ./data/pilot/pilot03/glozz_preannotation/pilot03_05.ac
git mv ./data/pilot/pilot03/glozz_preannotation/pilot03_6.aa ./data/pilot/pilot03/glozz_preannotation/pilot03_06.aa
git mv ./data/pilot/pilot03/glozz_preannotation/pilot03_6.ac ./data/pilot/pilot03/glozz_preannotation/pilot03_06.ac
git mv ./data/pilot/pilot03/glozz_preannotation/pilot03_7.aa ./data/pilot/pilot03/glozz_preannotation/pilot03_07.aa
git mv ./data/pilot/pilot03/glozz_preannotation/pilot03_7.ac ./data/pilot/pilot03/glozz_preannotation/pilot03_07.ac
git mv ./data/pilot/pilot03/glozz_preannotation/pilot03_8.aa ./data/pilot/pilot03/glozz_preannotation/pilot03_08.aa
git mv ./data/pilot/pilot03/glozz_preannotation/pilot03_8.ac ./data/pilot/pilot03/glozz_preannotation/pilot03_08.ac
git mv ./data/pilot/pilot03/glozz_preannotation/pilot03_9.aa ./data/pilot/pilot03/glozz_preannotation/pilot03_09.aa
git mv ./data/pilot/pilot03/glozz_preannotation/pilot03_9.ac ./data/pilot/pilot03/glozz_preannotation/pilot03_09.ac

git mv ./data/pilot/pilot03/Gold/Unit/pilot03_10_petersen_u_21092012.aa ./data/pilot/pilot03/Gold/Unit/pilot03_10.aa
git mv ./data/pilot/pilot03/Gold/Unit/pilot03_11_petersen_u_21092012.aa ./data/pilot/pilot03/Gold/Unit/pilot03_11.aa
git mv ./data/pilot/pilot03/Gold/Unit/pilot03_12_petersen_u_21092012.aa ./data/pilot/pilot03/Gold/Unit/pilot03_12.aa
git mv ./data/pilot/pilot03/Gold/Unit/pilot03_1_petersen_u_20092012.aa ./data/pilot/pilot03/Gold/Unit/pilot03_01.aa
git mv ./data/pilot/pilot03/Gold/Unit/pilot03_2_petersen_u_20092012.aa ./data/pilot/pilot03/Gold/Unit/pilot03_02.aa
git mv ./data/pilot/pilot03/Gold/Unit/pilot03_3_petersen_u_21092012.aa ./data/pilot/pilot03/Gold/Unit/pilot03_03.aa
git mv ./data/pilot/pilot03/Gold/Unit/pilot03_4_petersen_u_21092012.aa ./data/pilot/pilot03/Gold/Unit/pilot03_04.aa
git mv ./data/pilot/pilot03/Gold/Unit/pilot03_5_petersen_u_21092012.aa ./data/pilot/pilot03/Gold/Unit/pilot03_05.aa
git mv ./data/pilot/pilot03/Gold/Unit/pilot03_6_petersen_u_21092012.aa ./data/pilot/pilot03/Gold/Unit/pilot03_06.aa
git mv ./data/pilot/pilot03/Gold/Unit/pilot03_7_petersen_u_21092012.aa ./data/pilot/pilot03/Gold/Unit/pilot03_07.aa
git mv ./data/pilot/pilot03/Gold/Unit/pilot03_8_petersen_u_21092012.aa ./data/pilot/pilot03/Gold/Unit/pilot03_08.aa
git mv ./data/pilot/pilot03/Gold/Unit/pilot03_9_petersen_u_21092012.aa ./data/pilot/pilot03/Gold/Unit/pilot03_09.aa

git mv ./data/pilot/pilot03/Gold/Unit_pred_arg/pilot03_1.ac_petersen.seg ./data/pilot/pilot03/Gold/Unit_pred_arg/pilot03_01.ac.seg
git mv ./data/pilot/pilot03/Gold/Unit_pred_arg/pilot03_10.ac_petersen.seg ./data/pilot/pilot03/Gold/Unit_pred_arg/pilot03_10.ac.seg
git mv ./data/pilot/pilot03/Gold/Unit_pred_arg/pilot03_11.ac_petersen.seg ./data/pilot/pilot03/Gold/Unit_pred_arg/pilot03_11.ac.seg
git mv ./data/pilot/pilot03/Gold/Unit_pred_arg/pilot03_12.ac_petersen.seg ./data/pilot/pilot03/Gold/Unit_pred_arg/pilot03_12.ac.seg
git mv ./data/pilot/pilot03/Gold/Unit_pred_arg/pilot03_2.ac_petersen.seg ./data/pilot/pilot03/Gold/Unit_pred_arg/pilot03_02.ac.seg
git mv ./data/pilot/pilot03/Gold/Unit_pred_arg/pilot03_3.ac_petersen.seg ./data/pilot/pilot03/Gold/Unit_pred_arg/pilot03_03.ac.seg
git mv ./data/pilot/pilot03/Gold/Unit_pred_arg/pilot03_4.ac_petersen.seg ./data/pilot/pilot03/Gold/Unit_pred_arg/pilot03_04.ac.seg
git mv ./data/pilot/pilot03/Gold/Unit_pred_arg/pilot03_5.ac_petersen.seg ./data/pilot/pilot03/Gold/Unit_pred_arg/pilot03_05.ac.seg
git mv ./data/pilot/pilot03/Gold/Unit_pred_arg/pilot03_6.ac_petersen.seg ./data/pilot/pilot03/Gold/Unit_pred_arg/pilot03_06.ac.seg
git mv ./data/pilot/pilot03/Gold/Unit_pred_arg/pilot03_7.ac_petersen.seg ./data/pilot/pilot03/Gold/Unit_pred_arg/pilot03_07.ac.seg
git mv ./data/pilot/pilot03/Gold/Unit_pred_arg/pilot03_8.ac_petersen.seg ./data/pilot/pilot03/Gold/Unit_pred_arg/pilot03_08.ac.seg
git mv ./data/pilot/pilot03/Gold/Unit_pred_arg/pilot03_9.ac_petersen.seg ./data/pilot/pilot03/Gold/Unit_pred_arg/pilot03_09.ac.seg

git mv ./data/pilot/pilot03/pred_arg_annotations/hjoseph/discourse/pilot03_1.ac_joseph.rel ./data/pilot/pilot03/pred_arg_annotations/hjoseph/discourse/pilot03_01.ac.rel
git mv ./data/pilot/pilot03/pred_arg_annotations/hjoseph/discourse/pilot03_10.ac_joseph.rel ./data/pilot/pilot03/pred_arg_annotations/hjoseph/discourse/pilot03_10.ac.rel
git mv ./data/pilot/pilot03/pred_arg_annotations/hjoseph/discourse/pilot03_11.ac_joseph.rel ./data/pilot/pilot03/pred_arg_annotations/hjoseph/discourse/pilot03_11.ac.rel
git mv ./data/pilot/pilot03/pred_arg_annotations/hjoseph/discourse/pilot03_12.ac_joseph.rel ./data/pilot/pilot03/pred_arg_annotations/hjoseph/discourse/pilot03_12.ac.rel
git mv ./data/pilot/pilot03/pred_arg_annotations/hjoseph/discourse/pilot03_2.ac_joseph.rel ./data/pilot/pilot03/pred_arg_annotations/hjoseph/discourse/pilot03_02.ac.rel
git mv ./data/pilot/pilot03/pred_arg_annotations/hjoseph/discourse/pilot03_3.ac_joseph.rel ./data/pilot/pilot03/pred_arg_annotations/hjoseph/discourse/pilot03_03.ac.rel
git mv ./data/pilot/pilot03/pred_arg_annotations/hjoseph/discourse/pilot03_4.ac_joseph.rel ./data/pilot/pilot03/pred_arg_annotations/hjoseph/discourse/pilot03_04.ac.rel
git mv ./data/pilot/pilot03/pred_arg_annotations/hjoseph/discourse/pilot03_6.ac_joseph.rel ./data/pilot/pilot03/pred_arg_annotations/hjoseph/discourse/pilot03_06.ac.rel
git mv ./data/pilot/pilot03/pred_arg_annotations/hjoseph/discourse/pilot03_7.ac_joseph.rel ./data/pilot/pilot03/pred_arg_annotations/hjoseph/discourse/pilot03_07.ac.rel
git mv ./data/pilot/pilot03/pred_arg_annotations/hjoseph/discourse/pilot03_8.ac_joseph.rel ./data/pilot/pilot03/pred_arg_annotations/hjoseph/discourse/pilot03_08.ac.rel
git mv ./data/pilot/pilot03/pred_arg_annotations/hjoseph/discourse/pilot03_9.ac_joseph.rel ./data/pilot/pilot03/pred_arg_annotations/hjoseph/discourse/pilot03_09.ac.rel

git mv ./data/pilot/pilot03/pred_arg_annotations/hjoseph/unit/pilot03_1.ac_joseph.seg ./data/pilot/pilot03/pred_arg_annotations/hjoseph/unit/pilot03_01.ac.seg
git mv ./data/pilot/pilot03/pred_arg_annotations/hjoseph/unit/pilot03_10.ac_joseph.seg ./data/pilot/pilot03/pred_arg_annotations/hjoseph/unit/pilot03_10.ac.seg
git mv ./data/pilot/pilot03/pred_arg_annotations/hjoseph/unit/pilot03_11.ac_joseph.seg ./data/pilot/pilot03/pred_arg_annotations/hjoseph/unit/pilot03_11.ac.seg
git mv ./data/pilot/pilot03/pred_arg_annotations/hjoseph/unit/pilot03_12.ac_joseph.seg ./data/pilot/pilot03/pred_arg_annotations/hjoseph/unit/pilot03_12.ac.seg
git mv ./data/pilot/pilot03/pred_arg_annotations/hjoseph/unit/pilot03_3.ac_joseph.seg ./data/pilot/pilot03/pred_arg_annotations/hjoseph/unit/pilot03_03.ac.seg
git mv ./data/pilot/pilot03/pred_arg_annotations/hjoseph/unit/pilot03_4.ac_joseph.seg ./data/pilot/pilot03/pred_arg_annotations/hjoseph/unit/pilot03_04.ac.seg
git mv ./data/pilot/pilot03/pred_arg_annotations/hjoseph/unit/pilot03_5.ac_joseph.seg ./data/pilot/pilot03/pred_arg_annotations/hjoseph/unit/pilot03_05.ac.seg
git mv ./data/pilot/pilot03/pred_arg_annotations/hjoseph/unit/pilot03_6.ac_joseph.seg ./data/pilot/pilot03/pred_arg_annotations/hjoseph/unit/pilot03_06.ac.seg
git mv ./data/pilot/pilot03/pred_arg_annotations/hjoseph/unit/pilot03_7.ac_joseph.seg ./data/pilot/pilot03/pred_arg_annotations/hjoseph/unit/pilot03_07.ac.seg
git mv ./data/pilot/pilot03/pred_arg_annotations/hjoseph/unit/pilot03_8.ac_joseph.seg ./data/pilot/pilot03/pred_arg_annotations/hjoseph/unit/pilot03_08.ac.seg
git mv ./data/pilot/pilot03/pred_arg_annotations/hjoseph/unit/pilot03_9.ac_joseph.seg ./data/pilot/pilot03/pred_arg_annotations/hjoseph/unit/pilot03_09.ac.seg

git mv ./data/pilot/pilot03/pred_arg_annotations/lpetersen/discourse/pilot03_1.ac_petersen.rel ./data/pilot/pilot03/pred_arg_annotations/lpetersen/discourse/pilot03_01.ac.rel
git mv ./data/pilot/pilot03/pred_arg_annotations/lpetersen/discourse/pilot03_10.ac_petersen.rel ./data/pilot/pilot03/pred_arg_annotations/lpetersen/discourse/pilot03_10.ac.rel
git mv ./data/pilot/pilot03/pred_arg_annotations/lpetersen/discourse/pilot03_11.ac_petersen.rel ./data/pilot/pilot03/pred_arg_annotations/lpetersen/discourse/pilot03_11.ac.rel
git mv ./data/pilot/pilot03/pred_arg_annotations/lpetersen/discourse/pilot03_12.ac_petersen.rel ./data/pilot/pilot03/pred_arg_annotations/lpetersen/discourse/pilot03_12.ac.rel
git mv ./data/pilot/pilot03/pred_arg_annotations/lpetersen/discourse/pilot03_2.ac_petersen.rel ./data/pilot/pilot03/pred_arg_annotations/lpetersen/discourse/pilot03_02.ac.rel
git mv ./data/pilot/pilot03/pred_arg_annotations/lpetersen/discourse/pilot03_3.ac_petersen.rel ./data/pilot/pilot03/pred_arg_annotations/lpetersen/discourse/pilot03_03.ac.rel
git mv ./data/pilot/pilot03/pred_arg_annotations/lpetersen/discourse/pilot03_4.ac_petersen.rel ./data/pilot/pilot03/pred_arg_annotations/lpetersen/discourse/pilot03_04.ac.rel
git mv ./data/pilot/pilot03/pred_arg_annotations/lpetersen/discourse/pilot03_5.ac_petersen.rel ./data/pilot/pilot03/pred_arg_annotations/lpetersen/discourse/pilot03_05.ac.rel
git mv ./data/pilot/pilot03/pred_arg_annotations/lpetersen/discourse/pilot03_6.ac_petersen.rel ./data/pilot/pilot03/pred_arg_annotations/lpetersen/discourse/pilot03_06.ac.rel
git mv ./data/pilot/pilot03/pred_arg_annotations/lpetersen/discourse/pilot03_7.ac_petersen.rel ./data/pilot/pilot03/pred_arg_annotations/lpetersen/discourse/pilot03_07.ac.rel
git mv ./data/pilot/pilot03/pred_arg_annotations/lpetersen/discourse/pilot03_8.ac_petersen.rel ./data/pilot/pilot03/pred_arg_annotations/lpetersen/discourse/pilot03_08.ac.rel
git mv ./data/pilot/pilot03/pred_arg_annotations/lpetersen/discourse/pilot03_9.ac_petersen.rel ./data/pilot/pilot03/pred_arg_annotations/lpetersen/discourse/pilot03_09.ac.rel

git mv ./data/pilot/pilot03/pred_arg_annotations/lpetersen/unit/pilot03_1.ac_petersen.seg ./data/pilot/pilot03/pred_arg_annotations/lpetersen/unit/pilot03_01.ac.seg
git mv ./data/pilot/pilot03/pred_arg_annotations/lpetersen/unit/pilot03_10.ac_petersen.seg ./data/pilot/pilot03/pred_arg_annotations/lpetersen/unit/pilot03_10.ac.seg
git mv ./data/pilot/pilot03/pred_arg_annotations/lpetersen/unit/pilot03_11.ac_petersen.seg ./data/pilot/pilot03/pred_arg_annotations/lpetersen/unit/pilot03_11.ac.seg
git mv ./data/pilot/pilot03/pred_arg_annotations/lpetersen/unit/pilot03_12.ac_petersen.seg ./data/pilot/pilot03/pred_arg_annotations/lpetersen/unit/pilot03_12.ac.seg
git mv ./data/pilot/pilot03/pred_arg_annotations/lpetersen/unit/pilot03_2.ac_petersen.seg ./data/pilot/pilot03/pred_arg_annotations/lpetersen/unit/pilot03_02.ac.seg
git mv ./data/pilot/pilot03/pred_arg_annotations/lpetersen/unit/pilot03_3.ac_petersen.seg ./data/pilot/pilot03/pred_arg_annotations/lpetersen/unit/pilot03_03.ac.seg
git mv ./data/pilot/pilot03/pred_arg_annotations/lpetersen/unit/pilot03_4.ac_petersen.seg ./data/pilot/pilot03/pred_arg_annotations/lpetersen/unit/pilot03_04.ac.seg
git mv ./data/pilot/pilot03/pred_arg_annotations/lpetersen/unit/pilot03_5.ac_petersen.seg ./data/pilot/pilot03/pred_arg_annotations/lpetersen/unit/pilot03_05.ac.seg
git mv ./data/pilot/pilot03/pred_arg_annotations/lpetersen/unit/pilot03_6.ac_petersen.seg ./data/pilot/pilot03/pred_arg_annotations/lpetersen/unit/pilot03_06.ac.seg
git mv ./data/pilot/pilot03/pred_arg_annotations/lpetersen/unit/pilot03_7.ac_petersen.seg ./data/pilot/pilot03/pred_arg_annotations/lpetersen/unit/pilot03_07.ac.seg
git mv ./data/pilot/pilot03/pred_arg_annotations/lpetersen/unit/pilot03_8.ac_petersen.seg ./data/pilot/pilot03/pred_arg_annotations/lpetersen/unit/pilot03_08.ac.seg
git mv ./data/pilot/pilot03/pred_arg_annotations/lpetersen/unit/pilot03_9.ac_petersen.seg ./data/pilot/pilot03/pred_arg_annotations/lpetersen/unit/pilot03_09.ac.seg

git mv ./data/pilot/pilot04/glozz_annotations/hjoseph/discourse/pilot04_10_joseph_d_2012.aa ./data/pilot/pilot04/glozz_annotations/hjoseph/discourse/pilot04_10.aa
git mv ./data/pilot/pilot04/glozz_annotations/hjoseph/discourse/pilot04_12_joseph_d_2501.aa ./data/pilot/pilot04/glozz_annotations/hjoseph/discourse/pilot04_12.aa
git mv ./data/pilot/pilot04/glozz_annotations/hjoseph/discourse/pilot04_1_joseph_d_1012.aa ./data/pilot/pilot04/glozz_annotations/hjoseph/discourse/pilot04_01.aa
git mv ./data/pilot/pilot04/glozz_annotations/hjoseph/discourse/pilot04_3_joseph_d_1212.aa ./data/pilot/pilot04/glozz_annotations/hjoseph/discourse/pilot04_03.aa
git mv ./data/pilot/pilot04/glozz_annotations/hjoseph/discourse/pilot04_4_joseph_d_1712.aa ./data/pilot/pilot04/glozz_annotations/hjoseph/discourse/pilot04_04.aa
git mv ./data/pilot/pilot04/glozz_annotations/hjoseph/discourse/pilot04_6_joseph_d_1812.aa ./data/pilot/pilot04/glozz_annotations/hjoseph/discourse/pilot04_06.aa
git mv ./data/pilot/pilot04/glozz_annotations/hjoseph/discourse/pilot04_7_joseph_d_1812.aa ./data/pilot/pilot04/glozz_annotations/hjoseph/discourse/pilot04_07.aa
git mv ./data/pilot/pilot04/glozz_annotations/hjoseph/discourse/pilot04_9_joseph_d_1812.aa ./data/pilot/pilot04/glozz_annotations/hjoseph/discourse/pilot04_09.aa

git mv ./data/pilot/pilot04/glozz_annotations/hjoseph/units/pilot04_10_joseph_u_1812.aa ./data/pilot/pilot04/glozz_annotations/hjoseph/units/pilot04_10.aa
git mv ./data/pilot/pilot04/glozz_annotations/hjoseph/units/pilot04_12_joseph_u_2401.aa ./data/pilot/pilot04/glozz_annotations/hjoseph/units/pilot04_12.aa
git mv ./data/pilot/pilot04/glozz_annotations/hjoseph/units/pilot04_1_joseph_u_1012.aa ./data/pilot/pilot04/glozz_annotations/hjoseph/units/pilot04_01.aa
git mv ./data/pilot/pilot04/glozz_annotations/hjoseph/units/pilot04_3_joseph_u_1212.aa ./data/pilot/pilot04/glozz_annotations/hjoseph/units/pilot04_03.aa
git mv ./data/pilot/pilot04/glozz_annotations/hjoseph/units/pilot04_4_joseph_u_1712.aa ./data/pilot/pilot04/glozz_annotations/hjoseph/units/pilot04_04.aa
git mv ./data/pilot/pilot04/glozz_annotations/hjoseph/units/pilot04_6_joseph_u_1812.aa ./data/pilot/pilot04/glozz_annotations/hjoseph/units/pilot04_06.aa
git mv ./data/pilot/pilot04/glozz_annotations/hjoseph/units/pilot04_7_joseph_u_1812.aa ./data/pilot/pilot04/glozz_annotations/hjoseph/units/pilot04_07.aa
git mv ./data/pilot/pilot04/glozz_annotations/hjoseph/units/pilot04_9_joseph_u_1812.aa ./data/pilot/pilot04/glozz_annotations/hjoseph/units/pilot04_09.aa

git mv ./data/pilot/pilot04/glozz_annotations/jhall/discourse/pilot04_1.ac ./data/pilot/pilot04/glozz_annotations/jhall/discourse/pilot04_01.ac
#git mv ./data/pilot/pilot04/glozz_annotations/jhall/discourse/pilot04_10.ac ./data/pilot/pilot04/glozz_annotations/jhall/discourse/pilot04_10.ac
#git mv ./data/pilot/pilot04/glozz_annotations/jhall/discourse/pilot04_11.ac ./data/pilot/pilot04/glozz_annotations/jhall/discourse/pilot04_11.ac
#git mv ./data/pilot/pilot04/glozz_annotations/jhall/discourse/pilot04_12.ac ./data/pilot/pilot04/glozz_annotations/jhall/discourse/pilot04_12.ac
git mv ./data/pilot/pilot04/glozz_annotations/jhall/discourse/pilot04_2.ac ./data/pilot/pilot04/glozz_annotations/jhall/discourse/pilot04_02.ac
git mv ./data/pilot/pilot04/glozz_annotations/jhall/discourse/pilot04_3.ac ./data/pilot/pilot04/glozz_annotations/jhall/discourse/pilot04_03.ac
git mv ./data/pilot/pilot04/glozz_annotations/jhall/discourse/pilot04_4.ac ./data/pilot/pilot04/glozz_annotations/jhall/discourse/pilot04_04.ac
git mv ./data/pilot/pilot04/glozz_annotations/jhall/discourse/pilot04_5.ac ./data/pilot/pilot04/glozz_annotations/jhall/discourse/pilot04_05.ac
git mv ./data/pilot/pilot04/glozz_annotations/jhall/discourse/pilot04_6.ac ./data/pilot/pilot04/glozz_annotations/jhall/discourse/pilot04_06.ac
git mv ./data/pilot/pilot04/glozz_annotations/jhall/discourse/pilot04_7.ac ./data/pilot/pilot04/glozz_annotations/jhall/discourse/pilot04_07.ac
git mv ./data/pilot/pilot04/glozz_annotations/jhall/discourse/pilot04_8.ac ./data/pilot/pilot04/glozz_annotations/jhall/discourse/pilot04_08.ac
git mv ./data/pilot/pilot04/glozz_annotations/jhall/discourse/pilot04_9.ac ./data/pilot/pilot04/glozz_annotations/jhall/discourse/pilot04_09.ac

git mv ./data/pilot/pilot04/glozz_annotations/jhall/units/pilot04_1.ac ./data/pilot/pilot04/glozz_annotations/jhall/units/pilot04_01.ac
#git mv ./data/pilot/pilot04/glozz_annotations/jhall/units/pilot04_10.ac ./data/pilot/pilot04/glozz_annotations/jhall/units/pilot04_10.ac
#git mv ./data/pilot/pilot04/glozz_annotations/jhall/units/pilot04_11.ac ./data/pilot/pilot04/glozz_annotations/jhall/units/pilot04_11.ac
#git mv ./data/pilot/pilot04/glozz_annotations/jhall/units/pilot04_12.ac ./data/pilot/pilot04/glozz_annotations/jhall/units/pilot04_12.ac
git mv ./data/pilot/pilot04/glozz_annotations/jhall/units/pilot04_2.ac ./data/pilot/pilot04/glozz_annotations/jhall/units/pilot04_02.ac
git mv ./data/pilot/pilot04/glozz_annotations/jhall/units/pilot04_3.ac ./data/pilot/pilot04/glozz_annotations/jhall/units/pilot04_03.ac
git mv ./data/pilot/pilot04/glozz_annotations/jhall/units/pilot04_4.ac ./data/pilot/pilot04/glozz_annotations/jhall/units/pilot04_04.ac
git mv ./data/pilot/pilot04/glozz_annotations/jhall/units/pilot04_5.ac ./data/pilot/pilot04/glozz_annotations/jhall/units/pilot04_05.ac
git mv ./data/pilot/pilot04/glozz_annotations/jhall/units/pilot04_6.ac ./data/pilot/pilot04/glozz_annotations/jhall/units/pilot04_06.ac
git mv ./data/pilot/pilot04/glozz_annotations/jhall/units/pilot04_7.ac ./data/pilot/pilot04/glozz_annotations/jhall/units/pilot04_07.ac
git mv ./data/pilot/pilot04/glozz_annotations/jhall/units/pilot04_8.ac ./data/pilot/pilot04/glozz_annotations/jhall/units/pilot04_08.ac
git mv ./data/pilot/pilot04/glozz_annotations/jhall/units/pilot04_9.ac ./data/pilot/pilot04/glozz_annotations/jhall/units/pilot04_09.ac

git mv ./data/pilot/pilot04/glozz_annotations/lpetersen/discourse/pilot04_10_petersen_d_15122012.aa ./data/pilot/pilot04/glozz_annotations/lpetersen/discourse/pilot04_10.aa
git mv ./data/pilot/pilot04/glozz_annotations/lpetersen/discourse/pilot04_11_petersen_d_2012013.aa ./data/pilot/pilot04/glozz_annotations/lpetersen/discourse/pilot04_11.aa
git mv ./data/pilot/pilot04/glozz_annotations/lpetersen/discourse/pilot04_1_petersen_d_13122012.aa ./data/pilot/pilot04/glozz_annotations/lpetersen/discourse/pilot04_01.aa
git mv ./data/pilot/pilot04/glozz_annotations/lpetersen/discourse/pilot04_2_petersen_d_13122012.aa ./data/pilot/pilot04/glozz_annotations/lpetersen/discourse/pilot04_02.aa
git mv ./data/pilot/pilot04/glozz_annotations/lpetersen/discourse/pilot04_4_petersen_d_14122012.aa ./data/pilot/pilot04/glozz_annotations/lpetersen/discourse/pilot04_04.aa
git mv ./data/pilot/pilot04/glozz_annotations/lpetersen/discourse/pilot04_5_petersen_d_14122012.aa ./data/pilot/pilot04/glozz_annotations/lpetersen/discourse/pilot04_05.aa
git mv ./data/pilot/pilot04/glozz_annotations/lpetersen/discourse/pilot04_7_petersen_d_15122012.aa ./data/pilot/pilot04/glozz_annotations/lpetersen/discourse/pilot04_07.aa
git mv ./data/pilot/pilot04/glozz_annotations/lpetersen/discourse/pilot04_8_petersen_d_15122012.aa ./data/pilot/pilot04/glozz_annotations/lpetersen/discourse/pilot04_08.aa

git mv ./data/pilot/pilot04/glozz_annotations/lpetersen/units/pilot04_10_petersen_u_13122012.aa ./data/pilot/pilot04/glozz_annotations/lpetersen/units/pilot04_10.aa
git mv ./data/pilot/pilot04/glozz_annotations/lpetersen/units/pilot04_11_petersen_u_2012013.aa ./data/pilot/pilot04/glozz_annotations/lpetersen/units/pilot04_11.aa
git mv ./data/pilot/pilot04/glozz_annotations/lpetersen/units/pilot04_1_petersen_u_12122012.aa ./data/pilot/pilot04/glozz_annotations/lpetersen/units/pilot04_01.aa
git mv ./data/pilot/pilot04/glozz_annotations/lpetersen/units/pilot04_2_petersen_u_12122012.aa ./data/pilot/pilot04/glozz_annotations/lpetersen/units/pilot04_02.aa
git mv ./data/pilot/pilot04/glozz_annotations/lpetersen/units/pilot04_4_petersen_u_12122012.aa ./data/pilot/pilot04/glozz_annotations/lpetersen/units/pilot04_04.aa
git mv ./data/pilot/pilot04/glozz_annotations/lpetersen/units/pilot04_5_petersen_u_13122012.aa ./data/pilot/pilot04/glozz_annotations/lpetersen/units/pilot04_05.aa
git mv ./data/pilot/pilot04/glozz_annotations/lpetersen/units/pilot04_7_petersen_u_13122012.aa ./data/pilot/pilot04/glozz_annotations/lpetersen/units/pilot04_07.aa
git mv ./data/pilot/pilot04/glozz_annotations/lpetersen/units/pilot04_8_petersen_u_13122012.aa ./data/pilot/pilot04/glozz_annotations/lpetersen/units/pilot04_08.aa

git mv ./data/pilot/pilot04/glozz_annotations/mhunt/discourse/pilot04_1.ac ./data/pilot/pilot04/glozz_annotations/mhunt/discourse/pilot04_01.ac
git mv ./data/pilot/pilot04/glozz_annotations/mhunt/discourse/pilot04_2.ac ./data/pilot/pilot04/glozz_annotations/mhunt/discourse/pilot04_02.ac
git mv ./data/pilot/pilot04/glozz_annotations/mhunt/discourse/pilot04_2_martha_d.aa ./data/pilot/pilot04/glozz_annotations/mhunt/discourse/pilot04_02.aa
git mv ./data/pilot/pilot04/glozz_annotations/mhunt/discourse/pilot04_3.ac ./data/pilot/pilot04/glozz_annotations/mhunt/discourse/pilot04_03.ac
git mv ./data/pilot/pilot04/glozz_annotations/mhunt/discourse/pilot04_3_martha_d.aa ./data/pilot/pilot04/glozz_annotations/mhunt/discourse/pilot04_03.aa
git mv ./data/pilot/pilot04/glozz_annotations/mhunt/discourse/pilot04_5_martha_d.aa ./data/pilot/pilot04/glozz_annotations/mhunt/discourse/pilot04_05.aa
git mv ./data/pilot/pilot04/glozz_annotations/mhunt/discourse/pilot04_6_martha_d.aa ./data/pilot/pilot04/glozz_annotations/mhunt/discourse/pilot04_06.aa
git mv ./data/pilot/pilot04/glozz_annotations/mhunt/discourse/pilot04_8_martha_d.aa ./data/pilot/pilot04/glozz_annotations/mhunt/discourse/pilot04_08.aa
git mv ./data/pilot/pilot04/glozz_annotations/mhunt/discourse/pilot04_9_martha_d.aa ./data/pilot/pilot04/glozz_annotations/mhunt/discourse/pilot04_09.aa

git mv ./data/pilot/pilot04/glozz_annotations/mhunt/units/pilot04_1.ac ./data/pilot/pilot04/glozz_annotations/mhunt/units/pilot04_01.ac
#git mv ./data/pilot/pilot04/glozz_annotations/mhunt/units/pilot04_10.ac ./data/pilot/pilot04/glozz_annotations/mhunt/units/pilot04_10.ac
#git mv ./data/pilot/pilot04/glozz_annotations/mhunt/units/pilot04_11.ac ./data/pilot/pilot04/glozz_annotations/mhunt/units/pilot04_11.ac
#git mv ./data/pilot/pilot04/glozz_annotations/mhunt/units/pilot04_12.ac ./data/pilot/pilot04/glozz_annotations/mhunt/units/pilot04_12.ac
git mv ./data/pilot/pilot04/glozz_annotations/mhunt/units/pilot04_2.ac ./data/pilot/pilot04/glozz_annotations/mhunt/units/pilot04_02.ac
git mv ./data/pilot/pilot04/glozz_annotations/mhunt/units/pilot04_2_martha_u.aa ./data/pilot/pilot04/glozz_annotations/mhunt/units/pilot04_02.aa
git mv ./data/pilot/pilot04/glozz_annotations/mhunt/units/pilot04_3.ac ./data/pilot/pilot04/glozz_annotations/mhunt/units/pilot04_03.ac
git mv ./data/pilot/pilot04/glozz_annotations/mhunt/units/pilot04_3_martha_u.aa ./data/pilot/pilot04/glozz_annotations/mhunt/units/pilot04_03.aa
git mv ./data/pilot/pilot04/glozz_annotations/mhunt/units/pilot04_4.ac ./data/pilot/pilot04/glozz_annotations/mhunt/units/pilot04_04.ac
git mv ./data/pilot/pilot04/glozz_annotations/mhunt/units/pilot04_5.ac ./data/pilot/pilot04/glozz_annotations/mhunt/units/pilot04_05.ac
git mv ./data/pilot/pilot04/glozz_annotations/mhunt/units/pilot04_5_martha_u.aa ./data/pilot/pilot04/glozz_annotations/mhunt/units/pilot04_05.aa
git mv ./data/pilot/pilot04/glozz_annotations/mhunt/units/pilot04_6.ac ./data/pilot/pilot04/glozz_annotations/mhunt/units/pilot04_06.ac
git mv ./data/pilot/pilot04/glozz_annotations/mhunt/units/pilot04_6_martha_u.aa ./data/pilot/pilot04/glozz_annotations/mhunt/units/pilot04_06.aa
git mv ./data/pilot/pilot04/glozz_annotations/mhunt/units/pilot04_7.ac ./data/pilot/pilot04/glozz_annotations/mhunt/units/pilot04_07.ac
git mv ./data/pilot/pilot04/glozz_annotations/mhunt/units/pilot04_8.ac ./data/pilot/pilot04/glozz_annotations/mhunt/units/pilot04_08.ac
git mv ./data/pilot/pilot04/glozz_annotations/mhunt/units/pilot04_8_martha_u.aa ./data/pilot/pilot04/glozz_annotations/mhunt/units/pilot04_08.aa
git mv ./data/pilot/pilot04/glozz_annotations/mhunt/units/pilot04_9.ac ./data/pilot/pilot04/glozz_annotations/mhunt/units/pilot04_09.ac
git mv ./data/pilot/pilot04/glozz_annotations/mhunt/units/pilot04_9_martha_u.aa ./data/pilot/pilot04/glozz_annotations/mhunt/units/pilot04_09.aa

git mv ./data/pilot/pilot04/glozz_preannotation/pilot04_1.ac ./data/pilot/pilot04/glozz_preannotation/pilot04_01.ac
#git mv ./data/pilot/pilot04/glozz_preannotation/pilot04_10.ac ./data/pilot/pilot04/glozz_preannotation/pilot04_10.ac
#git mv ./data/pilot/pilot04/glozz_preannotation/pilot04_11.ac ./data/pilot/pilot04/glozz_preannotation/pilot04_11.ac
#git mv ./data/pilot/pilot04/glozz_preannotation/pilot04_12.ac ./data/pilot/pilot04/glozz_preannotation/pilot04_12.ac
git mv ./data/pilot/pilot04/glozz_preannotation/pilot04_2.ac ./data/pilot/pilot04/glozz_preannotation/pilot04_02.ac
git mv ./data/pilot/pilot04/glozz_preannotation/pilot04_3.ac ./data/pilot/pilot04/glozz_preannotation/pilot04_03.ac
git mv ./data/pilot/pilot04/glozz_preannotation/pilot04_4.ac ./data/pilot/pilot04/glozz_preannotation/pilot04_04.ac
git mv ./data/pilot/pilot04/glozz_preannotation/pilot04_5.ac ./data/pilot/pilot04/glozz_preannotation/pilot04_05.ac
git mv ./data/pilot/pilot04/glozz_preannotation/pilot04_6.ac ./data/pilot/pilot04/glozz_preannotation/pilot04_06.ac
git mv ./data/pilot/pilot04/glozz_preannotation/pilot04_7.ac ./data/pilot/pilot04/glozz_preannotation/pilot04_07.ac
git mv ./data/pilot/pilot04/glozz_preannotation/pilot04_8.ac ./data/pilot/pilot04/glozz_preannotation/pilot04_08.ac
git mv ./data/pilot/pilot04/glozz_preannotation/pilot04_9.ac ./data/pilot/pilot04/glozz_preannotation/pilot04_09.ac

git mv ./data/pilot/pilot04/Gold/Unit/pilot04_10_petersen_u_13122012.aa ./data/pilot/pilot04/Gold/Unit/pilot04_10.aa
git mv ./data/pilot/pilot04/Gold/Unit/pilot04_11_petersen_u_2012013.aa ./data/pilot/pilot04/Gold/Unit/pilot04_11.aa
git mv ./data/pilot/pilot04/Gold/Unit/pilot04_12_joseph_u_2401.aa ./data/pilot/pilot04/Gold/Unit/pilot04_12.aa
git mv ./data/pilot/pilot04/Gold/Unit/pilot04_1_petersen_u_12122012.aa ./data/pilot/pilot04/Gold/Unit/pilot04_01.aa
git mv ./data/pilot/pilot04/Gold/Unit/pilot04_2_petersen_u_12122012.aa ./data/pilot/pilot04/Gold/Unit/pilot04_02.aa
git mv ./data/pilot/pilot04/Gold/Unit/pilot04_3_joseph_u_1212.aa ./data/pilot/pilot04/Gold/Unit/pilot04_03.aa
git mv ./data/pilot/pilot04/Gold/Unit/pilot04_4_petersen_u_12122012.aa ./data/pilot/pilot04/Gold/Unit/pilot04_04.aa
git mv ./data/pilot/pilot04/Gold/Unit/pilot04_5_petersen_u_13122012.aa ./data/pilot/pilot04/Gold/Unit/pilot04_05.aa
git mv ./data/pilot/pilot04/Gold/Unit/pilot04_6_joseph_u_1812.aa ./data/pilot/pilot04/Gold/Unit/pilot04_06.aa
git mv ./data/pilot/pilot04/Gold/Unit/pilot04_7_petersen_u_13122012.aa ./data/pilot/pilot04/Gold/Unit/pilot04_07.aa
git mv ./data/pilot/pilot04/Gold/Unit/pilot04_8_petersen_u_13122012.aa ./data/pilot/pilot04/Gold/Unit/pilot04_08.aa
git mv ./data/pilot/pilot04/Gold/Unit/pilot04_9_joseph_u_1812.aa ./data/pilot/pilot04/Gold/Unit/pilot04_09.aa

git mv ./data/pilot/pilot04/Gold/unit_pred_arg/pilot04_1.ac_petersen.seg ./data/pilot/pilot04/Gold/unit_pred_arg/pilot04_01.ac.seg
git mv ./data/pilot/pilot04/Gold/unit_pred_arg/pilot04_10.ac_petersen.seg ./data/pilot/pilot04/Gold/unit_pred_arg/pilot04_10.ac.seg
git mv ./data/pilot/pilot04/Gold/unit_pred_arg/pilot04_11.ac_petersen.seg ./data/pilot/pilot04/Gold/unit_pred_arg/pilot04_11.ac.seg
git mv ./data/pilot/pilot04/Gold/unit_pred_arg/pilot04_12.ac_joseph.seg ./data/pilot/pilot04/Gold/unit_pred_arg/pilot04_12.ac.seg
git mv ./data/pilot/pilot04/Gold/unit_pred_arg/pilot04_2.ac_petersen.seg ./data/pilot/pilot04/Gold/unit_pred_arg/pilot04_02.ac.seg
git mv ./data/pilot/pilot04/Gold/unit_pred_arg/pilot04_3.ac_joseph.seg ./data/pilot/pilot04/Gold/unit_pred_arg/pilot04_03.ac.seg
git mv ./data/pilot/pilot04/Gold/unit_pred_arg/pilot04_4.ac_petersen.seg ./data/pilot/pilot04/Gold/unit_pred_arg/pilot04_04.ac.seg
git mv ./data/pilot/pilot04/Gold/unit_pred_arg/pilot04_5.ac_petersen.seg ./data/pilot/pilot04/Gold/unit_pred_arg/pilot04_05.ac.seg
git mv ./data/pilot/pilot04/Gold/unit_pred_arg/pilot04_6.ac_joseph.seg ./data/pilot/pilot04/Gold/unit_pred_arg/pilot04_06.ac.seg
git mv ./data/pilot/pilot04/Gold/unit_pred_arg/pilot04_7.ac_petersen.seg ./data/pilot/pilot04/Gold/unit_pred_arg/pilot04_07.ac.seg
git mv ./data/pilot/pilot04/Gold/unit_pred_arg/pilot04_8.ac_petersen.seg ./data/pilot/pilot04/Gold/unit_pred_arg/pilot04_08.ac.seg
git mv ./data/pilot/pilot04/Gold/unit_pred_arg/pilot04_9.ac_joseph.seg ./data/pilot/pilot04/Gold/unit_pred_arg/pilot04_09.ac.seg

git mv ./data/pilot/pilot04/pred_arg_annotations/hjoseph/discourse/pilot04_1.ac_joseph.rel ./data/pilot/pilot04/pred_arg_annotations/hjoseph/discourse/pilot04_01.ac.rel
git mv ./data/pilot/pilot04/pred_arg_annotations/hjoseph/discourse/pilot04_10.ac_joseph.rel ./data/pilot/pilot04/pred_arg_annotations/hjoseph/discourse/pilot04_10.ac.rel
git mv ./data/pilot/pilot04/pred_arg_annotations/hjoseph/discourse/pilot04_3.ac_joseph.rel ./data/pilot/pilot04/pred_arg_annotations/hjoseph/discourse/pilot04_03.ac.rel
git mv ./data/pilot/pilot04/pred_arg_annotations/hjoseph/discourse/pilot04_4.ac_joseph.rel ./data/pilot/pilot04/pred_arg_annotations/hjoseph/discourse/pilot04_04.ac.rel
git mv ./data/pilot/pilot04/pred_arg_annotations/hjoseph/discourse/pilot04_6.ac_joseph.rel ./data/pilot/pilot04/pred_arg_annotations/hjoseph/discourse/pilot04_06.ac.rel
git mv ./data/pilot/pilot04/pred_arg_annotations/hjoseph/discourse/pilot04_7.ac_joseph.rel ./data/pilot/pilot04/pred_arg_annotations/hjoseph/discourse/pilot04_07.ac.rel
git mv ./data/pilot/pilot04/pred_arg_annotations/hjoseph/discourse/pilot04_9.ac_joseph.rel ./data/pilot/pilot04/pred_arg_annotations/hjoseph/discourse/pilot04_09.ac.rel

git mv ./data/pilot/pilot04/pred_arg_annotations/hjoseph/unit/pilot04_1.ac_joseph.seg ./data/pilot/pilot04/pred_arg_annotations/hjoseph/unit/pilot04_01.ac.seg
git mv ./data/pilot/pilot04/pred_arg_annotations/hjoseph/unit/pilot04_10.ac_joseph.seg ./data/pilot/pilot04/pred_arg_annotations/hjoseph/unit/pilot04_10.ac.seg
git mv ./data/pilot/pilot04/pred_arg_annotations/hjoseph/unit/pilot04_3.ac_joseph.seg ./data/pilot/pilot04/pred_arg_annotations/hjoseph/unit/pilot04_03.ac.seg
git mv ./data/pilot/pilot04/pred_arg_annotations/hjoseph/unit/pilot04_4.ac_joseph.seg ./data/pilot/pilot04/pred_arg_annotations/hjoseph/unit/pilot04_04.ac.seg
git mv ./data/pilot/pilot04/pred_arg_annotations/hjoseph/unit/pilot04_6.ac_joseph.seg ./data/pilot/pilot04/pred_arg_annotations/hjoseph/unit/pilot04_06.ac.seg
git mv ./data/pilot/pilot04/pred_arg_annotations/hjoseph/unit/pilot04_7.ac_joseph.seg ./data/pilot/pilot04/pred_arg_annotations/hjoseph/unit/pilot04_07.ac.seg
git mv ./data/pilot/pilot04/pred_arg_annotations/hjoseph/unit/pilot04_9.ac_joseph.seg ./data/pilot/pilot04/pred_arg_annotations/hjoseph/unit/pilot04_09.ac.seg

git mv ./data/pilot/pilot04/pred_arg_annotations/lpetersen/discourse/pilot04_1.ac_petersen.rel ./data/pilot/pilot04/pred_arg_annotations/lpetersen/discourse/pilot04_01.ac.rel
git mv ./data/pilot/pilot04/pred_arg_annotations/lpetersen/discourse/pilot04_10.ac_petersen.rel ./data/pilot/pilot04/pred_arg_annotations/lpetersen/discourse/pilot04_10.ac.rel
git mv ./data/pilot/pilot04/pred_arg_annotations/lpetersen/discourse/pilot04_2.ac_petersen.rel ./data/pilot/pilot04/pred_arg_annotations/lpetersen/discourse/pilot04_02.ac.rel
git mv ./data/pilot/pilot04/pred_arg_annotations/lpetersen/discourse/pilot04_4.ac_petersen.rel ./data/pilot/pilot04/pred_arg_annotations/lpetersen/discourse/pilot04_04.ac.rel
git mv ./data/pilot/pilot04/pred_arg_annotations/lpetersen/discourse/pilot04_5.ac_petersen.rel ./data/pilot/pilot04/pred_arg_annotations/lpetersen/discourse/pilot04_05.ac.rel
git mv ./data/pilot/pilot04/pred_arg_annotations/lpetersen/discourse/pilot04_7.ac_petersen.rel ./data/pilot/pilot04/pred_arg_annotations/lpetersen/discourse/pilot04_07.ac.rel
git mv ./data/pilot/pilot04/pred_arg_annotations/lpetersen/discourse/pilot04_8.ac_petersen.rel ./data/pilot/pilot04/pred_arg_annotations/lpetersen/discourse/pilot04_08.ac.rel

git mv ./data/pilot/pilot04/pred_arg_annotations/lpetersen/unit/pilot04_1.ac_petersen.seg ./data/pilot/pilot04/pred_arg_annotations/lpetersen/unit/pilot04_01.ac.seg
git mv ./data/pilot/pilot04/pred_arg_annotations/lpetersen/unit/pilot04_10.ac_petersen.seg ./data/pilot/pilot04/pred_arg_annotations/lpetersen/unit/pilot04_10.ac.seg
git mv ./data/pilot/pilot04/pred_arg_annotations/lpetersen/unit/pilot04_2.ac_petersen.seg ./data/pilot/pilot04/pred_arg_annotations/lpetersen/unit/pilot04_02.ac.seg
git mv ./data/pilot/pilot04/pred_arg_annotations/lpetersen/unit/pilot04_4.ac_petersen.seg ./data/pilot/pilot04/pred_arg_annotations/lpetersen/unit/pilot04_04.ac.seg
git mv ./data/pilot/pilot04/pred_arg_annotations/lpetersen/unit/pilot04_5.ac_petersen.seg ./data/pilot/pilot04/pred_arg_annotations/lpetersen/unit/pilot04_05.ac.seg
git mv ./data/pilot/pilot04/pred_arg_annotations/lpetersen/unit/pilot04_7.ac_petersen.seg ./data/pilot/pilot04/pred_arg_annotations/lpetersen/unit/pilot04_07.ac.seg
git mv ./data/pilot/pilot04/pred_arg_annotations/lpetersen/unit/pilot04_8.ac_petersen.seg ./data/pilot/pilot04/pred_arg_annotations/lpetersen/unit/pilot04_08.ac.seg

git mv ./data/pilot/pilot14/glozz_annotations/hjoseph/discourse/pilot14_10_joseph_d_0801.aa ./data/pilot/pilot14/glozz_annotations/hjoseph/discourse/pilot14_10.aa
git mv ./data/pilot/pilot14/glozz_annotations/hjoseph/discourse/pilot14_11_joseph_d_2801.aa ./data/pilot/pilot14/glozz_annotations/hjoseph/discourse/pilot14_11.aa
git mv ./data/pilot/pilot14/glozz_annotations/hjoseph/discourse/pilot14_1_joseph_d_2012.aa ./data/pilot/pilot14/glozz_annotations/hjoseph/discourse/pilot14_01.aa
git mv ./data/pilot/pilot14/glozz_annotations/hjoseph/discourse/pilot14_3_joseph_d_2112.aa ./data/pilot/pilot14/glozz_annotations/hjoseph/discourse/pilot14_03.aa
git mv ./data/pilot/pilot14/glozz_annotations/hjoseph/discourse/pilot14_4_joseph_d_0801.aa ./data/pilot/pilot14/glozz_annotations/hjoseph/discourse/pilot14_04.aa
git mv ./data/pilot/pilot14/glozz_annotations/hjoseph/discourse/pilot14_6_joseph_d_0801.aa ./data/pilot/pilot14/glozz_annotations/hjoseph/discourse/pilot14_06.aa
git mv ./data/pilot/pilot14/glozz_annotations/hjoseph/discourse/pilot14_7_joseph_d_0801.aa ./data/pilot/pilot14/glozz_annotations/hjoseph/discourse/pilot14_07.aa
git mv ./data/pilot/pilot14/glozz_annotations/hjoseph/discourse/pilot14_9_joseph_d_0801.aa ./data/pilot/pilot14/glozz_annotations/hjoseph/discourse/pilot14_09.aa

git mv ./data/pilot/pilot14/glozz_annotations/hjoseph/units/pilot14_10_joseph_u_0801.aa ./data/pilot/pilot14/glozz_annotations/hjoseph/units/pilot14_10.aa
git mv ./data/pilot/pilot14/glozz_annotations/hjoseph/units/pilot14_11_joseph_u_2801.aa ./data/pilot/pilot14/glozz_annotations/hjoseph/units/pilot14_11.aa
git mv ./data/pilot/pilot14/glozz_annotations/hjoseph/units/pilot14_1_joseph_u_2012.aa ./data/pilot/pilot14/glozz_annotations/hjoseph/units/pilot14_01.aa
git mv ./data/pilot/pilot14/glozz_annotations/hjoseph/units/pilot14_3_joseph_u_2212.aa ./data/pilot/pilot14/glozz_annotations/hjoseph/units/pilot14_03.aa
git mv ./data/pilot/pilot14/glozz_annotations/hjoseph/units/pilot14_4_joseph_u_0801.aa ./data/pilot/pilot14/glozz_annotations/hjoseph/units/pilot14_04.aa
git mv ./data/pilot/pilot14/glozz_annotations/hjoseph/units/pilot14_6_joseph_u_0801.aa ./data/pilot/pilot14/glozz_annotations/hjoseph/units/pilot14_06.aa
git mv ./data/pilot/pilot14/glozz_annotations/hjoseph/units/pilot14_7_joseph_u_0801.aa ./data/pilot/pilot14/glozz_annotations/hjoseph/units/pilot14_07.aa
git mv ./data/pilot/pilot14/glozz_annotations/hjoseph/units/pilot14_9_joseph_u_0801.aa ./data/pilot/pilot14/glozz_annotations/hjoseph/units/pilot14_09.aa

git mv ./data/pilot/pilot14/glozz_annotations/jhall/discourse/pilot14_1.ac ./data/pilot/pilot14/glozz_annotations/jhall/discourse/pilot14_01.ac
#git mv ./data/pilot/pilot14/glozz_annotations/jhall/discourse/pilot14_10.ac ./data/pilot/pilot14/glozz_annotations/jhall/discourse/pilot14_10.ac
#git mv ./data/pilot/pilot14/glozz_annotations/jhall/discourse/pilot14_11.ac ./data/pilot/pilot14/glozz_annotations/jhall/discourse/pilot14_11.ac
#git mv ./data/pilot/pilot14/glozz_annotations/jhall/discourse/pilot14_12.ac ./data/pilot/pilot14/glozz_annotations/jhall/discourse/pilot14_12.ac
git mv ./data/pilot/pilot14/glozz_annotations/jhall/discourse/pilot14_2.ac ./data/pilot/pilot14/glozz_annotations/jhall/discourse/pilot14_02.ac
git mv ./data/pilot/pilot14/glozz_annotations/jhall/discourse/pilot14_3.ac ./data/pilot/pilot14/glozz_annotations/jhall/discourse/pilot14_03.ac
git mv ./data/pilot/pilot14/glozz_annotations/jhall/discourse/pilot14_4.ac ./data/pilot/pilot14/glozz_annotations/jhall/discourse/pilot14_04.ac
git mv ./data/pilot/pilot14/glozz_annotations/jhall/discourse/pilot14_5.ac ./data/pilot/pilot14/glozz_annotations/jhall/discourse/pilot14_05.ac
git mv ./data/pilot/pilot14/glozz_annotations/jhall/discourse/pilot14_6.ac ./data/pilot/pilot14/glozz_annotations/jhall/discourse/pilot14_06.ac
git mv ./data/pilot/pilot14/glozz_annotations/jhall/discourse/pilot14_7.ac ./data/pilot/pilot14/glozz_annotations/jhall/discourse/pilot14_07.ac
git mv ./data/pilot/pilot14/glozz_annotations/jhall/discourse/pilot14_8.ac ./data/pilot/pilot14/glozz_annotations/jhall/discourse/pilot14_08.ac
git mv ./data/pilot/pilot14/glozz_annotations/jhall/discourse/pilot14_9.ac ./data/pilot/pilot14/glozz_annotations/jhall/discourse/pilot14_09.ac

git mv ./data/pilot/pilot14/glozz_annotations/jhall/units/pilot14_1.ac ./data/pilot/pilot14/glozz_annotations/jhall/units/pilot14_01.ac
#git mv ./data/pilot/pilot14/glozz_annotations/jhall/units/pilot14_10.ac ./data/pilot/pilot14/glozz_annotations/jhall/units/pilot14_10.ac
#git mv ./data/pilot/pilot14/glozz_annotations/jhall/units/pilot14_11.ac ./data/pilot/pilot14/glozz_annotations/jhall/units/pilot14_11.ac
#git mv ./data/pilot/pilot14/glozz_annotations/jhall/units/pilot14_12.ac ./data/pilot/pilot14/glozz_annotations/jhall/units/pilot14_12.ac
git mv ./data/pilot/pilot14/glozz_annotations/jhall/units/pilot14_2.ac ./data/pilot/pilot14/glozz_annotations/jhall/units/pilot14_02.ac
git mv ./data/pilot/pilot14/glozz_annotations/jhall/units/pilot14_3.ac ./data/pilot/pilot14/glozz_annotations/jhall/units/pilot14_03.ac
git mv ./data/pilot/pilot14/glozz_annotations/jhall/units/pilot14_4.ac ./data/pilot/pilot14/glozz_annotations/jhall/units/pilot14_04.ac
git mv ./data/pilot/pilot14/glozz_annotations/jhall/units/pilot14_5.ac ./data/pilot/pilot14/glozz_annotations/jhall/units/pilot14_05.ac
git mv ./data/pilot/pilot14/glozz_annotations/jhall/units/pilot14_6.ac ./data/pilot/pilot14/glozz_annotations/jhall/units/pilot14_06.ac
git mv ./data/pilot/pilot14/glozz_annotations/jhall/units/pilot14_7.ac ./data/pilot/pilot14/glozz_annotations/jhall/units/pilot14_07.ac
git mv ./data/pilot/pilot14/glozz_annotations/jhall/units/pilot14_8.ac ./data/pilot/pilot14/glozz_annotations/jhall/units/pilot14_08.ac
git mv ./data/pilot/pilot14/glozz_annotations/jhall/units/pilot14_9.ac ./data/pilot/pilot14/glozz_annotations/jhall/units/pilot14_09.ac

git mv ./data/pilot/pilot14/glozz_annotations/lpetersen/discourse/pilot14_11_petersen_d_2012013.aa ./data/pilot/pilot14/glozz_annotations/lpetersen/discourse/pilot14_11.aa
git mv ./data/pilot/pilot14/glozz_annotations/lpetersen/discourse/pilot14_12_petersen_d_2012013.aa ./data/pilot/pilot14/glozz_annotations/lpetersen/discourse/pilot14_12.aa
git mv ./data/pilot/pilot14/glozz_annotations/lpetersen/discourse/pilot14_2_petersen_d_18122012.aa ./data/pilot/pilot14/glozz_annotations/lpetersen/discourse/pilot14_02.aa
git mv ./data/pilot/pilot14/glozz_annotations/lpetersen/discourse/pilot14_3_petersen_d_18122012.aa ./data/pilot/pilot14/glozz_annotations/lpetersen/discourse/pilot14_03.aa
git mv ./data/pilot/pilot14/glozz_annotations/lpetersen/discourse/pilot14_5_petersen_d_18122012.aa ./data/pilot/pilot14/glozz_annotations/lpetersen/discourse/pilot14_05.aa
git mv ./data/pilot/pilot14/glozz_annotations/lpetersen/discourse/pilot14_6_petersen_d_20122012.aa ./data/pilot/pilot14/glozz_annotations/lpetersen/discourse/pilot14_06.aa
git mv ./data/pilot/pilot14/glozz_annotations/lpetersen/discourse/pilot14_8_petersen_d_20122012.aa ./data/pilot/pilot14/glozz_annotations/lpetersen/discourse/pilot14_08.aa
git mv ./data/pilot/pilot14/glozz_annotations/lpetersen/discourse/pilot14_9_petersen_d_20122012.aa ./data/pilot/pilot14/glozz_annotations/lpetersen/discourse/pilot14_09.aa

git mv ./data/pilot/pilot14/glozz_annotations/lpetersen/units/pilot14_11_petersen_u_2012013.aa ./data/pilot/pilot14/glozz_annotations/lpetersen/units/pilot14_11.aa
git mv ./data/pilot/pilot14/glozz_annotations/lpetersen/units/pilot14_12_petersen_u_2012013.aa ./data/pilot/pilot14/glozz_annotations/lpetersen/units/pilot14_12.aa
git mv ./data/pilot/pilot14/glozz_annotations/lpetersen/units/pilot14_2_petersen_u_17122012.aa ./data/pilot/pilot14/glozz_annotations/lpetersen/units/pilot14_02.aa
git mv ./data/pilot/pilot14/glozz_annotations/lpetersen/units/pilot14_3_petersen_u_17122012.aa ./data/pilot/pilot14/glozz_annotations/lpetersen/units/pilot14_03.aa
git mv ./data/pilot/pilot14/glozz_annotations/lpetersen/units/pilot14_5_petersen_u_17122012.aa ./data/pilot/pilot14/glozz_annotations/lpetersen/units/pilot14_05.aa
git mv ./data/pilot/pilot14/glozz_annotations/lpetersen/units/pilot14_6_petersen_u_17122012.aa ./data/pilot/pilot14/glozz_annotations/lpetersen/units/pilot14_06.aa
git mv ./data/pilot/pilot14/glozz_annotations/lpetersen/units/pilot14_8_petersen_u_17122012.aa ./data/pilot/pilot14/glozz_annotations/lpetersen/units/pilot14_08.aa
git mv ./data/pilot/pilot14/glozz_annotations/lpetersen/units/pilot14_9_petersen_u_17122012.aa ./data/pilot/pilot14/glozz_annotations/lpetersen/units/pilot14_09.aa

git mv ./data/pilot/pilot14/glozz_annotations/mhunt/discourse/pilot14_1.ac ./data/pilot/pilot14/glozz_annotations/mhunt/discourse/pilot14_01.ac
#git mv ./data/pilot/pilot14/glozz_annotations/mhunt/discourse/pilot14_10.ac ./data/pilot/pilot14/glozz_annotations/mhunt/discourse/pilot14_10.ac
#git mv ./data/pilot/pilot14/glozz_annotations/mhunt/discourse/pilot14_11.ac ./data/pilot/pilot14/glozz_annotations/mhunt/discourse/pilot14_11.ac
#git mv ./data/pilot/pilot14/glozz_annotations/mhunt/discourse/pilot14_12.ac ./data/pilot/pilot14/glozz_annotations/mhunt/discourse/pilot14_12.ac
git mv ./data/pilot/pilot14/glozz_annotations/mhunt/discourse/pilot14_2.ac ./data/pilot/pilot14/glozz_annotations/mhunt/discourse/pilot14_02.ac
git mv ./data/pilot/pilot14/glozz_annotations/mhunt/discourse/pilot14_3.ac ./data/pilot/pilot14/glozz_annotations/mhunt/discourse/pilot14_03.ac
git mv ./data/pilot/pilot14/glozz_annotations/mhunt/discourse/pilot14_4.ac ./data/pilot/pilot14/glozz_annotations/mhunt/discourse/pilot14_04.ac
git mv ./data/pilot/pilot14/glozz_annotations/mhunt/discourse/pilot14_5.ac ./data/pilot/pilot14/glozz_annotations/mhunt/discourse/pilot14_05.ac
git mv ./data/pilot/pilot14/glozz_annotations/mhunt/discourse/pilot14_6.ac ./data/pilot/pilot14/glozz_annotations/mhunt/discourse/pilot14_06.ac
git mv ./data/pilot/pilot14/glozz_annotations/mhunt/discourse/pilot14_7.ac ./data/pilot/pilot14/glozz_annotations/mhunt/discourse/pilot14_07.ac
git mv ./data/pilot/pilot14/glozz_annotations/mhunt/discourse/pilot14_8.ac ./data/pilot/pilot14/glozz_annotations/mhunt/discourse/pilot14_08.ac
git mv ./data/pilot/pilot14/glozz_annotations/mhunt/discourse/pilot14_9.ac ./data/pilot/pilot14/glozz_annotations/mhunt/discourse/pilot14_09.ac

git mv ./data/pilot/pilot14/glozz_annotations/mhunt/units/pilot14_1.ac ./data/pilot/pilot14/glozz_annotations/mhunt/units/pilot14_01.ac
#git mv ./data/pilot/pilot14/glozz_annotations/mhunt/units/pilot14_10.ac ./data/pilot/pilot14/glozz_annotations/mhunt/units/pilot14_10.ac
#git mv ./data/pilot/pilot14/glozz_annotations/mhunt/units/pilot14_11.ac ./data/pilot/pilot14/glozz_annotations/mhunt/units/pilot14_11.ac
#git mv ./data/pilot/pilot14/glozz_annotations/mhunt/units/pilot14_12.ac ./data/pilot/pilot14/glozz_annotations/mhunt/units/pilot14_12.ac
git mv ./data/pilot/pilot14/glozz_annotations/mhunt/units/pilot14_2.ac ./data/pilot/pilot14/glozz_annotations/mhunt/units/pilot14_02.ac
git mv ./data/pilot/pilot14/glozz_annotations/mhunt/units/pilot14_3.ac ./data/pilot/pilot14/glozz_annotations/mhunt/units/pilot14_03.ac
git mv ./data/pilot/pilot14/glozz_annotations/mhunt/units/pilot14_4.ac ./data/pilot/pilot14/glozz_annotations/mhunt/units/pilot14_04.ac
git mv ./data/pilot/pilot14/glozz_annotations/mhunt/units/pilot14_5.ac ./data/pilot/pilot14/glozz_annotations/mhunt/units/pilot14_05.ac
git mv ./data/pilot/pilot14/glozz_annotations/mhunt/units/pilot14_6.ac ./data/pilot/pilot14/glozz_annotations/mhunt/units/pilot14_06.ac
git mv ./data/pilot/pilot14/glozz_annotations/mhunt/units/pilot14_7.ac ./data/pilot/pilot14/glozz_annotations/mhunt/units/pilot14_07.ac
git mv ./data/pilot/pilot14/glozz_annotations/mhunt/units/pilot14_8.ac ./data/pilot/pilot14/glozz_annotations/mhunt/units/pilot14_08.ac
git mv ./data/pilot/pilot14/glozz_annotations/mhunt/units/pilot14_9.ac ./data/pilot/pilot14/glozz_annotations/mhunt/units/pilot14_09.ac

git mv ./data/pilot/pilot14/glozz_preannotation/pilot14_1.ac ./data/pilot/pilot14/glozz_preannotation/pilot14_01.ac
#git mv ./data/pilot/pilot14/glozz_preannotation/pilot14_10.ac ./data/pilot/pilot14/glozz_preannotation/pilot14_10.ac
#git mv ./data/pilot/pilot14/glozz_preannotation/pilot14_11.ac ./data/pilot/pilot14/glozz_preannotation/pilot14_11.ac
#git mv ./data/pilot/pilot14/glozz_preannotation/pilot14_12.ac ./data/pilot/pilot14/glozz_preannotation/pilot14_12.ac
git mv ./data/pilot/pilot14/glozz_preannotation/pilot14_2.ac ./data/pilot/pilot14/glozz_preannotation/pilot14_02.ac
git mv ./data/pilot/pilot14/glozz_preannotation/pilot14_3.ac ./data/pilot/pilot14/glozz_preannotation/pilot14_03.ac
git mv ./data/pilot/pilot14/glozz_preannotation/pilot14_4.ac ./data/pilot/pilot14/glozz_preannotation/pilot14_04.ac
git mv ./data/pilot/pilot14/glozz_preannotation/pilot14_5.ac ./data/pilot/pilot14/glozz_preannotation/pilot14_05.ac
git mv ./data/pilot/pilot14/glozz_preannotation/pilot14_6.ac ./data/pilot/pilot14/glozz_preannotation/pilot14_06.ac
git mv ./data/pilot/pilot14/glozz_preannotation/pilot14_7.ac ./data/pilot/pilot14/glozz_preannotation/pilot14_07.ac
git mv ./data/pilot/pilot14/glozz_preannotation/pilot14_8.ac ./data/pilot/pilot14/glozz_preannotation/pilot14_08.ac
git mv ./data/pilot/pilot14/glozz_preannotation/pilot14_9.ac ./data/pilot/pilot14/glozz_preannotation/pilot14_09.ac

git mv ./data/pilot/pilot14/Gold/Unit/pilot14_10_joseph_u_0801.aa ./data/pilot/pilot14/Gold/Unit/pilot14_10.aa
git mv ./data/pilot/pilot14/Gold/Unit/pilot14_11_petersen_u_2012013.aa ./data/pilot/pilot14/Gold/Unit/pilot14_11.aa
git mv ./data/pilot/pilot14/Gold/Unit/pilot14_12_petersen_u_2012013.aa ./data/pilot/pilot14/Gold/Unit/pilot14_12.aa
git mv ./data/pilot/pilot14/Gold/Unit/pilot14_1_joseph_u_2012.aa ./data/pilot/pilot14/Gold/Unit/pilot14_01.aa
git mv ./data/pilot/pilot14/Gold/Unit/pilot14_2_petersen_u_17122012.aa ./data/pilot/pilot14/Gold/Unit/pilot14_02.aa
git mv ./data/pilot/pilot14/Gold/Unit/pilot14_3_petersen_u_17122012.aa ./data/pilot/pilot14/Gold/Unit/pilot14_03.aa
git mv ./data/pilot/pilot14/Gold/Unit/pilot14_4_joseph_u_0801.aa ./data/pilot/pilot14/Gold/Unit/pilot14_04.aa
git mv ./data/pilot/pilot14/Gold/Unit/pilot14_5_petersen_u_17122012.aa ./data/pilot/pilot14/Gold/Unit/pilot14_05.aa
git mv ./data/pilot/pilot14/Gold/Unit/pilot14_6_petersen_u_17122012.aa ./data/pilot/pilot14/Gold/Unit/pilot14_06.aa
git mv ./data/pilot/pilot14/Gold/Unit/pilot14_7_joseph_u_0801.aa ./data/pilot/pilot14/Gold/Unit/pilot14_07.aa
git mv ./data/pilot/pilot14/Gold/Unit/pilot14_8_petersen_u_17122012.aa ./data/pilot/pilot14/Gold/Unit/pilot14_08.aa
git mv ./data/pilot/pilot14/Gold/Unit/pilot14_9_petersen_u_17122012.aa ./data/pilot/pilot14/Gold/Unit/pilot14_09.aa

git mv ./data/pilot/pilot14/Gold/Unit_pred_arg/pilot14_1.ac_joseph.seg ./data/pilot/pilot14/Gold/Unit_pred_arg/pilot14_01.ac.seg
git mv ./data/pilot/pilot14/Gold/Unit_pred_arg/pilot14_10.ac_joseph.seg ./data/pilot/pilot14/Gold/Unit_pred_arg/pilot14_10.ac.seg
git mv ./data/pilot/pilot14/Gold/Unit_pred_arg/pilot14_11.ac_petersen.seg ./data/pilot/pilot14/Gold/Unit_pred_arg/pilot14_11.ac.seg
git mv ./data/pilot/pilot14/Gold/Unit_pred_arg/pilot14_12.ac_petersen.seg ./data/pilot/pilot14/Gold/Unit_pred_arg/pilot14_12.ac.seg
git mv ./data/pilot/pilot14/Gold/Unit_pred_arg/pilot14_2.ac_petersen.seg ./data/pilot/pilot14/Gold/Unit_pred_arg/pilot14_02.ac.seg
git mv ./data/pilot/pilot14/Gold/Unit_pred_arg/pilot14_3.ac_petersen.seg ./data/pilot/pilot14/Gold/Unit_pred_arg/pilot14_03.ac.seg
git mv ./data/pilot/pilot14/Gold/Unit_pred_arg/pilot14_4.ac_joseph.seg ./data/pilot/pilot14/Gold/Unit_pred_arg/pilot14_04.ac.seg
git mv ./data/pilot/pilot14/Gold/Unit_pred_arg/pilot14_5.ac_petersen.seg ./data/pilot/pilot14/Gold/Unit_pred_arg/pilot14_05.ac.seg
git mv ./data/pilot/pilot14/Gold/Unit_pred_arg/pilot14_6.ac_petersen.seg ./data/pilot/pilot14/Gold/Unit_pred_arg/pilot14_06.ac.seg
git mv ./data/pilot/pilot14/Gold/Unit_pred_arg/pilot14_7.ac_joseph.seg ./data/pilot/pilot14/Gold/Unit_pred_arg/pilot14_07.ac.seg
git mv ./data/pilot/pilot14/Gold/Unit_pred_arg/pilot14_8.ac_petersen.seg ./data/pilot/pilot14/Gold/Unit_pred_arg/pilot14_08.ac.seg
git mv ./data/pilot/pilot14/Gold/Unit_pred_arg/pilot14_9.ac_petersen.seg ./data/pilot/pilot14/Gold/Unit_pred_arg/pilot14_09.ac.seg

git mv ./data/pilot/pilot14/pred_arg_annotations/joseph/discourse/pilot14_1.ac_joseph.rel ./data/pilot/pilot14/pred_arg_annotations/joseph/discourse/pilot14_01.ac.rel
git mv ./data/pilot/pilot14/pred_arg_annotations/joseph/discourse/pilot14_10.ac_joseph.rel ./data/pilot/pilot14/pred_arg_annotations/joseph/discourse/pilot14_10.ac.rel
git mv ./data/pilot/pilot14/pred_arg_annotations/joseph/discourse/pilot14_3.ac_joseph.rel ./data/pilot/pilot14/pred_arg_annotations/joseph/discourse/pilot14_03.ac.rel
git mv ./data/pilot/pilot14/pred_arg_annotations/joseph/discourse/pilot14_4.ac_joseph.rel ./data/pilot/pilot14/pred_arg_annotations/joseph/discourse/pilot14_04.ac.rel
git mv ./data/pilot/pilot14/pred_arg_annotations/joseph/discourse/pilot14_6.ac_joseph.rel ./data/pilot/pilot14/pred_arg_annotations/joseph/discourse/pilot14_06.ac.rel
git mv ./data/pilot/pilot14/pred_arg_annotations/joseph/discourse/pilot14_7.ac_joseph.rel ./data/pilot/pilot14/pred_arg_annotations/joseph/discourse/pilot14_07.ac.rel
git mv ./data/pilot/pilot14/pred_arg_annotations/joseph/discourse/pilot14_9.ac_joseph.rel ./data/pilot/pilot14/pred_arg_annotations/joseph/discourse/pilot14_09.ac.rel

git mv ./data/pilot/pilot14/pred_arg_annotations/joseph/unit/pilot14_1.ac_joseph.seg ./data/pilot/pilot14/pred_arg_annotations/joseph/unit/pilot14_01.ac.seg
git mv ./data/pilot/pilot14/pred_arg_annotations/joseph/unit/pilot14_10.ac_joseph.seg ./data/pilot/pilot14/pred_arg_annotations/joseph/unit/pilot14_10.ac.seg
git mv ./data/pilot/pilot14/pred_arg_annotations/joseph/unit/pilot14_3.ac_joseph.seg ./data/pilot/pilot14/pred_arg_annotations/joseph/unit/pilot14_03.ac.seg
git mv ./data/pilot/pilot14/pred_arg_annotations/joseph/unit/pilot14_4.ac_joseph.seg ./data/pilot/pilot14/pred_arg_annotations/joseph/unit/pilot14_04.ac.seg
git mv ./data/pilot/pilot14/pred_arg_annotations/joseph/unit/pilot14_6.ac_joseph.seg ./data/pilot/pilot14/pred_arg_annotations/joseph/unit/pilot14_06.ac.seg
git mv ./data/pilot/pilot14/pred_arg_annotations/joseph/unit/pilot14_7.ac_joseph.seg ./data/pilot/pilot14/pred_arg_annotations/joseph/unit/pilot14_07.ac.seg
git mv ./data/pilot/pilot14/pred_arg_annotations/joseph/unit/pilot14_9.ac_joseph.seg ./data/pilot/pilot14/pred_arg_annotations/joseph/unit/pilot14_09.ac.seg

git mv ./data/pilot/pilot14/pred_arg_annotations/petersen/discourse/pilot14_11.ac_petersen.rel ./data/pilot/pilot14/pred_arg_annotations/petersen/discourse/pilot14_11.ac.rel
git mv ./data/pilot/pilot14/pred_arg_annotations/petersen/discourse/pilot14_12.ac_petersen.rel ./data/pilot/pilot14/pred_arg_annotations/petersen/discourse/pilot14_12.ac.rel
git mv ./data/pilot/pilot14/pred_arg_annotations/petersen/discourse/pilot14_2.ac_petersen.rel ./data/pilot/pilot14/pred_arg_annotations/petersen/discourse/pilot14_02.ac.rel
git mv ./data/pilot/pilot14/pred_arg_annotations/petersen/discourse/pilot14_3.ac_petersen.rel ./data/pilot/pilot14/pred_arg_annotations/petersen/discourse/pilot14_03.ac.rel
git mv ./data/pilot/pilot14/pred_arg_annotations/petersen/discourse/pilot14_5.ac_petersen.rel ./data/pilot/pilot14/pred_arg_annotations/petersen/discourse/pilot14_05.ac.rel
git mv ./data/pilot/pilot14/pred_arg_annotations/petersen/discourse/pilot14_6.ac_petersen.rel ./data/pilot/pilot14/pred_arg_annotations/petersen/discourse/pilot14_06.ac.rel
git mv ./data/pilot/pilot14/pred_arg_annotations/petersen/discourse/pilot14_8.ac_petersen.rel ./data/pilot/pilot14/pred_arg_annotations/petersen/discourse/pilot14_08.ac.rel
git mv ./data/pilot/pilot14/pred_arg_annotations/petersen/discourse/pilot14_9.ac_petersen.rel ./data/pilot/pilot14/pred_arg_annotations/petersen/discourse/pilot14_09.ac.rel

git mv ./data/pilot/pilot14/pred_arg_annotations/petersen/unit/pilot14_11.ac_petersen.seg ./data/pilot/pilot14/pred_arg_annotations/petersen/unit/pilot14_11.ac.seg
git mv ./data/pilot/pilot14/pred_arg_annotations/petersen/unit/pilot14_12.ac_petersen.seg ./data/pilot/pilot14/pred_arg_annotations/petersen/unit/pilot14_12.ac.seg
git mv ./data/pilot/pilot14/pred_arg_annotations/petersen/unit/pilot14_2.ac_petersen.seg ./data/pilot/pilot14/pred_arg_annotations/petersen/unit/pilot14_02.ac.seg
git mv ./data/pilot/pilot14/pred_arg_annotations/petersen/unit/pilot14_3.ac_petersen.seg ./data/pilot/pilot14/pred_arg_annotations/petersen/unit/pilot14_03.ac.seg
git mv ./data/pilot/pilot14/pred_arg_annotations/petersen/unit/pilot14_5.ac_petersen.seg ./data/pilot/pilot14/pred_arg_annotations/petersen/unit/pilot14_05.ac.seg
git mv ./data/pilot/pilot14/pred_arg_annotations/petersen/unit/pilot14_6.ac_petersen.seg ./data/pilot/pilot14/pred_arg_annotations/petersen/unit/pilot14_06.ac.seg
git mv ./data/pilot/pilot14/pred_arg_annotations/petersen/unit/pilot14_8.ac_petersen.seg ./data/pilot/pilot14/pred_arg_annotations/petersen/unit/pilot14_08.ac.seg
git mv ./data/pilot/pilot14/pred_arg_annotations/petersen/unit/pilot14_9.ac_petersen.seg ./data/pilot/pilot14/pred_arg_annotations/petersen/unit/pilot14_09.ac.seg

git mv ./data/pilot/pilot20/glozz_annotations/hjoseph/discourse/pilot20_11_joseph_d_2801.aa ./data/pilot/pilot20/glozz_annotations/hjoseph/discourse/pilot20_11.aa
git mv ./data/pilot/pilot20/glozz_annotations/hjoseph/discourse/pilot20_12_joseph_d_2801.aa ./data/pilot/pilot20/glozz_annotations/hjoseph/discourse/pilot20_12.aa
git mv ./data/pilot/pilot20/glozz_annotations/hjoseph/discourse/pilot20_2_joseph_d_1001.aa ./data/pilot/pilot20/glozz_annotations/hjoseph/discourse/pilot20_02.aa
git mv ./data/pilot/pilot20/glozz_annotations/hjoseph/discourse/pilot20_3_joseph_d_1001.aa ./data/pilot/pilot20/glozz_annotations/hjoseph/discourse/pilot20_03.aa
git mv ./data/pilot/pilot20/glozz_annotations/hjoseph/discourse/pilot20_5_joseph_d_1201.aa ./data/pilot/pilot20/glozz_annotations/hjoseph/discourse/pilot20_05.aa
git mv ./data/pilot/pilot20/glozz_annotations/hjoseph/discourse/pilot20_6_joseph_d_1401.aa ./data/pilot/pilot20/glozz_annotations/hjoseph/discourse/pilot20_06.aa
git mv ./data/pilot/pilot20/glozz_annotations/hjoseph/discourse/pilot20_8_joseph_d_1401.aa ./data/pilot/pilot20/glozz_annotations/hjoseph/discourse/pilot20_08.aa
git mv ./data/pilot/pilot20/glozz_annotations/hjoseph/discourse/pilot20_9_joseph_d_1501.aa ./data/pilot/pilot20/glozz_annotations/hjoseph/discourse/pilot20_09.aa

git mv ./data/pilot/pilot20/glozz_annotations/hjoseph/units/pilot20_11_joseph_u_2801.aa ./data/pilot/pilot20/glozz_annotations/hjoseph/units/pilot20_11.aa
git mv ./data/pilot/pilot20/glozz_annotations/hjoseph/units/pilot20_12_joseph_u_2801.aa ./data/pilot/pilot20/glozz_annotations/hjoseph/units/pilot20_12.aa
git mv ./data/pilot/pilot20/glozz_annotations/hjoseph/units/pilot20_2_joseph_u_1001.aa ./data/pilot/pilot20/glozz_annotations/hjoseph/units/pilot20_02.aa
git mv ./data/pilot/pilot20/glozz_annotations/hjoseph/units/pilot20_3_joseph_u_1001.aa ./data/pilot/pilot20/glozz_annotations/hjoseph/units/pilot20_03.aa
git mv ./data/pilot/pilot20/glozz_annotations/hjoseph/units/pilot20_5_joseph_u_1201.aa ./data/pilot/pilot20/glozz_annotations/hjoseph/units/pilot20_05.aa
git mv ./data/pilot/pilot20/glozz_annotations/hjoseph/units/pilot20_6_joseph_u_1201.aa ./data/pilot/pilot20/glozz_annotations/hjoseph/units/pilot20_06.aa
git mv ./data/pilot/pilot20/glozz_annotations/hjoseph/units/pilot20_8_joseph_u_1401.aa ./data/pilot/pilot20/glozz_annotations/hjoseph/units/pilot20_08.aa
git mv ./data/pilot/pilot20/glozz_annotations/hjoseph/units/pilot20_9_joseph_u_1501.aa ./data/pilot/pilot20/glozz_annotations/hjoseph/units/pilot20_09.aa

git mv ./data/pilot/pilot20/glozz_annotations/jhall/discourse/pilot20_1.ac ./data/pilot/pilot20/glozz_annotations/jhall/discourse/pilot20_01.ac
#git mv ./data/pilot/pilot20/glozz_annotations/jhall/discourse/pilot20_10.ac ./data/pilot/pilot20/glozz_annotations/jhall/discourse/pilot20_10.ac
#git mv ./data/pilot/pilot20/glozz_annotations/jhall/discourse/pilot20_11.ac ./data/pilot/pilot20/glozz_annotations/jhall/discourse/pilot20_11.ac
#git mv ./data/pilot/pilot20/glozz_annotations/jhall/discourse/pilot20_12.ac ./data/pilot/pilot20/glozz_annotations/jhall/discourse/pilot20_12.ac
git mv ./data/pilot/pilot20/glozz_annotations/jhall/discourse/pilot20_2.ac ./data/pilot/pilot20/glozz_annotations/jhall/discourse/pilot20_02.ac
git mv ./data/pilot/pilot20/glozz_annotations/jhall/discourse/pilot20_3.ac ./data/pilot/pilot20/glozz_annotations/jhall/discourse/pilot20_03.ac
git mv ./data/pilot/pilot20/glozz_annotations/jhall/discourse/pilot20_4.ac ./data/pilot/pilot20/glozz_annotations/jhall/discourse/pilot20_04.ac
git mv ./data/pilot/pilot20/glozz_annotations/jhall/discourse/pilot20_5.ac ./data/pilot/pilot20/glozz_annotations/jhall/discourse/pilot20_05.ac
git mv ./data/pilot/pilot20/glozz_annotations/jhall/discourse/pilot20_6.ac ./data/pilot/pilot20/glozz_annotations/jhall/discourse/pilot20_06.ac
git mv ./data/pilot/pilot20/glozz_annotations/jhall/discourse/pilot20_7.ac ./data/pilot/pilot20/glozz_annotations/jhall/discourse/pilot20_07.ac
git mv ./data/pilot/pilot20/glozz_annotations/jhall/discourse/pilot20_8.ac ./data/pilot/pilot20/glozz_annotations/jhall/discourse/pilot20_08.ac
git mv ./data/pilot/pilot20/glozz_annotations/jhall/discourse/pilot20_9.ac ./data/pilot/pilot20/glozz_annotations/jhall/discourse/pilot20_09.ac

git mv ./data/pilot/pilot20/glozz_annotations/jhall/units/pilot20_1.ac ./data/pilot/pilot20/glozz_annotations/jhall/units/pilot20_01.ac
#git mv ./data/pilot/pilot20/glozz_annotations/jhall/units/pilot20_10.ac ./data/pilot/pilot20/glozz_annotations/jhall/units/pilot20_10.ac
#git mv ./data/pilot/pilot20/glozz_annotations/jhall/units/pilot20_11.ac ./data/pilot/pilot20/glozz_annotations/jhall/units/pilot20_11.ac
#git mv ./data/pilot/pilot20/glozz_annotations/jhall/units/pilot20_12.ac ./data/pilot/pilot20/glozz_annotations/jhall/units/pilot20_12.ac
git mv ./data/pilot/pilot20/glozz_annotations/jhall/units/pilot20_2.ac ./data/pilot/pilot20/glozz_annotations/jhall/units/pilot20_02.ac
git mv ./data/pilot/pilot20/glozz_annotations/jhall/units/pilot20_3.ac ./data/pilot/pilot20/glozz_annotations/jhall/units/pilot20_03.ac
git mv ./data/pilot/pilot20/glozz_annotations/jhall/units/pilot20_4.ac ./data/pilot/pilot20/glozz_annotations/jhall/units/pilot20_04.ac
git mv ./data/pilot/pilot20/glozz_annotations/jhall/units/pilot20_5.ac ./data/pilot/pilot20/glozz_annotations/jhall/units/pilot20_05.ac
git mv ./data/pilot/pilot20/glozz_annotations/jhall/units/pilot20_6.ac ./data/pilot/pilot20/glozz_annotations/jhall/units/pilot20_06.ac
git mv ./data/pilot/pilot20/glozz_annotations/jhall/units/pilot20_7.ac ./data/pilot/pilot20/glozz_annotations/jhall/units/pilot20_07.ac
git mv ./data/pilot/pilot20/glozz_annotations/jhall/units/pilot20_8.ac ./data/pilot/pilot20/glozz_annotations/jhall/units/pilot20_08.ac
git mv ./data/pilot/pilot20/glozz_annotations/jhall/units/pilot20_9.ac ./data/pilot/pilot20/glozz_annotations/jhall/units/pilot20_09.ac

git mv ./data/pilot/pilot20/glozz_annotations/lpetersen/discourse/pilot20_10_petersen_d_25122012.aa ./data/pilot/pilot20/glozz_annotations/lpetersen/discourse/pilot20_10.aa
git mv ./data/pilot/pilot20/glozz_annotations/lpetersen/discourse/pilot20_12_petersen_d_3012013.aa ./data/pilot/pilot20/glozz_annotations/lpetersen/discourse/pilot20_12.aa
git mv ./data/pilot/pilot20/glozz_annotations/lpetersen/discourse/pilot20_1_petersen_d_23122012.aa ./data/pilot/pilot20/glozz_annotations/lpetersen/discourse/pilot20_01.aa
git mv ./data/pilot/pilot20/glozz_annotations/lpetersen/discourse/pilot20_2_petersen_d_27122012.aa ./data/pilot/pilot20/glozz_annotations/lpetersen/discourse/pilot20_02.aa
git mv ./data/pilot/pilot20/glozz_annotations/lpetersen/discourse/pilot20_4_petersen_d_24122012.aa ./data/pilot/pilot20/glozz_annotations/lpetersen/discourse/pilot20_04.aa
git mv ./data/pilot/pilot20/glozz_annotations/lpetersen/discourse/pilot20_5_petersen_d_24122012.aa ./data/pilot/pilot20/glozz_annotations/lpetersen/discourse/pilot20_05.aa
git mv ./data/pilot/pilot20/glozz_annotations/lpetersen/discourse/pilot20_7_petersen_d_24122012.aa ./data/pilot/pilot20/glozz_annotations/lpetersen/discourse/pilot20_07.aa
git mv ./data/pilot/pilot20/glozz_annotations/lpetersen/discourse/pilot20_8_petersen_d_25122012.aa ./data/pilot/pilot20/glozz_annotations/lpetersen/discourse/pilot20_08.aa

git mv ./data/pilot/pilot20/glozz_annotations/lpetersen/units/pilot20_10_petersen_u_21122012.aa ./data/pilot/pilot20/glozz_annotations/lpetersen/units/pilot20_10.aa
git mv ./data/pilot/pilot20/glozz_annotations/lpetersen/units/pilot20_12_petersen_u_2012013.aa ./data/pilot/pilot20/glozz_annotations/lpetersen/units/pilot20_12.aa
git mv ./data/pilot/pilot20/glozz_annotations/lpetersen/units/pilot20_1_petersen_u_20122012.aa ./data/pilot/pilot20/glozz_annotations/lpetersen/units/pilot20_01.aa
git mv ./data/pilot/pilot20/glozz_annotations/lpetersen/units/pilot20_2_petersen_u_20122012.aa ./data/pilot/pilot20/glozz_annotations/lpetersen/units/pilot20_02.aa
git mv ./data/pilot/pilot20/glozz_annotations/lpetersen/units/pilot20_4_petersen_u_20122012.aa ./data/pilot/pilot20/glozz_annotations/lpetersen/units/pilot20_04.aa
git mv ./data/pilot/pilot20/glozz_annotations/lpetersen/units/pilot20_5_petersen_u_21122012.aa ./data/pilot/pilot20/glozz_annotations/lpetersen/units/pilot20_05.aa
git mv ./data/pilot/pilot20/glozz_annotations/lpetersen/units/pilot20_7_petersen_u_21122012.aa ./data/pilot/pilot20/glozz_annotations/lpetersen/units/pilot20_07.aa
git mv ./data/pilot/pilot20/glozz_annotations/lpetersen/units/pilot20_8_petersen_u_21122012.aa ./data/pilot/pilot20/glozz_annotations/lpetersen/units/pilot20_08.aa

git mv ./data/pilot/pilot20/glozz_annotations/mhunt/discourse/pilot20_1.ac ./data/pilot/pilot20/glozz_annotations/mhunt/discourse/pilot20_01.ac
#git mv ./data/pilot/pilot20/glozz_annotations/mhunt/discourse/pilot20_10.ac ./data/pilot/pilot20/glozz_annotations/mhunt/discourse/pilot20_10.ac
#git mv ./data/pilot/pilot20/glozz_annotations/mhunt/discourse/pilot20_11.ac ./data/pilot/pilot20/glozz_annotations/mhunt/discourse/pilot20_11.ac
#git mv ./data/pilot/pilot20/glozz_annotations/mhunt/discourse/pilot20_12.ac ./data/pilot/pilot20/glozz_annotations/mhunt/discourse/pilot20_12.ac
git mv ./data/pilot/pilot20/glozz_annotations/mhunt/discourse/pilot20_2.ac ./data/pilot/pilot20/glozz_annotations/mhunt/discourse/pilot20_02.ac
git mv ./data/pilot/pilot20/glozz_annotations/mhunt/discourse/pilot20_3.ac ./data/pilot/pilot20/glozz_annotations/mhunt/discourse/pilot20_03.ac
git mv ./data/pilot/pilot20/glozz_annotations/mhunt/discourse/pilot20_4.ac ./data/pilot/pilot20/glozz_annotations/mhunt/discourse/pilot20_04.ac
git mv ./data/pilot/pilot20/glozz_annotations/mhunt/discourse/pilot20_5.ac ./data/pilot/pilot20/glozz_annotations/mhunt/discourse/pilot20_05.ac
git mv ./data/pilot/pilot20/glozz_annotations/mhunt/discourse/pilot20_6.ac ./data/pilot/pilot20/glozz_annotations/mhunt/discourse/pilot20_06.ac
git mv ./data/pilot/pilot20/glozz_annotations/mhunt/discourse/pilot20_7.ac ./data/pilot/pilot20/glozz_annotations/mhunt/discourse/pilot20_07.ac
git mv ./data/pilot/pilot20/glozz_annotations/mhunt/discourse/pilot20_8.ac ./data/pilot/pilot20/glozz_annotations/mhunt/discourse/pilot20_08.ac
git mv ./data/pilot/pilot20/glozz_annotations/mhunt/discourse/pilot20_9.ac ./data/pilot/pilot20/glozz_annotations/mhunt/discourse/pilot20_09.ac

git mv ./data/pilot/pilot20/glozz_annotations/mhunt/units/pilot20_1.ac ./data/pilot/pilot20/glozz_annotations/mhunt/units/pilot20_01.ac
#git mv ./data/pilot/pilot20/glozz_annotations/mhunt/units/pilot20_10.ac ./data/pilot/pilot20/glozz_annotations/mhunt/units/pilot20_10.ac
#git mv ./data/pilot/pilot20/glozz_annotations/mhunt/units/pilot20_11.ac ./data/pilot/pilot20/glozz_annotations/mhunt/units/pilot20_11.ac
#git mv ./data/pilot/pilot20/glozz_annotations/mhunt/units/pilot20_12.ac ./data/pilot/pilot20/glozz_annotations/mhunt/units/pilot20_12.ac
git mv ./data/pilot/pilot20/glozz_annotations/mhunt/units/pilot20_2.ac ./data/pilot/pilot20/glozz_annotations/mhunt/units/pilot20_02.ac
git mv ./data/pilot/pilot20/glozz_annotations/mhunt/units/pilot20_3.ac ./data/pilot/pilot20/glozz_annotations/mhunt/units/pilot20_03.ac
git mv ./data/pilot/pilot20/glozz_annotations/mhunt/units/pilot20_4.ac ./data/pilot/pilot20/glozz_annotations/mhunt/units/pilot20_04.ac
git mv ./data/pilot/pilot20/glozz_annotations/mhunt/units/pilot20_5.ac ./data/pilot/pilot20/glozz_annotations/mhunt/units/pilot20_05.ac
git mv ./data/pilot/pilot20/glozz_annotations/mhunt/units/pilot20_6.ac ./data/pilot/pilot20/glozz_annotations/mhunt/units/pilot20_06.ac
git mv ./data/pilot/pilot20/glozz_annotations/mhunt/units/pilot20_7.ac ./data/pilot/pilot20/glozz_annotations/mhunt/units/pilot20_07.ac
git mv ./data/pilot/pilot20/glozz_annotations/mhunt/units/pilot20_8.ac ./data/pilot/pilot20/glozz_annotations/mhunt/units/pilot20_08.ac
git mv ./data/pilot/pilot20/glozz_annotations/mhunt/units/pilot20_9.ac ./data/pilot/pilot20/glozz_annotations/mhunt/units/pilot20_09.ac

git mv ./data/pilot/pilot20/glozz_preannotation/pilot20_1.ac ./data/pilot/pilot20/glozz_preannotation/pilot20_01.ac
#git mv ./data/pilot/pilot20/glozz_preannotation/pilot20_10.ac ./data/pilot/pilot20/glozz_preannotation/pilot20_10.ac
#git mv ./data/pilot/pilot20/glozz_preannotation/pilot20_11.ac ./data/pilot/pilot20/glozz_preannotation/pilot20_11.ac
#git mv ./data/pilot/pilot20/glozz_preannotation/pilot20_12.ac ./data/pilot/pilot20/glozz_preannotation/pilot20_12.ac
git mv ./data/pilot/pilot20/glozz_preannotation/pilot20_2.ac ./data/pilot/pilot20/glozz_preannotation/pilot20_02.ac
git mv ./data/pilot/pilot20/glozz_preannotation/pilot20_3.ac ./data/pilot/pilot20/glozz_preannotation/pilot20_03.ac
git mv ./data/pilot/pilot20/glozz_preannotation/pilot20_4.ac ./data/pilot/pilot20/glozz_preannotation/pilot20_04.ac
git mv ./data/pilot/pilot20/glozz_preannotation/pilot20_5.ac ./data/pilot/pilot20/glozz_preannotation/pilot20_05.ac
git mv ./data/pilot/pilot20/glozz_preannotation/pilot20_6.ac ./data/pilot/pilot20/glozz_preannotation/pilot20_06.ac
git mv ./data/pilot/pilot20/glozz_preannotation/pilot20_7.ac ./data/pilot/pilot20/glozz_preannotation/pilot20_07.ac
git mv ./data/pilot/pilot20/glozz_preannotation/pilot20_8.ac ./data/pilot/pilot20/glozz_preannotation/pilot20_08.ac
git mv ./data/pilot/pilot20/glozz_preannotation/pilot20_9.ac ./data/pilot/pilot20/glozz_preannotation/pilot20_09.ac

git mv ./data/pilot/pilot20/Gold/Unit/pilot20_10_petersen_u_21122012.aa ./data/pilot/pilot20/Gold/Unit/pilot20_10.aa
git mv ./data/pilot/pilot20/Gold/Unit/pilot20_11_joseph_u_2801.aa ./data/pilot/pilot20/Gold/Unit/pilot20_11.aa
git mv ./data/pilot/pilot20/Gold/Unit/pilot20_12_petersen_u_2012013.aa ./data/pilot/pilot20/Gold/Unit/pilot20_12.aa
git mv ./data/pilot/pilot20/Gold/Unit/pilot20_1_petersen_u_20122012.aa ./data/pilot/pilot20/Gold/Unit/pilot20_01.aa
git mv ./data/pilot/pilot20/Gold/Unit/pilot20_2_petersen_u_20122012.aa ./data/pilot/pilot20/Gold/Unit/pilot20_02.aa
git mv ./data/pilot/pilot20/Gold/Unit/pilot20_3_joseph_u_1001.aa ./data/pilot/pilot20/Gold/Unit/pilot20_03.aa
git mv ./data/pilot/pilot20/Gold/Unit/pilot20_4_petersen_u_20122012.aa ./data/pilot/pilot20/Gold/Unit/pilot20_04.aa
git mv ./data/pilot/pilot20/Gold/Unit/pilot20_5_petersen_u_21122012.aa ./data/pilot/pilot20/Gold/Unit/pilot20_05.aa
git mv ./data/pilot/pilot20/Gold/Unit/pilot20_6_joseph_u_1201.aa ./data/pilot/pilot20/Gold/Unit/pilot20_06.aa
git mv ./data/pilot/pilot20/Gold/Unit/pilot20_7_petersen_u_21122012.aa ./data/pilot/pilot20/Gold/Unit/pilot20_07.aa
git mv ./data/pilot/pilot20/Gold/Unit/pilot20_8_petersen_u_21122012.aa ./data/pilot/pilot20/Gold/Unit/pilot20_08.aa
git mv ./data/pilot/pilot20/Gold/Unit/pilot20_9_joseph_u_1501.aa ./data/pilot/pilot20/Gold/Unit/pilot20_09.aa

git mv ./data/pilot/pilot20/Gold/Unit_Pred_Arg/pilot20_1.ac_petersen.seg ./data/pilot/pilot20/Gold/Unit_Pred_Arg/pilot20_01.ac.seg
git mv ./data/pilot/pilot20/Gold/Unit_Pred_Arg/pilot20_10.ac_petersen.seg ./data/pilot/pilot20/Gold/Unit_Pred_Arg/pilot20_10.ac.seg
git mv ./data/pilot/pilot20/Gold/Unit_Pred_Arg/pilot20_11.ac_joseph.seg ./data/pilot/pilot20/Gold/Unit_Pred_Arg/pilot20_11.ac.seg
git mv ./data/pilot/pilot20/Gold/Unit_Pred_Arg/pilot20_12.ac_petersen.seg ./data/pilot/pilot20/Gold/Unit_Pred_Arg/pilot20_12.ac.seg
git mv ./data/pilot/pilot20/Gold/Unit_Pred_Arg/pilot20_2.ac_petersen.seg ./data/pilot/pilot20/Gold/Unit_Pred_Arg/pilot20_02.ac.seg
git mv ./data/pilot/pilot20/Gold/Unit_Pred_Arg/pilot20_3.ac_joseph.seg ./data/pilot/pilot20/Gold/Unit_Pred_Arg/pilot20_03.ac.seg
git mv ./data/pilot/pilot20/Gold/Unit_Pred_Arg/pilot20_4.ac_petersen.seg ./data/pilot/pilot20/Gold/Unit_Pred_Arg/pilot20_04.ac.seg
git mv ./data/pilot/pilot20/Gold/Unit_Pred_Arg/pilot20_5.ac_petersen.seg ./data/pilot/pilot20/Gold/Unit_Pred_Arg/pilot20_05.ac.seg
git mv ./data/pilot/pilot20/Gold/Unit_Pred_Arg/pilot20_6.ac_joseph.seg ./data/pilot/pilot20/Gold/Unit_Pred_Arg/pilot20_06.ac.seg
git mv ./data/pilot/pilot20/Gold/Unit_Pred_Arg/pilot20_7.ac_petersen.seg ./data/pilot/pilot20/Gold/Unit_Pred_Arg/pilot20_07.ac.seg
git mv ./data/pilot/pilot20/Gold/Unit_Pred_Arg/pilot20_8.ac_petersen.seg ./data/pilot/pilot20/Gold/Unit_Pred_Arg/pilot20_08.ac.seg
git mv ./data/pilot/pilot20/Gold/Unit_Pred_Arg/pilot20_9.ac_joseph.seg ./data/pilot/pilot20/Gold/Unit_Pred_Arg/pilot20_09.ac.seg

git mv ./data/pilot/pilot20/pred_arg_annotations/joseph/discourse/pilot20_2.ac_joseph.rel ./data/pilot/pilot20/pred_arg_annotations/joseph/discourse/pilot20_02.ac.rel
git mv ./data/pilot/pilot20/pred_arg_annotations/joseph/discourse/pilot20_3.ac_joseph.rel ./data/pilot/pilot20/pred_arg_annotations/joseph/discourse/pilot20_03.ac.rel
git mv ./data/pilot/pilot20/pred_arg_annotations/joseph/discourse/pilot20_5.ac_joseph.rel ./data/pilot/pilot20/pred_arg_annotations/joseph/discourse/pilot20_05.ac.rel
git mv ./data/pilot/pilot20/pred_arg_annotations/joseph/discourse/pilot20_6.ac_joseph.rel ./data/pilot/pilot20/pred_arg_annotations/joseph/discourse/pilot20_06.ac.rel
git mv ./data/pilot/pilot20/pred_arg_annotations/joseph/discourse/pilot20_8.ac_joseph.rel ./data/pilot/pilot20/pred_arg_annotations/joseph/discourse/pilot20_08.ac.rel
git mv ./data/pilot/pilot20/pred_arg_annotations/joseph/discourse/pilot20_9.ac_joseph.rel ./data/pilot/pilot20/pred_arg_annotations/joseph/discourse/pilot20_09.ac.rel

git mv ./data/pilot/pilot20/pred_arg_annotations/joseph/unit/pilot20_2.ac_joseph.seg ./data/pilot/pilot20/pred_arg_annotations/joseph/unit/pilot20_02.ac.seg
git mv ./data/pilot/pilot20/pred_arg_annotations/joseph/unit/pilot20_3.ac_joseph.seg ./data/pilot/pilot20/pred_arg_annotations/joseph/unit/pilot20_03.ac.seg
git mv ./data/pilot/pilot20/pred_arg_annotations/joseph/unit/pilot20_5.ac_joseph.seg ./data/pilot/pilot20/pred_arg_annotations/joseph/unit/pilot20_05.ac.seg
git mv ./data/pilot/pilot20/pred_arg_annotations/joseph/unit/pilot20_6.ac_joseph.seg ./data/pilot/pilot20/pred_arg_annotations/joseph/unit/pilot20_06.ac.seg
git mv ./data/pilot/pilot20/pred_arg_annotations/joseph/unit/pilot20_8.ac_joseph.seg ./data/pilot/pilot20/pred_arg_annotations/joseph/unit/pilot20_08.ac.seg
git mv ./data/pilot/pilot20/pred_arg_annotations/joseph/unit/pilot20_9.ac_joseph.seg ./data/pilot/pilot20/pred_arg_annotations/joseph/unit/pilot20_09.ac.seg

git mv ./data/pilot/pilot20/pred_arg_annotations/petersen/discourse/pilot20_1.ac_petersen.rel ./data/pilot/pilot20/pred_arg_annotations/petersen/discourse/pilot20_01.ac.rel
git mv ./data/pilot/pilot20/pred_arg_annotations/petersen/discourse/pilot20_10.ac_petersen.rel ./data/pilot/pilot20/pred_arg_annotations/petersen/discourse/pilot20_10.ac.rel
git mv ./data/pilot/pilot20/pred_arg_annotations/petersen/discourse/pilot20_12.ac_petersen.rel ./data/pilot/pilot20/pred_arg_annotations/petersen/discourse/pilot20_12.ac.rel
git mv ./data/pilot/pilot20/pred_arg_annotations/petersen/discourse/pilot20_2.ac_petersen.rel ./data/pilot/pilot20/pred_arg_annotations/petersen/discourse/pilot20_02.ac.rel
git mv ./data/pilot/pilot20/pred_arg_annotations/petersen/discourse/pilot20_4.ac_petersen.rel ./data/pilot/pilot20/pred_arg_annotations/petersen/discourse/pilot20_04.ac.rel
git mv ./data/pilot/pilot20/pred_arg_annotations/petersen/discourse/pilot20_5.ac_petersen.rel ./data/pilot/pilot20/pred_arg_annotations/petersen/discourse/pilot20_05.ac.rel
git mv ./data/pilot/pilot20/pred_arg_annotations/petersen/discourse/pilot20_7.ac_petersen.rel ./data/pilot/pilot20/pred_arg_annotations/petersen/discourse/pilot20_07.ac.rel
git mv ./data/pilot/pilot20/pred_arg_annotations/petersen/discourse/pilot20_8.ac_petersen.rel ./data/pilot/pilot20/pred_arg_annotations/petersen/discourse/pilot20_08.ac.rel

git mv ./data/pilot/pilot20/pred_arg_annotations/petersen/unit/pilot20_1.ac_petersen.seg ./data/pilot/pilot20/pred_arg_annotations/petersen/unit/pilot20_01.ac.seg
git mv ./data/pilot/pilot20/pred_arg_annotations/petersen/unit/pilot20_10.ac_petersen.seg ./data/pilot/pilot20/pred_arg_annotations/petersen/unit/pilot20_10.ac.seg
git mv ./data/pilot/pilot20/pred_arg_annotations/petersen/unit/pilot20_12.ac_petersen.seg ./data/pilot/pilot20/pred_arg_annotations/petersen/unit/pilot20_12.ac.seg
git mv ./data/pilot/pilot20/pred_arg_annotations/petersen/unit/pilot20_2.ac_petersen.seg ./data/pilot/pilot20/pred_arg_annotations/petersen/unit/pilot20_02.ac.seg
git mv ./data/pilot/pilot20/pred_arg_annotations/petersen/unit/pilot20_4.ac_petersen.seg ./data/pilot/pilot20/pred_arg_annotations/petersen/unit/pilot20_04.ac.seg
git mv ./data/pilot/pilot20/pred_arg_annotations/petersen/unit/pilot20_5.ac_petersen.seg ./data/pilot/pilot20/pred_arg_annotations/petersen/unit/pilot20_05.ac.seg
git mv ./data/pilot/pilot20/pred_arg_annotations/petersen/unit/pilot20_7.ac_petersen.seg ./data/pilot/pilot20/pred_arg_annotations/petersen/unit/pilot20_07.ac.seg
git mv ./data/pilot/pilot20/pred_arg_annotations/petersen/unit/pilot20_8.ac_petersen.seg ./data/pilot/pilot20/pred_arg_annotations/petersen/unit/pilot20_08.ac.seg

git mv ./data/pilot/pilot21/glozz_annotations/hjoseph/discourse/pilot21_12_joseph_d_2801.aa ./data/pilot/pilot21/glozz_annotations/hjoseph/discourse/pilot21_12.aa
git mv ./data/pilot/pilot21/glozz_annotations/hjoseph/discourse/pilot21_1_joseph_d_1501.aa ./data/pilot/pilot21/glozz_annotations/hjoseph/discourse/pilot21_01.aa
git mv ./data/pilot/pilot21/glozz_annotations/hjoseph/discourse/pilot21_3_joseph_d_1701.aa ./data/pilot/pilot21/glozz_annotations/hjoseph/discourse/pilot21_03.aa
git mv ./data/pilot/pilot21/glozz_annotations/hjoseph/discourse/pilot21_4_joseph_d_1701.aa ./data/pilot/pilot21/glozz_annotations/hjoseph/discourse/pilot21_04.aa
git mv ./data/pilot/pilot21/glozz_annotations/hjoseph/discourse/pilot21_6_joseph_d_2301.aa ./data/pilot/pilot21/glozz_annotations/hjoseph/discourse/pilot21_06.aa
git mv ./data/pilot/pilot21/glozz_annotations/hjoseph/discourse/pilot21_7_joseph_d_2401.aa ./data/pilot/pilot21/glozz_annotations/hjoseph/discourse/pilot21_07.aa
git mv ./data/pilot/pilot21/glozz_annotations/hjoseph/discourse/pilot21_9_joseph_d_2401.aa ./data/pilot/pilot21/glozz_annotations/hjoseph/discourse/pilot21_09.aa

git mv ./data/pilot/pilot21/glozz_annotations/hjoseph/units/pilot21_12_joseph_u_2801.aa ./data/pilot/pilot21/glozz_annotations/hjoseph/units/pilot21_12.aa
git mv ./data/pilot/pilot21/glozz_annotations/hjoseph/units/pilot21_1_joseph_u_1501.aa ./data/pilot/pilot21/glozz_annotations/hjoseph/units/pilot21_01.aa
git mv ./data/pilot/pilot21/glozz_annotations/hjoseph/units/pilot21_3_joseph_u_1701.aa ./data/pilot/pilot21/glozz_annotations/hjoseph/units/pilot21_03.aa
git mv ./data/pilot/pilot21/glozz_annotations/hjoseph/units/pilot21_4_joseph_u_1701.aa ./data/pilot/pilot21/glozz_annotations/hjoseph/units/pilot21_04.aa
git mv ./data/pilot/pilot21/glozz_annotations/hjoseph/units/pilot21_6_joseph_u_2201.aa ./data/pilot/pilot21/glozz_annotations/hjoseph/units/pilot21_06.aa
git mv ./data/pilot/pilot21/glozz_annotations/hjoseph/units/pilot21_7_joseph_u_2401.aa ./data/pilot/pilot21/glozz_annotations/hjoseph/units/pilot21_07.aa
git mv ./data/pilot/pilot21/glozz_annotations/hjoseph/units/pilot21_9_joseph_u_2401.aa ./data/pilot/pilot21/glozz_annotations/hjoseph/units/pilot21_09.aa

git mv ./data/pilot/pilot21/glozz_annotations/jhall/discourse/pilot21_1.ac ./data/pilot/pilot21/glozz_annotations/jhall/discourse/pilot21_01.ac
#git mv ./data/pilot/pilot21/glozz_annotations/jhall/discourse/pilot21_10.ac ./data/pilot/pilot21/glozz_annotations/jhall/discourse/pilot21_10.ac
#git mv ./data/pilot/pilot21/glozz_annotations/jhall/discourse/pilot21_11.ac ./data/pilot/pilot21/glozz_annotations/jhall/discourse/pilot21_11.ac
#git mv ./data/pilot/pilot21/glozz_annotations/jhall/discourse/pilot21_12.ac ./data/pilot/pilot21/glozz_annotations/jhall/discourse/pilot21_12.ac
git mv ./data/pilot/pilot21/glozz_annotations/jhall/discourse/pilot21_2.ac ./data/pilot/pilot21/glozz_annotations/jhall/discourse/pilot21_02.ac
git mv ./data/pilot/pilot21/glozz_annotations/jhall/discourse/pilot21_3.ac ./data/pilot/pilot21/glozz_annotations/jhall/discourse/pilot21_03.ac
git mv ./data/pilot/pilot21/glozz_annotations/jhall/discourse/pilot21_4.ac ./data/pilot/pilot21/glozz_annotations/jhall/discourse/pilot21_04.ac
git mv ./data/pilot/pilot21/glozz_annotations/jhall/discourse/pilot21_5.ac ./data/pilot/pilot21/glozz_annotations/jhall/discourse/pilot21_05.ac
git mv ./data/pilot/pilot21/glozz_annotations/jhall/discourse/pilot21_6.ac ./data/pilot/pilot21/glozz_annotations/jhall/discourse/pilot21_06.ac
git mv ./data/pilot/pilot21/glozz_annotations/jhall/discourse/pilot21_7.ac ./data/pilot/pilot21/glozz_annotations/jhall/discourse/pilot21_07.ac
git mv ./data/pilot/pilot21/glozz_annotations/jhall/discourse/pilot21_8.ac ./data/pilot/pilot21/glozz_annotations/jhall/discourse/pilot21_08.ac
git mv ./data/pilot/pilot21/glozz_annotations/jhall/discourse/pilot21_9.ac ./data/pilot/pilot21/glozz_annotations/jhall/discourse/pilot21_09.ac

git mv ./data/pilot/pilot21/glozz_annotations/jhall/units/pilot21_1.ac ./data/pilot/pilot21/glozz_annotations/jhall/units/pilot21_01.ac
#git mv ./data/pilot/pilot21/glozz_annotations/jhall/units/pilot21_10.ac ./data/pilot/pilot21/glozz_annotations/jhall/units/pilot21_10.ac
#git mv ./data/pilot/pilot21/glozz_annotations/jhall/units/pilot21_11.ac ./data/pilot/pilot21/glozz_annotations/jhall/units/pilot21_11.ac
#git mv ./data/pilot/pilot21/glozz_annotations/jhall/units/pilot21_12.ac ./data/pilot/pilot21/glozz_annotations/jhall/units/pilot21_12.ac
git mv ./data/pilot/pilot21/glozz_annotations/jhall/units/pilot21_2.ac ./data/pilot/pilot21/glozz_annotations/jhall/units/pilot21_02.ac
git mv ./data/pilot/pilot21/glozz_annotations/jhall/units/pilot21_3.ac ./data/pilot/pilot21/glozz_annotations/jhall/units/pilot21_03.ac
git mv ./data/pilot/pilot21/glozz_annotations/jhall/units/pilot21_4.ac ./data/pilot/pilot21/glozz_annotations/jhall/units/pilot21_04.ac
git mv ./data/pilot/pilot21/glozz_annotations/jhall/units/pilot21_5.ac ./data/pilot/pilot21/glozz_annotations/jhall/units/pilot21_05.ac
git mv ./data/pilot/pilot21/glozz_annotations/jhall/units/pilot21_6.ac ./data/pilot/pilot21/glozz_annotations/jhall/units/pilot21_06.ac
git mv ./data/pilot/pilot21/glozz_annotations/jhall/units/pilot21_7.ac ./data/pilot/pilot21/glozz_annotations/jhall/units/pilot21_07.ac
git mv ./data/pilot/pilot21/glozz_annotations/jhall/units/pilot21_8.ac ./data/pilot/pilot21/glozz_annotations/jhall/units/pilot21_08.ac
git mv ./data/pilot/pilot21/glozz_annotations/jhall/units/pilot21_9.ac ./data/pilot/pilot21/glozz_annotations/jhall/units/pilot21_09.ac

git mv ./data/pilot/pilot21/glozz_annotations/lpetersen/discourse/pilot21_10_petersen_d_1012013.aa ./data/pilot/pilot21/glozz_annotations/lpetersen/discourse/pilot21_10.aa
git mv ./data/pilot/pilot21/glozz_annotations/lpetersen/discourse/pilot21_11_petersen_d_3012013.aa ./data/pilot/pilot21/glozz_annotations/lpetersen/discourse/pilot21_11.aa
git mv ./data/pilot/pilot21/glozz_annotations/lpetersen/discourse/pilot21_1_petersen_d_30012012.aa ./data/pilot/pilot21/glozz_annotations/lpetersen/discourse/pilot21_01.aa
git mv ./data/pilot/pilot21/glozz_annotations/lpetersen/discourse/pilot21_2_petersen_d_30122012.aa ./data/pilot/pilot21/glozz_annotations/lpetersen/discourse/pilot21_02.aa
git mv ./data/pilot/pilot21/glozz_annotations/lpetersen/discourse/pilot21_4_petersen_d_30122012.aa ./data/pilot/pilot21/glozz_annotations/lpetersen/discourse/pilot21_04.aa
git mv ./data/pilot/pilot21/glozz_annotations/lpetersen/discourse/pilot21_5_petersen_d_30122012.aa ./data/pilot/pilot21/glozz_annotations/lpetersen/discourse/pilot21_05.aa
git mv ./data/pilot/pilot21/glozz_annotations/lpetersen/discourse/pilot21_7_petersen_d_1012013.aa ./data/pilot/pilot21/glozz_annotations/lpetersen/discourse/pilot21_07.aa
git mv ./data/pilot/pilot21/glozz_annotations/lpetersen/discourse/pilot21_8_petersen_d_1012013.aa ./data/pilot/pilot21/glozz_annotations/lpetersen/discourse/pilot21_08.aa

git mv ./data/pilot/pilot21/glozz_annotations/lpetersen/units/pilot21_10_petersen_u_28122012.aa ./data/pilot/pilot21/glozz_annotations/lpetersen/units/pilot21_10.aa
git mv ./data/pilot/pilot21/glozz_annotations/lpetersen/units/pilot21_11_petersen_u_2012013.aa ./data/pilot/pilot21/glozz_annotations/lpetersen/units/pilot21_11.aa
git mv ./data/pilot/pilot21/glozz_annotations/lpetersen/units/pilot21_1_petersen_u_27122012.aa ./data/pilot/pilot21/glozz_annotations/lpetersen/units/pilot21_01.aa
git mv ./data/pilot/pilot21/glozz_annotations/lpetersen/units/pilot21_2_petersen_u_27122012.aa ./data/pilot/pilot21/glozz_annotations/lpetersen/units/pilot21_02.aa
git mv ./data/pilot/pilot21/glozz_annotations/lpetersen/units/pilot21_4_petersen_u_27122012.aa ./data/pilot/pilot21/glozz_annotations/lpetersen/units/pilot21_04.aa
git mv ./data/pilot/pilot21/glozz_annotations/lpetersen/units/pilot21_5_petersen_u_27122012.aa ./data/pilot/pilot21/glozz_annotations/lpetersen/units/pilot21_05.aa
git mv ./data/pilot/pilot21/glozz_annotations/lpetersen/units/pilot21_7_petersen_u_27122012.aa ./data/pilot/pilot21/glozz_annotations/lpetersen/units/pilot21_07.aa
git mv ./data/pilot/pilot21/glozz_annotations/lpetersen/units/pilot21_8_petersen_u_28122012.aa ./data/pilot/pilot21/glozz_annotations/lpetersen/units/pilot21_08.aa

git mv ./data/pilot/pilot21/glozz_annotations/mhunt/discourse/pilot21_1.ac ./data/pilot/pilot21/glozz_annotations/mhunt/discourse/pilot21_01.ac
#git mv ./data/pilot/pilot21/glozz_annotations/mhunt/discourse/pilot21_10.ac ./data/pilot/pilot21/glozz_annotations/mhunt/discourse/pilot21_10.ac
#git mv ./data/pilot/pilot21/glozz_annotations/mhunt/discourse/pilot21_11.ac ./data/pilot/pilot21/glozz_annotations/mhunt/discourse/pilot21_11.ac
#git mv ./data/pilot/pilot21/glozz_annotations/mhunt/discourse/pilot21_12.ac ./data/pilot/pilot21/glozz_annotations/mhunt/discourse/pilot21_12.ac
git mv ./data/pilot/pilot21/glozz_annotations/mhunt/discourse/pilot21_2.ac ./data/pilot/pilot21/glozz_annotations/mhunt/discourse/pilot21_02.ac
git mv ./data/pilot/pilot21/glozz_annotations/mhunt/discourse/pilot21_3.ac ./data/pilot/pilot21/glozz_annotations/mhunt/discourse/pilot21_03.ac
git mv ./data/pilot/pilot21/glozz_annotations/mhunt/discourse/pilot21_4.ac ./data/pilot/pilot21/glozz_annotations/mhunt/discourse/pilot21_04.ac
git mv ./data/pilot/pilot21/glozz_annotations/mhunt/discourse/pilot21_5.ac ./data/pilot/pilot21/glozz_annotations/mhunt/discourse/pilot21_05.ac
git mv ./data/pilot/pilot21/glozz_annotations/mhunt/discourse/pilot21_6.ac ./data/pilot/pilot21/glozz_annotations/mhunt/discourse/pilot21_06.ac
git mv ./data/pilot/pilot21/glozz_annotations/mhunt/discourse/pilot21_7.ac ./data/pilot/pilot21/glozz_annotations/mhunt/discourse/pilot21_07.ac
git mv ./data/pilot/pilot21/glozz_annotations/mhunt/discourse/pilot21_8.ac ./data/pilot/pilot21/glozz_annotations/mhunt/discourse/pilot21_08.ac
git mv ./data/pilot/pilot21/glozz_annotations/mhunt/discourse/pilot21_9.ac ./data/pilot/pilot21/glozz_annotations/mhunt/discourse/pilot21_09.ac

git mv ./data/pilot/pilot21/glozz_annotations/mhunt/units/pilot21_1.ac ./data/pilot/pilot21/glozz_annotations/mhunt/units/pilot21_01.ac
#git mv ./data/pilot/pilot21/glozz_annotations/mhunt/units/pilot21_10.ac ./data/pilot/pilot21/glozz_annotations/mhunt/units/pilot21_10.ac
#git mv ./data/pilot/pilot21/glozz_annotations/mhunt/units/pilot21_11.ac ./data/pilot/pilot21/glozz_annotations/mhunt/units/pilot21_11.ac
#git mv ./data/pilot/pilot21/glozz_annotations/mhunt/units/pilot21_12.ac ./data/pilot/pilot21/glozz_annotations/mhunt/units/pilot21_12.ac
git mv ./data/pilot/pilot21/glozz_annotations/mhunt/units/pilot21_2.ac ./data/pilot/pilot21/glozz_annotations/mhunt/units/pilot21_02.ac
git mv ./data/pilot/pilot21/glozz_annotations/mhunt/units/pilot21_3.ac ./data/pilot/pilot21/glozz_annotations/mhunt/units/pilot21_03.ac
git mv ./data/pilot/pilot21/glozz_annotations/mhunt/units/pilot21_4.ac ./data/pilot/pilot21/glozz_annotations/mhunt/units/pilot21_04.ac
git mv ./data/pilot/pilot21/glozz_annotations/mhunt/units/pilot21_5.ac ./data/pilot/pilot21/glozz_annotations/mhunt/units/pilot21_05.ac
git mv ./data/pilot/pilot21/glozz_annotations/mhunt/units/pilot21_6.ac ./data/pilot/pilot21/glozz_annotations/mhunt/units/pilot21_06.ac
git mv ./data/pilot/pilot21/glozz_annotations/mhunt/units/pilot21_7.ac ./data/pilot/pilot21/glozz_annotations/mhunt/units/pilot21_07.ac
git mv ./data/pilot/pilot21/glozz_annotations/mhunt/units/pilot21_8.ac ./data/pilot/pilot21/glozz_annotations/mhunt/units/pilot21_08.ac
git mv ./data/pilot/pilot21/glozz_annotations/mhunt/units/pilot21_9.ac ./data/pilot/pilot21/glozz_annotations/mhunt/units/pilot21_09.ac

git mv ./data/pilot/pilot21/glozz_preannotation/pilot21_1.aa ./data/pilot/pilot21/glozz_preannotation/pilot21_01.aa
git mv ./data/pilot/pilot21/glozz_preannotation/pilot21_1.ac ./data/pilot/pilot21/glozz_preannotation/pilot21_01.ac
#git mv ./data/pilot/pilot21/glozz_preannotation/pilot21_10.aa ./data/pilot/pilot21/glozz_preannotation/pilot21_10.aa
#git mv ./data/pilot/pilot21/glozz_preannotation/pilot21_10.ac ./data/pilot/pilot21/glozz_preannotation/pilot21_10.ac
#git mv ./data/pilot/pilot21/glozz_preannotation/pilot21_11.aa ./data/pilot/pilot21/glozz_preannotation/pilot21_11.aa
#git mv ./data/pilot/pilot21/glozz_preannotation/pilot21_11.ac ./data/pilot/pilot21/glozz_preannotation/pilot21_11.ac
#git mv ./data/pilot/pilot21/glozz_preannotation/pilot21_12.aa ./data/pilot/pilot21/glozz_preannotation/pilot21_12.aa
#git mv ./data/pilot/pilot21/glozz_preannotation/pilot21_12.ac ./data/pilot/pilot21/glozz_preannotation/pilot21_12.ac
git mv ./data/pilot/pilot21/glozz_preannotation/pilot21_2.aa ./data/pilot/pilot21/glozz_preannotation/pilot21_02.aa
git mv ./data/pilot/pilot21/glozz_preannotation/pilot21_2.ac ./data/pilot/pilot21/glozz_preannotation/pilot21_02.ac
git mv ./data/pilot/pilot21/glozz_preannotation/pilot21_3.aa ./data/pilot/pilot21/glozz_preannotation/pilot21_03.aa
git mv ./data/pilot/pilot21/glozz_preannotation/pilot21_3.ac ./data/pilot/pilot21/glozz_preannotation/pilot21_03.ac
git mv ./data/pilot/pilot21/glozz_preannotation/pilot21_4.aa ./data/pilot/pilot21/glozz_preannotation/pilot21_04.aa
git mv ./data/pilot/pilot21/glozz_preannotation/pilot21_4.ac ./data/pilot/pilot21/glozz_preannotation/pilot21_04.ac
git mv ./data/pilot/pilot21/glozz_preannotation/pilot21_5.aa ./data/pilot/pilot21/glozz_preannotation/pilot21_05.aa
git mv ./data/pilot/pilot21/glozz_preannotation/pilot21_5.ac ./data/pilot/pilot21/glozz_preannotation/pilot21_05.ac
git mv ./data/pilot/pilot21/glozz_preannotation/pilot21_6.aa ./data/pilot/pilot21/glozz_preannotation/pilot21_06.aa
git mv ./data/pilot/pilot21/glozz_preannotation/pilot21_6.ac ./data/pilot/pilot21/glozz_preannotation/pilot21_06.ac
git mv ./data/pilot/pilot21/glozz_preannotation/pilot21_7.aa ./data/pilot/pilot21/glozz_preannotation/pilot21_07.aa
git mv ./data/pilot/pilot21/glozz_preannotation/pilot21_7.ac ./data/pilot/pilot21/glozz_preannotation/pilot21_07.ac
git mv ./data/pilot/pilot21/glozz_preannotation/pilot21_8.aa ./data/pilot/pilot21/glozz_preannotation/pilot21_08.aa
git mv ./data/pilot/pilot21/glozz_preannotation/pilot21_8.ac ./data/pilot/pilot21/glozz_preannotation/pilot21_08.ac
git mv ./data/pilot/pilot21/glozz_preannotation/pilot21_9.aa ./data/pilot/pilot21/glozz_preannotation/pilot21_09.aa
git mv ./data/pilot/pilot21/glozz_preannotation/pilot21_9.ac ./data/pilot/pilot21/glozz_preannotation/pilot21_09.ac

git mv ./data/pilot/pilot21/Gold/Unit/pilot21_10_petersen_u_28122012.aa ./data/pilot/pilot21/Gold/Unit/pilot21_10.aa
git mv ./data/pilot/pilot21/Gold/Unit/pilot21_11_petersen_u_2012013.aa ./data/pilot/pilot21/Gold/Unit/pilot21_11.aa
git mv ./data/pilot/pilot21/Gold/Unit/pilot21_12_joseph_u_2801.aa ./data/pilot/pilot21/Gold/Unit/pilot21_12.aa
git mv ./data/pilot/pilot21/Gold/Unit/pilot21_1_petersen_u_27122012.aa ./data/pilot/pilot21/Gold/Unit/pilot21_01.aa
git mv ./data/pilot/pilot21/Gold/Unit/pilot21_2_petersen_u_27122012.aa ./data/pilot/pilot21/Gold/Unit/pilot21_02.aa
git mv ./data/pilot/pilot21/Gold/Unit/pilot21_3_joseph_u_1701.aa ./data/pilot/pilot21/Gold/Unit/pilot21_03.aa
git mv ./data/pilot/pilot21/Gold/Unit/pilot21_4_petersen_u_27122012.aa ./data/pilot/pilot21/Gold/Unit/pilot21_04.aa
git mv ./data/pilot/pilot21/Gold/Unit/pilot21_5_petersen_u_27122012.aa ./data/pilot/pilot21/Gold/Unit/pilot21_05.aa
git mv ./data/pilot/pilot21/Gold/Unit/pilot21_6_joseph_u_2201.aa ./data/pilot/pilot21/Gold/Unit/pilot21_06.aa
git mv ./data/pilot/pilot21/Gold/Unit/pilot21_7_petersen_u_27122012.aa ./data/pilot/pilot21/Gold/Unit/pilot21_07.aa
git mv ./data/pilot/pilot21/Gold/Unit/pilot21_8_petersen_u_28122012.aa ./data/pilot/pilot21/Gold/Unit/pilot21_08.aa
git mv ./data/pilot/pilot21/Gold/Unit/pilot21_9_joseph_u_2401.aa ./data/pilot/pilot21/Gold/Unit/pilot21_09.aa

git mv ./data/pilot/pilot21/Gold/Unit_Pred_Arg/pilot21_1.ac_petersen.seg ./data/pilot/pilot21/Gold/Unit_Pred_Arg/pilot21_01.ac.seg
git mv ./data/pilot/pilot21/Gold/Unit_Pred_Arg/pilot21_10.ac_petersen.seg ./data/pilot/pilot21/Gold/Unit_Pred_Arg/pilot21_10.ac.seg
git mv ./data/pilot/pilot21/Gold/Unit_Pred_Arg/pilot21_11.ac_petersen.seg ./data/pilot/pilot21/Gold/Unit_Pred_Arg/pilot21_11.ac.seg
git mv ./data/pilot/pilot21/Gold/Unit_Pred_Arg/pilot21_12.ac_joseph.seg ./data/pilot/pilot21/Gold/Unit_Pred_Arg/pilot21_12.ac.seg
git mv ./data/pilot/pilot21/Gold/Unit_Pred_Arg/pilot21_2.ac_petersen.seg ./data/pilot/pilot21/Gold/Unit_Pred_Arg/pilot21_02.ac.seg
git mv ./data/pilot/pilot21/Gold/Unit_Pred_Arg/pilot21_3.ac_joseph.seg ./data/pilot/pilot21/Gold/Unit_Pred_Arg/pilot21_03.ac.seg
git mv ./data/pilot/pilot21/Gold/Unit_Pred_Arg/pilot21_4.ac_petersen.seg ./data/pilot/pilot21/Gold/Unit_Pred_Arg/pilot21_04.ac.seg
git mv ./data/pilot/pilot21/Gold/Unit_Pred_Arg/pilot21_5.ac_petersen.seg ./data/pilot/pilot21/Gold/Unit_Pred_Arg/pilot21_05.ac.seg
git mv ./data/pilot/pilot21/Gold/Unit_Pred_Arg/pilot21_6.ac_joseph.seg ./data/pilot/pilot21/Gold/Unit_Pred_Arg/pilot21_06.ac.seg
git mv ./data/pilot/pilot21/Gold/Unit_Pred_Arg/pilot21_7.ac_petersen.seg ./data/pilot/pilot21/Gold/Unit_Pred_Arg/pilot21_07.ac.seg
git mv ./data/pilot/pilot21/Gold/Unit_Pred_Arg/pilot21_8.ac_petersen.seg ./data/pilot/pilot21/Gold/Unit_Pred_Arg/pilot21_08.ac.seg
git mv ./data/pilot/pilot21/Gold/Unit_Pred_Arg/pilot21_9.ac_joseph.seg ./data/pilot/pilot21/Gold/Unit_Pred_Arg/pilot21_09.ac.seg

git mv ./data/pilot/pilot21/pred_arg_annotations/petersen/discourse/pilot21_1.ac_petersen.rel ./data/pilot/pilot21/pred_arg_annotations/petersen/discourse/pilot21_01.ac.rel
git mv ./data/pilot/pilot21/pred_arg_annotations/petersen/discourse/pilot21_10.ac_petersen.rel ./data/pilot/pilot21/pred_arg_annotations/petersen/discourse/pilot21_10.ac.rel
git mv ./data/pilot/pilot21/pred_arg_annotations/petersen/discourse/pilot21_11.ac_petersen.rel ./data/pilot/pilot21/pred_arg_annotations/petersen/discourse/pilot21_11.ac.rel
git mv ./data/pilot/pilot21/pred_arg_annotations/petersen/discourse/pilot21_2.ac_petersen.rel ./data/pilot/pilot21/pred_arg_annotations/petersen/discourse/pilot21_02.ac.rel
git mv ./data/pilot/pilot21/pred_arg_annotations/petersen/discourse/pilot21_4.ac_petersen.rel ./data/pilot/pilot21/pred_arg_annotations/petersen/discourse/pilot21_04.ac.rel
git mv ./data/pilot/pilot21/pred_arg_annotations/petersen/discourse/pilot21_5.ac_petersen.rel ./data/pilot/pilot21/pred_arg_annotations/petersen/discourse/pilot21_05.ac.rel
git mv ./data/pilot/pilot21/pred_arg_annotations/petersen/discourse/pilot21_7.ac_petersen.rel ./data/pilot/pilot21/pred_arg_annotations/petersen/discourse/pilot21_07.ac.rel
git mv ./data/pilot/pilot21/pred_arg_annotations/petersen/discourse/pilot21_8.ac_petersen.rel ./data/pilot/pilot21/pred_arg_annotations/petersen/discourse/pilot21_08.ac.rel

git mv ./data/pilot/pilot21/pred_arg_annotations/petersen/unit/pilot21_1.ac_petersen.seg ./data/pilot/pilot21/pred_arg_annotations/petersen/unit/pilot21_01.ac.seg
git mv ./data/pilot/pilot21/pred_arg_annotations/petersen/unit/pilot21_10.ac_petersen.seg ./data/pilot/pilot21/pred_arg_annotations/petersen/unit/pilot21_10.ac.seg
git mv ./data/pilot/pilot21/pred_arg_annotations/petersen/unit/pilot21_11.ac_petersen.seg ./data/pilot/pilot21/pred_arg_annotations/petersen/unit/pilot21_11.ac.seg
git mv ./data/pilot/pilot21/pred_arg_annotations/petersen/unit/pilot21_2.ac_petersen.seg ./data/pilot/pilot21/pred_arg_annotations/petersen/unit/pilot21_02.ac.seg
git mv ./data/pilot/pilot21/pred_arg_annotations/petersen/unit/pilot21_4.ac_petersen.seg ./data/pilot/pilot21/pred_arg_annotations/petersen/unit/pilot21_04.ac.seg
git mv ./data/pilot/pilot21/pred_arg_annotations/petersen/unit/pilot21_5.ac_petersen.seg ./data/pilot/pilot21/pred_arg_annotations/petersen/unit/pilot21_05.ac.seg
git mv ./data/pilot/pilot21/pred_arg_annotations/petersen/unit/pilot21_7.ac_petersen.seg ./data/pilot/pilot21/pred_arg_annotations/petersen/unit/pilot21_07.ac.seg
git mv ./data/pilot/pilot21/pred_arg_annotations/petersen/unit/pilot21_8.ac_petersen.seg ./data/pilot/pilot21/pred_arg_annotations/petersen/unit/pilot21_08.ac.seg

# ======================================================================
# directory renames
# no tool names or formats
# ======================================================================

git mv ./data/pilot/pilot01/glozz_preannotation ./data/pilot/pilot01/unannotated
git mv ./data/pilot/pilot01/segmented_csv ./data/pilot/pilot01/segmented
git mv ./data/pilot/pilot02/glozz_preannotation ./data/pilot/pilot02/unannotated
git mv ./data/pilot/pilot02/segmented_csv ./data/pilot/pilot02/segmented
git mv ./data/pilot/pilot03/glozz_preannotation ./data/pilot/pilot03/unannotated
git mv ./data/pilot/pilot03/segmented_csv ./data/pilot/pilot03/segmented
git mv ./data/pilot/pilot04/glozz_preannotation ./data/pilot/pilot04/unannotated
git mv ./data/pilot/pilot04/segmented_csv ./data/pilot/pilot04/segmented
git mv ./data/pilot/pilot14/glozz_preannotation ./data/pilot/pilot14/unannotated
git mv ./data/pilot/pilot14/segmented_csv ./data/pilot/pilot14/segmented
git mv ./data/pilot/pilot20/glozz_preannotation ./data/pilot/pilot20/unannotated
git mv ./data/pilot/pilot20/segmented_csv ./data/pilot/pilot20/segmented
git mv ./data/pilot/pilot21/glozz_preannotation ./data/pilot/pilot21/unannotated
git mv ./data/pilot/pilot21/segmented_csv ./data/pilot/pilot21/segmented

# ======================================================================
# glozz usage: put aam files in right place, link for easier use
# ======================================================================

git mv glozz_tool/pilot01.aam ./data/pilot/pilot01/pilot01.aam
git mv glozz_tool/pilot02.aam ./data/pilot/pilot02/pilot02.aam
git mv glozz_tool/pilot03.aam ./data/pilot/pilot03/pilot03.aam
git mv glozz_tool/pilot04.aam ./data/pilot/pilot04/pilot04.aam
git mv glozz_tool/pilot14.aam ./data/pilot/pilot14/pilot14.aam
git mv glozz_tool/pilot20.aam ./data/pilot/pilot20/pilot20.aam
git mv glozz_tool/pilot21.aam ./data/pilot/pilot21/pilot21.aam

# ======================================================================
# hierarchy simplification: flatten, put processing stages first
# duplicate deletion: replace duplicate ac files with symlinks
# ======================================================================


# --------------------------------------------------
# ./data/pilot/pilot01/glozz_annotations
# --------------------------------------------------

mkdir -p ./data/pilot/pilot01/units
mkdir -p ./data/pilot/pilot01/discourse
git mv ./data/pilot/pilot01/glozz_annotations/hjoseph/discourse ./data/pilot/pilot01/discourse/hjoseph
(git rm -f ./data/pilot/pilot01/discourse/hjoseph/*.ac || :); mkdir -p ./data/pilot/pilot01/discourse/hjoseph
pushd ./data/pilot/pilot01/discourse/hjoseph
if [ ! -z `ls ../../unannotated/*.ac | head -n 1` ]; then ln -s ../../unannotated/*.ac .; fi
if [ ! -z `ls ../../*.aam | head -n 1` ]; then ln -s ../../*.aam .; fi
popd
git add ./data/pilot/pilot01/discourse/hjoseph/*.{ac,aam}
git mv ./data/pilot/pilot01/glozz_annotations/hjoseph/units ./data/pilot/pilot01/units/hjoseph
(git rm -f ./data/pilot/pilot01/units/hjoseph/*.ac || :); mkdir -p ./data/pilot/pilot01/units/hjoseph
pushd ./data/pilot/pilot01/units/hjoseph
if [ ! -z `ls ../../unannotated/*.ac | head -n 1` ]; then ln -s ../../unannotated/*.ac .; fi
if [ ! -z `ls ../../*.aam | head -n 1` ]; then ln -s ../../*.aam .; fi
popd
git add ./data/pilot/pilot01/units/hjoseph/*.{ac,aam}
git mv ./data/pilot/pilot01/glozz_annotations/jhall/discourse ./data/pilot/pilot01/discourse/jhall
(git rm -f ./data/pilot/pilot01/discourse/jhall/*.ac || :); mkdir -p ./data/pilot/pilot01/discourse/jhall
pushd ./data/pilot/pilot01/discourse/jhall
if [ ! -z `ls ../../unannotated/*.ac | head -n 1` ]; then ln -s ../../unannotated/*.ac .; fi
if [ ! -z `ls ../../*.aam | head -n 1` ]; then ln -s ../../*.aam .; fi
popd
git add ./data/pilot/pilot01/discourse/jhall/*.{ac,aam}
git mv ./data/pilot/pilot01/glozz_annotations/jhall/units ./data/pilot/pilot01/units/jhall
(git rm -f ./data/pilot/pilot01/units/jhall/*.ac || :); mkdir -p ./data/pilot/pilot01/units/jhall
pushd ./data/pilot/pilot01/units/jhall
if [ ! -z `ls ../../unannotated/*.ac | head -n 1` ]; then ln -s ../../unannotated/*.ac .; fi
if [ ! -z `ls ../../*.aam | head -n 1` ]; then ln -s ../../*.aam .; fi
popd
git add ./data/pilot/pilot01/units/jhall/*.{ac,aam}
git mv ./data/pilot/pilot01/glozz_annotations/lpetersen/discourse ./data/pilot/pilot01/discourse/lpetersen
(git rm -f ./data/pilot/pilot01/discourse/lpetersen/*.ac || :); mkdir -p ./data/pilot/pilot01/discourse/lpetersen
pushd ./data/pilot/pilot01/discourse/lpetersen
if [ ! -z `ls ../../unannotated/*.ac | head -n 1` ]; then ln -s ../../unannotated/*.ac .; fi
if [ ! -z `ls ../../*.aam | head -n 1` ]; then ln -s ../../*.aam .; fi
popd
git add ./data/pilot/pilot01/discourse/lpetersen/*.{ac,aam}
git mv ./data/pilot/pilot01/glozz_annotations/lpetersen/units ./data/pilot/pilot01/units/lpetersen
(git rm -f ./data/pilot/pilot01/units/lpetersen/*.ac || :); mkdir -p ./data/pilot/pilot01/units/lpetersen
pushd ./data/pilot/pilot01/units/lpetersen
if [ ! -z `ls ../../unannotated/*.ac | head -n 1` ]; then ln -s ../../unannotated/*.ac .; fi
if [ ! -z `ls ../../*.aam | head -n 1` ]; then ln -s ../../*.aam .; fi
popd
git add ./data/pilot/pilot01/units/lpetersen/*.{ac,aam}
git mv ./data/pilot/pilot01/glozz_annotations/mhunt/discourse ./data/pilot/pilot01/discourse/mhunt
(git rm -f ./data/pilot/pilot01/discourse/mhunt/*.ac || :); mkdir -p ./data/pilot/pilot01/discourse/mhunt
pushd ./data/pilot/pilot01/discourse/mhunt
if [ ! -z `ls ../../unannotated/*.ac | head -n 1` ]; then ln -s ../../unannotated/*.ac .; fi
if [ ! -z `ls ../../*.aam | head -n 1` ]; then ln -s ../../*.aam .; fi
popd
git add ./data/pilot/pilot01/discourse/mhunt/*.{ac,aam}
git mv ./data/pilot/pilot01/glozz_annotations/mhunt/units ./data/pilot/pilot01/units/mhunt
(git rm -f ./data/pilot/pilot01/units/mhunt/*.ac || :); mkdir -p ./data/pilot/pilot01/units/mhunt
pushd ./data/pilot/pilot01/units/mhunt
if [ ! -z `ls ../../unannotated/*.ac | head -n 1` ]; then ln -s ../../unannotated/*.ac .; fi
if [ ! -z `ls ../../*.aam | head -n 1` ]; then ln -s ../../*.aam .; fi
popd
git add ./data/pilot/pilot01/units/mhunt/*.{ac,aam}
git mv ./data/pilot/pilot01/Gold/Unit ./data/pilot/pilot01/units/GOLD
(git rm -f ./data/pilot/pilot01/units/GOLD/*.ac || :); mkdir -p ./data/pilot/pilot01/units/GOLD
pushd ./data/pilot/pilot01/units/GOLD
if [ ! -z `ls ../../unannotated/*.ac | head -n 1` ]; then ln -s ../../unannotated/*.ac .; fi
if [ ! -z `ls ../../*.aam | head -n 1` ]; then ln -s ../../*.aam .; fi
popd
git add ./data/pilot/pilot01/units/GOLD/*.{ac,aam}

# --------------------------------------------------
# ./data/pilot/pilot02/glozz_annotations
# --------------------------------------------------

mkdir -p ./data/pilot/pilot02/units
mkdir -p ./data/pilot/pilot02/discourse
git mv ./data/pilot/pilot02/glozz_annotations/hjoseph/discourse ./data/pilot/pilot02/discourse/hjoseph
(git rm -f ./data/pilot/pilot02/discourse/hjoseph/*.ac || :); mkdir -p ./data/pilot/pilot02/discourse/hjoseph
pushd ./data/pilot/pilot02/discourse/hjoseph
if [ ! -z `ls ../../unannotated/*.ac | head -n 1` ]; then ln -s ../../unannotated/*.ac .; fi
if [ ! -z `ls ../../*.aam | head -n 1` ]; then ln -s ../../*.aam .; fi
popd
git add ./data/pilot/pilot02/discourse/hjoseph/*.{ac,aam}
git mv ./data/pilot/pilot02/glozz_annotations/hjoseph/units ./data/pilot/pilot02/units/hjoseph
(git rm -f ./data/pilot/pilot02/units/hjoseph/*.ac || :); mkdir -p ./data/pilot/pilot02/units/hjoseph
pushd ./data/pilot/pilot02/units/hjoseph
if [ ! -z `ls ../../unannotated/*.ac | head -n 1` ]; then ln -s ../../unannotated/*.ac .; fi
if [ ! -z `ls ../../*.aam | head -n 1` ]; then ln -s ../../*.aam .; fi
popd
git add ./data/pilot/pilot02/units/hjoseph/*.{ac,aam}
git mv ./data/pilot/pilot02/glozz_annotations/lpetersen/discourse ./data/pilot/pilot02/discourse/lpetersen
(git rm -f ./data/pilot/pilot02/discourse/lpetersen/*.ac || :); mkdir -p ./data/pilot/pilot02/discourse/lpetersen
pushd ./data/pilot/pilot02/discourse/lpetersen
if [ ! -z `ls ../../unannotated/*.ac | head -n 1` ]; then ln -s ../../unannotated/*.ac .; fi
if [ ! -z `ls ../../*.aam | head -n 1` ]; then ln -s ../../*.aam .; fi
popd
git add ./data/pilot/pilot02/discourse/lpetersen/*.{ac,aam}
git mv ./data/pilot/pilot02/glozz_annotations/lpetersen/units ./data/pilot/pilot02/units/lpetersen
(git rm -f ./data/pilot/pilot02/units/lpetersen/*.ac || :); mkdir -p ./data/pilot/pilot02/units/lpetersen
pushd ./data/pilot/pilot02/units/lpetersen
if [ ! -z `ls ../../unannotated/*.ac | head -n 1` ]; then ln -s ../../unannotated/*.ac .; fi
if [ ! -z `ls ../../*.aam | head -n 1` ]; then ln -s ../../*.aam .; fi
popd
git add ./data/pilot/pilot02/units/lpetersen/*.{ac,aam}
git mv ./data/pilot/pilot02/Gold/Units ./data/pilot/pilot02/units/GOLD
(git rm -f ./data/pilot/pilot02/units/GOLD/*.ac || :); mkdir -p ./data/pilot/pilot02/units/GOLD
pushd ./data/pilot/pilot02/units/GOLD
if [ ! -z `ls ../../unannotated/*.ac | head -n 1` ]; then ln -s ../../unannotated/*.ac .; fi
if [ ! -z `ls ../../*.aam | head -n 1` ]; then ln -s ../../*.aam .; fi
popd
git add ./data/pilot/pilot02/units/GOLD/*.{ac,aam}

# --------------------------------------------------
# ./data/pilot/pilot03/glozz_annotations
# --------------------------------------------------

mkdir -p ./data/pilot/pilot03/units
mkdir -p ./data/pilot/pilot03/discourse
git mv ./data/pilot/pilot03/glozz_annotations/hjoseph/discourse ./data/pilot/pilot03/discourse/hjoseph
(git rm -f ./data/pilot/pilot03/discourse/hjoseph/*.ac || :); mkdir -p ./data/pilot/pilot03/discourse/hjoseph
pushd ./data/pilot/pilot03/discourse/hjoseph
if [ ! -z `ls ../../unannotated/*.ac | head -n 1` ]; then ln -s ../../unannotated/*.ac .; fi
if [ ! -z `ls ../../*.aam | head -n 1` ]; then ln -s ../../*.aam .; fi
popd
git add ./data/pilot/pilot03/discourse/hjoseph/*.{ac,aam}
git mv ./data/pilot/pilot03/glozz_annotations/hjoseph/units ./data/pilot/pilot03/units/hjoseph
(git rm -f ./data/pilot/pilot03/units/hjoseph/*.ac || :); mkdir -p ./data/pilot/pilot03/units/hjoseph
pushd ./data/pilot/pilot03/units/hjoseph
if [ ! -z `ls ../../unannotated/*.ac | head -n 1` ]; then ln -s ../../unannotated/*.ac .; fi
if [ ! -z `ls ../../*.aam | head -n 1` ]; then ln -s ../../*.aam .; fi
popd
git add ./data/pilot/pilot03/units/hjoseph/*.{ac,aam}
git mv ./data/pilot/pilot03/glozz_annotations/jhall/discourse ./data/pilot/pilot03/discourse/jhall
(git rm -f ./data/pilot/pilot03/discourse/jhall/*.ac || :); mkdir -p ./data/pilot/pilot03/discourse/jhall
pushd ./data/pilot/pilot03/discourse/jhall
if [ ! -z `ls ../../unannotated/*.ac | head -n 1` ]; then ln -s ../../unannotated/*.ac .; fi
if [ ! -z `ls ../../*.aam | head -n 1` ]; then ln -s ../../*.aam .; fi
popd
git add ./data/pilot/pilot03/discourse/jhall/*.{ac,aam}
git mv ./data/pilot/pilot03/glozz_annotations/jhall/units ./data/pilot/pilot03/units/jhall
(git rm -f ./data/pilot/pilot03/units/jhall/*.ac || :); mkdir -p ./data/pilot/pilot03/units/jhall
pushd ./data/pilot/pilot03/units/jhall
if [ ! -z `ls ../../unannotated/*.ac | head -n 1` ]; then ln -s ../../unannotated/*.ac .; fi
if [ ! -z `ls ../../*.aam | head -n 1` ]; then ln -s ../../*.aam .; fi
popd
git add ./data/pilot/pilot03/units/jhall/*.{ac,aam}
git mv ./data/pilot/pilot03/glozz_annotations/lpetersen/discourse ./data/pilot/pilot03/discourse/lpetersen
(git rm -f ./data/pilot/pilot03/discourse/lpetersen/*.ac || :); mkdir -p ./data/pilot/pilot03/discourse/lpetersen
pushd ./data/pilot/pilot03/discourse/lpetersen
if [ ! -z `ls ../../unannotated/*.ac | head -n 1` ]; then ln -s ../../unannotated/*.ac .; fi
if [ ! -z `ls ../../*.aam | head -n 1` ]; then ln -s ../../*.aam .; fi
popd
git add ./data/pilot/pilot03/discourse/lpetersen/*.{ac,aam}
git mv ./data/pilot/pilot03/glozz_annotations/lpetersen/units ./data/pilot/pilot03/units/lpetersen
(git rm -f ./data/pilot/pilot03/units/lpetersen/*.ac || :); mkdir -p ./data/pilot/pilot03/units/lpetersen
pushd ./data/pilot/pilot03/units/lpetersen
if [ ! -z `ls ../../unannotated/*.ac | head -n 1` ]; then ln -s ../../unannotated/*.ac .; fi
if [ ! -z `ls ../../*.aam | head -n 1` ]; then ln -s ../../*.aam .; fi
popd
git add ./data/pilot/pilot03/units/lpetersen/*.{ac,aam}
git mv ./data/pilot/pilot03/glozz_annotations/mhunt/discourse ./data/pilot/pilot03/discourse/mhunt
(git rm -f ./data/pilot/pilot03/discourse/mhunt/*.ac || :); mkdir -p ./data/pilot/pilot03/discourse/mhunt
pushd ./data/pilot/pilot03/discourse/mhunt
if [ ! -z `ls ../../unannotated/*.ac | head -n 1` ]; then ln -s ../../unannotated/*.ac .; fi
if [ ! -z `ls ../../*.aam | head -n 1` ]; then ln -s ../../*.aam .; fi
popd
git add ./data/pilot/pilot03/discourse/mhunt/*.{ac,aam}
git mv ./data/pilot/pilot03/glozz_annotations/mhunt/units ./data/pilot/pilot03/units/mhunt
(git rm -f ./data/pilot/pilot03/units/mhunt/*.ac || :); mkdir -p ./data/pilot/pilot03/units/mhunt
pushd ./data/pilot/pilot03/units/mhunt
if [ ! -z `ls ../../unannotated/*.ac | head -n 1` ]; then ln -s ../../unannotated/*.ac .; fi
if [ ! -z `ls ../../*.aam | head -n 1` ]; then ln -s ../../*.aam .; fi
popd
git add ./data/pilot/pilot03/units/mhunt/*.{ac,aam}
git mv ./data/pilot/pilot03/Gold/Unit ./data/pilot/pilot03/units/GOLD
(git rm -f ./data/pilot/pilot03/units/GOLD/*.ac || :); mkdir -p ./data/pilot/pilot03/units/GOLD
pushd ./data/pilot/pilot03/units/GOLD
if [ ! -z `ls ../../unannotated/*.ac | head -n 1` ]; then ln -s ../../unannotated/*.ac .; fi
if [ ! -z `ls ../../*.aam | head -n 1` ]; then ln -s ../../*.aam .; fi
popd
git add ./data/pilot/pilot03/units/GOLD/*.{ac,aam}

# --------------------------------------------------
# ./data/pilot/pilot04/glozz_annotations
# --------------------------------------------------

mkdir -p ./data/pilot/pilot04/units
mkdir -p ./data/pilot/pilot04/discourse
git mv ./data/pilot/pilot04/glozz_annotations/hjoseph/discourse ./data/pilot/pilot04/discourse/hjoseph
(git rm -f ./data/pilot/pilot04/discourse/hjoseph/*.ac || :); mkdir -p ./data/pilot/pilot04/discourse/hjoseph
pushd ./data/pilot/pilot04/discourse/hjoseph
if [ ! -z `ls ../../unannotated/*.ac | head -n 1` ]; then ln -s ../../unannotated/*.ac .; fi
if [ ! -z `ls ../../*.aam | head -n 1` ]; then ln -s ../../*.aam .; fi
popd
git add ./data/pilot/pilot04/discourse/hjoseph/*.{ac,aam}
git mv ./data/pilot/pilot04/glozz_annotations/hjoseph/units ./data/pilot/pilot04/units/hjoseph
(git rm -f ./data/pilot/pilot04/units/hjoseph/*.ac || :); mkdir -p ./data/pilot/pilot04/units/hjoseph
pushd ./data/pilot/pilot04/units/hjoseph
if [ ! -z `ls ../../unannotated/*.ac | head -n 1` ]; then ln -s ../../unannotated/*.ac .; fi
if [ ! -z `ls ../../*.aam | head -n 1` ]; then ln -s ../../*.aam .; fi
popd
git add ./data/pilot/pilot04/units/hjoseph/*.{ac,aam}
git mv ./data/pilot/pilot04/glozz_annotations/jhall/discourse ./data/pilot/pilot04/discourse/jhall
(git rm -f ./data/pilot/pilot04/discourse/jhall/*.ac || :); mkdir -p ./data/pilot/pilot04/discourse/jhall
pushd ./data/pilot/pilot04/discourse/jhall
if [ ! -z `ls ../../unannotated/*.ac | head -n 1` ]; then ln -s ../../unannotated/*.ac .; fi
if [ ! -z `ls ../../*.aam | head -n 1` ]; then ln -s ../../*.aam .; fi
popd
git add ./data/pilot/pilot04/discourse/jhall/*.{ac,aam}
git mv ./data/pilot/pilot04/glozz_annotations/jhall/units ./data/pilot/pilot04/units/jhall
(git rm -f ./data/pilot/pilot04/units/jhall/*.ac || :); mkdir -p ./data/pilot/pilot04/units/jhall
pushd ./data/pilot/pilot04/units/jhall
if [ ! -z `ls ../../unannotated/*.ac | head -n 1` ]; then ln -s ../../unannotated/*.ac .; fi
if [ ! -z `ls ../../*.aam | head -n 1` ]; then ln -s ../../*.aam .; fi
popd
git add ./data/pilot/pilot04/units/jhall/*.{ac,aam}
git mv ./data/pilot/pilot04/glozz_annotations/lpetersen/discourse ./data/pilot/pilot04/discourse/lpetersen
(git rm -f ./data/pilot/pilot04/discourse/lpetersen/*.ac || :); mkdir -p ./data/pilot/pilot04/discourse/lpetersen
pushd ./data/pilot/pilot04/discourse/lpetersen
if [ ! -z `ls ../../unannotated/*.ac | head -n 1` ]; then ln -s ../../unannotated/*.ac .; fi
if [ ! -z `ls ../../*.aam | head -n 1` ]; then ln -s ../../*.aam .; fi
popd
git add ./data/pilot/pilot04/discourse/lpetersen/*.{ac,aam}
git mv ./data/pilot/pilot04/glozz_annotations/lpetersen/units ./data/pilot/pilot04/units/lpetersen
(git rm -f ./data/pilot/pilot04/units/lpetersen/*.ac || :); mkdir -p ./data/pilot/pilot04/units/lpetersen
pushd ./data/pilot/pilot04/units/lpetersen
if [ ! -z `ls ../../unannotated/*.ac | head -n 1` ]; then ln -s ../../unannotated/*.ac .; fi
if [ ! -z `ls ../../*.aam | head -n 1` ]; then ln -s ../../*.aam .; fi
popd
git add ./data/pilot/pilot04/units/lpetersen/*.{ac,aam}
git mv ./data/pilot/pilot04/glozz_annotations/mhunt/discourse ./data/pilot/pilot04/discourse/mhunt
(git rm -f ./data/pilot/pilot04/discourse/mhunt/*.ac || :); mkdir -p ./data/pilot/pilot04/discourse/mhunt
pushd ./data/pilot/pilot04/discourse/mhunt
if [ ! -z `ls ../../unannotated/*.ac | head -n 1` ]; then ln -s ../../unannotated/*.ac .; fi
if [ ! -z `ls ../../*.aam | head -n 1` ]; then ln -s ../../*.aam .; fi
popd
git add ./data/pilot/pilot04/discourse/mhunt/*.{ac,aam}
git mv ./data/pilot/pilot04/glozz_annotations/mhunt/units ./data/pilot/pilot04/units/mhunt
(git rm -f ./data/pilot/pilot04/units/mhunt/*.ac || :); mkdir -p ./data/pilot/pilot04/units/mhunt
pushd ./data/pilot/pilot04/units/mhunt
if [ ! -z `ls ../../unannotated/*.ac | head -n 1` ]; then ln -s ../../unannotated/*.ac .; fi
if [ ! -z `ls ../../*.aam | head -n 1` ]; then ln -s ../../*.aam .; fi
popd
git add ./data/pilot/pilot04/units/mhunt/*.{ac,aam}
git mv ./data/pilot/pilot04/Gold/Unit ./data/pilot/pilot04/units/GOLD
(git rm -f ./data/pilot/pilot04/units/GOLD/*.ac || :); mkdir -p ./data/pilot/pilot04/units/GOLD
pushd ./data/pilot/pilot04/units/GOLD
if [ ! -z `ls ../../unannotated/*.ac | head -n 1` ]; then ln -s ../../unannotated/*.ac .; fi
if [ ! -z `ls ../../*.aam | head -n 1` ]; then ln -s ../../*.aam .; fi
popd
git add ./data/pilot/pilot04/units/GOLD/*.{ac,aam}

# --------------------------------------------------
# ./data/pilot/pilot14/glozz_annotations
# --------------------------------------------------

mkdir -p ./data/pilot/pilot14/units
mkdir -p ./data/pilot/pilot14/discourse
git mv ./data/pilot/pilot14/glozz_annotations/hjoseph/discourse ./data/pilot/pilot14/discourse/hjoseph
(git rm -f ./data/pilot/pilot14/discourse/hjoseph/*.ac || :); mkdir -p ./data/pilot/pilot14/discourse/hjoseph
pushd ./data/pilot/pilot14/discourse/hjoseph
if [ ! -z `ls ../../unannotated/*.ac | head -n 1` ]; then ln -s ../../unannotated/*.ac .; fi
if [ ! -z `ls ../../*.aam | head -n 1` ]; then ln -s ../../*.aam .; fi
popd
git add ./data/pilot/pilot14/discourse/hjoseph/*.{ac,aam}
git mv ./data/pilot/pilot14/glozz_annotations/hjoseph/units ./data/pilot/pilot14/units/hjoseph
(git rm -f ./data/pilot/pilot14/units/hjoseph/*.ac || :); mkdir -p ./data/pilot/pilot14/units/hjoseph
pushd ./data/pilot/pilot14/units/hjoseph
if [ ! -z `ls ../../unannotated/*.ac | head -n 1` ]; then ln -s ../../unannotated/*.ac .; fi
if [ ! -z `ls ../../*.aam | head -n 1` ]; then ln -s ../../*.aam .; fi
popd
git add ./data/pilot/pilot14/units/hjoseph/*.{ac,aam}
git mv ./data/pilot/pilot14/glozz_annotations/jhall/discourse ./data/pilot/pilot14/discourse/jhall
(git rm -f ./data/pilot/pilot14/discourse/jhall/*.ac || :); mkdir -p ./data/pilot/pilot14/discourse/jhall
pushd ./data/pilot/pilot14/discourse/jhall
if [ ! -z `ls ../../unannotated/*.ac | head -n 1` ]; then ln -s ../../unannotated/*.ac .; fi
if [ ! -z `ls ../../*.aam | head -n 1` ]; then ln -s ../../*.aam .; fi
popd
git add ./data/pilot/pilot14/discourse/jhall/*.{ac,aam}
git mv ./data/pilot/pilot14/glozz_annotations/jhall/units ./data/pilot/pilot14/units/jhall
(git rm -f ./data/pilot/pilot14/units/jhall/*.ac || :); mkdir -p ./data/pilot/pilot14/units/jhall
pushd ./data/pilot/pilot14/units/jhall
if [ ! -z `ls ../../unannotated/*.ac | head -n 1` ]; then ln -s ../../unannotated/*.ac .; fi
if [ ! -z `ls ../../*.aam | head -n 1` ]; then ln -s ../../*.aam .; fi
popd
git add ./data/pilot/pilot14/units/jhall/*.{ac,aam}
git mv ./data/pilot/pilot14/glozz_annotations/lpetersen/discourse ./data/pilot/pilot14/discourse/lpetersen
(git rm -f ./data/pilot/pilot14/discourse/lpetersen/*.ac || :); mkdir -p ./data/pilot/pilot14/discourse/lpetersen
pushd ./data/pilot/pilot14/discourse/lpetersen
if [ ! -z `ls ../../unannotated/*.ac | head -n 1` ]; then ln -s ../../unannotated/*.ac .; fi
if [ ! -z `ls ../../*.aam | head -n 1` ]; then ln -s ../../*.aam .; fi
popd
git add ./data/pilot/pilot14/discourse/lpetersen/*.{ac,aam}
git mv ./data/pilot/pilot14/glozz_annotations/lpetersen/units ./data/pilot/pilot14/units/lpetersen
(git rm -f ./data/pilot/pilot14/units/lpetersen/*.ac || :); mkdir -p ./data/pilot/pilot14/units/lpetersen
pushd ./data/pilot/pilot14/units/lpetersen
if [ ! -z `ls ../../unannotated/*.ac | head -n 1` ]; then ln -s ../../unannotated/*.ac .; fi
if [ ! -z `ls ../../*.aam | head -n 1` ]; then ln -s ../../*.aam .; fi
popd
git add ./data/pilot/pilot14/units/lpetersen/*.{ac,aam}
git mv ./data/pilot/pilot14/glozz_annotations/mhunt/discourse ./data/pilot/pilot14/discourse/mhunt
(git rm -f ./data/pilot/pilot14/discourse/mhunt/*.ac || :); mkdir -p ./data/pilot/pilot14/discourse/mhunt
pushd ./data/pilot/pilot14/discourse/mhunt
if [ ! -z `ls ../../unannotated/*.ac | head -n 1` ]; then ln -s ../../unannotated/*.ac .; fi
if [ ! -z `ls ../../*.aam | head -n 1` ]; then ln -s ../../*.aam .; fi
popd
git add ./data/pilot/pilot14/discourse/mhunt/*.{ac,aam}
git mv ./data/pilot/pilot14/glozz_annotations/mhunt/units ./data/pilot/pilot14/units/mhunt
(git rm -f ./data/pilot/pilot14/units/mhunt/*.ac || :); mkdir -p ./data/pilot/pilot14/units/mhunt
pushd ./data/pilot/pilot14/units/mhunt
if [ ! -z `ls ../../unannotated/*.ac | head -n 1` ]; then ln -s ../../unannotated/*.ac .; fi
if [ ! -z `ls ../../*.aam | head -n 1` ]; then ln -s ../../*.aam .; fi
popd
git add ./data/pilot/pilot14/units/mhunt/*.{ac,aam}
git mv ./data/pilot/pilot14/Gold/Unit ./data/pilot/pilot14/units/GOLD
(git rm -f ./data/pilot/pilot14/units/GOLD/*.ac || :); mkdir -p ./data/pilot/pilot14/units/GOLD
pushd ./data/pilot/pilot14/units/GOLD
if [ ! -z `ls ../../unannotated/*.ac | head -n 1` ]; then ln -s ../../unannotated/*.ac .; fi
if [ ! -z `ls ../../*.aam | head -n 1` ]; then ln -s ../../*.aam .; fi
popd
git add ./data/pilot/pilot14/units/GOLD/*.{ac,aam}

# --------------------------------------------------
# ./data/pilot/pilot20/glozz_annotations
# --------------------------------------------------

mkdir -p ./data/pilot/pilot20/units
mkdir -p ./data/pilot/pilot20/discourse
git mv ./data/pilot/pilot20/glozz_annotations/hjoseph/discourse ./data/pilot/pilot20/discourse/hjoseph
(git rm -f ./data/pilot/pilot20/discourse/hjoseph/*.ac || :); mkdir -p ./data/pilot/pilot20/discourse/hjoseph
pushd ./data/pilot/pilot20/discourse/hjoseph
if [ ! -z `ls ../../unannotated/*.ac | head -n 1` ]; then ln -s ../../unannotated/*.ac .; fi
if [ ! -z `ls ../../*.aam | head -n 1` ]; then ln -s ../../*.aam .; fi
popd
git add ./data/pilot/pilot20/discourse/hjoseph/*.{ac,aam}
git mv ./data/pilot/pilot20/glozz_annotations/hjoseph/units ./data/pilot/pilot20/units/hjoseph
(git rm -f ./data/pilot/pilot20/units/hjoseph/*.ac || :); mkdir -p ./data/pilot/pilot20/units/hjoseph
pushd ./data/pilot/pilot20/units/hjoseph
if [ ! -z `ls ../../unannotated/*.ac | head -n 1` ]; then ln -s ../../unannotated/*.ac .; fi
if [ ! -z `ls ../../*.aam | head -n 1` ]; then ln -s ../../*.aam .; fi
popd
git add ./data/pilot/pilot20/units/hjoseph/*.{ac,aam}
git mv ./data/pilot/pilot20/glozz_annotations/jhall/discourse ./data/pilot/pilot20/discourse/jhall
(git rm -f ./data/pilot/pilot20/discourse/jhall/*.ac || :); mkdir -p ./data/pilot/pilot20/discourse/jhall
pushd ./data/pilot/pilot20/discourse/jhall
if [ ! -z `ls ../../unannotated/*.ac | head -n 1` ]; then ln -s ../../unannotated/*.ac .; fi
if [ ! -z `ls ../../*.aam | head -n 1` ]; then ln -s ../../*.aam .; fi
popd
git add ./data/pilot/pilot20/discourse/jhall/*.{ac,aam}
git mv ./data/pilot/pilot20/glozz_annotations/jhall/units ./data/pilot/pilot20/units/jhall
(git rm -f ./data/pilot/pilot20/units/jhall/*.ac || :); mkdir -p ./data/pilot/pilot20/units/jhall
pushd ./data/pilot/pilot20/units/jhall
if [ ! -z `ls ../../unannotated/*.ac | head -n 1` ]; then ln -s ../../unannotated/*.ac .; fi
if [ ! -z `ls ../../*.aam | head -n 1` ]; then ln -s ../../*.aam .; fi
popd
git add ./data/pilot/pilot20/units/jhall/*.{ac,aam}
git mv ./data/pilot/pilot20/glozz_annotations/lpetersen/discourse ./data/pilot/pilot20/discourse/lpetersen
(git rm -f ./data/pilot/pilot20/discourse/lpetersen/*.ac || :); mkdir -p ./data/pilot/pilot20/discourse/lpetersen
pushd ./data/pilot/pilot20/discourse/lpetersen
if [ ! -z `ls ../../unannotated/*.ac | head -n 1` ]; then ln -s ../../unannotated/*.ac .; fi
if [ ! -z `ls ../../*.aam | head -n 1` ]; then ln -s ../../*.aam .; fi
popd
git add ./data/pilot/pilot20/discourse/lpetersen/*.{ac,aam}
git mv ./data/pilot/pilot20/glozz_annotations/lpetersen/units ./data/pilot/pilot20/units/lpetersen
(git rm -f ./data/pilot/pilot20/units/lpetersen/*.ac || :); mkdir -p ./data/pilot/pilot20/units/lpetersen
pushd ./data/pilot/pilot20/units/lpetersen
if [ ! -z `ls ../../unannotated/*.ac | head -n 1` ]; then ln -s ../../unannotated/*.ac .; fi
if [ ! -z `ls ../../*.aam | head -n 1` ]; then ln -s ../../*.aam .; fi
popd
git add ./data/pilot/pilot20/units/lpetersen/*.{ac,aam}
git mv ./data/pilot/pilot20/glozz_annotations/mhunt/discourse ./data/pilot/pilot20/discourse/mhunt
(git rm -f ./data/pilot/pilot20/discourse/mhunt/*.ac || :); mkdir -p ./data/pilot/pilot20/discourse/mhunt
pushd ./data/pilot/pilot20/discourse/mhunt
if [ ! -z `ls ../../unannotated/*.ac | head -n 1` ]; then ln -s ../../unannotated/*.ac .; fi
if [ ! -z `ls ../../*.aam | head -n 1` ]; then ln -s ../../*.aam .; fi
popd
git add ./data/pilot/pilot20/discourse/mhunt/*.{ac,aam}
git mv ./data/pilot/pilot20/glozz_annotations/mhunt/units ./data/pilot/pilot20/units/mhunt
(git rm -f ./data/pilot/pilot20/units/mhunt/*.ac || :); mkdir -p ./data/pilot/pilot20/units/mhunt
pushd ./data/pilot/pilot20/units/mhunt
if [ ! -z `ls ../../unannotated/*.ac | head -n 1` ]; then ln -s ../../unannotated/*.ac .; fi
if [ ! -z `ls ../../*.aam | head -n 1` ]; then ln -s ../../*.aam .; fi
popd
git add ./data/pilot/pilot20/units/mhunt/*.{ac,aam}
git mv ./data/pilot/pilot20/Gold/Unit ./data/pilot/pilot20/units/GOLD
(git rm -f ./data/pilot/pilot20/units/GOLD/*.ac || :); mkdir -p ./data/pilot/pilot20/units/GOLD
pushd ./data/pilot/pilot20/units/GOLD
if [ ! -z `ls ../../unannotated/*.ac | head -n 1` ]; then ln -s ../../unannotated/*.ac .; fi
if [ ! -z `ls ../../*.aam | head -n 1` ]; then ln -s ../../*.aam .; fi
popd
git add ./data/pilot/pilot20/units/GOLD/*.{ac,aam}

# --------------------------------------------------
# ./data/pilot/pilot21/glozz_annotations
# --------------------------------------------------

mkdir -p ./data/pilot/pilot21/units
mkdir -p ./data/pilot/pilot21/discourse
git mv ./data/pilot/pilot21/glozz_annotations/hjoseph/discourse ./data/pilot/pilot21/discourse/hjoseph
(git rm -f ./data/pilot/pilot21/discourse/hjoseph/*.ac || :); mkdir -p ./data/pilot/pilot21/discourse/hjoseph
pushd ./data/pilot/pilot21/discourse/hjoseph
if [ ! -z `ls ../../unannotated/*.ac | head -n 1` ]; then ln -s ../../unannotated/*.ac .; fi
if [ ! -z `ls ../../*.aam | head -n 1` ]; then ln -s ../../*.aam .; fi
popd
git add ./data/pilot/pilot21/discourse/hjoseph/*.{ac,aam}
git mv ./data/pilot/pilot21/glozz_annotations/hjoseph/units ./data/pilot/pilot21/units/hjoseph
(git rm -f ./data/pilot/pilot21/units/hjoseph/*.ac || :); mkdir -p ./data/pilot/pilot21/units/hjoseph
pushd ./data/pilot/pilot21/units/hjoseph
if [ ! -z `ls ../../unannotated/*.ac | head -n 1` ]; then ln -s ../../unannotated/*.ac .; fi
if [ ! -z `ls ../../*.aam | head -n 1` ]; then ln -s ../../*.aam .; fi
popd
git add ./data/pilot/pilot21/units/hjoseph/*.{ac,aam}
git mv ./data/pilot/pilot21/glozz_annotations/jhall/discourse ./data/pilot/pilot21/discourse/jhall
(git rm -f ./data/pilot/pilot21/discourse/jhall/*.ac || :); mkdir -p ./data/pilot/pilot21/discourse/jhall
pushd ./data/pilot/pilot21/discourse/jhall
if [ ! -z `ls ../../unannotated/*.ac | head -n 1` ]; then ln -s ../../unannotated/*.ac .; fi
if [ ! -z `ls ../../*.aam | head -n 1` ]; then ln -s ../../*.aam .; fi
popd
git add ./data/pilot/pilot21/discourse/jhall/*.{ac,aam}
git mv ./data/pilot/pilot21/glozz_annotations/jhall/units ./data/pilot/pilot21/units/jhall
(git rm -f ./data/pilot/pilot21/units/jhall/*.ac || :); mkdir -p ./data/pilot/pilot21/units/jhall
pushd ./data/pilot/pilot21/units/jhall
if [ ! -z `ls ../../unannotated/*.ac | head -n 1` ]; then ln -s ../../unannotated/*.ac .; fi
if [ ! -z `ls ../../*.aam | head -n 1` ]; then ln -s ../../*.aam .; fi
popd
git add ./data/pilot/pilot21/units/jhall/*.{ac,aam}
git mv ./data/pilot/pilot21/glozz_annotations/lpetersen/discourse ./data/pilot/pilot21/discourse/lpetersen
(git rm -f ./data/pilot/pilot21/discourse/lpetersen/*.ac || :); mkdir -p ./data/pilot/pilot21/discourse/lpetersen
pushd ./data/pilot/pilot21/discourse/lpetersen
if [ ! -z `ls ../../unannotated/*.ac | head -n 1` ]; then ln -s ../../unannotated/*.ac .; fi
if [ ! -z `ls ../../*.aam | head -n 1` ]; then ln -s ../../*.aam .; fi
popd
git add ./data/pilot/pilot21/discourse/lpetersen/*.{ac,aam}
git mv ./data/pilot/pilot21/glozz_annotations/lpetersen/units ./data/pilot/pilot21/units/lpetersen
(git rm -f ./data/pilot/pilot21/units/lpetersen/*.ac || :); mkdir -p ./data/pilot/pilot21/units/lpetersen
pushd ./data/pilot/pilot21/units/lpetersen
if [ ! -z `ls ../../unannotated/*.ac | head -n 1` ]; then ln -s ../../unannotated/*.ac .; fi
if [ ! -z `ls ../../*.aam | head -n 1` ]; then ln -s ../../*.aam .; fi
popd
git add ./data/pilot/pilot21/units/lpetersen/*.{ac,aam}
git mv ./data/pilot/pilot21/glozz_annotations/mhunt/discourse ./data/pilot/pilot21/discourse/mhunt
(git rm -f ./data/pilot/pilot21/discourse/mhunt/*.ac || :); mkdir -p ./data/pilot/pilot21/discourse/mhunt
pushd ./data/pilot/pilot21/discourse/mhunt
if [ ! -z `ls ../../unannotated/*.ac | head -n 1` ]; then ln -s ../../unannotated/*.ac .; fi
if [ ! -z `ls ../../*.aam | head -n 1` ]; then ln -s ../../*.aam .; fi
popd
git add ./data/pilot/pilot21/discourse/mhunt/*.{ac,aam}
git mv ./data/pilot/pilot21/glozz_annotations/mhunt/units ./data/pilot/pilot21/units/mhunt
(git rm -f ./data/pilot/pilot21/units/mhunt/*.ac || :); mkdir -p ./data/pilot/pilot21/units/mhunt
pushd ./data/pilot/pilot21/units/mhunt
if [ ! -z `ls ../../unannotated/*.ac | head -n 1` ]; then ln -s ../../unannotated/*.ac .; fi
if [ ! -z `ls ../../*.aam | head -n 1` ]; then ln -s ../../*.aam .; fi
popd
git add ./data/pilot/pilot21/units/mhunt/*.{ac,aam}
git mv ./data/pilot/pilot21/Gold/Unit ./data/pilot/pilot21/units/GOLD
(git rm -f ./data/pilot/pilot21/units/GOLD/*.ac || :); mkdir -p ./data/pilot/pilot21/units/GOLD
pushd ./data/pilot/pilot21/units/GOLD
if [ ! -z `ls ../../unannotated/*.ac | head -n 1` ]; then ln -s ../../unannotated/*.ac .; fi
if [ ! -z `ls ../../*.aam | head -n 1` ]; then ln -s ../../*.aam .; fi
popd
git add ./data/pilot/pilot21/units/GOLD/*.{ac,aam}

# ======================================================================
# hierarchy simplification 2 (pred_arg_annotations)
# ======================================================================

mkdir -p ./data/pilot/pilot01/pred_arg_annotations/units
git mv ./data/pilot/pilot01/Gold/Unit_pred_arg ./data/pilot/pilot01/pred_arg_annotations/units/GOLD

# --------------------------------------------------
# ./data/pilot/pilot01/pred_arg_annotations
# --------------------------------------------------

mkdir -p ./data/pilot/pilot01/pred_arg_annotations/units
mkdir -p ./data/pilot/pilot01/pred_arg_annotations/discourse
git mv ./data/pilot/pilot01/pred_arg_annotations/joseph/discourse ./data/pilot/pilot01/pred_arg_annotations/discourse/hjoseph
git mv ./data/pilot/pilot01/pred_arg_annotations/joseph/unit ./data/pilot/pilot01/pred_arg_annotations/units/hjoseph
git mv ./data/pilot/pilot01/pred_arg_annotations/lpetersen/discourse ./data/pilot/pilot01/pred_arg_annotations/discourse/lpetersen
git mv ./data/pilot/pilot01/pred_arg_annotations/lpetersen/unit ./data/pilot/pilot01/pred_arg_annotations/units/lpetersen
mkdir -p ./data/pilot/pilot02/pred_arg_annotations/units
git mv ./data/pilot/pilot02/Gold/Unit_Pred_Arg ./data/pilot/pilot02/pred_arg_annotations/units/GOLD
mkdir -p ./data/pilot/pilot03/pred_arg_annotations/units
git mv ./data/pilot/pilot03/Gold/Unit_pred_arg ./data/pilot/pilot03/pred_arg_annotations/units/GOLD

# --------------------------------------------------
# ./data/pilot/pilot03/pred_arg_annotations
# --------------------------------------------------

mkdir -p ./data/pilot/pilot03/pred_arg_annotations/units
mkdir -p ./data/pilot/pilot03/pred_arg_annotations/discourse
git mv ./data/pilot/pilot03/pred_arg_annotations/hjoseph/discourse ./data/pilot/pilot03/pred_arg_annotations/discourse/hjoseph
git mv ./data/pilot/pilot03/pred_arg_annotations/hjoseph/unit ./data/pilot/pilot03/pred_arg_annotations/units/hjoseph
git mv ./data/pilot/pilot03/pred_arg_annotations/lpetersen/discourse ./data/pilot/pilot03/pred_arg_annotations/discourse/lpetersen
git mv ./data/pilot/pilot03/pred_arg_annotations/lpetersen/unit ./data/pilot/pilot03/pred_arg_annotations/units/lpetersen
mkdir -p ./data/pilot/pilot04/pred_arg_annotations/units
git mv ./data/pilot/pilot04/Gold/unit_pred_arg ./data/pilot/pilot04/pred_arg_annotations/units/GOLD

# --------------------------------------------------
# ./data/pilot/pilot04/pred_arg_annotations
# --------------------------------------------------

mkdir -p ./data/pilot/pilot04/pred_arg_annotations/units
mkdir -p ./data/pilot/pilot04/pred_arg_annotations/discourse
git mv ./data/pilot/pilot04/pred_arg_annotations/hjoseph/discourse ./data/pilot/pilot04/pred_arg_annotations/discourse/hjoseph
git mv ./data/pilot/pilot04/pred_arg_annotations/hjoseph/unit ./data/pilot/pilot04/pred_arg_annotations/units/hjoseph
git mv ./data/pilot/pilot04/pred_arg_annotations/lpetersen/discourse ./data/pilot/pilot04/pred_arg_annotations/discourse/lpetersen
git mv ./data/pilot/pilot04/pred_arg_annotations/lpetersen/unit ./data/pilot/pilot04/pred_arg_annotations/units/lpetersen
mkdir -p ./data/pilot/pilot14/pred_arg_annotations/units
git mv ./data/pilot/pilot14/Gold/Unit_pred_arg ./data/pilot/pilot14/pred_arg_annotations/units/GOLD

# --------------------------------------------------
# ./data/pilot/pilot14/pred_arg_annotations
# --------------------------------------------------

mkdir -p ./data/pilot/pilot14/pred_arg_annotations/units
mkdir -p ./data/pilot/pilot14/pred_arg_annotations/discourse
git mv ./data/pilot/pilot14/pred_arg_annotations/joseph/discourse ./data/pilot/pilot14/pred_arg_annotations/discourse/hjoseph
git mv ./data/pilot/pilot14/pred_arg_annotations/joseph/unit ./data/pilot/pilot14/pred_arg_annotations/units/hjoseph
git mv ./data/pilot/pilot14/pred_arg_annotations/petersen/discourse ./data/pilot/pilot14/pred_arg_annotations/discourse/lpetersen
git mv ./data/pilot/pilot14/pred_arg_annotations/petersen/unit ./data/pilot/pilot14/pred_arg_annotations/units/lpetersen
mkdir -p ./data/pilot/pilot20/pred_arg_annotations/units
git mv ./data/pilot/pilot20/Gold/Unit_Pred_Arg ./data/pilot/pilot20/pred_arg_annotations/units/GOLD

# --------------------------------------------------
# ./data/pilot/pilot20/pred_arg_annotations
# --------------------------------------------------

mkdir -p ./data/pilot/pilot20/pred_arg_annotations/units
mkdir -p ./data/pilot/pilot20/pred_arg_annotations/discourse
git mv ./data/pilot/pilot20/pred_arg_annotations/joseph/discourse ./data/pilot/pilot20/pred_arg_annotations/discourse/hjoseph
git mv ./data/pilot/pilot20/pred_arg_annotations/joseph/unit ./data/pilot/pilot20/pred_arg_annotations/units/hjoseph
git mv ./data/pilot/pilot20/pred_arg_annotations/petersen/discourse ./data/pilot/pilot20/pred_arg_annotations/discourse/lpetersen
git mv ./data/pilot/pilot20/pred_arg_annotations/petersen/unit ./data/pilot/pilot20/pred_arg_annotations/units/lpetersen
mkdir -p ./data/pilot/pilot21/pred_arg_annotations/units
git mv ./data/pilot/pilot21/Gold/Unit_Pred_Arg ./data/pilot/pilot21/pred_arg_annotations/units/GOLD

# --------------------------------------------------
# ./data/pilot/pilot21/pred_arg_annotations
# --------------------------------------------------

mkdir -p ./data/pilot/pilot21/pred_arg_annotations/units
mkdir -p ./data/pilot/pilot21/pred_arg_annotations/discourse
git mv ./data/pilot/pilot21/pred_arg_annotations/petersen/discourse ./data/pilot/pilot21/pred_arg_annotations/discourse/lpetersen
git mv ./data/pilot/pilot21/pred_arg_annotations/petersen/unit ./data/pilot/pilot21/pred_arg_annotations/units/lpetersen

# ======================================================================
# new GOLD directories
# ======================================================================


shopt -s nullglob

for sd in discourse units; do
    for d in data/pilot/pilot*; do
        anno_dir=$d/$sd/GOLD
        if [ ! -d $anno_dir ]; then
            echo $anno_dir
            mkdir $anno_dir
            pushd $anno_dir > /dev/null
            echo " aa"
            for aa in ../../unannotated/*.aa; do
                cp $aa .
            done
            echo " ac"
            for ac in ../../unannotated/*.ac; do
                ln -s $ac .
            done
            echo " aam"
            ln -s ../../*.aam .
            echo " git"
            git add *.aa *.ac *.aam
            popd > /dev/null
        fi
    done
done


# ======================================================================
# cleanups
# ======================================================================

# **************************************************
# Hey! You should mention these in the commit log
#   data/pilot/pilot01/glozz_annotations/ResultUnit
#
# Also when you commit, remember to switch back to
# SVN and run code/cleanup-2013-02/mk-tidyup-script
# **************************************************
