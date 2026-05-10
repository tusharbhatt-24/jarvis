"""
JARVIS Desktop — Dashboard Page
===============================
Home dashboard with premium floating panels, glassmorphism, and live metrics.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout
from PySide6.QtCore import Qt
from desktop.ui.components.widgets import MetricCard, SectionHeader, GlowSeparator, AnimatedCounter, apply_glow
from desktop.state.app_state import AppState
from shared.constants import Colors

class DashboardPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Header
        header = SectionHeader("COMMAND DASHBOARD", "System overview and active operations.")
        layout.addWidget(header)
        
        layout.addWidget(GlowSeparator())
        
        # Quick Stats Grid
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(15)
        
        self.cpu_card = MetricCard("CPU UTILIZATION", "cpu-bar")
        self.ram_card = MetricCard("MEMORY USAGE", "ram-bar")
        self.gpu_card = MetricCard("GPU LOAD", "gpu-bar")
        
        stats_layout.addWidget(self.cpu_card)
        stats_layout.addWidget(self.ram_card)
        stats_layout.addWidget(self.gpu_card)
        
        layout.addLayout(stats_layout)
        
        # Main Content Area (Split into two columns)
        content_layout = QHBoxLayout()
        content_layout.setSpacing(20)
        
        # Left Panel — System Status Console
        left_panel = QFrame()
        left_panel.setObjectName("glass-panel")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(20, 20, 20, 20)
        
        left_header = QLabel("SYSTEM STATUS")
        left_header.setObjectName("title-md")
        left_layout.addWidget(left_header)
        left_layout.addWidget(GlowSeparator())
        
        self.status_console = QLabel(">> All systems operational.\n>> Awaiting voice command.\n>> Network secure.\n>> Local AI engine in standby.")
        self.status_console.setObjectName("mono")
        self.status_console.setWordWrap(True)
        left_layout.addWidget(self.status_console)
        left_layout.addStretch()
        
        content_layout.addWidget(left_panel, 2)
        
        # Right Panel — Activity Summary
        right_panel = QFrame()
        right_panel.setObjectName("glass-panel")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(20, 20, 20, 20)
        
        right_header = QLabel("ACTIVITY SUMMARY")
        right_header.setObjectName("title-md")
        right_layout.addWidget(right_header)
        right_layout.addWidget(GlowSeparator())
        
        # Grid for some counters
        grid = QGridLayout()
        grid.setSpacing(10)
        
        lbl1 = QLabel("Active Sessions:")
        lbl1.setObjectName("subtitle")
        self.val1 = AnimatedCounter(0, "")
        self.val1.setObjectName("accent-text")
        
        lbl2 = QLabel("Commands Processed:")
        lbl2.setObjectName("subtitle")
        self.val2 = AnimatedCounter(0, "")
        self.val2.setObjectName("accent-text")
        
        grid.addWidget(lbl1, 0, 0)
        grid.addWidget(self.val1, 0, 1)
        grid.addWidget(lbl2, 1, 0)
        grid.addWidget(self.val2, 1, 1)
        
        right_layout.addLayout(grid)
        right_layout.addStretch()
        
        content_layout.addWidget(right_panel, 1)
        
        layout.addLayout(content_layout)
        
        # Apply some glow to panels
        apply_glow(left_panel, color=Colors.BORDER_SUBTLE, radius=10)
        apply_glow(right_panel, color=Colors.BORDER_SUBTLE, radius=10)
        
        # Connect to state
        self.state = AppState.instance()
        self.state.metrics_updated.connect(self._on_metrics_updated)
        
    def _on_metrics_updated(self, metrics):
        self.cpu_card.update_value(metrics.cpu_percent, f"Temp: {metrics.cpu_temp_celsius or '--'}°C")
        self.ram_card.update_value(metrics.ram_percent, f"Used: {metrics.ram_used_gb:.1f} GB / {metrics.ram_total_gb:.1f} GB")
        if metrics.gpu_percent is not None:
            self.gpu_card.update_value(metrics.gpu_percent, f"VRAM: {metrics.gpu_vram_used_gb or '--'} GB")
        else:
            self.gpu_card.update_value(0, "N/A")
            
        self.val2.set_value(self.state.ai.total_queries)
