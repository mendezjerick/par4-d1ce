const WALLPAPERS = [
    {
        id: "wallpaper-dice",
        preview: "dice",
        name: "Dice",
        detail: "Imported JPG wallpaper asset for the desktop shell.",
    },
    {
        id: "wallpaper-neon-noir",
        preview: "neon-noir",
        name: "Neon Noir",
        detail: "Default city glow and dark glass panels.",
    },
    {
        id: "wallpaper-afterglow",
        preview: "afterglow",
        name: "Afterglow",
        detail: "Warm magenta haze with lounge lighting.",
    },
    {
        id: "wallpaper-rain-grid",
        preview: "rain-grid",
        name: "Rain Grid",
        detail: "Cold blue grid with rainy skyline energy.",
    },
    {
        id: "wallpaper-lounge",
        preview: "lounge",
        name: "Lounge Violet",
        detail: "Low-light purple atmosphere with amber highlights.",
    },
];

const APP_DEFINITIONS = [
    {
        id: "system",
        icon: "SYS",
        title: "System Monitor",
        subtitle: "Live shell overview",
        width: 900,
        height: 620,
    },
    {
        id: "process",
        icon: "PRC",
        title: "Process Manager",
        subtitle: "Task creation and process control",
        width: 1040,
        height: 650,
    },
    {
        id: "scheduler",
        icon: "CPU",
        title: "CPU Scheduler",
        subtitle: "Algorithms and Gantt timeline",
        width: 980,
        height: 660,
    },
    {
        id: "memory",
        icon: "MEM",
        title: "Memory Manager",
        subtitle: "Allocation, partitions, fragmentation",
        width: 860,
        height: 560,
    },
    {
        id: "disk",
        icon: "DSK",
        title: "Disk Manager",
        subtitle: "Head movement and storage blocks",
        width: 920,
        height: 600,
    },
    {
        id: "files",
        icon: "FIL",
        title: "File Explorer",
        subtitle: "Folders, files, viewer",
        width: 1080,
        height: 650,
    },
    {
        id: "printer",
        icon: "I/O",
        title: "Printer Queue",
        subtitle: "Spooling and completed jobs",
        width: 880,
        height: 560,
    },
    {
        id: "game",
        icon: "FUN",
        title: "Mini Game",
        subtitle: "Built-in app",
        width: 760,
        height: 460,
    },
    {
        id: "settings",
        icon: "SET",
        title: "Settings",
        subtitle: "Wallpaper and shell defaults",
        width: 780,
        height: 560,
    },
];

const DEFAULT_OPEN_APPS = ["system", "scheduler"];
const DEFAULT_WALLPAPER_ID = "wallpaper-dice";
const ALL_WALLPAPER_CLASSES = WALLPAPERS.map((wallpaper) => wallpaper.id);
const APP_LOOKUP = Object.fromEntries(APP_DEFINITIONS.map((app) => [app.id, app]));
const FOLDER_ALL = "__all__";

const appState = {
    data: null,
    busy: false,
    demoTimer: null,
    activeFilePath: null,
    activeFolder: FOLDER_ALL,
    activeApp: null,
    windows: {},
    zCounter: 10,
    bootReady: false,
    desktopEntered: false,
    wallpaperId: DEFAULT_WALLPAPER_ID,
    reducedMotion: false,
};

const elements = {
    bootScreen: document.getElementById("bootScreen"),
    bootProgressBar: document.getElementById("bootProgressBar"),
    enterDesktopBtn: document.getElementById("enterDesktopBtn"),
    desktopShell: document.getElementById("desktopShell"),
    desktopIcons: document.getElementById("desktopIcons"),
    desktopWallpaperLabel: document.getElementById("desktopWallpaperLabel"),
    activeAlgorithmLabel: document.getElementById("activeAlgorithmLabel"),
    stepCounter: document.getElementById("stepCounter"),
    windowLayer: document.getElementById("windowLayer"),
    startMenu: document.getElementById("startMenu"),
    startButton: document.getElementById("startButton"),
    startMenuApps: document.getElementById("startMenuApps"),
    taskbar: document.getElementById("taskbar"),
    taskbarApps: document.getElementById("taskbarApps"),
    traySettingsButton: document.getElementById("traySettingsButton"),
    systemMessage: document.getElementById("systemMessage"),
    liveClock: document.getElementById("liveClock"),
    wallpaperOptions: document.getElementById("wallpaperOptions"),
    startWallpaperChoices: document.getElementById("startWallpaperChoices"),
    animationToggle: document.getElementById("animationToggle"),
    startOpenSettingsBtn: document.getElementById("startOpenSettingsBtn"),
    startLoadSampleBtn: document.getElementById("startLoadSampleBtn"),
    startResetSystemBtn: document.getElementById("startResetSystemBtn"),
    settingsLoadSampleBtn: document.getElementById("settingsLoadSampleBtn"),
    settingsApplySchedulerBtn: document.getElementById("settingsApplySchedulerBtn"),
    settingsAlgorithmSelect: document.getElementById("settingsAlgorithmSelect"),
    settingsQuantumInput: document.getElementById("settingsQuantumInput"),
    settingsQueueQuantumInput: document.getElementById("settingsQueueQuantumInput"),
    settingsMemoryModeSelect: document.getElementById("settingsMemoryModeSelect"),
    heroStats: document.getElementById("heroStats"),
    summaryStats: document.getElementById("summaryStats"),
    activityFeed: document.getElementById("activityFeed"),
    algorithmSelect: document.getElementById("algorithmSelect"),
    quantumInput: document.getElementById("quantumInput"),
    queueQuantumInput: document.getElementById("queueQuantumInput"),
    memoryModeSelect: document.getElementById("memoryModeSelect"),
    applySchedulerBtn: document.getElementById("applySchedulerBtn"),
    resetBtn: document.getElementById("resetBtn"),
    loadSampleBtn: document.getElementById("loadSampleBtn"),
    generateSampleBtn: document.getElementById("generateSampleBtn"),
    resetProcessRuntimeBtn: document.getElementById("resetProcessRuntimeBtn"),
    resetScheduleBtn: document.getElementById("resetScheduleBtn"),
    stepBtn: document.getElementById("stepBtn"),
    runBtn: document.getElementById("runBtn"),
    demoBtn: document.getElementById("demoBtn"),
    processForm: document.getElementById("processForm"),
    processPidInput: document.getElementById("processPidInput"),
    processNameInput: document.getElementById("processNameInput"),
    processArrivalInput: document.getElementById("processArrivalInput"),
    processBurstInput: document.getElementById("processBurstInput"),
    processPriorityInput: document.getElementById("processPriorityInput"),
    processMemoryInput: document.getElementById("processMemoryInput"),
    processSubmitBtn: document.getElementById("processSubmitBtn"),
    processCancelBtn: document.getElementById("processCancelBtn"),
    processTableBody: document.getElementById("processTableBody"),
    readyQueues: document.getElementById("readyQueues"),
    schedulerHighlights: document.getElementById("schedulerHighlights"),
    ganttChart: document.getElementById("ganttChart"),
    ganttTimes: document.getElementById("ganttTimes"),
    executionOrder: document.getElementById("executionOrder"),
    memoryStats: document.getElementById("memoryStats"),
    memoryPartitions: document.getElementById("memoryPartitions"),
    memoryWaitingList: document.getElementById("memoryWaitingList"),
    diskForm: document.getElementById("diskForm"),
    diskRequestsInput: document.getElementById("diskRequestsInput"),
    diskHeadInput: document.getElementById("diskHeadInput"),
    diskAlgorithmSelect: document.getElementById("diskAlgorithmSelect"),
    diskDirectionSelect: document.getElementById("diskDirectionSelect"),
    runDiskBtn: document.getElementById("runDiskBtn"),
    diskStorageStats: document.getElementById("diskStorageStats"),
    diskScheduleResult: document.getElementById("diskScheduleResult"),
    diskBlockMap: document.getElementById("diskBlockMap"),
    fileForm: document.getElementById("fileForm"),
    fileOriginalPathInput: document.getElementById("fileOriginalPathInput"),
    fileFolderInput: document.getElementById("fileFolderInput"),
    fileNameInput: document.getElementById("fileNameInput"),
    fileContentInput: document.getElementById("fileContentInput"),
    fileSubmitBtn: document.getElementById("fileSubmitBtn"),
    fileCancelBtn: document.getElementById("fileCancelBtn"),
    folderSidebar: document.getElementById("folderSidebar"),
    fileList: document.getElementById("fileList"),
    viewerLabel: document.getElementById("viewerLabel"),
    fileViewer: document.getElementById("fileViewer"),
    printJobForm: document.getElementById("printJobForm"),
    printNameInput: document.getElementById("printNameInput"),
    printSourceSelect: document.getElementById("printSourceSelect"),
    printContentInput: document.getElementById("printContentInput"),
    printSubmitBtn: document.getElementById("printSubmitBtn"),
    processPrintBtn: document.getElementById("processPrintBtn"),
    printerQueue: document.getElementById("printerQueue"),
    completedPrintJobs: document.getElementById("completedPrintJobs"),
    gameForm: document.getElementById("gameForm"),
    gameGuessInput: document.getElementById("gameGuessInput"),
    gameGuessBtn: document.getElementById("gameGuessBtn"),
    gameResetBtn: document.getElementById("gameResetBtn"),
    gameMessage: document.getElementById("gameMessage"),
    gameHistory: document.getElementById("gameHistory"),
};

