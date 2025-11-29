import csv

input_file = "./output_15_200/emissions_15.txt"
output_file = "emissions_15.csv"

rows = []

with open(input_file, "r") as f:
    for line in f:
        # skip empty lines
        if not line.strip():
            continue

        # split on tabs OR spaces automatically
        parts = line.strip().split()
        rows.append(parts)

with open(output_file, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(rows)

print(f"CSV written to {output_file}")

