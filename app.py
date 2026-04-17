from __future__ import annotations

import math
import random
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from threading import Lock
from typing import Deque, Dict, List, Optional, Tuple

from flask import Flask, jsonify, render_template, request


def now_stamp() -> str:
    """Return a short timestamp for simulated files and activity."""

    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@dataclass
class Process:
    """Beginner-friendly process model used throughout the simulator."""

    pid: int
    name: str
    arrival_time: int
    burst_time: int
    priority: int
    memory_requirement: int
    remaining_time: int = field(init=False)
    state: str = "Waiting"
    waiting_time: int = 0
    turnaround_time: int = 0
    completion_time: Optional[int] = None
    partition_index: Optional[int] = None
    memory_slot: str = "Unassigned"
    queue_level: int = 0
    allocated: bool = False
    arrived: bool = False

    def __post_init__(self) -> None:
        self.remaining_time = self.burst_time

    def reset_runtime(self) -> None:
        """Reset scheduling and memory values while keeping the definition."""

        self.remaining_time = self.burst_time
        self.state = "Waiting"
        self.waiting_time = 0
        self.turnaround_time = 0
        self.completion_time = None
        self.partition_index = None
        self.memory_slot = "Unassigned"
        self.queue_level = 0
        self.allocated = False
        self.arrived = False

    def clone(self) -> "Process":
        """Create a fresh runtime copy for scheduling simulation."""

        return Process(
            pid=self.pid,
            name=self.name,
            arrival_time=self.arrival_time,
            burst_time=self.burst_time,
            priority=self.priority,
            memory_requirement=self.memory_requirement,
        )

    def to_dict(self) -> Dict[str, object]:
        """Serialize runtime data for the dashboard."""

        return {
            "pid": self.pid,
            "name": self.name,
            "arrival_time": self.arrival_time,
            "burst_time": self.burst_time,
            "remaining_time": self.remaining_time,
            "priority": self.priority,
            "memory_requirement": self.memory_requirement,
            "state": self.state,
            "waiting_time": self.waiting_time,
            "turnaround_time": self.turnaround_time,
            "completion_time": self.completion_time,
            "partition_index": self.partition_index,
            "partition_label": self.memory_slot,
            "queue_level": self.queue_level,
            "queue_label": f"Q{self.queue_level}",
        }


class ProcessManager:
    """Stores process definitions and exposes CRUD operations."""

    def __init__(self) -> None:
        self.processes: List[Process] = []
        self.load_sample_processes()

    def sample_processes(self) -> List[Process]:
        """Return a presentation-friendly default process set."""

        return [
            Process(1, "Mix Compiler", 0, 5, 2, 64),
            Process(2, "Neon Renderer", 1, 4, 1, 128),
            Process(3, "Receipt Sync", 2, 3, 4, 64),
            Process(4, "Night Backup", 3, 6, 5, 64),
            Process(5, "Sound Driver", 4, 2, 3, 32),
        ]

    def _normalize_text(self, value: object, default: str) -> str:
        text = str(value or "").strip()
        return text or default

    def _normalize_int(
        self,
        value: object,
        default: int,
        minimum: int = 0,
    ) -> int:
        try:
            parsed = int(value)
        except (TypeError, ValueError):
            parsed = default
        return max(minimum, parsed)

    def _next_pid(self) -> int:
        return max((process.pid for process in self.processes), default=0) + 1

    def list_processes(self) -> List[Process]:
        return sorted(self.processes, key=lambda process: process.pid)

    def load_sample_processes(self) -> None:
        self.processes = self.sample_processes()

    def generate_sample_processes(self, count: int = 5) -> str:
        """Generate additional random sample processes for experimentation."""

        count = max(3, min(8, int(count or 5)))
        rng = random.Random(1337 + count)
        names = [
            "Signal Mixer",
            "Queue Monitor",
            "Sprite Loader",
            "Archive Sync",
            "Proxy Agent",
            "Vision Cache",
            "Patch Installer",
            "Log Streamer",
        ]

        generated: List[Process] = []
        for index in range(count):
            generated.append(
                Process(
                    pid=index + 1,
                    name=names[index % len(names)],
                    arrival_time=rng.randint(0, 5),
                    burst_time=rng.randint(2, 8),
                    priority=rng.randint(1, 6),
                    memory_requirement=rng.choice([32, 48, 64, 96, 128]),
                )
            )

        self.processes = generated
        return f"Generated {count} sample processes."

    def reset_runtime(self) -> str:
        for process in self.processes:
            process.reset_runtime()
        return "Process runtime data reset."

    def add_process(self, payload: Dict[str, object]) -> Tuple[bool, str]:
        name = self._normalize_text(payload.get("name"), "New Process")
        process = Process(
            pid=self._next_pid(),
            name=name,
            arrival_time=self._normalize_int(payload.get("arrival_time"), 0, 0),
            burst_time=self._normalize_int(payload.get("burst_time"), 4, 1),
            priority=self._normalize_int(payload.get("priority"), 3, 1),
            memory_requirement=self._normalize_int(payload.get("memory_requirement"), 64, 1),
        )
        self.processes.append(process)
        self.processes.sort(key=lambda item: item.pid)
        return True, f"Added process P{process.pid} ({process.name})."

    def update_process(self, pid: int, payload: Dict[str, object]) -> Tuple[bool, str]:
        process = next((item for item in self.processes if item.pid == pid), None)
        if not process:
            return False, f"Process P{pid} was not found."

        process.name = self._normalize_text(payload.get("name"), process.name)
        process.arrival_time = self._normalize_int(
            payload.get("arrival_time"),
            process.arrival_time,
            0,
        )
        process.burst_time = self._normalize_int(payload.get("burst_time"), process.burst_time, 1)
        process.priority = self._normalize_int(payload.get("priority"), process.priority, 1)
        process.memory_requirement = self._normalize_int(
            payload.get("memory_requirement"),
            process.memory_requirement,
            1,
        )
        process.reset_runtime()
        return True, f"Updated process P{process.pid}."

    def delete_process(self, pid: int) -> Tuple[bool, str]:
        process = next((item for item in self.processes if item.pid == pid), None)
        if not process:
            return False, f"Process P{pid} was not found."

        self.processes = [item for item in self.processes if item.pid != pid]
        return True, f"Deleted process P{pid} ({process.name})."

    def snapshot(self) -> List[Dict[str, object]]:
        return [process.to_dict() for process in self.list_processes()]


