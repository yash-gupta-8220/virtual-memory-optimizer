# main.py
# Virtual Memory Paging Simulator
# Written by: Yash Gupta
# Course: Operating Systems (CSE316)
# Problem Statement 7

from collections import deque, OrderedDict

# -------------------------------
# FIFO Algorithm
# -------------------------------
def fifo(reference, frames_count):
    frames = deque()
    faults = 0
    trace = []

    for page in reference:
        if page not in frames:
            faults += 1
            if len(frames) < frames_count:
                frames.append(page)
            else:
                frames.popleft()
                frames.append(page)
        trace.append(list(frames))
    return faults, trace

# -------------------------------
# LRU Algorithm
# -------------------------------
def lru(reference, frames_count):
    frames = OrderedDict()
    faults = 0
    trace = []

    for page in reference:
        if page in frames:
            frames.pop(page)
            frames[page] = True
        else:
            faults += 1
            if len(frames) < frames_count:
                frames[page] = True
            else:
                frames.popitem(last=False)
                frames[page] = True
        trace.append(list(frames.keys()))
    return faults, trace

# -------------------------------
# Optimal Algorithm
# -------------------------------
def optimal(reference, frames_count):
    frames = []
    faults = 0
    trace = []
    n = len(reference)

    for i, page in enumerate(reference):
        if page not in frames:
            faults += 1
            if len(frames) < frames_count:
                frames.append(page)
            else:
                farthest = -1
                victim = 0
                for idx, p in enumerate(frames):
                    try:
                        next_use = reference.index(p, i + 1)
                    except ValueError:
                        next_use = float('inf')
                    if next_use > farthest:
                        farthest = next_use
                        victim = idx
                frames[victim] = page
        trace.append(list(frames))
    return faults, trace

# -------------------------------
# Clock Algorithm
# -------------------------------
def clock(reference, frames_count):
    frames = [None] * frames_count
    use = [0] * frames_count
    ptr = 0
    faults = 0
    trace = []

    for page in reference:
        if page in frames:
            idx = frames.index(page)
            use[idx] = 1
        else:
            faults += 1
            while True:
                if frames[ptr] is None:
                    frames[ptr] = page
                    use[ptr] = 1
                    ptr = (ptr + 1) % frames_count
                    break
                if use[ptr] == 0:
                    frames[ptr] = page
                    use[ptr] = 1
                    ptr = (ptr + 1) % frames_count
                    break
                else:
                    use[ptr] = 0
                    ptr = (ptr + 1) % frames_count

        snapshot = [f for f in frames if f is not None]
        trace.append(snapshot)

    return faults, trace

# -------------------------------
# Print function
# -------------------------------
def print_trace(reference, trace):
    for i, state in enumerate(trace):
        print(f"Step {i+1} | Ref {reference[i]} | Frames: {state}")

# -------------------------------
# Demo Run
# -------------------------------
def demo():
    print("\nRunning DEMO example...\n")
    reference = [7,0,1,2,0,3,0,4,2,3,0,3,2]
    frames = 3

    algorithms = {
        "FIFO": fifo,
        "LRU": lru,
        "OPTIMAL": optimal,
        "CLOCK": clock
    }

    for name, algo in algorithms.items():
        print("\n==============================")
        print(f"Algorithm: {name}")
        print("==============================")
        faults, trace = algo(reference, frames)
        print_trace(reference, trace)
        print(f"Total Page Faults ({name}): {faults}")

# -------------------------------
# Main Program
# -------------------------------
print("\nVirtual Memory Simulation (main.py)\n")
print("1) Run Demo Example")
print("2) Enter Your Own Reference String")

choice = input("\nEnter choice (1 or 2): ")

if choice == '1':
    demo()
else:
    raw = input("Enter reference string (space-separated numbers): ")
    try:
        reference = [int(x) for x in raw.split()]
    except:
        print("Invalid input, using default demo reference.")
        reference = [7,0,1,2,0,3,0,4,2,3,0,3,2]

    try:
        frames = int(input("Enter number of frames: "))
    except:
        print("Invalid input, using frames = 3")
        frames = 3

    print("\nRunning ALL algorithms...\n")
    for name, algo in {
        "FIFO": fifo,
        "LRU": lru,
        "OPTIMAL": optimal,
        "CLOCK": clock
    }.items():
        print("\n==============================")
        print(f"Algorithm: {name}")
        print("==============================")
        faults, trace = algo(reference, frames)
        print_trace(reference, trace)
        print(f"Total Page Faults ({name}): {faults}")