// File: frontend/web/js/favorites.js
// Hiển thị tài liệu được yêu thích ❤️

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
        const container = document.getElementById("favorites-container") || document.querySelector(".favorites-container");
        if (container) {
            container.innerHTML = "<p>Vui lòng đăng nhập để xem tài liệu yêu thích.</p>";
        }
        return;
    }
    
    loadFavorites(token);
});

async function loadFavorites(token) {
    const container = document.getElementById("favorites-container") || document.querySelector(".favorites-container");
    if (!container) return;
    
    container.innerHTML = "<p>Đang tải...</p>";
    
    try {
        const headers = {
            'Authorization': `Bearer ${token}`
        };
        
        const response = await fetch(`${API_URL}/api/documents/favorites`, { 
            method: 'GET', 
            headers 
        });
        
        if (!response.ok) {
            if (response.status === 401) {
                localStorage.removeItem('token');
                container.innerHTML = "<p>Phiên đăng nhập hết hạn. Vui lòng đăng nhập lại.</p>";
                return;
            }
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        renderFavorites(data.documents || [], token, container);
        
    } catch (error) {
        console.error("Lỗi tải yêu thích:", error);
        container.innerHTML = "<p>Lỗi tải tài liệu yêu thích.</p>";
    }
}

function renderFavorites(files, token, container) {
    container.innerHTML = "";
    
    if (!files || files.length === 0) {
        container.innerHTML = "<p>Bạn chưa yêu thích tài liệu nào. Hãy thêm tài liệu yêu thích!</p>";
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
        
        const actions = document.createElement('div');
        actions.className = 'doc-card-actions';
        
        // Nút bỏ yêu thích ❤️
        const removeFavBtn = document.createElement('button');
        removeFavBtn.className = 'btn-action btn-favorite favorited';
        removeFavBtn.type = 'button';
        removeFavBtn.textContent = '❤️ Bỏ yêu thích';
        removeFavBtn.dataset.id = file.id;
        
        actions.appendChild(removeFavBtn);
        
        fileCard.appendChild(title);
        fileCard.appendChild(owner);
        fileCard.appendChild(desc);
        fileCard.appendChild(infoRow1);
        fileCard.appendChild(infoRow2);
        fileCard.appendChild(infoRow3);
        fileCard.appendChild(actions);
        
        container.appendChild(fileCard);
    });
    
    addFavoriteButtonListeners(token, container);
}

function addFavoriteButtonListeners(token, container) {
    if (container._hasFavoriteListener) return;
    
    container.addEventListener('click', async (e) => {
        const removeFavBtn = e.target.closest('.btn-favorite');
        if (removeFavBtn) {
            const docId = removeFavBtn.dataset.id;
            
            try {
                await toggleFavorite(docId);
                alert("Đã bỏ yêu thích!");
                loadFavorites(token);
            } catch (err) {
                console.error("Lỗi:", err);
                alert("Lỗi: " + err.message);
            }
        }
    });
    
    container._hasFavoriteListener = true;
}

function escapeHTML(str) {
    if (!str) return '';
    return String(str).replace(/</g, "&lt;").replace(/>/g, "&gt;");
}
