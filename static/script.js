const appState = {
    data: null,
    busy: false,
    demoTimer: null,
    activeFileName: null,
    activeFileContent: null,
};

const elements = {
    heroStats: document.getElementById("heroStats"),
    quantumInput: document.getElementById("quantumInput"),
    saveQuantumBtn: document.getElementById("saveQuantumBtn"),
    resetBtn: document.getElementById("resetBtn"),
    loadSampleBtn: document.getElementById("loadSampleBtn"),
    stepBtn: document.getElementById("stepBtn"),
    demoBtn: document.getElementById("demoBtn"),
    allocateBtn: document.getElementById("allocateBtn"),
    releaseBtn: document.getElementById("releaseBtn"),
    processPrintBtn: document.getElementById("processPrintBtn"),
    noticeCard: document.getElementById("noticeCard"),
    systemMessage: document.getElementById("systemMessage"),
    processTableBody: document.getElementById("processTableBody"),
    readyQueue: document.getElementById("readyQueue"),
    executionOrder: document.getElementById("executionOrder"),
    schedulerHighlights: document.getElementById("schedulerHighlights"),
    ganttChart: document.getElementById("ganttChart"),
    ganttTimes: document.getElementById("ganttTimes"),
    memoryPartitions: document.getElementById("memoryPartitions"),
    memoryWaitingList: document.getElementById("memoryWaitingList"),
    fileForm: document.getElementById("fileForm"),
    fileNameInput: document.getElementById("fileNameInput"),
    fileContentInput: document.getElementById("fileContentInput"),
    fileList: document.getElementById("fileList"),
    viewerLabel: document.getElementById("viewerLabel"),
    fileViewer: document.getElementById("fileViewer"),
    printJobForm: document.getElementById("printJobForm"),
    printNameInput: document.getElementById("printNameInput"),
    printContentInput: document.getElementById("printContentInput"),
    printSourceSelect: document.getElementById("printSourceSelect"),
    printerQueue: document.getElementById("printerQueue"),
    completedPrintJobs: document.getElementById("completedPrintJobs"),
    summaryStats: document.getElementById("summaryStats"),
    activityFeed: document.getElementById("activityFeed"),
};

elements.fileSubmitBtn = elements.fileForm.querySelector("button[type='submit']");
elements.printSubmitBtn = elements.printJobForm.querySelector("button[type='submit']");

document.addEventListener("DOMContentLoaded", initializeDashboard);

async function initializeDashboard() {
    bindEvents();
    await loadState();
}

function bindEvents() {
    elements.saveQuantumBtn.addEventListener("click", async () => {
        await performAction("/api/quantum", {
            method: "POST",
            body: { time_quantum: Number(elements.quantumInput.value) || 2 },
        });
    });

    elements.resetBtn.addEventListener("click", async () => {
        stopDemo();
        await performAction("/api/reset", {
            method: "POST",
            body: { time_quantum: Number(elements.quantumInput.value) || 2 },
        });
    });

    elements.loadSampleBtn.addEventListener("click", async () => {
        stopDemo();
        await performAction("/api/load-sample", {
            method: "POST",
            body: { time_quantum: Number(elements.quantumInput.value) || 2 },
        });
    });

    elements.stepBtn.addEventListener("click", async () => {
        stopDemo();
        await performAction("/api/scheduler/step", { method: "POST" });
    });

    elements.demoBtn.addEventListener("click", toggleDemoMode);

    elements.allocateBtn.addEventListener("click", async () => {
        await performAction("/api/memory/allocate", { method: "POST" });
    });

    elements.releaseBtn.addEventListener("click", async () => {
        await performAction("/api/memory/release", { method: "POST" });
    });

    elements.processPrintBtn.addEventListener("click", async () => {
        await performAction("/api/printer/process", { method: "POST" });
    });

    elements.fileForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        const filename = elements.fileNameInput.value.trim();
        const content = elements.fileContentInput.value;

        const result = await performAction("/api/files", {
            method: "POST",
            body: { filename, content },
        });

        if (result?.ok) {
            elements.fileForm.reset();
        }
    });

    elements.printJobForm.addEventListener("submit", async (event) => {
        event.preventDefault();

        const result = await performAction("/api/printer/jobs", {
            method: "POST",
            body: {
                document_name: elements.printNameInput.value.trim(),
                content: elements.printContentInput.value,
                source: elements.printSourceSelect.value,
            },
        });

        if (result?.ok) {
            elements.printJobForm.reset();
            renderPrintSources(appState.data?.processes || []);
        }
    });
}

