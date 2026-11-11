import datetime
import json
import os
import sys
from PIL import Image, ImageChops

# Approved baseline (docs/INTENTIONAL_DIFFERENCES.md, I19). For every screen with approved differences
# tools/snapshots/pixel_approved/ holds <screen>.png: the branch screenshot cropped to the approved
# bounding box, alpha 255 on approved pixels and 0 elsewhere. A pixel that differs from main passes
# only if it is approved AND the branch pixel equals the approved one; everything else is new -> exit 1.
#   python tools/pixel_diff.py                         -> uses the baseline if meta.json exists
#   python tools/pixel_diff.py --no-approved           -> strict mode, every differing pixel counts
#   APPROVED_REFERENCE=404012d python tools/pixel_diff.py --write-approved   -> (re)capture the baseline
# PIXEL_APPROVED_DIR=<dir> overrides the baseline location.
APPROVED_DIR = os.environ.get('PIXEL_APPROVED_DIR') or os.path.join(os.path.dirname(__file__), 'snapshots', 'pixel_approved')
WRITE_APPROVED = '--write-approved' in sys.argv
NO_APPROVED = '--no-approved' in sys.argv


def diff_mask(im1, im2):
    """'L' mask, 255 where any RGB channel differs (strict zero tolerance), else 0."""
    r, g, b = ImageChops.difference(im1, im2).split()
    return ImageChops.lighter(ImageChops.lighter(r, g), b).point(lambda v: 255 if v else 0)


def count_on(mask):
    return mask.histogram()[255]


def approved_ok_mask(ref, approved_png, bbox):
    """Full-size 'L' mask: 255 where the pixel is approved and the branch shows the approved colour."""
    ok = Image.new('L', ref.size, 0)
    alpha = approved_png.getchannel('A')
    same = ImageChops.invert(diff_mask(ref.crop(bbox), approved_png.convert('RGB')))
    ok.paste(ImageChops.multiply(alpha, same), bbox[:2])
    return ok

def compare_images(img1_path, img2_path, diff_out_path):
    im1 = Image.open(img1_path).convert('RGB')
    im2 = Image.open(img2_path).convert('RGB')

    if im1.size != im2.size:
        return {
            'error': f'Size mismatch: {im1.size} vs {im2.size}',
            'total_pixels': max(im1.size[0]*im1.size[1], im2.size[0]*im2.size[1]),
            'diff_pixels': -1,
            'diff_percent': 100.0,
            'bbox': None
        }

    width, height = im1.size
    total_pixels = width * height

    # Difference image
    diff = ImageChops.difference(im1, im2)
    bbox = diff.getbbox()

    if not bbox:
        return {
            'total_pixels': total_pixels,
            'diff_pixels': 0,
            'diff_percent': 0.0,
            'bbox': '0 differences (identical)'
        }

    # Count exact mismatched pixels (with non-zero RGB delta)
    diff_data = diff.getdata()
    mismatched = 0
    # Create highlighted diff image (red highlight over dimmed base)
    highlight = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    h_data = []

    for pixel in diff_data:
        # Strict zero tolerance: any non-zero delta in RGB is counted as mismatched
        if pixel[0] > 0 or pixel[1] > 0 or pixel[2] > 0:
            mismatched += 1
            h_data.append((255, 0, 0, 255))
        else:
            h_data.append((0, 0, 0, 0))

    highlight.putdata(h_data)
    im_base = im1.convert('RGB')
    im_base = Image.blend(im_base, Image.new('RGB', (width, height), (255, 255, 255)), 0.3)
    im_base.paste(highlight, (0, 0), highlight)
    im_base.save(diff_out_path)

    percent = round((mismatched / total_pixels) * 100, 4)
    return {
        'total_pixels': total_pixels,
        'diff_pixels': mismatched,
        'diff_percent': percent,
        'bbox': f'({bbox[0]}, {bbox[1]}) to ({bbox[2]}, {bbox[3]})'
    }