class MemoryManager:
    """Supports fixed partitions and a simple variable partition mode."""

    def __init__(self, fixed_partitions: Optional[List[int]] = None) -> None:
        self.fixed_partitions = list(fixed_partitions or [64, 64, 128, 64])
        self.total_memory = sum(self.fixed_partitions)
        self.mode = "fixed"
        self.reset()

    def clone(self, mode: Optional[str] = None) -> "MemoryManager":
        cloned = MemoryManager(self.fixed_partitions)
        cloned.set_mode(mode or self.mode)
        return cloned

    def set_mode(self, mode: str) -> None:
        self.mode = mode if mode in {"fixed", "variable"} else "fixed"
        self.reset()

    def reset(self) -> None:
        self.partitions = [
            {"index": index, "size": size, "process_pid": None}
            for index, size in enumerate(self.fixed_partitions)
        ]
        self.segments = [{"start": 0, "size": self.total_memory, "process_pid": None}]

    def allocate(self, process: Process) -> bool:
        if process.allocated:
            return True
        if self.mode == "fixed":
            return self._allocate_fixed(process)
        return self._allocate_variable(process)

    def _allocate_fixed(self, process: Process) -> bool:
        for partition in self.partitions:
            if partition["process_pid"] is None and process.memory_requirement <= partition["size"]:
                partition["process_pid"] = process.pid
                process.partition_index = partition["index"]
                process.memory_slot = f"Partition {partition['index'] + 1}"
                process.allocated = True
                return True
        return False

    def _allocate_variable(self, process: Process) -> bool:
        for index, segment in enumerate(self.segments):
            if segment["process_pid"] is not None:
                continue
            if process.memory_requirement > segment["size"]:
                continue

            allocated = {
                "start": segment["start"],
                "size": process.memory_requirement,
                "process_pid": process.pid,
            }
            remainder = segment["size"] - process.memory_requirement
            replacement = [allocated]
            if remainder > 0:
                replacement.append(
                    {
                        "start": segment["start"] + process.memory_requirement,
                        "size": remainder,
                        "process_pid": None,
                    }
                )

            self.segments[index:index + 1] = replacement
            process.partition_index = None
            process.memory_slot = (
                f"Block {allocated['start']}-{allocated['start'] + allocated['size'] - 1}"
            )
            process.allocated = True
            return True
        return False

    def deallocate(self, pid: int, lookup: Dict[int, Process]) -> Optional[str]:
        if self.mode == "fixed":
            for partition in self.partitions:
                if partition["process_pid"] == pid:
                    partition["process_pid"] = None
                    process = lookup.get(pid)
                    if process:
                        process.partition_index = None
                        process.memory_slot = "Unassigned"
                        process.allocated = False
                    return f"Partition {partition['index'] + 1}"
            return None

        for segment in self.segments:
            if segment["process_pid"] == pid:
                segment["process_pid"] = None
                process = lookup.get(pid)
                if process:
                    process.partition_index = None
                    process.memory_slot = "Unassigned"
                    process.allocated = False
                self._merge_free_segments()
                return "Variable Segment"
        return None

    def _merge_free_segments(self) -> None:
        merged: List[Dict[str, Optional[int]]] = []
        for segment in self.segments:
            if not merged:
                merged.append(segment)
                continue
            previous = merged[-1]
            if previous["process_pid"] is None and segment["process_pid"] is None:
                previous["size"] += segment["size"]
            else:
                merged.append(segment)
        self.segments = merged

    def snapshot(self, lookup: Dict[int, Process]) -> Dict[str, object]:
        if self.mode == "fixed":
            return self._fixed_snapshot(lookup)
        return self._variable_snapshot(lookup)

    def _fixed_snapshot(self, lookup: Dict[int, Process]) -> Dict[str, object]:
        regions = []
        used_memory = 0
        internal_fragmentation = 0

        for partition in self.partitions:
            pid = partition["process_pid"]
            process = lookup.get(pid) if pid is not None else None
            used = process.memory_requirement if process else 0
            free = partition["size"] - used
            used_memory += used
            if process:
                internal_fragmentation += free

            regions.append(
                {
                    "label": f"Partition {partition['index'] + 1}",
                    "size": partition["size"],
                    "start": None,
                    "occupied": process is not None,
                    "used_memory": used,
                    "free_space": free,
                    "usage_percent": int((used / partition["size"]) * 100) if process else 0,
                    "process": process.to_dict() if process else None,
                    "type": "fixed",
                }
            )

        return {
            "mode": "fixed",
            "mode_label": "Fixed Partitions",
            "regions": regions,
            "total_memory": self.total_memory,
            "used_memory": used_memory,
            "free_memory": self.total_memory - used_memory,
            "used_regions": sum(1 for region in regions if region["occupied"]),
            "total_regions": len(regions),
            "fragmentation": {
                "internal": internal_fragmentation,
                "external": 0,
                "largest_free_block": max(
                    (region["size"] for region in regions if not region["occupied"]),
                    default=0,
                ),
            },
        }

    def _variable_snapshot(self, lookup: Dict[int, Process]) -> Dict[str, object]:
        regions = []
        used_memory = 0
        free_segments = []

        for index, segment in enumerate(self.segments):
            pid = segment["process_pid"]
            process = lookup.get(pid) if pid is not None else None
            used = segment["size"] if process else 0
            used_memory += used
            if not process:
                free_segments.append(segment["size"])

            regions.append(
                {
                    "label": f"Segment {index + 1}",
                    "size": segment["size"],
                    "start": segment["start"],
                    "occupied": process is not None,
                    "used_memory": used,
                    "free_space": 0 if process else segment["size"],
                    "usage_percent": 100 if process else 0,
                    "process": process.to_dict() if process else None,
                    "type": "variable",
                }
            )

        total_free = self.total_memory - used_memory
        largest_free = max(free_segments, default=0)

        return {
            "mode": "variable",
            "mode_label": "Variable Partitions",
            "regions": regions,
            "total_memory": self.total_memory,
            "used_memory": used_memory,
            "free_memory": total_free,
            "used_regions": sum(1 for region in regions if region["occupied"]),
            "total_regions": len(regions),
            "fragmentation": {
                "internal": 0,
                "external": total_free - largest_free,
                "largest_free_block": largest_free,
            },
        }


class InMemoryFileSystem:
    """In-memory file system with simple folders, timestamps, and editing."""

    def __init__(self) -> None:
        self.files: Dict[str, Dict[str, object]] = {}

    def reset(self) -> None:
        self.files = {}

    def normalize_folder(self, folder: object) -> str:
        cleaned = str(folder or "/").strip().replace("\\", "/")
        cleaned = cleaned.strip("/")
        return "/" if not cleaned else f"/{cleaned}"

    def build_path(self, folder: object, filename: object) -> str:
        name = str(filename or "").strip()
        folder_name = self.normalize_folder(folder)
        if folder_name == "/":
            return f"/{name}"
        return f"{folder_name}/{name}"

    def create_file(self, filename: str, content: str, folder: str = "/") -> Tuple[bool, str, Optional[str]]:
        filename = str(filename or "").strip()
        if not filename:
            return False, "File name cannot be empty.", None

        path = self.build_path(folder, filename)
        if path in self.files:
            return False, f"File '{path}' already exists.", None

        timestamp = now_stamp()
        self.files[path] = {
            "path": path,
            "name": filename,
            "folder": self.normalize_folder(folder),
            "content": content,
            "size": len(content),
            "created_at": timestamp,
            "updated_at": timestamp,
        }
        return True, f"Created file '{path}'.", path

    def edit_file(
        self,
        original_path: str,
        filename: str,
        content: str,
        folder: str,
    ) -> Tuple[bool, str, Optional[str]]:
        if original_path not in self.files:
            return False, f"File '{original_path}' was not found.", None

        filename = str(filename or "").strip()
        if not filename:
            return False, "File name cannot be empty.", None

        target_path = self.build_path(folder, filename)
        if target_path != original_path and target_path in self.files:
            return False, f"File '{target_path}' already exists.", None

        current = self.files.pop(original_path)
        updated = {
            **current,
            "path": target_path,
            "name": filename,
            "folder": self.normalize_folder(folder),
            "content": content,
            "size": len(content),
            "updated_at": now_stamp(),
        }
        self.files[target_path] = updated
        return True, f"Updated file '{target_path}'.", target_path

    def delete_file(self, path: str) -> Tuple[bool, str]:
        if path not in self.files:
            return False, f"File '{path}' was not found."
        del self.files[path]
        return True, f"Deleted file '{path}'."

    def read_file(self, path: str) -> Tuple[bool, Optional[Dict[str, object]], str]:
        item = self.files.get(path)
        if not item:
            return False, None, f"File '{path}' was not found."
        return True, item.copy(), f"Opened file '{path}'."

    def snapshot(self) -> Dict[str, object]:
        items = [self.files[path].copy() for path in sorted(self.files)]
        folders = sorted({item["folder"] for item in items}) or ["/"]
        return {
            "items": items,
            "count": len(items),
            "folders": folders,
        }


