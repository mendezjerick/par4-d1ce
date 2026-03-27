"""
Simple Operating System Simulator

This terminal program demonstrates beginner-friendly Operating Systems concepts:
- Process management
- Round Robin CPU scheduling
- Fixed-partition memory management
- In-memory file system operations
- Printer spooling

The visual output uses ANSI escape codes to create a neon, cyberpunk dashboard.
"""

from __future__ import annotations

import argparse
import ctypes
import os
import re
import sys
import textwrap
import time
from collections import deque
from dataclasses import dataclass, field
from typing import Deque, Dict, List, Optional, Tuple


class Neon:
    """ANSI color helpers and reusable terminal panel formatting."""

    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    BLACK_BG = "\033[40m"
    WHITE = "\033[97m"
    PINK = "\033[95m"
    CYAN = "\033[96m"
    PURPLE = "\033[35m"
    YELLOW = "\033[93m"
    GREEN = "\033[92m"
    RED = "\033[91m"
    ANSI_PATTERN = re.compile(r"\x1b\[[0-9;]*m")
    WIDTH = 96

    @classmethod
    def enable_windows_ansi(cls) -> None:
        """Enable ANSI escape support on modern Windows terminals."""

        if os.name != "nt":
            return

        try:
            kernel32 = ctypes.windll.kernel32
            handle = kernel32.GetStdHandle(-11)
            mode = ctypes.c_ulong()
            if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
                kernel32.SetConsoleMode(handle, mode.value | 0x0004)
        except Exception:
            pass

    @classmethod
    def style(cls, text: str, *codes: str) -> str:
        """Wrap text in ANSI style codes."""

        return "".join(codes) + text + cls.RESET

    @classmethod
    def plain_length(cls, text: str) -> int:
        """Measure visible text length without ANSI escape codes."""

        return len(cls.ANSI_PATTERN.sub("", text))

    @classmethod
    def pad(cls, text: str, width: int) -> str:
        """Pad text while respecting hidden ANSI codes."""

        return text + (" " * max(0, width - cls.plain_length(text)))

    @classmethod
    def truncate(cls, text: str, width: int) -> str:
        """Trim long plain text values to fit a column."""

        if len(text) <= width:
            return text
        return text[: max(0, width - 1)] + "~"

    @classmethod
    def banner(cls, title: str, subtitle: str) -> str:
        """Return the main futuristic header shown on every screen."""

        width = cls.WIDTH
        top = cls.style("=" * width, cls.BLACK_BG, cls.PINK, cls.BOLD)
        middle = cls.style(title.center(width), cls.BLACK_BG, cls.CYAN, cls.BOLD)
        lower = cls.style(subtitle.center(width), cls.BLACK_BG, cls.PURPLE)
        bottom = cls.style("=" * width, cls.BLACK_BG, cls.PINK, cls.BOLD)
        return "\n".join([top, middle, lower, bottom])

    @classmethod
    def panel(cls, title: str, lines: List[str], frame_color: str = CYAN) -> str:
        """Create a boxed panel that matches the neon dashboard style."""

        width = cls.WIDTH
        inner_width = width - 4
        border = cls.style("+" + ("=" * (width - 2)) + "+", cls.BLACK_BG, frame_color, cls.BOLD)
        title_text = "[ {} ]".format(title)
        title_line = cls.style(
            "| " + title_text.center(inner_width) + " |",
            cls.BLACK_BG,
            cls.PINK,
            cls.BOLD,
        )

        body = []
        if not lines:
            lines = [""]

        for line in lines:
            wrapped_lines = cls.wrap_visible(line, inner_width)
            for wrapped in wrapped_lines:
                padded = cls.pad(wrapped, inner_width)
                body.append(
                    cls.style("| ", cls.BLACK_BG, frame_color)
                    + padded
                    + cls.style(" |", cls.BLACK_BG, frame_color)
                )

        return "\n".join([border, title_line, border] + body + [border])

    @classmethod
    def wrap_visible(cls, text: str, width: int) -> List[str]:
        """Wrap plain text lines so they fit inside a panel."""

        if cls.ANSI_PATTERN.search(text):
            return [text]
        if not text:
            return [""]
        return textwrap.wrap(text, width=width) or [""]


@dataclass
class Process:
    """A simulated process tracked by the scheduler."""

    pid: int
    name: str
    burst_time: int
    memory_requirement: int
    remaining_time: int = field(init=False)
    state: str = "Waiting"
    waiting_time: int = 0
    turnaround_time: int = 0
    completion_time: Optional[int] = None
    partition_index: Optional[int] = None

    def __post_init__(self) -> None:
        self.remaining_time = self.burst_time


