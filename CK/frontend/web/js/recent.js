// File: frontend/web/js/recent.js
// Hiển thị tài liệu đã xem gần đây

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

document.addEventListener("DOMContentLoaded", () => {
    const token = localStorage.getItem("token");
    loadRecentlyViewed(token);
});

async function loadRecentlyViewed(token) {
    const container = document.getElementById("recent-view-container") || document.querySelector(".recent-container");
    if (!container) return;
    
    container.innerHTML = "<p>Đang tải...</p>";
    
    try {
        const headers = {};
        if (token) headers['Authorization'] = `Bearer ${token}`;
        
        const response = await fetch(`${API_URL}/api/documents/recently-viewed`, { 
            method: 'GET', 
            headers 
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        renderRecentlyViewed(data.documents || [], token, container);
        
    } catch (error) {
        console.error("Lỗi tải gần đây:", error);
        container.innerHTML = "<p>Chưa có tài liệu nào được xem gần đây.</p>";
    }
}

function renderRecentlyViewed(files, token, container) {
    container.innerHTML = "";
    
    if (!files || files.length === 0) {
        container.innerHTML = "<p>Chưa có tài liệu nào được xem gần đây.</p>";
        return;
    }
    
    files.forEach(file => {
        const fileCard = document.createElement("div");
        fileCard.className = "doc-card";
        fileCard.dataset.id = file.id;
        
        const tagsString = (file.tags || []).join(', ');
        
        const title = document.createElement('h3');
        title.textContent = file.filename || '';
        
        const owner = document.createElement('div');
        owner.className = 'info-row';
        owner.innerHTML = `<strong>Tác giả:</strong> <span>${escapeHTML(file.owner_name || 'Không rõ')}</span>`;
        
        const desc = document.createElement('p');
        desc.className = 'desc';
        desc.innerHTML = file.description ? escapeHTML(file.description) : '<i>Chưa có mô tả</i>';
        
        const infoRow1 = document.createElement('div');
        infoRow1.className = 'info-row';
        infoRow1.innerHTML = `<strong>Trạng thái:</strong> <span class="status ${file.visibility}">${file.visibility === 'public' ? 'Công khai' : 'Riêng tư'}</span>`;
        
        const infoRow2 = document.createElement('div');
        infoRow2.className = 'info-row';
        infoRow2.innerHTML = `<strong>Tags:</strong> <span>${tagsString || '<i>Không có thẻ</i>'}</span>`;
        
        const infoRow3 = document.createElement('div');
        infoRow3.className = 'info-row';
        infoRow3.innerHTML = `<strong>Ngày tải:</strong> <span>${formatDate(file.created_at)}</span>`;
        
        fileCard.appendChild(title);
        fileCard.appendChild(owner);
        fileCard.appendChild(desc);
        fileCard.appendChild(infoRow1);
        fileCard.appendChild(infoRow2);
        fileCard.appendChild(infoRow3);
        
        container.appendChild(fileCard);
    });
}

function escapeHTML(str) {
    if (!str) return '';
    return String(str).replace(/</g, "&lt;").replace(/>/g, "&gt;");
}
