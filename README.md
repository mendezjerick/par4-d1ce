# Simple Operating System Simulator

## Project Overview
This project is a Flask-based web application that simulates a small operating system inside the browser. The latest upgrade turns the interface into a literal desktop shell instead of a normal dashboard website.

When the app loads, the user enters a neon cyberpunk desktop inspired by VA-11 HALL-A. The shell includes:
- boot screen
- desktop wallpaper
- desktop icons
- taskbar
- launcher menu
- windowed applications
- live clock and system status area

Inside that desktop shell, the installed apps demonstrate classic Operating Systems concepts such as process management, CPU scheduling, memory allocation, disk scheduling, file management, and I/O spooling.

## Desktop Shell Features
- Full desktop operating system style interface in the browser
- Cyberpunk wallpaper presets with VA-11 HALL-A inspired color direction
- Desktop icons for installed apps
- Bottom taskbar with open app indicators
- Start-style launcher menu
- Window manager with focus, minimize, maximize, close, and layered z-index behavior
- Window dragging for desktop-style interaction
- Settings app for wallpaper and simulator defaults

## Supported Installed Apps
- System Monitor
- Process Manager
- CPU Scheduler
- Memory Manager
- Disk Manager
- File Explorer
- Printer Queue
- Mini Game
- Settings

## Process Management Features
- Add new processes
- Edit existing processes
- Delete processes
- Reset process runtime
- Generate sample processes
- Track PID, name, arrival time, burst time, remaining time, priority, memory requirement, state, waiting time, turnaround time, and completion time

## Supported CPU Scheduling Algorithms
- First Come First Served
- Shortest Job First (Non-Preemptive)
- Shortest Remaining Time First
- Priority Scheduling (Non-Preemptive)
- Priority Scheduling (Preemptive)
- Round Robin
- Multilevel Queue Scheduling
- Multilevel Feedback Queue Scheduling

The scheduler app shows:
- execution order
- waiting time
- turnaround time
- completion time
- average waiting time
- average turnaround time
- throughput
- web-based Gantt chart

## Memory Management Features
- Fixed partition simulation
- Optional variable partition mode
- Allocation and deallocation display
- Waiting processes when memory is unavailable
- Memory usage indicators
- Internal and external fragmentation indicators

## Supported Disk Scheduling Algorithms
- FCFS
- SSTF
- SCAN
- C-SCAN
- LOOK
- C-LOOK

The disk app shows:
- disk request list
- initial head position
- service order
- head path
- total head movement
- block-based storage map

## File System Features
- Create file
- Edit file
- Delete file
- View file contents
- List files
- Show file size
- Group files by folder
- Show timestamps

The file system is fully in memory. Files also affect the educational disk block map.

## Printer Queue / I-O Simulation
- Add print jobs
- View pending queue
- Process next queued job
- View completed jobs

This demonstrates simple FIFO spooling behavior.

## Built-In Mini App
The simulator includes a small default installed app:
- Guess the Number

Its purpose is to make the shell feel more like a complete mini operating system while keeping the project easy to explain.

## Installation
1. Open a terminal in the project folder.
2. Create and activate a virtual environment if desired.
3. Install dependencies:

```bash
pip install -r requirements.txt
```

## Run the Project
Start the Flask server:

```bash
python app.py
```

Then open:

```text
http://127.0.0.1:5000
```

## How To Use The Desktop Simulator
1. Start the server and open the browser app.
2. Wait for the boot screen to finish, then enter the desktop.
3. Open apps from desktop icons, the taskbar, or the launcher.
4. Add processes in Process Manager.
5. Choose a CPU scheduling algorithm in CPU Scheduler and run the simulation.
6. Inspect memory allocation in Memory Manager.
7. Run disk scheduling in Disk Manager.
8. Manage in-memory files in File Explorer.
9. Add and process jobs in Printer Queue.
10. Open Settings to change wallpaper and shell defaults.
11. Launch the Mini Game like a built-in OS app.

## Project Structure
```text
par4-d1ce/
|-- app.py
|-- os_simulator.py
|-- requirements.txt
|-- README.md
|-- report.md
|-- presentation_outline.md
|-- templates/
|   `-- index.html
`-- static/
    |-- style.css
    `-- script.js
```

## File Guide
- `app.py`: Flask backend, simulator classes, APIs, and in-memory system state
- `templates/index.html`: desktop shell layout, launcher, taskbar, and application windows
- `static/style.css`: cyberpunk desktop styling, wallpapers, taskbar, windows, and panels
- `static/script.js`: window manager, launcher behavior, wallpaper switching, taskbar logic, and frontend API calls
- `os_simulator.py`: original command-line version
- `report.md`: final project report
- `presentation_outline.md`: presentation plan

## Mapping Features To Operating Systems Concepts

### Process Management
- The Process Manager app lets the user create, edit, delete, and inspect processes.

### CPU Scheduling
- The CPU Scheduler app compares major scheduling algorithms and visualizes CPU time with a Gantt chart.

### Memory Management
- The Memory Manager app shows allocation decisions, waiting due to insufficient memory, and fragmentation.

### Disk Management
- The Disk Manager app demonstrates head movement algorithms and simple block allocation.

### File System
- The File Explorer app simulates file and folder operations using in-memory data only.

### I/O Spooling
- The Printer Queue app shows FIFO job handling.

### Desktop Shell
- The browser shell simulates the user-facing part of an operating system with windows, launcher, taskbar, settings, and wallpaper management.

## Simplified Assumptions
- Everything stays in memory while the Flask app is running.
- The desktop shell is a browser simulation, not a real operating system.
- Memory and disk behavior are educational approximations.
- Scheduling uses integer time units.
- MLQ and MLFQ are simplified classroom versions.
- The file explorer is not tied to the real host file system.

## Notes
- No database is required.
- No authentication is used.
- Restarting the Flask app resets the in-memory simulator state.
