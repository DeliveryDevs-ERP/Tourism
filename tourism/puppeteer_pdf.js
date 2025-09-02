const puppeteer = require('puppeteer');

(async () => {
    const url = process.argv[2]; // HTML file or URL
    const outputPath = process.argv[3]; // Output PDF path

    const browser = await puppeteer.launch({
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    const page = await browser.newPage();
    await page.goto(url, { waitUntil: 'networkidle0' });

    await page.pdf({
        path: outputPath,
        format: 'A4',
        printBackground: true
    });

    await browser.close();
})();