async function loadState() {
    try {
        const response = await apiRequest("/api/state", { method: "GET" });
        renderDashboard(response.state);
        setSystemMessage(response.message, "info");
    } catch (error) {
        setSystemMessage(error.message, "danger");
    }
}

async function apiRequest(url, options = {}) {
    const config = { ...options, headers: { ...(options.headers || {}) } };

    if (config.body && typeof config.body !== "string") {
        config.headers["Content-Type"] = "application/json";
        config.body = JSON.stringify(config.body);
    }

    const response = await fetch(url, config);
    const data = await response.json();

    if (!response.ok || data.ok === false) {
        throw new Error(data.message || "The request could not be completed.");
    }

    return data;
}

async function performAction(url, { method = "POST", body = null } = {}) {
    if (appState.busy) {
        return null;
    }

    appState.busy = true;
    updateActionStates();

    try {
        const response = await apiRequest(url, { method, body });
        if (response.state) {
            renderDashboard(response.state);
        }

        if (Object.prototype.hasOwnProperty.call(response, "content")) {
            appState.activeFileName = response.filename;
            appState.activeFileContent = response.content;
            renderFileViewer();
        } else {
            syncActiveFileWithState();
        }

        setSystemMessage(response.message, "success");
        return response;
    } catch (error) {
        setSystemMessage(error.message, "danger");
        return null;
    } finally {
        appState.busy = false;
        updateActionStates();
    }
}

function renderDashboard(state) {
    appState.data = state;
    elements.quantumInput.value = state.time_quantum;
    renderHeroStats(state);
    renderProcesses(state.processes);
    renderScheduler(state);
    renderMemory(state.memory);
    renderFiles(state.files);
    renderPrinter(state.printer, state.processes);
    renderSummary(state);
    syncActiveFileWithState();
    updateActionStates();
}

function renderHeroStats(state) {
    const stats = state.stats;
    const cards = [
        {
            label: "System Clock",
            value: `t=${state.clock}`,
            detail: `Round Robin quantum: ${state.time_quantum}`,
        },
        {
            label: "Process Completion",
            value: `${stats.terminated_count}/${stats.total_processes}`,
            detail: `${stats.waiting_count} waiting | ${stats.ready_count} ready`,
        },
        {
            label: "Memory Usage",
            value: `${state.memory.used_memory}/${state.memory.total_memory} MB`,
            detail: `${state.memory.used_partitions}/${state.memory.total_partitions} partitions occupied`,
        },
        {
            label: "Simulation Assets",
            value: `${state.files.count} files`,
            detail: `${state.printer.pending_count} pending print jobs`,
        },
    ];

    elements.heroStats.innerHTML = cards
        .map(
            (card) => `
                <article class="metric-card">
                    <div class="metric-label">${escapeHtml(card.label)}</div>
                    <div class="metric-value">${escapeHtml(card.value)}</div>
                    <div class="metric-detail">${escapeHtml(card.detail)}</div>
                </article>
            `
        )
        .join("");
}

function renderProcesses(processes) {
    if (!processes.length) {
        elements.processTableBody.innerHTML = `
            <tr>
                <td colspan="9" class="muted">No processes are currently loaded.</td>
            </tr>
        `;
        return;
    }

    elements.processTableBody.innerHTML = processes
        .map(
            (process) => `
                <tr>
                    <td>P${process.pid}</td>
                    <td>${escapeHtml(process.name)}</td>
                    <td>${process.burst_time}</td>
                    <td>${process.remaining_time}</td>
                    <td>${process.memory_requirement} MB</td>
                    <td><span class="state-badge ${stateClass(process.state)}">${escapeHtml(process.state)}</span></td>
                    <td>${process.waiting_time}</td>
                    <td>${process.turnaround_time}</td>
                    <td><span class="table-pill">${escapeHtml(process.partition_label)}</span></td>
                </tr>
            `
        )
        .join("");
}

