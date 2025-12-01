import os
import re
from datetime import datetime

def get_month_files(directory, year_month):
    files = []
    for f in os.listdir(directory):
        if f.startswith("visitors_"):
            try:
                date_str = f.replace("visitors_", "").replace(".txt", "")
                file_date = datetime.strptime(date_str, "%Y%m%d")
                if file_date.strftime("%Y%m") == year_month:
                    files.append(f)
            except ValueError:
                continue
    print(f"Found {len(files)} files for {year_month}.")
    return files

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
    year_month = input("Enter year and month in YYYYMM format: ").strip()
    files = get_month_files(directory, year_month)
    total_visitors = 0
    total_iao = 0
    for fname in files:
        v, i = parse_file(os.path.join(directory, fname))
        total_visitors += v
        total_iao += i
    print(f"Cumulative Visitors: {total_visitors}")
    print(f"Cumulative IAO: {total_iao}")


main()