#!/usr/bin/env python3
"""Regenerate this fork's branding from a PNG using Pillow, without platform SDKs."""
import argparse
import base64
from collections import Counter
from io import BytesIO
import json
from pathlib import Path
import re
import struct
from PIL import Image, ImageChops, ImageDraw, ImageOps

ROOT = Path(__file__).resolve().parents[1]
SIZES = (16, 24, 32, 48, 64, 128, 256)
GENERATED = set()


def destination(relative):
    path = ROOT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    GENERATED.add(relative)
    return path


def png(relative, image):
    image.save(destination(relative), format='PNG', optimize=True)


def square(image, size):
    return image.resize((size, size), Image.Resampling.LANCZOS)


def ico(relative, image):
    # Use Pillow's DIB encoder, then add explicit AND masks and planes=1.
    # No ICO frame is PNG compressed: this also supports older resource compilers.
    stream = BytesIO()
    image.save(stream, format='ICO', sizes=[(s, s) for s in SIZES], bitmap_format='bmp')
    data = stream.getvalue()
    count = struct.unpack_from('<H', data, 4)[0]
    entries, frames = [], []
    offset = 6 + 16 * count
    for i in range(count):
        w, h, colors, reserved, planes, bits, length, start = struct.unpack_from(
            '<BBBBHHII', data, 6 + 16 * i)
        width, height = w or 256, h or 256
        frame = bytearray(data[start:start + length])
        header_size = struct.unpack_from('<I', frame)[0]
        stride = ((width * bits + 31) // 32) * 4
        mask_stride = ((width + 31) // 32) * 4
        expected = header_size + stride * height
        if len(frame) == expected:
            # All app icons are flattened onto the supplied background.
            frame.extend(bytes(mask_stride * height))
        if len(frame) != expected + mask_stride * height:
            raise ValueError('Unexpected Pillow ICO frame layout')
        entries.append(struct.pack('<BBBBHHII', w, h, colors, reserved,
                                   1, bits, len(frame), offset))
        frames.append(frame)
        offset += len(frame)
    destination(relative).write_bytes(struct.pack('<HHH', 0, 1, count)
                                     + b''.join(entries) + b''.join(frames))


def foreground_mask(image):
    # Derive this supplied flat-background logo's silhouette from its corner.
    bg = image.getpixel((0, 0))
    channels = ImageChops.difference(image, Image.new('RGB', image.size, bg)).split()
    return ImageChops.lighter(ImageChops.lighter(channels[0], channels[1]),
                             channels[2]).point(lambda x: 255 if x > 70 else 0)


def silhouette(mask, size, color, content_size):
    content = ImageOps.contain(mask.crop(mask.getbbox()), (content_size, content_size),
                              Image.Resampling.LANCZOS)
    alpha = Image.new('L', (size, size), 0)
    alpha.paste(content, ((size-content.width)//2, (size-content.height)//2))
    out = Image.new('RGBA', (size, size), color)
    out.putalpha(alpha)
    return out


def svg(relative, image, mask, width=None, height=None):
    # Pure vector rectangles support flutter_svg; no embedded raster images.
    bg, fg = [entry[0] for entry in Counter(image.getdata()).most_common(2)]
    active, rectangles = {}, []
    for y in range(mask.height + 1):
        runs = set()
        if y < mask.height:
            row = list(mask.crop((0, y, mask.width, y+1)).getdata())
            x = 0
            while x < len(row):
                if not row[x]:
                    x += 1
                    continue
                start = x
                while x < len(row) and row[x]:
                    x += 1
                runs.add((start, x))
        for run in list(active):
            if run not in runs:
                first = active.pop(run)
                rectangles.append((run[0], first, run[1]-run[0], y-first))
        for run in sorted(runs):
            active.setdefault(run, y)
    w, h = width or image.width, height or image.height
    side = min(w, h)
    color = lambda rgb: '#%02x%02x%02x' % rgb
    body = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
            f'<rect width="{w}" height="{h}" fill="{color(bg)}"/>',
            f'<g transform="translate({(w-side)/2} {(h-side)/2}) scale({side/image.width})" fill="{color(fg)}">']
    body += [f'<rect x="{x}" y="{y}" width="{rw}" height="{rh}"/>' for x,y,rw,rh in rectangles]
    destination(relative).write_text('\n'.join(body + ['</g></svg>', '']), encoding='utf-8')


def replace_sciter_icons(image):
    path = ROOT / 'src/ui.rs'
    text = path.read_text(encoding='utf-8')
    start = text.index('pub fn get_icon() -> String {')
    end = text.index('\n}', start) + 2
    block = text[start:end]
    padded = Image.new('RGBA', (160, 160), (0, 0, 0, 0))
    padded.paste(square(image, 128), (16, 16))
    images = []
    for im in (square(padded, 128), square(image, 128)):
        stream = BytesIO()
        im.save(stream, format='PNG')
        images.append('data:image/png;base64,' + base64.b64encode(stream.getvalue()).decode())
    pattern = r'data:image/png;base64,[A-Za-z0-9+/=]+'
    if len(re.findall(pattern, block)) != 2:
        raise ValueError('Sciter get_icon() changed; review before regenerating')
    it = iter(images)
    block = re.sub(pattern, lambda _: next(it), block)
    path.write_text(text[:start] + block + text[end:], encoding='utf-8')


def update_gitignore():
    path = ROOT / '.gitignore'
    marker = '# BEGIN custom branding assets'
    text = re.sub(r'(?m)^# BEGIN custom branding assets\n.*?^# END custom branding assets\n?',
                  '', path.read_text(encoding='utf-8'), flags=re.DOTALL).rstrip() + '\n\n'
    images = sorted(p for p in GENERATED if p.endswith(('.png', '.svg')))
    path.write_text(text + marker + '\n' + '\n'.join('!/' + p for p in images)
                    + '\n# END custom branding assets\n', encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', nargs='?', type=Path, default=ROOT / 'res/branding-source.png')
    args = parser.parse_args()
    with Image.open(args.source) as original:
        original.load()
        bg = original.convert('RGB').getpixel((0, 0))
        rgba = original.convert('RGBA')
        flattened = Image.new('RGBA', rgba.size, bg + (255,))
        flattened.alpha_composite(rgba)
        source = flattened.convert('RGB')
    if source.width != source.height:
        source = ImageOps.pad(source, (max(source.size),) * 2, color=bg)
    mask = foreground_mask(source)
    if not mask.getbbox():
        raise ValueError('The logo must have a visible mark on a flat corner background')
    fg = Counter(source.getdata()).most_common(2)[1][0]
    png('res/branding-source.png', source)
    rgba = source.convert('RGBA')
    for name, size in {'icon.png':1024, 'mac-icon.png':1024, 'logo.png':source.width,
                       'logo_light.png':source.width, 'logo_dark.png':source.width,
                       '32x32.png':32, '64x64.png':64, '128x128.png':128, '128x128@2x.png':256}.items():
        png('res/' + name, square(rgba, size))
    for name in ('icon.png', 'logo.png', 'logo_light.png', 'logo_dark.png'):
        png('flutter/assets/' + name, square(rgba, 1024 if name == 'icon.png' else source.width))
    for path in ('res/icon.ico', 'res/tray-icon.ico',
                 'flutter/windows/runner/resources/app_icon.ico', 'flutter/assets/icon.ico'):
        ico(path, square(rgba, 256))
    icon = square(rgba, 1024)
    for path in ('res/icon.icns', 'flutter/macos/Runner/AppIcon.icns'):
        icon.save(destination(path), format='ICNS',
                  append_images=[square(icon, s) for s in (32,64,128,256,512)])
    for name, color in (('mac-tray-dark-x2.png','black'), ('mac-tray-light-x2.png','white')):
        png('res/' + name, silhouette(mask, 48, color, 32))
    png('flutter/assets/mac-tray.png', silhouette(mask, 48, 'black', 32))
    for path in ('res/logo.svg','res/scalable.svg','res/design.svg','flutter/assets/icon.svg'):
        svg(path, source, mask)
    svg('res/logo-header.svg', source, mask, 1000, 287)
    svg('res/rustdesk-banner.svg', source, mask, 454, 104)
    android = 'flutter/android/app/src/main/res/'
    for density,size in {'mdpi':48,'hdpi':72,'xhdpi':96,'xxhdpi':144,'xxxhdpi':192}.items():
        folder = android + f'mipmap-{density}/'
        png(folder + 'ic_launcher.png', square(rgba, size))
        rounded = square(rgba, size)
        alpha = Image.new('L', (size*4, size*4), 0)
        ImageDraw.Draw(alpha).ellipse((0,0,size*4-1,size*4-1), fill=255)
        rounded.putalpha(alpha.resize((size,size), Image.Resampling.LANCZOS))
        png(folder + 'ic_launcher_round.png', rounded)
        adaptive_size = size * 108 // 48
        # A 46 dp square fits inside Android's circular 66 dp safe zone.
        for name,color in (('ic_launcher_foreground.png',fg),('ic_launcher_monochrome.png','white')):
            png(folder + name, silhouette(mask, adaptive_size, color, round(adaptive_size*46/108)))
        png(folder + 'ic_stat_logo.png', silhouette(mask, size//2, 'white', round(size*20/48)))
    for name in ('ic_launcher.xml','ic_launcher_round.xml'):
        path = ROOT / android / 'mipmap-anydpi-v26' / name
        path.write_text(path.read_text().replace(
            '<monochrome android:drawable="@mipmap/ic_launcher_foreground"/>',
            '<monochrome android:drawable="@mipmap/ic_launcher_monochrome"/>'), encoding='utf-8')
    path = ROOT / android / 'values/ic_launcher_background.xml'
    path.write_text(re.sub(r'(<color name="ic_launcher_background">)[^<]+',
                          lambda m: m[1] + '#%02x%02x%02x' % bg, path.read_text()), encoding='utf-8')
    base = 'flutter/ios/Runner/Assets.xcassets/AppIcon.appiconset/'
    for entry in json.loads((ROOT / base / 'Contents.json').read_text())['images']:
        if 'filename' in entry:
            size = round(float(entry['size'].split('x')[0]) * float(entry['scale'].rstrip('x')))
            png(base + entry['filename'], square(source, size))
    png('fastlane/metadata/android/en-US/images/icon.png', square(rgba, 512))
    replace_sciter_icons(rgba)
    # A macOS template uses alpha only; the opaque app icon would become a square.
    path = ROOT / 'src/tray.rs'
    path.write_text(path.read_text().replace(
        '../Frameworks/App.framework/Resources/flutter_assets/assets/icon.png',
        '../Frameworks/App.framework/Resources/flutter_assets/assets/mac-tray.png'), encoding='utf-8')
    update_gitignore()
    destination('res/branding-manifest.json').write_text(json.dumps(
        {'source':'res/branding-source.png', 'assets':sorted(GENERATED - {'res/branding-manifest.json'})},
        ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'Generated {len(GENERATED)-1} branding assets; updated Sciter, macOS tray and Git rules.')


if __name__ == '__main__':
    main()
