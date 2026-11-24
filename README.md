# محاسبه‌گر هزینه حمل و نقل (Cargo Cost Calculator)

## معرفی (فارسی)

نرم‌افزار دسکتاپ برای **محاسبه هزینه حمل بار بر اساس شهرستان** — شهرها و نرخ‌هایشان را در `cities.json` تنظیم می‌کنید و برنامه بر اساس شهر مبدا/مقصد و مشخصات محموله، هزینه حمل را محاسبه و در `logs.json` ثبت می‌کند.

### ویژگی‌ها

- 🚚 محاسبه هزینه حمل بر اساس شهرستان (دیتای شهرها در `cities.json`)
- ⚙️ مدیریت شهرها و نرخ‌ها از داخل برنامه
- 🧾 ثبت سابقه محاسبات (`logs.json`) و تاریخچه
- 🖥 رابط گرافیکی مدرن (Flet/Flutter)

### فناوری

Python · Flet · JSON

### اجرا

```bash
pip install flet
python main.py
```

> نسخه‌های تکاملی (`main-2.py` تا `main-5.py`, `CargoBudTest`) هم موجودند.

---

# Cargo Cost Calculator

## Overview (English)

A desktop app for **calculating shipping costs based on destination city** — configure cities and their rates in `cities.json`, and the app computes freight costs from origin/destination and cargo details, logging each calculation to `logs.json`.

### Features

- 🚚 City-based freight calculation (`cities.json` data)
- ⚙️ Manage cities & rates from within the app
- 🧾 Calculation history log
- 🖥 Modern GUI (Flet)

### Tech Stack

Python · Flet · JSON

### Run

```bash
pip install flet
python main.py
```
