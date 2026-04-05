# --- Theme Colors (Cyberpunk Dark) ---
BG_DARK = "#0b0e14"       # Deep black/charcoal
BG_SIDEBAR = "#161b22"   # Slightly lighter dark
BG_CARD = "#1c2128"      # Card background
ACCENT_CYAN = "#00f2ff"  # Neon Cyan
ACCENT_GREEN = "#00ff41" # Matrix Green
ACCENT_PURPLE = "#7000ff" # Deep Purple
ACCENT_BLUE = "#3b82f6"   # Soft Blue
TEXT_MAIN = "#e6edf3"    # Main text color
TEXT_DIM = "#8b949e"     # Dimmed text color
ANOMALY_RED = "#ff3e3e"  # Alert/Anomaly color

# --- Fonts ---
FONT_TITLE = ("Arial", 18, "bold")
FONT_SUBTITLE = ("Arial", 14, "bold")
FONT_NORMAL = ("Arial", 10)
FONT_BOLD = ("Arial", 10, "bold")
FONT_MONO = ("Courier New", 10)

# --- UI Constants ---
SIDEBAR_WIDTH = 200
BORDER_RADIUS = 20

# --- Common UI Styles ---
BUTTON_STYLE = {
    "bg": BG_SIDEBAR,
    "fg": TEXT_MAIN,
    "activebackground": ACCENT_CYAN,
    "activeforeground": BG_DARK,
    "relief": "flat",
    "padx": 20,
    "pady": 12,
    "font": FONT_NORMAL,
    "anchor": "w",
}
