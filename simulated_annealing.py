import math
import os
import copy
import random
import time
import pandas as pd
from matplotlib import pyplot as plt


# =================
''' PARAMETERS '''
# =================

p = []
file = input('Define the name of your input file: ')
if os.path.exists(file):
    print(f"File '{file}' loaded succesfully!")
    with open(file, 'r', encoding = 'utf-8') as f:
        for i, line in enumerate(f):
            if i == 0:
                values = line.split()

                # Number of jobs
                n = int(values[0])

                # Number of machines
                m = int(values[1])

            else:
                values = line.split()

                # Processing time of job j in machine i (p ij)
                l = []
                for j in range(len(values)):
                    l.append(int(values[j]))
                p.append(l)

else:
    print(f"Error: File '{file}' doesn't exist.")
    exit()

# Big number
M = 0
max_p_t = 0
for row in p:
    for element in row:
        M += element
        max_p_t = max(max_p_t, element)

# Shift length
T = int(input("Shift length: "))

# Maximal number of shifts
S = int(input("Maximal number of shifts: "))

print(f"Big number created: {M}\n")

# =================
''' FUNCTIONS '''
# =================

def schedule_operation(earliest_start, processing_time, T):

    # Earliest shift in which the job can start (starting with 0)
    shift = int(earliest_start // T)

    # If the job can be scheduled in the earliest shift it will finish also there
    if earliest_start + processing_time <= (shift + 1) * T:
        return earliest_start + processing_time

    # Otherwise it'll start and finish in the next shift
    else:
        return (shift + 1) * T + processing_time


# It computes the E matrix given a permutation list
def compute_schedule(permutation_list):

    # Complection time of job in machine i in position l (E[i][l])
    E = [[0.0] * n for _ in range(m)]

    for i in range(m):
        for l in range(n):
            # Number of the job
            j = permutation_list[l]

            # If it's the first machine and the first job
            if i == 0 and l == 0:
                earliest_start = 0

            # If it's the first machine but not the first job we take the complection time of the job before in
            # the same machine
            elif i == 0 and l > 0:
                earliest_start = E[0][l - 1]

            # If it's the first job but not the first machine we take the complection time of the first job of
            # the machine before
            elif i > 0 and l == 0:
                earliest_start = E[i - 1][0]

            # If it's not the first machine and not the first job we take the biggest between the complection
            # time of the job before in the same machine and of the same job in the machine before
            else:
                earliest_start = max(E[i - 1][l], E[i][l - 1])

            # Knowing now the earliest start we schedule the operation
            E[i][l] = schedule_operation(earliest_start, p[i][j], T)

    return E


# It gives the total makespan of the job shop
def makespan(permutation_list):
    E = compute_schedule(permutation_list)
    return E[m - 1][n - 1]


# It swaps two jobs to see if the solution is better or worse
def swap_move(permutation_list):
    copy_list = copy.deepcopy(permutation_list)

    # We select two positions of the list swapping
    positions_swapping = random.sample(range(len(copy_list)), 2)

    # And we swap
    copy_list[positions_swapping[0]], copy_list[positions_swapping[1]] =(
        copy_list[positions_swapping[1]], copy_list[positions_swapping[0]])
    return copy_list


# It inserts a job in a different position to see if the solution is better or worse
def insertion_move(permutation_list):
    copy_list = copy.deepcopy(permutation_list)

    # We select two positions of the list inserting
    positions_insert = random.sample(range(len(copy_list)), 2)

    # And we insert
    elem = copy_list.pop(positions_insert[0])
    copy_list.insert(positions_insert[1], elem)
    return copy_list


# It takes on a 50/50 possibility the swap or the insertion move
def get_neighbour(permutation_list):
    choice = random.randint(0, 1)
    if choice == 0:
        return swap_move(permutation_list)
    else:
        return insertion_move(permutation_list)


def simulated_annealing(temperature, alpha, max_iterations):

    # We select the initial solution sorted by descending values of the sum of the processing time for every job
    current_list = sorted(range(n), key=lambda j: sum(p[i][j] for i in range(m)), reverse=True)
    current_cost = makespan(current_list)

    # The best actual solution is the initial solution
    best_list = current_list[:]
    best_cost = current_cost

    for iteration in range(max_iterations):

        # Creates a neighbour to the solution using swapping or insert
        neighbour_list = get_neighbour(current_list)
        neighbour_cost = makespan(neighbour_list)

        # Cost difference between the actual and the neighbour cost
        delta = neighbour_cost - current_cost

        # If the neighbour is better we always accept it, else we acccept with probability e^(-delta/T)
        if delta <= 0 or random.random() < math.exp(-delta / temperature):
            current_list = neighbour_list
            current_cost = neighbour_cost

        # If the current solution is better than the best solution we update it
        if current_cost < best_cost:
            best_list = current_list[:]
            best_cost = current_cost

        # Geometric cooling
        temperature *= alpha

        # If temperature is too low we stop the iteration
        if temperature < 1e-3:
            break

    return best_list, best_cost


# =================
''' ALGORITHM '''
# =================

start = time.time()
best_list, best_cost = simulated_annealing(1000, 0.9998, 100000)
end = time.time()
print(f"Best cost: {best_cost}")
print(end - start)

# =================
''' GANTT CHART '''
# =================

E = compute_schedule(best_list)
gantt_data = []

for i in range(m):
    for l in range(n):
        job_idx = best_list[l]
        end = E[i][l]
        duration = p[i][job_idx]
        start = end - duration

        gantt_data.append({
            "Machine": f"M{i + 1}",
            "Start": start,
            "End": end,
            "Duration": duration,
            "Job": f"J{job_idx + 1}"
        })

df = pd.DataFrame(gantt_data)
fig, ax = plt.subplots(figsize=(15, 6))
cmap = plt.get_cmap('tab20')
job_colors = {f"J{j+1}": cmap(j) for j in range(n)}

for i, row in df.iterrows():
    ax.barh(y=row["Machine"],
            width=row["Duration"],
            left=row["Start"],
            color=job_colors[row["Job"]],
            edgecolor='black',
            alpha=0.8)

    ax.text(x=row["Start"] + row["Duration"] / 2,
            y=row["Machine"],
            s=row["Job"],
            va='center', ha='center', color='black', fontweight='bold')

max_time = int(df["End"].max())
ax.set_xticks(range(0, max_time + 10, 10))
ax.set_xlabel('Time')
ax.set_ylabel('Machines')
ax.set_title('Flowshop Scheduling Gantt Chart')
ax.grid(True, axis='x', linestyle='--', alpha=0.7)

for s in range(S + 1):
    shift_position = s * T
    if shift_position < max_time:
        ax.axvline(x=shift_position,
                   color='red',
                   linestyle='-',
                   linewidth=2.5,
                   alpha=0.8,
                   zorder=0)

for m_id in df["Machine"].unique():
    m_df = df[df["Machine"] == m_id].sort_values("Start")

    for i in range(len(m_df) - 1):
        actual_end = m_df.iloc[i]["End"]
        next_start = m_df.iloc[i + 1]["Start"]
        duration_gap = next_start - actual_end

        if duration_gap > 1e-3:
            ax.barh(y=m_id,
                    width=duration_gap,
                    left=actual_end,
                    color='#FFF59D',
                    hatch='///',
                    edgecolor='#FBC02D',
                    alpha=0.6,
                    zorder=2)

            if duration_gap > 50:
                ax.text(x=actual_end + duration_gap / 2,
                        y=m_id,
                        s="Maintenance",
                        va='center', ha='center',
                        color='#7F6000',
                        fontsize=7,
                        fontweight='bold',
                        fontstyle='italic')

ax.invert_yaxis()
plt.tight_layout()
plt.show()