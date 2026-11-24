import json
import os
import datetime
import flet as ft

# --------- مسیرها ----------
CITIES_FILE = "cities.json"
LOGS_FILE = "logs.json"
ASSETS_DIR = "assets"
IRAN_FONT = "assets/IRANSans.ttf"  # نام فایل فونت را مطابق فایل واقعی تنظیم کنید
APP_ICON = "assets/icon.png"

# --------- وضعیت سراسری ----------
cities = []            # لیست شهرها: [{code, name, price, is_favorite}]
selected_city = None   # شهر انتخاب شده فعلی
current_focus = None   # کنترل فوکوس‌شده فعلی (فقط TextFieldها)
add_fields = set()     # مجموعه فیلدهای فرم افزودن/ویرایش برای مدیریت Tab
popular_area = None    # Column برای دکمه‌های محبوب‌ها
search_input = None
code_input = None
qty_input = None
result_text = None
fav_toggle = None      # Toggle برای محبوب کردن دستی در فرم ویرایش
page_global = None

# --------- ابزارهای فایل ----------
def ensure_files():
    # ایجاد assets
    if not os.path.isdir(ASSETS_DIR):
        os.makedirs(ASSETS_DIR, exist_ok=True)

    # cities.json
    if not os.path.isfile(CITIES_FILE):
        seed_cities = [
            {"code": "101", "name": "تهران", "price": 35000, "is_favorite": False},
            {"code": "102", "name": "مشهد", "price": 28000, "is_favorite": False},
            {"code": "103", "name": "اصفهان", "price": 30000, "is_favorite": False},
            {"code": "104", "name": "شیراز", "price": 32000, "is_favorite": False},
            {"code": "105", "name": "تبریز", "price": 31000, "is_favorite": False},
            {"code": "106", "name": "قم", "price": 26000, "is_favorite": False},
            {"code": "107", "name": "اهواز", "price": 33000, "is_favorite": False},
            {"code": "108", "name": "کرج", "price": 29000, "is_favorite": False},
            {"code": "109", "name": "کرمانشاه", "price": 27000, "is_favorite": False},
            {"code": "110", "name": "یزد", "price": 28000, "is_favorite": False},
            {"code": "111", "name": "اردبیل", "price": 26000, "is_favorite": False},
            {"code": "112", "name": "بندرعباس", "price": 34000, "is_favorite": False},
            {"code": "113", "name": "همدان", "price": 27000, "is_favorite": False},
            {"code": "114", "name": "کرمان", "price": 30000, "is_favorite": False},
            {"code": "115", "name": "رشت", "price": 29000, "is_favorite": False},
            {"code": "116", "name": "ساری", "price": 28000, "is_favorite": False},
            {"code": "117", "name": "ارومیه", "price": 30000, "is_favorite": False},
            {"code": "118", "name": "قزوین", "price": 27000, "is_favorite": False},
            {"code": "119", "name": "زنجان", "price": 27000, "is_favorite": False},
            {"code": "120", "name": "سنندج", "price": 26000, "is_favorite": False},
            {"code": "121", "name": "خرم‌آباد", "price": 27000, "is_favorite": False},
            {"code": "122", "name": "اراک", "price": 27000, "is_favorite": False},
            {"code": "123", "name": "گرگان", "price": 28000, "is_favorite": False},
            {"code": "124", "name": "ایلام", "price": 25000, "is_favorite": False},
            {"code": "125", "name": "بوشهر", "price": 32000, "is_favorite": False},
            {"code": "126", "name": "بیرجند", "price": 26000, "is_favorite": False},
            {"code": "127", "name": "بجنورد", "price": 26000, "is_favorite": False},
            {"code": "128", "name": "شهرکرد", "price": 26000, "is_favorite": False},
            {"code": "129", "name": "یاسوج", "price": 25000, "is_favorite": False},
            {"code": "130", "name": "سمنان", "price": 26000, "is_favorite": False},
            {"code": "131", "name": "گنبدکاووس", "price": 27000, "is_favorite": False},
            {"code": "132", "name": "ملایر", "price": 26000, "is_favorite": False},
            {"code": "133", "name": "کاشان", "price": 27000, "is_favorite": False},
            {"code": "134", "name": "دزفول", "price": 30000, "is_favorite": False},
            {"code": "135", "name": "سبزوار", "price": 27000, "is_favorite": False},
            {"code": "136", "name": "نیشابور", "price": 27000, "is_favorite": False},
            {"code": "137", "name": "بندر انزلی", "price": 29000, "is_favorite": False},
            {"code": "138", "name": "سیرجان", "price": 29000, "is_favorite": False},
            {"code": "139", "name": "رفسنجان", "price": 29000, "is_favorite": False},
            {"code": "140", "name": "مهاباد", "price": 26000, "is_favorite": False},
            {"code": "141", "name": "مراغه", "price": 27000, "is_favorite": False},
            {"code": "142", "name": "سقز", "price": 26000, "is_favorite": False},
            {"code": "143", "name": "خوی", "price": 27000, "is_favorite": False},
            {"code": "144", "name": "ساوه", "price": 26000, "is_favorite": False},
            {"code": "145", "name": "ورامین", "price": 26000, "is_favorite": False},
            {"code": "146", "name": "اسلامشهر", "price": 26000, "is_favorite": False},
            {"code": "147", "name": "ری", "price": 26000, "is_favorite": False},
            {"code": "148", "name": "شهریار", "price": 26000, "is_favorite": False},
            {"code": "149", "name": "پاکدشت", "price": 26000, "is_favorite": False},
            {"code": "150", "name": "اندیشه", "price": 25000, "is_favorite": False},
            {"code": "151", "name": "قرچک", "price": 25000, "is_favorite": False},
            {"code": "152", "name": "بومهن", "price": 25000, "is_favorite": False},
            {"code": "153", "name": "پرند", "price": 25000, "is_favorite": False},
            {"code": "154", "name": "پردیس", "price": 25000, "is_favorite": False},
            {"code": "155", "name": "نسیم‌شهر", "price": 25000, "is_favorite": False},
            {"code": "156", "name": "قدس", "price": 25000, "is_favorite": False},
            {"code": "157", "name": "نظرآباد", "price": 25000, "is_favorite": False},
            {"code": "158", "name": "هشتگرد", "price": 25000, "is_favorite": False},
            {"code": "159", "name": "فولادشهر", "price": 25000, "is_favorite": False},
            {"code": "160", "name": "شاهین‌شهر", "price": 26000, "is_favorite": False}
        ]
        with open(CITIES_FILE, "w", encoding="utf-8") as f:
            json.dump(seed_cities, f, ensure_ascii=False, indent=2)

    # logs.json
    if not os.path.isfile(LOGS_FILE):
        with open(LOGS_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)

