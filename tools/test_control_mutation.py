import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from PIL import Image
from tools.pixel_diff import compare_images

def run():
    screenshots = [
        ('desktop_analysis', 'refactor_desktop_analysis.png'),
        ('mobile_analysis', 'refactor_mobile_analysis.png')
    ]
    for name, fname in screenshots:
        p_base = os.path.join('docs', 'qa', 'evidence', 'screenshots', fname)
        p_mut = os.path.join('docs', 'qa', 'evidence', 'screenshots', 'mut_' + fname)
        p_diff = os.path.join('docs', 'qa', 'evidence', 'screenshots', 'diff_mut_' + fname)

        im = Image.open(p_base).convert('RGB')
        orig = im.getpixel((200, 200))
        # Deliberately invert exactly 1 pixel
        im.putpixel((200, 200), (255 - orig[0], 255 - orig[1], 255 - orig[2]))
        im.save(p_mut)

        res = compare_images(p_base, p_mut, p_diff)
        print(f"CONTROL 1-PIXEL TEST FOR {name}: total={res['total_pixels']}, diff_pixels={res['diff_pixels']}, bbox={res['bbox']}")
        
        if os.path.exists(p_mut):
            os.remove(p_mut)
        if os.path.exists(p_diff):
            os.remove(p_diff)

if __name__ == '__main__':
    run()
