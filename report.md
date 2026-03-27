# Simple Operating System Simulator Report

## Program Description
The **Simple Operating System Simulator** is a beginner-friendly Python command-line project that demonstrates core Operating Systems topics through a menu-driven neon terminal interface. The simulator is styled with a VA-11 HALL-A inspired cyberpunk aesthetic using ANSI escape codes, boxed panels, and neon colors.

The program includes:
- Process management with predefined processes
- Round Robin CPU scheduling with time quantum = 2
- Fixed-partition memory allocation and deallocation
- A text-based Gantt chart
- An in-memory file system
- Printer queue spooling
- A guided demo mode

The project is implemented using Object-Oriented Programming with the following classes:
- `Process`
- `Scheduler`
- `MemoryManager`
- `FileSystem`
- `PrinterSpooler`
- `OperatingSystemSimulator`

## How to Run
1. Open a terminal in the project folder.
2. Run the interactive program:

```bash
python os_simulator.py
```

3. Run the automatic demo mode:

```bash
python os_simulator.py --demo
```

4. Optional: install the project with pip from the project folder:

```bash
pip install .
```

5. After installation, you can launch it with:

```bash
simple-os-simulator
```

6. If your instructor expects a requirements file, this project also includes:

```bash
pip install -r requirements.txt
```

This command does not install extra packages because the simulator uses only the Python standard library.

## OS Concepts Explanation

### 1. Process Management
The simulator starts with four predefined processes. Each process stores:
- PID
- Process name
- Burst time
- Remaining time
- Memory requirement
- State
- Waiting time
- Turnaround time

The program tracks the required process states:
- **Ready**: the process has memory and is waiting for CPU time
- **Running**: the process is currently executing on the CPU
- **Waiting**: the process cannot run yet because memory is unavailable
- **Terminated**: the process has completed execution

This part of the project demonstrates how an operating system keeps information about active jobs and updates their state during execution.

### 2. Round Robin Scheduling
The CPU scheduler uses the **Round Robin** algorithm with a fixed time quantum of **2** time units.

How it works:
- A process from the ready queue gets the CPU
- It runs for up to 2 time units
- If it is not finished, it returns to the Ready state
- If it finishes, it moves to the Terminated state

The simulator also calculates:
- **Waiting time**
- **Turnaround time**
- **Execution order**

At the end of scheduling, the program prints a text-based **Gantt chart** to show the order and timing of execution.

### 3. Memory Management Using Fixed Partitions
The simulator uses fixed memory partitions:

```text
[64, 64, 128] MB
```

Each process has a memory requirement. A process is allocated only if it fits in a free partition.

Rules shown by the simulator:
- If a partition is available and large enough, the process is allocated
- If no suitable partition is available, the process enters the **Waiting** state
- When a process terminates, its partition is freed
- Waiting processes can then move to **Ready** if memory becomes available

The console memory map shows:
- Partition number
- Partition size
- Whether the partition is free or occupied
- Which process is currently using it

### 4. File System Simulation
The simulator includes a simple **in-memory file system**, meaning no real files are created by the OS simulation itself.

Supported operations:
- Create a file
- Delete a file
- List files
- Display file contents

This models the basic idea of a file system by storing file names and file contents in Python data structures.

### 5. I/O Spooling with a Printer Queue
The simulator includes a **printer spooler** that behaves like a print queue.

Supported operations:
- Add a print job
- View queued jobs
- Process the next print job

This demonstrates the idea of **spooling**, where I/O jobs are stored in a queue and handled in order instead of being processed immediately by the CPU.

## Program Features and Requirement Mapping

### Core Features Implemented
- Process management with 4 predefined processes
- Process states: Ready, Running, Waiting, Terminated
- Round Robin scheduling
- Waiting time and execution order tracking
- Text-based Gantt chart
- Fixed-partition memory management
- Memory allocation and deallocation
- Console memory map
- In-memory file system
- Printer queue / spooling simulation

### User Interface Features
- Dark terminal dashboard style
- Neon pink, cyan, purple, and yellow color palette
- Boxed section panels
- Styled headers such as `PROCESS MANAGER`, `MEMORY MAP`, and `PRINTER SPOOLER`
- Consistent visual formatting across all screens
- Highlighted process states using color

### Menu Features
- View process table
- Run scheduler
- View memory map
- File system operations
- Printer queue operations
- Run full demo

## Sample Outputs

### Screenshot Placeholder 1: Main Process Table
> Insert screenshot of the neon `PROCESS MANAGER` panel here.

### Screenshot Placeholder 2: Memory Map
> Insert screenshot of the `MEMORY MAP` panel here.

### Screenshot Placeholder 3: Gantt Chart
> Insert screenshot of the final Round Robin `GANTT CHART` here.

### Screenshot Placeholder 4: File System and Printer Queue
> Insert screenshot of the `IN-MEMORY FILE SYSTEM` and `PRINTER SPOOLER` panels here.

### Screenshot Placeholder 5: Demo Mode
> Insert screenshot of a step-by-step scheduler demo screen here.

## Conclusion
This project successfully demonstrates key Operating Systems ideas in a clear and presentation-friendly way. It shows how processes are managed, how CPU time is shared with Round Robin scheduling, how fixed memory partitions affect execution, how simple file operations can be simulated in memory, and how I/O spooling works through a printer queue.

The program remains simple enough for a live class presentation while still looking polished and visually distinctive because of its cyberpunk neon terminal design.
