
param distance := 5;


set E   := { 1 .. EDUs };

var x[E * E] binary;


maximize cost: sum<i,j> in E * E:  x[i,j];


subto missing: 
	 forall <i,j> in E * E:
	 	if (MSDAG[i,j] == 0) then x[i,j] == 0 end;
		
subto mst: 
	 forall <i,j> in E * E:
	 	if (MST[i,j] == 1) then x[i,j] == 1 end;

# Constraint on distance, but we shouldn't either remove MST links, otherwise there will be no solution		
subto distance: 
	forall <i,j> in E * E:
		if abs(i-j) >= distance and MST[i,j] == 0 then x[i,j] == 0 end;
		
subto transitivity:
	forall <a> in {1 .. EDUs-1}:
		forall <n> in {2 .. EDUs-1} with n <= EDUs-a:
			(sum <i> in {0 .. n-1} : x[a+i,a+i+1]) + x[a,a+n] <= n;

#subto compositionality3: 
#	forall <a,b,c> in E * E * E: 
#		x[a,b] + x[b,c] + x[a,c] <= 2;

subto compositionality4: 
	forall <a,b,c,d> in E * E * E * E: 
		x[a,b] + x[b,c] + x[c,d] + x[a,d] <= 3;