document.addEventListener("DOMContentLoaded", initializeDesktopShell);

async function initializeDesktopShell() {
    initializeWindowState();
    bindEvents();
    renderDesktopIcons();
    renderStartMenuApps();
    renderWallpaperOptions();
    syncShellViewportMetrics();
    applyWallpaperPreference(readPreference("wallpaper", DEFAULT_WALLPAPER_ID), false);
    applyReducedMotionPreference(readPreference("reduced_motion", "0") === "1", false);
    startClock();
    runBootSequence();
    await loadState();
}

function initializeWindowState() {
    APP_DEFINITIONS.forEach((app, index) => {
        appState.windows[app.id] = {
            open: false,
            minimized: false,
            maximized: false,
            z: 0,
            bounds: createDefaultBounds(app, index),
            restoreBounds: null,
        };
    });
}

function bindEvents() {
    elements.enterDesktopBtn.addEventListener("click", enterDesktop);

    elements.startButton.addEventListener("click", (event) => {
        event.stopPropagation();
        setStartMenuVisible(elements.startMenu.hidden);
    });

    elements.startMenu.addEventListener("click", (event) => {
        event.stopPropagation();
    });

    document.addEventListener("click", () => {
        setStartMenuVisible(false);
    });

    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape") {
            setStartMenuVisible(false);
        }
    });

    window.addEventListener("resize", handleViewportResize);
    window.visualViewport?.addEventListener("resize", handleViewportResize);
    elements.desktopIcons.addEventListener("click", handleAppLaunchClick);
    elements.startMenuApps.addEventListener("click", handleAppLaunchClick);
    elements.taskbarApps.addEventListener("click", handleTaskbarAppClick);
    elements.traySettingsButton.addEventListener("click", () => {
        openWindow("settings");
    });
    elements.startOpenSettingsBtn.addEventListener("click", () => {
        openWindow("settings");
    });

    elements.wallpaperOptions.addEventListener("click", handleWallpaperSelection);
    elements.startWallpaperChoices.addEventListener("click", handleWallpaperSelection);
    elements.animationToggle.addEventListener("change", () => {
        applyReducedMotionPreference(elements.animationToggle.checked, true);
    });

    elements.windowLayer.addEventListener("click", handleWindowLayerClick);
    elements.windowLayer.addEventListener("mousedown", handleWindowMouseDown);
    elements.windowLayer.addEventListener("dblclick", handleWindowDoubleClick);

    elements.applySchedulerBtn.addEventListener("click", async () => {
        await applySchedulerConfiguration("primary");
    });
    elements.settingsApplySchedulerBtn.addEventListener("click", async () => {
        await applySchedulerConfiguration("settings");
    });

    elements.resetBtn.addEventListener("click", handleResetSimulator);
    elements.startResetSystemBtn.addEventListener("click", handleResetSimulator);

    elements.loadSampleBtn.addEventListener("click", handleLoadSampleProcesses);
    elements.startLoadSampleBtn.addEventListener("click", handleLoadSampleProcesses);
    elements.settingsLoadSampleBtn.addEventListener("click", handleLoadSampleProcesses);

    elements.generateSampleBtn.addEventListener("click", handleGenerateSampleProcesses);
    elements.resetProcessRuntimeBtn.addEventListener("click", async () => {
        stopDemo();
        await performAction("/api/processes/reset", { method: "POST" });
    });
    elements.resetScheduleBtn.addEventListener("click", async () => {
        stopDemo();
        await performAction("/api/scheduler/reset", { method: "POST" });
    });
    elements.stepBtn.addEventListener("click", async () => {
        stopDemo();
        openWindow("scheduler");
        await performAction("/api/scheduler/step", { method: "POST" });
    });
    elements.runBtn.addEventListener("click", async () => {
        stopDemo();
        openWindow("scheduler");
        await performAction("/api/scheduler/run", { method: "POST" });
    });
    elements.demoBtn.addEventListener("click", toggleDemoMode);

    elements.processForm.addEventListener("submit", handleProcessSubmit);
    elements.processCancelBtn.addEventListener("click", resetProcessForm);
    elements.processTableBody.addEventListener("click", handleProcessTableClick);

    elements.diskForm.addEventListener("submit", handleDiskSubmit);

    elements.fileForm.addEventListener("submit", handleFileSubmit);
    elements.fileCancelBtn.addEventListener("click", resetFileForm);
    elements.folderSidebar.addEventListener("click", handleFolderSelection);
    elements.fileList.addEventListener("click", handleFileListClick);

    elements.printJobForm.addEventListener("submit", handlePrintJobSubmit);
    elements.processPrintBtn.addEventListener("click", async () => {
        await performAction("/api/printer/process", { method: "POST" });
    });

    elements.gameForm.addEventListener("submit", handleGameSubmit);
    elements.gameResetBtn.addEventListener("click", async () => {
        await performAction("/api/game/reset", { method: "POST" });
    });
}

function handleAppLaunchClick(event) {
    const button = event.target.closest("[data-app]");
    if (!button) {
        return;
    }
    const appId = button.dataset.app;
    if (!APP_LOOKUP[appId]) {
        return;
    }
    openWindow(appId);
}

function handleTaskbarAppClick(event) {
    const button = event.target.closest("[data-app]");
    if (!button) {
        return;
    }
    const appId = button.dataset.app;
    const windowState = appState.windows[appId];
    if (!windowState) {
        return;
    }

    if (windowState.minimized) {
        restoreWindow(appId);
        return;
    }

    if (appState.activeApp === appId) {
        minimizeWindow(appId);
        return;
    }

    openWindow(appId);
}

