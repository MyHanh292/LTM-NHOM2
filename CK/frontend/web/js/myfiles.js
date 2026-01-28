// File: frontend/web/js/myfiles.js
// Manage user's uploaded documents

const API_URL = "http://127.0.0.1:5000";

// Helper function format date safely
function formatDate(dateStr) {
    if (!dateStr) return 'N/A';
    try {
        const date = new Date(dateStr);
        if (isNaN(date.getTime())) return 'N/A';
        return date.toLocaleDateString('vi-VN', { year: 'numeric', month: '2-digit', day: '2-digit' });
    } catch (e) {
        return 'N/A';
    }
}

function formatTime(dateStr) {
    if (!dateStr) return 'N/A';
    try {
        const date = new Date(dateStr);
        if (isNaN(date.getTime())) return 'N/A';
        return date.toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    } catch (e) {
        return 'N/A';
    }
}

document.addEventListener("DOMContentLoaded", () => {
    const token = localStorage.getItem("token");
    if (!token) {
        window.location.href = "login.html";
        return;
    }
    loadMyFiles(token);
});

async function loadMyFiles(token) {
    try {
        const headers = { 'Authorization': `Bearer ${token}` };
        const response = await fetch(`${API_URL}/api/documents/my-documents`, {
            method: 'GET',
            headers
        });

        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }

        const data = await response.json();
        displayMyFiles(data.documents || [], token);
    } catch (error) {
        console.error("Error loading my files:", error);
        document.getElementById("loading-text").innerHTML = "Lỗi tải dữ liệu: " + error.message;
    }
}

function displayMyFiles(files, token) {
    const container = document.getElementById("file-list-container");
    document.getElementById("loading-text").style.display = "none";

    if (!files || files.length === 0) {
        container.innerHTML = "<p style='text-align: center; color: #999;'>Bạn chưa tải lên tài liệu nào</p>";
        return;
    }

    container.innerHTML = "";
    files.forEach(file => {
        const card = createFileCard(file, token);
        container.appendChild(card);
    });
}

function createFileCard(file, token) {
    const card = document.createElement("div");
    card.className = "file-card";
    
    const uploadDate = formatDate(file.created_at);
    const uploadTime = formatTime(file.created_at);

    card.innerHTML = `
        <div class="file-info">
            <h3>${file.filename}</h3>
            <p>${file.description || 'Không có mô tả'}</p>
            <div class="meta">
                <span>📅 ${uploadDate} ${uploadTime}</span>
                <span>👁️ ${file.view_count || 0} lượt xem</span>
                <span>${file.visibility === 'public' ? '🌐 Công khai' : '🔐 Riêng tư'}</span>
            </div>
        </div>
        <div class="file-actions">
            <button class="btn-view" onclick="viewFile('${file.id}', '${token}')">👁️ Xem</button>
            <button class="btn-edit" onclick="editFile('${file.id}')">✏️ Sửa</button>
            <button class="btn-delete" onclick="deleteFile('${file.id}', '${token}')">🗑️ Xóa</button>
        </div>
    `;
    
    return card;
}

async function viewFile(fileId, token) {
    try {
        const response = await fetch(`${API_URL}/api/documents/${fileId}/view`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (response.ok) {
            // Redirect to documents page to view the file
            window.location.href = `documents.html?fileId=${fileId}`;
        }
    } catch (error) {
        console.error("Error viewing file:", error);
    }
}

async function deleteFile(fileId, token) {
    if (!confirm("Bạn có chắc chắn muốn xóa tài liệu này?")) return;

    try {
        const response = await fetch(`${API_URL}/api/documents/${fileId}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (response.ok) {
            alert("Đã xóa tài liệu");
            location.reload();
        } else {
            alert("Lỗi xóa tài liệu");
        }
    } catch (error) {
        console.error("Error deleting file:", error);
        alert("Lỗi: " + error.message);
    }
}

function editFile(fileId) {
    // Placeholder - implement edit functionality
    alert("Chức năng sửa đang phát triển");
}