class MemoryManager:
    """Manages fixed memory partitions and tracks which process uses each one."""

    def __init__(self, partition_sizes: List[int]) -> None:
        self.partitions = [
            {"size": size, "process": None}
            for size in partition_sizes
        ]

    def can_fit(self, process: Process) -> bool:
        """Return True if the process can fit in at least one partition."""

        return any(process.memory_requirement <= part["size"] for part in self.partitions)

    def allocate(self, process: Process) -> bool:
        """Use first-fit allocation to place a process into memory."""

        if process.partition_index is not None:
            return True

        for index, partition in enumerate(self.partitions):
            if partition["process"] is None and process.memory_requirement <= partition["size"]:
                partition["process"] = process
                process.partition_index = index
                return True
        return False

    def deallocate(self, pid: int) -> Optional[int]:
        """Free the partition owned by the given process ID."""

        for index, partition in enumerate(self.partitions):
            process = partition["process"]
            if process and process.pid == pid:
                process.partition_index = None
                partition["process"] = None
                return index
        return None

    def memory_map_lines(self) -> List[str]:
        """Build a visual memory map for display."""

        lines = []
        for index, partition in enumerate(self.partitions):
            process = partition["process"]
            if process:
                state_color = state_to_color(process.state)
                status = Neon.style(
                    "OCCUPIED by P{} ({})".format(process.pid, process.name),
                    state_color,
                    Neon.BOLD,
                )
                bar = Neon.style("[########################]", state_color)
            else:
                status = Neon.style("FREE", Neon.YELLOW, Neon.BOLD)
                bar = Neon.style("[........................]", Neon.YELLOW)

            lines.append(
                "Partition {0} | {1:>3} MB | {2}".format(index + 1, partition["size"], status)
            )
            lines.append("{}  Fits requests up to {} MB".format(bar, partition["size"]))
            if index != len(self.partitions) - 1:
                lines.append("-" * 72)
        return lines


class FileSystem:
    """A simple in-memory file system stored inside a Python dictionary."""

    def __init__(self, starting_files: Optional[Dict[str, str]] = None) -> None:
        self.files = dict(starting_files or {})

    def create_file(self, filename: str, content: str) -> Tuple[bool, str]:
        """Create a simulated file if the name is valid and unique."""

        filename = filename.strip()
        if not filename:
            return False, "File name cannot be empty."
        if filename in self.files:
            return False, "A file with that name already exists."

        self.files[filename] = content
        return True, "Created simulated file '{}'.".format(filename)

    def delete_file(self, filename: str) -> Tuple[bool, str]:
        """Delete a simulated file by name."""

        if filename not in self.files:
            return False, "File '{}' was not found.".format(filename)

        del self.files[filename]
        return True, "Deleted simulated file '{}'.".format(filename)

    def list_files(self) -> List[Tuple[str, int]]:
        """Return files sorted by name with their content size."""

        return [(name, len(content)) for name, content in sorted(self.files.items())]

    def display_file(self, filename: str) -> Tuple[bool, str]:
        """Return file contents without touching the real file system."""

        if filename not in self.files:
            return False, "File '{}' was not found.".format(filename)
        return True, self.files[filename]


class PrinterSpooler:
    """A simple printer queue used to simulate I/O spooling."""

    def __init__(self) -> None:
        self.queue: Deque[Dict[str, str]] = deque()
        self.completed_jobs: List[Dict[str, str]] = []

    def add_job(self, document_name: str, content: str) -> str:
        """Add a print job to the end of the queue."""

        job = {"name": document_name.strip() or "untitled_job.txt", "content": content}
        self.queue.append(job)
        return "Added '{}' to the printer queue.".format(job["name"])

    def process_next_job(self) -> str:
        """Print the next job in FIFO order."""

        if not self.queue:
            return "Printer queue is empty."

        job = self.queue.popleft()
        self.completed_jobs.append(job)
        return "Printed '{}' ({} characters).".format(job["name"], len(job["content"]))

    def queue_lines(self) -> List[str]:
        """Build queue output for the dashboard."""

        lines = []
        if not self.queue:
            lines.append(Neon.style("No pending print jobs.", Neon.DIM, Neon.YELLOW))
        else:
            for index, job in enumerate(self.queue, start=1):
                lines.append(
                    "{}. {} ({:>3} chars)".format(
                        index,
                        Neon.style(job["name"], Neon.CYAN, Neon.BOLD),
                        len(job["content"]),
                    )
                )

        lines.append("")
        lines.append(Neon.style("Completed Jobs", Neon.PINK, Neon.BOLD))
        if not self.completed_jobs:
            lines.append(Neon.style("No jobs have been printed yet.", Neon.DIM, Neon.YELLOW))
        else:
            for job in self.completed_jobs[-5:]:
                lines.append(
                    "- {} ({:>3} chars)".format(
                        Neon.style(job["name"], Neon.GREEN),
                        len(job["content"]),
                    )
                )
        return lines


