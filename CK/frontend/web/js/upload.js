// =============================================
// 🚀 UPLOAD LOGIC (Socket.IO TCP Bridge)
// =============================================

// ===== DOM Elements =====
const dropZone = document.getElementById("dropZone");
const fileInput = document.getElementById("fileInput");
const browseFile = document.getElementById("browseFile");

const startBtn = document.getElementById("startBtn");
const pauseBtn = document.getElementById("pauseBtn");
const resumeBtn = document.getElementById("resumeBtn");
const stopBtn = document.getElementById("stopBtn");

const progressBar = document.getElementById("progress");
const statusText = document.getElementById("statusText");

const visibilityEl = document.getElementById("visibility");
const tagsEl = document.getElementById("tags");
const descriptionEl = document.getElementById("description");

// ===== State Variables =====
let selectedFile = null;
let socket = null; // Đây sẽ là socket.io
let uploadState = {
    file: null,
    upload_id: null,
    offset: 0,
    chunk_size: 65536,
    isPaused: false,
    isStopped: false,
};

// =============================================
// 🎨 UI & Drag/Drop Events
// =============================================
dropZone.addEventListener("dragover", (e) => { e.preventDefault(); dropZone.classList.add("dragover"); });
dropZone.addEventListener("dragleave", () => dropZone.classList.remove("dragover"));
dropZone.addEventListener("drop", (e) => { e.preventDefault(); dropZone.classList.remove("dragover"); handleFileSelect(e.dataTransfer.files[0]); });
browseFile.addEventListener("click", () => fileInput.click());
fileInput.addEventListener("change", (e) => handleFileSelect(e.target.files[0]));

function handleFileSelect(file) {
    if (!file) return;
    selectedFile = file;
    uploadState.upload_id = `${Date.now()}_${file.name}`;
    
    // Truncate long filenames
    const maxLength = 40;
    const displayName = file.name.length > maxLength 
        ? file.name.substring(0, maxLength - 3) + '...' 
        : file.name;
    const fileSizeMB = (file.size / 1024 / 1024).toFixed(2);
    
    dropZone.innerHTML = `
        <p style="word-break: break-word; white-space: normal; max-width: 100%; margin: 0;" title="${file.name}">
            📄 <strong>${displayName}</strong>
        </p>
        <p style="color: #999; margin-top: 8px; font-size: 14px;">${fileSizeMB} MB</p>
        <button id="changeFIle" style="margin-top: 15px; padding: 8px 20px; background: #f0f0f0; border: 1px solid #ddd; border-radius: 8px; cursor: pointer; font-size: 13px;">↩️ Chọn file khác</button>
    `;
    
    // Add event listener to change file button
    document.getElementById('changeFIle').addEventListener('click', () => fileInput.click());
    
    resetUI();
    startBtn.disabled = false;
}

// =============================================
// 🕹️ Control Button Events
// =============================================
startBtn.addEventListener("click", startUpload);
pauseBtn.addEventListener("click", () => {
    uploadState.isPaused = true;
    // Gửi lệnh pause tới server TCP (qua cầu nối)
    sendJsonMessage({ action: "pause", upload_id: uploadState.upload_id });
    setStatus("⏸️ Đang tạm dừng...", "info");
    pauseBtn.disabled = true;
    resumeBtn.disabled = false;
});
resumeBtn.addEventListener("click", () => {
    uploadState.isPaused = false;
    // Gửi lệnh resume và kích hoạt lại sendChunk
    sendJsonMessage({ action: "resume", upload_id: uploadState.upload_id });
    setStatus(`Đang tiếp tục tải... ${((uploadState.offset / uploadState.file.size) * 100).toFixed(0)}%`, "info");
    pauseBtn.disabled = false;
    resumeBtn.disabled = true;
    sendChunk(); 
});
stopBtn.addEventListener("click", () => {
    uploadState.isStopped = true;
    if (socket) {
        // Gửi lệnh stop và ngắt kết nối
        sendJsonMessage({ action: "stop", upload_id: uploadState.upload_id });
        socket.disconnect(); 
    }
    pauseBtn.disabled = true;
    stopBtn.disabled = true;
    resumeBtn.disabled = true;
    startBtn.disabled = false;
    setStatus("🚫 Đã hủy! Không tải nữa. Chọn file khác để tải lên.", "error");
});

// =============================================
// SOCKET.IO & UPLOAD LOGIC (SỬA LẠI)
// =============================================

/**
 * 1. Bắt đầu quá trình: Kết nối Socket.IO
 */
async function startUpload() {
    if (!selectedFile) { setStatus("Vui lòng chọn tệp!", "error"); return; }
    if (!isLoggedIn()) { setStatus("Vui lòng đăng nhập để upload!", "error"); return; }

    setStatus("Đang kết nối tới cầu nối...", "info");
    startBtn.disabled = true;

    // Khởi tạo trạng thái
    uploadState.file = selectedFile;
    uploadState.offset = 0;
    uploadState.isPaused = false;
    uploadState.isStopped = false;

    // Kết nối tới Socket.IO server - Dùng cùng host với API
    const host = window.location.hostname;
    const port = 5000;
    const socketUrl = `http://${host}:${port}`;
    connectToSocketIO(socketUrl);
}