function handleWindowLayerClick(event) {
    const control = event.target.closest("[data-window-action]");
    if (control) {
        const appId = control.dataset.app;
        const action = control.dataset.windowAction;

        if (action === "close") {
            closeWindow(appId);
        } else if (action === "minimize") {
            minimizeWindow(appId);
        } else if (action === "maximize") {
            toggleMaximizeWindow(appId);
        }
        return;
    }

    const windowElement = event.target.closest(".app-window");
    if (windowElement?.dataset.app) {
        focusWindow(windowElement.dataset.app);
    }
}

function handleWindowDoubleClick(event) {
    const titlebar = event.target.closest("[data-drag-handle]");
    if (!titlebar || event.target.closest(".window-control")) {
        return;
    }

    const windowElement = titlebar.closest(".app-window");
    if (windowElement?.dataset.app) {
        toggleMaximizeWindow(windowElement.dataset.app);
    }
}

function handleWindowMouseDown(event) {
    const windowElement = event.target.closest(".app-window");
    if (!windowElement?.dataset.app) {
        return;
    }

    focusWindow(windowElement.dataset.app);

    const titlebar = event.target.closest("[data-drag-handle]");
    if (!titlebar || event.target.closest(".window-control")) {
        return;
    }

    const appId = windowElement.dataset.app;
    const windowState = appState.windows[appId];
    if (!windowState || windowState.maximized || window.innerWidth <= 760) {
        return;
    }

    event.preventDefault();
    const originBounds = { ...windowState.bounds };
    const startX = event.clientX;
    const startY = event.clientY;

    titlebar.classList.add("dragging");

    const onMouseMove = (moveEvent) => {
        const nextBounds = {
            ...originBounds,
            x: originBounds.x + (moveEvent.clientX - startX),
            y: originBounds.y + (moveEvent.clientY - startY),
        };
        windowState.bounds = clampBounds(nextBounds);
        applyWindowLayout(appId);
    };

    const onMouseUp = () => {
        titlebar.classList.remove("dragging");
        document.removeEventListener("mousemove", onMouseMove);
        document.removeEventListener("mouseup", onMouseUp);
    };

    document.addEventListener("mousemove", onMouseMove);
    document.addEventListener("mouseup", onMouseUp);
}

async function handleResetSimulator() {
    stopDemo();
    appState.activeFilePath = null;
    appState.activeFolder = FOLDER_ALL;
    await performAction("/api/reset", { method: "POST" });
    openWindow("system");
}

async function handleLoadSampleProcesses() {
    stopDemo();
    await performAction("/api/load-sample", { method: "POST" });
    openWindow("process");
    openWindow("scheduler");
}

async function handleGenerateSampleProcesses() {
    const count = window.prompt("How many sample processes should be generated? (3-8)", "5");
    if (!count) {
        return;
    }

    stopDemo();
    await performAction("/api/processes/generate", {
        method: "POST",
        body: { count: Number(count) || 5 },
    });
    openWindow("process");
}

async function handleProcessSubmit(event) {
    event.preventDefault();

    const pid = elements.processPidInput.value;
    const payload = {
        name: elements.processNameInput.value.trim(),
        arrival_time: Number(elements.processArrivalInput.value) || 0,
        burst_time: Number(elements.processBurstInput.value) || 1,
        priority: Number(elements.processPriorityInput.value) || 1,
        memory_requirement: Number(elements.processMemoryInput.value) || 1,
    };

    const result = await performAction(pid ? `/api/processes/${pid}` : "/api/processes", {
        method: pid ? "PUT" : "POST",
        body: payload,
    });

    if (result?.ok) {
        resetProcessForm();
    }
}

async function handleProcessTableClick(event) {
    const actionButton = event.target.closest("[data-action]");
    if (!actionButton) {
        return;
    }

    const action = actionButton.dataset.action;
    const pid = Number(actionButton.dataset.pid);
    if (!pid) {
        return;
    }

    if (action === "edit") {
        startProcessEdit(pid);
        return;
    }

    if (action === "delete") {
        if (!window.confirm(`Delete process P${pid}?`)) {
            return;
        }
        await performAction(`/api/processes/${pid}`, { method: "DELETE" });
    }
}

async function handleDiskSubmit(event) {
    event.preventDefault();
    openWindow("disk");
    await performAction("/api/disk/schedule", {
        method: "POST",
        body: {
            requests: elements.diskRequestsInput.value,
            head_position: Number(elements.diskHeadInput.value) || 0,
            algorithm: elements.diskAlgorithmSelect.value,
            direction: elements.diskDirectionSelect.value,
        },
    });
}

async function handleFileSubmit(event) {
    event.preventDefault();

    const originalPath = elements.fileOriginalPathInput.value;
    const payload = {
        folder: elements.fileFolderInput.value.trim() || "/",
        filename: elements.fileNameInput.value.trim(),
        content: elements.fileContentInput.value,
    };

    const result = await performAction(
        originalPath ? `/api/files/${encodeURIComponent(originalPath.slice(1))}` : "/api/files",
        {
            method: originalPath ? "PUT" : "POST",
            body: payload,
        }
    );

    if (result?.ok) {
        resetFileForm();
        if (result.path) {
            appState.activeFilePath = result.path;
            appState.activeFolder = folderFromPath(result.path);
        }
    }
}

function handleFolderSelection(event) {
    const button = event.target.closest("[data-folder]");
    if (!button) {
        return;
    }

    appState.activeFolder = button.dataset.folder || FOLDER_ALL;
    if (appState.data?.files) {
        renderFiles(appState.data.files);
    }
}

async function handleFileListClick(event) {
    const actionButton = event.target.closest("[data-action]");
    if (!actionButton) {
        return;
    }

    const action = actionButton.dataset.action;
    const path = actionButton.dataset.path;
    if (!path) {
        return;
    }

    if (action === "view") {
        const result = await performAction(`/api/files/${encodeURIComponent(path.slice(1))}`, { method: "GET" });
        if (result?.ok && result.file) {
            appState.activeFilePath = result.file.path;
            appState.activeFolder = result.file.folder;
            renderFileViewer(result.file);
        }
        return;
    }

    if (action === "edit") {
        startFileEdit(path);
        return;
    }

    if (action === "delete") {
        if (!window.confirm(`Delete file "${path}"?`)) {
            return;
        }
        const result = await performAction(`/api/files/${encodeURIComponent(path.slice(1))}`, { method: "DELETE" });
        if (result?.ok && appState.activeFilePath === path) {
            appState.activeFilePath = null;
            renderFileViewer(null);
        }
    }
}

async function handlePrintJobSubmit(event) {
    event.preventDefault();

    const result = await performAction("/api/printer/jobs", {
        method: "POST",
        body: {
            document_name: elements.printNameInput.value.trim(),
            source: elements.printSourceSelect.value,
            content: elements.printContentInput.value,
        },
    });

    if (result?.ok) {
        elements.printJobForm.reset();
    }
}

async function handleGameSubmit(event) {
    event.preventDefault();
    const result = await performAction("/api/game/guess", {
        method: "POST",
        body: { guess: elements.gameGuessInput.value },
    });
    if (result?.ok) {
        elements.gameGuessInput.value = "";
    }
}

