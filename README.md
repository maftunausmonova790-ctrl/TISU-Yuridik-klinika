# ⚖️ Yuridik Maslahat Boti

O'zbek qonunlari asosida maslahat beruvchi Telegram bot.

## Imkoniyatlar

| Modul | Tavsif |
|-------|--------|
| ❓ Savol-javob | Foydalanuvchi savol → admin javob |
| 🤖 Avtomatik javob | Qonun bazasidan dastlabki javob |
| 🔍 Qonun qidirish | Kalit so'z bo'yicha qonun topish |
| 🗂 Kategoriyalar | Mehnat, Oila, Mulk, Jinoiy, Ma'muriy, Tadbirkorlik |
| 📋 Nizomlar | Hujjat va nizomlar bo'limi |
| 🔒 Anonimlik | Yashirib savol yuborish |
| 🔔 Bildirishnomalar | Javob kelganda xabar |
| 📊 Statistika | Eng ko'p so'raladigan kategoriyalar |
| 📢 Broadcast | Barcha foydalanuvchilarga xabar |
| 🌐 3 tilda | O'zbek, Rus, Ingliz |

---

## O'rnatish

```bash
pip install -r requirements.txt
```

## .env fayli

```
BOT_TOKEN=BotFather_dan_token
ADMIN_IDS=sizning_telegram_id
BOT_NAME=Yuridik Maslahat Boti
```

Bir nechta admin:
```
ADMIN_IDS=111222333,444555666
```

## Ishga tushirish

```bash
python bot.py
```

---

## Railway Deploy

1. GitHub ga yuklang (faqat `bot.py` va `requirements.txt`)
2. Railway → New Project → GitHub repo
3. Variables ga qo'shing: `BOT_TOKEN`, `ADMIN_IDS`, `BOT_NAME`
4. Settings → Start Command: `python bot.py`
5. Deploy ✅

---

## Qonunlar bazasini to'ldirish

`bot.py` dagi `LAWS_DB` dict ni to'ldiring:

```python
LAWS_DB = {
    "mehnat": [
        {
            "title": "Modda nomi",
            "article": "Mehnat kodeksi 134-modda",
            "text": "Modda matni...",
            "keywords": ["ta'til", "отпуск", "vacation"],
        },
        # ...ko'proq qonunlar...
    ],
    "oila": [...],
    # va hokazo
}
```

## FAQ ni o'zgartirish

`FAQ_DATA` dict ni tahrirlang:

```python
FAQ_DATA = {
    "uz": [
        ("Savol matni?", "Javob matni..."),
        # ...
    ],
    "ru": [...],
    "en": [...],
}
```

## Nizom qo'shish (bot orqali)

Admin `/admin` → "📋 Nizom qo'shish" tugmasini bosing va:
1. Sarlavha yozing
2. Kategoriya yozing
3. Matn yozing yoki fayl yuboring

---

## Admin buyruqlari

| Buyruq | Tavsif |
|--------|--------|
| `/admin` | Admin panelni ochish |

Admin panelda:
- Kutilayotgan savollarga javob yozish
- Nizom qo'shish
- Statistika ko'rish
- Barcha foydalanuvchilarga xabar yuborish
