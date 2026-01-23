"""
🚀 IMPROVED Socket Server - TCP (Port 6000)
===========================================

Enhancements:
- Comprehensive logging
- Input validation
- Better error handling
- Connection timeouts
- Atomic file operations
"""

import socket
import threading
import json
import os
import time
import traceback
import sys
from typing import Optional
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Import custom modules
try:
    from socket_server.persistence import Persistence
    from socket_server.chunk_handler import write_chunk
    from socket_server.backend_client import BackendClient
    from utils.logger import setup_logging
    from utils.validators import (
        validate_filename, validate_file_size, validate_chunk_offset, 
        validate_chunk_length, sanitize_filename
    )
    from config import (
        SOCKET_HOST, SOCKET_PORT, SOCKET_TIMEOUT, SOCKET_BACKLOG,
        STORAGE_DIR, TEMP_DIR, MAX_FILE_SIZE, MAX_CHUNK_SIZE, LOG_DIR
    )
except Exception as e:
    print(f"❌ IMPORT ERROR: {e}")
    traceback.print_exc()
    raise

# ====================================
# 📊 LOGGING SETUP
# ====================================
logger = setup_logging(__name__, LOG_DIR)

# ====================================
# ⚙️ GLOBAL CONFIG
# ====================================
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
state = Persistence(str(TEMP_DIR / "uploads_state.json"))
backend = BackendClient()

logger.info(f"📁 Storage directory: {STORAGE_DIR}")
logger.info(f"📁 Temp directory: {TEMP_DIR}")

# ====================================
# 🔧 UTILITY FUNCTIONS
# ====================================

