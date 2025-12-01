import os
from datetime import datetime

def get_day_file(directory, year_month_day):
    fname = f"visitors_{year_month_day}.txt"
    if fname in os.listdir(directory):
        print(f"Found file for {year_month_day}.")
        return fname
    else:
        print(f"No file found for {year_month_day}.")
        return None

def parse_file(filepath):
    with open(filepath, 'r') as f:
        lines = f.readlines()
    count_in = 0
    hand_count = 0
    for line in lines:
        if line.startswith("Visitor at"):
            count_in += 1
        elif line.startswith("IAO at"):
            hand_count += 1
    return count_in, hand_count

def main():
    directory = os.path.dirname(__file__)
    year_month_day = input("Enter date in YYYYMMDD format: ").strip()
    fname = get_day_file(directory, year_month_day)
    if not fname:
        return
    v, i = parse_file(os.path.join(directory, fname))
    print(f"Visitors: {v}")
    print(f"IAO: {i}")

main()
