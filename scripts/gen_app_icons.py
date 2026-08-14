# -*- coding: utf-8 -*-
"""生成 App 启动图标到 TEMP，再拷贝进工作区（工作区 python 直写受限）。"""
from PIL import Image, ImageDraw
import os, shutil, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TMP = os.path.join(tempfile.gettempdir(), "lasa_icons")
os.makedirs(TMP, exist_ok=True)
SIZES = {"mdpi": 48, "hdpi": 72, "xhdpi": 96, "xxhdpi": 144, "xxxhdpi": 192}

def make_icon(px):
    img = Image.new("RGBA", (px, px), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    r = int(px * 0.18)
    d.rounded_rectangle([0, 0, px, px], radius=r, fill=(27, 122, 74, 255))
    d.rounded_rectangle([0, int(px * 0.55), px, px], radius=r, fill=(21, 99, 60, 255))
    d.rectangle([0, int(px * 0.4), px, int(px * 0.6)], fill=(27, 122, 74, 255))
    d.polygon([(px * 0.12, px * 0.78), (px * 0.38, px * 0.30), (px * 0.62, px * 0.78)], fill=(240, 250, 244, 255))
    d.polygon([(px * 0.46, px * 0.78), (px * 0.66, px * 0.46), (px * 0.88, px * 0.78)], fill=(210, 235, 220, 255))
    d.polygon([(px * 0.38, px * 0.30), (px * 0.31, px * 0.44), (px * 0.45, px * 0.44)], fill=(255, 255, 255, 255))
    tx = px * 0.24
    d.rectangle([tx - px * 0.015, px * 0.72, tx + px * 0.015, px * 0.82], fill=(90, 60, 35, 255))
    d.ellipse([tx - px * 0.06, px * 0.60, tx + px * 0.06, px * 0.74], fill=(46, 158, 99, 255))
    return img

for dpi, px in SIZES.items():
    src = os.path.join(TMP, f"ic_launcher_{dpi}.png")
    make_icon(px).save(src)
    dst_dir = os.path.join(ROOT, "android-app", "app", "src", "main", "res", f"mipmap-{dpi}")
    shutil.copy(src, os.path.join(dst_dir, "ic_launcher.png"))
    print("OK", f"mipmap-{dpi}/ic_launcher.png", px)
