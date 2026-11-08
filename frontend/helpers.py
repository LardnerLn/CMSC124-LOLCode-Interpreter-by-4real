# Shared helpers: window-wide colors/fonts and canvas drawing functions.

# window-wide colors and fonts
BG = "#262626"      # window background
PANEL = "#DFD6BB"   # default beige panel body
TEXT_DARK = "#2B2B2B"
FONT = "Helvetica"


# hardcoded round rectangle in tkinter
def round_rect(canvas, x1, y1, x2, y2, r, **kw):
    # Draw a rounded rectangle on a tk.Canvas and return its item id.
    pts = [x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r, x2, y2 - r, x2, y2,
           x2 - r, y2, x1 + r, y2, x1, y2, x1, y2 - r, x1, y1 + r, x1, y1]
    return canvas.create_polygon(pts, smooth=True, **kw)