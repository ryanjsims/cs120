"""
Programmer: Ryan Sims
Email: ryanjsims@email.arizona.edu
Date: 6/7/2018
"""
from copy import *
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

    def is_empty(self):
        return self.size() == 0

def main():
    assg, loaded = get_assignment()
    if not loaded:
        rubric = get_rubric(assg)
        problems = parse_rubric(rubric)
        emails_to_names = get_netids_and_names()
        scores_csv = get_scores_csv()
        constraints = get_constraints() #Probably not actually
        base_scores = get_base_scores(scores_csv)
        final_scores = {}
    else:
        rubric = loaded["rubric"]
        problems = loaded["problems"]
        emails_to_names = loaded["emails"]
        constraints = loaded["constraints"]
        base_scores = loaded["base_scores"]
        final_scores = loaded["final_scores"]
    
    
