import asyncio
import logging
import pandas as pd
from datetime import datetime
import aiosqlite
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton

API_TOKEN = 'YOUR-TOKEN'
logging.basicConfig(level=logging.INFO)

LANGS = {
    'en': {
        'start': "Hi! Choose your currency:",
        'stats': "📊 All-time stats:",
        'export': "Exporting Excel...",
        'error': "❌ Error! Format: 'Amount Category'",
        'saved': "✅ Saved: {amount} {curr} for {cat}",
        'deleted': "🗑 Last record deleted",
        'empty': "No data yet",
        'btn_stats': "📈 Stats",
        'btn_excel': "📥 Export",
        'btn_delete': "🔙 Delete last"
    },
    'ru': {
        'start': "Привет! Выбери валюту для учета:",
        'stats': "📊 Статистика за всё время:",
        'export': "Выгружаю Excel...",
        'error': "❌ Ошибка! Формат: 'Сумма Категория'",
        'saved': "✅ Сохранено: {amount} {curr} на {cat}",
        'deleted': "🗑 Последняя запись удалена",
        'empty': "Данных пока нет",
        'btn_stats': "📈 Статистика",
        'btn_excel': "📥 Экспорт",
        'btn_delete': "🔙 Удалить последнюю"
    },
    'uk': {
        'start': "Привіт! Обери валюту для обліку:",
        'stats': "📊 Статистика за весь час:",
        'export': "Завантажую Excel...",
        'error': "❌ Помилка! Формат: 'Сума Категорія'",
        'saved': "✅ Збережено: {amount} {curr} на {cat}",
        'deleted': "🗑 Остання запіс видалена",
        'empty': "Даних ще немає",
        'btn_stats': "📈 Статистика",
        'btn_excel': "📥 Експорт",
        'btn_delete': "🔙 Видалити останню"
    },
    'pl': {
        'start': "Cześć! Wybierz walutę do rozliczeń:",
        'stats': "📊 Statystyki z całego czasu:",
        'export': "Eksportowanie do Excela...",
        'error': "❌ Błąd! Format: 'Kwota Kategoria'",
        'saved': "✅ Zapisano: {amount} {curr} na {cat}",
        'deleted': "🗑 Ostatni wpis został usunięty",
        'empty': "Brak danych",
        'btn_stats': "📈 Statystyki",
        'btn_excel': "📥 Eksport",
        'btn_delete': "🔙 Usuń ostatni"
    },
    'cs': {
        'start': "Ahoj! Vyberte měnu pro účetnictví:",
        'stats': "📊 Celková statistika:",
        'export': "Exportování do Excelu...",
        'error': "❌ Chyba! Formát: 'Částka Kategorie'",
        'saved': "✅ Uloženo: {amount} {curr} za {cat}",
        'deleted': "🗑 Poslední záznam smazán",
        'empty': "Zatím žádná data",
        'btn_stats': "📈 Statistiky",
        'btn_excel': "📥 Export",
        'btn_delete': "🔙 Smazat poslední"
    },
    'ro': {
        'start': "Bună! Alege moneda pentru contabilitate:",
        'stats': "📊 Statistici din toate timpurile:",
        'export': "Exportarea în Excel...",
        'error': "❌ Eroare! Format: 'Sumă Categorie'",
        'saved': "✅ Salvat: {amount} {curr} pentru {cat}",
        'deleted': "🗑 Ultima înregistrare a fost ștearsă",
        'empty': "Nu există date încă",
        'btn_stats': "📈 Statistici",
        'btn_excel': "📥 Export",
        'btn_delete': "🔙 Șterge ultima"
    },
    'de': {
        'start': "Hallo! Wählen Sie Ihre Währung:",
        'stats': "📊 Gesamtstatistik:",
        'export': "Excel wird exportiert...",
        'error': "❌ Fehler! Format: 'Betrag Kategorie'",
        'saved': "✅ Gespeichert: {amount} {curr} für {cat}",
        'deleted': "🗑 Letzter Datensatz gelöscht",
        'empty': "Noch keine Daten",
        'btn_stats': "📈 Statistiken",
        'btn_excel': "📥 Export",
        'btn_delete': "🔙 Letzten löschen"
    },
    'fr': {
        'start': "Salut ! Choisissez votre devise :",
        'stats': "📊 Statistiques globales :",
        'export': "Exportation vers Excel...",
        'error': "❌ Erreur ! Format : 'Montant Catégorie'",
        'saved': "✅ Enregistré : {amount} {curr} pour {cat}",
        'deleted': "🗑 Dernier enregistrement supprimé",
        'empty': "Aucune donnée pour le moment",
        'btn_stats': "📈 Statistiques",
        'btn_excel': "📥 Export",
        'btn_delete': "🔙 Supprimer dernier"
    },
    'es': {
        'start': "¡Hola! Elige tu moneda:",
        'stats': "📊 Estadísticas históricas:",
        'export': "Exportando a Excel...",
        'error': "❌ ¡Error! Formato: 'Cantidad Categoría'",
        'saved': "✅ Guardado: {amount} {curr} en {cat}",
        'deleted': "🗑 Último registro eliminado",
        'empty': "No hay datos aún",
        'btn_stats': "📈 Estadísticas",
        'btn_excel': "📥 Exportar",
        'btn_delete': "🔙 Eliminar último"
    },
    'it': {
        'start': "Ciao! Scegli la tua valuta:",
        'stats': "📊 Statistiche totali:",
        'export': "Esportazione in Excel...",
        'error': "❌ Errore! Formato: 'Importo Categoria'",
        'saved': "✅ Salvato: {amount} {curr} per {cat}",
        'deleted': "🗑 Ultimo record cancellato",
        'empty': "Ancora nessun dato",
        'btn_stats': "📈 Statistiche",
        'btn_excel': "📥 Esporta",
        'btn_delete': "🔙 Elimina ultimo"
    }
}
def is_btn(text: str, key: str):
    return any(text == lang_values.get(key) for lang_values in LANGS.values())