async function applySchedulerConfiguration(source) {
    const controls = readSchedulerControls(source);
    openWindow("scheduler");
    await performAction("/api/scheduler/config", {
        method: "POST",
        body: controls,
    });
}

function readSchedulerControls(source) {
    if (source === "settings") {
        return {
            algorithm: elements.settingsAlgorithmSelect.value,
            time_quantum: Number(elements.settingsQuantumInput.value) || 2,
            queue_quantums: elements.settingsQueueQuantumInput.value,
            memory_mode: elements.settingsMemoryModeSelect.value,
        };
    }

    return {
        algorithm: elements.algorithmSelect.value,
        time_quantum: Number(elements.quantumInput.value) || 2,
        queue_quantums: elements.queueQuantumInput.value,
        memory_mode: elements.memoryModeSelect.value,
    };
}

function runBootSequence() {
    let progress = 0;
    const timer = window.setInterval(() => {
        progress = Math.min(progress + 8, 100);
        elements.bootProgressBar.style.width = `${progress}%`;
        if (progress >= 100) {
            window.clearInterval(timer);
            appState.bootReady = true;
            elements.enterDesktopBtn.disabled = false;
            setSystemMessage("Boot sequence complete. Enter the desktop shell.", "success");
        }
    }, 120);
}

function enterDesktop() {
    if (!appState.bootReady) {
        return;
    }

    elements.bootScreen.classList.add("hidden");

    if (!appState.desktopEntered) {
        appState.desktopEntered = true;
        DEFAULT_OPEN_APPS.forEach((appId) => openWindow(appId));
        focusWindow(DEFAULT_OPEN_APPS.at(-1) || "system");
        setSystemMessage("Desktop ready. Launch apps from the icons or taskbar.", "info");
    }
}

function openWindow(appId) {
    const windowState = appState.windows[appId];
    const windowElement = getWindowElement(appId);
    if (!windowState || !windowElement) {
        return;
    }

    windowState.open = true;
    windowState.minimized = false;
    if (!windowState.bounds) {
        windowState.bounds = createDefaultBounds(APP_LOOKUP[appId], APP_DEFINITIONS.findIndex((app) => app.id === appId));
    }

    applyWindowLayout(appId);
    focusWindow(appId);
    renderTaskbarApps();
    renderDesktopIcons();
    setStartMenuVisible(false);
}

function closeWindow(appId) {
    const windowState = appState.windows[appId];
    const windowElement = getWindowElement(appId);
    if (!windowState || !windowElement) {
        return;
    }

    windowState.open = false;
    windowState.minimized = false;
    windowState.maximized = false;
    windowElement.classList.remove("open", "minimized", "maximized", "active");
    windowElement.style.zIndex = "0";

    if (appState.activeApp === appId) {
        appState.activeApp = null;
        focusHighestWindow();
    }

    renderTaskbarApps();
    renderDesktopIcons();
}

function minimizeWindow(appId) {
    const windowState = appState.windows[appId];
    if (!windowState || !windowState.open) {
        return;
    }

    windowState.minimized = true;
    applyWindowLayout(appId);

    if (appState.activeApp === appId) {
        appState.activeApp = null;
        focusHighestWindow();
    } else {
        renderTaskbarApps();
    }
}

function restoreWindow(appId) {
    const windowState = appState.windows[appId];
    if (!windowState) {
        return;
    }

    windowState.open = true;
    windowState.minimized = false;
    applyWindowLayout(appId);
    focusWindow(appId);
}

function toggleMaximizeWindow(appId) {
    const windowState = appState.windows[appId];
    if (!windowState) {
        return;
    }

    if (!windowState.open) {
        openWindow(appId);
    }

    if (windowState.maximized) {
        windowState.maximized = false;
        if (windowState.restoreBounds) {
            windowState.bounds = { ...windowState.restoreBounds };
        }
    } else {
        windowState.restoreBounds = { ...windowState.bounds };
        windowState.maximized = true;
    }

    applyWindowLayout(appId);
    focusWindow(appId);
}

function focusWindow(appId) {
    const windowState = appState.windows[appId];
    if (!windowState || !windowState.open || windowState.minimized) {
        return;
    }

    appState.zCounter += 1;
    windowState.z = appState.zCounter;
    appState.activeApp = appId;

    APP_DEFINITIONS.forEach((app) => {
        const appWindow = getWindowElement(app.id);
        const state = appState.windows[app.id];
        if (!appWindow || !state) {
            return;
        }
        appWindow.classList.toggle("active", app.id === appId && state.open && !state.minimized);
        appWindow.style.zIndex = String(state.z || 0);
    });

    renderTaskbarApps();
    renderDesktopIcons();
}

function focusHighestWindow() {
    const candidate = APP_DEFINITIONS
        .map((app) => ({ appId: app.id, state: appState.windows[app.id] }))
        .filter(({ state }) => state?.open && !state.minimized)
        .sort((left, right) => (right.state.z || 0) - (left.state.z || 0))[0];

    if (candidate) {
        focusWindow(candidate.appId);
        return;
    }

    appState.activeApp = null;
    renderTaskbarApps();
    renderDesktopIcons();
}

function applyWindowLayout(appId) {
    const windowElement = getWindowElement(appId);
    const windowState = appState.windows[appId];
    if (!windowElement || !windowState) {
        return;
    }

    windowElement.classList.toggle("open", windowState.open);
    windowElement.classList.toggle("minimized", windowState.minimized);
    windowElement.classList.toggle("maximized", windowState.maximized);
    windowElement.classList.toggle("active", appState.activeApp === appId && windowState.open && !windowState.minimized);
    windowElement.style.zIndex = String(windowState.z || 0);

    if (!windowState.open) {
        return;
    }

    if (windowState.maximized) {
        const desktopBounds = getDesktopBounds();
        windowElement.style.left = `${desktopBounds.left}px`;
        windowElement.style.top = `${desktopBounds.top}px`;
        windowElement.style.width = `${desktopBounds.width}px`;
        windowElement.style.height = `${desktopBounds.height}px`;
        return;
    }

    windowState.bounds = clampBounds(windowState.bounds);
    windowElement.style.left = `${windowState.bounds.x}px`;
    windowElement.style.top = `${windowState.bounds.y}px`;
    windowElement.style.width = `${windowState.bounds.width}px`;
    windowElement.style.height = `${windowState.bounds.height}px`;
}

function handleViewportResize() {
    syncShellViewportMetrics();
    APP_DEFINITIONS.forEach((app, index) => {
        const windowState = appState.windows[app.id];
        if (!windowState) {
            return;
        }

        if (!windowState.bounds) {
            windowState.bounds = createDefaultBounds(app, index);
        } else {
            windowState.bounds = clampBounds(windowState.bounds);
        }

        applyWindowLayout(app.id);
    });
}

function createDefaultBounds(app, index) {
    const desktopBounds = getDesktopBounds();
    const width = Math.min(app.width, desktopBounds.width - 20);
    const height = Math.min(app.height, desktopBounds.height - 20);
    const x = desktopBounds.left + 56 + (index % 4) * 34;
    const y = desktopBounds.top + 34 + (index % 4) * 28;
    return clampBounds({ x, y, width, height });
}

