import flet as ft
import os
import json
import requests
from google.oauth2 import service_account

# 1. KONFIGIRASYON SIKIRITE GOOGLE CLOUD SOU RENDER
credentials = None
project_id = "motivmotion-421715"
if "GOOGLE_APPLICATION_CREDENTIALS_JSON" in os.environ:
    try:
        creds_data = json.loads(os.environ["GOOGLE_APPLICATION_CREDENTIALS_JSON"])
        credentials = service_account.Credentials.from_service_account_info(creds_data)
        project_id = creds_data.get("project_id", project_id)
    except Exception as e:
        print(f"❌ Erè Google Cloud JSON: {e}")

# 2. BAZ DONE KREDI ITILIZATÈ YO (Fichye JSON)
FICHYE_KREDI = "users_credits.json"

if not os.path.exists(FICHYE_KREDI):
    tès_itilizatè = {
        "AVNI-AYITI-2026": {"non": "Pwofesè Jean", "kredi": 50},
        "MOTIV-GUEST-10": {"non": "Envite", "kredi": 10},
        "TEST-USER-0": {"non": "Itilizatè Tès", "kredi": 0}
    }
    with open(FICHYE_KREDI, "w") as f:
        json.dump(tès_itilizatè, f, indent=4)

def li_kredi_itilizatè():
    try:
        with open(FICHYE_KREDI, "r") as f:
            return json.load(f)
    except:
        return {}

def sove_kredi_itilizatè(data):
    with open(FICHYE_KREDI, "w") as f:
        json.dump(data, f, indent=4)


