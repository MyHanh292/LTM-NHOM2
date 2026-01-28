// File: frontend/web/js/main.js
// Script chung: menu, sidebar, navigation

window.API_URL = "http://127.0.0.1:5000";

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

function setupGlobalUI() {
    if (typeof isLoggedIn !== 'function') {
        console.error("Lỗi: api.js chưa được tải.");
        return;
    }

    const token = isLoggedIn();
    const loginBtn = document.getElementById("loginBtn");
    const registerBtn = document.getElementById("registerBtn");
    const logoutBtn = document.getElementById("logoutBtn");

    if (token) {
        // ĐÃ ĐĂNG NHẬP
        if (loginBtn) loginBtn.classList.add("hidden");
        if (registerBtn) registerBtn.classList.add("hidden");
        
        if (logoutBtn) {
            logoutBtn.classList.remove("hidden");
            logoutBtn.addEventListener("click", () => {
                if (confirm("Bạn có muốn đăng xuất không?")) {
                    if (typeof logout === 'function') {
                        logout(); 
                    }
                }
            });
        }
        
        // Auto-load recently viewed on page load
        setTimeout(() => {
            loadRecentlyViewedImmediately(token);
        }, 500);
    } else {
        // CHƯA ĐĂNG NHẬP
        if (loginBtn) loginBtn.classList.remove("hidden");
        if (registerBtn) registerBtn.classList.remove("hidden");
        if (logoutBtn) logoutBtn.classList.add("hidden");
    }
}

// Load recently viewed on page load
async function loadRecentlyViewedImmediately(token) {
    const viewGrid = document.getElementById("recent-view-grid");
    if (!viewGrid) return;
    
    try {
        const headers = { 'Authorization': `Bearer ${token}` };
        const response = await fetch(`${window.API_URL}/api/documents/recently-viewed`, {
            method: 'GET',
            headers
        });
        
        const data = await response.json();
        
        if (data.documents && data.documents.length > 0) {
            viewGrid.innerHTML = "";
            // Show ALL recently viewed files, not just 2
            data.documents.forEach(doc => {
                const card = createPublicDocCard(doc, token);
                viewGrid.appendChild(card);
            });
            if (!viewGrid._hasFavListener) {
                addPublicDocButtonListeners(viewGrid, token);
                viewGrid._hasFavListener = true;
            }
        } else {
            viewGrid.innerHTML = "<p style='grid-column: 1/-1; text-align: center; color: #999;'>Chưa có file được xem</p>";
        }
    } catch (error) {
        console.warn("Could not load recently viewed:", error);
    }
}
 
window.addEventListener("DOMContentLoaded", () => { 
    setupGlobalUI();
    loadHomepageFeed();
    loadPublicDocuments();
    
    const searchBtn = document.getElementById("searchBtn");
    const searchInput = document.getElementById("searchInput");
    
    if (searchBtn) {
        searchBtn.addEventListener("click", () => performSearch());
    }
    if (searchInput) {
        searchInput.addEventListener("keypress", (e) => {
            if (e.key === 'Enter') performSearch();
        });
    }
});

async function performSearch() {
    const keyword = document.getElementById("searchInput").value.trim();
    
    if (keyword === "") {
        alert("Vui lòng nhập từ khóa tìm kiếm!");
        return;
    }

    const token = localStorage.getItem("token");
    if (!token) {
        alert("Bạn cần đăng nhập để sử dụng tính năng tìm kiếm!");
        window.location.href = "login.html";
        return;
    }

    try {
        // Thử tìm theo tag trước
        let url = `${window.API_URL}/api/documents/search?tag=${encodeURIComponent(keyword)}`;
        
        const response = await fetch(url, { 
            method: "GET",
            headers: {
                "Authorization": "Bearer " + token,
                "Content-Type": "application/json"
            }
        });

        if (response.status === 401) {
            alert("Phiên đăng nhập hết hạn. Vui lòng đăng nhập lại.");
            window.location.href = "login.html";
            return;
        }

        const data = await response.json();
        const container = document.getElementById("public-docs-grid");
        if (container) {
            container.innerHTML = "";
            
            if (!data.documents || data.documents.length === 0) {
                container.innerHTML = `<p>Không tìm thấy kết quả cho tag "${keyword}"</p>`;
                return;
            }

            data.documents.forEach(doc => {
                const card = createPublicDocCard(doc, token);
                container.appendChild(card);
            });
            
            if (!container._hasFavListener) {
                addPublicDocButtonListeners(container, token);
                container._hasFavListener = true;
            }
        }
    } catch (error) {
        console.error("Lỗi tìm kiếm:", error);
        alert("Lỗi tìm kiếm. Vui lòng thử lại.");
    }
}

