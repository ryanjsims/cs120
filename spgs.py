"""
Programmer: Ryan Sims
Email: ryanjsims@email.arizona.edu
Date: 6/7/2018
"""
import sys
VERSION = (1, 3, 1)

class Stack:
    def __init__(self):
        self.__items = []

    def size(self):
        return len(self.__items)

    def push(self, value):
        self.__items.append(value)

    def pop(self):
        return self.__items.pop()

    def peek(self, index = -1):
        return self.__items[index]

    def is_empty(self):
        return self.size() == 0

    def append_list(self, values):
        assert type(values) == list
        self.__items += values

def main():
    assg, loaded = get_assignment()
    if not loaded:
        rubric = get_rubric(assg)
        sl_name = get_sl_name()
        problems = parse_rubric(rubric)
        emails_to_names = get_netids_and_names()
        scores_csv = get_scores_csv()
        constraints = get_constraints() #Probably not actually
        base_scores = get_base_scores(scores_csv)
        final_scores = {}
        previous_comments = ["Don't forget comments!"]
    else:
        rubric = loaded["rubric"]
        sl_name = loaded["sl_name"]
        problems = loaded["problems"]
        emails_to_names = loaded["emails"]
        constraints = loaded["constraints"]
        base_scores = loaded["base_scores"]
        final_scores = loaded["final_scores"]
        previous_comments = loaded["previous_comments"]
    to_grade = Stack()
    graded = Stack()
    for student in reversed(sorted(list(base_scores.keys()))):
        if student not in final_scores:
            to_grade.push(student)
        else:
            graded.push(student)
    
    print_intro()
    while not to_grade.is_empty():
        curr_student = to_grade.pop()
        print_student(curr_student)

        problem_stack = Stack()
        finished_problems = Stack()

        if curr_student not in final_scores:
            final_scores[curr_student] = {}
            problem_stack.append_list(problems)
        else:
            for problem in problems:
                if problem not in final_scores[curr_student]:
                    problem_stack.push(problem)
                else:
                    finished_problems.push(problem)

        while not problem_stack.is_empty():
            curr_problem = problem_stack.pop()
            print_code(curr_problem, curr_student, base_scores)
            deduct_resp = check_deduct()
            deduction = 0
            if deduct_resp == "y":
                #TODO: Figure out name for score here
                deduction = get_deduction(0, base_scores[curr_student][)
            elif deduct_resp == "u":
                if finished_problems.is_empty() and graded.is_empty():
                    print("Nothing to undo!", file=sys.stderr)
                    problem_stack.push(curr_problem)
                    continue
                elif finished_problems.is_empty():
                    to_grade.push(curr_student)
                    to_grade.push(graded.pop())
                    break
                else:
                    problem_stack.push(curr_problem)
                    problem_stack.push(finished_problems.pop())
                    continue
            elif deduct_resp == "s":
                problem_stack.push(curr_problem)
                save_all(rubric, sl_name, problems, emails_to_names, constraints,\
                        base_scores, final_scores, previous_comments)
                continue
            comments = get_comments(previous_comments)
            
