import flet as ft
import json
import os
from datetime import datetime
from collections import Counter
city_dialog = None
city_dialog_content = None

# ---------- فایل‌ها ----------
CITIES_FILE = "cities.json"
LOGS_FILE = "logs.json"

# ---------- وضعیت سراسری ----------
cities = []
logs = []
selected_city = None

current_focus = None
add_fields = set()

page_global = None

# ---------- کنترل‌ها ----------
code_input = None
search_input = None
qty_input = None
result_text = None
popular_area = None
search_results_column = None
city_name_text = None

# فرم افزودن/ویرایش
add_code_tf = None
add_name_tf = None
add_price_tf = None
add_fav_toggle = None


# ---------- کمک‌تابع‌های تم ----------
def is_light_theme():
    if page_global is None:
        return True
    if page_global.theme_mode == ft.ThemeMode.LIGHT:
        return True
    if page_global.theme_mode == ft.ThemeMode.DARK:
        return False
    # SYSTEM
    return page_global.platform_brightness == ft.Brightness.LIGHT

def text_color():
    return ft.Colors.BLACK87 if is_light_theme() else ft.Colors.WHITE

def subdued_text_color():
    return ft.Colors.BLACK54 if is_light_theme() else ft.Colors.GREY_300

def accent_text_color():
    return ft.Colors.CYAN_800 if is_light_theme() else ft.Colors.CYAN_300


def init_city_dialog():
    global city_dialog, city_dialog_content

    def close_dialog(e=None):
        city_dialog.open = False
        page_global.update()

    city_dialog_content = ft.Column(
        [],
        scroll=ft.ScrollMode.AUTO,
        height=400
    )

    city_dialog = ft.AlertDialog(
        title=ft.Text("لیست شهرها", color=text_color()),
        content=city_dialog_content,
        actions=[ft.TextButton("بستن", on_click=close_dialog)],
        modal=True
    )

    # اضافه به overlay فقط یک‌بار
    if city_dialog not in page_global.overlay:
        page_global.overlay.append(city_dialog)