class PrinterSpooler:
    """FIFO queue used to simulate printer spooling."""

    def __init__(self) -> None:
        self.queue: Deque[Dict[str, object]] = deque()
        self.completed_jobs: List[Dict[str, object]] = []
        self.next_job_id = 1

    def reset(self) -> None:
        self.queue.clear()
        self.completed_jobs = []
        self.next_job_id = 1

    def add_job(self, document_name: str, content: str, source: str = "Control Center") -> str:
        name = str(document_name or "").strip() or f"print_job_{self.next_job_id}.txt"
        job = {
            "id": self.next_job_id,
            "name": name,
            "content": content,
            "size": len(content),
            "source": str(source or "Control Center"),
            "created_at": now_stamp(),
        }
        self.next_job_id += 1
        self.queue.append(job)
        return f"Added '{name}' to the printer queue."

    def process_next_job(self) -> str:
        if not self.queue:
            return "Printer queue is empty."
        job = self.queue.popleft()
        job["completed_at"] = now_stamp()
        self.completed_jobs.append(job)
        return f"Printed '{job['name']}' from {job['source']}."

    def snapshot(self) -> Dict[str, object]:
        return {
            "queue": list(self.queue),
            "completed_jobs": self.completed_jobs[-6:],
            "pending_count": len(self.queue),
            "completed_count": len(self.completed_jobs),
        }


class DiskManager:
    """Combines storage usage simulation with classic disk scheduling."""

    DISK_ALGORITHMS = {
        "fcfs": "FCFS",
        "sstf": "SSTF",
        "scan": "SCAN",
        "c_scan": "C-SCAN",
        "look": "LOOK",
        "c_look": "C-LOOK",
    }

    def __init__(self, total_blocks: int = 64, block_size: int = 32, cylinder_max: int = 199) -> None:
        self.total_blocks = total_blocks
        self.block_size = block_size
        self.cylinder_max = cylinder_max
        self.file_allocations: Dict[str, List[int]] = {}
        self.last_schedule = {
            "algorithm": "fcfs",
            "algorithm_label": "FCFS",
            "head_position": 50,
            "direction": "up",
            "requests": [82, 170, 43, 140, 24, 16, 190],
            "service_order": [82, 170, 43, 140, 24, 16, 190],
            "path": [50, 82, 170, 43, 140, 24, 16, 190],
            "total_head_movement": 642,
        }

    def reset_storage(self) -> None:
        self.file_allocations = {}

    def blocks_needed(self, file_size: int) -> int:
        return max(1, math.ceil(max(file_size, 1) / self.block_size))

    def used_blocks(self) -> int:
        return sum(len(blocks) for blocks in self.file_allocations.values())

    def can_store(self, path: str, file_size: int, previous_path: Optional[str] = None) -> bool:
        current_blocks = len(self.file_allocations.get(previous_path or path, []))
        needed = self.blocks_needed(file_size)
        free_blocks = self.total_blocks - self.used_blocks() + current_blocks
        return needed <= free_blocks

    def store_file(self, path: str, file_size: int, previous_path: Optional[str] = None) -> bool:
        previous_key = previous_path or path
        current_blocks = self.file_allocations.pop(previous_key, [])
        needed = self.blocks_needed(file_size)
        available = [index for index in range(self.total_blocks) if not self._is_block_used(index)]

        if needed > len(current_blocks) + len(available):
            if current_blocks:
                self.file_allocations[previous_key] = current_blocks
            return False

        allocation = list(current_blocks[:needed])
        shortage = needed - len(allocation)
        if shortage > 0:
            allocation.extend(available[:shortage])
        self.file_allocations[path] = sorted(allocation)
        return True

    def delete_file(self, path: str) -> None:
        self.file_allocations.pop(path, None)

    def _is_block_used(self, block_index: int) -> bool:
        return any(block_index in blocks for blocks in self.file_allocations.values())

    def storage_snapshot(self, file_items: List[Dict[str, object]]) -> Dict[str, object]:
        used = self.used_blocks()
        files = []
        for item in file_items:
            blocks = self.file_allocations.get(item["path"], [])
            files.append(
                {
                    "path": item["path"],
                    "name": item["name"],
                    "folder": item["folder"],
                    "size": item["size"],
                    "blocks": blocks,
                    "block_count": len(blocks),
                }
            )

        block_map = []
        for index in range(self.total_blocks):
            owner = next(
                (
                    path
                    for path, blocks in self.file_allocations.items()
                    if index in blocks
                ),
                None,
            )
            block_map.append(
                {
                    "index": index,
                    "occupied": owner is not None,
                    "owner": owner,
                }
            )

        return {
            "total_blocks": self.total_blocks,
            "block_size": self.block_size,
            "used_blocks": used,
            "free_blocks": self.total_blocks - used,
            "used_percent": round((used / self.total_blocks) * 100, 2) if self.total_blocks else 0,
            "files": files,
            "block_map": block_map,
        }

    def run_schedule(
        self,
        algorithm: str,
        requests: List[int],
        head_position: int,
        direction: str = "up",
    ) -> Dict[str, object]:
        requests = [max(0, min(self.cylinder_max, int(item))) for item in requests]
        head_position = max(0, min(self.cylinder_max, int(head_position)))
        direction = "down" if str(direction).lower() == "down" else "up"

        if algorithm == "sstf":
            service_order = self._sstf(requests, head_position)
            path = [head_position] + service_order
        elif algorithm == "scan":
            service_order, path = self._scan_family(requests, head_position, direction, circular=False, look=False)
        elif algorithm == "c_scan":
            service_order, path = self._scan_family(requests, head_position, direction, circular=True, look=False)
        elif algorithm == "look":
            service_order, path = self._scan_family(requests, head_position, direction, circular=False, look=True)
        elif algorithm == "c_look":
            service_order, path = self._scan_family(requests, head_position, direction, circular=True, look=True)
        else:
            algorithm = "fcfs"
            service_order = list(requests)
            path = [head_position] + service_order

        total_head_movement = sum(abs(path[index + 1] - path[index]) for index in range(len(path) - 1))
        self.last_schedule = {
            "algorithm": algorithm,
            "algorithm_label": self.DISK_ALGORITHMS.get(algorithm, algorithm.upper()),
            "head_position": head_position,
            "direction": direction,
            "requests": requests,
            "service_order": service_order,
            "path": path,
            "total_head_movement": total_head_movement,
        }
        return self.last_schedule

    def _sstf(self, requests: List[int], head_position: int) -> List[int]:
        pending = list(requests)
        order = []
        current = head_position
        while pending:
            next_request = min(pending, key=lambda item: (abs(item - current), item))
            order.append(next_request)
            pending.remove(next_request)
            current = next_request
        return order

    def _scan_family(
        self,
        requests: List[int],
        head_position: int,
        direction: str,
        circular: bool,
        look: bool,
    ) -> Tuple[List[int], List[int]]:
        higher = sorted(item for item in requests if item >= head_position)
        lower = sorted((item for item in requests if item < head_position), reverse=True)
        service_order: List[int]
        path = [head_position]

        if direction == "up":
            service_order = higher + list(reversed(lower))
            path.extend(higher)
            if circular:
                if not look:
                    if path[-1] != self.cylinder_max:
                        path.append(self.cylinder_max)
                    path.append(0)
                elif lower:
                    path.append(min(lower))
                path.extend(sorted(lower))
            else:
                if lower:
                    if not look and path[-1] != self.cylinder_max:
                        path.append(self.cylinder_max)
                    path.extend(lower)
        else:
            service_order = lower + list(reversed(higher))
            path.extend(lower)
            if circular:
                if not look:
                    if path[-1] != 0:
                        path.append(0)
                    path.append(self.cylinder_max)
                elif higher:
                    path.append(max(higher))
                path.extend(sorted(higher, reverse=True))
            else:
                if higher:
                    if not look and path[-1] != 0:
                        path.append(0)
                    path.extend(sorted(higher))

        clean_service = [item for item in service_order if item in requests]
        clean_path = [path[0]]
        for point in path[1:]:
            if point != clean_path[-1]:
                clean_path.append(point)
        return clean_service, clean_path

    def snapshot(self, file_items: List[Dict[str, object]]) -> Dict[str, object]:
        return {
            "storage": self.storage_snapshot(file_items),
            "schedule": self.last_schedule,
            "algorithms": self.DISK_ALGORITHMS,
            "cylinder_max": self.cylinder_max,
        }