async function loadHomepageFeed() {
    const uploadGrid = document.getElementById("recent-upload-grid");
    if (uploadGrid) {
        try {
            const token = localStorage.getItem("token");
            const headers = token ? { 'Authorization': `Bearer ${token}` } : {};
            
            const response = await fetch(`${window.API_URL}/api/documents/recent-public`, { 
                method: 'GET',
                headers 
            });
            
            const data = await response.json();
            
            if (data.documents && data.documents.length > 0) {
                uploadGrid.innerHTML = ""; 
                data.documents.forEach(doc => {
                    const card = createPublicDocCard(doc, token);
                    uploadGrid.appendChild(card);
                });
                
                if (!uploadGrid._hasFavListener) {
                    addPublicDocButtonListeners(uploadGrid, token);
                    uploadGrid._hasFavListener = true;
                }
            } else {
                uploadGrid.innerHTML = "<p>Chưa có tài liệu public nào.</p>";
            }
        } catch (error) {
            console.error("Lỗi tải recent uploads:", error);
            uploadGrid.innerHTML = "<p>Không thể tải tài liệu.</p>";
        }
    }
 
    const viewGrid = document.getElementById("recent-view-grid");
    if (viewGrid) { 
        if (!isLoggedIn()) {  
             viewGrid.innerHTML = '<p><a href="login.html">Đăng nhập</a> để xem lịch sử của bạn.</p>';
        } else { 
            try { 
                const token = localStorage.getItem("token");
                const headers = { 'Authorization': `Bearer ${token}` };
                
                const response = await fetch(`${window.API_URL}/api/documents/recently-viewed`, {
                    method: 'GET',
                    headers
                });
                
                const data = await response.json();
                
                if (data.documents && data.documents.length > 0) {
                    viewGrid.innerHTML = "";  
                    
                    data.documents.forEach(doc => {
                        const card = createPublicDocCard(doc, token);
                        viewGrid.appendChild(card);
                    });
                } else {
                    viewGrid.innerHTML = "<p>Bạn chưa xem tài liệu nào.</p>";
                }
            } catch (error) {
                console.error("Lỗi tải recent views:", error);
                viewGrid.innerHTML = "<p>Không thể tải lịch sử xem.</p>";
            }
        }
    }
}

async function loadPublicDocuments() {
    const container = document.getElementById("public-docs-grid");
    if (!container) return;
    
    container.innerHTML = "<p>Đang tải...</p>";

    try {
        const token = localStorage.getItem("token");
        const headers = token ? { 'Authorization': `Bearer ${token}` } : {};
        
        const response = await fetch(`${window.API_URL}/api/documents/public`, { 
            method: 'GET',
            headers
        });
        
        const data = await response.json();

        if (response.ok) {
            container.innerHTML = "";
            if (!data.documents || data.documents.length === 0) {
                container.innerHTML = "<p>Hiện chưa có tài liệu public nào.</p>";
                return;
            }

            data.documents.forEach(doc => {
                const card = createPublicDocCard(doc, token);
                container.appendChild(card);
            });
            
            if (!container._hasFavListener) {
                addPublicDocButtonListeners(container, token);
                container._hasFavListener = true;
            }
        } else {
            container.innerHTML = "<p>Lỗi tải tài liệu.</p>";
        }
    } catch (error) {
        console.error("Lỗi:", error);
        container.innerHTML = "<p>Lỗi tải tài liệu.</p>";
    }
}

