# Simple Operating System Simulator - System Documentation

## 1. System Overview

The Simple Operating System Simulator is a Flask-based web application that presents Operating Systems concepts inside a browser desktop shell. The interface, named **Neon District OS**, simulates a small desktop environment with boot flow, wallpapers, movable shortcuts, a taskbar, launcher menu, windowed applications, and live system status.

The project is educational. It does not replace a real operating system, kernel, memory manager, disk driver, or file system. Instead, it models the behavior of common OS components with clear state transitions and visual feedback.

### Main Goals

| Goal | Description |
|---|---|
| Teach core OS concepts | Demonstrate process management, CPU scheduling, memory allocation, disk scheduling, file operations, and I/O spooling. |
| Provide a visual simulator | Replace terminal-only output with a desktop-style browser interface. |
| Support live demonstrations | Allow stepping through scheduling frames, running complete simulations, and inspecting system state. |
| Keep state understandable | Store all simulator data in memory so the project remains easy to run and explain. |

### Technology Stack

| Layer | Technology | Responsibility |
|---|---|---|
| Backend | Python 3.9+, Flask 3.x | Simulator state, algorithms, REST API, HTML rendering. |
| Frontend markup | HTML/Jinja template | Desktop shell structure and app windows. |
| Frontend behavior | JavaScript | Window manager, app launcher, API calls, rendering dynamic state. |
| Styling | CSS | Cyberpunk desktop theme, layouts, app windows, responsive design. |
| Storage | In-memory Python objects + browser localStorage | Simulator data in Flask memory; UI preferences and shortcut positions in browser storage. |

## 2. Project Structure

```text
par4-d1ce/
|-- app.py
|-- os_simulator.py
|-- requirements.txt
|-- pyproject.toml
|-- README.md
|-- report.md
|-- demo_guide.txt
|-- presentation_outline.md
|-- templates/
|   `-- index.html
|-- static/
|   |-- script.js
|   |-- style.css
|   `-- wallpapers/
|       `-- dice.jpg
|-- wallpaper/
|   |-- dice.jpg
|   `-- fangyi.png
`-- docs/
    `-- SYSTEM_DOCUMENTATION.md
```

### Important Files

| File | Purpose |
|---|---|
| `app.py` | Main Flask application and complete web simulator implementation. Defines data models, managers, scheduling logic, memory simulation, disk simulation, file system, spooler, mini game, and API routes. |
| `templates/index.html` | Browser desktop shell layout, including boot screen, desktop icon area, window layer, start menu, taskbar, and installed app windows. |
| `static/script.js` | Frontend controller for boot sequence, window management, draggable shortcuts, app rendering, API calls, form handling, and user interactions. |
| `static/style.css` | Full visual design for the shell, app windows, controls, charts, tables, taskbar, icons, and responsive layouts. |
| `os_simulator.py` | Earlier command-line simulator implementation retained as a reference. |
| `README.md` | User-facing project overview and setup notes. |
| `report.md` | Project report written for presentation/course submission. |

## 3. High-Level Architecture

```text
Browser
  |
  | GET /
  v
Flask renders templates/index.html
  |
  | static/script.js requests /api/state and action endpoints
  v
OperatingSystemSimulator
  |
  | coordinates
  v
ProcessManager, Scheduler, MemoryManager, DiskManager,
InMemoryFileSystem, PrinterSpooler, MiniGame
```

### Backend Module Relationships

