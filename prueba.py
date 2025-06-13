import asyncio
from playwright.async_api import async_playwright
import requests
import time

# 👉 Reemplaza con tu API key válida de Capsolver
CAPSOLVER_API_KEY = "CAP-94F52BDAB73FCD4707FA7A4BD9F3EF03B6B3410EF16EEBCE05C49E97DD91456D"
SITEKEY = "6LemEY4UAAAAAHVQd7ZyoCoqBKNoWrcUO4b5H-SP"
PAGE_URL = "https://srienlinea.sri.gob.ec/sri-en-linea/SriPagosWeb/ConsultaDeudasFirmesImpugnadas/Consultas/consultaDeudasFirmesImpugnadas"


def resolver_captcha_capsolver(api_key, sitekey, page_url):
    print("🧠 Enviando captcha a Capsolver...")

    create_url = "https://api.capsolver.com/createTask"
    result_url = "https://api.capsolver.com/getTaskResult"

    payload = {
        "clientKey": api_key,
        "task": {
            "type": "ReCaptchaV2TaskProxyLess",
            "websiteURL": page_url,
            "websiteKey": sitekey
        }
    }

    response = requests.post(create_url, json=payload, proxies={"http": None, "https": None})
    print("🔍 Respuesta sin parsear:", response.text)

    try:
        response_json = response.json()
    except Exception as e:
        raise Exception(f"❌ Error al parsear JSON: {e}")

    if 'taskId' not in response_json:
        raise Exception(f"❌ Error al crear tarea: {response_json}")

    task_id = response_json["taskId"]
    print(f"⏳ Esperando solución (taskId: {task_id})...")

    for _ in range(30):
        time.sleep(5)
        result = requests.post(
            result_url,
            json={"clientKey": api_key, "taskId": task_id},
            proxies={"http": None, "https": None}
        ).json()

        if result.get("status") == "ready":
            print("✅ Captcha resuelto")
            return result["solution"]["gRecaptchaResponse"]

    raise Exception("❌ Tiempo agotado esperando captcha")


async def main():
    cedula = "1727393983"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        print("🔄 Abriendo página...")
        await page.goto(PAGE_URL)

        print("⌛ Esperando campo de cédula...")
        await page.wait_for_selector('input[formcontrolname="inputRuc"]')
        await page.fill('input[formcontrolname="inputRuc"]', cedula)
        print("✅ ¡Cédula ingresada!")

        # 🔐 Resolver captcha
        token = resolver_captcha_capsolver(CAPSOLVER_API_KEY, SITEKEY, PAGE_URL)

        # 💉 Inyectar token en reCAPTCHA invisible
        await page.evaluate("""(token) => {
            document.querySelector('textarea[name="g-recaptcha-response"]').value = token;
        }""", token)
        print("✅ Token inyectado")

        # 🚀 Hacer clic en botón "Consultar"
        print("🖱️ Presionando botón...")
        await page.click('button:has-text("Consultar")')
        print("🚀 ¡Formulario enviado!")

        input("👀 Revisa el navegador y presiona Enter para cerrar...")
        await browser.close()


# ▶️ Ejecutar
asyncio.run(main())