def send_json(conn: socket.socket, obj: dict) -> bool:
    """
    Safely send JSON response over socket.
    
    Args:
        conn: Socket connection
        obj: Dictionary to send as JSON
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        data = (json.dumps(obj) + "\n").encode("utf-8")
        conn.sendall(data)
        return True
    except Exception as e:
        logger.error(f"⚠️ Failed to send JSON: {e}")
        return False


def recv_line(conn: socket.socket, maxlen=65536) -> Optional[bytes]:
    """
    Read line from socket (until newline).
    
    Args:
        conn: Socket connection
        maxlen: Maximum line length
    
    Returns:
        bytes: Read line or None if connection closed/timeout
    """
    buf = bytearray()
    try:
        while True:
            chunk = conn.recv(1)
            if not chunk:
                logger.debug("Connection closed (no data)")
                return None
            
            buf += chunk
            if buf.endswith(b'\n') or len(buf) >= maxlen:
                return bytes(buf)
    except socket.timeout:
        logger.warning("Socket timeout while reading line")
        return None
    except ConnectionResetError:
        logger.warning("Connection reset by peer")
        return None
    except Exception as e:
        logger.error(f"Error reading line: {e}")
        return None


def recv_exact(conn: socket.socket, n: int) -> Optional[bytes]:
    """
    Read exactly n bytes from socket.
    
    Args:
        conn: Socket connection
        n: Number of bytes to read
    
    Returns:
        bytes: Exactly n bytes or None if EOF/timeout
    """
    parts = []
    remaining = n
    
    try:
        while remaining > 0:
            chunk = conn.recv(min(65536, remaining))
            if not chunk:
                logger.warning(f"EOF reached: got {n - remaining}/{n} bytes")
                return None
            
            parts.append(chunk)
            remaining -= len(chunk)
        
        return b"".join(parts)
    except socket.timeout:
        logger.warning(f"Timeout: got {n - remaining}/{n} bytes")
        return None
    except ConnectionResetError:
        logger.warning("Connection reset while receiving data")
        return None
    except Exception as e:
        logger.error(f"Error receiving {n} bytes: {e}")
        return None


# ====================================
# 🧠 CLIENT HANDLER
# ====================================

def handle_client(conn: socket.socket, addr):
    """
    Handle single client connection.
    
    Supports actions:
    - start: Begin or resume upload
    - chunk: Receive file chunk
    - pause: Pause upload
    - resume: Resume upload
    - stop: Stop upload
    - query_resume: Query current offset
    """
    peer = f"{addr[0]}:{addr[1]}"
    logger.info(f"🔌 New client connected: {peer}")
    
    conn.settimeout(SOCKET_TIMEOUT)
    client_uploads = {}  # Track uploads from this client
    
    try:
        while True:
            # Read JSON header
            line = recv_line(conn)
            if not line:
                logger.info(f"❎ {peer} disconnected (no header)")
                break
            
            try:
                header = json.loads(line.decode("utf-8").strip())
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON from {peer}: {line[:100]}")
                send_json(conn, {"status": "error", "reason": "invalid_header"})
                continue
            
            # Validate header
            action = header.get("action")
            upload_id = header.get("upload_id")
            
            if not action:
                logger.warning(f"{peer}: Missing 'action'")
                send_json(conn, {"status": "error", "reason": "missing_action"})
                continue
            
            if not upload_id:
                logger.warning(f"{peer}: Missing 'upload_id'")
                send_json(conn, {"status": "error", "reason": "missing_upload_id"})
                continue
            
            # Dispatch action
            try:
                if action == "start":
                    handle_start(conn, peer, header, upload_id, client_uploads)
                
                elif action == "resume":
                    handle_resume(conn, peer, header, upload_id, client_uploads)
                
                elif action == "chunk":
                    handle_chunk(conn, peer, header, upload_id, client_uploads)
                
                elif action == "pause":
                    handle_pause(conn, peer, upload_id, client_uploads)
                
                elif action == "resume_after_pause":
                    handle_resume_after_pause(conn, peer, upload_id, client_uploads)
                
                elif action == "stop":
                    handle_stop(conn, peer, upload_id, client_uploads)
                
                elif action == "query_resume":
                    handle_query_resume(conn, peer, upload_id)
                
                else:
                    logger.warning(f"{peer}: Unknown action '{action}'")
                    send_json(conn, {"status": "error", "reason": "unknown_action"})
            
            except Exception as inner:
                logger.error(f"Error handling {action}: {inner}", exc_info=True)
                send_json(conn, {"status": "error", "reason": "internal_error"})
    
    except ConnectionResetError:
        logger.warning(f"🔥 Connection reset by {peer}")
    except Exception as ex:
        logger.error(f"🔥 Fatal error for {peer}: {ex}", exc_info=True)
    
    finally:
        try:
            conn.close()
            logger.info(f"🧹 Cleaned up connection for {peer}")
        except:
            pass


def handle_start(conn, peer, header, upload_id, client_uploads):
    """Handle upload START action."""
    filename = header.get("filename", "").strip()
    filesize = header.get("filesize", 0)
    chunk_size = header.get("chunk_size", 65536)
    metadata = header.get("metadata", {})
    
    # Validate inputs
    is_valid, msg = validate_filename(filename)
    if not is_valid:
        logger.warning(f"{peer}: Invalid filename '{filename}' - {msg}")
        send_json(conn, {"status": "error", "reason": f"invalid_filename: {msg}"})
        return
    
    is_valid, msg = validate_file_size(filesize, MAX_FILE_SIZE)
    if not is_valid:
        logger.warning(f"{peer}: File too large - {msg}")
        send_json(conn, {"status": "error", "reason": f"file_too_large: {msg}"})
        return
    
    is_valid, msg = validate_chunk_length(chunk_size, MAX_CHUNK_SIZE)
    if not is_valid:
        logger.warning(f"{peer}: Invalid chunk size - {msg}")
        send_json(conn, {"status": "error", "reason": f"invalid_chunk: {msg}"})
        return
    
    # Sanitize filename
    filename = sanitize_filename(filename)
    
    # Check if upload already exists
    info = state.get(upload_id)
    if not info:
        info = {
            "filename": filename,
            "filesize": filesize,
            "offset": 0,
            "status": "started",
            "peer": peer,
            "metadata": metadata,
            "created_at": time.time()
        }
        logger.info(f"🚀 Starting new upload: {upload_id} ({filename}, {filesize} bytes)")
    else:
        info["status"] = "resumed"
        info["peer"] = peer
        logger.info(f"▶️ Resuming upload: {upload_id}")
    
    state.update(upload_id, info)
    client_uploads[upload_id] = info
    
    offset = info.get("offset", 0)
    send_json(conn, {
        "status": "ok",
        "upload_id": upload_id,
        "offset": offset,
        "chunk_size": chunk_size
    })
    logger.debug(f"✅ START response: {peer} offset={offset}")


def handle_resume(conn, peer, header, upload_id, client_uploads):
    """Handle upload RESUME action."""
    info = state.get(upload_id)
    if not info:
        logger.warning(f"{peer}: Resume for unknown upload {upload_id}")
        send_json(conn, {"status": "error", "reason": "unknown_upload"})
        return
    
    info["status"] = "resuming"
    info["peer"] = peer
    state.update(upload_id, info)
    client_uploads[upload_id] = info
    
    offset = info.get("offset", 0)
    send_json(conn, {
        "status": "ok",
        "upload_id": upload_id,
        "offset": offset
    })
    logger.info(f"▶️ RESUME: {peer} {upload_id} from offset {offset}")


def handle_chunk(conn, peer, header, upload_id, client_uploads):
    """Handle file CHUNK upload."""
    length = header.get("length", 0)
    offset = header.get("offset", 0)
    
    # Validate inputs
    is_valid, msg = validate_chunk_length(length, MAX_CHUNK_SIZE)
    if not is_valid:
        logger.warning(f"{peer}: Invalid chunk length - {msg}")
        send_json(conn, {"status": "error", "reason": f"invalid_length: {msg}"})
        return
    
    info = state.get(upload_id)
    if not info:
        logger.warning(f"{peer}: Chunk for unknown upload {upload_id}")
        send_json(conn, {"status": "error", "reason": "unknown_upload"})
        return
    
    is_valid, msg = validate_chunk_offset(offset, info["filesize"])
    if not is_valid:
        logger.warning(f"{peer}: Invalid chunk offset - {msg}")
        send_json(conn, {"status": "error", "reason": f"invalid_offset: {msg}"})
        return
    
    # Read chunk data
    data = recv_exact(conn, length)
    if data is None:
        logger.error(f"⚠️ Connection lost from {peer} (expected {length} bytes)")
        info["status"] = "failed"
        state.update(upload_id, info)
        return
    
    if len(data) != length:
        logger.error(f"⚠️ Incomplete chunk: got {len(data)}/{length} bytes")
        send_json(conn, {"status": "error", "reason": "incomplete_chunk"})
        return
    
    # Save chunk to disk
    filename = info.get("filename")
    save_dir = STORAGE_DIR / upload_id
    save_dir.mkdir(parents=True, exist_ok=True)
    file_path = save_dir / filename
    
    if not write_chunk(str(file_path), data, offset):
        logger.error(f"❌ Failed to write chunk for {upload_id}")
        send_json(conn, {"status": "error", "reason": "write_failed"})
        return
    
    # Update state
    new_offset = offset + length
    info["offset"] = new_offset
    info["status"] = "uploading"
    info["last_update"] = time.time()
    state.update(upload_id, info)
    
    send_json(conn, {
        "status": "ok",
        "upload_id": upload_id,
        "offset": new_offset
    })
    
    # Check if upload complete
    if new_offset >= info.get("filesize", 0):
        logger.info(f"✅ Upload complete: {upload_id} ({filename})")
        
        # Notify backend
        full_metadata = info.get("metadata", {})
        if "filename" not in full_metadata:
            full_metadata["filename"] = filename
        
        backend.notify_completion(upload_id, str(file_path), full_metadata)
        state.delete(upload_id)
        if upload_id in client_uploads:
            del client_uploads[upload_id]


def handle_pause(conn, peer, upload_id, client_uploads):
    """Handle upload PAUSE action."""
    info = state.get(upload_id)
    if not info:
        logger.warning(f"{peer}: Pause for unknown upload {upload_id}")
        send_json(conn, {"status": "error", "reason": "unknown_upload"})
        return
    
    info["status"] = "paused"
    state.update(upload_id, info)
    
    send_json(conn, {
        "status": "ok",
        "upload_id": upload_id,
        "state": "paused"
    })
    logger.info(f"⏸️  Upload paused: {peer} {upload_id}")


def handle_resume_after_pause(conn, peer, upload_id, client_uploads):
    """Handle resume after PAUSE."""
    info = state.get(upload_id)
    if not info:
        logger.warning(f"{peer}: Resume-after-pause for unknown upload {upload_id}")
        send_json(conn, {"status": "error", "reason": "unknown_upload"})
        return
    
    info["status"] = "uploading"
    state.update(upload_id, info)
    
    send_json(conn, {
        "status": "ok",
        "upload_id": upload_id,
        "offset": info.get("offset", 0)
    })
    logger.info(f"▶️  Upload resumed after pause: {peer} {upload_id}")


def handle_stop(conn, peer, upload_id, client_uploads):
    """Handle upload STOP action."""
    info = state.get(upload_id)
    if not info:
        logger.warning(f"{peer}: Stop for unknown upload {upload_id}")
        send_json(conn, {"status": "error", "reason": "unknown_upload"})
        return
    
    info["status"] = "stopped"
    state.update(upload_id, info)
    
    send_json(conn, {
        "status": "ok",
        "upload_id": upload_id,
        "state": "stopped"
    })
    logger.info(f"⛔ Upload stopped: {peer} {upload_id}")


def handle_query_resume(conn, peer, upload_id):
    """Query current offset for resuming."""
    info = state.get(upload_id)
    if not info:
        offset = 0
    else:
        offset = info.get("offset", 0)
    
    send_json(conn, {
        "status": "ok",
        "upload_id": upload_id,
        "offset": offset
    })
    logger.debug(f"📊 Query resume: {peer} {upload_id} offset={offset}")


# ====================================
# 🖥️ MAIN SERVER LOOP
# ====================================

def accept_loop():
    """Main server loop - accept and handle connections."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((SOCKET_HOST, SOCKET_PORT))
        s.listen(SOCKET_BACKLOG)
        
        logger.info(f"🚀 Socket TCP Server listening at {SOCKET_HOST}:{SOCKET_PORT}")
        logger.info(f"⏰ Connection timeout: {SOCKET_TIMEOUT}s")
        logger.info(f"📁 Storage: {STORAGE_DIR}")
        logger.info(f"📊 Max file size: {MAX_FILE_SIZE / (1024*1024):.0f}MB")
        
        try:
            while True:
                try:
                    conn, addr = s.accept()
                    thread = threading.Thread(
                        target=handle_client,
                        args=(conn, addr),
                        daemon=True
                    )
                    thread.start()
                except KeyboardInterrupt:
                    logger.info("🛑 Server shutdown requested")
                    break
                except Exception as e:
                    logger.error(f"Error accepting connection: {e}")
                    time.sleep(0.1)
        finally:
            logger.info("👋 Socket server stopped")


if __name__ == "__main__":
    try:
        accept_loop()
    except KeyboardInterrupt:
        logger.info("🛑 Server interrupted")
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
