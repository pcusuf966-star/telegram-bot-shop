import os
import logging
import random
import string
from datetime import datetime, timedelta
from typing import Dict, Optional
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# Загрузка переменных окружения
load_dotenv()
TOKEN = os.getenv("TOKEN", "8357454901:AAGioA2mGfdCw_Ht5KkpU0ATE0svDyHNhk8")
ADMIN_ID = int(os.getenv("ADMIN_ID", 6392766209))

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Состояния для ConversationHandler
SELECTING_PAYMENT, UPLOAD_RECEIPT = range(2)

# Базы данных ключей
KEYS_DATABASE = {
    "Zolo 1 день": ["ZOLO-1D-k8Lp9nQ2mFvA", "ZOLO-1D-j3Rw7sY1bNcX", "ZOLO-1D-p5Tq2zU8dKgH"],
    "Zolo 3 дня": ["ZOLO-3D-7k4Mp9R2sT5V", "ZOLO-3D-X3yZ8cN1jL6p", "ZOLO-3D-H9dM2rS5tQ8w"],
    "Zolo 7 дней": ["ZOLO-7D-c8Lp2nQ5mFvR", "ZOLO-7D-a3Rw9sY1bNcT", "ZOLO-7D-k5Tq4zU8dKgS"],
    "Zolo 30 дней": ["ZOLO-30D-w8Lp3nQ2mFvS", "ZOLO-30D-e3Rw5sY1bNcV", "ZOLO-30D-r5Tq7zU8dKgM"],
    "Zolo 60 дней": ["ZOLO-60D-p5Lk9jQ3mFvR", "ZOLO-60D-w8Xs2tY6bNcV", "ZOLO-60D-r3Tq7zU1dKgM"]
}

# Использованные ключи
used_keys = {product: [] for product in KEYS_DATABASE.keys()}

# База данных (временная)
user_data = {}
orders = {}
referral_codes = {}

def generate_order_id() -> str:
    return ''.join(random.choices(string.digits, k=6))

def generate_referral_code(user_id: int) -> str:
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    referral_codes[code] = user_id
    return code

