"""
AUTOR: David Martín Castro
This script contains the functions that were automatically made on the test page
"""

#--------------------- LIBRARIES IMPORTS -------------------

from playwright.async_api import Page
import asyncio

#--------------------- FUNCTIONS ---------------------------

async def actions_on_web(page: Page):
    # Navegar a la página inicial
    await page.goto("http://localhost:8080/index.html", wait_until="domcontentloaded")

    await page.wait_for_event("close", timeout=0)

    """ await asyncio.sleep(2)

    # Rellenar formulario de login
    await page.fill("#username", "ana")
    await page.fill("#password", "recetas123")
    await page.click("text=Entrar")

    await asyncio.sleep(2)

    # Esperar a que cargue el desplegable y filtrar por "Cena"
    await page.wait_for_selector('select[name="tipo"]')
    await page.select_option('select[name="tipo"]', 'Cena')

    await asyncio.sleep(1)

    # Esperar a que aparezcan las recetas filtradas (mejor usar espera activa)
    await page.wait_for_selector(".receta-card", timeout=3000)

    await asyncio.sleep(1)

    # Hacer clic en "Cerrar sesión"
    await page.click("text=Cerrar sesión") """
