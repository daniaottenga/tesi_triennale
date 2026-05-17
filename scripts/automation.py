import os
import csv
from main import function
from simulated_annealing import simulated_annealing

directory = os.path.dirname(os.path.abspath(__file__))
folder_name = "results"
folder_path = os.path.join(directory, folder_name)

if not os.path.exists(folder_path):
    os.makedirs(folder_path)

#results
csv_file_path = os.path.join(folder_path, "max_time.csv")

headers = ["Instance", "LB", "Best Obj.", "Time 1", "Obj.", "Time 2", "vs Best", "vs LB"]

with open(csv_file_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f, delimiter=";")

    writer.writerow(headers)
    #51
    for i in range(1, 2):
        solution, lb, time1 = function(i)
        metaheuristic, time2 = simulated_annealing(i)

        #if time1 >= 300:
        #    time1 = "300*"
        #else:
        time1 = round(float(time1), 4)

        if solution is not None:
            vs_best = (metaheuristic - solution) / solution * 100
            solution = int(solution)
            vs_best = round(float(vs_best), 2)
        else:
            vs_best = "-"
            solution = "-"

        if lb is not None:
            vs_lb = (metaheuristic - lb) / lb * 100
            vs_lb = round(float(vs_lb), 2)
        else:
            vs_lb = "-"

        row = [i, int(lb), solution, time1, metaheuristic, round(float(time2), 4),
               vs_best, vs_lb]
        writer.writerow(row)
