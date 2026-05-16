import os
import random


def creation_files():
    directory = os.path.dirname(os.path.abspath(__file__))

    for i in range(1, 51):
        job = random.randint(5, 20)
        machine = random.randint(5, 10)

        file_name = f"instance_{i}.txt"
        path = os.path.join(directory, file_name)

        with open(path, "w", encoding="utf-8") as f:
            f.write(f"{job} {machine}\n")

            for _ in range(machine):
                processing_times = [str(random.randint(1, 100)) for _ in range(job)]
                f.write(" ".join(processing_times) + "\n")


creation_files()
print("The files have been created!")