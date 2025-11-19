#!/usr/bin/env python3
"""Render PlantUML file via the public PlantUML server.

Usage:
  python docs/render_plantuml.py docs/architecture.puml docs/architecture.png

This script encodes the PlantUML source using the same algorithm as the PlantUML server
and downloads the generated PNG to the output path.

Warning: this sends the diagram text to the public PlantUML server (https://www.plantuml.com).
Don't use it for private/confidential diagrams unless acceptable.
"""
import sys
import zlib
import urllib.request

_encode_table = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_"

def _append3bytes(b1, b2, b3):
    c1 = (b1 >> 2) & 0x3F
    c2 = ((b1 & 0x3) << 4) | ((b2 >> 4) & 0xF)
    c3 = ((b2 & 0xF) << 2) | ((b3 >> 6) & 0x3)
    c4 = b3 & 0x3F
    return _encode_table[c1] + _encode_table[c2] + _encode_table[c3] + _encode_table[c4]

def plantuml_encode(plantuml_text: str) -> str:
    compressed = zlib.compress(plantuml_text.encode('utf-8'))
    # strip zlib header and checksum (RFC1950 wrapper)
    data = compressed[2:-4]
    res = []
    i = 0
    while i < len(data):
        b1 = data[i]
        b2 = data[i+1] if i+1 < len(data) else 0
        b3 = data[i+2] if i+2 < len(data) else 0
        res.append(_append3bytes(b1, b2, b3))
        i += 3
    return ''.join(res)

def render(puml_path: str, out_png: str, server: str = 'https://www.plantuml.com'):
    with open(puml_path, 'r', encoding='utf-8') as f:
        text = f.read()

    encoded = plantuml_encode(text)
    url = f"{server}/plantuml/png/{encoded}"

    print(f"Requesting: {url}")
    with urllib.request.urlopen(url) as resp:
        if resp.status != 200:
            raise SystemExit(f"Server returned status {resp.status}")
        data = resp.read()

    with open(out_png, 'wb') as f:
        f.write(data)

    print(f"Saved: {out_png}")


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python docs/render_plantuml.py <input.puml> <output.png>")
        raise SystemExit(2)
    render(sys.argv[1], sys.argv[2])
