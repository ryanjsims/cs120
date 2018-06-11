"""
Programmer: Ryan Sims
Email: ryanjsims@email.arizona.edu
Date: 6/7/2018
"""
import sys
from gradebuffer import *
VERSION = (1, 3, 1)

def main():
    assg, loaded = get_assignment()
    sl_name = get_sl_name()
    emails_to_names = get_netids_and_names()
    if not loaded:
        rubric = get_rubric(assg)
        problems = parse_rubric(rubric)
        scores_csv = get_scores_csv()
        constraints = get_constraints() #Probably not actually
        base_scores = get_base_scores(scores_csv)
        final_scores = {}
        previous_comments = ["Don't forget comments!"]
        to_grade = GradeBuffer(sorted(list(base_scores.keys())))
    else:
        rubric = loaded["rubric"]
        problems = loaded["problems"]
        constraints = loaded["constraints"]
        base_scores = loaded["base_scores"]
        final_scores = loaded["final_scores"]
        previous_comments = loaded["previous_comments"]
        to_grade = GradeBuffer([])
        to_grade.decode(loaded["to_grade"])
    
    print_intro()
    while not to_grade.is_empty():
        curr_student = to_grade.next()
        print_student(curr_student)

        problem_buffer = GradeBuffer(problems)

        if curr_student not in final_scores:
            final_scores[curr_student] = {}

        for problem in problems:
            if problem in final_scores[curr_student]:
                #Can print this to notify that it is being skipped
                problem_buffer.next()

        while not problem_buffer.is_empty():
            curr_problem = problem_buffer.next()
            print_code(curr_problem, curr_student, base_scores)
            deduct_resp = check_deduct()
            score = base_scores[curr_student][curr_problem]
            if deduct_resp == "y":
                score -= get_deduction(base_scores[curr_student][curr_problem])
            elif deduct_resp == "u":
                if len(problem_buffer.get_graded()) == 1 and len(to_grade.get_graded()) == 1:
                    print("Nothing to undo!", file=sys.stderr)
                    problem_buffer.rewind(1)
                    continue
                elif len(problem_buffer.get_graded()) == 1:
                    to_grade.rewind(2)
                    break
                else:
                    problem_buffer.rewind(2)
                    continue
            elif deduct_resp == "s":
                filename = get_save_name()
                save_all(filename, rubric, problems, to_grade, emails_to_names, constraints, 
                        base_scores, final_scores, previous_comments)
                continue
            
            if curr_problem not in final_scores[curr_student]:
                final_scores[curr_student][curr_problem] = {}
            final_scores[curr_student][curr_problem]["score"] = score
            final_scores[curr_student][curr_problem]["comments"] = get_comments(previous_comments)

            filename = "_assg{:02d}autosave".format(assg)
            save_all(filename, rubric, problems, to_grade, emails_to_names, constraints, 
                    base_scores, final_scores, previous_comments)
    
    write_emails(rubric, emails_to_names, final_scores)
    write_csv(emails_to_names, final_scores)

def get_assignment():
    pass

def get_sl_name():
    pass

def get_netids_and_names():
    pass

def get_rubric(assg):
    pass

def parse_rubric(rubric):
    pass

def get_scores_csv():
    pass

def get_base_scores(scores_csv):
    pass

def print_intro():
    pass

def print_student(curr_student):
    pass

def print_code(curr_problem, curr_student, base_scores):
    pass

def check_deduct():
    pass

def get_deduction(max_deduct):
    pass

def get_save_name():
    pass

def save_all(filename, rubric, problems, to_grade, emails_to_names, constraints, 
                        base_scores, final_scores, previous_comments):
    pass

def get_comments(previous_comments):
    pass

def write_emails(rubric, emails_to_names, final_scores):
    pass

def write_csv(emails_to_names, final_scores):
    pass