class MiniGame:
    """Tiny built-in Guess the Number app for the desktop launcher."""

    def __init__(self) -> None:
        self.reset()

    def reset(self) -> str:
        self.target = random.randint(1, 20)
        self.attempts = 0
        self.status = "playing"
        self.history: List[Dict[str, object]] = []
        self.message = "New game started. Guess a number from 1 to 20."
        return self.message

    def guess(self, value: object) -> Tuple[bool, str]:
        if self.status == "won":
            return False, "Game already solved. Start a new round to play again."

        try:
            guess = int(value)
        except (TypeError, ValueError):
            return False, "Enter a valid whole number."

        if guess < 1 or guess > 20:
            return False, "Guesses must stay between 1 and 20."

        self.attempts += 1
        if guess == self.target:
            hint = "Correct"
            self.status = "won"
            self.message = f"Correct. You found the number in {self.attempts} attempt(s)."
        elif guess < self.target:
            hint = "Too Low"
            self.message = f"{guess} is too low."
        else:
            hint = "Too High"
            self.message = f"{guess} is too high."

        self.history.append(
            {
                "guess": guess,
                "hint": hint,
                "attempt": self.attempts,
            }
        )
        self.history = self.history[-8:]
        return True, self.message

    def snapshot(self) -> Dict[str, object]:
        return {
            "status": self.status,
            "attempts": self.attempts,
            "message": self.message,
            "history": self.history,
        }


