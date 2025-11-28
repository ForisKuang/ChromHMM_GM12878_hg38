import pandas as pd
import matplotlib.pyplot as plt

# -----------------------
# INPUT FILES
# -----------------------
STATE_COMPARISON_FILE = "state_comparison.txt"
STATE_SWITCH_FILE = "state_switch_matrix.txt"

# -----------------------
# OUTPUT FILES
# -----------------------
STATE_FRACTIONS_PNG = "state_fractions_GM12878_vs_K562.png"
STATE_SWITCH_PNG = "state_switch_heatmap_GM12878_vs_K562.png"

# -----------------------
# LOAD STATE COMPARISON
# -----------------------
comp_rows = []

with open(STATE_COMPARISON_FILE) as f:
    for line in f:
        line = line.strip()
        if not line:
            continue

        # Expected format per line:
        # GMcount  E1   Kcount   E1
        parts = line.split()
        if len(parts) < 4:
            continue

        gm_count = int(parts[0])
        gm_state = parts[1]
        k_count = int(parts[2])
        k_state = parts[3]

        comp_rows.append((gm_state, gm_count, k_count))

comp_df = pd.DataFrame(comp_rows, columns=["state", "GM12878", "K562"])

# Sort states numerically (E1..E15)
comp_df["state_num"] = comp_df["state"].str.extract(r'E(\d+)').astype(int)
comp_df = comp_df.sort_values("state_num")

# Convert counts to fractions
gm_total = comp_df["GM12878"].sum()
k_total = comp_df["K562"].sum()

comp_df["GM_frac"] = comp_df["GM12878"] / gm_total
comp_df["K_frac"] = comp_df["K562"] / k_total

# -----------------------
# PLOT STATE FRACTIONS
# -----------------------
plt.figure(figsize=(10, 5))

x = range(len(comp_df))
width = 0.4

plt.bar([i - width/2 for i in x], comp_df["GM_frac"], width=width, label="GM12878")
plt.bar([i + width/2 for i in x], comp_df["K_frac"], width=width, label="K562")

plt.xticks(list(x), comp_df["state"])
plt.ylabel("Genome fraction")
plt.title("Chromatin state fractions (GM12878 vs K562)")
plt.legend()
plt.tight_layout()
plt.savefig(STATE_FRACTIONS_PNG)
plt.close()

print(f"Saved: {STATE_FRACTIONS_PNG}")

# -----------------------
# LOAD STATE SWITCH MATRIX
# -----------------------
rows = []
states_set = set()

with open(STATE_SWITCH_FILE) as f:
    for line in f:
        line = line.strip()
        if not line:
            continue

        # Expected format:
        # count  E1  E2
        parts = line.split()
        if len(parts) != 3:
            continue

        count = int(parts[0])
        gm_state = parts[1]
        k_state = parts[2]

        rows.append((gm_state, k_state, count))
        states_set.add(gm_state)
        states_set.add(k_state)

# Sort states (E1..E15)
states = sorted(states_set, key=lambda s: int(s[1:]))

# Build full matrix
matrix_df = pd.DataFrame(0, index=states, columns=states)

for gm_state, k_state, count in rows:
    matrix_df.loc[gm_state, k_state] += count

# Normalize rows to fractions
row_sums = matrix_df.sum(axis=1)
frac_df = matrix_df.div(row_sums, axis=0)

# -----------------------
# PLOT HEATMAP
# -----------------------
plt.figure(figsize=(8, 6))
plt.imshow(frac_df.values, aspect='auto', interpolation='nearest')
plt.colorbar(label="Fraction of GM12878 state reassigned")
plt.xticks(range(len(states)), states, rotation=90)
plt.yticks(range(len(states)), states)
plt.xlabel("K562 state")
plt.ylabel("GM12878 state")
plt.title("Chromatin state switching: GM12878 → K562")
plt.tight_layout()
plt.savefig(STATE_SWITCH_PNG)
plt.close()

print(f"Saved: {STATE_SWITCH_PNG}")