function renderScheduler(state) {
    renderTokenRow(elements.readyQueue, state.ready_queue, (item) => `${item.label} :: ${item.name}`);
    renderTokenRow(elements.executionOrder, state.execution_order, (item) => item);

    const schedulerStats = [
        {
            label: "Current Clock",
            value: `t=${state.clock}`,
            detail: "global simulation time",
        },
        {
            label: "Quantum",
            value: state.time_quantum,
            detail: "time units per slice",
        },
        {
            label: "Avg Waiting",
            value: state.stats.average_waiting_time,
            detail: "time units",
        },
        {
            label: "Avg Turnaround",
            value: state.stats.average_turnaround_time,
            detail: "time units",
        },
    ];

    elements.schedulerHighlights.innerHTML = schedulerStats
        .map(
            (card) => `
                <article class="metric-card">
                    <div class="metric-label">${escapeHtml(card.label)}</div>
                    <div class="metric-value">${escapeHtml(String(card.value))}</div>
                    <div class="metric-detail">${escapeHtml(card.detail)}</div>
                </article>
            `
        )
        .join("");

    if (!state.gantt_segments.length) {
        elements.ganttChart.innerHTML = `<span class="empty-chip">Run the scheduler to build the Gantt chart.</span>`;
        elements.ganttTimes.innerHTML = "";
        return;
    }

    elements.ganttChart.innerHTML = state.gantt_segments
        .map(
            (segment) => `
                <article class="gantt-segment pid-${segment.pid}" style="--duration:${segment.duration}">
                    <div class="gantt-label">${escapeHtml(segment.label)}</div>
                    <div class="gantt-meta">
                        ${escapeHtml(segment.process_name)}<br>
                        t=${segment.start} to t=${segment.end}
                    </div>
                </article>
            `
        )
        .join("");

    elements.ganttTimes.innerHTML = state.gantt_segments
        .map(
            (segment) => `
                <div class="time-badge" style="--duration:${segment.duration}">
                    <span>${segment.start}</span>
                    <span>${segment.end}</span>
                </div>
            `
        )
        .join("");
}

function renderMemory(memory) {
    elements.memoryPartitions.innerHTML = memory.partitions
        .map((partition) => {
            const occupant = partition.process;
            const title = occupant
                ? `P${occupant.pid} :: ${occupant.name}`
                : "Free Partition";
            const state = occupant ? occupant.state : "Available";
            const fillWidth = Math.max(partition.usage_percent, occupant ? 14 : 2);

            return `
                <article class="partition-card">
                    <div class="partition-header">
                        <div>
                            <div class="partition-title">${escapeHtml(partition.label)}</div>
                            <div class="partition-size">${partition.size} MB capacity</div>
                        </div>
                        <span class="state-badge ${stateClass(state)}">${escapeHtml(state)}</span>
                    </div>
                    <div class="memory-bar">
                        <div class="memory-fill" style="width:${fillWidth}%"></div>
                    </div>
                    <div class="memory-meta">
                        <span>${escapeHtml(title)}</span>
                        <span>Used: ${partition.used_memory} MB</span>
                        <span>Free: ${partition.free_space} MB</span>
                    </div>
                </article>
            `;
        })
        .join("");

    if (!memory.waiting_processes.length) {
        elements.memoryWaitingList.innerHTML = `<span class="empty-chip">No processes are waiting for memory.</span>`;
        return;
    }

    elements.memoryWaitingList.innerHTML = memory.waiting_processes
        .map(
            (process) => `
                <div class="queue-chip waiting">
                    P${process.pid} :: ${escapeHtml(process.name)} needs ${process.memory_requirement} MB
                </div>
            `
        )
        .join("");
}

function renderFiles(files) {
    if (!files.items.length) {
        elements.fileList.innerHTML = `<span class="empty-chip">No simulated files stored in memory.</span>`;
        return;
    }

    elements.fileList.innerHTML = files.items
        .map((file) => {
            const isActive = appState.activeFileName === file.name;
            return `
                <article class="list-card" data-file="${escapeAttribute(file.name)}">
                    <div class="list-card-header">
                        <div>
                            <strong>${escapeHtml(file.name)}</strong>
                            <div class="file-meta">
                                <span>${file.size} characters</span>
                                <span>${isActive ? "Viewer active" : "Ready to open"}</span>
                            </div>
                        </div>
                        <span class="queue-chip ready">Stored</span>
                    </div>
                    <div class="list-card-actions">
                        <button class="button ghost-button small-button" type="button" data-action="view" data-file="${escapeAttribute(file.name)}">View Contents</button>
                        <button class="button ghost-button small-button" type="button" data-action="delete" data-file="${escapeAttribute(file.name)}">Delete File</button>
                    </div>
                </article>
            `;
        })
        .join("");

    elements.fileList.querySelectorAll("[data-action='view']").forEach((button) => {
        button.addEventListener("click", async () => {
            const filename = button.getAttribute("data-file");
            const result = await performAction(`/api/files/${encodeURIComponent(filename)}`, {
                method: "GET",
            });

            if (result?.ok) {
                appState.activeFileName = result.filename;
                appState.activeFileContent = result.content;
                renderFileViewer();
            }
        });
    });

    elements.fileList.querySelectorAll("[data-action='delete']").forEach((button) => {
        button.addEventListener("click", async () => {
            const filename = button.getAttribute("data-file");
            const confirmed = window.confirm(`Delete the simulated file "${filename}"?`);
            if (!confirmed) {
                return;
            }

            const result = await performAction(`/api/files/${encodeURIComponent(filename)}`, {
                method: "DELETE",
            });

            if (result?.ok && appState.activeFileName === filename) {
                appState.activeFileName = null;
                appState.activeFileContent = null;
                renderFileViewer();
            }
        });
    });
}

