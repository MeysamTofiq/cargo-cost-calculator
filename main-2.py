import flet as ft
colors = ft.Colors
import json
import os
from datetime import datetime

DATA_DIR = "."
CITIES_FILE = os.path.join(DATA_DIR, "cities.json")
LOGS_FILE = os.path.join(DATA_DIR, "logs.json")


def ensure_files():
    if not os.path.exists(CITIES_FILE):
        with open(CITIES_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)
    if not os.path.exists(LOGS_FILE):
        with open(LOGS_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)


def load_cities():
    with open(CITIES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_cities(cities):
    with open(CITIES_FILE, "w", encoding="utf-8") as f:
        json.dump(cities, f, ensure_ascii=False, indent=2)


def load_logs():
    with open(LOGS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def append_log(entry):
    logs = load_logs()
    logs.append(entry)
    with open(LOGS_FILE, "w", encoding="utf-8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)


def main(page: ft.Page):
    ensure_files()

    page.title = "ماشین‌حساب هزینه حمل"
    page.window_width = 1000
    page.window_height = 720
    page.window_icon = "assets/icon.png"
    page.rtl = True
    page.fonts = {"IranSans": "assets/IranSans.ttf"}

    # تم سیستم (دارک/لایت)
    page.theme_mode = ft.ThemeMode.SYSTEM
    page.theme = ft.Theme(font_family="IranSans", color_scheme_seed=colors.BLUE)

    page.dark_theme = ft.Theme(
        font_family="IranSans",
        color_scheme_seed=colors.BLUE,
    )

    page.theme_mode = ft.ThemeMode.SYSTEM

    page.scroll = ft.ScrollMode.AUTO

    cities = load_cities()

    # مرجع کنترل‌ها برای مدیریت کیبورد
    ui = {
        "code_input": None,
        "search_input": None,
        "filtered": [],
    }

    def panel_container(content):
        return ft.Container(
            content=content,
            padding=20,
            expand=True,
            bgcolor=colors.with_opacity(0.06, colors.ON_SURFACE),
            border_radius=12,
        )

    def find_city_by_code(code):
        for c in cities:
            if c["code"] == code:
                return c
        return None

    def show_snack(msg, color=colors.RED):
        page.snack_bar = ft.SnackBar(ft.Text(msg), bgcolor=color)
        page.snack_bar.open = True
        page.update()

    def open_city(code):
        code = code.strip()
        if not code:
            show_snack("کد شهر را وارد کنید.")
            return
        city = find_city_by_code(code)
        if not city:
            show_snack("شهر با این کد یافت نشد.")
            return
        page.go(f"/city/{code}")

    def format_price(p):
        return f"{int(p):,} تومان"

    def get_filtered_cities(filter_text=""):
        txt = filter_text.strip()
        result = []
        for c in cities:
            if not txt or (txt in c["name"] or txt in c["code"]):
                result.append(c)
        # اولویت با شهرهای پرکاربرد
        result.sort(key=lambda c: (not c.get("popular", False), c["name"]))
        return result

    def build_city_list(cities_list):
        lv = ft.ListView(expand=True, spacing=5, padding=0)
        for c in cities_list:
            tile = ft.ListTile(
                title=ft.Text(c["name"]),
                subtitle=ft.Text(f"کد: {c['code']}  |  هزینه هر کالا: {format_price(c['price'])}"),
                on_click=lambda e, code=c["code"]: open_city(code),
            )
            lv.controls.append(tile)
        return lv

    def open_top_search_result():
        filtered = get_filtered_cities(ui["search_input"].value if ui["search_input"] else "")
        ui["filtered"] = filtered
        if not filtered:
            show_snack("نتیجه‌ای یافت نشد.")
            return
        open_city(filtered[0]["code"])


    def build_popular_buttons(popular_cities, per_row=4):
        rows = []
        for i in range(0, len(popular_cities), per_row):
            chunk = popular_cities[i:i + per_row]
            row = ft.Row(
                controls=[
                    ft.OutlinedButton(
                        text=f"{c['name']} ({c['code']})",
                        on_click=lambda e, code=c["code"]: open_city(code),
                    )
                    for c in chunk
                ],
                spacing=8,
            )
            rows.append(row)
        return ft.Column(rows, spacing=8)

    def build_home_view():
        code_input = ft.TextField(label="کد شهر", autofocus=True, on_submit=lambda e: open_city(code_input.value))
        search_input = ft.TextField(
            label="جستجوی شهر",
            on_change=lambda e: refresh_list(),
            on_submit=lambda e: open_top_search_result(),
        )
        list_container = ft.Container(expand=True)

        ui["code_input"] = code_input
        ui["search_input"] = search_input

        def refresh_list():
            filtered = get_filtered_cities(search_input.value)
            ui["filtered"] = filtered
            list_container.content = build_city_list(filtered)
            page.update()

        add_code = ft.TextField(label="کد", width=120)
        add_name = ft.TextField(label="نام شهر", expand=True)
        add_price = ft.TextField(label="هزینه هر کالا", width=160, keyboard_type=ft.KeyboardType.NUMBER)
        add_popular = ft.Checkbox(label="پرکاربرد")

        def add_city(e):
            code = add_code.value.strip()
            name = add_name.value.strip()
            price_text = add_price.value.strip().replace(",", "")
            if not code or not name or not price_text:
                show_snack("همه فیلدها را تکمیل کنید.")
                return
            if find_city_by_code(code):
                show_snack("کد شهر تکراری است.")
                return
            try:
                price = int(price_text)
            except:
                show_snack("هزینه معتبر نیست.")
                return
            new_city = {"code": code, "name": name, "price": price, "popular": bool(add_popular.value)}
            cities.append(new_city)
            save_cities(cities)
            add_code.value = ""
            add_name.value = ""
            add_price.value = ""
            add_popular.value = False
            refresh_list()
            show_snack("شهر اضافه شد.", color=colors.GREEN)

        add_btn = ft.ElevatedButton("افزودن شهر", on_click=add_city)

        # نمایش شهرهای پرکاربرد به صورت دکمه
       
        popular_cities = [c for c in cities if c.get("popular", False)]
        popular_cities.sort(key=lambda c: c["name"])
        popular_buttons = build_popular_buttons(popular_cities, per_row=4)
        for c in popular_cities:
            popular_buttons.controls.append(
                ft.OutlinedButton(
                    text=f"{c['name']} ({c['code']})",
                    on_click=lambda e, code=c["code"]: open_city(code),
                )
            )

        home = ft.View(
            "/",
            controls=[
                ft.AppBar(title=ft.Text("ماشین‌حساب هزینه حمل")),
                panel_container(
                    ft.Column(
                        [
                            ft.Text("شهرهای پرکاربرد", weight=ft.FontWeight.BOLD),
                            popular_buttons,
                            ft.Divider(),
                            ft.Row([code_input], alignment=ft.MainAxisAlignment.START),
                            ft.Row([search_input], alignment=ft.MainAxisAlignment.START),
                            ft.Container(content=list_container, expand=True),
                            ft.Divider(),
                            ft.Text("افزودن شهر جدید", weight=ft.FontWeight.BOLD),
                            ft.Row([add_code, add_name, add_price, add_popular, add_btn], spacing=8),
                        ],
                        expand=True,
                        spacing=10,
                    )
                ),
            ],
        )
        refresh_list()
        return home

    def build_city_view(code):
        city = find_city_by_code(code)
        if not city:
            page.go("/")
            return ft.View("/")

        price_input = ft.TextField(
            label="هزینه هر کالا",
            value=str(city["price"]),
            keyboard_type=ft.KeyboardType.NUMBER,
            width=200,
        )

        qty_input = ft.TextField(label="تعداد کالا", keyboard_type=ft.KeyboardType.NUMBER, autofocus=True)
        result_text = ft.Text("", size=16, weight=ft.FontWeight.BOLD)

        history_lv = ft.ListView(expand=True, spacing=6)

        def refresh_history():
            logs = load_logs()
            items = [l for l in logs if l["code"] == code]
            items = list(reversed(items))  # جدیدترین اول
            history_lv.controls.clear()
            for item in items:
                history_lv.controls.append(
                    ft.ListTile(
                        title=ft.Text(f"{item['qty']} عدد"),
                        subtitle=ft.Text(f"{item['ts']}  |  مبلغ: {format_price(item['total'])}"),
                    )
                )
            page.update()

        def save_price(e):
            price_text = price_input.value.strip().replace(",", "")
            try:
                price = int(price_text)
            except:
                show_snack("هزینه معتبر نیست.")
                return
            city["price"] = price
            save_cities(cities)
            show_snack("قیمت بروزرسانی شد.", color=colors.GREEN)
            page.update()

        def calculate(e):
            qty_text = qty_input.value.strip().replace(",", "")
            try:
                qty = int(qty_text)
                if qty <= 0:
                    raise ValueError
            except:
                show_snack("تعداد معتبر نیست.")
                return
            total = qty * city["price"]
            result_text.value = f"مبلغ نهایی: {format_price(total)}"
            entry = {
                "ts": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "code": city["code"],
                "name": city["name"],
                "qty": qty,
                "total": total,
            }
            append_log(entry)
            refresh_history()

        view = ft.View(
            f"/city/{code}",
            controls=[
                ft.AppBar(title=ft.Text(f"{city['name']} - {city['code']}")),
                panel_container(
                    ft.Column(
                        [
                            ft.Text(f"شهر: {city['name']}  |  کد: {city['code']}"),
                            ft.Row(
                                [
                                    price_input,
                                    ft.ElevatedButton("ذخیره قیمت", on_click=save_price),
                                ],
                                spacing=8,
                            ),
                            ft.Divider(),
                            ft.Row([qty_input], alignment=ft.MainAxisAlignment.START),
                            ft.ElevatedButton("محاسبه", on_click=calculate),
                            result_text,
                            ft.Divider(),
                            ft.Text("سوابق این شهر", weight=ft.FontWeight.BOLD),
                            history_lv,
                        ],
                        spacing=10,
                    )
                ),
            ],
        )
        qty_input.on_submit = calculate
        refresh_history()
        return view

    def build_archive_view():
        logs = load_logs()
        logs = list(reversed(logs))
        lv = ft.ListView(expand=True, spacing=6)
        for item in logs:
            lv.controls.append(
                ft.ListTile(
                    title=ft.Text(f"{item['name']} ({item['code']})"),
                    subtitle=ft.Text(
                        f"زمان: {item['ts']}  |  تعداد: {item['qty']}  |  مبلغ: {format_price(item['total'])}"
                    ),
                )
            )

        view = ft.View(
            "/archive",
            controls=[
                ft.AppBar(title=ft.Text("آرشیو محاسبات")),
                panel_container(lv),
            ],
        )
        return view

    def route_change(e):
        page.views.clear()
        if page.route == "/":
            page.views.append(build_home_view())
        elif page.route.startswith("/city/"):
            code = page.route.split("/city/")[-1]
            page.views.append(build_city_view(code))
        elif page.route == "/archive":
            page.views.append(build_archive_view())
        page.update()

    def keyboard_handler(e: ft.KeyboardEvent):
        # میانبرها
        if e.key == "F2":
            page.go("/archive")
            return
        if e.key == "Escape":
            if page.route != "/":
                page.go("/")
            return

        if page.route == "/":
            code_input = ui.get("code_input")
            search_input = ui.get("search_input")

            # تایپ عدد بدون کلیک
            if len(e.key) == 1 and e.key.isdigit() and not (getattr(e, "alt", False) or getattr(e, "ctrl", False) or getattr(e, "meta", False)):
                if code_input:
                    if not code_input.focused:
                        code_input.focus()
                    code_input.value = (code_input.value or "") + e.key
                    page.update()
                return

            # Backspace برای کد شهر
            if e.key == "Backspace":
                if code_input:
                    code_input.value = (code_input.value or "")[:-1]
                    page.update()
                return

            # Enter: اگر جستجو فوکوس بود -> نتیجه بالا، در غیر اینصورت کد شهر
            if e.key == "Enter":
                if search_input and search_input.focused:
                    open_top_search_result()
                else:
                    if code_input and code_input.value.strip():
                        open_city(code_input.value)
                    else:
                        open_top_search_result()

    page.on_route_change = route_change
    page.on_keyboard_event = keyboard_handler
    page.go("/")


if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets")
