import asyncio
import requests
from playwright.async_api import async_playwright

async def solve_recaptcha(api_key: str, site_key: str, page_url: str):
    """Resuelve reCAPTCHA invisible usando CapSolver y devuelve el token."""
    payload = {
        "clientKey": api_key,
        "task": {
            "type": "ReCaptchaV2TaskProxyLess",
            "websiteURL": page_url,
            "websiteKey": site_key,
            "isInvisible": True  # ¡Clave para reCAPTCHA invisible!
        }
    }
    
    # Enviar tarea a CapSolver
    response = requests.post("https://api.capsolver.com/createTask", json=payload)
    task_id = response.json()["taskId"]
    
    # Esperar solución (máximo 60 segundos)
    for _ in range(30):
        result = requests.post("https://api.capsolver.com/getTaskResult", json={"clientKey": api_key, "taskId": task_id}).json()
        if result.get("status") == "ready":
            return result["solution"]["gRecaptchaResponse"]
        await asyncio.sleep(2)
    raise Exception("❌ No se pudo resolver el reCAPTCHA")

async def main():
    cedula = "1727393983"
    url = "https://srienlinea.sri.gob.ec/sri-en-linea/SriPagosWeb/ConsultaDeudasFirmesImpugnadas/Consultas/consultaDeudasFirmesImpugnadas"
    CAPSOLVER_API_KEY = "CAP-68BCA0BD217E86352D43CD4E8CFF9B94F28E35A17DC6AB9D9B9963CC59F64D7F"  # Reemplázala con tu clave real
    SITE_KEY = "6LemEY4UAAAAAHVQd7ZyoCoqBKNoWrcUO4b5H-SP"  # Clave del sitio SRI

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
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

            print("⌨️ Escribiendo cédula...")
            await page.locator('input[formcontrolname="inputRuc"]').type(cedula, delay=100)
            await page.wait_for_timeout(1000)

            print("🔍 Resolviendo reCAPTCHA...")
            token = await solve_recaptcha(CAPSOLVER_API_KEY, SITE_KEY, url)
            
            # Inyectar token en la página
            await page.evaluate(f'document.getElementById("g-recaptcha-response").value = "{token}";')
            print("✅ Token de reCAPTCHA inyectado")

            print("🖱️ Haciendo clic en Consultar...")
            await page.get_by_role("button", name="Consultar").click()
            
            # Esperar resultado (ajusta según sea necesario)
            await page.wait_for_selector("#resultados-consulta", timeout=15000)
            print("🚀 Consulta completada")

        except Exception as e:
            print(f"❌ Error: {e}")

        input("👀 Revisa el navegador y presiona Enter para cerrar...")
        await browser.close()

asyncio.run(main())