class Scheduler:
    """Implements Round Robin scheduling with a time quantum of 2."""

    def __init__(self, processes: List[Process], memory_manager: MemoryManager, time_quantum: int = 2) -> None:
        self.processes = processes
        self.memory_manager = memory_manager
        self.time_quantum = time_quantum
        self.current_time = 0
        self.execution_order: List[str] = []
        self.gantt_segments: List[Dict[str, int]] = []

    def all_terminated(self) -> bool:
        """Return True when every process has finished."""

        return all(process.state == "Terminated" for process in self.processes)

    def allocate_waiting_processes(self) -> List[Process]:
        """Try to allocate memory to waiting processes and move them to Ready."""

        ready_processes = []
        for process in self.processes:
            if process.state == "Terminated":
                continue
            if process.partition_index is None and self.memory_manager.allocate(process):
                if process.remaining_time > 0:
                    process.state = "Ready"
                    ready_processes.append(process)
        return ready_processes

    def build_ready_queue(self) -> Deque[Process]:
        """Create a ready queue in process ID order."""

        return deque(process for process in self.processes if process.state == "Ready")

    def increment_waiting_times(self, running_pid: int) -> None:
        """Increase waiting time for processes that are not currently running."""

        for process in self.processes:
            if process.pid != running_pid and process.state in ("Ready", "Waiting"):
                process.waiting_time += 1

    def run(self, step_callback=None) -> str:
        """Run the Round Robin scheduler until all possible work is complete."""

        if self.all_terminated():
            return "All processes are already terminated."

        self.allocate_waiting_processes()
        ready_queue = self.build_ready_queue()
        last_message = "Scheduler completed successfully."

        while True:
            if self.all_terminated():
                break

            if not ready_queue:
                newly_ready = self.allocate_waiting_processes()
                if newly_ready:
                    ready_queue.extend(newly_ready)
                    continue

                blocked = [
                    process
                    for process in self.processes
                    if process.state == "Waiting" and process.remaining_time > 0
                ]
                if blocked:
                    last_message = "Scheduler stopped because waiting processes could not be allocated."
                break

            process = ready_queue.popleft()
            if process.state != "Ready":
                continue

            process.state = "Running"
            time_slice = min(self.time_quantum, process.remaining_time)
            start_time = self.current_time

            for _ in range(time_slice):
                process.remaining_time -= 1
                self.current_time += 1
                self.increment_waiting_times(process.pid)

            end_time = self.current_time
            self.gantt_segments.append({"pid": process.pid, "start": start_time, "end": end_time})
            self.execution_order.append("P{}".format(process.pid))

            events = [
                "CPU dispatched P{} ({}) from t={} to t={}.".format(
                    process.pid,
                    process.name,
                    start_time,
                    end_time,
                )
            ]

            if process.remaining_time == 0:
                process.state = "Terminated"
                process.completion_time = self.current_time
                process.turnaround_time = process.completion_time
                freed_partition = self.memory_manager.deallocate(process.pid)
                if freed_partition is not None:
                    events.append("Freed memory partition {}.".format(freed_partition + 1))
                events.append("P{} terminated.".format(process.pid))

                newly_ready = self.allocate_waiting_processes()
                if newly_ready:
                    ids = ", ".join("P{}".format(item.pid) for item in newly_ready)
                    events.append("Moved from Waiting to Ready after allocation: {}.".format(ids))
                    ready_queue.extend(newly_ready)
            else:
                process.state = "Ready"
                ready_queue.append(process)
                events.append(
                    "P{} returned to Ready with {} unit(s) remaining.".format(
                        process.pid,
                        process.remaining_time,
                    )
                )

                newly_ready = self.allocate_waiting_processes()
                if newly_ready:
                    ids = ", ".join("P{}".format(item.pid) for item in newly_ready)
                    events.append("Newly allocated process(es): {}.".format(ids))
                    ready_queue.extend(newly_ready)

            snapshot = {
                "time": self.current_time,
                "start_time": start_time,
                "end_time": end_time,
                "running_pid": process.pid,
                "events": events,
            }
            if step_callback:
                step_callback(snapshot)

        for process in self.processes:
            if process.completion_time is not None:
                process.turnaround_time = process.completion_time

        return last_message