| Component | Main Class | Responsibility |
|---|---|---|
| Process model | `Process` | Stores PID, arrival time, burst time, priority, memory requirement, runtime state, waiting time, and completion metrics. |
| Process management | `ProcessManager` | Creates, edits, deletes, resets, lists, and generates sample processes. |
| CPU scheduling | `Scheduler` | Builds full timeline frames for supported scheduling algorithms. |
| Memory management | `MemoryManager` | Allocates and releases fixed or variable memory regions. |
| File system | `InMemoryFileSystem` | Creates, edits, deletes, reads, and lists simulated files and folders. |
| Disk management | `DiskManager` | Simulates file block allocation and disk head scheduling algorithms. |
| I/O spooling | `PrinterSpooler` | Manages FIFO print jobs and completed output history. |
| Mini app | `MiniGame` | Provides a small Guess the Number app in the desktop shell. |
| System coordinator | `OperatingSystemSimulator` | Owns all modules, rebuilds schedules, logs events, and returns frontend snapshots. |

## 4. Runtime State Model

All main simulator state is stored in memory inside one global `OperatingSystemSimulator` instance in `app.py`.

```text
simulator = OperatingSystemSimulator()
```

Because the state is in memory:

| Behavior | Result |
|---|---|
| Refresh browser | Current backend state is reloaded from Flask memory. |
| Restart Flask server | Simulator resets to default sample data. |
| Multiple browser tabs | They share the same backend simulator state. |
| Browser localStorage | Stores UI-only preferences such as wallpaper, reduced motion, and desktop shortcut positions. |

## 5. Desktop Shell

The desktop shell is the user-facing environment. It is implemented by `templates/index.html`, `static/style.css`, and `static/script.js`.

### Shell Features

| Feature | Description |
|---|---|
| Boot screen | Shows a simulated startup sequence before entering the desktop. |
| Wallpaper presets | User can switch cyberpunk-themed backgrounds. |
| Desktop shortcuts | Launch apps from desktop icons. Shortcuts can be moved by holding and dragging. |
| Taskbar | Shows launcher button, open apps, status message, settings shortcut, and live clock. |
| Launcher menu | Opens installed apps and exposes quick wallpaper/system actions. |
| Window manager | Supports app focus, z-index layering, minimize, maximize, close, drag, and restore behavior. |
| Settings app | Controls wallpaper, reduced motion, scheduler defaults, loading sample data, and reset. |

### Installed Desktop Apps

| App | Purpose |
|---|---|
| System Monitor | Overview metrics, activity feed, and OS concept map. |
| Process Manager | Process CRUD, sample generation, and process table. |
| CPU Scheduler | Algorithm configuration, step/run controls, ready queues, execution order, and Gantt chart. |
| Memory Manager | Partition/segment view, memory usage, waiting processes, and fragmentation. |
| Disk Manager | Disk scheduling and block-based storage visualization. |
| File Explorer | Create, edit, delete, view, and group in-memory files. |
| Printer Queue | Add and process print jobs using FIFO spooling. |
| Mini Game | External game launcher window. |
| Settings | Shell and simulator configuration. |

## 6. Process Management

### Process Fields

| Field | Meaning |
|---|---|
| `pid` | Unique process identifier. |
| `name` | Display name of the process. |
| `arrival_time` | Time unit when the process enters the system. |
| `burst_time` | Total CPU time required. |
| `remaining_time` | CPU time still needed. |
| `priority` | Lower number means higher priority in priority algorithms. |
| `memory_requirement` | Memory needed before the process can run. |
| `state` | `Waiting`, `Ready`, `Running`, or `Terminated`. |
| `waiting_time` | Time spent waiting while not running after arrival. |
| `turnaround_time` | Completion time minus arrival time. |
| `completion_time` | Clock time when the process terminates. |
| `memory_slot` | Assigned partition/segment label or `Unassigned`. |
| `queue_level` | MLQ/MLFQ queue number. |

### Process State Meaning

| State | Meaning |
|---|---|
| Waiting | Process has not arrived yet, has no memory, or cannot currently run. |
| Ready | Process has arrived, has memory, and is waiting for CPU. |
| Running | Process is currently dispatched on the simulated CPU. |
| Terminated | Process completed all CPU burst time and released memory. |

### Default Sample Processes

