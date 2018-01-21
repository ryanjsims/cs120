import re, os

"""
Simple script to create emails_and_names.txt from the section lists provided on Piazza
"""

def main():
    currdir = os.listdir(".")
    r = re.compile("Section.*csv")
    csv_name = list(filter(r.match, currdir))
    if len(csv_name) == 0:
        print("Could not find Section_1x.csv!")
        return
    elif len(csv_name) > 1:
        print("Found multiple Section_1x.csv files, using " + csv_name[0])
    csv_file = open(csv_name[0])
    csv_lines = csv_file.readlines()[1:]
    names_file = open("emails_and_names.txt", "w")
    for i in range(len(csv_lines)):
        csv_lines[i] = csv_lines[i].strip("#\n").split(",")
        names_file.write("{}\t{}, {}\n".format(csv_lines[i][0].lower(), csv_lines[i][1], csv_lines[i][2]))
main()
    
    
    
