import flet as ft
import os
import json
import requests
from google.oauth2 import service_account

# 1. KONFIGIRASYON SIKIRITE GOOGLE CLOUD SOU RENDER
credentials = None
if "GOOGLE_APPLICATION_CREDENTIALS_JSON" in os.environ:
    try:
        creds_data = json.loads(os.environ["GOOGLE_APPLICATION_CREDENTIALS_JSON"])
        credentials = service_account.Credentials.from_service_account_info(creds_data)
        print("✅ Kle Google Cloud la chaje ak siksè depi nan Render!")
    except Exception as e:
        print(f"❌ Erè lè n ap li JSON sekirite a: {e}")
else:
    print("❌ Erè: GOOGLE_APPLICATION_CREDENTIALS_JSON pa nan anviwònman Render la.")

# 2. KONFIGIRASYON KLE AKTIVASYON LOKAL
KLE_SEKRÈ = "AVNI-AYITI-2026"

def main(page: ft.Page):
    page.title = "Motivmotion Ultimate"
    page.theme_mode = ft.ThemeMode.DARK
    page.scroll = ft.ScrollMode.AUTO
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.padding = 30

    # Lyen videyo ki kreye a
    lyen_videyo_aktyèl = ft.Ref[str]()

    # Kontwòl pou kle aktivasyon an
    input_key = ft.TextField(label="Antre Kle Aktivasyon Ou", password=True, can_reveal_password=True, width=400)
    msg_status = ft.Text("", weight=ft.FontWeight.BOLD)
    btn_verify = ft.Ref[ft.ElevatedButton]()
    
    # Gwo veso ki kenbe pati kle a pou n ka kache l lendi a fin bon
    bwat_kle_sekirite = ft.Container(
        content=ft.Column([
            input_key,
            ft.ElevatedButton("VÈRIFYE KLE A", on_click=lambda e: verifye_kle(e), bgcolor="blue", color="white"),
            msg_status
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        padding=20,
        border_radius=10,
        bgcolor="grey",
        width=450
    )
    
    # Kontwòl pou kreyasyon videyo a (ki kache okòmansman)
    prompt_input = ft.TextField(label="Ki videyo ou vle kreye? (Prompt nan lang Anglè)", multiline=True, min_lines=3, width=500, disabled=True)
    resolution_dropdown = ft.Dropdown(
        label="Kalite Videyo",
        width=200,
        options=[
            ft.dropdown.Option("720p"),
            ft.dropdown.Option("1080p"),
        ],
        value="720p",
        disabled=True
    )
    
    btn_generate = ft.ElevatedButton("JENERÈ VIDEYO", disabled=True)
    video_output = ft.Text("Videyo a ap parèt la a...", italic=True)
    btn_download = ft.ElevatedButton("📥 TELECHAJE VIDEYO A", bgcolor="green", color="white", visible=False)

    def verifye_kle(e):
        if input_key.value == KLE_SEKRÈ:
            msg_status.value = "✅ Aksè Aksepte! Byenvini nan Motivmotion."
            msg_status.color = "green"
            
            # 🌟 NOU KACHE BWAT KLE A NÈT LA A POU L PA PRAN ESPAS
            bwat_kle_sekirite.visible = False
            
            # NOU DEBLOKE PATI VIDEYO A
            prompt_input.disabled = False
            resolution_dropdown.disabled = False
            btn_generate.disabled = False
            page.update()
        else:
            msg_status.value = "❌ Kle a pa bon. Eseye ankò!"
            msg_status.color = "red"
            page.update()

    # Nou ajoute bouton telechaje a nan fonksyon an tou
    def telechaje_videyo(e):
        if lyen_videyo_aktyèl.current:
            page.launch_url(lyen_videyo_aktyèl.current)
        else:
            video_output.value = "❌ Pa gen videyo ki ko jenere!"
            page.update()
            
    btn_download.on_click = telechaje_videyo

    page.add(
        ft.Text("🌟 MOTIVMOTION ULTIMATE 🌟", size=28, weight=ft.FontWeight.BOLD, color="blue"),
        ft.Text("Sistèm Jenerasyon Videyo Sinematik ak AI (Google Veo)", size=16, color="grey"),
        ft.Divider(),
        bwat_kle_sekirite,  # Bwat sa a ap disparèt nèt lè kle a bon
        ft.Container(height=20),
        ft.Column([
            prompt_input,
            resolution_dropdown,
            btn_generate,
            video_output,
            btn_download
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=port)
