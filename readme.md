# 💰 Telegram Simple Finance Manager (TSFM)

An asynchronous Telegram bot for personal finance tracking with automatic language detection, currency selection, and Excel data export.

## ✅ Features

* **Multi-language Support**: Automatic detection of the user's language (EN, RU, UK, ES, DE) using the `langdetect` library.
* **Expense Tracking**: Simple input format: `Amount Category` (e.g., `50 Food`).
* **Currency Selection**: Support for **₴, $, €, and ₽**. Settings are saved individually for each user in the database.
* **Data Management**: "Delete Last" button to quickly undo the most recent entry.
* **Excel Export**: Generates a professional `.xlsx` report with all transaction history and timestamps.
* **Local Storage**: Uses **SQLite** (via `aiosqlite`), ensuring your financial data stays private on your own machine/server.

## 🛠 Requirements

* **Python 3.10+**
* **aiogram 3.x** (Modern Asynchronous Telegram Bot API)
* **aiosqlite** (Asynchronous SQLite wrapper)
* **pandas** & **openpyxl** (Data processing & Excel generation)
* **langdetect** (Language identification)