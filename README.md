# Simple Operating System Simulator

## Overview
This project is a web-based version of the **Simple Operating System Simulator** final project.  
It converts the original terminal demo into a browser dashboard while preserving the same academic goals:

- process management
- Round Robin CPU scheduling
- fixed-partition memory management
- in-memory file system operations
- printer queue / I/O spooling

The new interface uses a **VA-11 HALL-A inspired cyberpunk control-console design** with neon panels, dark backgrounds, glowing accents, and a presentation-friendly layout.

## Features
- Browser-based single-page dashboard built with Flask, HTML, CSS, and JavaScript
- Preloaded sample processes for a repeatable classroom demo
- Round Robin scheduling with configurable time quantum
- Step-by-step scheduling and automatic demo mode
- Web Gantt chart for execution order and CPU timeline
- Fixed memory partitions with visual memory cards
- In-memory file creation, listing, display, and deletion
- Printer queue simulation with FIFO spooling
- Summary statistics for waiting time, turnaround time, and throughput

## Tech Stack
- **Frontend:** HTML, CSS, JavaScript
- **Backend:** Python, Flask
- **Storage:** In-memory Python data structures only

## Installation
1. Open a terminal in the project folder.
2. Create a virtual environment if you want an isolated setup:

```bash
python -m venv .venv
```

3. Activate the virtual environment:

```bash
.venv\Scripts\activate
```

4. Install dependencies:

```bash
pip install -r requirements.txt
```

## How to Run Locally
1. Start the Flask app:

```bash
python app.py
```

2. Open your browser and visit:

```text
http://127.0.0.1:5000
```

## Project Structure
```text
par4-d1ce/
├── app.py
├── os_simulator.py
├── requirements.txt
├── README.md
├── report.md
├── presentation_outline.md
├── templates/
│   └── index.html
└── static/
    ├── style.css
    └── script.js
```

## File Guide
- `app.py` - Flask backend, simulator state, and JSON API routes
- `templates/index.html` - single-page dashboard layout
- `static/style.css` - cyberpunk VA-11 HALL-A inspired interface styling
- `static/script.js` - frontend logic, rendering, fetch calls, and demo controls
- `os_simulator.py` - original terminal-based reference version
- `report.md` - final project written report
- `presentation_outline.md` - slide-by-slide presentation outline

## Course Requirement Mapping
### 1. Process Management
- Displays PID, name, burst time, remaining time, memory requirement, state, waiting time, and turnaround time
- Shows states: Ready, Running, Waiting, and Terminated

### 2. CPU Scheduling
- Implements **Round Robin**
- Default time quantum is **2**, but it can be changed in the dashboard
- Shows execution order, waiting time, turnaround time, average waiting time, and a web-based Gantt chart

### 3. Memory Management
- Uses fixed partitions: `64 MB`, `64 MB`, `128 MB`
- Allocates and deallocates memory visually
- Keeps processes in **Waiting** when no partition fits

### 4. File System Simulation
- Uses an in-memory dictionary only
- Supports create, delete, list, and display operations

### 5. I/O Spooling
- Simulates a printer queue
- Adds print jobs and processes them one at a time using FIFO order

## Why the Web Version Is Better for Presentation
- Easier to demonstrate live in class because everything is visible in one dashboard
- Better visuals for screenshots, report documentation, and slides
- Clearer module separation for explaining OS concepts
- Step-by-step controls make Round Robin behavior easier to follow than a terminal scroll

## Notes
- No database is used.
- No real disk access is required for the simulated file system.
- The simulator state resets in memory when the Flask server restarts.
