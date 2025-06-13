import asyncio
from playwright.async_api import async_playwright

async def main():
    cedula = "1727393983"
    url = "https://srienlinea.sri.gob.ec/sri-en-linea/SriPagosWeb/ConsultaDeudasFirmesImpugnadas/Consultas/consultaDeudasFirmesImpugnadas"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # headless=True si no quieres ver el navegador
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122 Safari/537.36"
        )
        page = await context.new_page()

        print("🔄 Abriendo página...")
        await page.goto(url)
        await page.wait_for_timeout(5000)

        try:
            print("⌛ Esperando campo de cédula...")
            await page.wait_for_selector('input[formcontrolname="inputRuc"]', timeout=20000)

            print("⌨️ Escribiendo cédula (como humano)...")
            await page.locator('input[formcontrolname="inputRuc"]').type(cedula, delay=100)
            await page.wait_for_timeout(1000)  # esperar un momento a que Angular active el botón

            print("🖱️ Buscando botón de consulta...")
            await page.get_by_role("button", name="Consultar").click()
            print("✅ ¡Botón presionado!")

        except Exception as e:
            print("❌ Algo falló:", e)

        input("👀 Revisa el navegador y presiona Enter para cerrar...")
        await browser.close()

asyncio.run(main())