/**
 * 2. Kết nối Socket.IO (thay vì WebSocket)
 */
function connectToSocketIO(url) {
    socket = io(url);

    socket.on("connect", () => {
        setStatus("✅ Kết nối thành công. Đang gửi metadata...", "info");
        sendStartMessage();
    });

    // Lắng nghe phản hồi từ server TCP (đã được chuyển tiếp)
    socket.on("tcp_response", (data) => {
        handleSocketMessage(data);
    });

    socket.on("connect_error", (err) => {
        console.error("Lỗi Socket.IO:", err);
        setStatus("Lỗi kết nối máy chủ (Socket.IO Error).", "error");
        resetUI();
    });

    socket.on("disconnect", () => {
        if (!uploadState.isStopped && uploadState.offset >= uploadState.file.size) {
            return;
        }
        if (!uploadState.isStopped) {
            setStatus("Mất kết nối máy chủ.", "error");
            resetUI();
        }
    });
}

/** Helper: Gửi tin nhắn JSON qua cầu nối */
function sendJsonMessage(obj) {
    if (socket && socket.connected) {
        socket.emit('tcp_message', obj);
    }
}

/** Helper: Gửi tin nhắn Bytes (chunk) qua cầu nối */
function sendBytes(chunk) {
    if (socket && socket.connected) {
        socket.emit('tcp_message', chunk);
    }
}

/**
 * 3. Gửi thông tin bắt đầu (Metadata)
 */
function sendStartMessage() {
    const token = localStorage.getItem("token"); 
    const tagsArray = tagsEl.value.split(',').map(t => t.trim()).filter(t => t);

    const message = {
        action: "start",
        upload_id: uploadState.upload_id,
        filename: uploadState.file.name,
        filesize: uploadState.file.size,
        chunk_size: uploadState.chunk_size,
        metadata: {
            token: token,
            description: descriptionEl.value,
            visibility: visibilityEl.value,
            tags: tagsArray
        }
    };
    sendJsonMessage(message); // Gửi qua cầu nối
}

/**
 * 4. Xử lý phản hồi từ Server (Đã chuyển tiếp qua Socket.IO)
 */
function handleSocketMessage(data) {
    if (data.status !== "ok") {
        setStatus(`Lỗi từ server: ${data.reason}`, "error");
        resetUI();
        socket.disconnect();
        return;
    }

    // Server phản hồi 'start' OK
    if (data.offset !== undefined && uploadState.offset === 0) {
        uploadState.offset = data.offset;
        uploadState.chunk_size = data.chunk_size || uploadState.chunk_size;

        setStatus("Đang bắt đầu upload...", "info");
        pauseBtn.disabled = false;
        stopBtn.disabled = false;

        sendChunk(); 
    }

    // Server phản hồi 'chunk' OK (ACK)
    else if (data.offset !== undefined) {
        updateProgress(data.offset, uploadState.file.size);
        uploadState.offset = data.offset;

        if (data.offset <Tải lên thành côngle.size) {
            sendChunk(); // Gửi chunk tiếp
        } else {
            setStatus("✅ Upload hoàn tất! Đang chuyển hướng...", "success");
            progressBar.style.width = "100%";
            resetUI();
            socket.disconnect();
            setTimeout(() => window.location.href = "documents.html", 800); 
        }
    }
}

/**
 * 5. Vòng lặp gửi Chunk (phần chính)
 */
async function sendChunk() {
    if (uploadState.isPaused || uploadState.isStopped || !socket || !socket.connected) {
        if(uploadState.isPaused) {
            setStatus("⏸ Đã tạm dừng.", "info");
            pauseBtn.disabled = true;
            resumeBtn.disabled = false;
        }
        return; 
    }

    pauseBtn.disabled = false;
    resumeBtn.disabled = true;
    setStatus(`Đang tải... ${((uploadState.offset / uploadState.file.size) * 100).toFixed(0)}%`, "info");

    const start = uploadState.offset;
    const end = Math.min(start + uploadState.chunk_size, uploadState.file.size);
    const chunk = uploadState.file.slice(start, end);
    const chunkLength = chunk.size;

    if (chunkLength === 0) {
        return;
    }

    // 1. Gửi Header (JSON)
    const header = {
        action: "chunk",
        upload_id: uploadState.upload_id,
        offset: start,
        length: chunkLength,
    };
    sendJsonMessage(header);

    // 2. Gửi Data (Binary)
    sendBytes(chunk);
}

// =Cập nhật UI
function updateProgress(loaded, total) {
    const percent = total > 0 ? (loaded / total) * 100 : 0;
    progressBar.style.width = percent + "%";
}

function setStatus(message, type = "info") {
    statusText.textContent = message;
    statusText.className = `status-text ${type}`; // info, success, error
}

function resetUI() {
    startBtn.disabled = false;
    pauseBtn.disabled = true;
    resumeBtn.disabled = true;
    stopBtn.disabled = true;
}