"""Generate QuestBeats store assets in the Vertex style.

Outputs into ../store_assets/:
  - icon_app_1024.png         (1:1 app icon)
  - icon_app_512.png
  - icon_app_256.png
  - icon_app_180.png          (Meta Quest Store icon — 180x180)
  - header_1200x630.png       (store header / social)
  - poster_2880x1620.png      (Meta Quest Store poster)

Style is taken from f1tt0n.github.io/vertex-privacy:
  bg-0 #05060a, accent #7c5cff (purple), accent-2 #22d3ee (cyan),
  radial glow gradients tilted at 15%/-10%, 95%/10%, 50%/110%,
  white-to-purple gradient on the big logo letters.
"""

import os
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT_DIR = os.path.dirname(os.path.abspath(__file__))

# --- Palette (mirrors vertex-privacy style) ---------------------------------
BG0   = (5, 6, 10)
BG1   = (11, 13, 20)
BG2   = (17, 20, 29)
LINE  = (255, 255, 255, 20)
TEXT  = (232, 236, 244)
WHITE = (255, 255, 255)
PURP  = (124, 92, 255)
PURP_LT = (185, 177, 255)
CYAN  = (34, 211, 238)


def bg(size):
    """Dark gradient background with three radial glows + grid."""
    W = H = size
    img = Image.new("RGB", (W, H), BG0)
    pix = img.load()

    def blend(p, a):
        return tuple(int(p[i] * a + BG0[i] * (1 - a)) for i in range(3))

    # Three radial gradients (sampled, no ImageDraw ellipse for speed)
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

    # Grid overlay
    grid = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(grid)
    step = max(32, W // 16)
    for x in range(0, W, step):
        gd.line([(x, 0), (x, H)], fill=(255, 255, 255, 9), width=1)
    for y in range(0, H, step):
        gd.line([(0, y), (W, y)], fill=(255, 255, 255, 9), width=1)
    # soft mask so grid fades at the edges
    mask = Image.new("L", (W, H), 0)
    md = ImageDraw.Draw(mask)
    cx, cy = W // 2, H // 2
    for y in range(H):
        for x in range(W):
            d = math.hypot(x - cx, y - cy) / (W * 0.7)
            md.point((x, y), fill=int(max(0, 1 - d) * 255))
    grid.putalpha(Image.eval(mask, lambda v: v // 3))
    img = Image.alpha_composite(img.convert("RGBA"), grid).convert("RGB")
    return img


def text_white_to_purple(draw, xy, text, font):
    """Draw text with vertical white-to-purple gradient + soft glow."""
    x, y = xy
    bbox = font.getbbox(text)
    th = bbox[3] - bbox[1]
    tw = bbox[2] - bbox[0]
    # glow pass
    glow = Image.new("RGBA", (tw + 80, th + 80), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.text((40 - bbox[0], 40 - bbox[1]), text, font=font, fill=(124, 92, 255, 220))
    glow = glow.filter(ImageFilter.GaussianBlur(18))
    # gradient pass
    grad = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    gd = ImageDraw.Draw(grad)
    for i in range(th):
        t = i / max(1, th - 1)
        if t < 0.6:
            c = (255, 255, 255, 255)
        else:
            t2 = (t - 0.6) / 0.4
            c = (
                int(PURP_LT[0] * (1 - t2) + PURP[0] * t2),
                int(PURP_LT[1] * (1 - t2) + PURP[1] * t2),
                int(PURP_LT[2] * (1 - t2) + PURP[2] * t2),
                255,
            )
        gd.line([(0, i), (tw, i)], fill=c)
    mask = Image.new("L", (tw, th), 0)
    ImageDraw.Draw(mask).text((-bbox[0], -bbox[1]), text, font=font, fill=255)
    grad.putalpha(mask)

    out = Image.new("RGBA", (tw + 80, th + 80), (0, 0, 0, 0))
    out.paste(glow, (0, 0), glow)
    out.paste(grad, (40, 40), grad)
    canvas = Image.new("RGBA", (tw + 80, th + 80), (0, 0, 0, 0))
    canvas.alpha_composite(out)
    canvas.alpha_composite(out)  # double up the glow for crispness
    draw.bitmap((x - 40, y - 40), canvas, fill=None)


def icon_notes(size):
    """Draw a faint, oversized music note as background detail."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", int(size * 0.55))
    # off-position, low alpha musical note (🎵 emoji renders the eighth-note flag)
    note = "♫"   # ♪ eighth note — uses Segoe glyph
    bbox = f.getbbox(note)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    # purple-tinted alpha
    d.text(((size - tw) / 2 - bbox[0], (size - th) / 2 - bbox[1] - int(size * 0.02)),
           note, font=f, fill=(124, 92, 255, 60))
    return img.filter(ImageFilter.GaussianBlur(size * 0.015))


def icon_play(size):
    """Draw a small rounded-square PLAY triangle marker (the ▶ icon)."""
    W = H = size
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # small rounded badge in upper-right
    bw = int(W * 0.22)
    bx = int(W * 0.74)
    by = int(W * 0.06)
    d.rounded_rectangle([bx, by, bx + bw, by + bw], radius=int(bw * 0.22),
                        fill=(124, 92, 255, 235),
                        outline=(255, 255, 255, 70), width=2)
    # triangle (slight inset for optical centering)
    pad = int(bw * 0.28)
    d.polygon([
        (bx + pad, by + pad),
        (bx + bw - pad, by + bw / 2),
        (bx + pad, by + bw - pad),
    ], fill=(255, 255, 255, 255))
    return img


def make_icon(size, out_path):
    canvas = bg(size).convert("RGBA")

    # 1) faint background music note
    canvas.alpha_composite(icon_notes(size))

    # 2) QB wordmark — vertical, oversized, gradient — slightly offset left to
    #    leave room for the PLAY badge on top-right
    f = ImageFont.truetype("C:/Windows/Fonts/seguisb.ttf", int(size * 0.46))
    d = ImageDraw.Draw(canvas)
    text = "QB"
    bbox = f.getbbox(text)
    tw = bbox[2] - bbox[0]
    x = (size - tw) / 2 - int(size * 0.04) - bbox[0]
    y = (size - (bbox[3] - bbox[1])) / 2 - bbox[1]
    text_white_to_purple(d, (int(x), int(y)), text, f)

    # 3) PLAY badge
    canvas.alpha_composite(icon_play(size))

    canvas.convert("RGB").save(out_path, "PNG", optimize=True)
    print(f"  -> {out_path}  ({size}x{size})")


def make_header(w, h, out_path):
    canvas = bg(max(w, h)).resize((w, h), Image.LANCZOS).convert("RGBA")

    # logo block, left-aligned
    f = ImageFont.truetype("C:/Windows/Fonts/seguisb.ttf", int(h * 0.34))
    d = ImageDraw.Draw(canvas)
    text = "QB"
    bbox = f.getbbox(text)
    x = int(w * 0.07)
    y = (h - (bbox[3] - bbox[1])) / 2 - bbox[1]
    text_white_to_purple(d, (x, int(y)), text, f)

    # subtitle right of logo
    f2 = ImageFont.truetype("C:/Windows/Fonts/segoeuil.ttf", int(h * 0.075))
    subtitle = "VR MUSIC PLAYER  ·  META QUEST"
    bbox2 = f2.getbbox(subtitle)
    d.text((int(w * 0.07) + (bbox[2] - bbox[0]) + int(h * 0.04),
            int(y + (bbox[3] - bbox[1]) * 0.62)),
           subtitle, font=f2, fill=(34, 211, 238, 255))

    # background note, very faint
    canvas.alpha_composite(icon_notes(max(w, h)).resize((w, h), Image.LANCZOS))

    canvas.convert("RGB").save(out_path, "PNG", optimize=True)
    print(f"  -> {out_path}  ({w}x{h})")


def main():
    print("Generating QuestBeats store assets in:", OUT_DIR)
    make_icon(1024, os.path.join(OUT_DIR, "icon_app_1024.png"))
    make_icon(512,  os.path.join(OUT_DIR, "icon_app_512.png"))
    make_icon(256,  os.path.join(OUT_DIR, "icon_app_256.png"))
    make_icon(180,  os.path.join(OUT_DIR, "icon_app_180.png"))
    make_header(1200, 630, os.path.join(OUT_DIR, "header_1200x630.png"))
    make_header(2880, 1620, os.path.join(OUT_DIR, "poster_2880x1620.png"))
    print("Done.")


if __name__ == "__main__":
    main()