function clampBounds(bounds) {
    const desktopBounds = getDesktopBounds();
    const minimumWidth = Math.min(320, desktopBounds.width);
    const minimumHeight = Math.min(240, desktopBounds.height);
    const width = Math.max(minimumWidth, Math.min(bounds.width, desktopBounds.width));
    const height = Math.max(minimumHeight, Math.min(bounds.height, desktopBounds.height));
    const maxX = desktopBounds.left + desktopBounds.width - width;
    const maxY = desktopBounds.top + desktopBounds.height - height;

    return {
        x: Math.min(Math.max(bounds.x, desktopBounds.left), maxX),
        y: Math.min(Math.max(bounds.y, desktopBounds.top), maxY),
        width,
        height,
    };
}

function getDesktopBounds() {
    const viewportWidth = Math.round(window.visualViewport?.width || window.innerWidth);
    const viewportHeight = Math.round(window.visualViewport?.height || window.innerHeight);
    const shellEdge = 12;
    const taskbarOffset = viewportWidth <= 760 ? 8 : 12;
    const taskbarHeight = elements.taskbar?.offsetHeight || 56;
    const safeBottom = taskbarHeight + taskbarOffset + 8;

    return {
        left: shellEdge,
        top: shellEdge,
        width: Math.max(300, viewportWidth - shellEdge * 2),
        height: Math.max(220, viewportHeight - shellEdge - safeBottom),
    };
}

function syncShellViewportMetrics() {
    const taskbarHeight = elements.taskbar?.offsetHeight || 56;
    document.documentElement.style.setProperty("--taskbar-live-height", `${taskbarHeight}px`);
}

function getWindowElement(appId) {
    return document.getElementById(`window-${appId}`);
}

function renderDesktopIcons() {
    elements.desktopIcons.innerHTML = APP_DEFINITIONS
        .map((app) => {
            const state = appState.windows[app.id];
            const status = state?.open ? (state.minimized ? "Minimized" : "Open") : "Closed";
            const classes = [
                "desktop-icon",
                state?.open ? "open" : "",
                appState.activeApp === app.id ? "active" : "",
            ]
                .filter(Boolean)
                .join(" ");

            return `
                <button class="${classes}" type="button" data-app="${escapeAttribute(app.id)}" title="${escapeAttribute(app.title)}">
                    <span class="desktop-icon-glyph">${escapeHtml(app.icon)}</span>
                    <span class="desktop-icon-label">${escapeHtml(app.title)}<br>${escapeHtml(status)}</span>
                </button>
            `;
        })
        .join("");
}

function renderStartMenuApps() {
    elements.startMenuApps.innerHTML = APP_DEFINITIONS
        .map(
            (app) => `
                <button class="start-app-button" type="button" data-app="${escapeAttribute(app.id)}">
                    <span class="window-app-icon">${escapeHtml(app.icon)}</span>
                    <span>
                        <strong>${escapeHtml(app.title)}</strong>
                        <span>${escapeHtml(app.subtitle)}</span>
                    </span>
                </button>
            `
        )
        .join("");
}

function renderTaskbarApps() {
    const openApps = APP_DEFINITIONS.filter((app) => appState.windows[app.id]?.open);

    if (!openApps.length) {
        elements.taskbarApps.innerHTML = `<span class="tray-message">No application windows are open.</span>`;
        syncShellViewportMetrics();
        APP_DEFINITIONS.forEach((app) => {
            if (appState.windows[app.id]?.open) {
                applyWindowLayout(app.id);
            }
        });
        return;
    }

    elements.taskbarApps.innerHTML = openApps
        .map((app) => {
            const state = appState.windows[app.id];
            const classes = [
                "taskbar-app",
                appState.activeApp === app.id && !state.minimized ? "active" : "",
                state.minimized ? "minimized" : "",
            ]
                .filter(Boolean)
                .join(" ");

            return `
                <button class="${classes}" type="button" data-app="${escapeAttribute(app.id)}">
                    <span class="window-app-icon">${escapeHtml(app.icon)}</span>
                    <span>${escapeHtml(app.title)}</span>
                </button>
            `;
        })
        .join("");

    syncShellViewportMetrics();
    APP_DEFINITIONS.forEach((app) => {
        if (appState.windows[app.id]?.open) {
            applyWindowLayout(app.id);
        }
    });
}

function renderWallpaperOptions() {
    const markup = WALLPAPERS
        .map(
            (wallpaper) => `
                <button class="wallpaper-option" type="button" data-wallpaper="${escapeAttribute(wallpaper.id)}">
                    <span class="wallpaper-preview ${escapeAttribute(wallpaper.preview)}"></span>
                    <strong>${escapeHtml(wallpaper.name)}</strong>
                    <span class="file-meta">${escapeHtml(wallpaper.detail)}</span>
                </button>
            `
        )
        .join("");

    elements.wallpaperOptions.innerHTML = markup;
    elements.startWallpaperChoices.innerHTML = markup;
    updateWallpaperSelectionState();
}

function handleWallpaperSelection(event) {
    const button = event.target.closest("[data-wallpaper]");
    if (!button) {
        return;
    }

    applyWallpaperPreference(button.dataset.wallpaper, true);
}

function applyWallpaperPreference(wallpaperId, announce) {
    const selected = WALLPAPERS.find((wallpaper) => wallpaper.id === wallpaperId) || WALLPAPERS[0];
    appState.wallpaperId = selected.id;

    document.body.classList.remove(...ALL_WALLPAPER_CLASSES);
    elements.desktopShell.classList.remove(...ALL_WALLPAPER_CLASSES);
    document.body.classList.add(selected.id);
    elements.desktopShell.classList.add(selected.id);
    elements.desktopWallpaperLabel.textContent = selected.name;
    storePreference("wallpaper", selected.id);
    updateWallpaperSelectionState();

    if (announce) {
        setSystemMessage(`Wallpaper changed to ${selected.name}.`, "info");
        setStartMenuVisible(false);
    }
}

function updateWallpaperSelectionState() {
    document.querySelectorAll("[data-wallpaper]").forEach((button) => {
        button.classList.toggle("active", button.dataset.wallpaper === appState.wallpaperId);
    });
}

function applyReducedMotionPreference(enabled, announce) {
    appState.reducedMotion = Boolean(enabled);
    document.body.classList.toggle("reduced-motion", appState.reducedMotion);
    elements.animationToggle.checked = appState.reducedMotion;
    storePreference("reduced_motion", appState.reducedMotion ? "1" : "0");

    if (announce) {
        setSystemMessage(
            appState.reducedMotion ? "Reduced motion enabled." : "Desktop motion restored.",
            "info"
        );
    }
}

function setStartMenuVisible(visible) {
    elements.startMenu.hidden = !visible;
    syncShellViewportMetrics();
}

function startClock() {
    updateClock();
    window.setInterval(updateClock, 1000);
}

function updateClock() {
    const now = new Date();
    elements.liveClock.textContent = now.toLocaleTimeString([], { hour12: false });
}

