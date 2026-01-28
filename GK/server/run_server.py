#!/usr/bin/env python3
"""
Chạy server socket trực tiếp
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server.server import main

if __name__ == "__main__":
    main()