class Scheduler:
    """Builds full scheduling timelines and step-by-step frames."""

    ALGORITHMS = {
        "fcfs": "First Come First Served",
        "sjf": "Shortest Job First (Non-Preemptive)",
        "srtf": "Shortest Remaining Time First",
        "priority_np": "Priority Scheduling (Non-Preemptive)",
        "priority_p": "Priority Scheduling (Preemptive)",
        "round_robin": "Round Robin",
        "mlq": "Multilevel Queue Scheduling",
        "mlfq": "Multilevel Feedback Queue Scheduling",
    }

    def algorithm_label(self, key: str) -> str:
        return self.ALGORITHMS.get(key, "Round Robin")

    def simulate(
        self,
        process_definitions: List[Process],
        memory_blueprint: MemoryManager,
        algorithm: str,
        time_quantum: int,
        queue_quantums: List[int],
    ) -> Dict[str, object]:
        processes = [process.clone() for process in process_definitions]
        lookup = {process.pid: process for process in processes}
        memory_manager = memory_blueprint.clone()
        queue_quantums = (queue_quantums + [4, 8, 12])[:3]

        frames: List[Dict[str, object]] = []
        execution_order: List[str] = []
        gantt_segments: List[Dict[str, object]] = []
        current_time = 0
        blocked = False
        current_pid: Optional[int] = None
        current_level = 0
        slice_used = 0
        rr_queue: Deque[int] = deque()
        mlq_queues = [deque(), deque(), deque()]
        mlfq_queues = [deque(), deque(), deque()]
        max_ticks = max(80, sum(process.burst_time for process in processes) * 12)

        self._refresh_process_states(processes, current_pid)
        self._handle_arrivals_and_memory(
            processes,
            memory_manager,
            current_time,
            algorithm,
            rr_queue,
            mlq_queues,
            mlfq_queues,
        )
        frames.append(
            self._capture_frame(
                processes=processes,
                lookup=lookup,
                memory_manager=memory_manager,
                clock=current_time,
                execution_order=execution_order,
                gantt_segments=gantt_segments,
                algorithm=algorithm,
                current_pid=current_pid,
                rr_queue=rr_queue,
                mlq_queues=mlq_queues,
                mlfq_queues=mlfq_queues,
                last_event="Simulation ready. Configure an algorithm and step through the timeline.",
                blocked=False,
            )
        )

        if not processes:
            return {"frames": frames, "blocked": False}

        while not self._all_terminated(processes) and current_time < max_ticks:
            events: List[str] = []
            previous_running_pid = current_pid

            if algorithm == "mlfq" and current_time > 0 and current_time % 10 == 0:
                boosted = self._boost_feedback_queues(processes, mlfq_queues, current_pid)
                if boosted:
                    events.append("MLFQ priority boost moved waiting jobs back to Q0.")
                if current_pid is not None:
                    current_level = lookup[current_pid].queue_level
                    slice_used = 0

            arrivals = self._handle_arrivals_and_memory(
                processes,
                memory_manager,
                current_time,
                algorithm,
                rr_queue,
                mlq_queues,
                mlfq_queues,
            )
            events.extend(arrivals)
            self._refresh_process_states(processes, current_pid)

            selected_pid: Optional[int] = None

            if algorithm == "fcfs":
                if current_pid and lookup[current_pid].remaining_time > 0:
                    selected_pid = current_pid
                else:
                    ready = self._ready_pool(processes)
                    ready.sort(key=lambda item: (item.arrival_time, item.pid))
                    selected_pid = ready[0].pid if ready else None
            elif algorithm == "sjf":
                if current_pid and lookup[current_pid].remaining_time > 0:
                    selected_pid = current_pid
                else:
                    ready = self._ready_pool(processes)
                    ready.sort(key=lambda item: (item.burst_time, item.arrival_time, item.pid))
                    selected_pid = ready[0].pid if ready else None
            elif algorithm == "srtf":
                ready = self._ready_pool(processes)
                ready.sort(key=lambda item: (item.remaining_time, item.arrival_time, item.pid))
                selected_pid = ready[0].pid if ready else None
                if current_pid and selected_pid and current_pid != selected_pid:
                    events.append(
                        f"Preempted P{current_pid} because P{selected_pid} has a shorter remaining time."
                    )
            elif algorithm == "priority_np":
                if current_pid and lookup[current_pid].remaining_time > 0:
                    selected_pid = current_pid
                else:
                    ready = self._ready_pool(processes)
                    ready.sort(key=lambda item: (item.priority, item.arrival_time, item.pid))
                    selected_pid = ready[0].pid if ready else None
            elif algorithm == "priority_p":
                ready = self._ready_pool(processes)
                ready.sort(key=lambda item: (item.priority, item.arrival_time, item.pid))
                selected_pid = ready[0].pid if ready else None
                if current_pid and selected_pid and current_pid != selected_pid:
                    events.append(
                        f"Preempted P{current_pid} because P{selected_pid} has a higher priority."
                    )
            elif algorithm == "mlq":
                if (
                    current_pid
                    and lookup[current_pid].remaining_time > 0
                    and self._higher_priority_queue_exists(mlq_queues, current_level)
                ):
                    self._enqueue_unique(mlq_queues[current_level], current_pid)
                    lookup[current_pid].state = "Ready"
                    events.append(f"P{current_pid} was preempted by a higher queue in MLQ.")
                    current_pid = None
                    slice_used = 0

                if current_pid and lookup[current_pid].remaining_time > 0:
                    selected_pid = current_pid
                else:
                    selected_pid, current_level = self._select_from_level_queues(mlq_queues)
                    slice_used = 0
            elif algorithm == "mlfq":
                if (
                    current_pid
                    and lookup[current_pid].remaining_time > 0
                    and self._higher_priority_queue_exists(mlfq_queues, current_level)
                ):
                    self._enqueue_unique(mlfq_queues[current_level], current_pid)
                    lookup[current_pid].state = "Ready"
                    events.append(f"P{current_pid} was preempted by a higher feedback queue.")
                    current_pid = None
                    slice_used = 0

                if current_pid and lookup[current_pid].remaining_time > 0:
                    selected_pid = current_pid
                else:
                    selected_pid, current_level = self._select_from_level_queues(mlfq_queues)
                    slice_used = 0
            else:
                if current_pid and lookup[current_pid].remaining_time > 0 and slice_used < time_quantum:
                    selected_pid = current_pid
                else:
                    if current_pid and lookup[current_pid].remaining_time > 0 and slice_used >= time_quantum:
                        self._enqueue_unique(rr_queue, current_pid)
                        lookup[current_pid].state = "Ready"
                        events.append(f"Time quantum expired for P{current_pid}; returned to the ready queue.")
                    current_pid = None
                    slice_used = 0
                    selected_pid = rr_queue.popleft() if rr_queue else None

            if selected_pid is None:
                if self._can_advance_time(processes):
                    self._increment_waiting(processes, None)
                    self._append_segment(gantt_segments, None, "CPU Idle", current_time, current_time + 1)
                    current_time += 1
                    frames.append(
                        self._capture_frame(
                            processes=processes,
                            lookup=lookup,
                            memory_manager=memory_manager,
                            clock=current_time,
                            execution_order=execution_order,
                            gantt_segments=gantt_segments,
                            algorithm=algorithm,
                            current_pid=None,
                            rr_queue=rr_queue,
                            mlq_queues=mlq_queues,
                            mlfq_queues=mlfq_queues,
                            last_event=" ".join(events) or "CPU idle while waiting for the next arrival.",
                            blocked=False,
                        )
                    )
                    continue

                blocked = True
                frames.append(
                    self._capture_frame(
                        processes=processes,
                        lookup=lookup,
                        memory_manager=memory_manager,
                        clock=current_time,
                        execution_order=execution_order,
                        gantt_segments=gantt_segments,
                        algorithm=algorithm,
                        current_pid=None,
                        rr_queue=rr_queue,
                        mlq_queues=mlq_queues,
                        mlfq_queues=mlfq_queues,
                        last_event="Simulation blocked because at least one process cannot be allocated or resumed.",
                        blocked=True,
                    )
                )
                break

            current_pid = selected_pid
            current_process = lookup[current_pid]
            if previous_running_pid and previous_running_pid != current_pid and previous_running_pid in lookup:
                previous = lookup[previous_running_pid]
                if previous.remaining_time > 0 and previous.arrived and previous.allocated:
                    previous.state = "Ready"

            if not execution_order or execution_order[-1] != f"P{current_pid}":
                execution_order.append(f"P{current_pid}")
            events.append(f"CPU dispatched P{current_pid} ({current_process.name}).")

            current_process.state = "Running"
            current_process.remaining_time -= 1
            self._append_segment(
                gantt_segments,
                current_process.pid,
                current_process.name,
                current_time,
                current_time + 1,
            )
            self._increment_waiting(processes, current_pid)
            current_time += 1
            slice_used += 1

            if current_process.remaining_time == 0:
                current_process.state = "Terminated"
                current_process.completion_time = current_time
                current_process.turnaround_time = current_time - current_process.arrival_time
                released_label = memory_manager.deallocate(current_pid, lookup)
                if released_label:
                    events.append(f"Released {released_label} after P{current_pid} completed.")
                events.append(f"P{current_pid} terminated.")
                current_pid = None
                slice_used = 0
                current_level = 0
            else:
                if algorithm == "round_robin":
                    if slice_used >= time_quantum:
                        self._enqueue_unique(rr_queue, current_pid)
                        current_process.state = "Ready"
                        events.append(f"P{current_pid} used its Round Robin quantum and returned to Ready.")
                        current_pid = None
                        slice_used = 0
                elif algorithm == "mlq":
                    level_quantum = queue_quantums[current_level]
                    if current_level < 2 and slice_used >= level_quantum:
                        self._enqueue_unique(mlq_queues[current_level], current_pid)
                        current_process.state = "Ready"
                        events.append(
                            f"P{current_pid} used queue Q{current_level} quantum and re-entered that queue."
                        )
                        current_pid = None
                        slice_used = 0
                elif algorithm == "mlfq":
                    level_quantum = queue_quantums[current_level]
                    if current_level < 2 and slice_used >= level_quantum:
                        new_level = min(2, current_level + 1)
                        current_process.queue_level = new_level
                        self._enqueue_unique(mlfq_queues[new_level], current_pid)
                        current_process.state = "Ready"
                        events.append(
                            f"P{current_pid} used its MLFQ quantum and was demoted to Q{new_level}."
                        )
                        current_pid = None
                        current_level = new_level
                        slice_used = 0
                elif algorithm in {"srtf", "priority_p"}:
                    current_process.state = "Ready"

            frames.append(
                self._capture_frame(
                    processes=processes,
                    lookup=lookup,
                    memory_manager=memory_manager,
                    clock=current_time,
                    execution_order=execution_order,
                    gantt_segments=gantt_segments,
                    algorithm=algorithm,
                    current_pid=current_pid,
                    rr_queue=rr_queue,
                    mlq_queues=mlq_queues,
                    mlfq_queues=mlfq_queues,
                    last_event=" ".join(events),
                    blocked=False,
                )
            )

        if current_time >= max_ticks and not self._all_terminated(processes):
            blocked = True
            frames.append(
                self._capture_frame(
                    processes=processes,
                    lookup=lookup,
                    memory_manager=memory_manager,
                    clock=current_time,
                    execution_order=execution_order,
                    gantt_segments=gantt_segments,
                    algorithm=algorithm,
                    current_pid=current_pid,
                    rr_queue=rr_queue,
                    mlq_queues=mlq_queues,
                    mlfq_queues=mlfq_queues,
                    last_event="Safety stop reached. The schedule did not finish within the tick limit.",
                    blocked=True,
                )
            )

        return {"frames": frames, "blocked": blocked}

    def _all_terminated(self, processes: List[Process]) -> bool:
        return all(process.remaining_time == 0 for process in processes)

    def _ready_pool(self, processes: List[Process]) -> List[Process]:
        return [
            process
            for process in processes
            if process.arrived and process.allocated and process.remaining_time > 0
        ]

    def _refresh_process_states(self, processes: List[Process], current_pid: Optional[int]) -> None:
        for process in processes:
            if process.remaining_time == 0:
                process.state = "Terminated"
            elif not process.arrived:
                process.state = "Waiting"
            elif not process.allocated:
                process.state = "Waiting"
            elif process.pid == current_pid:
                process.state = "Running"
            else:
                process.state = "Ready"

    def _handle_arrivals_and_memory(
        self,
        processes: List[Process],
        memory_manager: MemoryManager,
        current_time: int,
        algorithm: str,
        rr_queue: Deque[int],
        mlq_queues: List[Deque[int]],
        mlfq_queues: List[Deque[int]],
    ) -> List[str]:
        events: List[str] = []
        for process in sorted(processes, key=lambda item: (item.arrival_time, item.pid)):
            if not process.arrived and process.arrival_time <= current_time:
                process.arrived = True
                events.append(f"P{process.pid} arrived at t={current_time}.")

            if not process.arrived or process.remaining_time == 0 or process.allocated:
                continue

            if memory_manager.allocate(process):
                process.state = "Ready"
                if algorithm == "round_robin":
                    self._enqueue_unique(rr_queue, process.pid)
                elif algorithm == "mlq":
                    process.queue_level = self._mlq_level(process.priority)
                    self._enqueue_unique(mlq_queues[process.queue_level], process.pid)
                elif algorithm == "mlfq":
                    process.queue_level = 0
                    self._enqueue_unique(mlfq_queues[0], process.pid)
                events.append(f"Allocated memory to P{process.pid} in {process.memory_slot}.")
            else:
                process.state = "Waiting"
        return events

    def _increment_waiting(self, processes: List[Process], running_pid: Optional[int]) -> None:
        for process in processes:
            if not process.arrived or process.remaining_time == 0:
                continue
            if process.pid != running_pid:
                process.waiting_time += 1

    def _append_segment(
        self,
        gantt_segments: List[Dict[str, object]],
        pid: Optional[int],
        name: str,
        start: int,
        end: int,
    ) -> None:
        label = f"P{pid}" if pid is not None else "IDLE"
        css_class = f"pid-{pid}" if pid is not None else "pid-idle"
        if gantt_segments and gantt_segments[-1]["label"] == label:
            gantt_segments[-1]["end"] = end
            gantt_segments[-1]["duration"] = gantt_segments[-1]["end"] - gantt_segments[-1]["start"]
            return

        gantt_segments.append(
            {
                "pid": pid,
                "label": label,
                "process_name": name,
                "start": start,
                "end": end,
                "duration": end - start,
                "css_class": css_class,
            }
        )

    def _enqueue_unique(self, queue: Deque[int], pid: int) -> None:
        if pid not in queue:
            queue.append(pid)

    def _select_from_level_queues(self, queues: List[Deque[int]]) -> Tuple[Optional[int], int]:
        for index, queue in enumerate(queues):
            if queue:
                return queue.popleft(), index
        return None, 0

    def _higher_priority_queue_exists(self, queues: List[Deque[int]], current_level: int) -> bool:
        return any(queue for queue in queues[:current_level])

    def _boost_feedback_queues(
        self,
        processes: List[Process],
        queues: List[Deque[int]],
        current_pid: Optional[int],
    ) -> bool:
        boosted = False
        for queue in queues:
            queue.clear()
        for process in processes:
            if process.remaining_time == 0 or not process.arrived or not process.allocated:
                continue
            process.queue_level = 0
            if process.pid != current_pid:
                self._enqueue_unique(queues[0], process.pid)
            boosted = True
        return boosted

    def _mlq_level(self, priority: int) -> int:
        if priority <= 2:
            return 0
        if priority <= 4:
            return 1
        return 2

    def _can_advance_time(self, processes: List[Process]) -> bool:
        future_arrivals = any(not process.arrived and process.remaining_time > 0 for process in processes)
        return future_arrivals

    def _capture_frame(
        self,
        *,
        processes: List[Process],
        lookup: Dict[int, Process],
        memory_manager: MemoryManager,
        clock: int,
        execution_order: List[str],
        gantt_segments: List[Dict[str, object]],
        algorithm: str,
        current_pid: Optional[int],
        rr_queue: Deque[int],
        mlq_queues: List[Deque[int]],
        mlfq_queues: List[Deque[int]],
        last_event: str,
        blocked: bool,
    ) -> Dict[str, object]:
        memory_snapshot = memory_manager.snapshot(lookup)
        waiting_processes = [
            {
                "pid": process.pid,
                "name": process.name,
                "memory_requirement": process.memory_requirement,
                "arrival_time": process.arrival_time,
            }
            for process in processes
            if process.arrived and process.remaining_time > 0 and not process.allocated
        ]
        memory_snapshot["waiting_processes"] = waiting_processes

        stats = self._build_stats(processes, clock)
        ready_queues = self._ready_queue_snapshot(
            algorithm=algorithm,
            processes=processes,
            rr_queue=rr_queue,
            mlq_queues=mlq_queues,
            mlfq_queues=mlfq_queues,
        )

        return {
            "clock": clock,
            "processes": [process.to_dict() for process in sorted(processes, key=lambda item: item.pid)],
            "execution_order": execution_order.copy(),
            "gantt_segments": [segment.copy() for segment in gantt_segments],
            "memory": memory_snapshot,
            "stats": stats,
            "ready_queues": ready_queues,
            "current_process": current_pid,
            "last_event": last_event,
            "blocked": blocked,
        }

    def _ready_queue_snapshot(
        self,
        *,
        algorithm: str,
        processes: List[Process],
        rr_queue: Deque[int],
        mlq_queues: List[Deque[int]],
        mlfq_queues: List[Deque[int]],
    ) -> List[Dict[str, object]]:
        lookup = {process.pid: process for process in processes}

        if algorithm == "round_robin":
            return [
                {
                    "label": "Ready Queue",
                    "items": [self._queue_item(lookup[pid]) for pid in rr_queue if pid in lookup],
                }
            ]
        if algorithm == "mlq":
            return [
                {
                    "label": f"Q{index}",
                    "items": [self._queue_item(lookup[pid]) for pid in queue if pid in lookup],
                }
                for index, queue in enumerate(mlq_queues)
            ]
        if algorithm == "mlfq":
            return [
                {
                    "label": f"Q{index}",
                    "items": [self._queue_item(lookup[pid]) for pid in queue if pid in lookup],
                }
                for index, queue in enumerate(mlfq_queues)
            ]

        ready_pool = [
            self._queue_item(process)
            for process in processes
            if process.arrived and process.allocated and process.remaining_time > 0 and process.state != "Running"
        ]
        return [{"label": "Ready Pool", "items": ready_pool}]

    def _queue_item(self, process: Process) -> Dict[str, object]:
        return {
            "pid": process.pid,
            "label": f"P{process.pid}",
            "name": process.name,
            "priority": process.priority,
            "remaining_time": process.remaining_time,
            "queue_label": f"Q{process.queue_level}",
        }

    def _build_stats(self, processes: List[Process], clock: int) -> Dict[str, object]:
        total = len(processes)
        terminated = [process for process in processes if process.remaining_time == 0]
        divisor = total or 1
        return {
            "total_processes": total,
            "ready_count": sum(process.state == "Ready" for process in processes),
            "running_count": sum(process.state == "Running" for process in processes),
            "waiting_count": sum(process.state == "Waiting" for process in processes),
            "terminated_count": len(terminated),
            "average_waiting_time": round(
                sum(process.waiting_time for process in processes) / divisor,
                2,
            ),
            "average_turnaround_time": round(
                sum(process.turnaround_time for process in processes) / divisor,
                2,
            ),
            "throughput": round(len(terminated) / clock, 2) if clock else 0,
        }


