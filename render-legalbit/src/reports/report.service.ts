import puppeteer, { Browser, PDFOptions, Page } from 'puppeteer';

export class HtmlToPdfService {
  async render(html: string, params: PDFOptions) {
    const browser: Browser = await puppeteer.launch({

      executablePath: process?.env?.BROWSER_PATH || '/usr/bin/chromium',
      args: ['--no-sandbox', '--disable-extensions'],
      headless: true,
    });
    const page: Page = await browser.newPage();
    await page.setContent(html, { waitUntil: 'networkidle2' });

    // Añadir el zoom del 85%
    const zoomFactor = 0.85;

    // Verificar si la propiedad viewport es potencialmente nula
    const pageViewport = page.viewport();
    if (pageViewport) {
      await page.setViewport({
        width: pageViewport.width,
        height: pageViewport.height,
        deviceScaleFactor: zoomFactor,
      });
    }

    console.log('params:', JSON.stringify(params));
    const pdf: Buffer = await page.pdf({
      "preferCSSPageSize": true,
      "format": "letter",
      "printBackground": true,
      "scale": zoomFactor, // Establecer el zoom al 85%
      ...params,
    });

    await browser.close();

    let result = Buffer.from(pdf);
    return { data: result.toString('base64') };
  }
}

export default new HtmlToPdfService();
