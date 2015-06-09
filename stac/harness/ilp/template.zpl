
# Template with relation handling

# Automatically generated
# param EDU_COUNT := ??? ;
# param TURN_COUNT := ??? ;
# param LABEL_COUNT := ??? ;

set EDUs := {1 to EDU_COUNT} ;
set Turns := {1 to TURN_COUNT} ;
set Labels := {1 to LABEL_COUNT} ;

param TLEN[Turns] := read "./turn.dat" as "n+" ;
param TOFF[Turns] := read "./turn.dat" as "n+" skip 1 ;
param TEDU[EDUs] := read "./turn.dat" as "n+" skip 2 ;
set TIND[<t> in Turns] := {1 to TLEN[t]} ;

param PATT[EDUs*EDUs] := read "./raw.attach.dat" as "n+" ;
param PLAB[EDUs*EDUs*Labels] := read "./raw.label.dat" as "n+" ;

var c[<t,i> in Turns*EDUs
    with i <= TLEN[t]] integer <= EDU_COUNT;
var h[<i> in EDUs] binary ;
var a[<i,j> in EDUs*EDUs] binary ;
var x[<i,j,r> in EDUs*EDUs*Labels] binary ;

# Objective function
maximize score: sum <i,j,r> in EDUs*EDUs*Labels: PLAB[i, j, r]*x[i, j, r] ;

# Attachment definition
subto attachment:
    forall <i,j> in EDUs*EDUs:
        a[i, j] == sum <r> in Labels: x[i, j, r] ;

# No auto-link
subto no_diagonal:
    forall <i> in EDUs:
        a[i, i] == 0 ;

# No zero-prob links
subto no_zero_att:
    forall <i,j> in EDUs*EDUs:
        if PATT[i, j] == 0
            then a[i, j] == 0 end ;

subto no_zero_lab:
    forall <i,j,r> in EDUs*EDUs*Labels:
        if PLAB[i, j, r] == 0
            then x[i, j, r] == 0 end ;

# No backwards inter-turn
subto no_back:
    forall <i,j> in EDUs*EDUs with TEDU[i] != TEDU[j] and j<i:
        a[i, j] == 0 ;

# Intra-turn acyclicity constraint
subto cyc_bounds: forall <t> in Turns:
    forall <i> in TIND[t]:
        1 <= c[t, i] <= TLEN[t] ;

subto cyc_transition: forall <t> in Turns:
    forall <i, j> in TIND[t]*TIND[t] with i!=j:
        c[t, j] <= c[t, i] - 1 + EDU_COUNT*(1 - a[TOFF[t] + i, TOFF[t] + j]) ;

# Unique head and connexity (requires full acyclicity)
subto unique_head:
    sum <i> in EDUs: h[i] == 1 ;

subto find_heads:
    forall <j> in EDUs:
        1 <= sum <i> in EDUs:a[i, j] + EDU_COUNT*h[j] <= EDU_COUNT ;

# Transitive closure
subto transitivity:
    forall <m> in {1 to EDU_COUNT-1}:
        forall <n> in {2 to EDU_COUNT-m}:
            (sum <i> in {0 to n-1} : a[m + i, m + i + 1]) + a[m, m + n] <= n ;
