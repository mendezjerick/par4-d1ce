from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from threading import Lock
from typing import Deque, Dict, List, Optional, Tuple

from flask import Flask, jsonify, render_template, request


@dataclass
class Process:
    """A beginner-friendly process model used by the web simulator."""

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

    def to_dict(self) -> Dict[str, object]:
        """Serialize the process for the frontend dashboard."""

        return {
            "pid": self.pid,
            "name": self.name,
            "burst_time": self.burst_time,
            "remaining_time": self.remaining_time,
            "memory_requirement": self.memory_requirement,
            "state": self.state,
            "waiting_time": self.waiting_time,
            "turnaround_time": self.turnaround_time,
            "completion_time": self.completion_time,
            "partition_index": self.partition_index,
            "partition_label": (
                f"Partition {self.partition_index + 1}"
                if self.partition_index is not None
                else "Unassigned"
            ),
        }


class MemoryManager:
    """Fixed-partition memory manager used by the scheduler."""

    def __init__(self, partition_sizes: List[int]) -> None:
        self.partition_sizes = list(partition_sizes)
        self.partitions = [
            {"size": size, "process_pid": None}
            for size in partition_sizes
        ]

    def allocate(self, process: Process) -> bool:
        """Allocate the first partition that can fit the process."""

        if process.partition_index is not None:
            return True

        for index, partition in enumerate(self.partitions):
            if partition["process_pid"] is None and process.memory_requirement <= partition["size"]:
                partition["process_pid"] = process.pid
                process.partition_index = index
                return True
        return False

    def deallocate(self, pid: int, process_lookup: Dict[int, Process]) -> Optional[int]:
        """Free the partition currently assigned to the given process."""

        for index, partition in enumerate(self.partitions):
            if partition["process_pid"] == pid:
                partition["process_pid"] = None
                process = process_lookup.get(pid)
                if process:
                    process.partition_index = None
                return index
        return None

    def release_terminated(self, processes: List[Process], process_lookup: Dict[int, Process]) -> List[int]:
        """Safety pass that ensures terminated processes no longer occupy memory."""

        terminated_ids = {process.pid for process in processes if process.state == "Terminated"}
        released = []

        for index, partition in enumerate(self.partitions):
            pid = partition["process_pid"]
            if pid in terminated_ids:
                partition["process_pid"] = None
                released.append(index)
                process = process_lookup.get(pid)
                if process:
                    process.partition_index = None

        return released

    def snapshot(self, process_lookup: Dict[int, Process]) -> Dict[str, object]:
        """Return a frontend-friendly view of the memory map."""

        partition_cards = []

        for index, partition in enumerate(self.partitions):
            pid = partition["process_pid"]
            process = process_lookup.get(pid) if pid is not None else None
            used_memory = process.memory_requirement if process else 0
            free_space = partition["size"] - used_memory
            usage_percent = int((used_memory / partition["size"]) * 100) if process else 0

            partition_cards.append(
                {
                    "index": index,
                    "label": f"Partition {index + 1}",
                    "size": partition["size"],
                    "occupied": process is not None,
                    "used_memory": used_memory,
                    "free_space": free_space,
                    "usage_percent": usage_percent,
                    "process": (
                        {
                            "pid": process.pid,
                            "name": process.name,
                            "state": process.state,
                            "memory_requirement": process.memory_requirement,
                        }
                        if process
                        else None
                    ),
                }
            )

        total_memory = sum(partition["size"] for partition in self.partitions)
        used_memory_total = sum(
            card["used_memory"] for card in partition_cards
        )

        return {
            "partitions": partition_cards,
            "total_memory": total_memory,
            "used_memory": used_memory_total,
            "free_memory": total_memory - used_memory_total,
            "used_partitions": sum(1 for card in partition_cards if card["occupied"]),
            "total_partitions": len(partition_cards),
        }


