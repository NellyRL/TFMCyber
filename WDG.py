import dearpygui.dearpygui as dpg
from tkinter import filedialog
import tkinter as tk
import os
import asyncio
from main import main
from prediction import predict

selected_output_dir = ""

def select_file_callback():
    root = tk.Tk()
    root.withdraw()
    extension_path = filedialog.askopenfilename(filetypes=[("Extensiones", "*.crx *.zip")])
    root.destroy()

    if extension_path:
        dpg.set_value("selected_file", extension_path)
        dpg.set_value("status_text", "Archivo seleccionado, listo para analizar.")
    else:
        dpg.set_value("status_text", "No se seleccionó ningún archivo.")

def select_output_dir_callback():
    global selected_output_dir
    root = tk.Tk()
    root.withdraw()
    folder_selected = filedialog.askdirectory()
    root.destroy()

    if folder_selected:
        selected_output_dir = folder_selected
        dpg.set_value("selected_output_dir", folder_selected)
    else:
        dpg.set_value("selected_output_dir", "No se seleccionó ninguna carpeta.")

def confirm_callback():
    dpg.set_value("status_text", "Clasificación iniciada...")
    clase, p_assistant, p_other = predict(selected_output_dir + "/webGraphDiff.gexf")

    dpg.set_value("resultado_clase", f"Predicción: {clase.upper()}")
    dpg.set_value("prob_assistant", p_assistant)
    dpg.set_value("prob_other", p_other)

    dpg.configure_item("prob_assistant", overlay=f"Probabilidad assistant: {p_assistant:.2%}")
    dpg.configure_item("prob_other", overlay=f"Probabilidad other: {p_other:.2%}")

    # Color según clase
    if clase == "assistant":
        dpg.configure_item("resultado_clase", color=(0, 255, 0))  # Verde
    else:
        dpg.configure_item("resultado_clase", color=(255, 100, 100))  # Rojo claro

    dpg.delete_item("alert_popup")
    dpg.set_value("status_text", "Clasificación finalizada, resultados disponibles")


def exit_callback():
    dpg.stop_dearpygui()

def show_alert_popup():
    with dpg.window(label="Análisis Completado", modal=True, tag="alert_popup", no_resize=True, no_move=True, width=400, height=200, pos=(300, 250)):
        dpg.add_text("¿Deseas realizar una clasificación del grafo resultante?", wrap=350)
        dpg.add_spacer(height=20)
        with dpg.group(horizontal=True):
            dpg.add_button(label="Confirmar", width=120, callback=confirm_callback)
            dpg.add_button(label="Salir", width=120, callback=exit_callback)

def execute_analysis():
    extension_path = dpg.get_value("selected_file")
    if not extension_path or not os.path.exists(extension_path):
        dpg.set_value("status_text", "Error: Selecciona un archivo válido primero.")
        return

    dpg.set_value("status_text", "Analizando...")
    asyncio.run(main(extension_path, selected_output_dir))
    dpg.set_value("status_text", "Análisis completado correctamente.")
    show_alert_popup()

# ========== GUI ==========

dpg.create_context()

with dpg.font_registry():
    try:
        default_font = dpg.add_font("C:\\Windows\\Fonts\\segoeui.ttf", 18)
    except:
        default_font = None

with dpg.theme() as custom_theme:
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 10)
        dpg.add_theme_style(dpg.mvStyleVar_WindowRounding, 10)
        dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 10, 10)
        dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (30, 30, 30, 255))
        dpg.add_theme_color(dpg.mvThemeCol_Text, (230, 230, 230, 255))
        dpg.add_theme_color(dpg.mvThemeCol_Button, (70, 70, 70, 255))
        dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (120, 120, 120, 255))
        dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (140, 140, 140, 255))

dpg.create_viewport(title="Analizador de Extensiones", width=1000, height=700, resizable=True)

with dpg.window(tag="main_window", no_title_bar=True, no_resize=True, no_move=True,
                pos=(0, 0), width=1000, height=700):
    with dpg.tab_bar():

        with dpg.tab(label="Análisis de Extensión"):
            dpg.add_spacer(height=30)
            with dpg.group(horizontal=False):
                dpg.add_text("1. Selecciona una extensión (.crx o .zip)", bullet=True)
                dpg.add_button(label="Seleccionar archivo", callback=select_file_callback, width=250)
                dpg.add_input_text(tag="selected_file", readonly=True, width=600, hint="Ruta del archivo")

                dpg.add_spacer(height=15)
                dpg.add_text("2. Selecciona la carpeta de salida", bullet=True)
                dpg.add_button(label="Seleccionar carpeta de salida", callback=select_output_dir_callback, width=250)
                dpg.add_input_text(tag="selected_output_dir", readonly=True, width=600, hint="Ruta de salida")

                dpg.add_spacer(height=20)
                dpg.add_button(label="Ejecutar análisis", callback=execute_analysis, width=250)

                dpg.add_spacer(height=25)
                dpg.add_text("Estado:")
                dpg.add_text("Esperando archivo...", tag="status_text")

        with dpg.tab(label="Resultados del Análisis"):
            dpg.add_text("Resultado del modelo:", tag="resultado_clase", color=(200, 200, 200))
            dpg.add_spacer(height=10)
            dpg.add_progress_bar(default_value=0.0, tag="prob_assistant", overlay="Probabilidad assistant: 0.0", width=400)
            dpg.add_progress_bar(default_value=0.0, tag="prob_other", overlay="Probabilidad other: 0.0", width=400)
            dpg.add_spacer(height=10)

# Adaptación al redimensionamiento

def resize_main_window():
    width = dpg.get_viewport_client_width()
    height = dpg.get_viewport_client_height()
    dpg.set_item_width("main_window", width)
    dpg.set_item_height("main_window", height)
    dpg.set_item_pos("main_window", (0, 0))

def check_viewport_resize():
    global last_w, last_h
    w = dpg.get_viewport_client_width()
    h = dpg.get_viewport_client_height()
    if w != last_w or h != last_h:
        resize_main_window()
        last_w, last_h = w, h

last_w, last_h = 0, 0

# === Lanzamiento de DearPyGui ===
dpg.setup_dearpygui()
dpg.bind_theme(custom_theme)
if default_font:
    dpg.bind_font(default_font)
resize_main_window()
dpg.show_viewport()

while dpg.is_dearpygui_running():
    check_viewport_resize()
    dpg.render_dearpygui_frame()

dpg.destroy_context()
