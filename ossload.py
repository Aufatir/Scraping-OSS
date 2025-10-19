from playwright.sync_api import sync_playwright
import json
import os
import re

# ===== INPUT NIB =====
print("Masukkan NIB satu per baris. Tekan enter kosong untuk selesai:")
nib_list = []
while True:
    nib = input("➤ ").strip()
    if not nib:
        break
    nib_list.append(nib)

if not nib_list:
    print("❌ Tidak ada NIB yang dimasukkan. Keluar.")
    exit()

# ===== BUAT FOLDER OUTPUT =====
base_dir = "data_nib"
os.makedirs(base_dir, exist_ok=True)

existing_runs = [d for d in os.listdir(base_dir) if d.startswith("run_") and os.path.isdir(os.path.join(base_dir, d))]
run_numbers = [int(re.findall(r"run_(\d+)", d)[0]) for d in existing_runs if re.findall(r"run_(\d+)", d)]
next_run_num = max(run_numbers) + 1 if run_numbers else 1
output_dir = os.path.join(base_dir, f"run_{next_run_num}")
os.makedirs(output_dir, exist_ok=True)

print(f"📁 Folder output: {output_dir}")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    all_responses = []

    def handle_all_response(response):
        all_responses.append(response)

    context.on("response", handle_all_response)

    for idx, nib_to_search in enumerate(nib_list):
        profile_response_data = {}

        # ===== LOGIN =====
        if idx == 0:
            page.goto("https://ui-login.oss.go.id/login")
            page.get_by_role("textbox", name="Contoh: 081xxxxxxxxx atau").fill("dispenak@gmail.com")
            page.get_by_role("textbox", name="Masukkan kata sandi").fill("Disperinaker@2024")
            page.get_by_role("button", name="Masuk").click()
            page.wait_for_url("https://pemrosesan.oss.go.id/#/dashboard", timeout=0)

        # ===== CARI NIB =====
        page.get_by_role("button", name="").click()
        page.get_by_role("button", name="PROFILE", exact=True).click()
        page.get_by_role("option", name="PELAKU USAHA").click()
        page.get_by_role("button", name="Cari Berdasarkan").click()
        page.get_by_text("NIB", exact=True).click()
        page.get_by_text("Pencarian", exact=True).click()
        page.get_by_role("textbox", name="Pencarian").fill(nib_to_search)
        page.get_by_role("textbox", name="Pencarian").press("Enter")
        page.get_by_role("button", name="Cari", exact=True).click()
        page.wait_for_timeout(3000)

        detail_links = page.query_selector_all('div.custom-cell a.h-text-col-link')
        if not detail_links:
            print(f"❌ Tidak ditemukan link 'Lihat Detail' untuk NIB {nib_to_search}")
            continue
        detail_links[0].click()
        page.wait_for_timeout(4000)

        try:
            page.wait_for_selector("text=Profil Pelaku Usaha", timeout=20000)
        except:
            page.wait_for_timeout(3000)

        profile_resp = None
        for resp in all_responses[::-1]:
            if "/profile/profile-pelaku-usaha/" in resp.url and resp.status == 200:
                profile_resp = resp
                break

        if profile_resp:
            try:
                data_profile = profile_resp.json()
                nama_perusahaan = data_profile.get("results", {}).get("nama_perusahaan", "").strip()
                skala_badan_usaha = data_profile.get("results", {}).get("skala_badan_usaha", "")
                profile_response_data["nama_perusahaan"] = nama_perusahaan
                profile_response_data["skala_badan_usaha"] = skala_badan_usaha
                print(f"🏢 {nama_perusahaan} | Skala: {skala_badan_usaha}")
            except Exception as e:
                print(f"⚠️ Gagal parsing data profile NIB {nib_to_search}: {e}")
                nama_perusahaan = nib_to_search
        else:
            print(f"⚠️ Tidak ditemukan response profile untuk NIB {nib_to_search}")
            nama_perusahaan = nib_to_search

        safe_filename = re.sub(r'[\\/*?:"<>|]', "_", nama_perusahaan or nib_to_search)

        # ===== PROYEK =====
        try:
            page.get_by_role("button", name="5").nth(3).click()
            page.get_by_role('option', name='100').click()
        except:
            pass

        with page.expect_response(lambda resp: "limit=100" in resp.url and resp.status == 200) as resp_info:
            pass
        resp = resp_info.value

        try:
            data = resp.json()
        except:
            print(f"⚠️ Respons tidak valid untuk NIB {nib_to_search}. Skip.")
            continue

        if not data.get("success", True) or not data.get("data"):
            print(f"ℹ️ NIB {nib_to_search} tidak punya data proyek. Disimpan kosong.")
            items = []
        else:
            items = data.get("data", {}).get("items", [])
            if isinstance(data.get("data"), list):
                items = data["data"]

        projects_investment = {}
        for item in items:
            id_proyek = item.get("id_proyek")
            total = int(item.get("investment_total", 0))
            lain_lain = int(item.get("lain_lain", 0))
            invest = total if lain_lain == 0 else max(total - lain_lain, 0)
            projects_investment[id_proyek] = invest

        # ===== SIMPAN FILE JSON =====
        nib_path = os.path.join(output_dir, f"{safe_filename}.json")
        with open(nib_path, "w", encoding="utf-8") as f:
            json.dump({
                "nama_perusahaan": profile_response_data.get("nama_perusahaan", ""),
                "skala_badan_usaha": profile_response_data.get("skala_badan_usaha", ""),
                "projects_investment": projects_investment
            }, f, ensure_ascii=False, indent=4)

        print(f"💾 Data {nama_perusahaan} disimpan di '{nib_path}'")

        page.goto("https://pemrosesan.oss.go.id/#/dashboard")
        page.wait_for_timeout(2000)

    browser.close()
    print(f"✅ Semua data NIB sudah disimpan di folder '{output_dir}'")