class InMemoryFileSystem:
    """A simple dictionary-backed file system simulation."""

    def __init__(self, starting_files: Optional[Dict[str, str]] = None) -> None:
        self.files = dict(starting_files or {})

    def create_file(self, filename: str, content: str) -> Tuple[bool, str]:
        filename = filename.strip()
        if not filename:
            return False, "File name cannot be empty."
        if filename in self.files:
            return False, f"File '{filename}' already exists."

        self.files[filename] = content
        return True, f"Created simulated file '{filename}'."

    def delete_file(self, filename: str) -> Tuple[bool, str]:
        if filename not in self.files:
            return False, f"File '{filename}' was not found."

        del self.files[filename]
        return True, f"Deleted simulated file '{filename}'."

    def read_file(self, filename: str) -> Tuple[bool, str]:
        if filename not in self.files:
            return False, f"File '{filename}' was not found."
        return True, self.files[filename]

    def snapshot(self) -> Dict[str, object]:
        items = []
        for name, content in sorted(self.files.items()):
            items.append(
                {
                    "name": name,
                    "content": content,
                    "size": len(content),
                }
            )
        return {
            "items": items,
            "count": len(items),
        }


class PrinterSpooler:
    """FIFO queue used to demonstrate I/O spooling."""

    def __init__(self) -> None:
        self.queue: Deque[Dict[str, object]] = deque()
        self.completed_jobs: List[Dict[str, object]] = []
        self.next_job_id = 1

    def add_job(self, document_name: str, content: str, source: str = "User Console") -> str:
        name = document_name.strip() or f"print_job_{self.next_job_id}.txt"
        job = {
            "id": self.next_job_id,
            "name": name,
            "content": content,
            "size": len(content),
            "source": source.strip() or "User Console",
        }
        self.next_job_id += 1
        self.queue.append(job)
        return f"Added '{name}' to the printer queue."

    def process_next_job(self) -> str:
        if not self.queue:
            return "Printer queue is empty."

        job = self.queue.popleft()
        self.completed_jobs.append(job)
        return f"Printed '{job['name']}' from {job['source']}."

    def snapshot(self) -> Dict[str, object]:
        return {
            "queue": list(self.queue),
            "completed_jobs": self.completed_jobs[-6:],
            "pending_count": len(self.queue),
            "completed_count": len(self.completed_jobs),
        }


