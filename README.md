# ⚖️ TISU Yuridik Klinika Telegram Bot

TISU talabalari uchun huquqiy yordam Telegram boti.

## Imkoniyatlar

- 🌐 **3 tilda ishlaydi**: O'zbek, Rus, Ingliz
- ❓ **Savol yuborish** — yuristga to'g'ridan-to'g'ri savol
- 📋 **6 turdagi ariza** — chetlash, tiklash, ko'chirish, ta'til, stipendiya, qayta topshirish
- 📊 **Murojaat kuzatuvi** — holat va javob bildirishnomalari
- ⚖️ **Yurist admin paneli** — javob berish, tasdiqlash, rad etish

## O'rnatish

### 1. Talablar
```bash
Python 3.10+
```

### 2. Bog'liqliklarni o'rnatish
```bash
cd tisu_bot
pip install -r requirements.txt
```

### 3. .env faylini sozlash
```bash
cp .env.example .env
# .env faylini tahrirlang:
nano .env
```

`.env` faylida to'ldiring:
```
BOT_TOKEN=BotFather dan olingan token
ADMIN_IDS=Sizning Telegram ID ingiz
LAWYER_IDS=Yuristlar Telegram ID lari
```

### 4. Telegram ID olish
[@userinfobot](https://t.me/userinfobot) ga `/start` yozing — ID ni ko'rasiz.

### 5. Botni ishga tushirish
```bash
python bot.py
```

## Fayl tuzilmasi

```
tisu_bot/
├── bot.py              # Asosiy kirish nuqtasi
├── config.py           # Sozlamalar
├── database.py         # SQLite bazasi
├── texts.py            # 3 tildagi matnlar
├── keyboards.py        # Tugmalar
├── handlers/
│   ├── __init__.py
│   ├── main.py         # Asosiy menyu
│   ├── questions.py    # Savol yuborish (FSM)
│   ├── applications.py # Ariza shakllantirish (FSM)
│   └── admin.py        # Yurist panel
├── requirements.txt
└── .env.example
```

## Admin panel buyruqlari

| Buyruq | Tavsif |
|--------|--------|
| `/admin` | Admin panelni ochish |

Admin panelda:
- ❓ Kutilayotgan savollarga javob yozish
- 📋 Arizalarni tasdiqlash / rad etish
- 📊 Statistikani ko'rish

## Server da ishlatish (systemd)

```ini
[Unit]
Description=TISU Legal Bot
After=network.target

[Service]
WorkingDirectory=/path/to/tisu_bot
ExecStart=/usr/bin/python3 bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable tisu-bot
sudo systemctl start tisu-bot
```