async function loadState() {
    try {
        const response = await apiRequest("/api/state", { method: "GET" });
        renderDesktop(response.state);
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
            renderDesktop(response.state);
        }
        if (response.file) {
            appState.activeFilePath = response.file.path;
            appState.activeFolder = response.file.folder;
            renderFileViewer(response.file);
        }
        if (response.path) {
            appState.activeFilePath = response.path;
            appState.activeFolder = folderFromPath(response.path);
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

function renderDesktop(state) {
    appState.data = state;
    document.title = state.shell?.name ? `${state.shell.name} :: Simple Operating System Simulator` : document.title;
    elements.activeAlgorithmLabel.textContent = state.scheduler.algorithm_label;
    elements.stepCounter.textContent = `${state.demo.step_index} / ${state.demo.total_steps}`;

    populateSchedulerControls(state.scheduler);
    renderHeroStats(state);
    renderSummary(state);
    renderProcesses(state.processes);
    renderScheduler(state);
    renderMemory(state.memory);
    renderDisk(state.disk);
    renderFiles(state.files);
    renderPrinter(state.printer, state.processes);
    renderGame(state.game);
    syncActiveFile();
    updateActionStates();
}

function populateSchedulerControls(scheduler) {
    populateSelectFromMap(elements.algorithmSelect, scheduler.algorithms, scheduler.algorithm);
    populateSelectFromMap(elements.settingsAlgorithmSelect, scheduler.algorithms, scheduler.algorithm);
    elements.quantumInput.value = scheduler.time_quantum;
    elements.settingsQuantumInput.value = scheduler.time_quantum;
    elements.queueQuantumInput.value = scheduler.queue_quantums.join(",");
    elements.settingsQueueQuantumInput.value = scheduler.queue_quantums.join(",");
    elements.memoryModeSelect.value = scheduler.memory_mode;
    elements.settingsMemoryModeSelect.value = scheduler.memory_mode;
}

function populateSelectFromMap(selectElement, items, selectedValue) {
    const currentValue = selectElement.value;
    selectElement.innerHTML = Object.entries(items)
        .map(([value, label]) => `<option value="${escapeAttribute(value)}">${escapeHtml(label)}</option>`)
        .join("");
    selectElement.value = selectedValue || currentValue || Object.keys(items)[0];
}

function renderHeroStats(state) {
    const currentProcess = state.current_process ? `P${state.current_process.pid}` : "Idle";
    const cards = [
        {
            label: "Shell Clock",
            value: `t=${state.clock}`,
            detail: state.shell?.build || "Academic Desktop Shell",
        },
        {
            label: "Active Dispatch",
            value: currentProcess,
            detail: state.current_process?.name || state.last_event || "Waiting for next action",
        },
        {
            label: "Memory Load",
            value: `${state.memory.used_memory}/${state.memory.total_memory} MB`,
            detail: state.memory.mode_label,
        },
        {
            label: "Storage + I/O",
            value: `${state.files.count} files / ${state.printer.pending_count} jobs`,
            detail: `${state.disk.storage.used_blocks}/${state.disk.storage.total_blocks} blocks in use`,
        },
    ];

    elements.heroStats.innerHTML = cards.map(metricCardMarkup).join("");
}

function renderSummary(state) {
    const cards = [
        { label: "Average Waiting", value: state.stats.average_waiting_time, detail: "time units" },
        { label: "Average Turnaround", value: state.stats.average_turnaround_time, detail: "time units" },
        { label: "Throughput", value: state.stats.throughput, detail: "completed per time unit" },
        {
            label: "Last Scheduler Event",
            value: state.demo.blocked ? "Blocked" : "Online",
            detail: state.last_event || "No scheduler event recorded yet.",
        },
    ];

    elements.summaryStats.innerHTML = cards.map(metricCardMarkup).join("");

    if (!state.activity_log.length) {
        elements.activityFeed.innerHTML = `<div class="activity-item">No activity recorded yet.</div>`;
        return;
    }

    elements.activityFeed.innerHTML = state.activity_log
        .slice()
        .reverse()
        .map(
            (entry) => `
                <article class="activity-item">
                    <div class="activity-time">t=${entry.clock} | ${escapeHtml(entry.timestamp)}</div>
                    <div class="activity-message">${escapeHtml(entry.message)}</div>
                </article>
            `
        )
        .join("");
}

function renderProcesses(processes) {
    if (!processes.length) {
        elements.processTableBody.innerHTML = `<tr><td colspan="13">No processes loaded.</td></tr>`;
        return;
    }

    elements.processTableBody.innerHTML = processes
        .map(
            (process) => `
                <tr>
                    <td>P${process.pid}</td>
                    <td>${escapeHtml(process.name)}</td>
                    <td>${process.arrival_time}</td>
                    <td>${process.burst_time}</td>
                    <td>${process.remaining_time}</td>
                    <td>${process.priority}</td>
                    <td>${process.memory_requirement} MB</td>
                    <td><span class="state-badge ${stateClass(process.state)}">${escapeHtml(process.state)}</span></td>
                    <td>${process.waiting_time}</td>
                    <td>${process.turnaround_time}</td>
                    <td>${process.completion_time ?? "-"}</td>
                    <td><span class="table-pill">${escapeHtml(process.partition_label || "Unassigned")}</span></td>
                    <td>
                        <div class="button-row">
                            <button class="button ghost-button small-button" type="button" data-action="edit" data-pid="${process.pid}">Edit</button>
                            <button class="button ghost-button small-button" type="button" data-action="delete" data-pid="${process.pid}">Delete</button>
                        </div>
                    </td>
                </tr>
            `
        )
        .join("");
}

function renderScheduler(state) {
    renderReadyQueues(state.ready_queues);
    renderTokenRow(elements.executionOrder, state.execution_order);

    const currentProcess = state.current_process
        ? `P${state.current_process.pid} :: ${state.current_process.name}`
        : state.demo.blocked
          ? "Memory blocked"
          : "CPU idle";

    const cards = [
        {
            label: "Algorithm",
            value: state.scheduler.algorithm_label,
            detail: state.scheduler.memory_mode_label,
        },
        {
            label: "Current Dispatch",
            value: currentProcess,
            detail: `${state.stats.running_count} running | ${state.stats.ready_count} ready`,
        },
        {
            label: "Average Waiting",
            value: state.stats.average_waiting_time,
            detail: "time units",
        },
        {
            label: "Average Turnaround",
            value: state.stats.average_turnaround_time,
            detail: "time units",
        },
        {
            label: "Last Event",
            value: state.demo.blocked ? "Blocked" : "Active",
            detail: state.last_event || "No event recorded yet.",
        },
    ];

    elements.schedulerHighlights.innerHTML = cards.map(metricCardMarkup).join("");

    if (!state.gantt_segments.length) {
        elements.ganttChart.innerHTML = `<span class="empty-chip">Run the scheduler to build a Gantt chart.</span>`;
        elements.ganttTimes.innerHTML = "";
        return;
    }

    elements.ganttChart.innerHTML = state.gantt_segments
        .map(
            (segment) => `
                <article class="gantt-segment ${escapeAttribute(segment.css_class)}" style="--duration:${segment.duration}">
                    <div class="gantt-label">${escapeHtml(segment.label)}</div>
                    <div class="gantt-meta">${escapeHtml(segment.process_name)}<br>t=${segment.start} to t=${segment.end}</div>
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

function renderReadyQueues(queues) {
    if (!queues.length) {
        elements.readyQueues.innerHTML = `<span class="empty-chip">No ready queue data.</span>`;
        return;
    }

    elements.readyQueues.innerHTML = queues
        .map(
            (queue) => `
                <article class="subpanel">
                    <div class="subpanel-header">
                        <h3>${escapeHtml(queue.label)}</h3>
                        <span class="mini-label">${queue.items.length} item(s)</span>
                    </div>
                    <div class="token-row">
                        ${
                            queue.items.length
                                ? queue.items
                                      .map(
                                          (item) => `<span class="token">${escapeHtml(item.label)} :: ${escapeHtml(item.name)} | r=${item.remaining_time}</span>`
                                      )
                                      .join("")
                                : `<span class="empty-chip">Queue is empty.</span>`
                        }
                    </div>
                </article>
            `
        )
        .join("");
}

function renderMemory(memory) {
    const cards = [
        { label: "Mode", value: memory.mode_label, detail: `${memory.used_regions}/${memory.total_regions} regions allocated` },
        { label: "Used Memory", value: `${memory.used_memory} MB`, detail: `${memory.free_memory} MB free` },
        { label: "Largest Free Block", value: `${memory.fragmentation.largest_free_block} MB`, detail: "largest available region" },
        { label: "Fragmentation", value: `I:${memory.fragmentation.internal} / E:${memory.fragmentation.external}`, detail: "educational indicator" },
    ];

    elements.memoryStats.innerHTML = cards.map(metricCardMarkup).join("");
    elements.memoryPartitions.innerHTML = memory.regions
        .map(
            (region) => `
                <article class="partition-card">
                    <div class="partition-header">
                        <div>
                            <div class="partition-title">${escapeHtml(region.label)}</div>
                            <div class="partition-size">${region.size} MB capacity</div>
                        </div>
                        <span class="state-badge ${region.occupied ? "running" : "waiting"}">${region.occupied ? "Allocated" : "Free"}</span>
                    </div>
                    <div class="memory-bar">
                        <div class="memory-fill" style="width:${Math.max(region.usage_percent || 0, region.occupied ? 18 : 2)}%"></div>
                    </div>
                    <div class="memory-meta">
                        <span>${region.process ? `P${region.process.pid} :: ${escapeHtml(region.process.name)}` : "Available region"}</span>
                        <span>Used: ${region.used_memory} MB</span>
                        <span>Free: ${region.free_space} MB</span>
                    </div>
                </article>
            `
        )
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

function renderDisk(disk) {
    const storage = disk.storage;
    const schedule = disk.schedule;

    if (disk.algorithms) {
        populateSelectFromMap(elements.diskAlgorithmSelect, disk.algorithms, schedule.algorithm);
    }
    elements.diskHeadInput.value = schedule.head_position;
    elements.diskDirectionSelect.value = schedule.direction || "up";
    if (!elements.diskRequestsInput.value || document.activeElement !== elements.diskRequestsInput) {
        elements.diskRequestsInput.value = schedule.requests.join(", ");
    }

    const cards = [
        { label: "Used Blocks", value: `${storage.used_blocks}/${storage.total_blocks}`, detail: `${storage.free_blocks} free blocks` },
        { label: "Block Size", value: `${storage.block_size} chars`, detail: "educational storage unit" },
        { label: "Disk Algorithm", value: schedule.algorithm_label, detail: `Head @ ${schedule.head_position}` },
        { label: "Head Movement", value: schedule.total_head_movement, detail: "total cylinders moved" },
    ];

    elements.diskStorageStats.innerHTML = cards.map(metricCardMarkup).join("");
    elements.diskScheduleResult.innerHTML = `
        <article class="list-card">
            <div class="list-card-header">
                <div>
                    <strong>${escapeHtml(schedule.algorithm_label)}</strong>
                    <div class="file-meta">Direction: ${escapeHtml(schedule.direction)}</div>
                </div>
                <span class="queue-chip running">Active</span>
            </div>
            <div class="memory-meta">
                <span>Requests: ${escapeHtml(schedule.requests.join(", ") || "None")}</span>
                <span>Service Order: ${escapeHtml(schedule.service_order.join(" -> ") || "None")}</span>
                <span>Path: ${escapeHtml(schedule.path.join(" -> "))}</span>
                <span>Total Head Movement: ${schedule.total_head_movement}</span>
            </div>
        </article>
    `;

    elements.diskBlockMap.innerHTML = storage.block_map
        .map(
            (block) => `
                <div class="block-cell ${block.occupied ? "occupied" : ""}" title="${escapeAttribute(block.owner || "Free block")}">
                    ${block.index}
                </div>
            `
        )
        .join("");
}

function renderFiles(files) {
    const items = files.items.slice().sort((left, right) => {
        if (left.folder !== right.folder) {
            return left.folder.localeCompare(right.folder);
        }
        return left.name.localeCompare(right.name);
    });
    const folders = [...new Set(items.map((file) => file.folder))];

    if (appState.activeFolder !== FOLDER_ALL && !folders.includes(appState.activeFolder)) {
        appState.activeFolder = FOLDER_ALL;
    }

    renderFolderSidebar(folders, items);

    const visibleFiles = appState.activeFolder === FOLDER_ALL
        ? items
        : items.filter((file) => file.folder === appState.activeFolder);

    if (!visibleFiles.length) {
        elements.fileList.innerHTML = `<span class="empty-chip">No files stored in this folder.</span>`;
        return;
    }

    const blockLookup = new Map(
        (appState.data?.disk?.storage?.files || []).map((file) => [file.path, file.block_count])
    );

    elements.fileList.innerHTML = visibleFiles
        .map(
            (file) => `
                <article class="list-card">
                    <div class="list-card-header">
                        <div>
                            <strong>${escapeHtml(file.name)}</strong>
                            <div class="file-meta">
                                ${escapeHtml(file.folder)} | ${file.size} chars | ${blockLookup.get(file.path) || 0} block(s)
                            </div>
                            <div class="file-meta">Updated ${escapeHtml(file.updated_at)}</div>
                        </div>
                        <span class="queue-chip ready">Stored</span>
                    </div>
                    <div class="list-card-actions">
                        <button class="button ghost-button small-button" type="button" data-action="view" data-path="${escapeAttribute(file.path)}">View</button>
                        <button class="button ghost-button small-button" type="button" data-action="edit" data-path="${escapeAttribute(file.path)}">Edit</button>
                        <button class="button ghost-button small-button" type="button" data-action="delete" data-path="${escapeAttribute(file.path)}">Delete</button>
                    </div>
                </article>
            `
        )
        .join("");
}

function renderFolderSidebar(folders, items) {
    const folderButtons = [
        {
            key: FOLDER_ALL,
            label: `All Files (${items.length})`,
        },
        ...folders.map((folder) => ({
            key: folder,
            label: `${folder} (${items.filter((file) => file.folder === folder).length})`,
        })),
    ];

    elements.folderSidebar.innerHTML = folderButtons
        .map(
            (folder) => `
                <button
                    class="folder-button ${appState.activeFolder === folder.key ? "active" : ""}"
                    type="button"
                    data-folder="${escapeAttribute(folder.key)}"
                >
                    ${escapeHtml(folder.label)}
                </button>
            `
        )
        .join("");
}

function syncActiveFile() {
    const activeFile = (appState.data?.files?.items || []).find((file) => file.path === appState.activeFilePath);
    renderFileViewer(activeFile || null);
}

function renderFileViewer(file) {
    if (!file) {
        elements.viewerLabel.textContent = "Select a file";
        elements.fileViewer.textContent = "Select a file from the list to display its contents.";
        return;
    }

    elements.viewerLabel.textContent = file.path;
    elements.fileViewer.textContent = file.content;
}

function renderPrinter(printer, processes) {
    const sources = ["Control Center", ...processes.map((process) => `P${process.pid} :: ${process.name}`)];
    const previousSource = elements.printSourceSelect.value || "Control Center";
    elements.printSourceSelect.innerHTML = sources
        .map((source) => `<option value="${escapeAttribute(source)}">${escapeHtml(source)}</option>`)
        .join("");
    elements.printSourceSelect.value = sources.includes(previousSource) ? previousSource : "Control Center";

    elements.printerQueue.innerHTML = printer.queue.length
        ? printer.queue
              .map(
                  (job, index) => `
                      <article class="queue-item">
                          <div class="queue-item-header">
                              <strong>${index + 1}. ${escapeHtml(job.name)}</strong>
                              <span class="queue-chip waiting">Queued</span>
                          </div>
                          <div class="queue-meta">Source: ${escapeHtml(job.source)} | Size: ${job.size} chars | ${escapeHtml(job.created_at)}</div>
                      </article>
                  `
              )
              .join("")
        : `<span class="empty-chip">No pending print jobs.</span>`;

    elements.completedPrintJobs.innerHTML = printer.completed_jobs.length
        ? printer.completed_jobs
              .slice()
              .reverse()
              .map(
                  (job) => `
                      <article class="queue-item">
                          <div class="queue-item-header">
                              <strong>${escapeHtml(job.name)}</strong>
                              <span class="queue-chip running">Printed</span>
                          </div>
                          <div class="queue-meta">Source: ${escapeHtml(job.source)} | Size: ${job.size} chars</div>
                      </article>
                  `
              )
              .join("")
        : `<span class="empty-chip">No completed print jobs yet.</span>`;
}

function renderGame(game) {
    elements.gameMessage.textContent = game.message;
    elements.gameHistory.innerHTML = game.history.length
        ? game.history
              .slice()
              .reverse()
              .map(
                  (attempt) => `
                      <article class="queue-item">
                          <div class="queue-item-header">
                              <strong>Attempt ${attempt.attempt}</strong>
                              <span class="queue-chip ${attempt.hint === "Correct" ? "running" : "waiting"}">${escapeHtml(attempt.hint)}</span>
                          </div>
                          <div class="queue-meta">Guess: ${attempt.guess}</div>
                      </article>
                  `
              )
              .join("")
        : `<span class="empty-chip">No guesses yet.</span>`;
}

function renderTokenRow(container, items) {
    if (!items.length) {
        container.innerHTML = `<span class="empty-chip">No entries yet.</span>`;
        return;
    }
    container.innerHTML = items.map((item) => `<span class="token">${escapeHtml(item)}</span>`).join("");
}

function metricCardMarkup(card) {
    return `
        <article class="metric-card">
            <div class="metric-label">${escapeHtml(card.label)}</div>
            <div class="metric-value">${escapeHtml(String(card.value))}</div>
            <div class="metric-detail">${escapeHtml(card.detail)}</div>
        </article>
    `;
}

function startProcessEdit(pid) {
    const process = (appState.data?.processes || []).find((item) => item.pid === pid);
    if (!process) {
        return;
    }

    openWindow("process");
    elements.processPidInput.value = process.pid;
    elements.processNameInput.value = process.name;
    elements.processArrivalInput.value = process.arrival_time;
    elements.processBurstInput.value = process.burst_time;
    elements.processPriorityInput.value = process.priority;
    elements.processMemoryInput.value = process.memory_requirement;
    elements.processSubmitBtn.textContent = "Update Process";
}

function resetProcessForm() {
    elements.processForm.reset();
    elements.processPidInput.value = "";
    elements.processArrivalInput.value = "0";
    elements.processBurstInput.value = "4";
    elements.processPriorityInput.value = "3";
    elements.processMemoryInput.value = "64";
    elements.processSubmitBtn.textContent = "Add Process";
}

function startFileEdit(path) {
    const file = (appState.data?.files?.items || []).find((item) => item.path === path);
    if (!file) {
        return;
    }

    openWindow("files");
    appState.activeFilePath = file.path;
    appState.activeFolder = file.folder;
    elements.fileOriginalPathInput.value = file.path;
    elements.fileFolderInput.value = file.folder;
    elements.fileNameInput.value = file.name;
    elements.fileContentInput.value = file.content;
    elements.fileSubmitBtn.textContent = "Update File";
    renderFileViewer(file);
}

function resetFileForm() {
    elements.fileForm.reset();
    elements.fileOriginalPathInput.value = "";
    elements.fileFolderInput.value = "/docs";
    elements.fileSubmitBtn.textContent = "Create File";
}

async function toggleDemoMode() {
    openWindow("scheduler");

    if (appState.demoTimer) {
        stopDemo("Auto demo paused.");
        return;
    }

    if (!appState.data || !appState.data.demo.can_step) {
        const resetResult = await performAction("/api/scheduler/reset", { method: "POST" });
        if (!resetResult?.ok) {
            return;
        }
    }

    appState.demoTimer = window.setInterval(runDemoStep, 900);
    elements.demoBtn.textContent = "Pause Demo";
    setSystemMessage("Auto demo is stepping through the current schedule.", "info");
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

    if (!result.state.demo.can_step) {
        stopDemo(
            result.state.demo.blocked
                ? "Auto demo stopped because the simulation is blocked."
                : "Auto demo finished."
        );
    }
}

function stopDemo(message = "") {
    if (appState.demoTimer) {
        window.clearInterval(appState.demoTimer);
        appState.demoTimer = null;
    }

    elements.demoBtn.textContent = "Auto Demo";
    updateActionStates();
    if (message) {
        setSystemMessage(message, "info");
    }
}

function updateActionStates() {
    const demoRunning = Boolean(appState.demoTimer);
    const state = appState.data;
    const busyOrDemo = appState.busy || demoRunning;

    elements.applySchedulerBtn.disabled = busyOrDemo;
    elements.settingsApplySchedulerBtn.disabled = busyOrDemo;
    elements.resetBtn.disabled = appState.busy;
    elements.startResetSystemBtn.disabled = appState.busy;
    elements.loadSampleBtn.disabled = busyOrDemo;
    elements.startLoadSampleBtn.disabled = busyOrDemo;
    elements.settingsLoadSampleBtn.disabled = busyOrDemo;
    elements.generateSampleBtn.disabled = busyOrDemo;
    elements.resetProcessRuntimeBtn.disabled = busyOrDemo;
    elements.resetScheduleBtn.disabled = appState.busy;
    elements.stepBtn.disabled = busyOrDemo || !state?.demo?.can_step;
    elements.runBtn.disabled = busyOrDemo || !state;
    elements.demoBtn.disabled = appState.busy || !state;
    elements.processSubmitBtn.disabled = appState.busy;
    elements.processCancelBtn.disabled = appState.busy;
    elements.fileSubmitBtn.disabled = appState.busy;
    elements.fileCancelBtn.disabled = appState.busy;
    elements.runDiskBtn.disabled = appState.busy;
    elements.printSubmitBtn.disabled = appState.busy;
    elements.processPrintBtn.disabled = appState.busy || !state?.printer?.pending_count;
    elements.gameGuessBtn.disabled = appState.busy;
    elements.gameResetBtn.disabled = appState.busy;
}

function setSystemMessage(message, tone = "info") {
    elements.systemMessage.textContent = message;
    elements.systemMessage.dataset.tone = tone;
}

function folderFromPath(path) {
    const normalized = String(path || "").trim();
    if (!normalized || normalized === "/") {
        return "/";
    }

    const pieces = normalized.split("/").filter(Boolean);
    if (pieces.length <= 1) {
        return "/";
    }

    return `/${pieces.slice(0, -1).join("/")}`;
}

function readPreference(key, fallback) {
    try {
        return window.localStorage.getItem(key) || fallback;
    } catch (error) {
        return fallback;
    }
}

function storePreference(key, value) {
    try {
        window.localStorage.setItem(key, value);
    } catch (error) {
        return;
    }
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
