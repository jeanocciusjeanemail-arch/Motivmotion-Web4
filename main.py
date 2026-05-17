import flet as ft
import os
import threading
import requests
import base64
import time
import google.auth
import google.auth.transport.requests

# ========================================================
# 🔑 KONFIGIRASYON PWOKJÈ - JEAN OCCIUS
# ========================================================
PROJECT_ID = "gen-lang-client-0501880711"
LOCATION = "us-central1"
MODEL_ID = "veo-3.1-generate-001"
BUCKET_NAME = "motivmotion-jean-haiti-2026"
LICENSE_KEY = "AVNI-AYITI-2026"


def main(page: ft.Page):
    # Nou fikse gwosè fenèt la byen pròp depi nan kòmansman
    page.title = "Motivmotion Ultimate - Avni Ayiti Avan"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "black"  # Fòse background lan nwa pou evite flash blanch lan

    page.window_width = 440
    page.window_height = 500
    page.window_resizable = False

    page.scroll = ft.ScrollMode.AUTO
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.padding = 15

    # State variables
    user_credits = 5
    last_video_url = ""

    # Tit Prensipal
    title = ft.Text(
        value="🌟 MOTIVMOTION ULTIMATE 🌟\nAvni Ayiti Avan",
        size=20,
        weight=ft.FontWeight.BOLD,
        color="greenaccent",
        text_align=ft.TextAlign.CENTER
    )

    # ==========================================
    # 1. ELEMAN POU APLIKASYON PRINCIPAL LA
    # ==========================================
    email_text = ft.Text(value="📧 Imel: jeanoccius@gmail.com", size=13)
    credits_text = ft.Text(value=f"🪙 Kredi ki rete: {user_credits} videyo", size=15, weight=ft.FontWeight.BOLD,
                           color="amber")

    credit_card = ft.Card(
        content=ft.Container(
            content=ft.Column([email_text, credits_text], alignment=ft.MainAxisAlignment.CENTER),
            padding=12,
            width=360,
            bgcolor="bluegrey900",
            border_radius=10
        )
    )

    first_image_input = ft.TextField(
        label="🖼️ Chemen Imaj sou PC a oswa Lyen Entènèt",
        hint_text="Egz: C:\\Users\\Jean\\Imaj\\foto.jpg",
        width=360
    )
    last_image_input = ft.TextField(
        label="🖼️ Dènye Imaj (Opsyonèl)",
        hint_text="Egz: C:\\Users\\Jean\\Imaj\\finisman.jpg",
        width=360
    )

    format_dd = ft.Dropdown(
        label="📱 Fòma",
        width=175,
        options=[
            ft.dropdown.Option("16:9 (YouTube)"),
            ft.dropdown.Option("9:16 (TikTok)"),
            ft.dropdown.Option("1:1 (Kare)"),
        ],
        value="16:9 (YouTube)"
    )

    res_dd = ft.Dropdown(
        label="🎬 Rezolisyon",
        width=175,
        options=[
            ft.dropdown.Option("720p"),
            ft.dropdown.Option("1080p"),
        ],
        value="720p"
    )

    dropdowns_row = ft.Row([format_dd, res_dd], alignment=ft.MainAxisAlignment.CENTER, width=360)

    prompt_input = ft.TextField(
        label="✍️ Deskripsyon Videyo a (An anglè)",
        multiline=True,
        min_lines=2,
        max_lines=4,
        value="A cinematic video of a scientific laboratory in Haiti, 4k, realistic lighting.",
        width=360
    )

    log_box = ft.TextField(
        label="📜 Log Sistèm",
        multiline=True,
        read_only=True,
        min_lines=4,
        max_lines=6,
        value="Sistèm pare...\n",
        width=360,
        text_style=ft.TextStyle(color="greenaccent", font_family="Consolas")
    )

    def log(message):
        log_box.value += f"> {message}\n"
        page.update()

    preview_image = ft.Image(
        src="https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=400",
        width=360,
        height=190,
        fit="cover",
        border_radius=10,
    )

    def open_video_link(e):
        nonlocal last_video_url
        if last_video_url:
            log("🌐 Ap louvri lyen an nan navigatè w la...")
            try:
                page.launch_url(last_video_url)
            except Exception as ex:
                log(f"⚠️ Pa ka louvri otomatikman. Kopye lyen sa a: {last_video_url}")
        else:
            log("⚠️ Pa gen videyo ki jenere pou kounye a.")

    btn_play_video = ft.FilledButton(
        content=ft.Text("▶ Louvri / Gade Videyo a", color="white", weight="bold"),
        on_click=open_video_link,
        width=360,
        disabled=True
    )

    video_container = ft.Container(
        content=ft.Column([
            preview_image,
            btn_play_video
        ], alignment=ft.MainAxisAlignment.CENTER),
        width=360,
        padding=10,
        bgcolor="black",
        border_radius=10
    )

    def jwenn_imaj_base64(chemen):
        chemen = chemen.strip()
        if chemen.startswith("http://") or chemen.startswith("https://"):
            log(f"📥 Ap telechaje imaj sou entènèt...")
            img_res = requests.get(chemen)
            if img_res.status_code == 200:
                return base64.b64encode(img_res.content).decode("utf-8")
            else:
                log("⚠️ Erè: Lyen entènèt la pa bon.")
                return None
        else:
            log(f"📥 Ap li imaj sou PC a: {chemen}")
            if os.path.exists(chemen):
                with open(chemen, "rb") as f:
                    return base64.b64encode(f.read()).decode("utf-8")
            else:
                log(f"⚠️ Erè: Fichye a pa egziste sou PC a: {chemen}")
                return None

    def call_veo_api():
        nonlocal user_credits, last_video_url
        try:
            log("🔑 Otantifikasyon Google Cloud...")
            credentials, project = google.auth.default()
            auth_request = google.auth.transport.requests.Request()
            credentials.refresh(auth_request)
            token = credentials.token

            url = f"https://{LOCATION}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{LOCATION}/publishers/google/models/{MODEL_ID}:predictLongRunning"
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json; charset=utf-8"
            }

            aspect_ratio = "16:9"
            if "9:16" in format_dd.value:
                aspect_ratio = "9:16"
            elif "1:1" in format_dd.value:
                aspect_ratio = "1:1"

            prompt_text = prompt_input.value.strip()
            instance = {"prompt": prompt_text}

            val_premye_imaj = first_image_input.value.strip()
            if val_premye_imaj:
                b64_img = jwenn_imaj_base64(val_premye_imaj)
                if b64_img:
                    instance["image"] = {"bytesBase64Encoded": b64_img, "mimeType": "image/jpeg"}

            val_denye_imaj = last_image_input.value.strip()
            if val_denye_imaj:
                b64_img_last = jwenn_imaj_base64(val_denye_imaj)
                if b64_img_last:
                    instance["lastFrameImage"] = {"bytesBase64Encoded": b64_img_last, "mimeType": "image/jpeg"}

            payload = {
                "instances": [instance],
                "parameters": {
                    "sampleCount": 1,
                    "aspectRatio": aspect_ratio,
                    "resolution": res_dd.value,
                    "storageUri": f"gs://{BUCKET_NAME}"
                }
            }

            log("🚀 Voye demann bay Google Veo...")
            response = requests.post(url, headers=headers, json=payload)
            if response.status_code != 200:
                log(f"❌ Erè API: {response.text}")
                return

            op_name = response.json().get("name")
            log(f"⏳ Operasyon kòmanse! ID: {op_name}")

            while True:
                time.sleep(15)
                poll_url = f"https://{LOCATION}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{LOCATION}/publishers/google/models/{MODEL_ID}:fetchPredictOperation"
                poll_res = requests.post(poll_url, headers=headers, json={"operationName": op_name})

                if poll_res.status_code == 200:
                    status_res = poll_res.json()
                    if status_res.get("done"):
                        log("✅ VEO FINI TRAVAY LA!")
                        if "response" in status_res:
                            videos = status_res['response'].get('videos', [])
                            if videos:
                                gcs_uri = videos[0].get('gcsUri')
                                http_url = gcs_uri.replace("gs://", "https://storage.googleapis.com/").replace(" ",
                                                                                                               "%20")
                                last_video_url = http_url

                                log(f"🎯 Lyen videyo a pare: {last_video_url}")
                                log("Klike sou bouton 'Gade Videyo' a pou louvri l!")

                                preview_image.src = "https://images.unsplash.com/photo-1461360370896-922624d12aa1?w=400"
                                btn_play_video.disabled = False

                                user_credits -= 1
                                credits_text.value = f"🪙 Kredi ki rete: {user_credits} videyo"
                        break
                    else:
                        log("⏳ Veo ap kalkile mouvman yo...")

        except Exception as ex:
            log(f"❌ Erè: {str(ex)}")
        finally:
            btn_run.disabled = False
            btn_run.content = ft.Text("🎬 JENERE VIDEYO KÒNÈKTE AK VEO", color="white", weight="bold")
            page.update()

    def start_thread(e):
        nonlocal user_credits
        if user_credits <= 0:
            log("❌ Ou pa gen ase kredi ankò!")
            return

        btn_run.disabled = True
        btn_run.content = ft.Text("🔄 VEO AP TRAVAY...", color="white", weight="bold")
        page.update()
        threading.Thread(target=call_veo_api, daemon=True).start()

    btn_run = ft.FilledButton(
        content=ft.Text("🎬 JENERE VIDEYO KÒNÈKTE AK VEO", color="white", weight="bold"),
        on_click=start_thread,
        width=360,
        style=ft.ButtonStyle(bgcolor="green800")
    )

    main_app_container = ft.Column([
        credit_card,
        first_image_input,
        last_image_input,
        dropdowns_row,
        prompt_input,
        btn_run,
        video_container,
        log_box
    ], visible=False, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    # ==========================================
    # 2. SEKSYON SOU KLE AKTIVASYON AN
    # ==========================================
    license_input = ft.TextField(
        label="🔑 Tape Kle Aktivasyon an la a",
        password=True,
        can_reveal_password=True,
        width=280,
        text_align=ft.TextAlign.CENTER
    )

    def verifye_kle_a(e):
        if license_input.value == LICENSE_KEY:
            # Lè kle a fin verifye, nou elaji fenèt la pou tout lojisyèl la parèt byen
            page.window_resizable = True
            page.window_width = 440
            page.window_height = 820

            activation_container.visible = False
            main_app_container.visible = True
            log("🔑 Aktivasyon reyisi! Byenveni nan Motivmotion.")
            page.update()
        else:
            license_input.error_text = "❌ Kle a pa bon! Tanpri eseye ankò."
            page.update()

    btn_verify = ft.FilledButton(
        content=ft.Text("VÈRIFYE KLE A", color="white", weight="bold"),
        on_click=verifye_kle_a,
        width=280,
        style=ft.ButtonStyle(bgcolor="blue700")
    )

    activation_container = ft.Container(
        content=ft.Column([
            ft.Icon("lock", size=40, color="amber"),
            ft.Text("LOJISYÈL SEKIRIZE", size=16, weight="bold"),
            ft.Text("Antre kle a pou w jwenn aksè.", color="white54", size=11),
            ft.Divider(height=10, color="transparent"),
            license_input,
            btn_verify
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        padding=15,
        bgcolor="bluegrey900",
        border_radius=12,
        width=320,
    )

    # ==========================================
    # 3. AJOUTE TOUT BAGAY SOU EKRAN AN
    # ==========================================
    page.add(
        title,
        ft.Divider(height=10, color="transparent"),
        activation_container,
        main_app_container
    )


if __name__ == "__main__":
    ft.run(main)
