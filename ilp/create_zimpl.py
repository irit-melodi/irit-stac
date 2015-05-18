import glob
from os.path import basename

input_directory = "/Users/stergos/Dropbox/theses/Perret/ILP/probs/maxent/msdag/"
output_dir = "/Users/stergos/Dropbox/theses/Perret/ILP/zimpl/"
template_file = "/Users/stergos/Dropbox/theses/Perret/ILP/template.zpl"

for file_name in glob.glob(input_directory + "*.attach.dat"): 
    with open(file_name, 'r') as f: 
        number_of_EDUs = f.readline().count(':') + 1
        with open(output_dir + basename(file_name).split('.')[0] +".zpl", "w") as zpl_file:
            zpl_file.write("param EDUs := " + str(number_of_EDUs) + ";\n")
            zpl_file.write("param MSDAG[{1..EDUs}*{1..EDUs}] := read \"" + file_name + "\" as \"n+\" skip 1;\n")
            zpl_file.write("param MST[{1..EDUs}*{1..EDUs}] := read \"" + file_name.replace("msdag","mst") + "\" as \"n+\" skip 1;\n\n")
            with open(template_file) as template:
                for line in template: 
                    zpl_file.write(line)
            zpl_file.write("\n\n")