class OperatingSystemSimulator:
    """Coordinates all modules and exposes dashboard-friendly state."""

    DEFAULT_QUANTUM = 2

    def __init__(self) -> None:
        self.lock = Lock()
        self.process_manager = ProcessManager()
        self.scheduler = Scheduler()
        self.memory_blueprint = MemoryManager()
        self.file_system = InMemoryFileSystem()
        self.disk_manager = DiskManager()
        self.printer_spooler = PrinterSpooler()
        self.mini_game = MiniGame()
        self.activity_log: List[Dict[str, object]] = []
        self.active_algorithm = "round_robin"
        self.time_quantum = self.DEFAULT_QUANTUM
        self.queue_quantums = [2, 4, 8]
        self.frame_index = 0
        self.frames: List[Dict[str, object]] = []
        self.reset_all()

    def _log(self, message: str) -> None:
        frame = self.frames[self.frame_index] if self.frames else {"clock": 0}
        self.activity_log.append({"clock": frame["clock"], "message": message, "timestamp": now_stamp()})
        self.activity_log = self.activity_log[-18:]

    def _seed_sample_files(self) -> None:
        self.file_system.reset()
        self.disk_manager.reset_storage()

        sample_files = [
            ("/system", "boot.log", "Boot complete. Neon services online."),
            ("/system", "scheduler_notes.txt", "Try RR, SRTF, and MLFQ to compare response patterns."),
            ("/docs", "memory_map.txt", "Fixed and variable partition modes are available in the dashboard."),
        ]
        for folder, name, content in sample_files:
            success, _, path = self.file_system.create_file(name, content, folder)
            if success and path:
                self.disk_manager.store_file(path, len(content))

    def rebuild_simulation(self, message: Optional[str] = None) -> None:
        result = self.scheduler.simulate(
            process_definitions=self.process_manager.list_processes(),
            memory_blueprint=self.memory_blueprint,
            algorithm=self.active_algorithm,
            time_quantum=self.time_quantum,
            queue_quantums=self.queue_quantums,
        )
        self.frames = result["frames"]
        self.frame_index = 0
        if message:
            self._log(message)

    def reset_all(self) -> None:
        self.active_algorithm = "round_robin"
        self.time_quantum = self.DEFAULT_QUANTUM
        self.queue_quantums = [2, 4, 8]
        self.memory_blueprint.set_mode("fixed")
        self.process_manager.load_sample_processes()
        self.printer_spooler.reset()
        self.mini_game.reset()
        self.activity_log = []
        self._seed_sample_files()
        self.rebuild_simulation()
        self._log("Simulator reset. Sample processes, files, disk blocks, and printer state are ready.")

    def load_sample_processes(self) -> str:
        self.process_manager.load_sample_processes()
        self.rebuild_simulation("Loaded the default sample process set.")
        return "Sample processes loaded."

    def generate_processes(self, count: int) -> str:
        message = self.process_manager.generate_sample_processes(count)
        self.rebuild_simulation(message)
        return message

    def reset_process_runtime(self) -> str:
        message = self.process_manager.reset_runtime()
        self.rebuild_simulation("Reset process runtime values and rebuilt the schedule.")
        return message

    def set_scheduler_config(self, payload: Dict[str, object]) -> str:
        algorithm = str(payload.get("algorithm") or self.active_algorithm)
        if algorithm in self.scheduler.ALGORITHMS:
            self.active_algorithm = algorithm

        try:
            self.time_quantum = max(1, int(payload.get("time_quantum", self.time_quantum)))
        except (TypeError, ValueError):
            self.time_quantum = self.DEFAULT_QUANTUM

        raw_queue_quantums = str(payload.get("queue_quantums", "")).strip()
        if raw_queue_quantums:
            parsed = []
            for chunk in raw_queue_quantums.split(","):
                try:
                    parsed.append(max(1, int(chunk.strip())))
                except (TypeError, ValueError):
                    continue
            if parsed:
                self.queue_quantums = (parsed + self.queue_quantums)[:3]

        memory_mode = str(payload.get("memory_mode") or self.memory_blueprint.mode)
        self.memory_blueprint.set_mode(memory_mode)
        self.rebuild_simulation(
            f"Scheduler set to {self.scheduler.algorithm_label(self.active_algorithm)} with {self.memory_blueprint.mode} memory."
        )
        return "Scheduler configuration updated."

    def add_process(self, payload: Dict[str, object]) -> Tuple[bool, str]:
        success, message = self.process_manager.add_process(payload)
        if success:
            self.rebuild_simulation(message)
        return success, message

    def update_process(self, pid: int, payload: Dict[str, object]) -> Tuple[bool, str]:
        success, message = self.process_manager.update_process(pid, payload)
        if success:
            self.rebuild_simulation(message)
        return success, message

    def delete_process(self, pid: int) -> Tuple[bool, str]:
        success, message = self.process_manager.delete_process(pid)
        if success:
            self.rebuild_simulation(message)
        return success, message

    def step_schedule(self) -> str:
        if self.frame_index >= len(self.frames) - 1:
            message = "No more scheduling steps remain."
            self._log(message)
            return message
        self.frame_index += 1
        message = self.frames[self.frame_index]["last_event"]
        self._log(message)
        return message

    def run_schedule(self) -> str:
        if not self.frames:
            self.rebuild_simulation()
        self.frame_index = len(self.frames) - 1
        message = self.frames[self.frame_index]["last_event"]
        self._log(f"Completed full run using {self.scheduler.algorithm_label(self.active_algorithm)}.")
        return message

    def reset_schedule_view(self) -> str:
        self.frame_index = 0
        message = "Returned to the beginning of the current scheduling simulation."
        self._log(message)
        return message

    def create_file(self, payload: Dict[str, object]) -> Tuple[bool, str]:
        filename = str(payload.get("filename") or "").strip()
        content = str(payload.get("content") or "")
        folder = str(payload.get("folder") or "/")
        success, message, path = self.file_system.create_file(filename, content, folder)
        if not success or not path:
            return False, message
        if not self.disk_manager.store_file(path, len(content)):
            self.file_system.delete_file(path)
            return False, "Not enough disk blocks are available for that file."
        self._log(message)
        return True, message

    def edit_file(self, path: str, payload: Dict[str, object]) -> Tuple[bool, str, Optional[str]]:
        filename = str(payload.get("filename") or "").strip()
        content = str(payload.get("content") or "")
        folder = str(payload.get("folder") or "/")
        target_path = self.file_system.build_path(folder, filename)
        if not self.disk_manager.can_store(target_path, len(content), previous_path=path):
            return False, "Not enough disk blocks are available for the edited file.", None
        success, message, new_path = self.file_system.edit_file(path, filename, content, folder)
        if not success or not new_path:
            return False, message, None
        self.disk_manager.store_file(new_path, len(content), previous_path=path)
        self._log(message)
        return True, message, new_path

    def delete_file(self, path: str) -> Tuple[bool, str]:
        success, message = self.file_system.delete_file(path)
        if success:
            self.disk_manager.delete_file(path)
            self._log(message)
        return success, message

    def add_print_job(self, payload: Dict[str, object]) -> str:
        message = self.printer_spooler.add_job(
            document_name=str(payload.get("document_name") or ""),
            content=str(payload.get("content") or ""),
            source=str(payload.get("source") or "Control Center"),
        )
        self._log(message)
        return message

    def process_print_job(self) -> str:
        message = self.printer_spooler.process_next_job()
        self._log(message)
        return message

    def run_disk_schedule(self, payload: Dict[str, object]) -> str:
        raw_requests = str(payload.get("requests") or "")
        requests = [chunk.strip() for chunk in raw_requests.split(",") if chunk.strip()]
        parsed_requests = [int(item) for item in requests] if requests else []
        head_position = int(payload.get("head_position", 50))
        algorithm = str(payload.get("algorithm") or "fcfs")
        direction = str(payload.get("direction") or "up")
        result = self.disk_manager.run_schedule(algorithm, parsed_requests, head_position, direction)
        message = (
            f"Disk schedule ran with {result['algorithm_label']} and total head movement "
            f"of {result['total_head_movement']}."
        )
        self._log(message)
        return message

    def reset_game(self) -> str:
        message = self.mini_game.reset()
        self._log("Mini game reset.")
        return message

    def make_guess(self, payload: Dict[str, object]) -> Tuple[bool, str]:
        success, message = self.mini_game.guess(payload.get("guess"))
        self._log(f"Mini game update: {message}")
        return success, message

    def snapshot(self) -> Dict[str, object]:
        frame = self.frames[self.frame_index] if self.frames else {
            "clock": 0,
            "processes": [],
            "execution_order": [],
            "gantt_segments": [],
            "memory": self.memory_blueprint.snapshot({}),
            "stats": {
                "total_processes": 0,
                "ready_count": 0,
                "running_count": 0,
                "waiting_count": 0,
                "terminated_count": 0,
                "average_waiting_time": 0,
                "average_turnaround_time": 0,
                "throughput": 0,
            },
            "ready_queues": [],
            "current_process": None,
            "last_event": "No simulation data available.",
            "blocked": False,
        }

        files_snapshot = self.file_system.snapshot()
        terminated_count = frame["stats"]["terminated_count"]
        total_processes = frame["stats"]["total_processes"]

        return {
            "clock": frame["clock"],
            "shell": {
                "name": "Neon District OS",
                "build": "Academic Desktop Shell",
                "theme": "VA-11 HALL-A inspired cyberpunk desktop",
                "installed_apps": [
                    "System Monitor",
                    "Process Manager",
                    "CPU Scheduler",
                    "Memory Manager",
                    "Disk Manager",
                    "File Explorer",
                    "Printer Queue",
                    "Mini Game",
                    "Settings",
                ],
            },
            "scheduler": {
                "algorithm": self.active_algorithm,
                "algorithm_label": self.scheduler.algorithm_label(self.active_algorithm),
                "time_quantum": self.time_quantum,
                "queue_quantums": self.queue_quantums,
                "memory_mode": self.memory_blueprint.mode,
                "memory_mode_label": self.memory_blueprint.snapshot({}).get("mode_label", "Fixed Partitions"),
                "algorithms": self.scheduler.ALGORITHMS,
            },
            "time_quantum": self.time_quantum,
            "queue_quantums": self.queue_quantums,
            "processes": frame["processes"],
            "execution_order": frame["execution_order"],
            "gantt_segments": frame["gantt_segments"],
            "current_process": frame["current_process"],
            "last_event": frame["last_event"],
            "memory": frame["memory"],
            "stats": frame["stats"],
            "ready_queues": frame["ready_queues"],
            "files": files_snapshot,
            "printer": self.printer_spooler.snapshot(),
            "disk": self.disk_manager.snapshot(files_snapshot["items"]),
            "game": self.mini_game.snapshot(),
            "activity_log": self.activity_log,
            "demo": {
                "step_index": self.frame_index,
                "total_steps": max(len(self.frames) - 1, 0),
                "can_step": self.frame_index < len(self.frames) - 1,
                "all_terminated": total_processes > 0 and terminated_count == total_processes,
                "blocked": frame["blocked"],
            },
        }