class OperatingSystemSimulator:
    """Top-level application that coordinates all simulator subsystems."""

    def __init__(self) -> None:
        Neon.enable_windows_ansi()
        self.live_terminal = sys.stdout.isatty()
        self.reset_system()

    def reset_system(self) -> None:
        """Load fresh predefined processes and simulated resources."""

        self.memory_manager = MemoryManager([64, 64, 128])
        self.processes = [
            Process(1, "Mix Compiler", 5, 64),
            Process(2, "Neon Renderer", 4, 128),
            Process(3, "Receipt Sync", 3, 64),
            Process(4, "Night Backup", 6, 64),
        ]
        self.scheduler = Scheduler(self.processes, self.memory_manager, time_quantum=2)
        self.file_system = FileSystem(
            {
                "boot.log": "System boot sequence complete. Neon dashboard online.",
                "scheduler_notes.txt": "Round Robin quantum = 2. Fixed partitions = 64, 64, 128 MB.",
            }
        )
        self.printer_spooler = PrinterSpooler()
        self.scheduler.allocate_waiting_processes()

    def clear_screen(self) -> None:
        """Clear the terminal in interactive mode to keep the dashboard clean."""

        if self.live_terminal:
            os.system("cls" if os.name == "nt" else "clear")

    def pause(self, message: str = "Press Enter to continue...") -> None:
        """Pause between menu screens when the program is interactive."""

        if not sys.stdin.isatty():
            return
        try:
            input(Neon.style("\n" + message, Neon.YELLOW, Neon.BOLD))
        except EOFError:
            pass

    def prompt(self, message: str) -> str:
        """Read user input while keeping prompts styled."""

        try:
            return input(Neon.style(message, Neon.CYAN, Neon.BOLD))
        except EOFError:
            return ""

    def render_screen(self, title: str, subtitle: str, panels: List[str]) -> None:
        """Print a fully themed screen."""

        self.clear_screen()
        print(Neon.banner(title, subtitle))
        print()
        for panel in panels:
            print(panel)
            print()

    def build_status_panel(self) -> str:
        """Show high-level simulator status."""

        ready_count = sum(process.state == "Ready" for process in self.processes)
        waiting_count = sum(process.state == "Waiting" for process in self.processes)
        running_count = sum(process.state == "Running" for process in self.processes)
        terminated_count = sum(process.state == "Terminated" for process in self.processes)

        lines = [
            "Clock Time: {}".format(self.scheduler.current_time),
            "Time Quantum: {}".format(self.scheduler.time_quantum),
            "Ready: {} | Running: {} | Waiting: {} | Terminated: {}".format(
                ready_count,
                running_count,
                waiting_count,
                terminated_count,
            ),
            "Simulated Files: {} | Printer Queue: {}".format(
                len(self.file_system.files),
                len(self.printer_spooler.queue),
            ),
        ]
        return Neon.panel("SYSTEM STATUS", lines, Neon.PURPLE)

    def build_process_table_lines(self) -> List[str]:
        """Build the process table required by the assignment."""

        columns = [
            ("PID", 5),
            ("NAME", 17),
            ("BURST", 7),
            ("REMAIN", 8),
            ("MEM", 6),
            ("STATE", 12),
            ("WAIT", 6),
            ("TURN", 8),
            ("PART", 8),
        ]

        header = " ".join(Neon.pad(name, width) for name, width in columns)
        lines = [
            Neon.style(header, Neon.YELLOW, Neon.BOLD),
            "-" * Neon.plain_length(header),
        ]

        for process in self.processes:
            state_text = Neon.style(process.state, state_to_color(process.state), Neon.BOLD)
            partition_text = "#{}".format(process.partition_index + 1) if process.partition_index is not None else "-"

            row_values = [
                str(process.pid),
                Neon.truncate(process.name, 17),
                str(process.burst_time),
                str(process.remaining_time),
                "{}MB".format(process.memory_requirement),
                state_text,
                str(process.waiting_time),
                str(process.turnaround_time),
                partition_text,
            ]

            padded_row = []
            for value, (_, width) in zip(row_values, columns):
                padded_row.append(Neon.pad(value, width))
            lines.append(" ".join(padded_row))

        lines.append("")
        lines.append(
            "Legend: {}  {}  {}  {}".format(
                Neon.style("Ready", Neon.PURPLE, Neon.BOLD),
                Neon.style("Running", Neon.CYAN, Neon.BOLD),
                Neon.style("Waiting", Neon.YELLOW, Neon.BOLD),
                Neon.style("Terminated", Neon.RED, Neon.DIM),
            )
        )
        return lines

    def build_gantt_lines(self) -> List[str]:
        """Create a simple text-based Gantt chart."""

        if not self.scheduler.gantt_segments:
            return ["Scheduler has not been run yet."]

        timeline = []
        time_marks = ["0"]
        cursor = 0

        for segment in self.scheduler.gantt_segments:
            duration = segment["end"] - segment["start"]
            width = max(6, duration * 4)
            label = "P{}".format(segment["pid"])
            timeline.append("[{}]".format(label.center(width, "=")))
            cursor += width + 2
            end_label = str(segment["end"])
            spacing = max(1, cursor - len("".join(time_marks)) - len(end_label))
            time_marks.append((" " * spacing) + end_label)

        average_wait = sum(process.waiting_time for process in self.processes) / len(self.processes)
        average_turnaround = sum(process.turnaround_time for process in self.processes) / len(self.processes)

        return [
            "Timeline : {}".format("".join(timeline)),
            "Time     : {}".format("".join(time_marks)),
            "Order    : {}".format(" -> ".join(self.scheduler.execution_order)),
            "Avg Wait : {:.2f} time unit(s)".format(average_wait),
            "Avg Turn : {:.2f} time unit(s)".format(average_turnaround),
        ]

    def build_memory_waiting_lines(self) -> List[str]:
        """Show which processes are waiting because memory is not available."""

        waiting = [process for process in self.processes if process.state == "Waiting"]
        if not waiting:
            return [Neon.style("No processes are waiting for memory.", Neon.GREEN, Neon.BOLD)]

        lines = []
        for process in waiting:
            lines.append(
                "P{} ({}) needs {} MB and is waiting for a free partition.".format(
                    process.pid,
                    process.name,
                    process.memory_requirement,
                )
            )
        return lines

    def build_file_list_lines(self) -> List[str]:
        """Display the simulated file system contents."""

        files = self.file_system.list_files()
        if not files:
            return [Neon.style("No simulated files available.", Neon.DIM, Neon.YELLOW)]

        lines = [
            Neon.style(Neon.pad("NAME", 28) + " " + Neon.pad("SIZE", 8), Neon.YELLOW, Neon.BOLD),
            "-" * 38,
        ]
        for name, size in files:
            lines.append(
                "{} {} chars".format(
                    Neon.pad(Neon.style(name, Neon.CYAN, Neon.BOLD), 28),
                    str(size).rjust(5),
                )
            )
        return lines

    def show_process_table(self) -> None:
        """Screen: process table plus current scheduler summary."""

        panels = [
            self.build_status_panel(),
            Neon.panel("PROCESS MANAGER", self.build_process_table_lines(), Neon.CYAN),
            Neon.panel("EXECUTION SUMMARY", self.build_gantt_lines(), Neon.PINK),
        ]
        self.render_screen(
            "SIMPLE OPERATING SYSTEM SIMULATOR",
            "VA-11 HALL-A INSPIRED PROCESS DASHBOARD",
            panels,
        )
        self.pause()

    def show_memory_map(self) -> None:
        """Screen: memory partitions and waiting list."""

        panels = [
            self.build_status_panel(),
            Neon.panel("MEMORY MAP", self.memory_manager.memory_map_lines(), Neon.YELLOW),
            Neon.panel("WAITING QUEUE", self.build_memory_waiting_lines(), Neon.PURPLE),
        ]
        self.render_screen(
            "SIMPLE OPERATING SYSTEM SIMULATOR",
            "FIXED PARTITION MEMORY VIEW",
            panels,
        )
        self.pause()

    def show_file_system_screen(self, message: Optional[str] = None, file_display: Optional[Tuple[str, str]] = None) -> None:
        """Screen: file system list and optional file contents."""

        panels = [self.build_status_panel()]
        if message:
            panels.append(Neon.panel("FILESYSTEM STATUS", [message], Neon.PINK))
        panels.append(Neon.panel("IN-MEMORY FILE SYSTEM", self.build_file_list_lines(), Neon.CYAN))

        if file_display:
            filename, content = file_display
            wrapped_content = []
            for line in content.splitlines() or [""]:
                wrapped_content.extend(Neon.wrap_visible(line, Neon.WIDTH - 4))
            panels.append(Neon.panel("DISPLAY FILE :: {}".format(filename), wrapped_content, Neon.YELLOW))

        self.render_screen(
            "SIMPLE OPERATING SYSTEM SIMULATOR",
            "SIMULATED FILE SYSTEM CONSOLE",
            panels,
        )

    def show_printer_queue_screen(self, message: Optional[str] = None) -> None:
        """Screen: printer queue and completed print jobs."""

        panels = [self.build_status_panel()]
        if message:
            panels.append(Neon.panel("PRINTER STATUS", [message], Neon.PINK))
        panels.append(Neon.panel("PRINTER SPOOLER", self.printer_spooler.queue_lines(), Neon.CYAN))
        self.render_screen(
            "SIMPLE OPERATING SYSTEM SIMULATOR",
            "I/O SPOOLING TERMINAL",
            panels,
        )

    def run_scheduler(self, demo_mode: bool = False, delay: float = 0.7) -> None:
        """Run the scheduler and optionally show each time slice step-by-step."""

        if self.scheduler.all_terminated():
            panels = [
                self.build_status_panel(),
                Neon.panel("SCHEDULER NOTICE", ["All processes are already terminated."], Neon.PINK),
                Neon.panel("PROCESS MANAGER", self.build_process_table_lines(), Neon.CYAN),
                Neon.panel("GANTT CHART", self.build_gantt_lines(), Neon.YELLOW),
            ]
            self.render_screen(
                "SIMPLE OPERATING SYSTEM SIMULATOR",
                "ROUND ROBIN CPU SCHEDULER",
                panels,
            )
            if not demo_mode:
                self.pause()
            return

        def step_callback(snapshot: Dict[str, object]) -> None:
            if not demo_mode:
                return

            event_lines = [Neon.style(line, Neon.WHITE) for line in snapshot["events"]]
            summary_lines = [
                "Clock advanced to t={}".format(snapshot["time"]),
                "Latest slice: P{} from {} to {}".format(
                    snapshot["running_pid"],
                    snapshot["start_time"],
                    snapshot["end_time"],
                ),
            ]
            panels = [
                self.build_status_panel(),
                Neon.panel("SCHEDULER EVENTS", event_lines, Neon.PINK),
                Neon.panel("SLICE SUMMARY", summary_lines, Neon.CYAN),
                Neon.panel("PROCESS MANAGER", self.build_process_table_lines(), Neon.CYAN),
                Neon.panel("MEMORY MAP", self.memory_manager.memory_map_lines(), Neon.YELLOW),
            ]
            self.render_screen(
                "SIMPLE OPERATING SYSTEM SIMULATOR",
                "ROUND ROBIN CPU SCHEDULER",
                panels,
            )
            time.sleep(delay)

        message = self.scheduler.run(step_callback=step_callback)

        panels = [
            self.build_status_panel(),
            Neon.panel("SCHEDULER RESULT", [message], Neon.PINK),
            Neon.panel("PROCESS MANAGER", self.build_process_table_lines(), Neon.CYAN),
            Neon.panel("GANTT CHART", self.build_gantt_lines(), Neon.YELLOW),
            Neon.panel("MEMORY MAP", self.memory_manager.memory_map_lines(), Neon.PURPLE),
        ]
        self.render_screen(
            "SIMPLE OPERATING SYSTEM SIMULATOR",
            "ROUND ROBIN CPU SCHEDULER",
            panels,
        )

        if not demo_mode:
            self.pause()

    def file_system_menu(self) -> None:
        """Submenu for create, delete, list, and display operations."""

        message = None
        file_display = None

        while True:
            self.show_file_system_screen(message=message, file_display=file_display)
            print(Neon.panel(
                "FILE SYSTEM MENU",
                [
                    "1. List files",
                    "2. Create file",
                    "3. Display file",
                    "4. Delete file",
                    "0. Back to main menu",
                ],
                Neon.PURPLE,
            ))

            choice = self.prompt("\nSelect file system option > ").strip()
            message = None
            file_display = None

            if choice == "1":
                message = "Displayed current in-memory file list."
            elif choice == "2":
                filename = self.prompt("Enter file name > ").strip()
                content = self.prompt("Enter file content > ")
                success, message = self.file_system.create_file(filename, content)
                if not success:
                    message = Neon.style(message, Neon.RED, Neon.BOLD)
                else:
                    message = Neon.style(message, Neon.GREEN, Neon.BOLD)
            elif choice == "3":
                filename = self.prompt("Enter file name to display > ").strip()
                success, result = self.file_system.display_file(filename)
                if success:
                    message = Neon.style("Displayed '{}'.".format(filename), Neon.GREEN, Neon.BOLD)
                    file_display = (filename, result)
                else:
                    message = Neon.style(result, Neon.RED, Neon.BOLD)
            elif choice == "4":
                filename = self.prompt("Enter file name to delete > ").strip()
                success, message = self.file_system.delete_file(filename)
                if not success:
                    message = Neon.style(message, Neon.RED, Neon.BOLD)
                else:
                    message = Neon.style(message, Neon.GREEN, Neon.BOLD)
            elif choice == "0":
                return
            else:
                message = Neon.style("Invalid file system option.", Neon.RED, Neon.BOLD)

    def printer_menu(self) -> None:
        """Submenu for printer queue operations."""

        message = None

        while True:
            self.show_printer_queue_screen(message=message)
            print(Neon.panel(
                "PRINTER MENU",
                [
                    "1. View queue",
                    "2. Add print job",
                    "3. Process next print job",
                    "0. Back to main menu",
                ],
                Neon.PURPLE,
            ))

            choice = self.prompt("\nSelect printer option > ").strip()
            message = None

            if choice == "1":
                message = "Displayed current printer queue."
            elif choice == "2":
                job_name = self.prompt("Enter document name > ").strip()
                content = self.prompt("Enter document content > ")
                message = Neon.style(self.printer_spooler.add_job(job_name, content), Neon.GREEN, Neon.BOLD)
            elif choice == "3":
                result = self.printer_spooler.process_next_job()
                color = Neon.GREEN if "Printed" in result else Neon.YELLOW
                message = Neon.style(result, color, Neon.BOLD)
            elif choice == "0":
                return
            else:
                message = Neon.style("Invalid printer option.", Neon.RED, Neon.BOLD)

    def run_full_demo(self, delay: float = 0.8, pause_at_end: bool = True) -> None:
        """Show a step-by-step demonstration of all assignment features."""

        self.reset_system()
        self.render_screen(
            "SIMPLE OPERATING SYSTEM SIMULATOR",
            "DEMO MODE :: CYBERPUNK OPERATING SYSTEM WALKTHROUGH",
            [
                self.build_status_panel(),
                Neon.panel(
                    "DEMO BOOT SEQUENCE",
                    [
                        "Loading predefined processes, memory partitions, simulated files, and printer queue.",
                        "The dashboard will demonstrate process states, Round Robin scheduling, fixed partitions, file operations, and I/O spooling.",
                    ],
                    Neon.PINK,
                ),
            ],
        )
        time.sleep(delay)

        file_message = self.file_system.create_file(
            "shift_report.txt",
            "Night shift summary: scheduler online, neon terminal stable, memory map verified.",
        )[1]
        self.show_file_system_screen(message=Neon.style(file_message, Neon.GREEN, Neon.BOLD))
        time.sleep(delay)

        success, content = self.file_system.display_file("shift_report.txt")
        if success:
            self.show_file_system_screen(
                message=Neon.style("Displayed sample file for the demo.", Neon.GREEN, Neon.BOLD),
                file_display=("shift_report.txt", content),
            )
            time.sleep(delay)

        spool_message_1 = self.printer_spooler.add_job(
            "receipt_batch.txt",
            "Receipt batch 42 queued for printing.",
        )
        spool_message_2 = self.printer_spooler.add_job(
            "daily_summary.txt",
            "CPU log, memory map, and file system checks queued.",
        )
        self.show_printer_queue_screen(
            message=Neon.style("{} {}".format(spool_message_1, spool_message_2), Neon.GREEN, Neon.BOLD)
        )
        time.sleep(delay)

        printed_message = self.printer_spooler.process_next_job()
        self.show_printer_queue_screen(message=Neon.style(printed_message, Neon.GREEN, Neon.BOLD))
        time.sleep(delay)

        self.render_screen(
            "SIMPLE OPERATING SYSTEM SIMULATOR",
            "INITIAL PROCESS AND MEMORY STATE",
            [
                self.build_status_panel(),
                Neon.panel("PROCESS MANAGER", self.build_process_table_lines(), Neon.CYAN),
                Neon.panel("MEMORY MAP", self.memory_manager.memory_map_lines(), Neon.YELLOW),
                Neon.panel("WAITING QUEUE", self.build_memory_waiting_lines(), Neon.PURPLE),
            ],
        )
        time.sleep(delay)

        self.run_scheduler(demo_mode=True, delay=delay)
        time.sleep(delay)

        self.render_screen(
            "SIMPLE OPERATING SYSTEM SIMULATOR",
            "DEMO COMPLETE",
            [
                self.build_status_panel(),
                Neon.panel("FINAL PROCESS TABLE", self.build_process_table_lines(), Neon.CYAN),
                Neon.panel("FINAL GANTT CHART", self.build_gantt_lines(), Neon.YELLOW),
                Neon.panel("FINAL FILE SYSTEM", self.build_file_list_lines(), Neon.PURPLE),
                Neon.panel("FINAL PRINTER QUEUE", self.printer_spooler.queue_lines(), Neon.PINK),
            ],
        )

        if pause_at_end and sys.stdin.isatty():
            self.pause("Demo finished. Press Enter to return to the main menu...")

    def run_menu(self) -> None:
        """Main menu loop required by the assignment."""

        while True:
            panels = [
                self.build_status_panel(),
                Neon.panel(
                    "MAIN MENU",
                    [
                        "1. View process table",
                        "2. Run scheduler",
                        "3. View memory map",
                        "4. File system operations",
                        "5. Printer queue operations",
                        "6. Run full demo",
                        "7. Reset simulator data",
                        "0. Exit",
                    ],
                    Neon.CYAN,
                ),
            ]
            self.render_screen(
                "SIMPLE OPERATING SYSTEM SIMULATOR",
                "VA-11 HALL-A INSPIRED NEON TERMINAL DASHBOARD",
                panels,
            )

            choice = self.prompt("Select menu option > ").strip()

            if choice == "1":
                self.show_process_table()
            elif choice == "2":
                self.run_scheduler()
            elif choice == "3":
                self.show_memory_map()
            elif choice == "4":
                self.file_system_menu()
            elif choice == "5":
                self.printer_menu()
            elif choice == "6":
                self.run_full_demo()
            elif choice == "7":
                self.reset_system()
                self.render_screen(
                    "SIMPLE OPERATING SYSTEM SIMULATOR",
                    "SYSTEM RESET COMPLETE",
                    [
                        self.build_status_panel(),
                        Neon.panel(
                            "RESET STATUS",
                            ["Predefined processes, memory map, files, and queue were restored."],
                            Neon.GREEN,
                        ),
                    ],
                )
                self.pause()
            elif choice == "0":
                self.render_screen(
                    "SIMPLE OPERATING SYSTEM SIMULATOR",
                    "SESSION CLOSED",
                    [
                        Neon.panel(
                            "SHUTDOWN",
                            ["Neon terminal offline. Thank you for using the simulator."],
                            Neon.PINK,
                        )
                    ],
                )
                return
            else:
                self.render_screen(
                    "SIMPLE OPERATING SYSTEM SIMULATOR",
                    "INVALID MENU OPTION",
                    [
                        Neon.panel(
                            "ERROR",
                            ["Please choose a valid menu option from the dashboard."],
                            Neon.RED,
                        )
                    ],
                )
                self.pause()


def state_to_color(state: str) -> str:
    """Map process states to neon colors."""

    if state == "Running":
        return Neon.CYAN
    if state == "Waiting":
        return Neon.YELLOW
    if state == "Terminated":
        return Neon.RED
    if state == "Ready":
        return Neon.PURPLE
    return Neon.WHITE


def build_argument_parser() -> argparse.ArgumentParser:
    """Create command-line options for easier demos."""

    parser = argparse.ArgumentParser(description="Simple Operating System Simulator")
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run the full demo automatically and exit.",
    )
    parser.add_argument(
        "--demo-delay",
        type=float,
        default=0.6,
        help="Delay in seconds between demo screens.",
    )
    return parser


def main() -> None:
    """Program entry point."""

    parser = build_argument_parser()
    args = parser.parse_args()

    simulator = OperatingSystemSimulator()

    if args.demo:
        simulator.run_full_demo(delay=max(0.0, args.demo_delay), pause_at_end=False)
    else:
        simulator.run_menu()


if __name__ == "__main__":
    main()