class WebOperatingSystemSimulator:
    """Shared simulation state for the Flask web application."""

    DEFAULT_QUANTUM = 2
    DEFAULT_PARTITIONS = [64, 64, 128, 64]

    def __init__(self) -> None:
        self.lock = Lock()
        self.reset_all()

    def _build_sample_processes(self) -> List[Process]:
        """Preloaded processes keep the demo deterministic and presentation-friendly."""

        return [
            Process(1, "Mix Compiler", 5, 64),
            Process(2, "Neon Renderer", 4, 128),
            Process(3, "Receipt Sync", 3, 64),
            Process(4, "Night Backup", 6, 64),
        ]

    def _build_sample_files(self) -> Dict[str, str]:
        return {
            "boot.log": "System boot sequence complete. Cyberpunk dashboard online.",
            "scheduler_notes.txt": "Round Robin time quantum = 2. Fixed partitions = 64, 64, 128 MB.",
            "memory_map.txt": "Processes can only run after they fit in a fixed memory partition.",
        }

    def _sanitize_quantum(self, value: Optional[object]) -> int:
        try:
            quantum = int(value)
        except (TypeError, ValueError):
            return self.DEFAULT_QUANTUM

        return max(1, quantum)

    def _reset_process_subsystem(self, time_quantum: Optional[object] = None) -> None:
        self.memory_manager = MemoryManager(self.DEFAULT_PARTITIONS)
        self.processes = self._build_sample_processes()
        self.process_lookup = {process.pid: process for process in self.processes}
        chosen_quantum = time_quantum if time_quantum is not None else self.time_quantum
        self.time_quantum = self._sanitize_quantum(chosen_quantum)
        self.current_time = 0
        self.ready_queue: Deque[int] = deque()
        self.execution_order: List[str] = []
        self.gantt_segments: List[Dict[str, object]] = []
        self._allocate_waiting_processes()
        self._clean_ready_queue()

    def reset_all(self, time_quantum: Optional[object] = None) -> None:
        """Reset every module to the default project state."""

        chosen_quantum = time_quantum if time_quantum is not None else self.DEFAULT_QUANTUM
        self.time_quantum = self._sanitize_quantum(chosen_quantum)
        self.activity_log: List[Dict[str, object]] = []
        self.file_system = InMemoryFileSystem(self._build_sample_files())
        self.printer_spooler = PrinterSpooler()
        self._reset_process_subsystem(self.time_quantum)
        self._log("Simulator reset. Sample processes, files, and memory partitions are ready.")

    def load_sample_processes(self, time_quantum: Optional[object] = None) -> None:
        """Reload only the process, CPU, and memory modules for a repeatable demo."""

        self.activity_log = []
        chosen_quantum = time_quantum if time_quantum is not None else self.time_quantum
        self.time_quantum = self._sanitize_quantum(chosen_quantum)
        self._reset_process_subsystem(self.time_quantum)
        self._log("Sample processes reloaded. Files and printer jobs were preserved.")

    def set_time_quantum(self, value: Optional[object]) -> int:
        self.time_quantum = self._sanitize_quantum(value)
        self._log(f"Time quantum set to {self.time_quantum}.")
        return self.time_quantum

    def _log(self, message: str) -> None:
        self.activity_log.append({"clock": self.current_time, "message": message})
        self.activity_log = self.activity_log[-12:]

    def _enqueue_ready_process(self, pid: int) -> None:
        process = self.process_lookup.get(pid)
        if not process:
            return
        if process.state != "Ready" or process.remaining_time <= 0:
            return
        if pid not in self.ready_queue:
            self.ready_queue.append(pid)

    def _clean_ready_queue(self) -> None:
        cleaned_queue: Deque[int] = deque()
        seen = set()

        for pid in self.ready_queue:
            process = self.process_lookup.get(pid)
            if not process:
                continue
            if process.state != "Ready" or process.remaining_time <= 0:
                continue
            if pid in seen:
                continue
            cleaned_queue.append(pid)
            seen.add(pid)

        self.ready_queue = cleaned_queue

    def _allocate_waiting_processes(self) -> List[Process]:
        """Move waiting processes to Ready when a fixed partition becomes available."""

        newly_ready = []

        for process in self.processes:
            if process.state == "Terminated" or process.remaining_time <= 0:
                continue

            if process.partition_index is not None:
                if process.state == "Waiting":
                    process.state = "Ready"
                    self._enqueue_ready_process(process.pid)
                continue

            if self.memory_manager.allocate(process):
                process.state = "Ready"
                self._enqueue_ready_process(process.pid)
                newly_ready.append(process)

        return newly_ready

    def allocate_memory(self) -> str:
        waiting_before = [
            process
            for process in self.processes
            if process.state == "Waiting" and process.remaining_time > 0
        ]
        newly_ready = self._allocate_waiting_processes()
        self._clean_ready_queue()

        if newly_ready:
            names = ", ".join(f"P{process.pid}" for process in newly_ready)
            message = f"Allocated memory for {names}."
        elif waiting_before:
            message = "No waiting process could be allocated with the current free partitions."
        else:
            message = "No processes are waiting for memory."

        self._log(message)
        return message

    def release_completed_processes(self) -> str:
        released = self.memory_manager.release_terminated(self.processes, self.process_lookup)
        if released:
            labels = ", ".join(f"Partition {index + 1}" for index in released)
            message = f"Released completed processes from {labels}."
        else:
            message = "Completed processes are already released automatically."

        self._clean_ready_queue()
        self._log(message)
        return message

    def all_terminated(self) -> bool:
        return all(process.state == "Terminated" for process in self.processes)

    def is_blocked(self) -> bool:
        self._clean_ready_queue()
        waiting_processes = [
            process
            for process in self.processes
            if process.state == "Waiting" and process.remaining_time > 0
        ]
        return bool(waiting_processes) and not self.ready_queue

    def run_next_step(self) -> str:
        """Run one Round Robin time slice for the next ready process."""

        if self.all_terminated():
            message = "All processes are already terminated."
            self._log(message)
            return message

        self._allocate_waiting_processes()
        self._clean_ready_queue()

        if not self.ready_queue:
            message = "No ready process can run because waiting processes still need a free memory partition."
            self._log(message)
            return message

        pid = self.ready_queue.popleft()
        process = self.process_lookup[pid]
        process.state = "Running"

        slice_duration = min(self.time_quantum, process.remaining_time)
        start_time = self.current_time

        # Waiting time grows while another process owns the CPU.
        for _ in range(slice_duration):
            process.remaining_time -= 1
            self.current_time += 1

            for other in self.processes:
                if other.pid != process.pid and other.state in ("Ready", "Waiting"):
                    other.waiting_time += 1

        end_time = self.current_time

        self.gantt_segments.append(
            {
                "pid": process.pid,
                "label": f"P{process.pid}",
                "process_name": process.name,
                "start": start_time,
                "end": end_time,
                "duration": slice_duration,
            }
        )
        self.execution_order.append(f"P{process.pid}")

        events = [
            (
                f"CPU dispatched P{process.pid} ({process.name}) "
                f"from t={start_time} to t={end_time}."
            )
        ]

        if process.remaining_time == 0:
            process.state = "Terminated"
            process.completion_time = self.current_time
            process.turnaround_time = process.completion_time

            released_partition = self.memory_manager.deallocate(process.pid, self.process_lookup)
            if released_partition is not None:
                events.append(f"Freed Partition {released_partition + 1}.")
            events.append(f"P{process.pid} terminated.")

            newly_ready = self._allocate_waiting_processes()
            if newly_ready:
                labels = ", ".join(f"P{item.pid}" for item in newly_ready)
                events.append(f"Waiting process(es) moved to Ready: {labels}.")
        else:
            process.state = "Ready"
            self._enqueue_ready_process(process.pid)
            events.append(
                f"P{process.pid} returned to Ready with {process.remaining_time} unit(s) remaining."
            )

        self._clean_ready_queue()
        message = " ".join(events)
        self._log(message)
        return message

    def run_full_schedule(self) -> str:
        """Run until all processes terminate or the system becomes blocked."""

        if self.all_terminated():
            message = "All processes are already terminated."
            self._log(message)
            return message

        slices = 0
        while not self.all_terminated():
            previous_time = self.current_time
            self.run_next_step()
            if self.current_time == previous_time:
                break
            slices += 1

        if self.all_terminated():
            message = f"Full scheduling run completed in {slices} time slice(s)."
        else:
            message = "Full scheduling run stopped because no ready process could continue."

        self._log(message)
        return message

    def snapshot(self) -> Dict[str, object]:
        self._clean_ready_queue()

        for process in self.processes:
            if process.completion_time is not None:
                process.turnaround_time = process.completion_time

        memory_view = self.memory_manager.snapshot(self.process_lookup)
        waiting_processes = [
            {
                "pid": process.pid,
                "name": process.name,
                "memory_requirement": process.memory_requirement,
            }
            for process in self.processes
            if process.state == "Waiting" and process.remaining_time > 0
        ]

        stats = {
            "total_processes": len(self.processes),
            "ready_count": sum(process.state == "Ready" for process in self.processes),
            "running_count": sum(process.state == "Running" for process in self.processes),
            "waiting_count": sum(process.state == "Waiting" for process in self.processes),
            "terminated_count": sum(process.state == "Terminated" for process in self.processes),
            "average_waiting_time": round(
                sum(process.waiting_time for process in self.processes) / len(self.processes),
                2,
            ),
            "average_turnaround_time": round(
                sum(process.turnaround_time for process in self.processes) / len(self.processes),
                2,
            ),
            "throughput": round(
                (
                    sum(process.state == "Terminated" for process in self.processes)
                    / self.current_time
                ),
                2,
            )
            if self.current_time
            else 0,
        }

        return {
            "clock": self.current_time,
            "time_quantum": self.time_quantum,
            "processes": [process.to_dict() for process in self.processes],
            "ready_queue": [
                {
                    "pid": pid,
                    "label": f"P{pid}",
                    "name": self.process_lookup[pid].name,
                }
                for pid in self.ready_queue
            ],
            "execution_order": self.execution_order,
            "gantt_segments": self.gantt_segments,
            "memory": {
                **memory_view,
                "waiting_processes": waiting_processes,
            },
            "files": self.file_system.snapshot(),
            "printer": self.printer_spooler.snapshot(),
            "stats": stats,
            "demo": {
                "all_terminated": self.all_terminated(),
                "blocked": self.is_blocked(),
                "can_step": not self.all_terminated() and not self.is_blocked(),
            },
            "activity_log": self.activity_log,
        }


