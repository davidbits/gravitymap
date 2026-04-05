from __future__ import annotations

import sys
from pathlib import Path

from streamlit.web.cli import main as streamlit_main


def main() -> int:
    app_path = Path(__file__).with_name("app.py")
    sys.argv = ["streamlit", "run", str(app_path), "--server.headless=true"]
    streamlit_main()
    return 0
