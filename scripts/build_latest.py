#!/usr/bin/env python3
"""构建看板数据（趋势 + AI + 静态 API）—— CI / 本地通用入口。"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qd_tracker.build import main  # noqa: E402

if __name__ == "__main__":
    main()