function renderFileViewer() {
    if (!appState.activeFileName || appState.activeFileContent == null) {
        elements.viewerLabel.textContent = "Select a file";
        elements.fileViewer.textContent = "Select a file from the list to display its contents.";
        return;
    }

    elements.viewerLabel.textContent = appState.activeFileName;
    elements.fileViewer.textContent = appState.activeFileContent;
}

function syncActiveFileWithState() {
    const availableFiles = appState.data?.files?.items || [];
    const activeFile = availableFiles.find((file) => file.name === appState.activeFileName);

    if (!activeFile) {
        appState.activeFileName = null;
        appState.activeFileContent = null;
        renderFileViewer();
        return;
    }

    if (appState.activeFileContent == null) {
        appState.activeFileContent = activeFile.content;
    }

    renderFileViewer();
}

function renderPrintSources(processes) {
    const previousValue = elements.printSourceSelect.value || "User Console";
    const options = ["User Console", ...processes.map((process) => `P${process.pid} :: ${process.name}`)];

    elements.printSourceSelect.innerHTML = options
        .map(
            (option) => `
                <option value="${escapeAttribute(option)}">${escapeHtml(option)}</option>
            `
        )
        .join("");

    elements.printSourceSelect.value = options.includes(previousValue) ? previousValue : "User Console";
}

function renderPrinter(printer, processes) {
    renderPrintSources(processes);

    if (!printer.queue.length) {
        elements.printerQueue.innerHTML = `<span class="empty-chip">No pending print jobs in the spooler.</span>`;
    } else {
        elements.printerQueue.innerHTML = printer.queue
            .map(
                (job, index) => `
                    <article class="queue-item">
                        <div class="queue-item-header">
                            <strong>${index + 1}. ${escapeHtml(job.name)}</strong>
                            <span class="queue-chip waiting">Queued</span>
                        </div>
                        <div class="queue-meta">
                            <span>Source: ${escapeHtml(job.source)}</span>
                            <span>Size: ${job.size} chars</span>
                        </div>
                    </article>
                `
            )
            .join("");
    }

    if (!printer.completed_jobs.length) {
        elements.completedPrintJobs.innerHTML = `<span class="empty-chip">No completed print jobs yet.</span>`;
    } else {
        elements.completedPrintJobs.innerHTML = printer.completed_jobs
            .slice()
            .reverse()
            .map(
                (job) => `
                    <article class="queue-item">
                        <div class="queue-item-header">
                            <strong>${escapeHtml(job.name)}</strong>
                            <span class="queue-chip running">Printed</span>
                        </div>
                        <div class="queue-meta">
                            <span>Source: ${escapeHtml(job.source)}</span>
                            <span>Size: ${job.size} chars</span>
                        </div>
                    </article>
                `
            )
            .join("");
    }
}

function renderSummary(state) {
    const stats = state.stats;
    const summaryCards = [
        {
            label: "Average Waiting Time",
            value: stats.average_waiting_time,
            detail: "time units",
        },
        {
            label: "Average Turnaround Time",
            value: stats.average_turnaround_time,
            detail: "time units",
        },
        {
            label: "Throughput",
            value: stats.throughput,
            detail: "completed processes per unit",
        },
        {
            label: "Completion Rate",
            value: `${stats.terminated_count}/${stats.total_processes}`,
            detail: "processes terminated",
        },
    ];

    elements.summaryStats.innerHTML = summaryCards
        .map(
            (card) => `
                <article class="metric-card">
                    <div class="metric-label">${escapeHtml(card.label)}</div>
                    <div class="metric-value">${escapeHtml(String(card.value))}</div>
                    <div class="metric-detail">${escapeHtml(card.detail)}</div>
                </article>
            `
        )
        .join("");

    if (!state.activity_log.length) {
        elements.activityFeed.innerHTML = `<div class="activity-item muted">No activity recorded yet.</div>`;
        return;
    }

    elements.activityFeed.innerHTML = state.activity_log
        .slice()
        .reverse()
        .map(
            (entry) => `
                <article class="activity-item">
                    <div class="activity-time">t=${entry.clock}</div>
                    <div class="activity-message">${escapeHtml(entry.message)}</div>
                </article>
            `
        )
        .join("");
}