def main():
    # Windows consoles/pipes default to cp1251: the report has ✓/✗, keep the log readable as UTF-8.
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except (AttributeError, ValueError):
        pass
    screenshots_dir = os.path.join(os.path.dirname(__file__), '..', 'docs', 'qa', 'evidence', 'screenshots')
    pairs = [
        ('desktop_catalog', 'main_desktop_catalog.png', 'refactor_desktop_catalog.png'),
        ('desktop_pretest', 'main_desktop_pretest.png', 'refactor_desktop_pretest.png'),
        ('desktop_report', 'main_desktop_report.png', 'refactor_desktop_report.png'),
        ('mobile_catalog', 'main_mobile_catalog.png', 'refactor_mobile_catalog.png'),
        ('mobile_pretest', 'main_mobile_pretest.png', 'refactor_mobile_pretest.png'),
        ('mobile_report', 'main_mobile_report.png', 'refactor_mobile_report.png'),
        ('mobile_solved_col', 'main_mobile_solved_col.png', 'refactor_mobile_solved_col.png'),
        ('desktop_sync_modal', 'main_desktop_sync_modal.png', 'refactor_desktop_sync_modal.png'),
        ('mobile_sync_modal', 'main_mobile_sync_modal.png', 'refactor_mobile_sync_modal.png'),
        ('desktop_pdf_import', 'main_desktop_pdf_import.png', 'refactor_desktop_pdf_import.png'),
        ('mobile_pdf_import', 'main_mobile_pdf_import.png', 'refactor_mobile_pdf_import.png'),
        ('desktop_exercise', 'main_desktop_exercise.png', 'refactor_desktop_exercise.png'),
        ('mobile_exercise', 'main_mobile_exercise.png', 'refactor_mobile_exercise.png'),
        ('desktop_analysis', 'main_desktop_analysis.png', 'refactor_desktop_analysis.png'),
        ('mobile_analysis', 'main_mobile_analysis.png', 'refactor_mobile_analysis.png'),
    ]

    meta_path = os.path.join(APPROVED_DIR, 'meta.json')
    approved_meta = None
    if not NO_APPROVED and not WRITE_APPROVED and os.path.exists(meta_path):
        with open(meta_path, encoding='utf-8') as fh:
            approved_meta = json.load(fh)
        print(f"Approved baseline: {os.path.relpath(APPROVED_DIR)} (reference: {approved_meta.get('reference', 'unknown')}, "
              f"{sum(1 for v in approved_meta['screens'].values() if v['diff_pixels'])} screens with approved pixels)")
        print()

    print('| Экран / Виджет | Разрешение | Всего пикселей | Отличающихся пикселей | % расхождения | Область различий (BBox) | Одобрено | Новых |')
    print('| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |')

    all_passed = True
    missing = False
    new_meta = {'screens': {}}
    for name, f_main, f_ref in pairs:
        p_main = os.path.join(screenshots_dir, f_main)
        p_ref = os.path.join(screenshots_dir, f_ref)
        p_diff = os.path.join(screenshots_dir, f'diff_{name}.png')

        if not os.path.exists(p_main) or not os.path.exists(p_ref):
            print(f'| {name} | - | - | Файлы не найдены | - | - | - | - |')
            missing = True
            continue

        res = compare_images(p_main, p_ref, p_diff)
        im_main = Image.open(p_main).convert('RGB')
        im_ref = Image.open(p_ref).convert('RGB')
        w, h = im_main.size
        if im_main.size != im_ref.size:
            print(f"| `{name}` | {w}x{h} | - | {res.get('error')} | - | - | - | - |")
            all_passed = False
            continue

        mask = diff_mask(im_main, im_ref)
        diff_pixels = count_on(mask)
        approved_col, new_col = '-', str(diff_pixels)
        new_pixels = diff_pixels

        if WRITE_APPROVED:
            bbox = mask.getbbox()
            entry = {'size': [w, h], 'diff_pixels': diff_pixels, 'bbox': list(bbox) if bbox else None}
            png_path = os.path.join(APPROVED_DIR, f'{name}.png')
            if bbox:
                os.makedirs(APPROVED_DIR, exist_ok=True)
                crop = im_ref.crop(bbox).convert('RGBA')
                crop.putalpha(mask.crop(bbox))
                crop.save(png_path, optimize=True)
            elif os.path.exists(png_path):
                os.remove(png_path)
            new_meta['screens'][name] = entry
            approved_col, new_col = str(diff_pixels), '0'
            new_pixels = 0
        elif approved_meta is not None:
            entry = approved_meta['screens'].get(name)
            ok_pixels = 0
            if entry and entry.get('bbox') and entry.get('size') == [w, h]:
                approved_png = Image.open(os.path.join(APPROVED_DIR, f'{name}.png')).convert('RGBA')
                ok = approved_ok_mask(im_ref, approved_png, tuple(entry['bbox']))
                ok_pixels = count_on(ImageChops.multiply(mask, ok))
                new_pixels = count_on(ImageChops.subtract(mask, ok))
            approved_col, new_col = str(ok_pixels), str(new_pixels)

        print(f"| `{name}` | {w}x{h} | {res['total_pixels']:,} | {res['diff_pixels']:,} | **{res['diff_percent']}%** | {res['bbox']} | {approved_col} | {new_col} |")
        if new_pixels > 0:
            all_passed = False

    if WRITE_APPROVED:
        new_meta = {
            'reference': os.environ.get('APPROVED_REFERENCE', 'unknown'),
            'captured_at': datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds'),
            'note': 'Approved pixel differences vs the reference served on :8001 (main_*.png). '
                    'See docs/INTENTIONAL_DIFFERENCES.md (I19). Recapture after the reference changes.',
            **new_meta,
        }
        if missing:
            print()
            print('Не все скриншоты найдены — эталон не записан.')
            sys.exit(1)
        os.makedirs(APPROVED_DIR, exist_ok=True)
        with open(meta_path, 'w', encoding='utf-8') as fh:
            json.dump(new_meta, fh, ensure_ascii=False, indent=1)
            fh.write('\n')
        print()
        print(f"Approved baseline written: {APPROVED_DIR} (reference: {new_meta['reference']}).")
        sys.exit(0)

    print()
    if all_passed and not missing:
        print('✓ 0 NEW PIXEL DIFFERENCES' + (' outside the approved baseline.' if approved_meta is not None else ' (identical).'))
    else:
        print('✗ NEW PIXEL DIFFERENCES FOUND (see the «Новых» column).')

    if not all_passed:
        sys.exit(1)
    sys.exit(0)

if __name__ == '__main__':
    main()