def main(page: ft.Page):
    page.title = "Motivmotion Ultimate - Peman"
    page.theme_mode = ft.ThemeMode.DARK
    page.scroll = ft.ScrollMode.AUTO
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.padding = 30

    lyen_medya_aktyèl = [None]
    tip_medya = ["video"]
    kle_itilizatè_aktyèl = [None]

    input_key = ft.TextField(label="Antre Kle Aktivasyon Ou", password=True, can_reveal_password=True, width=400)
    msg_status = ft.Text("", weight=ft.FontWeight.BOLD)
    
    txt_byenvini = ft.Text("", size=18, weight=ft.FontWeight.BOLD, color="blue")
    txt_kredi = ft.Text("", size=16, weight=ft.FontWeight.BOLD, color="green")
    
    def louvri_paj_peman(e):
        page.dialog = bwat_opsyon_peman
        bwat_opsyon_peman.open = True
        page.update()

    btn_buy_credits = ft.ElevatedButton("💳 ACHTE KREDI (Kat Kredi / Pix / MonCash)", on_click=louvri_paj_peman, bgcolor="orange", color="white")
    bwat_enfo_kredi = ft.Column([txt_byenvini, txt_kredi, btn_buy_credits], horizontal_alignment=ft.CrossAxisAlignment.CENTER, visible=False)

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
    
    def chanje_tip(e):
        tip_medya[0] = e.control.value
        btn_generate.text = "JENERÈ VIDEYO (5 Kredi)" if tip_medya[0] == "video" else "JENERÈ IMAJ / FOTO (1 Kredi)"
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
    btn_generate = ft.ElevatedButton("JENERÈ VIDEYO (5 Kredi)", disabled=True, bgcolor="blue", color="white")
    progress_bar = ft.ProgressBar(width=500, visible=False)
    container_rezilta = ft.Container(visible=False, content=ft.Text("Rezilta a ap parèt la a"))
    btn_download = ft.ElevatedButton("📥 TELECHAJE / EKSPÒTE", bgcolor="green", color="white", visible=False)

    def peye_kat_kredi(e):
        page.launch_url("https://dashboard.stripe.com/") 
        bwat_opsyon_peman.open = False
        page.update()

    def peye_pix(e):
        page.dialog = bwat_pix_detay
        bwat_pix_detay.open = True
        page.update()

    bwat_opsyon_peman = ft.AlertDialog(
        title=ft.Text("Chwazi Mwayen Peman Ou"),
        content=ft.Column([
            ft.Text("Kredi yo ap monte otomatikman sou kont ou apre peman an."),
            ft.ElevatedButton("💳 Peye ak Kat Kredi (Stripe)", on_click=peye_kat_kredi, width=300, bgcolor="blue", color="white"),
            ft.ElevatedButton("📱 Peye ak PIX (Brezil)", on_click=peye_pix, width=300, bgcolor="teal", color="white"),
            ft.Text("🇭🇹 Pou Ayiti: Kontakte Admin nan MonCash (+509 xx xx xx)", size=12, color="grey")
        ], height=200, tight=True),
    )

    bwat_pix_detay = ft.AlertDialog(
        title=ft.Text("Peman pa PIX"),
        content=ft.Column([
            ft.Text("Kole kle PIX sa a nan aplikasyon bank ou a pou w fè transfè a:"),
            ft.TextField(value="jeanoccius@email.com", read_only=True, label="Kle PIX (Email/CNPJ)"),
            ft.Text("⚠️ Apre w fin voye lajan an, voye prèv la bay sipò a pou kredi w ka monte.", size=12, color="yellow")
        ], height=150, tight=True),
    )

    # FONKSYON JENERASYON MEDYA
    def kòmanse_jenerasyon(e):
        if not prompt_input.value:
            prompt_input.error_text = "Tanpri ekri yon tèks anvan!"
            page.update()
            return
        
        db_kredi = li_kredi_itilizatè()
        kle = kle_itilizatè_aktyèl[0]
        kredi_aktyèl = db_kredi[kle]["kredi"]
        koute = 5 if tip_medya[0] == "video" else 1

        if kredi_aktyèl < koute:
            container_rezilta.content = ft.Column([
                ft.Text("❌ Kredi ou pa ase pou aksyon sa a!", color="red", weight=ft.FontWeight.BOLD),
                ft.ElevatedButton("💳 ACHTE KREDI KOUNYE A", on_click=louvri_paj_peman, bgcolor="orange", color="white")
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            container_rezilta.visible = True
            page.update()
            return

        if credentials is None:
            container_rezilta.content = ft.Text("❌ Erè: Kle Google Cloud la (JSON) pa configuré.", color="red")
            container_rezilta.visible = True
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
                # NOU RE-LI BAZ DONE A POU EVITE ERÈ ANVAN N SOVE
                db_kredi_saved = li_kredi_itilizatè()
                db_kredi_saved[kle]["kredi"] -= koute
                sove_kredi_itilizatè(db_kredi_saved)
                txt_kredi.value = f"Kredi ki rete: {db_kredi_saved[kle]['kredi']} Kredi"

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
        kle_antre = input_key.value
        db_kredi_verify = li_kredi_itilizatè()

        if kle_antre in db_kredi_verify:
            kle_itilizatè_aktyèl[0] = kle_antre
            bwat_kle_sekirite.visible = False
            
            txt_byenvini.value = f"Byenvini, {db_kredi_verify[kle_antre]['non']}!"
            txt_kredi.value = f"Kredi ki rete: {db_kredi_verify[kle_antre]['kredi']} Kredi"
            bwat_enfo_kredi.visible = True
            
            opsyon_chwa.visible = True
            prompt_input.disabled = False
            btn_generate.disabled = False
            page.update()
        else:
            msg_status.value = "❌ Kle sa a pa egziste nan sistèm nan!"
            msg_status.color = "red"
            page.update()

    def telechaje_medya(e):
        if lyen_medya_aktyèl[0]:
            page.launch_url(lyen_medya_aktyèl[0])

    btn_download.on_click = telechaje_medya

    page.add(
        ft.Text("🌟 MOTIVMOTION ULTIMATE 🌟", size=28, weight=ft.FontWeight.BOLD, color="blue"),
        ft.Text("Jenerasyon Medya ak Sistèm Peman Kat Kredi & PIX", size=16, color="grey"),
        ft.Divider(),
        bwat_kle_sekirite,
        bwat_enfo_kredi,
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
