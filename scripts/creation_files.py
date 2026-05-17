import math
import os
import random


def creation_files():

    directory = os.path.dirname(os.path.abspath(__file__))
    folder_name = "instances"
    folder_path = os.path.join(directory, folder_name)

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    for i in range(1, 51):
        job = random.randint(5, 20)
        machine = random.randint(5, 10)

        file_name = f"instance_{i}.txt"
        path = os.path.join(folder_path, file_name)

        with open(path, "w", encoding="utf-8") as f:
            f.write(f"{job} {machine}\n")

            # Big number
            M = 0
            max_p = 0
            for _ in range(machine):
                processing_times = [str(random.randint(1, 100)) for _ in range(job)]
                for p in processing_times:
                    M += int(p)
                    if int(p) > max_p:
                        max_p = int(p)
                f.write(" ".join(processing_times) + "\n")

            # Shift length
            T = max_p * random.choice([2, 3, 4, 5])

            # Maximal number of shifts
            S = max(1, math.ceil(M / T))

            f.write(f"{M} {T} {S}")


creation_files()
print("The files have been created!")