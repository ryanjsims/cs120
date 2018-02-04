"""
Programmer: Ryan Sims
Email: ryanjsims@email.arizona.edu
Date: 8/28/2017
"""
VERSION = "1.3.1"
"""
Description: A short problem grading script for CSC120 SLs.
             For use in unix-like OSes, though it can be run in Windows as well.
Requirements:
    1. Text file listing all of your students' NetIDs and full names,
       one student per line, of the format:
        <NetID>\tLastname, Firstname
       This text file needs to be in the same directory as this script,
       and it must be named "emails_and_names.txt".
    2. Assignment folders in the same directory, named "Assignment <#>"
       where <#> is replaced with the assignment number. Each Assignment <#>
       folder should have a "Short Problems" subdirectory, which contains
       your students' code folders out of the tar file, the CCscores.csv file,
       the rubric provided by Ryan in a "rubric.txt" file, and an optional
       "constraints.txt" file to exclude lines you do not want printed.
    So your setup should look like:
    
    <basedir>/
        short_problem_grading_script.py
        emails_and_names.txt
        Assignment 1/
            Short Problems/
                ryanjsims/
                    code.py
                CCscores#######.csv
                rubric.txt
                constraints.txt (optional)
        Assignment 2/
            Short Problems/
                ryanjsims/
                    amazing_code.py
                CCscores#####.csv
                rubric.txt
                
    and so on...
"""




import os, re, errno, platform, json, sys, copy
FOLDSEP = "/"
SAVECLEAR = "tput smcup"
CLEAR = "clear"
RESTORE = "tput rmcup"
if os.name == "nt":
    FOLDSEP = "\\"
    SAVECLEAR = "cls"
    CLEAR = "cls"
    RESTORE = ""

def main():
    grader = ShortGrader()
    grader.grade()

