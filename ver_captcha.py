import asyncio
from playwright.async_api import async_playwright

async def verificar_captcha(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url)

        content = await page.content()

        if "www.google.com/recaptcha/api.js" in content:
            print("⚠️ Se detectó reCAPTCHA en la página.")
        elif "hcaptcha.com/1/api.js" in content:
            print("⚠️ Se detectó hCaptcha en la página.")
        else:
            print("✅ No se detectó CAPTCHA tradicional en la página.")

        await browser.close()

asyncio.run(verificar_captcha("https://www.iess.gob.ec/empleador-web/pages/morapatronal/certificadoCumplimientoPublico.jsf"))