def get_key_for_product(product_name: str, quantity: int) -> list:
    """Получить ключи для продукта"""
    keys = []
    if product_name in KEYS_DATABASE:
        available_keys = [k for k in KEYS_DATABASE[product_name] if k not in used_keys[product_name]]
        if len(available_keys) >= quantity:
            for i in range(quantity):
                key = available_keys[i]
                keys.append(key)
                used_keys[product_name].append(key)
        else:
            keys = [f"ERROR: Недостаточно ключей для {product_name}"]
    return keys

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    if user_id not in user_data:
        user_data[user_id] = {
            "username": user.username or user.first_name,
            "balance": 0.0,
            "referral_code": generate_referral_code(user_id),
            "orders": []
        }
    welcome_text = (
        "W1NDY CONFIG - команда официальных реселлеров, предоставляем лучший и проверенные ключи для мобильных игр!\n\n"
        "❗️ Цены указаны в рублях, но мы децентрализованная организация и не привязываемся к странам. "
        "Мы также принимаем оплаты из 🇰🇿,🇧🇾,🇺🇦 \n\n"
        "💸 реферальная система :\n"
        "└ Приглашай своих друзей через свою реферальную ссылку и получай от 15% и выше от их покупок "
        "и выводи себе на электронный кошелек или карту\n\n"
        "♻️ - обновить меню команда /start\n\n"
        "➡️ - не могу купить в боте - @Attack_w1ndy"
    )
    
    keyboard = [
        [KeyboardButton("Каталог"), KeyboardButton("Мой кабинет 🏠")],
        [KeyboardButton("Как купить ?"), KeyboardButton("Тех.Поддержка")],
        [KeyboardButton("Отзывы / файлы")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    inline_keyboard = [[InlineKeyboardButton("Наш канал", url="https://t.me/w1ndy_config")]]
    inline_markup = InlineKeyboardMarkup(inline_keyboard)
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)
    await update.message.reply_text("👇 Наш канал с актуальными новостями и обновлениями:", reply_markup=inline_markup)

async def catalog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("PUBG MOBILE", callback_data="pubg_mobile")],
        [InlineKeyboardButton("DELTA FORCE", callback_data="delta_force")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выберите категорию:", reply_markup=reply_markup)

async def pubg_mobile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("ANDROID", callback_data="android")],
        [InlineKeyboardButton("IOS", callback_data="ios")],
        [InlineKeyboardButton("ANDROID ROOT", callback_data="android_root")],
        [InlineKeyboardButton("Назад ко всем категориям", callback_data="back_to_catalog")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = (
        "Описание:\n"
        "ПРИВАТНОСТЬ И СТАБИЛЬНОСТЬ — НАША ОСНОВА.\n"
        "НАШИ ПРОДУКТЫ ОТОБРАНЫ НАШИМИ ТЕСТИРОВЩИКАМИ! У НАС ВЫ НАЙДЕТЕ ЛУЧШИЕ ЧИТЫ!\n\n"
        "Выберите ваше устройство"
    )
    await query.edit_message_text(text, reply_markup=reply_markup)

async def android(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("ZOLO", callback_data="zolo")],
        [InlineKeyboardButton("UKI MOD", callback_data="uki_mod")],
        [InlineKeyboardButton("PULSE X", callback_data="pulse_x")],
        [InlineKeyboardButton("Z MOD", callback_data="z_mod")],
        [InlineKeyboardButton("Назад ко всем категориям", callback_data="back_to_catalog")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = (
        "# Описание:\n\n"
        "Приватный чит для PUBG MOBILE, который не обнаруживается системами защит.\n"
        "Мы следим за качеством продукта, за все время существования нашего проекта не было массовых блокировок"
    )
    await query.edit_message_text(text, reply_markup=reply_markup)

async def zolo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("Zolo 1 день", callback_data="zolo_1")],
        [InlineKeyboardButton("Zolo 3 дня", callback_data="zolo_3")],
        [InlineKeyboardButton("Zolo 7 дней", callback_data="zolo_7")],
        [InlineKeyboardButton("Zolo 30 дней", callback_data="zolo_30")],
        [InlineKeyboardButton("Zolo 60 дней", callback_data="zolo_60")],
        [InlineKeyboardButton("Назад ко всем категориям", callback_data="back_to_catalog")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = (
        "Описание: Zolo\n\n"
        "Приватный чит Zolo для игры PUBG Mobile Android. Одна из немногих программ, которой не нужны root права на устройстве. "
        "Зарекомендовал себя с хорошей стороны. Есть большая армия постоянных пользователей, которые покупают ключи активации и продлевают их. "
        "Чит оснащен всем необходимым набором возможностей, которые способы привести к заветной фразе Winner Winner Chiken Dinner.\n\n"
        "📌 Описание функций на скрине выше 📌\n\n"
        "- AИМ (150 метро) - данная функция помогает навестись на голову или тело противника\n"
        "- ВХ - функция с помощью которой вы сможете видеть своих противников через стены(пример в видео обзоре)\n"
        "- ЧИТ ОБДЛАДАЕТ СИЛЬНЕЙШИМ УРОВНЕМ БЕЗОПАСНОСТИ\n\n"
        "💡 Совместим с устройствами Android от 9 до 15, Для устройств 32/64 BIT, Поддерживаемые входы: Twitter, Facebook, гостевой, номер и вход по email, Рут права не требуются.\n"
        "✅ Работает в МЕТРО ,Classic и остальных режимах для версий Global, Korea ,VNG,Taiwan"
    )
    await query.edit_message_text(text, reply_markup=reply_markup)

async def zolo_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    product_map = {
        "zolo_1": {"name": "Zolo 1 день", "price": 170},
        "zolo_3": {"name": "Zolo 3 дня", "price": 400},
        "zolo_7": {"name": "Zolo 7 дней", "price": 800},
        "zolo_30": {"name": "Zolo 30 дней", "price": 1500},
        "zolo_60": {"name": "Zolo 60 дней", "price": 2000},
    }
    
    product_key = query.data
    product = product_map.get(product_key)
    
    if not product:
        return
    
    context.user_data["selected_product"] = product
    
    keyboard_buttons = []
    row = []
    for i in range(1, 11):
        row.append(InlineKeyboardButton(str(i), callback_data=f"quantity_{i}"))
        if len(row) == 5:
            keyboard_buttons.append(row)
            row = []
    if row:
        keyboard_buttons.append(row)
    
    keyboard_buttons.append([InlineKeyboardButton("Назад", callback_data="zolo")])
    keyboard_buttons.append([InlineKeyboardButton("Назад ко всем категориям", callback_data="back_to_catalog")])
    
    reply_markup = InlineKeyboardMarkup(keyboard_buttons)
    
    text = (
        f"Товар: {product['name']}\n"
        f"Цена: {product['price']} ₽\n\n"
        f"Выберите количество товара, которое хотите купить:"
    )
    await query.edit_message_text(text, reply_markup=reply_markup)

async def select_quantity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    quantity = int(query.data.split("_")[1])
    product = context.user_data.get("selected_product")
    
    if not product:
        await query.edit_message_text("Произошла ошибка. Пожалуйста, начните заново с /start")
        return
    
    total_price = product['price'] * quantity
    order_id = generate_order_id()
    
    user_id = query.from_user.id
    username = query.from_user.username or query.from_user.first_name
    
    order_data = {
        "order_id": order_id,
        "product": product['name'],
        "quantity": quantity,
        "total_price": total_price,
        "timestamp": datetime.now(),
        "user_id": user_id,
        "username": username,
        "status": "pending"
    }
    
    orders[order_id] = order_data
    context.user_data["current_order"] = order_data
    
    if user_id not in user_data:
        user_data[user_id] = {
            "username": username,
            "balance": 0.0,
            "referral_code": generate_referral_code(user_id),
            "orders": []
        }
    user_data[user_id]["orders"].append(order_data)
    
    await query.edit_message_text(
        f"Вы выбрали: {product['name']}\n"
        f"Количество: {quantity}\n"
        f"Общая сумма: {total_price} ₽\n\n"
        f"Выберите способ оплаты:"
    )
    
    keyboard = [
        [InlineKeyboardButton("СберБанк", callback_data="payment_sber")],
        [InlineKeyboardButton("OzonBank", callback_data="payment_ozon")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text("Выберите способ оплаты:", reply_markup=reply_markup)

async def payment_method(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    method = query.data
    order = context.user_data.get("current_order")
    
    if not order:
        await query.edit_message_text("Произошла ошибка. Пожалуйста, начните заново с /start")
        return
    
    sber_text = (
        "Для оплаты заказа намер заказа переведите цена на карту\n\n"
        "Сбер: 2202 2082 2937 7453\n"
        "Номер: +79604312170\n"
        "(Мавиля.А)\n\n"
        "Озон: 2204 3209 1914 2564\n"
        "Номер: +79604312170\n"
        "(Мавиля.А)\n\n"
        "Сохраните чек!\n"
        "После оплаты нажмите на кнопку 'Я оплатил'"
    )
    
    ozon_text = (
        "Для оплаты заказа намер заказа переведите цена на карту\n\n"
        "Озон: 2204 3209 1914 2564\n"
        "Номер: +79604312170\n"
        "(Мавиля.А)\n\n"
        "Сбер: 2202 2082 2937 7453\n"
        "Номер: +79604312170\n"
        "(Мавиля.А)\n\n"
        "Сохраните чек!\n"
        "После оплаты нажмите на кнопку 'Я оплатил'"
    )
    
    text = sber_text if method == "payment_sber" else ozon_text
    
    keyboard = [[InlineKeyboardButton("Я оплатил", callback_data="paid")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup)
    return SELECTING_PAYMENT

async def paid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    text = "Пришлите фото чека"
    keyboard = [[InlineKeyboardButton("Отменить оплату", callback_data="cancel_payment")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup)
    return UPLOAD_RECEIPT

async def handle_receipt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    order = context.user_data.get("current_order")
    
    if not order:
        await update.message.reply_text("Заказ не найден. Пожалуйста, начните заново с /start")
        return ConversationHandler.END
    
    if update.message.photo:
        order_id = order['order_id']
        if order_id in orders:
            orders[order_id]['status'] = 'waiting_payment'
        
        admin_text = (
            f"🛒 НОВЫЙ ЗАКАЗ ОЖИДАЕТ ПОДТВЕРЖДЕНИЯ!\n\n"
            f"📋 Заказ: #{order_id}\n"
            f"🛍️ Товар: {order['product']}\n"
            f"📦 Количество: {order['quantity']}\n"
            f"💰 Сумма: {order['total_price']} ₽\n"
            f"👤 Пользователь: @{update.effective_user.username or 'N/A'} (ID: {user_id})\n"
            f"⏰ Дата: {order['timestamp'].strftime('%d.%m.%Y %H:%M')}"
        )
        
        try:
            keyboard = [
                [InlineKeyboardButton("✅ Подтвердить заказ", callback_data=f"confirm_order_{order_id}")],
                [InlineKeyboardButton("❌ Отклонить заказ", callback_data=f"reject_order_{order_id}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await context.bot.send_message(
                chat_id=ADMIN_ID, 
                text=admin_text, 
                reply_markup=reply_markup
            )
            
            await context.bot.send_photo(chat_id=ADMIN_ID, photo=update.message.photo[-1].file_id)
            
        except Exception as e:
            logger.error(f"Ошибка отправки админу: {e}")
        
        user_text = (
            "✅ Заявка принята, как только Администратор @cr1ck_pahan увидит оплату примет вашу заявку!\n\n"
            "⏱️ Ожидайте проверки платежа, обычно заявка принимается в течение 5-10 минут "
            "но если заявка не принимается в течении 1 часа, напишите поддержке - @cr1ck_pahan, "
            "и ожидайте ответа) в ночное время с 23:00 время проверки заявки может быть больше обычного 🛎"
        )
        await update.message.reply_text(user_text)
        
        context.job_queue.run_once(cancel_order, 2400, data={
            'order_id': order_id,
            'user_id': user_id,
        })
        
        return ConversationHandler.END
    
    else:
        await update.message.reply_text("Отправьте файл")
        text = "Пришлите фото чека"
        keyboard = [[InlineKeyboardButton("Отменить оплату", callback_data="cancel_payment")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(text, reply_markup=reply_markup)
        return UPLOAD_RECEIPT

async def confirm_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    order_id = query.data.replace("confirm_order_", "")
    
    if order_id in orders:
        order = orders[order_id]
        user_id = order.get('user_id')
        
        if user_id:
            keys = get_key_for_product(order['product'], order['quantity'])
            
            if keys and not keys[0].startswith("ERROR"):
                keys_text = f"🔑 Ваши ключи для {order['product']}:\n\n"
                for i, key in enumerate(keys, 1):
                    keys_text += f"{i}. {key}\n"
                
                keys_text += "\n📝 Инструкция по активации:\n"
                keys_text += "1. Запустите Zolo чит\n"
                keys_text += "2. Введите ключ в соответствующее поле\n"
                keys_text += "3. Нажмите активировать\n\n"
                keys_text += "🆘 Если возникли проблемы - @Attack_w1ndy"
                
                try:
                    await context.bot.send_message(
                        chat_id=user_id,
                        text=keys_text
                    )
                    
                    await query.edit_message_text(
                        text=f"✅ Заказ #{order_id} подтвержден!\n"
                             f"Ключи отправлены пользователю.",
                        reply_markup=None
                    )
                    
                    orders[order_id]['status'] = 'completed'
                    
                    if user_id in user_data:
                        for user_order in user_data[user_id]["orders"]:
                            if user_order.get('order_id') == order_id:
                                user_order['status'] = 'completed'
                                break
                    
                except Exception as e:
                    logger.error(f"Ошибка отправки ключей: {e}")
                    await query.edit_message_text(
                        text=f"❌ Ошибка отправки ключей для заказа #{order_id}\n"
                             f"Ошибка: {str(e)[:100]}",
                        reply_markup=None
                    )
            else:
                error_msg = "Недостаточно ключей" if keys else "Ошибка получения ключей"
                await query.edit_message_text(
                    text=f"❌ {error_msg} для заказа #{order_id}",
                    reply_markup=None
                )
        else:
            await query.edit_message_text(
                text=f"❌ Не найден пользователь для заказа #{order_id}",
                reply_markup=None
            )
    else:
        await query.edit_message_text(
            text=f"❌ Заказ #{order_id} не найден",
            reply_markup=None
        )

async def reject_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    order_id = query.data.replace("reject_order_", "")
    
    if order_id in orders:
        order = orders[order_id]
        user_id = order.get('user_id')
        
        if user_id:
            try:
                await context.bot.send_message(
                    chat_id=user_id,
                    text=f"❌ Ваш заказ #{order_id} был отклонен администратором."
                )
            except:
                pass
        
        del orders[order_id]
    
    await query.edit_message_text(
        text=f"❌ Заказ #{order_id} отклонен",
        reply_markup=None
    )

async def cancel_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text("Оплата отменена. Вы можете начать заново с /start")
    return ConversationHandler.END

async def cancel_order(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    data = job.data
    order_id = data['order_id']
    user_id = data['user_id']
    
    if order_id in orders:
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=f"🕒 Заказ #{order_id} был отменен (истекло время оплаты)"
            )
        except:
            pass
        
        del orders[order_id]

async def my_account(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = user_data.get(user_id, {})
    
    text = (
        f"❤️ Имя: {user.get('username', 'N/A')}\n"
        f"🔑 ID: {user_id}\n"
        f"💰 Ваш баланс: {user.get('balance', 0)} ₽"
    )
    
    keyboard = [[InlineKeyboardButton("мои покупки", callback_data="my_orders")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(text, reply_markup=reply_markup)

async def my_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    user = user_data.get(user_id, {})
    orders_list = user.get("orders", [])
    
    if not orders_list:
        await query.edit_message_text("У вас нет активных заказов")
        return
    
    text = "Ваши покупки:\n\n"
    for order in orders_list[-5:]:
        status_text = {
            "pending": "⏳ Ожидание",
            "waiting_payment": "🔄 Ожидает оплаты",
            "completed": "✅ Завершен",
            "cancelled": "❌ Отменен"
        }.get(order.get('status', 'pending'), order.get('status', 'pending'))
        
        text += (
            f"📋 Заказ: #{order.get('order_id', 'N/A')}\n"
            f"🛍️ Товар: {order.get('product', 'N/A')}\n"
            f"📦 Количество: {order.get('quantity', 0)}\n"
            f"💰 Сумма: {order.get('total_price', 0)} ₽\n"
            f"📅 Дата: {order.get('timestamp', '').strftime('%d.%m.%Y %H:%M')}\n"
            f"📊 Статус: {status_text}\n\n"
        )
    
    await query.edit_message_text(text)

async def support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "😨 Возник вопрос или проблема?\n"
        "└ Просто напиши нам — мы всё решим максимально быстро!\n\n"
        "Главное правило:\n"
        "• Сразу указывай суть в одном сообщении, без длинных предисловий.\n"
        "• Если сложно описать словами — запиши короткое видео\n"
        "• Чем чётче и конкретнее обращение, тем быстрее мы сможем помочь. 🚀"
    )
    
    keyboard = [[InlineKeyboardButton("ПОДДЕРЖКА ПОЛЬЗОВАТЕЛЕЙ", url="https://t.me/cr1ck_pahan")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(text, reply_markup=reply_markup)

async def how_to_buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🎮 **Как купить?**\n\n"
        "1. Выберите товар в каталоге\n"
        "2. Укажите количество\n"
        "3. Оплатите заказ по указанным реквизитам\n"
        "4. Отправьте чек об оплате\n"
        "5. Получите ключ активации после проверки платежа\n\n"
        "⏱️ Обычная проверка занимает 5-10 минут\n"
        "📞 Если возникли проблемы - @Attack_w1ndy"
    )
    
    await update.message.reply_text(text)

async def reviews_files(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "Отзывов у нас много!\n\n"
        "- А все потому-что у нас самые лучшие пользователи 😉\n\n"
        "Туторы + файлы + решение всех ошибок при установке\n"
        "Всё в одном месте — удобно, быстро и надёжно! 🍀"
    )
    
    keyboard = [
        [InlineKeyboardButton("Отзывы", url="https://t.me/otziv_w1ndy")],
        [InlineKeyboardButton("Файлы", url="https://t.me/dozaobb")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(text, reply_markup=reply_markup)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if text == "Каталог":
        await catalog(update, context)
    elif text == "Мой кабинет 🏠":
        await my_account(update, context)
    elif text == "Как купить ?":
        await how_to_buy(update, context)
    elif text == "Тех.Поддержка":
        await support(update, context)
    elif text == "Отзывы / файлы":
        await reviews_files(update, context)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    
    if data.startswith("confirm_order_"):
        await confirm_order(update, context)
    elif data.startswith("reject_order_"):
        await reject_order(update, context)
    elif data == "back_to_catalog":
        await catalog(update, context)
    elif data == "pubg_mobile":
        await pubg_mobile(update, context)
    elif data == "android":
        await android(update, context)
    elif data == "zolo":
        await zolo(update, context)
    elif data.startswith("zolo_"):
        await zolo_product(update, context)
    elif data.startswith("quantity_"):
        await select_quantity(update, context)
    elif data.startswith("payment_"):
        await payment_method(update, context)
    elif data == "paid":
        await paid(update, context)
    elif data == "cancel_payment":
        await cancel_payment(update, context)
    elif data == "my_orders":
        await my_orders(update, context)
    elif data in ["ios", "android_root", "uki_mod", "pulse_x", "z_mod", "delta_force"]:
        await query.answer("Скоро будет доступно! 👷", show_alert=True)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Ошибка: {context.error}", exc_info=context.error)

def main():
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    
    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(paid, pattern="^paid$")],
        states={
            SELECTING_PAYMENT: [CallbackQueryHandler(paid, pattern="^paid$")],
            UPLOAD_RECEIPT: [
                CallbackQueryHandler(cancel_payment, pattern="^cancel_payment$"),
                MessageHandler(filters.ALL, handle_receipt)
            ]
        },
        fallbacks=[]
    )
    application.add_handler(conv_handler)
    
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_error_handler(error_handler)
    
    print("✅ Бот запущен успешно!")
    print(f"🤖 Админ ID: {ADMIN_ID}")
    print("🎮 Готов к работе!")
    application.run_polling()

if __name__ == "__main__":
    main()