app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False
simulator = WebOperatingSystemSimulator()


def build_response(message: str, *, ok: bool = True, status_code: int = 200, **extra: object):
    payload = {
        "ok": ok,
        "message": message,
        "state": simulator.snapshot(),
    }
    payload.update(extra)
    return jsonify(payload), status_code


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/state")
def get_state():
    with simulator.lock:
        return build_response("Loaded current simulator state.")


@app.post("/api/reset")
def reset_simulation():
    payload = request.get_json(silent=True) or {}
    with simulator.lock:
        simulator.reset_all(payload.get("time_quantum"))
        return build_response("Simulation reset to the default web demo state.")


@app.post("/api/load-sample")
def load_sample_processes():
    payload = request.get_json(silent=True) or {}
    with simulator.lock:
        simulator.load_sample_processes(payload.get("time_quantum"))
        return build_response("Sample processes reloaded for another scheduling demo.")


@app.post("/api/quantum")
def update_quantum():
    payload = request.get_json(silent=True) or {}
    with simulator.lock:
        quantum = simulator.set_time_quantum(payload.get("time_quantum"))
        return build_response(f"Time quantum updated to {quantum}.")


@app.get("/api/processes")
def get_processes():
    with simulator.lock:
        state = simulator.snapshot()
        return jsonify(
            {
                "ok": True,
                "message": "Loaded process management data.",
                "processes": state["processes"],
                "stats": state["stats"],
                "ready_queue": state["ready_queue"],
            }
        )


