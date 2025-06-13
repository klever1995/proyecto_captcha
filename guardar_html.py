import asyncio
from playwright.async_api import async_playwright

async def main():
    cedula = "1727393983"
    url = "https://srienlinea.sri.gob.ec/sri-en-linea/SriPagosWeb/ConsultaDeudasFirmesImpugnadas/Consultas/consultaDeudasFirmesImpugnadas"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122 Safari/537.36"
        )
        page = await context.new_page()

        print("🔄 Abriendo página...")
        await page.goto(url)

        # Esperamos a que cargue algo que SIEMPRE aparece, como el texto del título
        await page.wait_for_timeout(5000)

        try:
            print("⌛ Esperando campo de cédula...")
            await page.wait_for_selector('input[formcontrolname="identificacion"]', timeout=20000)
            await page.fill('input[formcontrolname="identificacion"]', cedula)
            print("✅ ¡Cédula ingresada!")
        except Exception as e:
            print("❌ No se encontró el campo. Mostrando HTML de la página para analizar...")
            content = await page.content()
            with open("contenido.html", "w", encoding="utf-8") as f:
                f.write(content)
            print("📝 Se guardó el contenido de la página en 'contenido.html'. Revísalo.")

        input("👀 Mira el navegador y presiona Enter para cerrar...")
        await browser.close()

asyncio.run(main())
