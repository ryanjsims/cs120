import re, os

def main():
    currdir = os.listdir(".")
    r = re.compile("Section.*csv")
    csv_name = filter(r.match, currdir)
    if len(csv_name) == 0:
        print("Could not find Section_1x.csv!")
        return
    elif len(csv_name) > 1:
        print("Found multiple Section_1x.csv files, using " + csv_name[0])
    csv_file = open(csv_name[0])
    