| PID | Name | Arrival | Burst | Priority | Memory |
|---:|---|---:|---:|---:|---:|
| 1 | Mix Compiler | 0 | 5 | 2 | 64 MB |
| 2 | Neon Renderer | 1 | 4 | 1 | 128 MB |
| 3 | Receipt Sync | 2 | 3 | 4 | 64 MB |
| 4 | Night Backup | 3 | 6 | 5 | 64 MB |
| 5 | Sound Driver | 4 | 2 | 3 | 32 MB |

## 7. CPU Scheduling

The scheduler does not mutate the original process definitions directly. It clones process definitions, simulates a full timeline, captures each time step as a frame, and lets the frontend step through those frames.

### Supported Algorithms

| Key | Algorithm | Preemptive | Selection Rule |
|---|---|---:|---|
| `fcfs` | First Come First Served | No | Earliest arrival time, then PID. |
| `sjf` | Shortest Job First | No | Lowest total burst time among ready processes. |
| `srtf` | Shortest Remaining Time First | Yes | Lowest remaining time among ready processes. |
| `priority_np` | Priority Scheduling | No | Lowest priority number among ready processes. |
| `priority_p` | Priority Scheduling | Yes | Lowest priority number; may preempt current process. |
| `round_robin` | Round Robin | Yes | FIFO ready queue with fixed time quantum. |
| `mlq` | Multilevel Queue | Partially | Uses fixed queue levels from priority ranges. Higher queue can preempt lower queue. |
| `mlfq` | Multilevel Feedback Queue | Yes | Starts jobs at Q0, demotes after quantum use, periodically boosts to Q0. |

### Queue Behavior

| Algorithm | Queue Model |
|---|---|
| FCFS, SJF, SRTF, Priority | Uses a computed ready pool each tick. |
| Round Robin | Uses one FIFO ready queue. |
| MLQ | Uses three fixed queues. Priority 1-2 maps to Q0, 3-4 to Q1, 5+ to Q2. |
| MLFQ | Uses three feedback queues. Jobs start at Q0 and are demoted after consuming their queue quantum. Every 10 time units, waiting jobs are boosted to Q0. |

### Scheduling Formulas

| Metric | Formula |
|---|---|
| Turnaround Time | `turnaround_time = completion_time - arrival_time` |
| Waiting Time | In this simulator, incremented by 1 for each arrived, unfinished process that is not running during a tick. |
| Average Waiting Time | `avg_waiting = sum(waiting_time) / total_processes` |
| Average Turnaround Time | `avg_turnaround = sum(turnaround_time) / total_processes` |
| Throughput | `throughput = terminated_processes / current_clock` |
| Gantt Segment Duration | `duration = end - start` |

### Simulation Flow

```text
1. Clone all process definitions.
2. Reset memory according to selected mode.
3. At each clock tick:
   a. Mark newly arrived processes.
   b. Try to allocate memory to arrived processes.
   c. Build or update ready queues.
   d. Select a process based on the active algorithm.
   e. Run selected process for one tick.
   f. Decrement remaining time.
   g. Increment waiting time for other arrived unfinished processes.
   h. Capture Gantt segment and frame snapshot.
   i. If process completes, release its memory.
4. Stop when all processes terminate, a memory block occurs, or the safety tick limit is reached.
```

## 8. Memory Management

The simulator supports two educational memory modes: fixed partitions and variable partitions.

### Fixed Partition Mode

Default fixed partitions:

| Partition | Size |
|---|---:|
| Partition 1 | 64 MB |
| Partition 2 | 64 MB |
| Partition 3 | 128 MB |
| Partition 4 | 64 MB |

A process can be allocated to the first available partition large enough for its memory requirement.

### Variable Partition Mode

Variable mode begins with one free segment equal to total memory. When a process is allocated, the segment is split into:

| Segment | Meaning |
|---|---|
| Allocated block | Exactly the process memory requirement. |
| Free remainder | Remaining unallocated memory after the process block. |