function createPublicDocCard(doc, token) {
    const card = document.createElement('div');
    card.className = 'doc-card';
    card.dataset.id = doc.id;
    
    const tagsString = (doc.tags || []).join(', ');
    
    const title = document.createElement('h3');
    title.textContent = doc.filename || '';
    title.style.cursor = 'pointer';
    title.title = 'Nhấp để xem tài liệu';
    
    const owner = document.createElement('div');
    owner.className = 'info-row';
    owner.innerHTML = `<strong>Tác giả:</strong> <span>${escapeHTML(doc.owner_name || 'Không rõ')}</span>`;
    
    const desc = document.createElement('p');
    desc.className = 'desc';
    desc.innerHTML = doc.description ? escapeHTML(doc.description) : '<i>Chưa có mô tả</i>';
    
    const infoRow2 = document.createElement('div');
    infoRow2.className = 'info-row';
    infoRow2.innerHTML = `<strong>Tags:</strong> <span>${tagsString || '<i>Không có thẻ</i>'}</span>`;
    
    const infoRow3 = document.createElement('div');
    infoRow3.className = 'info-row';
    const dateStr = formatDate(doc.created_at);
    infoRow3.innerHTML = `<strong>Ngày tải:</strong> <span>${dateStr}</span>`;
    
    const actions = document.createElement('div');
    actions.className = 'doc-card-actions';
    
    // ALWAYS show favorite button (even for non-logged-in users)
    const favBtn = document.createElement('button');
    favBtn.className = 'btn-action btn-favorite';
    favBtn.type = 'button';
    favBtn.dataset.id = doc.id;
    
    if (token) {
        const currentUser = getCurrentUser();
        // Check if this is user's own file
        if (currentUser && doc.owner_name === currentUser.name) {
            // Hide favorite for own files
            favBtn.style.display = 'none';
        } else {
            // Show favorite for other users' files
            if (doc.is_favorited) {
                favBtn.classList.add('favorited');
                favBtn.textContent = '❤️ Đã yêu thích';
            } else {
                favBtn.textContent = '🤍 Yêu thích';
            }
            favBtn.dataset.canFav = 'true';
        }
    } else {
        // Not logged in - show favorite but require login
        favBtn.textContent = '🤍 Yêu thích';
        favBtn.dataset.canFav = 'false';
    }
    
    actions.appendChild(favBtn);
    
    // Add view button
    const viewBtn = document.createElement('button');
    viewBtn.className = 'btn-action btn-edit';
    viewBtn.type = 'button';
    viewBtn.textContent = '👁️ Xem';
    viewBtn.dataset.id = doc.id;
    viewBtn.dataset.filePath = doc.file_path;
    viewBtn.dataset.filename = doc.filename;
    actions.appendChild(viewBtn);
    
    card.appendChild(title);
    card.appendChild(owner);
    card.appendChild(desc);
    card.appendChild(infoRow2);
    card.appendChild(infoRow3);
    if (actions.children.length > 0) {
        card.appendChild(actions);
    }
    
    // Add click handler to title for opening file
    title.addEventListener('click', () => {
        openDocumentFile(doc.id, doc.file_path, doc.filename, token);
    });
    
    return card;
}