async def init_db():
    async with aiosqlite.connect("finance.db") as db:
        await db.execute("CREATE TABLE IF NOT EXISTS expenses (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, amount REAL, category TEXT, date TEXT)")
        await db.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, currency TEXT DEFAULT '$')")
        await db.commit()
async def get_user_currency(user_id):
    async with aiosqlite.connect("finance.db") as db:
        async with db.execute("SELECT currency FROM users WHERE user_id = ?", (user_id,)) as cur:
            row = await cur.fetchone()
            return row[0] if row else "₴"
def get_lang(message: types.Message):
    code = message.from_user.language_code
    return code if code in LANGS else 'en'
def get_main_kb(lang):
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=LANGS[lang]['btn_stats']), KeyboardButton(text=LANGS[lang]['btn_excel'])],
            [KeyboardButton(text=LANGS[lang]['btn_delete'])]
        ],
        resize_keyboard=True
    )
bot = Bot(token=API_TOKEN)
dp = Dispatcher()
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    lang = get_lang(message)
    buttons = [
        [InlineKeyboardButton(text="₴ UAH", callback_data="set_curr_₴"), InlineKeyboardButton(text="$ USD", callback_data="set_curr_$")],
        [InlineKeyboardButton(text="€ EUR", callback_data="set_curr_€"), InlineKeyboardButton(text="₽ RUB", callback_data="set_curr_₽")]
    ]
    await message.answer(LANGS[lang]['start'], reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
@dp.callback_query(F.data.startswith("set_curr_"))
async def set_currency(callback: types.CallbackQuery):
    curr = callback.data.split("_")[-1]
    async with aiosqlite.connect("finance.db") as db:
        await db.execute("INSERT OR REPLACE INTO users (user_id, currency) VALUES (?, ?)", (callback.from_user.id, curr))
        await db.commit()
    await callback.message.answer(f"✅ Currency: {curr}", reply_markup=get_main_kb(get_lang(callback)))
    await callback.answer()
@dp.message(lambda msg: is_btn(msg.text, 'btn_stats'))
async def show_stats(message: types.Message):
    lang = get_lang(message)
    curr = await get_user_currency(message.from_user.id)
    async with aiosqlite.connect("finance.db") as db:
        async with db.execute("SELECT category, SUM(amount) FROM expenses WHERE user_id = ? GROUP BY category", (message.from_user.id,)) as cursor:
            rows = await cursor.fetchall()
            if not rows: return await message.answer(LANGS[lang]['empty'])
            text = f"{LANGS[lang]['stats']}\n"
            total = sum(r[1] for r in rows)
            for cat, amt in rows: text += f"• {cat}: {amt:.2f} {curr}\n"
            text += f"\n**Total: {total:.2f} {curr}**"
            await message.answer(text, parse_mode="Markdown")
@dp.message(lambda msg: is_btn(msg.text, 'btn_excel'))
async def export_excel(message: types.Message):
    lang = get_lang(message)
    async with aiosqlite.connect("finance.db") as db:
        async with db.execute("SELECT amount, category, date FROM expenses WHERE user_id = ?", (message.from_user.id,)) as c:
            rows = await c.fetchall()
            if not rows: return await message.answer(LANGS[lang]['empty'])
            df = pd.DataFrame(rows, columns=['Amount', 'Category', 'Date'])
            path = f"report_{message.from_user.id}.xlsx"
            df.to_excel(path, index=False)
            await message.answer_document(FSInputFile(path))
@dp.message(lambda msg: is_btn(msg.text, 'btn_delete'))
async def delete_last(message: types.Message):
    lang = get_lang(message)
    async with aiosqlite.connect("finance.db") as db:
        await db.execute("DELETE FROM expenses WHERE id = (SELECT id FROM expenses WHERE user_id = ? ORDER BY id DESC LIMIT 1)", (message.from_user.id,))
        await db.commit()
    await message.answer(LANGS[lang]['deleted'])
@dp.message()
async def save_expense(message: types.Message):
    if not message.text: return
    lang = get_lang(message)
    curr = await get_user_currency(message.from_user.id)
    try:
        parts = message.text.split(maxsplit=1)
        amount = float(parts[0].replace(',', '.'))
        category = parts[1] if len(parts) > 1 else "..."
        async with aiosqlite.connect("finance.db") as db:
            await db.execute("INSERT INTO expenses (user_id, amount, category, date) VALUES (?, ?, ?, ?)",
                             (message.from_user.id, amount, category, datetime.now().strftime("%Y-%m-%d %H:%M")))
            await db.commit()
        await message.answer(LANGS[lang]['saved'].format(amount=amount, curr=curr, cat=category))
    except:
        await message.answer(LANGS[lang]['error'])
async def main():
    await init_db()
    await dp.start_polling(bot)
if __name__ == "__main__":
    asyncio.run(main())