When a process terminates, its segment is released and adjacent free segments are merged.

### Memory Formulas

| Metric | Formula |
|---|---|
| Fixed Used Memory | `sum(process.memory_requirement for allocated processes)` |
| Fixed Free Space Per Partition | `partition_size - process_memory_requirement` |
| Internal Fragmentation | `sum(unused_space_inside_allocated_fixed_partitions)` |
| Variable Used Memory | `sum(size of allocated variable segments)` |
| Total Free Memory | `total_memory - used_memory` |
| Largest Free Block | `max(size of free regions)` |
| External Fragmentation | `total_free_memory - largest_free_block` |
| Usage Percent | `(used_memory / total_memory) * 100` |

### System Memory Overlay

The displayed memory view also adds educational system regions:

| Region | Formula |
|---|---|
| File Cache | `ceil(total_file_bytes / 32)` MB, minimum 1 MB when files exist. |
| I/O Spooler | `ceil((queued_print_bytes + recent_completed_print_bytes) / 32)` MB. |

These regions make file and printer actions visibly affect the memory view.

## 9. Disk Management

The Disk Manager combines disk scheduling with a simplified block storage model.

### Storage Model

| Property | Default |
|---|---:|
| Total blocks | 64 |
| Block size | 32 characters |
| Cylinder range | 0 to 199 |
| Default head position | 50 |

File storage uses simulated blocks. File content length determines how many blocks are needed.

### Storage Formulas

| Metric | Formula |
|---|---|
| Blocks Needed | `blocks_needed = max(1, ceil(max(file_size, 1) / block_size))` |
| Used Blocks | `sum(blocks allocated to each stored file)` |
| Free Blocks | `total_blocks - used_blocks` |
| Used Percent | `(used_blocks / total_blocks) * 100` |

### Disk Scheduling Algorithms

| Key | Algorithm | Behavior |
|---|---|---|
| `fcfs` | First Come First Served | Services requests in input order. |
| `sstf` | Shortest Seek Time First | Always services the closest pending request. |
| `scan` | SCAN | Moves in one direction to disk end, then reverses. |
| `c_scan` | Circular SCAN | Moves in one direction to disk end, jumps to the other end, then continues. |
| `look` | LOOK | Like SCAN, but only moves as far as the furthest request. |
| `c_look` | Circular LOOK | Like C-SCAN, but jumps between furthest real requests instead of disk ends. |

### Head Movement Formula

```text
total_head_movement = sum(abs(path[i + 1] - path[i]) for i in range(len(path) - 1))
```

Example:

```text
Path: 50 -> 82 -> 170
Movement: |82 - 50| + |170 - 82| = 32 + 88 = 120
```

## 10. File System Simulation

The file system is implemented by `InMemoryFileSystem`. It stores file metadata and content in a Python dictionary keyed by normalized path.

### File Fields

| Field | Meaning |
|---|---|
| `path` | Full simulated path, such as `/docs/notes.txt`. |
| `name` | File name only. |
| `folder` | Normalized folder path. |
| `content` | Text content. |
| `size` | Character count of content. |
| `created_at` | Timestamp from file creation. |
| `updated_at` | Timestamp from latest edit. |

### File Operations

| Operation | Behavior |
|---|---|
| Create | Validates filename, creates dictionary entry, allocates disk blocks. |
| Read | Returns file metadata and content. |
| Edit | Can rename, move folders, replace content, and update disk allocation. |
| Delete | Removes file entry and frees disk blocks. |
| List | Returns sorted file items and discovered folders. |

The file system never writes user-created files to the host computer.

## 11. Printer Queue and I/O Spooling

The printer queue simulates FIFO spooling with a pending queue and completed history.

### Print Job Fields

| Field | Meaning |
|---|---|
| `id` | Incrementing job ID. |
| `name` | Document name. |
| `content` | Text sent to printer. |
| `size` | Character count. |
| `source` | Submitting app/process label. |
| `created_at` | Timestamp when the job was queued. |