@app.post("/api/scheduler/step")
def run_scheduler_step():
    with simulator.lock:
        message = simulator.run_next_step()
        return build_response(message)


@app.post("/api/scheduler/run")
def run_scheduler_full():
    with simulator.lock:
        message = simulator.run_full_schedule()
        return build_response(message)


@app.get("/api/memory")
def get_memory():
    with simulator.lock:
        state = simulator.snapshot()
        return jsonify(
            {
                "ok": True,
                "message": "Loaded memory manager data.",
                "memory": state["memory"],
            }
        )


@app.post("/api/memory/allocate")
def allocate_memory():
    with simulator.lock:
        message = simulator.allocate_memory()
        return build_response(message)


@app.post("/api/memory/release")
def release_completed_processes():
    with simulator.lock:
        message = simulator.release_completed_processes()
        return build_response(message)


@app.get("/api/files")
def list_files():
    with simulator.lock:
        return jsonify(
            {
                "ok": True,
                "message": "Loaded in-memory file system data.",
                "files": simulator.file_system.snapshot(),
                "state": simulator.snapshot(),
            }
        )


@app.post("/api/files")
def create_file():
    payload = request.get_json(silent=True) or {}
    filename = payload.get("filename", "")
    content = payload.get("content", "")

    with simulator.lock:
        success, message = simulator.file_system.create_file(filename, content)
        status_code = 200 if success else 400
        return build_response(message, ok=success, status_code=status_code)


@app.get("/api/files/<path:filename>")
def read_file(filename: str):
    with simulator.lock:
        success, content = simulator.file_system.read_file(filename)
        if not success:
            return build_response(content, ok=False, status_code=404)

        return build_response(
            f"Displayed simulated file '{filename}'.",
            filename=filename,
            content=content,
        )


@app.delete("/api/files/<path:filename>")
def delete_file(filename: str):
    with simulator.lock:
        success, message = simulator.file_system.delete_file(filename)
        status_code = 200 if success else 404
        return build_response(message, ok=success, status_code=status_code)


@app.get("/api/printer")
def get_printer_queue():
    with simulator.lock:
        return jsonify(
            {
                "ok": True,
                "message": "Loaded printer spooler data.",
                "printer": simulator.printer_spooler.snapshot(),
                "state": simulator.snapshot(),
            }
        )


@app.post("/api/printer/jobs")
def add_print_job():
    payload = request.get_json(silent=True) or {}
    document_name = payload.get("document_name", "")
    content = payload.get("content", "")
    source = payload.get("source", "User Console")

    with simulator.lock:
        message = simulator.printer_spooler.add_job(document_name, content, source)
        simulator._log(message)
        return build_response(message)


@app.post("/api/printer/process")
def process_next_print_job():
    with simulator.lock:
        message = simulator.printer_spooler.process_next_job()
        simulator._log(message)
        return build_response(message)


if __name__ == "__main__":
    app.run(debug=True)
