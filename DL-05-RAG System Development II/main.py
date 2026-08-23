# -*- coding: utf-8 -*-
# Main script for demonstrating 10 LLM & RAG problem scenarios
#
# Run:
#     python main.py
#
# Or select a problem directly:
#     python main.py 4

import sys

from problem01_hallucination import run as problem01
from problem02_transformer import run as problem02
from problem03_data_quality import run as problem03
from problem04_chunking import run as problem04
from problem05_metadata import run as problem05
from problem06_reranking import run as problem06
from problem07_generation import run as problem07
from problem08_config import run as problem08
from problem09_evaluation import run as problem09
from problem10_debug_scripts import run as problem10

PROBLEMS = {
    1: ("Hallucination / Context", problem01),
    2: ("Transformer / Position / Attention", problem02),
    3: ("Data Quality", problem03),
    4: ("Chunk Size / Overlap", problem04),
    5: ("Metadata Filtering", problem05),
    6: ("Top-k / Re-ranking", problem06),
    7: ("Retrieval Correct, Generation Wrong", problem07),
    8: ("RAG Configuration", problem08),
    9: ("Chunk & Retrieval Evaluation", problem09),
    10: ("Debug RAG Scripts", problem10),
}

def show_menu():
    print("*" * 65)
    print("       LLM & RAG — 10 Problem-Based Simulations")
    print("*" * 65)
    print(" 0. Run All")
    for no, (name, _) in PROBLEMS.items():
        print(f"{no:2}. {name}")
    print("*" * 65)

def execute(number):
    if number == 0:
        for no, (name, func) in PROBLEMS.items():
            print("\n" + "*" * 65)
            print(f"PROBLEM {no}: {name}")
            print("*" * 65)
            func()
        return

    if number not in PROBLEMS:
        print("Please choose a number 0-10")
        return

    name, func = PROBLEMS[number]
    print("\n" + "*" * 65)
    print(f"PROBLEM {number}: {name}")
    print("*" * 65)
    func()

def main_loop():
    while True:
        show_menu()
        choice = input("Select a problem to simulate [0-10] or Q to exit: ").strip()

        if choice.upper() == "Q":
            print("Exiting the program")
            break

        try:
            number = int(choice)
        except ValueError:
            print("Please enter a number 0-10 or Q\n")
            continue

        if number < 0 or (number not in PROBLEMS and number != 0):
            print("Please choose a number 0-10\n")
            continue

        execute(number)
        print()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        arg = sys.argv[1].strip()
        if arg.upper() == "Q":
            sys.exit(0)
        try:
            execute(int(arg))
        except ValueError:
            print("Please enter a number 0-10 or Q")
    else:
        main_loop()