app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False
simulator = OperatingSystemSimulator()


def build_response(
    message: str,
    *,
    ok: bool = True,
    status_code: int = 200,
    **extra: object,
):
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
def reset_simulator():
    with simulator.lock:
        simulator.reset_all()
        return build_response("Simulator reset to the upgraded default state.")


@app.post("/api/load-sample")
def load_sample_processes():
    with simulator.lock:
        message = simulator.load_sample_processes()
        return build_response(message)


@app.post("/api/processes/reset")
def reset_process_runtime():
    with simulator.lock:
        message = simulator.reset_process_runtime()
        return build_response(message)


@app.post("/api/processes/generate")
def generate_sample_processes():
    payload = request.get_json(silent=True) or {}
    count = payload.get("count", 5)
    with simulator.lock:
        message = simulator.generate_processes(count)
        return build_response(message)


@app.get("/api/processes")
def list_processes():
    with simulator.lock:
        state = simulator.snapshot()
        return jsonify(
            {
                "ok": True,
                "message": "Loaded process management data.",
                "processes": state["processes"],
                "scheduler": state["scheduler"],
                "stats": state["stats"],
            }
        )


@app.post("/api/processes")
def create_process():
    payload = request.get_json(silent=True) or {}
    with simulator.lock:
        success, message = simulator.add_process(payload)
        return build_response(message, ok=success, status_code=200 if success else 400)


