import tkinter as tk
from src.ui.styles import (
    BG_SIDEBAR, ACCENT_CYAN, TEXT_MAIN, TEXT_DIM, SIDEBAR_WIDTH,
    BUTTON_STYLE, FONT_TITLE, FONT_BOLD
)

class Sidebar(tk.Frame):
    def __init__(self, master, nav_items, on_navigate, **kwargs):
        super().__init__(master, bg=BG_SIDEBAR, width=SIDEBAR_WIDTH, **kwargs)
        self.pack_propagate(False)
        self.on_navigate = on_navigate

        # Header
        tk.Label(self, text="NETSPY", fg=ACCENT_CYAN, bg=BG_SIDEBAR, font=FONT_TITLE, pady=30).pack()

        # Nav items
        self.buttons = {}
        for item in nav_items:
            btn_frame = tk.Frame(self, bg=BG_SIDEBAR)
            btn_frame.pack(fill=tk.X)
            
            # Indicator
            indicator = tk.Frame(btn_frame, bg=BG_SIDEBAR, width=4)
            indicator.pack(side=tk.LEFT, fill=tk.Y)
            
            btn = tk.Button(
                btn_frame,
                text=f"  {item['icon']}  {item['label']}",
                command=lambda n=item["name"]: self.on_navigate(n),
                **BUTTON_STYLE
            )
            btn.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            self.buttons[item["name"]] = {"btn": btn, "ind": indicator}

            # Hover
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#1c2128"))
            btn.bind("<Leave>", lambda e, n=item["name"]: self._reset_btn_bg(n))

    def _reset_btn_bg(self, name):
        if self.active_name != name:
            self.buttons[name]["btn"].config(bg=BG_SIDEBAR)

    def set_active(self, name):
        self.active_name = name
        for n, components in self.buttons.items():
            if n == name:
                components["btn"].config(fg=ACCENT_CYAN, font=FONT_BOLD)
                components["ind"].config(bg=ACCENT_CYAN)
            else:
                components["btn"].config(fg=TEXT_MAIN, font=BUTTON_STYLE["font"], bg=BG_SIDEBAR)
                components["ind"].config(bg=BG_SIDEBAR)
