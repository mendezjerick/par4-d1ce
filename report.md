# Simple Operating System Simulator Report

## Program Description
The **Simple Operating System Simulator** is a web-based final project built to demonstrate core Operating Systems concepts in a clear, beginner-friendly, and visually polished way. It is a rebuilt version of the original terminal demo, but now presented as a browser dashboard using **Flask**, **HTML**, **CSS**, and **JavaScript**.

The simulator keeps the same academic purpose as the original project while improving usability and presentation. It includes:

- process management
- Round Robin CPU scheduling
- fixed-partition memory management
- an in-memory file system
- printer queue / I/O spooling
- step-by-step and automatic demo controls

The interface uses a **VA-11 HALL-A inspired cyberpunk aesthetic** with dark panels, neon highlights, glowing borders, and a futuristic dashboard layout to make the project more engaging during live presentation and easier to capture in screenshots.

## OS Concepts Used
This project demonstrates several important Operating Systems concepts:

- **Process Management** through process records and state transitions
- **CPU Scheduling** through the Round Robin algorithm
- **Memory Management** through fixed partitions and allocation/deallocation
- **File System Concepts** through in-memory file operations
- **I/O Management** through printer queue spooling

Each concept is shown visually in its own panel so that the relationship between modules is easy to explain.

## Process Management Explanation
The simulator starts with four predefined processes:

- `P1 - Mix Compiler`
- `P2 - Neon Renderer`
- `P3 - Receipt Sync`
- `P4 - Night Backup`

Each process contains the required fields:

- PID
- process name
- burst time
- remaining time
- memory requirement
- state
- waiting time
- turnaround time

The system tracks these process states:

- **Ready** - the process has memory and is waiting for CPU time
- **Running** - the process is currently using the CPU
- **Waiting** - the process cannot continue because memory is not available
- **Terminated** - the process has finished execution

The Process Manager panel shows all of this data in a structured table, making it easy to discuss how processes are represented inside an operating system.

## Round Robin Scheduling Explanation
The CPU scheduling module uses the **Round Robin** algorithm.

- Default time quantum: **2**
- The quantum can be changed in the web interface
- One scheduling step runs exactly one time slice
- Demo mode automatically keeps stepping until the sample run finishes

Round Robin works as follows:

1. A process from the ready queue is selected.
2. It runs for up to the configured time quantum.
3. If it is not finished, it returns to the Ready queue.
4. If it finishes, it moves to the Terminated state.

The simulator records:

- execution order
- waiting time
- turnaround time
- average waiting time
- average turnaround time

The web dashboard also includes a **Gantt chart** that displays the order and duration of CPU slices as a horizontal timeline.

## Memory Management Explanation
The simulator uses **fixed memory partitions**:

```text
[64, 64, 128] MB
```

Each process has a memory requirement. The memory manager uses a simple **first-fit allocation** approach:

- If a free partition is large enough, the process is allocated there.
- If no partition fits, the process stays in the **Waiting** state.
- When a process terminates, its partition is automatically freed.
- Waiting processes are checked again when memory becomes available.

The web version represents memory as a set of cards and bars, showing:

- partition number
- partition size
- whether the partition is occupied
- which process is using it
- used and free memory inside each partition

This makes the memory concept easier to explain than a plain text console output.

## File System Explanation
The project includes a simple **in-memory file system**, meaning it does not create or delete real operating system files as part of the simulation itself.

Supported operations:

- create file
- delete file
- list files
- display file contents

Each file stores:

- file name
- contents
- size

The File System panel includes a file creation form, a file list, and a file viewer. This demonstrates the idea of file storage and retrieval while keeping the implementation safe and simple.

## I/O Spooling Explanation
The simulator includes a **printer spooler** to demonstrate I/O spooling.

Supported actions:

- add a print job
- view queued print jobs
- process the next job
- review recently completed jobs

The spooler uses **FIFO order**, which means the first job added is the first one processed. This models how operating systems often buffer output jobs before sending them to a device.

## Web Implementation Overview
The web version uses a simple client-server structure:

- **Flask backend** stores the simulator state in Python objects
- **HTML/CSS frontend** builds the dashboard layout and cyberpunk design
- **JavaScript** sends `fetch()` requests to Flask routes and updates the page dynamically

Important implementation details:

- No database is used
- All simulator data is stored in memory
- The scheduler state is deterministic for presentation
- Completed processes free memory automatically
- The page updates without reloading when actions are performed

Main files:

- `app.py` - backend logic and API routes
- `templates/index.html` - dashboard layout
- `static/style.css` - interface styling
- `static/script.js` - frontend interactivity

## Sample Output / Screenshot Placeholders
### Screenshot Placeholder 1: Hero Dashboard
> Insert screenshot of the main web dashboard header and control panel here.

### Screenshot Placeholder 2: Process Manager
> Insert screenshot of the process table with different process states here.

### Screenshot Placeholder 3: CPU Scheduler and Gantt Chart
> Insert screenshot of the scheduler panel after several Round Robin steps here.

### Screenshot Placeholder 4: Memory Manager
> Insert screenshot of the fixed partition memory cards here.

### Screenshot Placeholder 5: File System Panel
> Insert screenshot of the file list and file viewer here.

### Screenshot Placeholder 6: Printer Queue / I-O Spooler
> Insert screenshot of the printer queue and completed jobs here.

## Conclusion
The web-based **Simple Operating System Simulator** successfully demonstrates the required Operating Systems concepts in a form that is more visual, interactive, and presentation-friendly than the original terminal version.

It still satisfies the original academic requirements, but the browser dashboard makes the simulation easier to understand, easier to demo live, and more impressive in screenshots for the final report and presentation. The project remains simple enough for student explanation while providing a polished and memorable user experience.
