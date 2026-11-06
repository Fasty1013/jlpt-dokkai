import os
import sys
from PIL import Image, ImageChops

def compare_images(img1_path, img2_path, diff_out_path):
    im1 = Image.open(img1_path).convert('RGBA')
    im2 = Image.open(img2_path).convert('RGBA')

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
        # Check if R, G, B, or A differ significantly (> 2 threshold to filter micro subpixel anti-aliasing)
        if pixel[0] > 2 or pixel[1] > 2 or pixel[2] > 2:
            mismatched += 1
            h_data.append((255, 0, 0, 255))
        else:
            h_data.append((0, 0, 0, 0))

    highlight.putdata(h_data)
    im_base = im1.convert('RGB')
    im_base = Image.blend(im_base, Image.new('RGB', (width, height), (255, 255, 255)), 0.3)
    im_base.paste(highlight, (0, 0), highlight)
    im_base.save(diff_out_path)

    percent = round((mismatched / total_pixels) * 100, 3)
    return {
        'total_pixels': total_pixels,
        'diff_pixels': mismatched,
        'diff_percent': percent,
        'bbox': f'({bbox[0]}, {bbox[1]}) to ({bbox[2]}, {bbox[3]})'
    }

def main():
    screenshots_dir = os.path.join(os.path.dirname(__file__), '..', 'docs', 'qa', 'evidence', 'screenshots')
    pairs = [
        ('desktop_catalog', 'main_desktop_catalog.png', 'refactor_desktop_catalog.png'),
        ('desktop_pretest', 'main_desktop_pretest.png', 'refactor_desktop_pretest.png'),
        ('desktop_report', 'main_desktop_report.png', 'refactor_desktop_report.png'),
        ('mobile_catalog', 'main_mobile_catalog.png', 'refactor_mobile_catalog.png'),
        ('mobile_pretest', 'main_mobile_pretest.png', 'refactor_mobile_pretest.png'),
        ('mobile_report', 'main_mobile_report.png', 'refactor_mobile_report.png'),
        ('mobile_solved_col', 'main_mobile_solved_col.png', 'refactor_mobile_solved_col.png'),
    ]

    print('| Экран / Виджет | Разрешение | Всего пикселей | Отличающихся пикселей | % расхождения | Область различий (BBox) |')
    print('| :--- | :--- | :--- | :--- | :--- | :--- |')

    all_passed = True
    for name, f_main, f_ref in pairs:
        p_main = os.path.join(screenshots_dir, f_main)
        p_ref = os.path.join(screenshots_dir, f_ref)
        p_diff = os.path.join(screenshots_dir, f'diff_{name}.png')

        if not os.path.exists(p_main) or not os.path.exists(p_ref):
            print(f'| {name} | - | - | Файлы не найдены | - | - |')
            continue

        res = compare_images(p_main, p_ref, p_diff)
        w, h = Image.open(p_main).size
        print(f"| `{name}` | {w}x{h} | {res['total_pixels']:,} | {res['diff_pixels']:,} | **{res['diff_percent']}%** | {res['bbox']} |")
        if res['diff_percent'] > 0.05:
            all_passed = False

if __name__ == '__main__':
    main()
