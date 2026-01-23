// ═══════════════════════════════════════════════════════════════
// 🌐 CLOUDVAULT API CLIENT
// Dynamic configuration with localStorage support
// ═══════════════════════════════════════════════════════════════

const API_BASE = `http://${window.location.hostname}:5000/api`;
const TOKEN_KEY = "token";
const USER_KEY = "user";

function showError(message) {
  const msgEl = document.querySelector(".msg");
  if (msgEl) {
    msgEl.textContent = message;
    msgEl.classList.remove("success");
    msgEl.classList.add("error");
  } else {
    alert("❌ " + message);
  }
}

// Core API request handler with automatic token management
async function apiRequest(endpoint, method = "GET", body = null, requireAuth = true) {
  const headers = {};
  const token = localStorage.getItem(TOKEN_KEY);

  if (body && !(body instanceof FormData)) headers["Content-Type"] = "application/json";
  if (requireAuth && token) headers["Authorization"] = `Bearer ${token}`;

  const options = { method, headers };
  if (body) options.body = body instanceof FormData ? body : JSON.stringify(body);

  try {
    const res = await fetch(`${API_BASE}${endpoint}`, options);

    if (res.status === 204) return null;

    const data = await res.json().catch(() => ({}));

    if (res.status === 401) {
      localStorage.removeItem(TOKEN_KEY);
      localStorage.removeItem(USER_KEY);
      showError("Phiên đã hết hạn. Vui lòng đăng nhập lại.");
      if (!location.pathname.endsWith("login.html")) {
        setTimeout(() => (window.location.href = "login.html"), 800);
      }
      throw new Error(data.message || "Unauthorized");
    }

    if (!res.ok) {
      const message = data.message || `Lỗi API (${res.status})`;
      throw new Error(message);
    }

    return data;
  } catch (err) {
    showError(err.message || "Không thể kết nối tới máy chủ");
    throw err;
  }
}

/* ========== AUTH (Đăng ký/Đăng nhập/Đăng xuất) ========== */

/**
 * register(name, email, password)
 * - Không yêu cầu token
 */
async function register(name, email, password) {
  try {
    const data = await apiRequest("/register", "POST", { name, email, password }, false);
    // backend có thể trả data.message
    return data;
  } catch (err) {
    // apiRequest đã showError
    throw err;
 / Authentication functions
async function register(name, email, password) {
  return apiRequest("/register", "POST", { name, email, password }, false);
}

async function login(email, password) {
  const data = await apiRequest("/login", "POST", { email, password }, false);
  if (data.token) {
    localStorage.setItem(TOKEN_KEY, data.token);
    if (data.user) localStorage.setItem(USER_KEY, JSON.stringify(data.user));
  }
  return data;
}

function logout() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
  } catch (err) {
    throw err;
  }
}

/**
 * getDocuments()
 */
async function getDocuments() {
  try {
 / Document CRUD operations
async function createDocumentMetadata(filename, file_path, description, visibility = "private", tags = []) {
  const payload = { filename, file_path, description, visibility, tags };
  return apiRequest("/documents", "POST", payload);
}

async function getDocuments() {
  return apiRequest("/documents", "GET");
}

function downloadDocument(doc_id) {
  const token = localStorage.getItem(TOKEN_KEY);
  const url = `${API_BASE}/documents/${doc_id}/download${token ? `?token=${token}` : ""}`;
  window.open(url, "_blank");
}

async function deleteDocument(doc_id) {
  return apiRequest(`/documents/${doc_id}`, "DELETE");
}

async function updateDocumentFile(doc_id, newFile) {
  const form = new FormData();
  form.append("file", newFile);
  return apiRequest(`/documents/${doc_id}`, "PUT", form);
}

async function rateDocument(doc_id, stars) {
  try {
    const data = await apiRequest(`/documents/${doc_id}/rate`, "POST", { rating: stars });
    return data;
  } catch (err) {
    throw err;
  }
}

async function reportDocument(doc_id, reason) {
  try {
    const data = await apiRequest(`/documents/${doc_id}/report`, "POST", { reason });
    return data;
  } catch (err) {
    throw err;
  }
}

/* ========== SOCKET UPLOAD TRIGGER ========== */
/* ========== THÙNG RÁC (TRASH) ========== */

a/ Trash management
async function trashDocument(doc_id) {
  return apiRequest(`/documents/${doc_id}/trash`, "POST");
}

async function restoreDocument(doc_id) {
  return apiRequest(`/documents/${doc_id}/restore`, "POST");
}

async function permanentDeleteDocument(doc_id) {
  return apiRequest(`/documents/${doc_id}/permanent`, "DELETE");
}

async function getTrashDocuments() {
  return apiRequest("/documents/trash", "GET"); return data.socket_url;
  } catch (err) {
    throw err;
  }
}
 
/* ========== TIỆN ÍCH ========== */

function getCurrentUser() {
  const u = localStorage.getItem(USER_KEY);
  return u ? JSON.parse(u) : null;
}

function isLoggedIn() {
  return !!localStorage.getItem(TOKEN_KEY);
}

/* ========== USER SETTINGS ========== */

async function getMe() { 
    return apiRequest("/me", "GET");
}

async function updateMe(name) { 
    return apiRequest("/me", "PUT", { name });
}/ Favorites management
async function toggleFavorite(doc_id) {
  return apiRequest(`/documents/${doc_id}/favorite`, "POST");
}

async function getFavoriteDocuments() {
  return apiRequest("/documents/favorites", "GET");
}

// Recent files
async function getRecentlyViewed() {
  return apiRequest("/documents/recently-viewed", "GET");
}

// User utilities
function getCurrentUser() {
  const u = localStorage.getItem(USER_KEY);
  return u ? JSON.parse(u) : null;
}

function isLoggedIn() {
  return !!localStorage.getItem(TOKEN_KEY);
}

// User settings
async function getMe() {
  return apiRequest("/me", "GET");
}

async function updateMe(name) {
  return apiRequest("/me", "PUT", { name });
}

async function changePassword(old_password, new_password) {
