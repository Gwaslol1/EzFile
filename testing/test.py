import random
import time
from shutil import get_terminal_size
from typing import Callable, TextIO


def timeme(function):
    def wrapper(*args, **kw):
        start_time = int(round(time.time()))
        result = function(*args, **kw)
        end_time = int(round(time.time()))
        time_taken = end_time - start_time
        return (result, time_taken)
    return wrapper

# -> Splitting functions
# ------------------------------------------ #
def custom_pysplit(line: str, delim: str) -> list[str]:
    filtered = []
    temp_string = ""
    for char in line:
        if char == delim and temp_string:
            if temp_string == "pattern": filtered.append(temp_string)
            temp_string = ""
            continue
        elif char == delim:
            continue
        else:
            temp_string += char
    return filtered

# -> Turns out this is actually way way way faster, I guess cause the underlying C implementation of split() is really fast
def worse_custom_pysplit(line: str, delim: str) -> list[str]:
    split_array = line.split(delim)
    filtered = []
    for string in split_array:
        if string == "pattern": filtered.append(string)
    return filtered

def custom_csplit(line: str, delim: str) -> list[str]:
    return
# ------------------------------------------ #

@timeme
def test_read_time(func: Callable[[str, str], str], rfile: TextIO) -> int:
    count = 0
    with open(rfile, "r") as infile:
        for line in infile:
            filtered = func(line, " ")
            if len(filtered) == 1 and filtered[0] == "pattern": count += 1
    return count

def generate_wfile():
    nopat_line = "For some unfathomable reason, the response team didn't consider a lack of milk for my cereal as a proper emergency."
    pat_lines = []
    nopat_split = nopat_line.split()
    length = len(nopat_split)
    for i in range(10):
        pos = random.randrange(1,length)
        new_string = ""
        for i in range(length):
            addition = f"{nopat_split[i]} "
            new_string += addition if i != pos else "pattern "
        new_string += "\n"
        pat_lines.append(new_string)

    with open("test_file.txt", "w") as wfile:
        for i in range(4000000):
            wfile.write(random.choice(pat_lines))

def main():
    pysplit_time = 0
    worse_pysplit_time = 0
    csplit_time = 0
    result = 0
    rfile = "test_file.txt"
    expected = 4000000
    result, pysplit_time = test_read_time(custom_pysplit, rfile)
    if result != expected: print(f"\n!!!!!!!!!!!Test failure -- Pysplit!!!!!!!!!!!\n")
    result, worse_pysplit_time = test_read_time(worse_custom_pysplit, rfile)
    if result != expected: print(f"\n!!!!!!!!!!!Test failure -- Worse Pysplit!!!!!!!!!!!\n")
    # result, csplit_time = test_read_time(custom_csplit, rfile)
    # if result != expected: print(f"\n!!!!!!!!!!!Test failure -- Csplit!!!!!!!!!!!\n")

    terminal_width = get_terminal_size().columns
    print(f"\nBoth methods finished...")
    print('-' * terminal_width)
    print(f"Python implementation of custom split function took - [{pysplit_time}s]")
    print('-' * terminal_width)
    print(f"Inefficient Python implementation of custom split function took - [{worse_pysplit_time}s]")
    print('-' * terminal_width)
    print(f"Cython implementation of custom split function took - [{csplit_time}s]\n")


if __name__ == "__main__":
    main()