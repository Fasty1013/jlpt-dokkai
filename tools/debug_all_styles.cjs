const path = require('path');
const { chromium } = require(path.resolve(__dirname, '../tests/qa/node_modules/@playwright/test'));

(async () => {
  const browser = await chromium.launch();
  
  const pageMain = await browser.newPage({ viewport: { width: 1280, height: 800 } });
  await pageMain.goto('http://localhost:8001/');
  await pageMain.waitForSelector('#active-slots-list .stream-slot-card button');
  await pageMain.click('#active-slots-list .stream-slot-card button');
  await pageMain.waitForSelector('#modal-btn-start');
  await pageMain.click('#modal-btn-start');
  await pageMain.waitForSelector('#exercise-view:not(.hidden)');
  await pageMain.evaluate(() => document.fonts.ready);
  await pageMain.waitForTimeout(500);

  const pageRef = await browser.newPage({ viewport: { width: 1280, height: 800 } });
  await pageRef.goto('http://localhost:8000/');
  await pageRef.waitForSelector('#active-slots-list .stream-slot-card button');
  await pageRef.click('#active-slots-list .stream-slot-card button');
  await pageRef.waitForSelector('#modal-btn-start');
  await pageRef.click('#modal-btn-start');
  await pageRef.waitForSelector('#exercise-view:not(.hidden)');
  await pageRef.evaluate(() => document.fonts.ready);
  await pageRef.waitForTimeout(500);

  // Focus specifically on the header and all elements inside header
  const getHeaderElements = () => {
    const root = document.querySelector('.app-header');
    if (!root) return {};
    const map = {};
    const walk = (el, pathStr) => {
      const s = window.getComputedStyle(el);
      const rect = el.getBoundingClientRect();
      const interestingProps = [
        'display', 'position', 'top', 'left', 'width', 'height',
        'margin-top', 'margin-right', 'margin-bottom', 'margin-left',
        'padding-top', 'padding-right', 'padding-bottom', 'padding-left',
        'font-family', 'font-size', 'font-weight', 'line-height',
        'letter-spacing', 'color', 'background-color', 'border', 'gap',
        'white-space', 'flex-direction', 'align-items', 'justify-content'
      ];
      const styles = {};
      for (const p of interestingProps) {
        styles[p] = s.getPropertyValue(p);
      }
      map[pathStr] = {
        tag: el.tagName,
        id: el.id,
        className: el.className,
        rect: { x: rect.x, y: rect.y, w: rect.width, h: rect.height },
        styles
      };
      Array.from(el.children).forEach((child, idx) => {
        const childKey = child.id ? `#${child.id}` : `${pathStr} > ${child.tagName.toLowerCase()}:nth-child(${idx+1})`;
        walk(child, childKey);
      });
    };
    walk(root, 'header.app-header');
    return map;
  };

  const headerMain = await pageMain.evaluate(getHeaderElements);
  const headerRef = await pageRef.evaluate(getHeaderElements);

  console.log('Main header keys:', Object.keys(headerMain).length);
  console.log('Ref header keys:', Object.keys(headerRef).length);

  for (const [key, valMain] of Object.entries(headerMain)) {
    const valRef = headerRef[key];
    if (!valRef) {
      console.log('Missing in Ref:', key);
      continue;
    }
    const rx = Math.abs(valMain.rect.x - valRef.rect.x);
    const ry = Math.abs(valMain.rect.y - valRef.rect.y);
    const rw = Math.abs(valMain.rect.w - valRef.rect.w);
    const rh = Math.abs(valMain.rect.h - valRef.rect.h);

    const styleDiffs = {};
    for (const [prop, val] of Object.entries(valMain.styles)) {
      if (val !== valRef.styles[prop]) {
        styleDiffs[prop] = { main: val, ref: valRef.styles[prop] };
      }
    }

    if (rx > 0.05 || ry > 0.05 || rw > 0.05 || rh > 0.05 || Object.keys(styleDiffs).length > 0) {
      console.log('DIFF on ' + key + ':');
      console.log('  Rect Main:', JSON.stringify(valMain.rect));
      console.log('  Rect Ref: ', JSON.stringify(valRef.rect));
      if (Object.keys(styleDiffs).length > 0) {
        console.log('  Style diffs:', JSON.stringify(styleDiffs, null, 2));
      }
    }
  }

  await browser.close();
})();