@app.put("/api/processes/<int:pid>")
def update_process(pid: int):
    payload = request.get_json(silent=True) or {}
    with simulator.lock:
        success, message = simulator.update_process(pid, payload)
        return build_response(message, ok=success, status_code=200 if success else 404)


@app.delete("/api/processes/<int:pid>")
def delete_process(pid: int):
    with simulator.lock:
        success, message = simulator.delete_process(pid)
        return build_response(message, ok=success, status_code=200 if success else 404)


@app.post("/api/scheduler/config")
def update_scheduler_config():
    payload = request.get_json(silent=True) or {}
    with simulator.lock:
        message = simulator.set_scheduler_config(payload)
        return build_response(message)


@app.post("/api/quantum")
def update_quantum():
    payload = request.get_json(silent=True) or {}
    with simulator.lock:
        message = simulator.set_scheduler_config({"time_quantum": payload.get("time_quantum")})
        return build_response(message)


@app.post("/api/scheduler/reset")
def reset_schedule_view():
    with simulator.lock:
        message = simulator.reset_schedule_view()
        return build_response(message)


@app.post("/api/scheduler/step")
def step_scheduler():
    with simulator.lock:
        message = simulator.step_schedule()
        return build_response(message)


@app.post("/api/scheduler/run")
def run_scheduler():
    with simulator.lock:
        message = simulator.run_schedule()
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
                "scheduler": state["scheduler"],
            }
        )


@app.post("/api/memory/config")
def update_memory_mode():
    payload = request.get_json(silent=True) or {}
    with simulator.lock:
        message = simulator.set_scheduler_config({"memory_mode": payload.get("memory_mode")})
        return build_response(message)


@app.post("/api/memory/allocate")
def reallocate_memory():
    with simulator.lock:
        simulator.rebuild_simulation("Memory allocations recalculated from the current process set.")
        return build_response("Memory allocations recalculated.")


@app.post("/api/memory/release")
def release_memory():
    with simulator.lock:
        simulator.rebuild_simulation("Memory view refreshed. Completed processes already release memory automatically.")
        return build_response("Completed processes release memory automatically during simulation.")


@app.get("/api/files")
def get_files():
    with simulator.lock:
        return build_response("Loaded in-memory file system data.")


@app.post("/api/files")
def create_file():
    payload = request.get_json(silent=True) or {}
    with simulator.lock:
        success, message = simulator.create_file(payload)
        return build_response(message, ok=success, status_code=200 if success else 400)


@app.get("/api/files/<path:file_path>")
def read_file(file_path: str):
    normalized = "/" + file_path.lstrip("/")
    with simulator.lock:
        success, item, message = simulator.file_system.read_file(normalized)
        if not success or not item:
            return build_response(message, ok=False, status_code=404)
        return build_response(message, file=item)


@app.put("/api/files/<path:file_path>")
def edit_file(file_path: str):
    normalized = "/" + file_path.lstrip("/")
    payload = request.get_json(silent=True) or {}
    with simulator.lock:
        success, message, new_path = simulator.edit_file(normalized, payload)
        status_code = 200 if success else 400
        return build_response(message, ok=success, status_code=status_code, path=new_path)


@app.delete("/api/files/<path:file_path>")
def delete_file(file_path: str):
    normalized = "/" + file_path.lstrip("/")
    with simulator.lock:
        success, message = simulator.delete_file(normalized)
        return build_response(message, ok=success, status_code=200 if success else 404)


@app.get("/api/printer")
def get_printer():
    with simulator.lock:
        state = simulator.snapshot()
        return jsonify(
            {
                "ok": True,
                "message": "Loaded printer queue data.",
                "printer": state["printer"],
                "state": state,
            }
        )


@app.post("/api/printer/jobs")
def add_print_job():
    payload = request.get_json(silent=True) or {}
    with simulator.lock:
        message = simulator.add_print_job(payload)
        return build_response(message)


@app.post("/api/printer/process")
def process_print_job():
    with simulator.lock:
        message = simulator.process_print_job()
        return build_response(message)


@app.get("/api/disk")
def get_disk():
    with simulator.lock:
        state = simulator.snapshot()
        return jsonify(
            {
                "ok": True,
                "message": "Loaded disk manager data.",
                "disk": state["disk"],
                "state": state,
            }
        )


@app.post("/api/disk/schedule")
def run_disk_schedule():
    payload = request.get_json(silent=True) or {}
    with simulator.lock:
        message = simulator.run_disk_schedule(payload)
        return build_response(message)


@app.post("/api/game/reset")
def reset_game():
    with simulator.lock:
        message = simulator.reset_game()
        return build_response(message)


@app.post("/api/game/guess")
def make_guess():
    payload = request.get_json(silent=True) or {}
    with simulator.lock:
        success, message = simulator.make_guess(payload)
        return build_response(message, ok=success, status_code=200 if success else 400)


if __name__ == "__main__":
    app.run(debug=True)
