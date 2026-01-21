"""
utils/validators.py - Input Validation Utilities
==================================================

Validation functions for common input types and constraints.
"""

import os
import re
from pathlib import Path


def validate_email(email):
    """
    Validate email format.
    
    Args:
        email (str): Email address to validate
    
    Returns:
        bool: True if valid, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_password(password, min_length=6):
    """
    Validate password strength.
    
    Args:
        password (str): Password to validate
        min_length (int): Minimum password length
    
    Returns:
        tuple: (is_valid, message)
    """
    if not password or len(password) < min_length:
        return False, f"Password must be at least {min_length} characters"
    
    # Optional: Add more checks
    # if not any(c.isupper() for c in password):
    #     return False, "Password must contain uppercase letter"
    # if not any(c.isdigit() for c in password):
    #     return False, "Password must contain digit"
    
    return True, "Password is valid"


def validate_filename(filename, max_length=255):
    """
    Validate filename safety.
    
    Args:
        filename (str): Filename to validate
        max_length (int): Maximum filename length
    
    Returns:
        tuple: (is_valid, message)
    """
    if not filename or len(filename) == 0:
        return False, "Filename cannot be empty"
    
    if len(filename) > max_length:
        return False, f"Filename cannot exceed {max_length} characters"
    
    # Prevent path traversal attacks
    if '..' in filename or '/' in filename or '\\' in filename:
        return False, "Filename contains invalid characters"
    
    # Check for reserved filenames (Windows)
    reserved = {'CON', 'PRN', 'AUX', 'NUL', 'COM1', 'LPT1'}
    if filename.upper() in reserved:
        return False, f"Filename '{filename}' is reserved"
    
    return True, "Filename is valid"


def validate_file_size(file_size, max_size):
    """
    Validate file size.
    
    Args:
        file_size (int): File size in bytes
        max_size (int): Maximum allowed size in bytes
    
    Returns:
        tuple: (is_valid, message)
    """
    if file_size <= 0:
        return False, "File size must be greater than 0"
    
    if file_size > max_size:
        max_mb = max_size / (1024 * 1024)
        file_mb = file_size / (1024 * 1024)
        return False, f"File size ({file_mb:.2f}MB) exceeds limit ({max_mb:.2f}MB)"
    
    return True, "File size is valid"


def validate_file_extension(filename, allowed_extensions):
    """
    Validate file extension.
    
    Args:
        filename (str): Filename
        allowed_extensions (set): Set of allowed extensions (e.g., {'pdf', 'doc'})
    
    Returns:
        tuple: (is_valid, message)
    """
    if not filename or '.' not in filename:
        return False, "File has no extension"
    
    ext = filename.rsplit('.', 1)[1].lower()
    
    if ext not in allowed_extensions:
        return False, f"File type '.{ext}' is not allowed"
    
    return True, f"File extension '.{ext}' is valid"


def sanitize_filename(filename):
    """
    Sanitize filename by removing dangerous characters.
    
    Args:
        filename (str): Filename to sanitize
    
    Returns:
        str: Sanitized filename
    """
    # Remove path separators and dangerous characters
    filename = filename.replace('..', '')
    filename = filename.replace('/', '_')
    filename = filename.replace('\\', '_')
    filename = re.sub(r'[<>:"|?*]', '_', filename)
    
    return filename.strip()


def validate_chunk_offset(offset, file_size):
    """
    Validate chunk offset.
    
    Args:
        offset (int): Chunk offset
        file_size (int): Total file size
    
    Returns:
        tuple: (is_valid, message)
    """
    if offset < 0:
        return False, "Offset cannot be negative"
    
    if offset > file_size:
        return False, f"Offset ({offset}) exceeds file size ({file_size})"
    
    return True, "Offset is valid"


def validate_chunk_length(length, max_chunk_size, min_chunk_size=1024):
    """
    Validate chunk length.
    
    Args:
        length (int): Chunk length in bytes
        max_chunk_size (int): Maximum chunk size
        min_chunk_size (int): Minimum chunk size
    
    Returns:
        tuple: (is_valid, message)
    """
    if length < min_chunk_size:
        return False, f"Chunk size must be at least {min_chunk_size} bytes"
    
    if length > max_chunk_size:
        return False, f"Chunk size cannot exceed {max_chunk_size} bytes"
    
    return True, "Chunk length is valid"


def validate_tags(tags, max_tags=10):
    """
    Validate tags list.
    
    Args:
        tags (list): List of tag strings
        max_tags (int): Maximum number of tags allowed
    
    Returns:
        tuple: (is_valid, message)
    """
    if not isinstance(tags, list):
        return False, "Tags must be a list"
    
    if len(tags) > max_tags:
        return False, f"Maximum {max_tags} tags allowed"
    
    for tag in tags:
        if not isinstance(tag, str) or len(tag) == 0:
            return False, "Tag cannot be empty"
        if len(tag) > 50:
            return False, f"Tag cannot exceed 50 characters"
    
    return True, "Tags are valid"


def validate_visibility(visibility):
    """
    Validate visibility setting.
    
    Args:
        visibility (str): 'public' or 'private'
    
    Returns:
        tuple: (is_valid, message)
    """
    if visibility not in ('public', 'private'):
        return False, "Visibility must be 'public' or 'private'"
    
    return True, "Visibility is valid"
