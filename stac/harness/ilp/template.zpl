
# Automatically generated
# param EDU_COUNT := ??? ;
# param TURN_COUNT := ??? ;

set EDUs := {1 to EDU_COUNT} ;
set Turns := {1 to TURN_COUNT} ;

param TLEN[Turns] := read "./turn.dat" as "n+" ;
param TOFF[Turns] := read "./turn.dat" as "n+" skip 1 ;
param TEDU[EDUs] := read "./turn.dat" as "n+" skip 2 ;
set TIND[<t> in Turns] := {1 to TLEN[t]} ;

param PATT[EDUs*EDUs] := read "./raw.attach.dat" as "n+" ;

var c[<t,i> in Turns*EDUs
    with i <= TLEN[t]] integer <= EDU_COUNT;
var x[<i,j> in EDUs*EDUs] binary ;

# Objective function
maximize score: sum <i,j> in EDUs*EDUs: PATT[i,j]*x[i,j] ;

# No auto-link
subto no_diagonal: forall <i> in EDUs:
    x[i, i] == 0 ;

# Intra-turn acyclicity constraint
subto cyc_bounds: forall <t> in Turns:
    forall <i> in TIND[t]:
        1 <= c[t, i] <= TLEN[t]	 ;

subto cyc_transition: forall <t> in Turns:
    forall <i, j> in TIND[t]*TIND[t] with i!=j:
        c[t, j] <= c[t, i] - 1 + EDU_COUNT*(1-x[TOFF[t]+i, TOFF[t]+j]) ;
