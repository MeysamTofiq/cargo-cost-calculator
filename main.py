import flet as ft
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
    page.theme = ft.Theme(font_family="IranSans")
    page.scroll = ft.ScrollMode.AUTO

    cities = load_cities()

    def find_city_by_code(code):
        for c in cities:
            if c["code"] == code:
                return c
        return None

    def show_snack(msg, color=ft.Colors.RED):
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

    def build_city_list(filter_text=""):
        lv = ft.ListView(expand=True, spacing=5, padding=0)
        ft_text = filter_text.strip()
        for c in cities:
            if ft_text:
                if ft_text not in c["name"] and ft_text not in c["code"]:
                    continue
            tile = ft.ListTile(
                title=ft.Text(c["name"]),
                subtitle=ft.Text(f"کد: {c['code']}  |  هزینه هر کالا: {format_price(c['price'])}"),
                on_click=lambda e, code=c["code"]: open_city(code),
            )
            lv.controls.append(tile)
        return lv

    def build_home_view():
        code_input = ft.TextField(label="کد شهر", autofocus=True, on_submit=lambda e: open_city(code_input.value))
        search_input = ft.TextField(label="جستجوی شهر", on_change=lambda e: refresh_list())
        list_container = ft.Container(expand=True)

        def refresh_list():
            list_container.content = build_city_list(search_input.value)
            page.update()

        add_code = ft.TextField(label="کد", width=120)
        add_name = ft.TextField(label="نام شهر", expand=True)
        add_price = ft.TextField(label="هزینه هر کالا", width=160, keyboard_type=ft.KeyboardType.NUMBER)

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
            new_city = {"code": code, "name": name, "price": price, "popular": False}
            cities.append(new_city)
            save_cities(cities)
            add_code.value = ""
            add_name.value = ""
            add_price.value = ""
            refresh_list()
            show_snack("شهر اضافه شد.", color=ft.Colors.GREEN)

        add_btn = ft.ElevatedButton("افزودن شهر", on_click=add_city)

        home = ft.View(
            "/",
            controls=[
                ft.AppBar(title=ft.Text("ماشین‌حساب هزینه حمل")),
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Row([code_input], alignment=ft.MainAxisAlignment.START),
                            ft.Row([search_input], alignment=ft.MainAxisAlignment.START),
                            ft.Container(content=list_container, expand=True),
                            ft.Divider(),
                            ft.Text("افزودن شهر جدید", weight=ft.FontWeight.BOLD),
                            ft.Row([add_code, add_name, add_price, add_btn], spacing=8),
                        ],
                        expand=True,
                        spacing=10,
                    ),
                    padding=20,
                    expand=True,
                    bgcolor=ft.Colors.BLUE_GREY_50,
                    border_radius=12,
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

        def save_price(e):
            price_text = price_input.value.strip().replace(",", "")
            try:
                price = int(price_text)
            except:
                show_snack("هزینه معتبر نیست.")
                return
            city["price"] = price
            save_cities(cities)
            show_snack("قیمت بروزرسانی شد.", color=ft.Colors.GREEN)
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
            page.update()

        view = ft.View(
            f"/city/{code}",
            controls=[
                ft.AppBar(title=ft.Text(f"{city['name']} - {city['code']}")),
                ft.Container(
                    content=ft.Column(
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
                        ],
                        spacing=10,
                    ),
                    padding=20,
                    expand=True,
                    bgcolor=ft.Colors.BLUE_GREY_50,
                    border_radius=12,
                ),
            ],
        )
        qty_input.on_submit = calculate
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
                ft.Container(content=lv, padding=20, expand=True, bgcolor=ft.Colors.BLUE_GREY_50, border_radius=12),
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
        if e.key == "F2":
            page.go("/archive")
        elif e.key == "Escape":
            if page.route != "/":
                page.go("/")

    page.on_route_change = route_change
    page.on_keyboard_event = keyboard_handler

    page.go("/")


if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets")
