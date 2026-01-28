// File: frontend/web/js/trash.js
// Hiển thị tài liệu trong thùng rác

const API_URL = "http://127.0.0.1:5000";

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
    
    if (!token) {
        const container = document.getElementById("trash-container") || document.querySelector(".trash-container");
        if (container) {
            container.innerHTML = "<p>Vui lòng đăng nhập để xem thùng rác.</p>";
        }
        return;
    }
    
    loadTrash(token);
});

async function loadTrash(token) {
    const container = document.getElementById("trash-container") || document.querySelector(".trash-container");
    if (!container) return;
    
    container.innerHTML = "<p>Đang tải...</p>";
    
    try {
        const headers = {
            'Authorization': `Bearer ${token}`
        };
        
        const response = await fetch(`${API_URL}/api/documents/trash`, { 
            method: 'GET', 
            headers 
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        renderTrash(data.documents || [], token, container);
        
    } catch (error) {
        console.error("Lỗi tải thùng rác:", error);
        container.innerHTML = "<p>Lỗi tải thùng rác.</p>";
    }
}

function renderTrash(files, token, container) {
    container.innerHTML = "";
    
    if (!files || files.length === 0) {
        container.innerHTML = "<p style='text-align: center; padding: 40px; color: #999;'>🗑️ Thùng rác trống.</p>";
        return;
    }
    
    files.forEach(file => {
        const fileCard = document.createElement("div");
        fileCard.className = "doc-card trash-item";
        fileCard.dataset.id = file.id;
        
        const tagsString = (file.tags || []).join(', ');
        
        const title = document.createElement('h3');
        title.textContent = file.filename || '';
        
        const desc = document.createElement('p');
        desc.className = 'desc';
        desc.innerHTML = file.description ? escapeHTML(file.description) : '<i>Chưa có mô tả</i>';
        
        const infoRow1 = document.createElement('div');
        infoRow1.className = 'info-row';
        infoRow1.innerHTML = `<strong>Trạng thái:</strong> <span style="color: #ff6b6b;">❌ Đã xóa</span>`;
        
        const infoRow2 = document.createElement('div');
        infoRow2.className = 'info-row';
        infoRow2.innerHTML = `<strong>Ngày xóa:</strong> <span>${formatDate(file.updated_at)}</span>`;
        
        const infoRow3 = document.createElement('div');
        infoRow3.className = 'info-row';
        infoRow3.innerHTML = `<strong>Tags:</strong> <span>${tagsString || '<i>Không có thẻ</i>'}</span>`;
        
        const actions = document.createElement('div');
        actions.className = 'doc-card-actions';
        
        // Nút khôi phục
        const restoreBtn = document.createElement('button');
        restoreBtn.className = 'btn-action btn-restore';
        restoreBtn.type = 'button';
        restoreBtn.textContent = '↩️ Khôi phục';
        restoreBtn.dataset.id = file.id;
        
        // Nút xóa vĩnh viễn
        const deletePermBtn = document.createElement('button');
        deletePermBtn.className = 'btn-action btn-delete-perm';
        deletePermBtn.type = 'button';
        deletePermBtn.textContent = '❌ Xóa vĩnh viễn';
        deletePermBtn.dataset.id = file.id;
        
        actions.appendChild(restoreBtn);
        actions.appendChild(deletePermBtn);
        
        fileCard.appendChild(title);
        fileCard.appendChild(desc);
        fileCard.appendChild(infoRow1);
        fileCard.appendChild(infoRow2);
        fileCard.appendChild(infoRow3);
        fileCard.appendChild(actions);
        
        container.appendChild(fileCard);
    });
    
    addTrashButtonListeners(token, container);
}

function addTrashButtonListeners(token, container) {
    if (container._hasTrashListener) return;
    
    container.addEventListener('click', async (e) => {
        const restoreBtn = e.target.closest('.btn-restore');
        if (restoreBtn) {
            const docId = restoreBtn.dataset.id;
            
            try {
                await restoreDocument(docId);
                alert("Đã khôi phục tài liệu!");
                loadTrash(token);
            } catch (err) {
                console.error("Lỗi:", err);
                alert("Lỗi: " + err.message);
            }
            return;
        }
        
        const deletePermBtn = e.target.closest('.btn-delete-perm');
        if (deletePermBtn) {
            const docId = deletePermBtn.dataset.id;
            
            if (!confirm("Bạn có chắc chắn muốn xóa vĩnh viễn tài liệu này không? Hành động này không thể hoàn tác.")) {
                return;
            }
            
            try {
                await permanentDeleteDocument(docId);
                alert("Đã xóa vĩnh viễn!");
                loadTrash(token);
            } catch (err) {
                console.error("Lỗi:", err);
                alert("Lỗi: " + err.message);
            }
            return;
        }
    });
    
    container._hasTrashListener = true;
}

function escapeHTML(str) {
    if (!str) return '';
    return String(str).replace(/</g, "&lt;").replace(/>/g, "&gt;");
}
