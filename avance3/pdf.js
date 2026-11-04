const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage();
  await p.goto('file://' + path.resolve(__dirname, 'Avance3.html'));
  await p.waitForTimeout(800);
  await p.pdf({ path: path.resolve(__dirname, 'Avance3.pdf'), format: 'Letter', printBackground: true, displayHeaderFooter: true,
    headerTemplate: '<span></span>', footerTemplate: '<div style="font-size:8px;width:100%;text-align:center;font-family:serif"><span class="pageNumber"></span></div>',
    margin: { top: '0.75in', bottom: '0.8in', left: '0.7in', right: '0.7in' } });
  await b.close();
})();
