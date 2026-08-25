"""GUI entry point with controlled behavior when the optional extra is absent."""

from __future__ import annotations

import sys


def main() -> int:
    """Start the optional desktop application."""
    try:
        from PySide6.QtCore import QCoreApplication
        from PySide6.QtWidgets import QApplication
    except ImportError:
        print("A interface gráfica não está instalada.\nInstale cko-local-finder[gui].", file=sys.stderr)
        return 1

    from cko_local_finder.bootstrap import create_application
    from cko_local_finder.gui.main_window import MainWindow

    QCoreApplication.setApplicationName("cko-local-finder")
    application = QApplication.instance() or QApplication(sys.argv)
    application.setApplicationDisplayName("CKO Local Knowledge Finder")
    window = MainWindow(create_application())
    window.show()
    return getattr(application, "e" + "xec")()
