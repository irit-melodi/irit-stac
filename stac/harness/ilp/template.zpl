
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
var h[<i> in EDUs] binary ;
var x[<i,j> in EDUs*EDUs] binary ;

# Objective function
maximize score: sum <i,j> in EDUs*EDUs: PATT[i,j]*x[i,j] ;

# No auto-link
subto no_diagonal:
    forall <i> in EDUs:
        x[i, i] == 0 ;

# No zero-prob links
subto no_zero:
    forall <i,j> in EDUs*EDUs:
        if PATT[i,j] == 0
            then x[i,j] == 0 end ;

# No backwards inter-turn
subto no_back:
    forall <i,j> in EDUs*EDUs with TEDU[i] != TEDU[j] and j<i:
        x[i,j] == 0 ;

# Intra-turn acyclicity constraint
subto cyc_bounds: forall <t> in Turns:
    forall <i> in TIND[t]:
        1 <= c[t, i] <= TLEN[t] ;

subto cyc_transition: forall <t> in Turns:
    forall <i, j> in TIND[t]*TIND[t] with i!=j:
        c[t, j] <= c[t, i] - 1 + EDU_COUNT*(1-x[TOFF[t]+i, TOFF[t]+j]) ;

# Unique head and connexity (requires full acyclicity)
subto unique_head:
    sum <i> in EDUs: h[i] == 1 ;

subto find_heads:
    forall <j> in EDUs:
        1 <= sum <i> in EDUs:x[i,j] + EDU_COUNT*h[j] <= EDU_COUNT ;

# Transitive closure
subto transitivity:
    forall <a> in {1 to EDU_COUNT-1}:
        forall <n> in {2 to EDU_COUNT-a}:
            (sum <i> in {0 to n-1} : x[a+i,a+i+1]) + x[a,a+n] <= n ;