### FIFO Behavior

```text
enqueue(job) -> append to right side of queue
process_next_job() -> remove from left side of queue
```

This demonstrates that I/O jobs are buffered and processed one at a time instead of being handled instantly.

## 12. Mini Game

The system includes a small Guess the Number app as a demonstration of a normal installed program inside the desktop shell. It tracks:

| Field | Meaning |
|---|---|
| Secret number | Random number from 1 to 20. |
| Attempts | Number of guesses. |
| Message | Current hint/result. |
| History | Recent guesses and hints. |

## 13. API Reference

Most API responses follow this shape:

```json
{
  "ok": true,
  "message": "Action result.",
  "state": {}
}
```

### Core and Process Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Render desktop shell. |
| GET | `/api/state` | Return full simulator snapshot. |
| POST | `/api/reset` | Reset simulator to defaults. |
| POST | `/api/load-sample` | Reload default sample processes. |
| POST | `/api/processes/reset` | Reset process runtime values. |
| POST | `/api/processes/generate` | Generate random sample processes. |
| GET | `/api/processes` | Return process-oriented snapshot. |
| POST | `/api/processes` | Create a process. |
| PUT | `/api/processes/<pid>` | Update a process. |
| DELETE | `/api/processes/<pid>` | Delete a process. |

### Scheduler and Memory Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/scheduler/config` | Update scheduler algorithm, quantum, queue quantums, and memory mode. |
| POST | `/api/quantum` | Update Round Robin quantum. |
| POST | `/api/scheduler/reset` | Reset the schedule view to frame 0. |
| POST | `/api/scheduler/step` | Advance one simulation frame. |
| POST | `/api/scheduler/run` | Jump to final simulation frame. |
| GET | `/api/memory` | Return memory-oriented snapshot. |
| POST | `/api/memory/config` | Update memory mode. |
| POST | `/api/memory/allocate` | Rebuild allocation view. |
| POST | `/api/memory/release` | Refresh memory release view. |

### File, Printer, Disk, and Game Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/files` | Return file system state. |
| POST | `/api/files` | Create a simulated file. |
| GET | `/api/files/<path:file_path>` | Read a simulated file. |
| PUT | `/api/files/<path:file_path>` | Edit a simulated file. |
| DELETE | `/api/files/<path:file_path>` | Delete a simulated file. |
| GET | `/api/printer` | Return printer queue state. |
| POST | `/api/printer/jobs` | Add a print job. |
| POST | `/api/printer/process` | Process next print job. |
| GET | `/api/disk` | Return disk manager state. |
| POST | `/api/disk/schedule` | Run disk scheduling. |
| POST | `/api/game/reset` | Reset mini game. |
| POST | `/api/game/guess` | Submit mini game guess. |

## 14. Frontend Rendering and Interaction

### Important Frontend Responsibilities

| Function Area | Representative Functions | Description |
|---|---|---|
| Boot flow | `runBootSequence`, `enterDesktop` | Simulates boot progress and opens default apps. |
| Window manager | `openWindow`, `closeWindow`, `minimizeWindow`, `toggleMaximizeWindow`, `applyWindowLayout` | Controls app window lifecycle and layout. |
| Desktop shortcuts | `renderDesktopIcons`, `handleDesktopIconPointerDown`, `handleDesktopIconPointerMove`, `handleDesktopIconPointerEnd` | Renders and moves desktop shortcuts. |
| API actions | `loadState`, `performAction` | Fetches snapshots and sends commands to Flask. |
| App rendering | `renderProcesses`, `renderScheduler`, `renderMemory`, `renderDisk`, `renderFiles`, `renderPrinter` | Converts backend state into UI panels. |
| Form handling | Process, disk, file, printer, scheduler handlers | Reads user input and sends API requests. |

### Browser-Persisted UI Preferences

