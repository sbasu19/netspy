import tkinter as tk

class RoundedFrame(tk.Canvas):
    def __init__(self, master, bg, border_color, radius=15, **kwargs):
        super().__init__(master, bg=master["bg"], highlightthickness=0, **kwargs)
        self.radius = radius
        self.fill_color = bg
        self.border_color = border_color
        
        # Internal container for child widgets
        self.container = tk.Frame(self, bg=bg)
        self.container_window = self.create_window(0, 0, window=self.container, anchor="nw")
        
        self.bind("<Configure>", self._on_configure)

    def _on_configure(self, event):
        self.delete("bg")
        w, h = event.width, event.height
        r = self.radius
        
        # Draw slightly inside to avoid clipping (1px inset)
        self._draw_rounded_rect(1, 1, w-1, h-1, r, fill=self.fill_color, outline=self.border_color, tags="bg")
        self.tag_lower("bg")
        
        padding = 6
        self.coords(self.container_window, padding, padding)
        self.container.config(width=w - (padding*2), height=h - (padding*2))
        self.container.pack_propagate(False)

    def _draw_rounded_rect(self, x1, y1, x2, y2, r, **kwargs):
        points = [
            x1 + r, y1,
            x1 + r, y1,
            x2 - r, y1,
            x2 - r, y1,
            x2, y1,
            x2, y1 + r,
            x2, y1 + r,
            x2, y2 - r,
            x2, y2 - r,
            x2, y2,
            x2 - r, y2,
            x2 - r, y2,
            x1 + r, y2,
            x1 + r, y2,
            x1, y2,
            x1, y2 - r,
            x1, y2 - r,
            x1, y1 + r,
            x1, y1 + r,
            x1, y1,
        ]
        return self.create_polygon(points, **kwargs, smooth=True)

    def get_container(self):
        return self.container