function renderTokenRow(container, items, labelBuilder) {
    if (!items.length) {
        container.innerHTML = `<span class="empty-chip">No entries yet.</span>`;
        return;
    }

    container.innerHTML = items
        .map((item) => `<span class="token">${escapeHtml(labelBuilder(item))}</span>`)
        .join("");
}

async function toggleDemoMode() {
    if (appState.demoTimer) {
        stopDemo("Demo mode paused.");
        return;
    }

    if (!appState.data) {
        return;
    }

    if (appState.data.demo.all_terminated || appState.data.demo.blocked) {
        const reloaded = await performAction("/api/load-sample", {
            method: "POST",
            body: { time_quantum: Number(elements.quantumInput.value) || 2 },
        });
        if (!reloaded) {
            return;
        }
    }

    appState.demoTimer = window.setInterval(runDemoStep, 1050);
    elements.demoBtn.textContent = "Pause Demo";
    setSystemMessage("Demo mode running. The scheduler will advance automatically.", "info");
    await runDemoStep();
}

async function runDemoStep() {
    if (appState.busy) {
        return;
    }

    const result = await performAction("/api/scheduler/step", { method: "POST" });
    if (!result?.state) {
        stopDemo();
        return;
    }

    if (result.state.demo.all_terminated) {
        stopDemo("Demo complete. All sample processes have terminated.");
        return;
    }

    if (result.state.demo.blocked) {
        stopDemo("Demo stopped because no ready process could continue.");
    }
}

function stopDemo(message = "") {
    if (appState.demoTimer) {
        window.clearInterval(appState.demoTimer);
        appState.demoTimer = null;
    }

    elements.demoBtn.textContent = "Run Full Scheduling Demo";
    updateActionStates();

    if (message) {
        setSystemMessage(message, "info");
    }
}

function updateActionStates() {
    const data = appState.data;
    const demoRunning = Boolean(appState.demoTimer);
    const canStep = data ? data.demo.can_step : false;
    const hasWaitingMemory = data ? data.memory.waiting_processes.length > 0 : false;
    const hasPrintJobs = data ? data.printer.pending_count > 0 : false;

    elements.saveQuantumBtn.disabled = appState.busy || demoRunning;
    elements.resetBtn.disabled = appState.busy;
    elements.loadSampleBtn.disabled = appState.busy;
    elements.stepBtn.disabled = appState.busy || demoRunning || !canStep;
    elements.allocateBtn.disabled = appState.busy || demoRunning || !hasWaitingMemory;
    elements.releaseBtn.disabled = appState.busy || demoRunning;
    elements.processPrintBtn.disabled = appState.busy || !hasPrintJobs;
    elements.fileNameInput.disabled = appState.busy;
    elements.fileContentInput.disabled = appState.busy;
    elements.fileSubmitBtn.disabled = appState.busy;
    elements.printNameInput.disabled = appState.busy;
    elements.printSourceSelect.disabled = appState.busy;
    elements.printContentInput.disabled = appState.busy;
    elements.printSubmitBtn.disabled = appState.busy;

    if (!demoRunning) {
        elements.demoBtn.disabled = appState.busy || !data;
    } else {
        elements.demoBtn.disabled = false;
    }
}

function setSystemMessage(message, tone = "info") {
    elements.noticeCard.dataset.tone = tone;
    elements.systemMessage.textContent = message;
}

function stateClass(state) {
    const normalized = String(state).toLowerCase();
    if (normalized === "ready") {
        return "ready";
    }
    if (normalized === "running") {
        return "running";
    }
    if (normalized === "waiting") {
        return "waiting";
    }
    if (normalized === "terminated") {
        return "terminated";
    }
    return "ready";
}

function escapeHtml(value) {
    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#39;");
}

function escapeAttribute(value) {
    return escapeHtml(value);
}