function addPublicDocButtonListeners(container, token) {
    container.addEventListener('click', async (e) => {
        // Handle favorite button
        const favBtn = e.target.closest('.btn-favorite');
        if (favBtn) {
            const docId = favBtn.dataset.id;
            const canFav = favBtn.dataset.canFav;
            
            if (canFav === 'false') {
                alert("Vui lòng đăng nhập để yêu thích tài liệu.");
                return;
            }
            
            if (!token) {
                alert("Vui lòng đăng nhập để yêu thích tài liệu.");
                return;
            }
            
            try {
                await toggleFavorite(docId);
                if (favBtn.classList.contains('favorited')) {
                    favBtn.classList.remove('favorited');
                    favBtn.textContent = '🤍 Yêu thích';
                } else {
                    favBtn.classList.add('favorited');
                    favBtn.textContent = '❤️ Đã yêu thích';
                }
            } catch (err) {
                console.error("Lỗi:", err);
                alert("Lỗi: " + err.message);
            }
            return;
        }
        
        // Handle view button
        const viewBtn = e.target.closest('.btn-edit[data-file-path]');
        if (viewBtn) {
            const docId = viewBtn.dataset.id;
            const filePath = viewBtn.dataset.filePath;
            const filename = viewBtn.dataset.filename;
            openDocumentFile(docId, filePath, filename, token);
        }
    });
}


function escapeHTML(str) {
    if (!str) return '';
    return String(str).replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

// Function to open/view document file
async function openDocumentFile(docId, filePath, filename, token) {
    if (!filePath) {
        alert("Không tìm thấy đường dẫn file.");
        return;
    }
    
    try {
        // Log view history if user is logged in
        if (token && typeof logViewHistory === 'function') {
            await logViewHistory(docId);
            // Refresh recently viewed if it exists
            const recentViewGrid = document.getElementById("recent-view-grid");
            if (recentViewGrid) {
                const viewGridToken = localStorage.getItem("token");
                if (viewGridToken) {
                    try {
                        const response = await fetch(`${window.API_URL}/api/documents/recently-viewed`, {
                            headers: { 'Authorization': `Bearer ${viewGridToken}` }
                        });
                        const data = await response.json();
                        if (data.documents) {
                            recentViewGrid.innerHTML = "";
                            // Show ALL recently viewed files
                            data.documents.forEach(doc => {
                                const card = createPublicDocCard(doc, viewGridToken);
                                recentViewGrid.appendChild(card);
                            });
                        }
                    } catch (e) {
                        console.warn("Could not refresh recently viewed:", e);
                    }
                }
            }
        }
        
        const fileUrl = `${window.API_URL}/storage/uploads/${filePath}`;
        const ext = filename.toLowerCase().split('.').pop();
        
        // Check if file type can be viewed inline
        if (ext === 'pdf') {
            // Show PDF in modal with iframe
            showFileViewer(filename, fileUrl, 'pdf');
        } else if (['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp'].includes(ext)) {
            // Show image in modal
            showFileViewer(filename, fileUrl, 'image');
        } else {
            // Download file
            const link = document.createElement('a');
            link.href = fileUrl;
            link.download = filename;
            link.click();
        }
    } catch (error) {
        console.error("Lỗi mở file:", error);
        alert("Lỗi mở file. Vui lòng thử lại.");
    }
}

function showFileViewer(filename, fileUrl, type) {
    const modal = document.getElementById('fileViewerModal');
    const viewerTitle = document.getElementById('viewerTitle');
    const viewerContainer = document.getElementById('viewerContainer');
    
    viewerTitle.textContent = filename;
    viewerContainer.innerHTML = '';
    
    if (type === 'pdf') {
        const iframe = document.createElement('iframe');
        iframe.src = fileUrl;
        iframe.type = 'application/pdf';
        viewerContainer.appendChild(iframe);
    } else if (type === 'image') {
        const img = document.createElement('img');
        img.src = fileUrl;
        img.alt = filename;
        viewerContainer.appendChild(img);
    }
    
    modal.classList.remove('hidden');
}

function closeFileViewer() {
    const modal = document.getElementById('fileViewerModal');
    modal.classList.add('hidden');
    document.getElementById('viewerContainer').innerHTML = '';
}

// Close modal when clicking outside
document.addEventListener('DOMContentLoaded', () => {
    const modal = document.getElementById('fileViewerModal');
    if (modal) {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                closeFileViewer();
            }
        });
    }
});