# ---------- ابزارهای فایل ----------
def load_json(path, default):
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(default, f, ensure_ascii=False, indent=2)
        return default
    with open(path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except:
            return default

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def ensure_files():
    if not os.path.exists(CITIES_FILE):
        # 60 شهر نمونه (قابل ویرایش توسط کاربر)
        sample = []
        for i in range(1, 61):
            sample.append({
                "code": str(1000 + i),
                "name": f"شهر {i:02d}",
                "price": 10000 + i * 250,
                "is_favorite": False
            })
        save_json(CITIES_FILE, sample)

    if not os.path.exists(LOGS_FILE):
        save_json(LOGS_FILE, [])

def reload_data():
    global cities, logs
    cities = load_json(CITIES_FILE, [])
    logs = load_json(LOGS_FILE, [])

# ---------- محبوب‌ها ----------
def get_popular_cities():
    counts = Counter([l.get("code") for l in logs])
    top_codes = [c for c, _ in counts.most_common(5)]
    top = [get_city_by_code(code) for code in top_codes if get_city_by_code(code)]

    favorites = [c for c in cities if c.get("is_favorite")]
    result = []
    seen = set()
    for c in top + favorites:
        if c and c["code"] not in seen:
            result.append(c)
            seen.add(c["code"])
    return result

def refresh_popular():
    if popular_area is None or popular_area.page is None:
        return
    popular_area.controls.clear()

    popular = get_popular_cities()
    buttons = []
    for c in popular:
        btn = ft.OutlinedButton(
            f"{c['name']} ({c['code']})",
            on_click=lambda e, cc=c: open_city(cc)
        )
        buttons.append(btn)

    # شبیه‌سازی wrap با ردیف‌های 4تایی
    row_size = 4
    rows = []
    for i in range(0, len(buttons), row_size):
        rows.append(ft.Row(buttons[i:i+row_size], spacing=6))
    popular_area.controls.extend(rows)
    popular_area.update()

# ---------- جستجو ----------
def search_cities(query):
    q = (query or "").strip()
    if not q:
        return []

    popular_codes = {c["code"] for c in get_popular_cities()}

    def score(c):
        in_pop = 0 if c["code"] in popular_codes else 1
        exact_code = 0 if c["code"] == q else 1
        return (exact_code, in_pop, c["name"])

    results = [c for c in cities if q in c["name"] or q in c["code"]]
    results.sort(key=score)
    return results

def update_search_results():
    if search_results_column is None:
        return
    query = search_input.value if search_input else ""
    results = search_cities(query)

    search_results_column.controls.clear()
    for c in results[:10]:
        item = ft.TextButton(
            f"{c['name']} ({c['code']})",
            on_click=lambda e, cc=c: open_city(cc)
        )
        search_results_column.controls.append(item)
    search_results_column.update()

# ---------- مدیریت شهر ----------
def get_city_by_code(code):
    for c in cities:
        if c["code"] == str(code):
            return c
    return None

def open_city(city):
    global selected_city
    selected_city = city
    city_name_text.value = f"{city['name']} | کد: {city['code']} | هزینه واحد: {city['price']:,}"
    qty_input.value = ""
    city_name_text.update()
    qty_input.focus()

def compute_and_log():
    global logs
    if not selected_city:
        show_msg("ابتدا شهر را انتخاب کنید")
        return

    q = qty_input.value.strip() if qty_input.value else ""
    if not q.isdigit():
        show_msg("تعداد نامعتبر است")
        return

    qty = int(q)
    if qty <= 0:
        show_msg("تعداد باید بزرگ‌تر از صفر باشد")
        return

    total = qty * int(selected_city["price"])
    result_text.value = f"{selected_city['name']} — {total:,} تومان"
    result_text.update()

    logs.append({
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "code": selected_city["code"],
        "name": selected_city["name"],
        "qty": qty,
        "total": total
    })
    save_json(LOGS_FILE, logs)
    refresh_popular()
    code_input.focus()

def handle_enter():
    if current_focus == code_input:
        code = code_input.value.strip() if code_input.value else ""
        city = get_city_by_code(code)
        if city:
            open_city(city)
        else:
            show_msg("شهر یافت نشد")
    elif current_focus == search_input:
        results = search_cities(search_input.value)
        if results:
            open_city(results[0])
        else:
            show_msg("نتیجه‌ای یافت نشد")
    elif current_focus == qty_input:
        compute_and_log()

# ---------- UI پیام ----------
def show_msg(text):
    page_global.snack_bar = ft.SnackBar(ft.Text(text, color=text_color()))
    page_global.snack_bar.open = True
    page_global.update()

# ---------- فرم افزودن/ویرایش ----------
def save_city(e=None):
    code = add_code_tf.value.strip()
    name = add_name_tf.value.strip()
    price = add_price_tf.value.strip()
    fav = add_fav_toggle.value

    if not code or not name or not price.isdigit():
        show_msg("ورودی‌های فرم صحیح نیست")
        return

    existing = get_city_by_code(code)
    if existing:
        existing["name"] = name
        existing["price"] = int(price)
        existing["is_favorite"] = fav
    else:
        cities.append({
            "code": code,
            "name": name,
            "price": int(price),
            "is_favorite": fav
        })

    save_json(CITIES_FILE, cities)
    refresh_popular()
    show_msg("ذخیره شد")

def build_city_form():
    global add_code_tf, add_name_tf, add_price_tf, add_fav_toggle, add_fields
    add_code_tf = ft.TextField(label="کد شهر", width=120, on_focus=on_focus)
    add_name_tf = ft.TextField(label="نام شهر", width=200, on_focus=on_focus)
    add_price_tf = ft.TextField(label="هزینه واحد", width=140, keyboard_type=ft.KeyboardType.NUMBER, on_focus=on_focus)
    add_fav_toggle = ft.Checkbox(label="نشان‌دار", value=False)

    add_fields = {add_code_tf, add_name_tf, add_price_tf}

    return ft.Container(
        content=ft.Column([
            ft.Text("افزودن / ویرایش شهر", weight="bold", color=text_color()),
            ft.Row([add_code_tf, add_name_tf, add_price_tf]),
            add_fav_toggle,
            ft.Row([ft.ElevatedButton("ذخیره", on_click=save_city)])
        ], spacing=8),
        padding=10,
        border_radius=8,
        bgcolor=ft.Colors.BLACK12
    )

# ---------- لیست شهرها ----------
def show_city_list():
    

    if city_dialog is None:
        init_city_dialog()

    # ساخت لیست محتوا
    if not cities:
        city_dialog_content.controls = [ft.Text("لیست شهرها خالی است.", color=text_color())]
    else:
        city_dialog_content.controls = [
            ft.Text(f" {c['name']} - {c['price']:,} - {c['code']}", color=text_color()) for c in cities
        ]

    city_dialog.open = True
    page_global.update()
    

# ---------- فوکوس ----------
def on_focus(e):
    global current_focus
    current_focus = e.control

# ---------- رویدادهای کیبورد ----------
def keyboard_handler(e: ft.KeyboardEvent):
    global current_focus

    key = e.key
    route = page_global.route

    # اگر در آرشیو هستیم، فقط ESC کار کند
    if route == "/archive":
        if key in ("Escape", "ESC"):
            page_global.go("/")
        return
    
    # --- کلیدهای میانبر همیشه فعال باشند ---
    if key == "F2":
        page_global.go("/archive")
        return

    if key == "F3":
        show_city_list()
        return

    # اگر در فرم افزودن/ویرایش هستیم، بقیه‌ی کنترل‌ها را دست نزن
    if current_focus in add_fields:
        return

    if key in ("Tab", "TAB"):
        if current_focus == code_input:
            search_input.focus()
        else:
            code_input.focus()
        return

    if len(key) == 1 and key.isdigit():
        code_input.focus()
        code_input.value = (code_input.value or "") + key
        code_input.update()
        return

    if key in ("Enter", "NumpadEnter"):
        handle_enter()

# ---------- ویو اصلی ----------
def build_main_view():
    global code_input, search_input, qty_input, result_text, popular_area, search_results_column, city_name_text

    code_input = ft.TextField(
        label="کد شهر",
        width=160,
        on_submit=lambda e: handle_enter(),
        on_change=lambda e: None,
        on_focus=on_focus
    )

    search_input = ft.TextField(
        label="جستجو (کد/نام)",
        width=240,
        on_change=lambda e: update_search_results(),
        on_submit=lambda e: handle_enter(),
        on_focus=on_focus
    )

    qty_input = ft.TextField(
        label="تعداد",
        width=140,
        keyboard_type=ft.KeyboardType.NUMBER,
        on_submit=lambda e: compute_and_log(),
        on_focus=on_focus
    )

    show_list_btn = ft.OutlinedButton("نمایش لیست شهرها", on_click=lambda e: show_city_list())

    city_name_text = ft.Text("—", size=14, color=subdued_text_color())
    result_text = ft.Text("", size=22, weight="bold", color=accent_text_color())

    popular_area = ft.Column(spacing=6)

    search_results_column = ft.Column(spacing=4)

    main = ft.Column(
        [
            ft.Row([code_input, search_input, show_list_btn], spacing=10),
            ft.Row([qty_input], spacing=10),
            city_name_text,
            result_text,
            ft.Text("شهرهای پرکاربرد", weight="bold", color=text_color()),
            popular_area,
            ft.Text("نتایج جستجو", weight="bold", color=text_color()),
            search_results_column,
            build_city_form()
        ],
        spacing=12
    )

    return ft.View(
        route="/",
        controls=[
            ft.Container(main, padding=15)
        ]
    )

# ---------- آرشیو ----------
def build_archive_view():
    items = []
    for l in reversed(logs):
        total = l.get("total")
        if total is None:
            try:
                total = int(l.get("qty", 0)) * int(l.get("price", 0))
            except:
                total = 0

        items.append(
            ft.Text(
                f"{l.get('time','')} | {l.get('name','')} | تعداد: {l.get('qty','')} | مبلغ: {int(total):,}",
                color=text_color()
            )
        )

    content = ft.Column(items, scroll=ft.ScrollMode.AUTO)

    return ft.View(
        route="/archive",
        controls=[
            ft.Container(
                content=ft.Column([
                    ft.Text("آرشیو محاسبات", size=18, weight="bold", color=text_color()),
                    ft.Container(content=content, height=500),
                    ft.ElevatedButton("بازگشت", on_click=lambda e: page_global.go("/"))
                ], spacing=10),
                padding=15
            )
        ]
    )

# ---------- روتینگ ----------
def on_route_change(e):
    page_global.views.clear()
    if page_global.route == "/archive":
        page_global.views.append(build_archive_view())
    else:
        page_global.views.append(build_main_view())

    page_global.update()

    if page_global.route == "/":
        refresh_popular()
        code_input.focus()

def main(page: ft.Page):
    global page_global
    page_global = page

    page.title = "ماشین حساب هزینه حمل"
    page.rtl = True
    page.theme_mode = ft.ThemeMode.SYSTEM
    page.fonts = {"IranSans": "assets/IranSans.ttf"}
    page.theme = ft.Theme(font_family="IranSans")

    # --- همیشه روی همه پنجره‌ها ---
    page.window.always_on_top = True

    try:
        page.window.icon = "icon.ico"
    except Exception as e:
        print(f"خطا در بارگذاری آیکون: {e}") # چاپ خطا برای دیباگ

    ensure_files()
    reload_data()

    page.on_keyboard_event = keyboard_handler
    page.on_route_change = on_route_change
    init_city_dialog()
    page.go("/")

ft.app(target=main, assets_dir="assets")
