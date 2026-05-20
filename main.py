import flet as ft
import os
import json
import requests
from google.oauth2 import service_account

# 1. KONFIGIRASYON SIKIRITE GOOGLE CLOUD SOU RENDER
credentials = None
project_id = "motivmotion-421715" # ID pwojè Google Cloud ou a
if "GOOGLE_APPLICATION_CREDENTIALS_JSON" in os.environ:
    try:
        creds_data = json.loads(os.environ["GOOGLE_APPLICATION_CREDENTIALS_JSON"])
        credentials = service_account.Credentials.from_service_account_info(creds_data)
        project_id = creds_data.get("project_id", project_id)
        print("✅ Kle Google Cloud la chaje ak siksè depi nan Render!")
    except Exception as e:
        print(f"❌ Erè lè n ap li JSON sekirite a: {e}")

# 2. KONFIGIRASYON KLE AKTIVASYON LOKAL
KLE_SEKRÈ = "AVNI-AYITI-2026"

def main(page: ft.Page):
    page.title = "Motivmotion Ultimate"
    page.theme_mode = ft.ThemeMode.DARK
    page.scroll = ft.ScrollMode.AUTO
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.padding = 30

    # Sove lyen medya ki jenere a
    lyen_medya_aktyèl = [None]
    tip_medya = ["video"] # Ka "video" oswa "image"

    # Kontwòl pou kle aktivasyon an
    input_key = ft.TextField(label="Antre Kle Aktivasyon Ou", password=True, can_reveal_password=True, width=400)
    msg_status = ft.Text("", weight=ft.FontWeight.BOLD)
    
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
    
    # Chwa ant Videyo ak Imaj (Nou ranplase Tabs pa RadioGroup pou evite erè)
    def chanje_tip(e):
        tip_medya[0] = e.control.value
        btn_generate.text = "JENERÈ VIDEYO" if tip_medya[0] == "video" else "JENERÈ IMAJ / FOTO"
        page.update()

    opsyon_chwa = ft.RadioGroup(
        content=ft.Row([
            ft.Radio(value="video", label="🎬 Kreye Videyo AI"),
            ft.Radio(value="image", label="🖼️ Kreye Imaj / Foto AI"),
        ], alignment=ft.MainAxisAlignment.CENTER),
        value="video",
        on_change=chanje_tip,
        visible=False
    )

    prompt_input = ft.TextField(label="Ki sa ou vle AI a kreye pou ou? (Ekri an Anglè)", multiline=True, min_lines=3, width=500, disabled=True)
    
    btn_generate = ft.ElevatedButton("JENERÈ VIDEYO", disabled=True, bgcolor="blue", color="white")
    progress_bar = ft.ProgressBar(width=500, visible=False)
    
    container_rezilta = ft.Container(visible=False, content=ft.Text("Rezilta a ap parèt la a"))
    btn_download = ft.ElevatedButton("📥 TELECHAJE / EKSPÒTE", bgcolor="green", color="white", visible=False)

    # FONKSYON API GOOGLE CLOUD
    def kòmanse_jenerasyon(e):
        if not prompt_input.value:
            prompt_input.error_text = "Tanpri ekri yon tèks anvan!"
            page.update()
            return
        
        btn_generate.disabled = True
        progress_bar.visible = True
        container_rezilta.visible = False
        btn_download.visible = False
        page.update()

        try:
            import google.auth.transport.requests
            auth_req = google.auth.transport.requests.Request()
            credentials.refresh(auth_req)
            access_token = credentials.token

            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }

            if tip_medya[0] == "video":
                url = f"https://us-central1-aiplatform.googleapis.com/v1/projects/{project_id}/locations/us-central1/publishers/google/models/veo-2.0-generate-video:predict"
                payload = {
                    "instances": [{"prompt": prompt_input.value}],
                    "parameters": {"aspectRatio": "16:9", "durationSeconds": 5}
                }
            else:
                url = f"https://us-central1-aiplatform.googleapis.com/v1/projects/{project_id}/locations/us-central1/publishers/google/models/imagen-3.0-generate-002:predict"
                payload = {
                    "instances": [{"prompt": prompt_input.value}],
                    "parameters": {"sampleCount": 1, "aspectRatio": "1:1", "outputMimeType": "image/jpeg"}
                }

            response = requests.post(url, headers=headers, json=payload)
            res_data = response.json()

            if response.status_code == 200:
                if tip_medya[0] == "video":
                    video_uri = res_data["predictions"][0]["generatedSamples"][0]["video"]["uri"]
                    lyen_medya_aktyèl[0] = video_uri.replace("gs://", "https://storage.googleapis.com/")
                    container_rezilta.content = ft.Video(playlist=[ft.VideoMedia(lyen_medya_aktyèl[0])], width=500, height=300)
                else:
                    img_base64 = res_data["predictions"][0]["bytesBase64Encoded"]
                    lyen_medya_aktyèl[0] = f"data:image/jpeg;base64,{img_base64}"
                    container_rezilta.content = ft.Image(src_base64=img_base64, width=400, height=400)
                
                container_rezilta.visible = True
                btn_download.visible = True
            else:
                container_rezilta.content = ft.Text(f"❌ Erè Google Cloud: {response.text}", color="red")
                container_rezilta.visible = True

        except Exception as ex:
            container_rezilta.content = ft.Text(f"❌ Erè Sistèm: {ex}", color="red")
            container_rezilta.visible = True

        btn_generate.disabled = False
        progress_bar.visible = False
        page.update()

    btn_generate.on_click = kòmanse_jenerasyon

    def verifye_kle(e):
        if input_key.value == KLE_SEKRÈ:
            bwat_kle_sekirite.visible = False
            opsyon_chwa.visible = True
            prompt_input.disabled = False
            btn_generate.disabled = False
            page.update()
        else:
            msg_status.value = "❌ Kle a pa bon. Eseye ankò!"
            msg_status.color = "red"
            page.update()

    def telechaje_medya(e):
        if lyen_medya_aktyèl[0]:
            page.launch_url(lyen_medya_aktyèl[0])

    btn_download.on_click = telechaje_medya

    page.add(
        ft.Text("🌟 MOTIVMOTION ULTIMATE 🌟", size=28, weight=ft.FontWeight.BOLD, color="blue"),
        ft.Text("Sistèm Jenerasyon Videyo ak Imaj ak AI (Google Veo & Imagen)", size=16, color="grey"),
        ft.Divider(),
        bwat_kle_sekirite,
        opsyon_chwa,
        ft.Container(height=20),
        ft.Column([
            prompt_input,
            progress_bar,
            btn_generate,
            container_rezilta,
            btn_download
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=port)
       