class ShortGrader:
    def __init__(self):
        # sl_name is the name of the SL grading the problems
        self.sl_name = self.get_sl_name()
        # rubric is a list of all the lines in the rubric provided by Abigail
        self.rubric = [""]
        # problems is a list of tuples of strings.
        # Each tuple consists of 2 strings, the first of which is the point
        # value of the problem. The second is the name of the problem.
        self.problems = [()]
        # scores_csv is a list of the lines in the cloud coder csv that have
        # your students scores in them.
        self.scores_csv = [","]
        # assignment is the assignment number, entered manually
        self.assignment = -1
        # emails is a list of students netIDs, provided by the section leader
        # in emails.txt in the same directory as this script
        self.emails = [""]
        # netids_to_names is a dictionary mapping netids to full names of the form
        # "lastname, firstname"
        self.netids_to_names = {}
        # student_scores is generated from the csv file, and consists of strings
        # of the student's netIDs mapping to a dictionary containing their name
        # and their scores on each problem
        self.student_scores = {}
        # finished_students is used for saving/loading grading progress to keep track
        # of who has been graded so far in between grading sessions.
        # List of strings of netids
        self.finished_students = []
        # prev_problem is to allow the user to undo any mistakes they made in the previous
        # problem
        self.prev_problem = []
        # constraints is a list of lines that should not be output when reading the code.
        self.constraints = []
        
    """
    grade()
    The main function of the program, controls all function calls
    and return values.
    """
    def grade(self):
        self.get_assignment()
        if(len(self.student_scores[sorted(self.student_scores.keys())[0]]["problems_finished"]) == 0):
            """
            We have not loaded anything, so we need to initialize
            everything.
            """
            if(not self.parse_rubric()):
                return
            if(not self.get_emails_and_names()):
                return
            csv_name = self.get_csv_name()
            if(not self.parse_csv(csv_name)):
                return
            self.get_constraints()
            self.get_base_scores()
        print("\n--------------------------------------------------")
        print("\tType save at any time to save")
        print("\tthe current state of your grading.")
        print("\n\tType undo at the start of a new")
        print("\tstudent/problem to regrade the previous")
        print("\tstudent or previous problem")
        print("--------------------------------------------------\n")
        self.check_code_quality()
        self.write_emails()
        self.write_csv()

    """
    get_assignment()
    Controls which assignment is currently being graded.
    Either sets the assignment number directly for a clean run,
    or loads saved data from disk from an earlier grading session.
    """
    def get_assignment(self):
        while self.assignment == -1:
            try:
                self.assignment = input("Enter the assignment number or 'load' to load a save file. ")
                if self.assignment.lower().startswith("l"):
                    self.load_data()
                else:
                    self.assignment = int(self.assignment)
            except ValueError:
                print("Please enter a number (1, 2, etc...)")
                self.assignment = -1
                continue
            except AssertionError:
                """
                Incompatible save!
                """
                sys.exit(1)
        
    """
    parse_rubric()
    Opens and loads the rubric and problems into self.rubric and self.problems.
    Problems are found via regex looking for '/<number> <whitespace> name_of_function'
    and are stored in self.problems as a tuple consisting of two strings ('point_val', 'name').
    The rubric is stored as a list of lines in the provided rubric file.
    Returns True on success, False on exception
    """
    def parse_rubric(self):
        rubric_path = os.getcwd() + FOLDSEP + "Assignment " + str(self.assignment)\
                     + FOLDSEP + "Short Problems" + FOLDSEP + "rubric.txt"
        print("Looking for rubric in " + rubric_path)
        try:
            self.rubric = open(rubric_path).readlines()
        except IOError:
            print("Unable to find rubric.txt")
            return False
        else:
            # This regex finds anything of the format "/<#> <valid_python_func_name>"
            # The first group is the points value, and the second group is the
            # name of the function
            self.problems = re.findall("\/(\d+)\s+([a-zA-Z0-9_\- #]+)", "".join(self.rubric))
            for i in range(len(self.problems)):
                if(" " in self.problems[i][1]):
                    self.problems[i] = (self.problems[i][0], self.problems[i][1].replace(" ", ""))
                if("#" in self.problems[i][1]):
                    self.problems[i] = (self.problems[i][0], self.problems[i][1].replace("#", ""))
            print("Rubric found and parsed successfully")
            return True
    """
    get_emails_and_names()
    Opens the email file containing the netids for your section and stores it in
    self.emails, a list of netid strings.
    Returns True on success, False on exception
    """    
    def get_emails_and_names(self):
        print("Looking for email and name list in " + os.getcwd() + FOLDSEP + "emails_and_names.txt")
        try:
            emails_and_names = open("emails_and_names.txt").readlines()
            emails_and_names = [line.lower().split("\t") for line in emails_and_names]
            self.emails = [line[0] for line in emails_and_names]
            for line in emails_and_names:
                self.netids_to_names[line[0]] = " ".join(reversed(line[1].split(", "))).replace("\n", "")
            
        except:
            print("Email list not found.")
            return False
        else:
            print("Email list found.")
            for i in range(len(self.emails)):
                self.emails[i] = self.emails[i].strip()
            return True

    """
    get_csv_name()
    Looks for .csv file containing scores in ./Assignment #/Short Problems/
    CSV name is matched via regex of pattern <any number of C's>scores<any number of numbers>.csv
    If multiple matches are found, the user must select the correct CSV to be used.
    Returns "" on no match, and "<csv_name>" on match
    """    
    def get_csv_name(self):
        csv_dir = os.getcwd() + FOLDSEP + "Assignment " +\
              str(self.assignment) + FOLDSEP + "Short Problems" + FOLDSEP
        print("Looking for csv file in " + csv_dir)
        matches = re.findall("\bC*scores[a-zA-Z0-9]*\.csv", "\n".join(os.listdir(csv_dir)))
        csv_name = ""
        if(len(matches) == 0):
            print("CSV scores file of form C*scores[0-9]*\.csv not found.")
            print("Make sure the file is named scores.csv and is in the correct location.")
        elif(len(matches) > 1):
            print("Several matches found. Please select correct CSV from below list:")
            for i in range(len(matches)):
                print("\t" + str(i) + ". " + matches[i])
            selection = int(input("Enter number of correct CSV: [0 - " +
                                  str(len(matches) - 1) + "]\n"))
            csv_name = matches[selection]
        else:
            csv_name = matches[0]
        return csv_name

    """
    parse_csv(csv_name)
    Error checks csv_name and parses CSV, cutting it down to only the students specified in self.emails
    Stores csv as list of lists in self.scores_csv
    Returns False if csv not found, True otherwise
    """
    def parse_csv(self, csv_name):
        short_prob_path = os.getcwd() + FOLDSEP + "Assignment " +\
              str(self.assignment) + FOLDSEP + "Short Problems" + FOLDSEP
        if(csv_name == ""):
            return False
        print("Parsing " + csv_name)
        self.scores_csv = open(short_prob_path + csv_name).readlines()
        i = 0
        #Cut csv down to contain only the students in self.emails
        while i < len(self.scores_csv):
            self.scores_csv[i] = self.scores_csv[i].split(",")
            if i == 0:
                i += 1
                continue
            if(not self.scores_csv[i][2] in self.emails or not
               os.path.exists(short_prob_path + self.scores_csv[i][2])):
                self.scores_csv.remove(self.scores_csv[i])
                continue
            i += 1
        return True                              

    """
    get_constraints()
    Checks to see if there is a constraints file present. If there is, it loads
    the constraints. Else, it does nothing, and self.constraints remains an
    empty list.
    """
    def get_constraints(self):
        short_prob_path = os.getcwd() + FOLDSEP + "Assignment " +\
            str(self.assignment) + FOLDSEP + "Short Problems" + FOLDSEP
        if(os.path.exists(short_prob_path + "constraints.txt")):
            self.constraints = open(short_prob_path + "constraints.txt").readlines()
    
    """
    get_base_scores()
    Takes the scores from self.scores_csv and stores them in self.student_scores
    under student_scores["<netid>"]["<problem_name>"].
    Also stores students' names under netid->"name", netid->"(first|last)_name"
    No return value
    """    
    def get_base_scores(self):
        print("Getting base scores...")
        problem_indices = {}
        for student in self.scores_csv:
            student[len(student) - 1] = student[len(student) - 1].strip()
            if student[2] == "netid":
                for problem in self.problems:
                    problem_indices[problem[1]] = student.index(problem[1] + " score")
                continue
            self.student_scores[student[2]] = {}
            self.student_scores[student[2]]["name"] = student[1] + " " + student[0]
            self.student_scores[student[2]]["last_name"] = student[0]
            self.student_scores[student[2]]["first_name"] = student[1]
            for problem in self.problems:
                if(student[problem_indices[problem[1]]].strip() == ''):
                    student[problem_indices[problem[1]]] = "0"
                self.student_scores[student[2]][problem[1]] =\
                                float(problem[0]) * float(student[problem_indices[problem[1]]].strip())
                self.student_scores[student[2]][problem[1]] =\
                                self._round(self.student_scores[student[2]][problem[1]])

    def _round(self, num):
        mid = float(int(num)) + 0.5
        if num < mid:
            return int(num)
        return int(num) + 1
                
            
    """
    check_code_quality()
    Interactive method that prints students' code to screen for review.
    Calls get_deductions() and get_comments() for input from section leader.
    If loaded from save, this is the method that is called, and it will skip any
    students or problems that are already graded.
    No return value
    """
    def check_code_quality(self):
        
        directory = os.getcwd() + FOLDSEP + "Assignment " +\
              str(self.assignment) + FOLDSEP + "Short Problems" + FOLDSEP
        for netid in sorted(list(self.student_scores.keys())):
            if netid in self.finished_students:
                print("Skipping " + netid + ", already graded.")
                continue
            print("\nStudent: " + netid)

            #Check if loaded from save
            if not "comments" in list(self.student_scores[netid].keys()):
                self.student_scores[netid]["comments"] = {}
            if not "total" in list(self.student_scores[netid].keys()):
                self.student_scores[netid]["total"] = 0
            if "problems_finished" not in list(self.student_scores[netid].keys()):
                self.student_scores[netid]["problems_finished"] = []
            i = 0
            while i < len(self.problems):
                problem = self.problems[i]
                if problem[1] in self.student_scores[netid]["problems_finished"]:
                    print("Skipping " + problem[1] + ", already graded.")
                    i += 1
                    continue
                if(not self.grade_problem(problem, netid, directory)):
                    self.grade_problem(self.prev_problem[1], self.prev_problem[0], directory)
                    continue
                i += 1
                
            print("\n-------------------------------------------\n")
            self.finished_students.append(netid)
            self.save_data("_assg" + str(self.assignment) + "_autosave")

    """
    grade_problem(problem, netid, directory)
    Grades a single problem given by the problem list for name netid

    problem: list of strings consisting of ['<point_val>', '<problem_name>']
    netid: string containing current netid
    directory: the directory containing the students' code.

    returns True on successful grade,
            False if user indicates they need to undo a problem.
    """            
    def grade_problem(self, problem, netid, directory):
        self.student_scores[netid][problem[1] + "_backup"] =\
                            copy.deepcopy(self.student_scores[netid][problem[1]])
        solution_code = open(directory + netid + FOLDSEP + problem[1] + ".py")
        print()
        self.print_code(solution_code)
        print("Base score: " + str(self.student_scores[netid][problem[1]])
                  + "/" + problem[0])
        
        deduct = self.get_deductions()
        # get_deductions() returns an int when there is a deduction to be made,
        # string if the user wants to undo. It's hacky, I know.
        if type(deduct) is int:
            self.student_scores[netid][problem[1]] += deduct
        else:
            # Just way too messy. This resets the previous problem when
            # the user indicates they want to undo, and returns False.
            self.student_scores[self.prev_problem[0]]["total"]\
                = (self.student_scores[self.prev_problem[0]]["total"]
                           - self.student_scores[self.prev_problem[0]][self.prev_problem[1][1]])
            self.student_scores[self.prev_problem[0]][self.prev_problem[1][1]]\
                     = self.student_scores[self.prev_problem[0]][self.prev_problem[1][1] +"_backup"]
            return False
        # No negative scores allowed
        if(self.student_scores[netid][problem[1]] < 0):
            self.student_scores[netid][problem[1]] = 0
        self.student_scores[netid]["comments"][problem[1]] = self.get_comments(directory)
        self.student_scores[netid]["total"] += self.student_scores[netid][problem[1]]
        self.student_scores[netid]["problems_finished"].append(problem[1])
        self.prev_problem = [netid, problem]
        return True

    def print_code(self, code_file):
        solution_code = code_file.readlines()
        nl_flag = 0
        for line in solution_code:
            if '"""DO NOT MODIFY ANYTHING BELOW THIS LINE"""' in line:
                break
            if line in self.constraints:
                continue
            if len(line.strip()) == 0:
                print(["\n", ""][nl_flag], end='')
                nl_flag = 1
                continue
            nl_flag = 0
            print(line, end='')
        if nl_flag == 0:
            print()
    """
    get_deductions()
    Prompts the user to input any deductions necessary
    or if the program should save/undo its state.
    <terrible_hack>
    Returns deductions (int <= 0), "undo", or exits depending on user decision.
    </terrible_hack>
    """
    def get_deductions(self):
        while True:
            response = input("Any deductions? Save? Undo? (y/N/s/u) ")
            if not response or response.lower().startswith("n"):
                return 0
            elif response.lower().startswith("s"):
                self.save_data()
                response = input("Exit? (y/N)")
                if response.lower().startswith("y"):
                    sys.exit()
            elif response.lower().startswith("u"):
                return "undo" #ew
            else:
                deduct = 1
                while deduct > 0:
                    try:
                        deduct = -1 * int(input("How many points need to be deducted? (Enter an int >= 0) "))
                    except ValueError:
                        print("Enter an integer value please.")
                        deduct = 1
                        continue
                return deduct

    """
    get_comments()
    Prompts the user to input any comments they may have.
    User may choose from previous comments on each assignment.
    Returns a string of comments.
    """
    def get_comments(self, directory):
        regex = "<comment \d+>\s([\w\W]+?)</comment \d+>"
        ret = ""
        fav_list = ["Don't forget comments!"]
        if(not os.path.isfile(directory + "prev_comments.txt")):
            favorites = open(directory + "prev_comments.txt", "w")
        else:
            favorites = open(directory + "prev_comments.txt", "r+")
        if favorites.readable():
            fav_text = favorites.read()
            for comment in re.findall(regex, fav_text):
                fav_list.append(comment.strip())
        
        response = input("Any comments? You can choose from previous comments with 'f' (y/N/f) ")
        if not response or response.lower().startswith("n"):
            pass
        elif response.lower().startswith("f"):
            os.system(SAVECLEAR)
            print("{:2d}:\n\tNew...".format(0))
            for i in range(len(fav_list)):
                print("{:2d}:".format(i + 1))
                for line in fav_list[i].split("\n"):
                    if line != '':
                        print("\t" + line)
            choice = ""
            while type(choice) != int:
                try:
                    choice = int(input("Choose a comment. (0 - {:d}): ".format(len(fav_list))))
                except ValueError:
                    pass
            choice -= 1
            if choice >= 0:
                ret = fav_list[choice]
            else:
                print("Enter as many lines as you would like. End with a blank line.")
                ret = self.get_lines()
                self.write_comment_to_file(ret, favorites, len(fav_list))
            os.system(RESTORE)
            print(ret)
        else:
            print("Enter as many lines as you would like. End with a blank line.")
            ret = self.get_lines()
            self.write_comment_to_file(ret, favorites, len(fav_list))
        return ret

    def get_lines(self):
        ret = ""
        while True:
            line = input()
            if line:
                ret += line + "\n"
            else:
                return ret
    
    def write_comment_to_file(self, comment, file, num):
        if comment != "":
            file.write("<comment {:d}>\n".format(num)
                        + comment + "</comment {:d}>\n".format(num))

    """
    write_emails()
    Uses the rubric to create an email for each student.
    First saves state to disk. Second fills in any students who did not submit
    Then fills in all relevant data to the rubric and saves each email to
    ./Assignment #/Short Problems/_emails to be emailed later by the SL
    No return value
    """
    def write_emails(self):
        email_path = os.getcwd() + FOLDSEP + "Assignment " + str(self.assignment)\
                     + FOLDSEP + "Short Problems" + FOLDSEP + "_emails"
        rel_path = "." + FOLDSEP + "Assignment " + str(self.assignment)\
                     + FOLDSEP + "Short Problems" + FOLDSEP + "_emails"
        print("Grading completed. Writing email files to " + rel_path)
        print("Saved state to ./grader_saves/assignment" + str(self.assignment) + "preemail.gsv")
        self.save_data("assignment" + str(self.assignment) + "preemail")
        self.make_sure_path_exists(email_path)
        for netid in self.emails:
            if not netid in self.student_scores.keys():
                self.student_scores[netid] = {}
                self.student_scores[netid]["name"] = self.netids_to_names[netid]
                self.student_scores[netid]["last_name"] = self.netids_to_names[netid].split()[1]
                self.student_scores[netid]["first_name"] = self.netids_to_names[netid].split()[0]
                self.student_scores[netid]["comments"] = {}
                for problem in self.problems:
                    self.student_scores[netid]["comments"][problem[1]] = ""
                    self.student_scores[netid][problem[1]] = 0.0
                self.student_scores[netid]["total"] = 0
        for netid, data in self.student_scores.items():
            email_file = open(email_path + FOLDSEP + netid + ".txt", "w")
            for line in self.rubric:
                if("student:" in line.lower()):
                    email_file.write(line.strip() + " " + data["name"] + "\n")
                elif("section" in line.lower()):
                    email_file.write(line.strip() + " " + self.sl_name + "\n")
                elif("total:" in line.lower()):
                    line = line.split()
                    email_file.write(line[0] + "\t" + str(data["total"]) + line[1].strip() + "\n")
                elif("comments:" in line.lower()):
                    email_file.write(line.strip() + "\n\t")
                    for problem in self.problems:
                        if(data["comments"][problem[1]]):
                            email_file.write(problem[1] + ": " + str(data["comments"][problem[1]]) +"\n\n\t")
                else:
                    match = re.findall("\/\d+\s+([a-zA-Z0-9_\- #]+)", line)
                    if(len(match) != 0):
                        match[0] = match[0].replace(" ", "").replace("#", "")
                        for problem in self.problems:
                            if(problem[1] in match):
                                line = line.strip().split()
                                email_file.write(str(data[problem[1]]) + line[0] + "\t\t" + line[1] + "\n")
                    else:
                        email_file.write(line.strip() + "\n")
            email_file.close()
                    
                

    """
    make_sure_path_exists(path)
    Ensures a path exists.
    If error occurs that is not related to path already existing, raises that error.
    No return value
    """
    def make_sure_path_exists(self, path): 
        try:
            os.makedirs(path)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise

    """
    get_sl_name()
    Finds the current SL's name.
    The first time this program is run it will prompt the user to enter their name
    and will store the name to disk in sl_name.txt.
    If sl_name.txt exists then the name will be read from there instead of prompting.
    """
    def get_sl_name(self):
        if("ryan" in platform.node().lower()):
            return "Ryan Sims"
        elif(os.path.isfile("sl_name.txt")):
            return open("sl_name.txt").read().strip()
        else:
            sl_name_file = open("sl_name.txt", "w")
            name = input("Enter your full name, as you want your students to see it. ")
            sl_name_file.write(name)
            sl_name_file.close()
            return name

    """
    save_data(save_name="")
    If save_name is specified, saves data serialized to JSON to disk without prompting.
    Otherwise prompts for file name, then saves to disk.
    No return value
    """
    def save_data(self, save_name=""):
        data = {}
        data["version"]             = VERSION
        data["sl_name"]             = self.sl_name
        data["rubric"]              = self.rubric
        data["problems"]            = self.problems
        data["scores_csv"]          = self.scores_csv
        data["assignment"]          = self.assignment
        data["emails"]              = self.emails
        data["student_scores"]      = self.student_scores
        data["finished_students"]   = self.finished_students
        data["netids_to_names"]     = self.netids_to_names
        data["constraints"]         = self.constraints
        self.make_sure_path_exists("grader_saves")
        if not save_name:
            save_name = input("Enter a name for the save file. ")
        save_file = open(os.getcwd() + FOLDSEP + "grader_saves" + FOLDSEP + save_name + ".gsv", "w")
        save_file.write(json.dumps(data))
        save_file.close()

    """
    load_data()
    Prompts user to select a save file and loads JSON into memory.
    No return value.
    Throws AssertionError if save is incompatible with current version.
    """
    def load_data(self):
        print("Save files:")
        for line in os.listdir("grader_saves"):
            print("\t" + line)
        load_name = input("What save would you like to load? ")
        load_file = open("grader_saves" + FOLDSEP + load_name, "r")
        loaded_string = load_file.read()
        load_file.close()
        data = json.loads(loaded_string)
        assert "version" in data.keys(),\
                "Incompatible save from earlier version (unknown)" 
        currVersion = VERSION.split(".")
        oldVersion = str(data["version"]).split(".")
        assert currVersion[0] == oldVersion[0] and currVersion[1] == oldVersion[1],\
                "Incompatible save from earlier version ({})"\
                .format(data["version"])
        self.sl_name = data["sl_name"]
        self.rubric = data["rubric"]
        self.problems = data["problems"]
        self.scores_csv = data["scores_csv"]
        self.assignment = data["assignment"]
        self.emails = data["emails"]
        self.student_scores = data["student_scores"]
        self.finished_students = data["finished_students"]
        self.netids_to_names = data["netids_to_names"]
        self.constraints = data["constraints"]

    """
    write_csv()
    Writes user scores to csv file for easy access.
    Writes to ./Assignment #/Short Problems/adjusted_scores.csv
    """
    def write_csv(self):
        csv_path = os.getcwd() + FOLDSEP + "Assignment " + str(self.assignment)\
                   + FOLDSEP + "Short Problems" + FOLDSEP + "adjusted_scores.csv"
        rel_path = "." + FOLDSEP + "Assignment " + str(self.assignment)\
                   + FOLDSEP + "Short Problems" + FOLDSEP + "adjusted_scores.csv"
        print("Writing CSV to " + rel_path)
        csv_list = [["Last Name", "First Name", "NetID", "Total"]]
        csv_list_sort = []
        for netid in self.student_scores.keys():
            student_data = []
            student_data.append(self.student_scores[netid]["last_name"])
            student_data.append(self.student_scores[netid]["first_name"])
            student_data.append(netid)
            student_data.append(str(self.student_scores[netid]["total"]))
            csv_list_sort.append(student_data)
        csv_list_sort.sort()
        for line in csv_list_sort:
            csv_list.append(line)
        csv_file = open(csv_path, "w")
        for line in csv_list:
            csv_file.write(",".join(line) + "\n")
        csv_file.close()
            

        
main()            
            
        
        
        

    
