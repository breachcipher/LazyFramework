# widgets/module_tab.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QScrollArea, QFormLayout, QLabel
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from core.module_runner import ModuleRunner


class ModuleTab(QWidget):
    """Satu tab untuk satu module yang berjalan independen."""

    def __init__(self, framework, module_name, module_instance, parent=None):
        super().__init__(parent)
        self.framework = framework
        self.module_name = module_name
        self.module_instance = module_instance
        self.module_runner = None
        self.option_widgets = {}

        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        # --- Label nama module ---
        title = QLabel(f"[{self.module_name}]")
        title.setStyleSheet("color: #ff5252; font-weight: bold; font-size: 11pt;")
        layout.addWidget(title)

        # --- Options area ---
        self.options_widget = QWidget()
        self.options_layout = QFormLayout(self.options_widget)
        options_scroll = QScrollArea()
        options_scroll.setWidgetResizable(True)
        options_scroll.setWidget(self.options_widget)
        options_scroll.setMaximumHeight(200)
        layout.addWidget(options_scroll)

        # --- Console output ---
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setFont(QFont("DejaVu Sans Mono", 10))
        layout.addWidget(self.console)

        # --- Control buttons ---
        btn_layout = QHBoxLayout()

        self.run_btn = QPushButton("START")
        self.run_btn.setProperty("action", "run")
        self.run_btn.clicked.connect(self._handle_run_stop)
        btn_layout.addWidget(self.run_btn)

        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self.console.clear)
        btn_layout.addWidget(clear_btn)

        close_btn = QPushButton("✕ Close Tab")
        close_btn.setStyleSheet("color: #ff5252;")
        close_btn.clicked.connect(self._request_close)
        btn_layout.addWidget(close_btn)

        layout.addLayout(btn_layout)

    # ── Output ──────────────────────────────────────────────
    def append_output(self, text: str):
        """Append rich-formatted text ke console tab ini."""
        from io import StringIO
        try:
            from rich.console import Console
            buf = StringIO()
            con = Console(file=buf, force_terminal=False, width=120)
            con.print(text)
            plain = buf.getvalue().rstrip()
        except Exception:
            plain = text

        self.console.append(plain)
        # Auto-scroll
        cursor = self.console.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.console.setTextCursor(cursor)

    # ── Run / Stop ───────────────────────────────────────────
    def _handle_run_stop(self):
        if self.run_btn.property("action") == "run":
            self._start()
        else:
            self._stop()

    def _start(self):
        if self.module_runner and self.module_runner.isRunning():
            return

        self.module_runner = ModuleRunner(self.framework, self.module_instance)
        self.module_runner.output.connect(self.append_output)
        self.module_runner.finished.connect(self._on_finished)
        self.module_runner.start()

        self.run_btn.setText("STOP")
        self.run_btn.setProperty("action", "stop")
        self.append_output(f"[green]▶ Starting {self.module_name}...[/]")

    def _stop(self):
        if self.module_runner and self.module_runner.isRunning():
            self.module_runner.stop()
        self.append_output(f"[yellow]■ Stopping {self.module_name}...[/]")

    def _on_finished(self):
        self.run_btn.setText("START")
        self.run_btn.setProperty("action", "run")
        self.append_output(f"[cyan]✓ {self.module_name} finished.[/]")

    # ── Close ────────────────────────────────────────────────
    def _request_close(self):
        """Signal ke parent (GUI) untuk menutup tab ini."""
        self._stop()
        # Cari index tab ini di parent QTabWidget dan tutup
        parent_tabs = self.parent()
        if hasattr(parent_tabs, 'indexOf'):          # QTabWidget
            idx = parent_tabs.indexOf(self)
            if idx >= 0:
                parent_tabs.removeTab(idx)
        self.deleteLater()
