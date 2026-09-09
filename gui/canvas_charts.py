"""
Custom Native Tkinter Canvas Charting Engine for College Management System.
Renders responsive, beautiful Bar Charts, Donut Charts, and Gauge Meters
using pure Python standard library vector mathematics and Tkinter Canvas primitives.
Zero external dependencies required.
"""

import tkinter as tk
from typing import Any, List, Optional, Tuple
from gui.styles import PALETTE, FONTS


class BarChart(tk.Canvas):
    """
    Native vector Bar Chart on Tkinter Canvas.
    Supports dynamic scaling, grid lines, value labels, and custom color bars.
    """

    def __init__(self, parent, title: str = "", width: int = 380, height: int = 240, bg: str = "#FFFFFF", **kwargs):
        super().__init__(parent, width=width, height=height, bg=bg, highlightthickness=0, **kwargs)
        self.chart_title = title
        self._width = width
        self._height = height
        self._bg = bg

    def draw_chart(self, data: List[Tuple[str, float]], bar_color: str = PALETTE["primary"], value_suffix: str = "") -> None:
        """
        data: List of (label, value)
        """
        self.delete("all")
        w = self._width
        h = self._height

        # Title
        if self.chart_title:
            self.create_text(w / 2, 18, text=self.chart_title, font=FONTS["heading"], fill=PALETTE["text_primary"])

        if not data:
            self.create_text(w / 2, h / 2, text="No Data Available", font=FONTS["body"], fill=PALETTE["text_muted"])
            return

        max_val = max(val for _, val in data) if data else 1.0
        if max_val <= 0:
            max_val = 1.0

        margin_left = 45
        margin_right = 20
        margin_top = 40
        margin_bottom = 45

        plot_w = w - margin_left - margin_right
        plot_h = h - margin_top - margin_bottom

        # Draw grid lines & Y axis ticks
        for i in range(4):
            y = margin_top + (plot_h * (3 - i) / 3)
            val_tick = round((max_val * i) / 3, 1)
            # Horizontal dashed line
            self.create_line(margin_left, y, w - margin_right, y, fill="#E2E8F0", dash=(2, 2))
            self.create_text(margin_left - 8, y, text=f"{val_tick:g}", font=FONTS["small"], fill=PALETTE["text_secondary"], anchor="e")

        # Baseline
        self.create_line(margin_left, margin_top + plot_h, w - margin_right, margin_top + plot_h, fill="#CBD5E1", width=1)

        # Draw Bars
        n = len(data)
        bar_slot = plot_w / n
        bar_width = min(40, bar_slot * 0.65)

        colors = [PALETTE["primary"], PALETTE["secondary"], "#8B5CF6", "#EC4899", PALETTE["success"], PALETTE["warning"]]

        for idx, (label, val) in enumerate(data):
            slot_center = margin_left + (idx * bar_slot) + (bar_slot / 2)
            x0 = slot_center - (bar_width / 2)
            x1 = slot_center + (bar_width / 2)
            bar_h = (val / max_val) * plot_h
            y0 = margin_top + plot_h - bar_h
            y1 = margin_top + plot_h

            color = colors[idx % len(colors)]
            # Draw rounded bar or rect
            self.create_rectangle(x0, y0, x1, y1, fill=color, outline="", width=0)

            # Value label on top
            val_str = f"{val:g}{value_suffix}"
            self.create_text(slot_center, y0 - 8, text=val_str, font=FONTS["small"], fill=PALETTE["text_primary"])

            # Category label below
            # Truncate label if too long
            display_lbl = label if len(label) <= 10 else label[:8] + ".."
            self.create_text(slot_center, y1 + 14, text=display_lbl, font=FONTS["small"], fill=PALETTE["text_secondary"])


class DonutChart(tk.Canvas):
    """
    Native vector Donut Chart on Tkinter Canvas.
    Renders clean segmented arcs with an inner cutout and interactive legend.
    """

    def __init__(self, parent, title: str = "", width: int = 380, height: int = 240, bg: str = "#FFFFFF", **kwargs):
        super().__init__(parent, width=width, height=height, bg=bg, highlightthickness=0, **kwargs)
        self.chart_title = title
        self._width = width
        self._height = height
        self._bg = bg

    def draw_chart(self, data: List[Any], center_text: str = "") -> None:
        """
        data: List of (label, value) or (label, value, hex_color)
        """
        self.delete("all")
        w = self._width
        h = self._height

        if self.chart_title:
            self.create_text(w / 2, 18, text=self.chart_title, font=FONTS["heading"], fill=PALETTE["text_primary"])

        if not data:
            self.create_text(w / 2, h / 2, text="No Data", font=FONTS["body"], fill=PALETTE["text_muted"])
            return

        default_colors = ["#10B981", "#F59E0B", "#EF4444", "#6366F1", "#3B82F6", "#8B5CF6", "#EC4899"]
        normalized_data = []
        for idx, item in enumerate(data):
            if len(item) == 2:
                lbl, val = item
                col = default_colors[idx % len(default_colors)]
            else:
                lbl, val, col = item[:3]
            normalized_data.append((str(lbl), float(val), col))

        total = sum(val for _, val, _ in normalized_data)
        if total <= 0:
            self.create_text(w / 2, h / 2, text="No Data", font=FONTS["body"], fill=PALETTE["text_muted"])
            return

        cx = w * 0.35
        cy = (h + 20) / 2
        radius = min(cx - 20, (h - 60) / 2)
        inner_radius = radius * 0.55

        start_angle = 90.0
        for label, val, color in normalized_data:
            if val <= 0:
                continue
            extent = (val / total) * 360.0
            # Outer pie slice
            self.create_arc(
                cx - radius, cy - radius, cx + radius, cy + radius,
                start=start_angle, extent=extent, fill=color, outline="#FFFFFF", width=2
            )
            start_angle += extent

        # Inner cutout to create Donut
        self.create_oval(
            cx - inner_radius, cy - inner_radius, cx + inner_radius, cy + inner_radius,
            fill=self._bg, outline=""
        )

        # Center summary text
        if center_text:
            self.create_text(cx, cy, text=center_text, font=FONTS["subtitle"], fill=PALETTE["text_primary"])

        # Legend on right side
        legend_x = w * 0.65
        legend_y = 50
        for idx, (label, val, color) in enumerate(normalized_data):
            y = legend_y + (idx * 26)
            pct = (val / total) * 100.0 if total > 0 else 0
            # Color indicator
            self.create_rectangle(legend_x, y, legend_x + 12, y + 12, fill=color, outline="")
            # Text label and percentage
            text_str = f"{label}: {val:g} ({pct:.0f}%)"
            self.create_text(legend_x + 18, y + 6, text=text_str, font=FONTS["small"], fill=PALETTE["text_primary"], anchor="w")