def load_cities():
    global cities
    with open(CITIES_FILE, "r", encoding="utf-8") as f:
        cities = json.load(f)

def save_cities():
    with open(CITIES_FILE, "w", encoding="utf-8") as f:
        json.dump(cities, f, ensure_ascii=False, indent=2)

def load_logs():
    with open(LOGS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_logs(logs):
    with open(LOGS_FILE, "w", encoding="utf-8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)

# --------- محاسبه محبوب‌ها ----------
def usage_counts_from_logs():
    logs = load_logs()
    counts = {}
    for entry in logs:
        code = entry.get("code")
        if not code:
            continue
        counts[code] = counts.get(code, 0) + 1
    return counts

def get_top5_popular_codes():
    counts = usage_counts_from_logs()
    sorted_codes = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)
    return [code for code, _ in sorted_codes[:5]]

def get_favorite_codes():
    return [c["code"] for c in cities if c.get("is_favorite")]

def get_union_popular_codes():
    # Top 5 از لاگ‌ها + موارد محبوب دستی
    top5 = set(get_top5_popular_codes())
    favs = set(get_favorite_codes())
    return list(top5.union(favs))

def get_city_by_code(code):
    for c in cities:
        if str(c["code"]).strip() == str(code).strip():
            return c
    return None

def search_cities(query):
    q = str(query or "").strip()
    if not q:
        return []
    q_norm = q.lower()
    # جستجو بر اساس کد یا نام (حساسیت به حروف: ندارد)
    matches = []
    for c in cities:
        code_match = str(c["code"]).startswith(q)
        name_match = str(c["name"]).lower().find(q_norm) != -1
        if code_match or name_match:
            matches.append(c)
    # اولویت: محبوب‌ها جلوتر
    popular_codes = set(get_union_popular_codes())
    matches.sort(key=lambda c: (0 if c["code"] in popular_codes else 1, c["name"]))
    return matches

# --------- ساخت دکمه‌های محبوب‌ها ----------
def build_popular_buttons_for_codes(codes, per_row=5, on_open=None):
    # ایجاد دکمه‌ها برای کدهای داده‌شده
    btns = []
    for code in codes:
        c = get_city_by_code(code)
        if not c:
            continue
        btns.append(
            ft.OutlinedButton(
                text=f"{c['name']} ({c['code']})",
                on_click=lambda e, code=c["code"]: on_open(code) if on_open else None,
            )
        )
    # چندستونی بدون Wrap: تقسیم به ردیف‌ها
    rows = []
    for i in range(0, len(btns), per_row):
        rows.append(ft.Row(controls=btns[i:i+per_row], spacing=8))
    return ft.Column(controls=rows, spacing=8)

def refresh_popular():
    global popular_area, page_global
    union_codes = get_union_popular_codes()
    popular_buttons_block = build_popular_buttons_for_codes(union_codes, per_row=5, on_open=open_city)
    # جایگزینی محتوا
    popular_area.controls = popular_buttons_block.controls
    if popular_area.page is not None:
        popular_area.update()

# --------- مدیریت فوکوس ----------
def set_focus(e: ft.ControlEvent):
    global current_focus
    current_focus = e.control

# --------- عملیات شهری ----------
def open_city(code):
    global selected_city
    c = get_city_by_code(code)
    if not c:
        show_snack(f"شهر با کد {code} یافت نشد.")
        return
    selected_city = c
    # نمایش نام و قیمت و فوکوس روی تعداد
    result_text.value = f"شهر: {c['name']} | قیمت هر کالا: {format_price(c['price'])} تومان"
    result_text.update()
    qty_input.value = ""
    qty_input.focus()

def handle_enter():
    # بسته به فوکوس فعلی
    if current_focus == code_input:
        code = code_input.value.strip()
        if code:
            open_city(code)
        else:
            show_snack("کد شهر را وارد کنید.")
    elif current_focus == search_input:
        query = search_input.value
        matches = search_cities(query)
        if matches:
            open_city(matches[0]["code"])
        else:
            show_snack("نتیجه‌ای یافت نشد.")
    elif current_focus == qty_input:
        compute_and_log()
    else:
        # پیش‌فرض: اگر هیچ فیلد خاصی فوکوس ندارد، Enter را برای کد شهر در نظر بگیر
        if code_input:
            code_input.focus()

def compute_and_log():
    global selected_city
    if not selected_city:
        show_snack("ابتدا شهر را انتخاب کنید.")
        return
    qty_str = (qty_input.value or "").strip()
    if not qty_str.isdigit():
        show_snack("تعداد کالا باید عدد باشد.")
        return
    qty = int(qty_str)
    price = int(selected_city["price"])
    amount = qty * price
    result_text.value = f"تعداد: {qty} | مبلغ نهایی: {format_price(amount)} تومان"
    result_text.update()

    # ثبت لاگ
    logs = load_logs()
    logs.append({
        "time": datetime.datetime.now().isoformat(timespec="seconds"),
        "code": selected_city["code"],
        "name": selected_city["name"],
        "qty": qty,
        "amount": amount
    })
    save_logs(logs)

    # بروزرسانی محبوب‌ها بر اساس لاگ جدید
    refresh_popular()
        # بعد از محاسبه، فوکوس سریع برگردد روی کد شهر
    code_input.focus()

# --------- ابزارهای نمایش ----------
def format_price(n):
    try:
        return f"{int(n):,}"
    except:
        return str(n)

def show_snack(msg):
    page_global.snack_bar = ft.SnackBar(ft.Text(msg), open=True)

# --------- کیبورد سراسری ----------
def keyboard_handler(e: ft.KeyboardEvent):
    global current_focus
    key = e.key

    # اگر در فرم افزودن/ویرایش هستیم، دخالت نکن
    if current_focus in add_fields:
        return

    # Tab فقط بین جستجو و کد شهر جابجا شود
    if key == "TAB":
        if current_focus == code_input:
            search_input.focus()
        else:
            code_input.focus()
        return

    # اعداد مستقیم وارد کد شهر
    if len(key) == 1 and key.isdigit():
        code_input.focus()
        code_input.value = (code_input.value or "") + key
        code_input.update()
        return

    if key == "ENTER":
        handle_enter()
    elif key == "F2":
        page_global.go("/archive")
    elif key == "ESC":
        page_global.go("/")

# --------- فرم افزودن/ویرایش شهر ----------
def build_city_form():
    global fav_toggle
    code_tf = ft.TextField(label="کد شهر", on_focus=set_focus)
    name_tf = ft.TextField(label="نام شهر", on_focus=set_focus)
    price_tf = ft.TextField(label="قیمت هر کالا (تومان)", on_focus=set_focus)
    fav_toggle = ft.Switch(label="محبوب (دستی)", value=False)

    add_fields.update({code_tf, name_tf, price_tf})

    def fill_if_exists(e):
        # اگر کد موجود است، اتوماتیک مقادیر را پر کن
        c = get_city_by_code(code_tf.value.strip())
        if c:
            name_tf.value = c["name"]
            price_tf.value = str(c["price"])
            fav_toggle.value = bool(c.get("is_favorite"))
            name_tf.update()
            price_tf.update()
            fav_toggle.update()

    code_tf.on_change = fill_if_exists

    def save_city(e):
        code = (code_tf.value or "").strip()
        name = (name_tf.value or "").strip()
        price_str = (price_tf.value or "").strip()
        is_fav = bool(fav_toggle.value)

        if not code or not name or not price_str.isdigit():
            show_snack("اطلاعات را صحیح وارد کنید.")
            return

        price = int(price_str)
        existing = get_city_by_code(code)
        if existing:
            existing["name"] = name
            existing["price"] = price
            existing["is_favorite"] = is_fav
        else:
            cities.append({"code": code, "name": name, "price": price, "is_favorite": is_fav})
        save_cities()
        show_snack("ذخیره شد.")
        refresh_popular()

    return ft.Container(
        content=ft.Column([
            ft.Text("افزودن / ویرایش شهر", weight="bold", color=ft.Colors.WHITE),
            ft.Row([code_tf, name_tf, price_tf]),
            fav_toggle,
            ft.Row([ft.ElevatedButton("ذخیره", on_click=save_city)])
        ], spacing=12),
        padding=10,
        border_radius=8,
        bgcolor=ft.Colors.BLACK12  # یا BLACK26 برای تیره‌تر
    )


# --------- صفحه خانه ----------
def build_home_view():
    global popular_area, search_input, code_input, qty_input, result_text

    # نوار محبوب‌ها
    popular_area = ft.Column(spacing=8)

    # فیلدها
    search_input = ft.TextField(
        label="جستجو (نام یا کد شهر) - Enter برای انتخاب نتیجه اول",
        on_focus=set_focus,
    )
    # Enter روی جستجو: انتخاب نتیجه اول
    def on_search_submit(e):
        handle_enter()
    search_input.on_submit = lambda e: handle_enter()


    code_input = ft.TextField(
        label="کد شهر - Enter برای باز کردن",
        on_focus=set_focus,
    )
    code_input.on_submit = lambda e: handle_enter()

    qty_input = ft.TextField(
        label="تعداد کالا - Enter برای محاسبه",
        on_focus=set_focus,
        keyboard_type=ft.KeyboardType.NUMBER,
    )
    qty_input.on_submit = lambda e: handle_enter()

    result_text = ft.Text(value="")

    # فرم افزودن/ویرایش
    city_form = build_city_form()

    # بدنه
    content = ft.Container(
        content=ft.Column([
            ft.Text("ماشین‌حساب هزینه حمل"),
            ft.Divider(),
            ft.Text("شهرهای پرکاربرد"),
            popular_area,
            ft.Divider(),
            ft.Row([search_input]),
            ft.Row([code_input, qty_input]),
            result_text,
            ft.Divider(),
            city_form,
            ft.Divider(),
            ft.Row([
                ft.Text("میانبرها: Enter • F2 آرشیو • Esc بازگشت • تایپ مستقیم عدد برای کد شهر")
            ])
        ], spacing=14),
        padding=16
    )

    # پس از اضافه شدن کنترل‌ها به صفحه، محبوب‌ها را پر کن
    refresh_popular()

    return ft.View("/", controls=[content])

# --------- صفحه آرشیو ----------
def build_archive_view():
    logs = load_logs()
    rows = []
    # جدول ساده برای نمایش لاگ‌ها
    for i, entry in enumerate(reversed(logs), start=1):
        rows.append(
            ft.DataRow(cells=[
                ft.DataCell(ft.Text(str(i))),
                ft.DataCell(ft.Text(entry.get("time", ""))),
                ft.DataCell(ft.Text(entry.get("name", ""))),
                ft.DataCell(ft.Text(str(entry.get("code", "")))),
                ft.DataCell(ft.Text(str(entry.get("qty", "")))),
                ft.DataCell(ft.Text(format_price(entry.get("amount", 0))))
            ])
        )

    table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("#")),
            ft.DataColumn(ft.Text("زمان")),
            ft.DataColumn(ft.Text("شهر")),
            ft.DataColumn(ft.Text("کد")),
            ft.DataColumn(ft.Text("تعداد")),
            ft.DataColumn(ft.Text("مبلغ")),
        ],
        rows=rows
    )

    top = ft.Row([
        ft.Text("آرشیو محاسبات", weight="bold"),
        ft.Container(expand=1),
        ft.ElevatedButton("بازگشت (Esc)", on_click=lambda e: page_global.go("/"))
    ])

    return ft.View("/archive", controls=[top, table])

# --------- مدیریت مسیر ----------
def route_change(route):
    page_global.views.clear()
    if page_global.route == "/archive":
        page_global.views.append(build_archive_view())
    else:
        page_global.views.append(build_home_view())
    page_global.update()

# --------- main ----------
def main(page: ft.Page):
    global page_global
    page_global = page

    # فایل‌ها
    ensure_files()
    load_cities()

    # تنظیمات ظاهر
    page.title = "ماشین‌حساب هزینه حمل"
    page.window_icon = APP_ICON if os.path.isfile(APP_ICON) else None
    page.theme_mode = ft.ThemeMode.SYSTEM
    # فونت
    if os.path.isfile(IRAN_FONT):
        page.fonts = {"IranSans": IRAN_FONT}
        page.theme = ft.Theme(font_family="IranSans")
    else:
        page.theme = ft.Theme()  # بدون فونت سفارشی

    # رویدادهای صفحه
    page.on_route_change = route_change
    page.on_keyboard_event = keyboard_handler

    # نمایش اولیه
    route_change(page.route)

# اجرای برنامه
if __name__ == "__main__":
    ft.app(target=main, assets_dir=ASSETS_DIR)
