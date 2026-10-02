#!/usr/bin/env python3
"""Generate extension icons at 16, 48, and 128px.

Draws a YouTube-style red rounded-rect with two white filled forward
triangles (fast-forward ▶▶). Pure Python — no dependencies beyond
the standard library. Outputs raw RGBA PNGs using zlib + struct.
"""

import struct
import zlib
import os
import math

# ── PNG writer (no dependencies) ──────────────────────────────────────

def create_png(width, height, pixels):
    """Create a PNG file from raw RGBA pixel data."""
    def chunk(chunk_type, data):
        c = chunk_type + data
        return struct.pack('>I', len(data)) + c + struct.pack('>I', zlib.crc32(c) & 0xffffffff)

    # IHDR
    ihdr = struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0)  # 8-bit RGBA

    # IDAT — raw image data with filter byte 0 per row
    raw = b''
    for y in range(height):
        raw += b'\x00'  # filter: none
        for x in range(width):
            idx = (y * width + x) * 4
            raw += bytes(pixels[idx:idx+4])

    compressed = zlib.compress(raw, 9)

    png = b'\x89PNG\r\n\x1a\n'
    png += chunk(b'IHDR', ihdr)
    png += chunk(b'IDAT', compressed)
    png += chunk(b'IEND', b'')
    return png


# ── Drawing helpers ───────────────────────────────────────────────────

def sdf_rounded_rect(px, py, cx, cy, hw, hh, r):
    """Signed distance field for a rounded rectangle centered at (cx,cy)
    with half-width hw, half-height hh, and corner radius r.
    Returns negative values inside, positive outside."""
    dx = abs(px - cx) - hw + r
    dy = abs(py - cy) - hh + r
    outside = math.sqrt(max(dx, 0)**2 + max(dy, 0)**2) - r
    inside = min(max(dx, dy), 0)
    return outside + inside


def point_in_triangle(px, py, x1, y1, x2, y2, x3, y3):
    """Return a coverage value (0.0-1.0) for how much pixel (px,py) is
    inside the triangle. Uses sub-pixel sampling for anti-aliasing."""
    def sign(ax, ay, bx, by, cx, cy):
        return (ax - cx) * (by - cy) - (bx - cx) * (ay - cy)

    def inside(tx, ty):
        d1 = sign(tx, ty, x1, y1, x2, y2)
        d2 = sign(tx, ty, x2, y2, x3, y3)
        d3 = sign(tx, ty, x3, y3, x1, y1)
        has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
        has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)
        return not (has_neg and has_pos)

    # 4x4 sub-pixel grid for anti-aliasing
    samples = 4
    count = 0
    for sy in range(samples):
        for sx in range(samples):
            spx = px + (sx + 0.5) / samples
            spy = py + (sy + 0.5) / samples
            if inside(spx, spy):
                count += 1
    return count / (samples * samples)


def blend_pixel(pixels, idx, color, alpha):
    """Alpha-blend a color onto existing pixel data."""
    if alpha <= 0:
        return
    src_r, src_g, src_b, src_a = color
    src_a = int(src_a * alpha)

    dst_r = pixels[idx]
    dst_g = pixels[idx + 1]
    dst_b = pixels[idx + 2]
    dst_a = pixels[idx + 3]

    if dst_a == 0:
        pixels[idx] = src_r
        pixels[idx + 1] = src_g
        pixels[idx + 2] = src_b
        pixels[idx + 3] = src_a
    else:
        # Standard alpha compositing
        sa = src_a / 255.0
        da = dst_a / 255.0
        out_a = sa + da * (1 - sa)
        if out_a > 0:
            pixels[idx] = int((src_r * sa + dst_r * da * (1 - sa)) / out_a)
            pixels[idx + 1] = int((src_g * sa + dst_g * da * (1 - sa)) / out_a)
            pixels[idx + 2] = int((src_b * sa + dst_b * da * (1 - sa)) / out_a)
            pixels[idx + 3] = int(out_a * 255)


def generate_icon(size):
    """Generate a single icon at the given size."""
    pixels = [0] * (size * size * 4)  # transparent

    # Colors — YouTube red with white arrows
    red = (255, 0, 0, 255)        # #FF0000 YouTube red
    white = (255, 255, 255, 255)  # #FFFFFF

    # The red rounded rectangle — YouTube-style proportions
    # Wider than tall, like the YouTube play button logo
    rect_w = size               # full width
    rect_h = size * 0.72        # ~72% height for YouTube proportions
    rect_cx = size / 2
    rect_cy = size / 2
    rect_hw = rect_w / 2        # half-width
    rect_hh = rect_h / 2        # half-height
    corner_r = size * 0.18      # generous corner radius

    # Draw rounded rectangle with anti-aliased edges
    for y in range(size):
        for x in range(size):
            d = sdf_rounded_rect(x + 0.5, y + 0.5, rect_cx, rect_cy, rect_hw, rect_hh, corner_r)
            if d < -1.0:
                alpha = 1.0
            elif d < 1.0:
                alpha = 0.5 - d * 0.5  # smooth edge
            else:
                alpha = 0.0
            if alpha > 0:
                idx = (y * size + x) * 4
                blend_pixel(pixels, idx, red, alpha)

    # Two forward-pointing filled triangles (▶▶ fast-forward)
    # Position them centered within the rectangle
    top = rect_cy - rect_hh * 0.55     # vertical extent
    bot = rect_cy + rect_hh * 0.55
    mid_y = rect_cy

    # Total horizontal span for both triangles
    total_w = size * 0.55
    gap = size * 0.02                   # slight overlap/gap between triangles
    tri_w = (total_w - gap) / 2

    # Center the pair horizontally
    start_x = rect_cx - total_w / 2

    # Triangle 1 (left)
    t1_left = start_x
    t1_right = start_x + tri_w
    tri1 = [
        (t1_left, top),
        (t1_right, mid_y),
        (t1_left, bot),
    ]

    # Triangle 2 (right)
    t2_left = start_x + tri_w + gap
    t2_right = t2_left + tri_w
    tri2 = [
        (t2_left, top),
        (t2_right, mid_y),
        (t2_left, bot),
    ]

    # Draw triangles with anti-aliasing
    for y in range(size):
        for x in range(size):
            idx = (y * size + x) * 4
            # Only draw on pixels that are part of the red rect
            if pixels[idx + 3] == 0:
                continue

            cov1 = point_in_triangle(x, y, *tri1[0], *tri1[1], *tri1[2])
            cov2 = point_in_triangle(x, y, *tri2[0], *tri2[1], *tri2[2])
            cov = max(cov1, cov2)

            if cov > 0:
                blend_pixel(pixels, idx, white, cov)

    return create_png(size, size, pixels)


# ── Main ──────────────────────────────────────────────────────────────

if __name__ == '__main__':
    script_dir = os.path.dirname(os.path.abspath(__file__))
    icons_dir = os.path.join(script_dir, 'icons')
    os.makedirs(icons_dir, exist_ok=True)

    for s in (16, 48, 128):
        data = generate_icon(s)
        path = os.path.join(icons_dir, f'icon-{s}.png')
        with open(path, 'wb') as f:
            f.write(data)
        print(f'  ✅ icons/icon-{s}.png ({s}×{s}px, {len(data)} bytes)')

    print('\n🎉 Icons generated!')