| Key | Purpose |
|---|---|
| `wallpaper` | Selected wallpaper preset. |
| `reduced_motion` | Reduced motion setting. |
| `desktop_icon_positions_v1` | Movable shortcut positions. |

## 15. Default Configuration

| Setting | Default |
|---|---|
| Active scheduling algorithm | Round Robin |
| Round Robin quantum | 2 |
| Queue quantums | `2, 4, 8` |
| Memory mode | Fixed partitions |
| Disk blocks | 64 |
| Disk block size | 32 characters |
| Disk cylinders | 0-199 |
| Open apps after entering desktop | System Monitor, CPU Scheduler |

## 16. Running the System

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Start the App

```bash
python app.py
```

### Open in Browser

```text
http://127.0.0.1:5000
```

Alternative Flask command:

```bash
python -m flask --app app run
```

## 17. Testing and Verification

The project currently has no dedicated automated test suite. Useful manual and syntax checks include:

| Check | Command |
|---|---|
| Python syntax | `python -m py_compile app.py` |
| JavaScript syntax | `node --check static/script.js` |
| Run app | `python app.py` |
| Smoke test home route | Open `http://127.0.0.1:5000` |

Recommended manual checks:

1. Enter desktop after boot.
2. Move a shortcut by holding and dragging.
3. Open, minimize, maximize, close, and drag app windows.
4. Add/edit/delete a process and confirm the schedule rebuilds.
5. Run one scheduler step and verify process state changes.
6. Run full schedule and verify terminated processes release memory.
7. Create/edit/delete a file and confirm disk block map updates.
8. Add/process print jobs and confirm FIFO behavior.
9. Change scheduler and memory settings.
10. Reset simulator and confirm sample state returns.

## 18. Known Assumptions and Limits

| Area | Assumption or Limit |
|---|---|
| Persistence | Backend state is in memory only. Restarting Flask resets simulator state. |
| Concurrency | A Python `Lock` protects simulator mutations, but this is still a simple educational single-process design. |
| File system | Simulated files are not written to the host disk. |
| Memory model | Fixed/variable partition behavior is simplified for teaching. |
| Scheduling | Uses integer time units and classroom versions of MLQ/MLFQ. |
| Disk model | Blocks and cylinders are visual approximations, not real hardware I/O. |
| Authentication | No login, users, or permissions are implemented. |
| Database | No database is used. |
| Browser support | Modern browsers with JavaScript, CSS grid/flex, pointer events, and localStorage are expected. |

## 19. Suggested Future Improvements

| Improvement | Benefit |
|---|---|
| Add automated tests | Protect scheduling, memory, and API behavior from regressions. |
| Export/import simulator state | Allow saving a demo setup between server restarts. |
| Add process blocking/I/O states | Demonstrate richer process lifecycle behavior. |
| Add visual comparisons between algorithms | Make scheduling performance easier to compare. |
| Add persistent storage option | Optional SQLite or JSON persistence for files/processes. |
| Add accessibility pass | Improve keyboard navigation and screen reader labels. |
| Add screenshots to docs | Make the documentation more presentation-ready. |

## 20. Glossary

| Term | Meaning |
|---|---|
| CPU burst | Amount of CPU time a process needs. |
| Gantt chart | Timeline visualization showing which process used the CPU at each time range. |
| Throughput | Number of completed processes per time unit. |
| Turnaround time | Total time from process arrival to completion. |
| Waiting time | Time spent ready/waiting while not running. |
| Internal fragmentation | Wasted memory inside an allocated fixed partition. |
| External fragmentation | Free memory split into pieces too small to satisfy a large request. |
| Spooling | Queueing I/O jobs before a slower device processes them. |
| FCFS | First Come First Served. |
| SJF | Shortest Job First. |
| SRTF | Shortest Remaining Time First. |
| RR | Round Robin. |
| MLQ | Multilevel Queue scheduling. |
| MLFQ | Multilevel Feedback Queue scheduling. |
