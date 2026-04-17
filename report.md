# Simple Operating System Simulator Report

## Project Description
The Simple Operating System Simulator is a web-based final project for an Operating Systems course. It is built with Flask, HTML, CSS, and JavaScript and is designed to demonstrate major OS concepts through an interactive browser experience.

The latest version upgrades the project from a web dashboard into a literal desktop operating system simulation. The browser now opens into a cyberpunk desktop shell with wallpapers, desktop icons, a taskbar, a launcher menu, and separate windowed applications.

The visual direction remains inspired by VA-11 HALL-A:
- dark moody background
- neon pink, cyan, purple, magenta, and blue accents
- glowing glass-like panels
- retro-futuristic desktop atmosphere

## Upgrade Summary
The upgraded version adds a full desktop shell on top of the existing simulator logic:
- boot screen before entering the desktop
- desktop wallpaper presets
- desktop icons for installed apps
- taskbar with open window indicators
- launcher / start menu
- multiple application windows with focus, minimize, maximize, close, and drag behavior
- settings app for wallpaper and scheduler defaults

This change makes the application feel like a small operating system running inside the browser instead of a typical single-page website.

## Desktop Shell Design
The shell is intentionally not a Windows clone. It uses a generic desktop interaction model while keeping the same cyberpunk aesthetic.

Main shell elements:
- full-screen desktop background
- desktop icon area
- taskbar
- clock and status tray
- launcher menu
- application window layer

This shell acts as the user-facing environment, while each installed app demonstrates an Operating Systems concept.

## Process Management
The Process Manager app supports full process CRUD operations.

Each process includes:
- PID
- process name
- arrival time
- burst time
- remaining time
- priority
- memory requirement
- state
- waiting time
- turnaround time
- completion time

Supported actions:
- add process
- edit process
- delete process
- reset runtime
- generate sample processes

This allows the process list to change dynamically during the demonstration instead of staying hardcoded.

## CPU Scheduling Algorithms
The CPU Scheduler app supports the following algorithms:
- FCFS
- SJF Non-Preemptive
- SRTF
- Priority Non-Preemptive
- Priority Preemptive
- Round Robin
- Multilevel Queue Scheduling
- Multilevel Feedback Queue Scheduling

Displayed scheduling results:
- execution order
- waiting time
- turnaround time
- completion time
- average waiting time
- average turnaround time
- throughput
- web-based Gantt chart
- ready queue view

This makes it easy to compare algorithm behavior inside a visual app window.

## Memory Management
The Memory Manager app keeps the project educational while making allocation more visible.

Implemented features:
- fixed partition simulation
- optional variable partition mode
- allocation and deallocation display
- waiting state when memory is unavailable
- memory usage indicators
- fragmentation indicators

This helps explain how memory availability affects process readiness and completion.

## Disk Management
The project now includes a dedicated Disk Manager app.

### Disk Scheduling
Supported algorithms:
- FCFS
- SSTF
- SCAN
- C-SCAN
- LOOK
- C-LOOK

Displayed results:
- request list
- service order
- head path
- total head movement

### Storage Simulation
The Disk Manager also includes a simplified block-based storage model:
- total block capacity
- used blocks
- free blocks
- file-to-block mapping
- storage block visualization

This remains educational and is not meant to behave like real low-level storage hardware.

## File System Simulation
The File Explorer app expands the in-memory file system and gives it a desktop-style presentation.

Supported operations:
- create file
- edit file
- delete file
- display file contents
- list files
- show file size
- group files by folder
- show timestamps

The explorer window includes:
- folder sidebar
- file list
- content viewer
- file form actions

All files remain in memory only.

## I/O Simulation
The Printer Queue app simulates a simple spooler.

Supported features:
- add print job
- view pending jobs
- process next job
- view completed jobs

This demonstrates FIFO queue behavior and basic spooling as an Operating Systems concept.

## Built-In Mini App
To make the desktop feel more like a complete operating system, the project includes one small built-in app:
- Guess the Number

The app is intentionally simple so it feels like a default installed program without distracting from the academic simulation.

## System Monitor And Settings
The System Monitor app provides a desktop-style overview of the simulator:
- shell clock
- active process
- memory usage
- storage usage
- activity feed
- summary metrics

The Settings app provides shell-level controls:
- wallpaper selection
- reduced motion toggle
- scheduler defaults
- system reset
- sample data loading

These apps help the simulator feel more like a literal operating system environment.

## Educational Value
This project demonstrates several major OS topics inside one coherent interface:
- process management
- CPU scheduling
- memory allocation
- disk scheduling
- storage usage
- file management
- I/O spooling
- desktop shell concepts

The browser-based desktop makes the project easier to present because the user can switch between apps just like a mini operating system.

## Sample Output / Screenshot Placeholders

### Screenshot Placeholder 1
> Boot screen before entering the cyberpunk desktop

### Screenshot Placeholder 2
> Desktop shell with wallpaper, icons, taskbar, and launcher

### Screenshot Placeholder 3
> Process Manager window with editable process list

### Screenshot Placeholder 4
> CPU Scheduler window showing selected algorithm and Gantt chart

### Screenshot Placeholder 5
> Memory Manager window showing partitions and waiting processes

### Screenshot Placeholder 6
> Disk Manager window showing head movement and block map

### Screenshot Placeholder 7
> File Explorer window with folders and file viewer

### Screenshot Placeholder 8
> Printer Queue window with pending and completed jobs

### Screenshot Placeholder 9
> Settings window with wallpaper presets

### Screenshot Placeholder 10
> Mini Game window opened as a built-in desktop app

## Simplified Assumptions
- The desktop shell is only a browser simulation.
- All simulator state is stored in memory while Flask is running.
- The file system is not connected to the real computer file system.
- Storage blocks are educational and simplified.
- Memory behavior is a teaching model, not a real operating system allocator.
- Scheduling uses integer time units.
- MLQ and MLFQ are simplified academic versions.

## Conclusion
The upgraded Simple Operating System Simulator successfully preserves the original cyberpunk theme while transforming the interface into a literal desktop operating system simulation in the browser.

The result is visually stronger, more immersive, and more impressive for a final project presentation, while still remaining compact, understandable, and centered on Operating Systems concepts.
