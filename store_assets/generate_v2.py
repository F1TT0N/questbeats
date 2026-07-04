"""QuestBeats v2 icon — VR music player brand.

Layout (1024x1024 base, scales cleanly):

  +-----------------------------------------+
  |  (round)              (round)           |   <- corner glow dots
  |                                         |
  |                  nutka                  |   <- background motif (music note)
  |              (soft alpha)               |
  |                                         |
  |                                         |
  |              [   >>  ]                 |   <- BIG center PLAY triangle
  |            (filled, with soft halo)     |
  |                                         |
  |                  QB                    |   <- 'QB' wordmark UNDER the button
  |                                         |
  +-----------------------------------------+

Triangles point right (play direction). Purple/cyan from vertex-privacy.
"""

import os
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT_DIR = os.path.dirname(os.path.abspath(__file__))

# Palette (vertex-privacy mirror)
BG0   = (5, 6, 10)
PURP  = (124, 92, 255)
PURP_LT = (185, 177, 255)
CYAN  = (34, 211, 238)


def bg(size):
    W = H = size
    img = Image.new("RGB", (W, H), BG0)
    pix = img.load()

    glows = [
        (int(W * 0.15), int(-H * 0.10), int(W * 0.55), (124, 92, 255), 0.18),
        (int(W * 0.95), int(H * 0.10), int(W * 0.50), (34, 211, 238), 0.14),
        (int(W * 0.50), int(H * 1.10), int(W * 0.45), (124, 92, 255), 0.10),
    ]
    for cx, cy, r, c, strength in glows:
        r2 = r * r
        for y in range(H):
            dy = y - cy
            for x in range(W):
                dx = x - cx
                d2 = dx * dx + dy * dy
                if d2 < r2:
                    a = strength * (1 - d2 / r2) ** 2
                    if a > 0.01:
                        px = pix[x, y]
                        pix[x, y] = (
                            int(px[0] * (1 - a) + c[0] * a),
                            int(px[1] * (1 - a) + c[1] * a),
                            int(px[2] * (1 - a) + c[2] * a),
                        )

    grid = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(grid)
    step = max(32, W // 16)
    for x in range(0, W, step):
        gd.line([(x, 0), (x, H)], fill=(255, 255, 255, 9), width=1)
    for y in range(0, H, step):
        gd.line([(0, y), (W, y)], fill=(255, 255, 255, 9), width=1)
    mask = Image.new("L", (W, H), 0)
    md = ImageDraw.Draw(mask)
    for y in range(H):
        for x in range(W):
            d = math.hypot(x - W // 2, y - H // 2) / (W * 0.7)
            md.point((x, y), fill=int(max(0, 1 - d) * 255))
    grid.putalpha(Image.eval(mask, lambda v: v // 3))
    img = Image.alpha_composite(img.convert("RGBA"), grid).convert("RGB")
    return img


def big_play_button(size):
    """Centered rounded-square play button with filled triangle, and a music note badge in bottom-right."""
    W = H = size
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    cx, cy = W // 2, H // 2  # Perfectly centered on the canvas

    r = int(W * 0.38)  # Play button covers ~76% of canvas
    corner_radius = int(r * 0.35)

    # 1) Main Play Button Halo / Glow (soft, blurry shadow/glow)
    halo = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    hd = ImageDraw.Draw(halo)
    hd.rounded_rectangle(
        [cx - r, cy - r, cx + r, cy + r],
        radius=corner_radius,
        fill=(124, 92, 255, 130),
    )
    halo = halo.filter(ImageFilter.GaussianBlur(W * 0.07))
    img.alpha_composite(halo)

    # 2) Draw Main Play Button
    d = ImageDraw.Draw(img)
    d.rounded_rectangle(
        [cx - r, cy - r, cx + r, cy + r],
        radius=corner_radius,
        fill=(124, 92, 255, 245),
        outline=(255, 255, 255, 60),
        width=int(W * 0.005),
    )

    # 3) Draw Centered Triangle (slight right offset for optical centering)
    tri_r = int(r * 0.55)  # size of triangle
    tri_h_box = int(tri_r * 1.05)
    pad_x = int(r * 0.12)  # optical shift to the right
    pts = [
        (cx - tri_h_box + pad_x, cy - int(tri_r * 1.10)),
        (cx + tri_h_box + pad_x - int(tri_r * 0.20), cy),
        (cx - tri_h_box + pad_x, cy + int(tri_r * 1.10)),
    ]
    d.polygon(pts, fill=(255, 255, 255, 255))

    # 4) Draw Badge Shadow in bottom right corner of play button
    br = int(W * 0.125)  # Badge radius
    bcx = cx + r - int(br * 0.65)
    bcy = cy + r - int(br * 0.65)
    
    badge_shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bsd = ImageDraw.Draw(badge_shadow)
    bsd.ellipse(
        [bcx - br - 4, bcy - br - 4, bcx + br + 8, bcy + br + 8],
        fill=(0, 0, 0, 180)
    )
    badge_shadow = badge_shadow.filter(ImageFilter.GaussianBlur(int(W * 0.015)))
    img.alpha_composite(badge_shadow)

    # 5) Draw Badge Circle (Cyan)
    d = ImageDraw.Draw(img)
    d.ellipse(
        [bcx - br, bcy - br, bcx + br, bcy + br],
        fill=(34, 211, 238, 255),
        outline=(255, 255, 255, 220),
        width=int(W * 0.006)
    )

    # 6) Draw Music Note inside the Badge
    note_font_size = int(br * 1.3)
    note_font = ImageFont.truetype("C:/Windows/Fonts/seguisym.ttf", note_font_size)
    note_text = chr(0x266A)  # ♪ eighth note
    note_bbox = note_font.getbbox(note_text)
    nw = note_bbox[2] - note_bbox[0]
    nh = note_bbox[3] - note_bbox[1]
    
    d.text(
        (bcx - nw // 2 - note_bbox[0], bcy - nh // 2 - note_bbox[1] - int(br * 0.06)),
        note_text,
        font=note_font,
        fill=(255, 255, 255, 255)
    )

    return img


def qb_wordmark(size):
    """Big '♪ QuestBeats' wordmark under the play button with high contrast."""
    W = H = size
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    
    font_size = int(W * 0.095)
    note_font = ImageFont.truetype("C:/Windows/Fonts/seguisym.ttf", font_size)
    qb_font = ImageFont.truetype("C:/Windows/Fonts/seguisb.ttf", font_size)
    
    note_text = chr(0x266A) + " "
    qb_text = "QuestBeats"
    
    note_bbox = note_font.getbbox(note_text)
    note_w = note_bbox[2] - note_bbox[0]
    note_h = note_bbox[3] - note_bbox[1]
    
    qb_bbox = qb_font.getbbox(qb_text)
    qb_w = qb_bbox[2] - qb_bbox[0]
    qb_h = qb_bbox[3] - qb_bbox[1]
    
    tw = note_w + qb_w
    th = max(note_h, qb_h)
    
    note_offset_y = 0
    qb_offset_y = 0
    if note_h > qb_h:
        qb_offset_y = (note_h - qb_h) // 2
    else:
        note_offset_y = (qb_h - note_h) // 2
        
    x = (W - tw) // 2
    y = int(H * 0.78)
    
    # 1) Drop shadow (black, soft, offset)
    shadow_offset = max(2, int(W * 0.005))
    shadow_blur = max(2, int(W * 0.006))
    
    shadow = Image.new("RGBA", (tw + 80, th + 80), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.text((40 - note_bbox[0] + shadow_offset, 40 - note_bbox[1] + note_offset_y + shadow_offset), 
            note_text, font=note_font, fill=(0, 0, 0, 255))
    sd.text((40 + note_w - qb_bbox[0] + shadow_offset, 40 - qb_bbox[1] + qb_offset_y + shadow_offset), 
            qb_text, font=qb_font, fill=(0, 0, 0, 255))
    shadow = shadow.filter(ImageFilter.GaussianBlur(shadow_blur))
    
    # 2) Text fill mask
    mask = Image.new("L", (tw, th), 0)
    md = ImageDraw.Draw(mask)
    md.text((-note_bbox[0], -note_bbox[1] + note_offset_y), note_text, font=note_font, fill=255)
    md.text((note_w - qb_bbox[0], -qb_bbox[1] + qb_offset_y), qb_text, font=qb_font, fill=255)
    
    # 3) Text gradient (white to light cyan for high contrast)
    grad = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    gd = ImageDraw.Draw(grad)
    for i in range(th):
        t = i / max(1, th - 1)
        if t < 0.3:
            c = (255, 255, 255, 255)
        else:
            t2 = (t - 0.3) / 0.7
            c = (
                int(255 * (1 - t2) + 210 * t2),
                int(255 * (1 - t2) + 230 * t2),
                int(255 * (1 - t2) + 255 * t2),
                255,
            )
        gd.line([(0, i), (tw, i)], fill=c)
    grad.putalpha(mask)
    
    out = Image.new("RGBA", (tw + 80, th + 80), (0, 0, 0, 0))
    out.paste(shadow, (0, 0), shadow)
    out.paste(grad, (40, 40), grad)
    
    img.paste(out, (x - 40, y - 40), out)
    return img, (int(x), int(y), int(tw), int(th))


def nutka_motif(size):
    """Stylized music note (🎵 / ♪) — larger, more visible than before.

    Two-note beat off the ⌈ figure, rendered in purple at ~12% opacity
    behind the play button. Reads as 'music' but never competes with center.
    """
    W = H = size
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # Larger glyph than before so it actually reads at icon scale.
    glyph = chr(0x266A)  # ♪ 8th note
    symbols_fonts = [
        "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/seguibl.ttf",
        "C:/Windows/Fonts/seguisb.ttf",
    ]
    font = None
    for fp in symbols_fonts:
        if os.path.exists(fp):
            try:
                font = ImageFont.truetype(fp, int(W * 0.42))
                break
            except Exception:
                continue
    if font is None:
        font = ImageFont.load_default()

    bbox = font.getbbox(glyph)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    cx, cy = W // 2, int(H * 0.20)  # top-third, behind + above play button
    d.text(
        (cx - tw // 2 - bbox[0], cy - th // 2 - bbox[1]),
        glyph,
        font=font,
        fill=(124, 92, 255, 70),  # higher alpha than v1 — visible
    )
    img = img.filter(ImageFilter.GaussianBlur(W * 0.012))
    return img


def make(size, out_path):
    canvas = bg(size).convert("RGBA")
    # canvas.alpha_composite(nutka_motif(size))
    canvas.alpha_composite(big_play_button(size))
    canvas.convert("RGB").save(out_path, "PNG", optimize=True)
    print(f"  -> {out_path}  ({size}x{size})")


def main():
    print("Regenerating QuestBeats v2 assets in:", OUT_DIR)
    targets = [
        (180, "icon_app_180.png"),
        (256, "icon_app_256.png"),
        (512, "icon_app_512.png"),
        (1024, "icon_app_1024.png"),
    ]
    for sz, fname in targets:
        make(sz, os.path.join(OUT_DIR, fname))


if __name__ == "__main__":
    main()
