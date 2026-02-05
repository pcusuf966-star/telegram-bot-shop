import os
import logging
import random
import string
import json
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
SELECTING_PAYMENT, UPLOAD_RECEIPT, WAITING_RATING, WAITING_FEEDBACK = range(4)

# База данных ключей (добавлены ВСЕ ваши ключи)
KEYS_DATABASE = {
    "Zolo 1 день": [
        "ZOLO-1D-k8Lp9nQ2mFvA", "ZOLO-1D-j3Rw7sY1bNcX", "ZOLO-1D-p5Tq2zU8dKgH",
        "ZOLO-1D-m9Xv4rS6lJfP", "ZOLO-1D-h7Fd1cV3nMbZ", "ZOLO-1D-s2Wp5yQ9tRxK",
        "ZOLO-1D-g4Nl8jB6vCzD", "ZOLO-1D-r6Zt3mP7wAsE", "ZOLO-1D-b1Kq9cX2hFyL",
        "ZOLO-1D-t8Gv5nR4jMpS", "ZOLO-1D-y3Hs7wQ1kDfT", "ZOLO-1D-q9Pm2lB8cVzR",
        "ZOLO-1D-v5Cr4sN3tJxW", "ZOLO-1D-n1Bd6jL7pFkG", "ZOLO-1D-d7Xw9mZ2qHrT",
        "ZOLO-1D-l2Fv5sR8nCyK", "ZOLO-1D-f8Tp3zQ6bJxM", "ZOLO-1D-w4Nc1gV9kLhD",
        "ZOLO-1D-j6Ss7rY2mPdQ", "ZOLO-1D-p3Rv8lB5tKfX", "ZOLO-1D-m1Zq4wC9jHsN",
        "ZOLO-1D-h9Gt2nV7rFpL", "ZOLO-1D-s5Dc8xQ3bMkY", "ZOLO-1D-g7Xf1jR6wTzB",
        "ZOLO-1D-r2Lp9sY4qHvN", "ZOLO-1D-b4Nw3mK8dJfT", "ZOLO-1D-t6Fv7zQ1cRxP",
        "ZOLO-1D-y8Mp2rB5sKgH", "ZOLO-1D-q1Ts9lV3nDxW", "ZOLO-1D-v3Jc4wZ7hFyL",
        "ZOLO-1D-n5Rd8sQ2bGtM", "ZOLO-1D-d9Xq1mP6jKvC", "ZOLO-1D-l7Fs3nY4tHwB",
        "ZOLO-1D-f2Pv5zR8cMxL", "ZOLO-1D-w4Tl9jB1qNfK", "ZOLO-1D-j6Hc8sY3rDpX",
        "ZOLO-1D-p1Nw2mQ7bFvZ", "ZOLO-1D-m3Rq5lV9tJsG", "ZOLO-1D-h8Xd4sB2kCzP",
        "ZOLO-1D-s5Fv1nR6wMyT", "ZOLO-1D-g9Tp7zQ4jLhK", "ZOLO-1D-r2Bc3mY8sNfX",
        "ZOLO-1D-b4Mq6lV1dKwR", "ZOLO-1D-t6Js9sQ3rHxP", "ZOLO-1D-y8Pv2nZ5cFyL",
        "ZOLO-1D-q1Xw4mB7tGdK", "ZOLO-1D-v3Tl8jR9sNfH", "ZOLO-1D-n5Dc1zQ2bMvP",
        "ZOLO-1D-d7Fq6sY4rKxW", "ZOLO-1D-l9Hv3nB8jTpZ", "ZOLO-1D-f2Rw5mQ1cFsL",
        "ZOLO-1D-w4Np8lV7tJxG", "ZOLO-1D-j6Xs9sB3qDfK", "ZOLO-1D-p1Tc2zR5bMvY",
        "ZOLO-1D-m3Fq4nQ8wHpL", "ZOLO-1D-h8Jv7lB1sKxT", "ZOLO-1D-s5Pd3zR6cNfW",
        "ZOLO-1D-g9Xw2mY4tGqK", "ZOLO-1D-r2Bs8lV1jHxP", "ZOLO-1D-b4Tq5nQ7dFvZ",
        "ZOLO-1D-t6Mc3sR9wJpL", "ZOLO-1D-y8Nv1zB2cKxH", "ZOLO-1D-q1Fw4mQ5sGdT",
        "ZOLO-1D-v3Ps7lR8jHxZ", "ZOLO-1D-n5Xc2nB1tDqK", "ZOLO-1D-d7Tv6zQ4rMfW",
        "ZOLO-1D-l9Bw3sY8cJpL", "ZOLO-1D-f2Hs5mQ1nFvX", "ZOLO-1D-w4Rq8lB7tDzK",
        "ZOLO-1D-j6Nv1sR3wJpY", "ZOLO-1D-p1Xc4zQ5bMfT", "ZOLO-1D-m3Fs2nB8rKqL",
        "ZOLO-1D-h8Tv7lV1jHxP", "ZOLO-1D-s5Pw3sR6cNfZ", "ZOLO-1D-g9Bq2mY4tDxK",
        "ZOLO-1D-r2Mc8lV1sJpW", "ZOLO-1D-b4Xv5nQ7rFzT", "ZOLO-1D-t6Ts3sB9wHqL",
        "ZOLO-1D-y8Nw1zR2cKxP", "ZOLO-1D-q1Fc4mQ5jDvZ", "ZOLO-1D-v3Ps6lB8tHxK",
        "ZOLO-1D-n5Xv2sR1rMqT", "ZOLO-1D-d7Tw4zQ9cJpL", "ZOLO-1D-l9Bc3nB6sFvX",
        "ZOLO-1D-f2Hs7mQ1tDzK", "ZOLO-1D-w4Rq5lV8jNpY", "ZOLO-1D-j6Nv2sR3wXfT",
        "ZOLO-1D-p1Tc8zQ5bMqL", "ZOLO-1D-m3Fs4nB7rHxP", "ZOLO-1D-h8Pv1lV9jKwZ",
        "ZOLO-1D-s5Xw6sR2cNfT", "ZOLO-1D-g9Bq3mY4tDvL", "ZOLO-1D-r2Mc7lV1sJpX",
        "ZOLO-1D-b4Tv5nQ8rFzK", "ZOLO-1D-t6Ns2sB9wHqP", "ZOLO-1D-y8Fw1zR3cKxL",
        "ZOLO-1D-q1Ps4mQ6jDvT", "ZOLO-1D-v3Xc7lB8tHxZ", "ZOLO-1D-n5Tv2sR1rMqK",
        "ZOLO-1D-d7Bw4zQ9cJpL"
    ],
    "Zolo 3 дня": [
        "ZOLO-3D-7k4Mp9R2sT5V", "ZOLO-3D-X3yZ8cN1jL6p", "ZOLO-3D-H9dM2rS5tQ8w",
        "ZOLO-3D-F6nJ7gV1zC4x", "ZOLO-3D-T3pB8kD2mR5s", "ZOLO-3D-L9qM4nR7tS2w",
        "ZOLO-3D-P2jH6kD9mF4r", "ZOLO-3D-W8sK3bV5mQ7z", "ZOLO-3D-E4tN9pB2mS6v",
        "ZOLO-3D-R1dF7kM3pQ9s", "ZOLO-3D-C5mP8jB3nV6s", "ZOLO-3D-K2rS7dF4mP9n",
        "ZOLO-3D-N8vC3kM5pR7s", "ZOLO-3D-S4mP9jB2nV5s", "ZOLO-3D-V3qM8nB1pS6r",
        "ZOLO-3D-Y7tP4jN2mV9s", "ZOLO-3D-Z6rB3kM8pS2n", "ZOLO-3D-Q9mN4pB7sV3k",
        "ZOLO-3D-J2sV8kP3nB6m", "ZOLO-3D-D4nK7pB2mV8s", "ZOLO-3D-U1pN6kB9mS4r",
        "ZOLO-3D-I5mB8kS3pN9r", "ZOLO-3D-O3rV9kP2nS6m", "ZOLO-3D-B7nK4pS1mV8r",
        "ZOLO-3D-M2pN8kS5rV3m", "ZOLO-3D-G9rB3kP6nS2m", "ZOLO-3D-W5nV8kP2rS9m",
        "ZOLO-3D-E1mB7kS4pN3r", "ZOLO-3D-R8pV3kS6nB2m", "ZOLO-3D-T4nB9kS2pV7m",
        "ZOLO-3D-Y6rS8kP3nV2m", "ZOLO-3D-U9mP4kS7nB3r", "ZOLO-3D-I2rB6kP9nS4m",
        "ZOLO-3D-O5nV7kP1rS3m", "ZOLO-3D-B8mS4kP6nV2r", "ZOLO-3D-M3rV5kP8nS1m",
        "ZOLO-3D-G7nB2kP4rS9m", "ZOLO-3D-W2mP8kS3nB6r", "ZOLO-3D-E9rV4kP2nS7m",
        "ZOLO-3D-R5nB1kP8rS3m", "ZOLO-3D-T7mS9kP4nV2r", "ZOLO-3D-Y3rB8kP6nS1m",
        "ZOLO-3D-U6nV9kP2rS4m", "ZOLO-3D-I8mB3kP7nS2r", "ZOLO-3D-O1rS5kP9nV4m",
        "ZOLO-3D-B4nP8kS2rV3m", "ZOLO-3D-M9rV2kP5nS1m", "ZOLO-3D-G5mS7kP3nB4r",
        "ZOLO-3D-W3nB6kP8rS2m", "ZOLO-3D-E7rP4kS9nV1m"
    ],
    "Zolo 7 дней": [
        "ZOLO-7D-c8Lp2nQ5mFvR", "ZOLO-7D-a3Rw9sY1bNcT", "ZOLO-7D-k5Tq4zU8dKgS",
        "ZOLO-7D-p9Xv1rS6lJfM", "ZOLO-7D-h7Fd3cV2nMbW", "ZOLO-7D-s2Wp6yQ9tRxZ",
        "ZOLO-7D-g4Nl5jB6vCzX", "ZOLO-7D-r6Zt8mP7wAsL", "ZOLO-7D-b1Kq3cX2hFyP",
        "ZOLO-7D-t8Gv7nR4jMpK", "ZOLO-7D-y3Hs2wQ1kDfV", "ZOLO-7D-q9Pm8lB5cVzR",
        "ZOLO-7D-v5Cr1sN3tJxW", "ZOLO-7D-n1Bd9jL7pFkG", "ZOLO-7D-d7Xw4mZ2qHrT",
        "ZOLO-7D-l2Fv8sR6nCyK", "ZOLO-7D-f8Tp3zQ1bJxM", "ZOLO-7D-w4Nc6gV9kLhD",
        "ZOLO-7D-j6Ss2rY5mPdQ", "ZOLO-7D-p3Rv7lB8tKfX", "ZOLO-7D-m1Zq9wC4jHsN",
        "ZOLO-7D-h9Gt5nV2rFpL", "ZOLO-7D-s5Dc3xQ8bMkY", "ZOLO-7D-g7Xf4jR1wTzB",
        "ZOLO-7D-r2Lp6sY9qHvN", "ZOLO-7D-b4Nw8mK3dJfT", "ZOLO-7D-t6Fv2zQ7cRxP",
        "ZOLO-7D-y8Mp9rB1sKgH", "ZOLO-7D-q1Ts5lV4nDxW", "ZOLO-7D-v3Jc7wZ2hFyL",
        "ZOLO-7D-n5Rd1sQ9bGtM", "ZOLO-7D-d9Xq3mP6jKvC", "ZOLO-7D-l7Fs8nY5tHwB",
        "ZOLO-7D-f2Pv4zR3cMxL", "ZOLO-7D-w4Tl6jB1qNfK", "ZOLO-7D-j6Hc9sY2rDpX",
        "ZOLO-7D-p1Nw5mQ7bFvZ", "ZOLO-7D-m3Rq2lV8tJsG", "ZOLO-7D-h8Xd7sB1kCzP",
        "ZOLO-7D-s5Fv4nR3wMyT", "ZOLO-7D-g9Tp1zQ6jLhK", "ZOLO-7D-r2Bc8mY5sNfX",
        "ZOLO-7D-b4Mq3lV9dKwR", "ZOLO-7D-t6Js2sQ7rHxP", "ZOLO-7D-y8Pv5nZ1cFyL",
        "ZOLO-7D-q1Xw7mB4tGdK", "ZOLO-7D-v3Tl9jR2sNfH", "ZOLO-7D-n5Dc4zQ8bMvP",
        "ZOLO-7D-d7Fq1sY3rKxW", "ZOLO-7D-l9Hv6nB5jTpZ", "ZOLO-7D-f2Rw3mQ9cFsL",
        "ZOLO-7D-w4Np7lV2tJxG", "ZOLO-7D-j6Xs4sB8qDfK", "ZOLO-7D-p1Tc5zR3bMvY",
        "ZOLO-7D-m3Fq9nQ1wHpL", "ZOLO-7D-h8Jv2lB7sKxT", "ZOLO-7D-s5Pd6zR4cNfW",
        "ZOLO-7D-g9Xw8mY3tGqK", "ZOLO-7D-r2Bs1lV5jHxP", "ZOLO-7D-b4Tq7nQ2dFvZ",
        "ZOLO-7D-t6Mc4sR8wJpL", "ZOLO-7D-y8Nv3zB1cKxH", "ZOLO-7D-q1Fw5mQ9sGdT",
        "ZOLO-7D-v3Ps2lR6jHxZ", "ZOLO-7D-n5Xc8nB4tDqK", "ZOLO-7D-d7Tv1zQ3rMfW",
        "ZOLO-7D-l9Bw7sY2cJpL", "ZOLO-7D-f2Hs4mQ8nFvX", "ZOLO-7D-w4Rq6lB3tDzK",
        "ZOLO-7D-j6Nv9sR1wJpY", "ZOLO-7D-p1Xc2zQ7bMfT", "ZOLO-7D-m3Fs5nB4rKqL",
        "ZOLO-7D-h8Tv3lV9jHxP", "ZOLO-7D-s5Pw7sR2cNfZ", "ZOLO-7D-g9Bq1mY6tDxK",
        "ZOLO-7D-r2Mc8lV4sJpW", "ZOLO-7D-b4Xv6nQ3rFzT", "ZOLO-7D-t6Ts9sB1wHqL",
        "ZOLO-7D-y8Nw5zR7cKxP", "ZOLO-7D-q1Fc2mQ8jDvZ", "ZOLO-7D-v3Ps4lB3tHxK",
        "ZOLO-7D-n5Xv7sR9rMqT", "ZOLO-7D-d7Tw3zQ2cJpL", "ZOLO-7D-l9Bc6nB5sFvX",
        "ZOLO-7D-f2Hs1mQ4tDzK", "ZOLO-7D-w4Rq8lV7jNpY", "ZOLO-7D-j6Nv5sR2wXfT",
        "ZOLO-7D-p1Tc3zQ9bMqL", "ZOLO-7D-m3Fs6nB8rHxP", "ZOLO-7D-h8Pv4lV1jKwZ",
        "ZOLO-7D-s5Xw9sR3cNfT", "ZOLO-7D-g9Bq2mY7tDvL", "ZOLO-7D-r2Mc1lV5sJpX",
        "ZOLO-7D-b4Tv8nQ6rFzK", "ZOLO-7D-t6Ns3sB2wHqP", "ZOLO-7D-y8Fw7zR4cKxL",
        "ZOLO-7D-q1Ps9mQ3jDvT", "ZOLO-7D-v3Xc5lB1tHxZ", "ZOLO-7D-n5Tv2sR8rMqK",
        "ZOLO-7D-d7Bw4zQ6cJpL"
    ],
    "Zolo 30 дней": [
        "ZOLO-30D-w8Lp3nQ2mFvS", "ZOLO-30D-e3Rw5sY1bNcV", "ZOLO-30D-r5Tq7zU8dKgM",
        "ZOLO-30D-t9Xv2rS6lJfP", "ZOLO-30D-u7Fd4cV3nMbW", "ZOLO-30D-i2Wp8yQ9tRxZ",
        "ZOLO-30D-o4Nl1jB6vCzX", "ZOLO-30D-a6Zt9mP7wAsL", "ZOLO-30D-s1Kq5cX2hFyP",
        "ZOLO-30D-d8Gv3nR4jMpK", "ZOLO-30D-f3Hs6wQ1kDfV", "ZOLO-30D-g9Pm4lB5cVzR",
        "ZOLO-30D-h5Cr8sN3tJxW", "ZOLO-30D-j1Bd2jL7pFkG", "ZOLO-30D-k7Xw9mZ2qHrT",
        "ZOLO-30D-l2Fv5sR6nCyK", "ZOLO-30D-z8Tp1zQ3bJxM", "ZOLO-30D-x4Nc7gV9kLhD",
        "ZOLO-30D-c6Ss3rY5mPdQ", "ZOLO-30D-v3Rv2lB8tKfX", "ZOLO-30D-b1Zq6wC4jHsN",
        "ZOLO-30D-n9Gt8nV2rFpL", "ZOLO-30D-m5Dc1xQ7bMkY", "ZOLO-30D-q7Xf3jR1wTzB",
        "ZOLO-30D-p2Lp4sY9qHvN", "ZOLO-30D-o4Nw7mK3dJfT", "ZOLO-30D-i6Fv9zQ2cRxP",
        "ZOLO-30D-u8Mp5rB1sKgH", "ZOLO-30D-y1Ts3lV4nDxW", "ZOLO-30D-t3Jc2wZ7hFyL",
        "ZOLO-30D-r5Rd6sQ9bGtM", "ZOLO-30D-e9Xq4mP6jKvC", "ZOLO-30D-w7Fs1nY5tHwB",
        "ZOLO-30D-q2Pv8zR3cMxL", "ZOLO-30D-a4Tl3jB1qNfK", "ZOLO-30D-s6Hc5sY2rDpX",
        "ZOLO-30D-d1Nw9mQ7bFvZ", "ZOLO-30D-f3Rq2lV8tJsG", "ZOLO-30D-g8Xd4sB1kCzP",
        "ZOLO-30D-h5Fv7nR3wMyT", "ZOLO-30D-j9Tp1zQ6jLhK", "ZOLO-30D-k2Bc3mY5sNfX",
        "ZOLO-30D-l4Mq8lV9dKwR", "ZOLO-30D-z6Js5sQ7rHxP", "ZOLO-30D-x8Pv2nZ1cFyL",
        "ZOLO-30D-c1Xw6mB4tGdK", "ZOLO-30D-v3Tl4jR2sNfH", "ZOLO-30D-b5Dc9zQ8bMvP",
        "ZOLO-30D-n7Fq2sY3rKxW", "ZOLO-30D-m9Hv1nB5jTpZ", "ZOLO-30D-q2Rw7mQ9cFsL",
        "ZOLO-30D-p4Np3lV2tJxG", "ZOLO-30D-o6Xs8sB4qDfK", "ZOLO-30D-i1Tc2zR3bMvY",
        "ZOLO-30D-u3Fq5nQ1wHpL", "ZOLO-30D-y8Jv9lB7sKxT", "ZOLO-30D-t5Pd3zR4cNfW",
        "ZOLO-30D-r9Xw7mY3tGqK", "ZOLO-30D-e2Bs4lV5jHxP", "ZOLO-30D-w4Tq1nQ2dFvZ",
        "ZOLO-30D-q6Mc8sR3wJpL", "ZOLO-30D-a8Nv2zB1cKxH", "ZOLO-30D-s1Fw5mQ9sGdT",
        "ZOLO-30D-d3Ps7lR6jHxZ", "ZOLO-30D-f5Xc3nB4tDqK", "ZOLO-30D-g7Tv6zQ3rMfW",
        "ZOLO-30D-h9Bw2sY2cJpL", "ZOLO-30D-j2Hs8mQ4nFvX", "ZOLO-30D-k4Rq1lB3tDzK",
        "ZOLO-30D-l6Nv5sR1wJpY", "ZOLO-30D-z1Xc9zQ7bMfT", "ZOLO-30D-x3Fs4nB8rKqL",
        "ZOLO-30D-c8Tv2lV9jHxP", "ZOLO-30D-v5Pw6sR2cNfZ", "ZOLO-30D-b9Bq3mY6tDxK",
        "ZOLO-30D-n2Mc7lV4sJpW", "ZOLO-30D-m4Xv5nQ3rFzT", "ZOLO-30D-q6Ts8sB1wHqL",
        "ZOLO-30D-p8Nw4zR7cKxP", "ZOLO-30D-o1Fc2mQ8jDvZ", "ZOLO-30D-i3Ps9lB3tHxK",
        "ZOLO-30D-u5Xv6sR9rMqT", "ZOLO-30D-y7Tw1zQ2cJpL", "ZOLO-30D-t9Bc5nB5sFvX",
        "ZOLO-30D-r2Hs3mQ4tDzK", "ZOLO-30D-e4Rq7lV7jNpY", "ZOLO-30D-w6Nv2sR5wXfT",
        "ZOLO-30D-q1Tc4zQ9bMqL", "ZOLO-30D-a3Fs8nB6rHxP", "ZOLO-30D-s8Pv1lV4jKwZ",
        "ZOLO-30D-d5Xw7sR3cNfT", "ZOLO-30D-f9Bq2mY8tDvL", "ZOLO-30D-g2Mc6lV5sJpX",
        "ZOLO-30D-h4Tv3nQ9rFzK", "ZOLO-30D-j6Ns5sB2wHqP", "ZOLO-30D-k8Fw1zR4cKxL",
        "ZOLO-30D-l1Ps7mQ3jDvT", "ZOLO-30D-z3Xc4lB1tHxZ", "ZOLO-30D-x5Tv9sR8rMqK",
        "ZOLO-30D-c7Bw2zQ6cJpL"
    ],
    "Zolo 60 дней": [
        "ZOLO-60D-p5Lk9jQ3mFvR", "ZOLO-60D-w8Xs2tY6bNcV", "ZOLO-60D-r3Tq7zU1dKgM",
        "ZOLO-60D-t4Xv9rS2lJfP", "ZOLO-60D-u6Fd1cV5nMbW", "ZOLO-60D-i2Wp8yQ4tRxZ",
        "ZOLO-60D-o9Nl3jB7vCzX", "ZOLO-60D-a5Zt6mP2wAsL", "ZOLO-60D-s7Kq4cX1hFyP",
        "ZOLO-60D-d1Gv8nR3jMpK", "ZOLO-60D-f4Hs5wQ9kDfV", "ZOLO-60D-g2Pm6lB8cVzR",
        "ZOLO-60D-h8Cr3sN1tJxW", "ZOLO-60D-j9Bd7jL4pFkG", "ZOLO-60D-k3Xw5mZ6qHrT",
        "ZOLO-60D-l1Fv2sR8nCyK", "ZOLO-60D-z7Tp4zQ5bJxM", "ZOLO-60D-x2Nc8gV3kLhD",
        "ZOLO-60D-c6Ss1rY9mPdQ", "ZOLO-60D-v9Rv5lB2tKfX", "ZOLO-60D-b4Zq3wC7jHsN",
        "ZOLO-60D-n8Gt2nV5rFpL", "ZOLO-60D-m1Dc9xQ4bMkY", "ZOLO-60D-q5Xf7jR2wTzB",
        "ZOLO-60D-p3Lp6sY1qHvN", "ZOLO-60D-o2Nw4mK8dJfT", "ZOLO-60D-i7Fv9zQ3cRxP",
        "ZOLO-60D-u1Mp5rB6sKgH", "ZOLO-60D-y8Ts2lV7nDxW", "ZOLO-60D-t6Jc4wZ3hFyL",
        "ZOLO-60D-r9Rd1sQ5bGtM", "ZOLO-60D-e5Xq8mP2jKvC", "ZOLO-60D-w3Fs6nY7tHwB",
        "ZOLO-60D-q4Pv2zR9cMxL", "ZOLO-60D-a1Tl7jB5qNfK", "ZOLO-60D-s8Hc3sY4rDpX",
        "ZOLO-60D-d6Nw9mQ1bFvZ", "ZOLO-60D-f2Rq5lV8tJsG", "ZOLO-60D-g7Xd4sB3kCzP",
        "ZOLO-60D-h3Fv1nR6wMyT", "ZOLO-60D-j5Tp8zQ2jLhK", "ZOLO-60D-k9Bc6mY7sNfX",
        "ZOLO-60D-l4Mq2lV1dKwR", "ZOLO-60D-z8Js3sQ6rHxP", "ZOLO-60D-x5Pv7nZ9cFyL",
        "ZOLO-60D-c2Xw1mB4tGdK", "ZOLO-60D-v4Tl9jR8sNfH", "ZOLO-60D-b7Dc5zQ3bMvP",
        "ZOLO-60D-n3Fq2sY1rKxW", "ZOLO-60D-m6Hv8nB5jTpZ", "ZOLO-60D-q9Rw4mQ2cFsL",
        "ZOLO-60D-p1Np7lV3tJxG", "ZOLO-60D-o5Xs9sB8qDfK", "ZOLO-60D-i3Tc6zR4bMvY",
        "ZOLO-60D-u8Fq2nQ7wHpL", "ZOLO-60D-y4Jv1lB9sKxT", "ZOLO-60D-t7Pd5zR3cNfW",
        "ZOLO-60D-r2Xw8mY6tGqK", "ZOLO-60D-e9Bs3lV5jHxP", "ZOLO-60D-w6Tq4nQ1dFvZ",
        "ZOLO-60D-q5Mc7sR2wJpL", "ZOLO-60D-a3Nv9zB8cKxH", "ZOLO-60D-s1Fw6mQ4sGdT",
        "ZOLO-60D-d4Ps2lR7jHxZ", "ZOLO-60D-f8Xc5nB3tDqK", "ZOLO-60D-g6Tv1zQ9rMfW",
        "ZOLO-60D-h2Bw7sY4cJpL", "ZOLO-60D-j9Hs3mQ5nFvX", "ZOLO-60D-k5Rq8lB1tDzK",
        "ZOLO-60D-l7Nv4sR2wJpY", "ZOLO-60D-z3Xc9zQ6bMfT", "ZOLO-60D-x2Fs5nB7rKqL",
        "ZOLO-60D-c8Tv3lV4jHxP", "ZOLO-60D-v1Pw6sR9cNfZ", "ZOLO-60D-b4Bq2mY8tDxK",
        "ZOLO-60D-n7Mc5lV1sJpW", "ZOLO-60D-m9Xv8nQ3rFzT", "ZOLO-60D-q6Ts2sB5wHqL",
        "ZOLO-60D-p8Nw1zR7cKxP", "ZOLO-60D-o2Fc4mQ9jDvZ", "ZOLO-60D-i5Ps3lB6tHxK",
        "ZOLO-60D-u7Xv9sR4rMqT", "ZOLO-60D-y1Tw6zQ2cJpL", "ZOLO-60D-t3Bc8nB5sFvX",
        "ZOLO-60D-r4Hs2mQ7tDzK", "ZOLO-60D-e6Rq1lV9jNpY", "ZOLO-60D-w9Nv5sR3wXfT",
        "ZOLO-60D-q7Tc4zQ8bMqL", "ZOLO-60D-a2Fs6nB1rHxP", "ZOLO-60D-s8Pv3lV5jKwZ",
        "ZOLO-60D-d5Xw9sR2cNfT", "ZOLO-60D-f1Bq7mY4tDvL", "ZOLO-60D-g3Mc2lV6sJpX",
        "ZOLO-60D-h6Tv4nQ8rFzK", "ZOLO-60D-j8Ns1sB3wHqP", "ZOLO-60D-k2Fw5zR9cKxL",
        "ZOLO-60D-l4Ps7mQ6jDvT", "ZOLO-60D-z9Xc3lB2tHxZ", "ZOLO-60D-x5Tv8sR1rMqK",
        "ZOLO-60D-c7Bw2zQ4cJpL"
    ]
}

# Использованные ключи
used_keys = {product: [] for product in KEYS_DATABASE.keys()}

# Базы данных
user_data = {}
orders = {}
referral_codes = {}
feedbacks = []

# Сохранение данных в файл
def save_data():
    data = {
        'user_data': user_data,
        'orders': orders,
        'referral_codes': referral_codes,
        'used_keys': used_keys,
        'feedbacks': feedbacks
    }
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)

# Загрузка данных из файла
def load_data():
    global user_data, orders, referral_codes, used_keys, feedbacks
    try:
        with open('data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            user_data = data.get('user_data', {})
            orders = data.get('orders', {})
            referral_codes = data.get('referral_codes', {})
            used_keys = data.get('used_keys', {product: [] for product in KEYS_DATABASE.keys()})
            feedbacks = data.get('feedbacks', [])
    except FileNotFoundError:
        pass

# Админ команды
ADMIN_COMMANDS = {
    "/admin": "Панель администратора",
    "/stats": "Статистика пользователей",
    "/broadcast": "Сделать рассылку всем пользователям",
    "/users": "Список всех пользователей",
    "/orders": "Просмотр всех заказов",
    "/keys": "Проверка остатков ключей"
}

def generate_order_id() -> str:
    return ''.join(random.choices(string.digits, k=6))

def generate_referral_code(user_id: int) -> str:
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    referral_codes[code] = user_id
    save_data()
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
            save_data()
        else:
            keys = [f"ERROR: Недостаточно ключей для {product_name}"]
    return keys

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Админ панель"""
    user_id = update.effective_user.id
    
    if user_id != ADMIN_ID:
        await update.message.reply_text("⛔ У вас нет доступа к этой команде.")
        return
    
    text = "👑 АДМИН ПАНЕЛЬ\n\n"
    text += "Доступные команды:\n"
    for cmd, desc in ADMIN_COMMANDS.items():
        text += f"{cmd} - {desc}\n"
    
    keyboard = [
        [InlineKeyboardButton("📊 Статистика", callback_data="admin_stats")],
        [InlineKeyboardButton("📢 Рассылка", callback_data="admin_broadcast")],
        [InlineKeyboardButton("👥 Пользователи", callback_data="admin_users")],
        [InlineKeyboardButton("📦 Заказы", callback_data="admin_orders")],
        [InlineKeyboardButton("🔑 Ключи", callback_data="admin_keys")],
        [InlineKeyboardButton("⭐ Отзывы", callback_data="admin_feedbacks")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(text, reply_markup=reply_markup)

async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Статистика"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    if user_id != ADMIN_ID:
        await query.edit_message_text("⛔ У вас нет доступа.")
        return
    
    total_users = len(user_data)
    total_orders = len(orders)
    completed_orders = sum(1 for o in orders.values() if o.get('status') == 'completed')
    total_revenue = sum(o.get('total_price', 0) for o in orders.values() if o.get('status') == 'completed')
    
    # Ключи
    keys_stats = {}
    for product, keys in KEYS_DATABASE.items():
        used = len(used_keys.get(product, []))
        available = len(keys) - used
        keys_stats[product] = {
            'total': len(keys),
            'used': used,
            'available': available,
            'percentage': (used / len(keys) * 100) if len(keys) > 0 else 0
        }
    
    text = f"📊 СТАТИСТИКА БОТА\n\n"
    text += f"👥 Пользователей: {total_users}\n"
    text += f"📦 Всего заказов: {total_orders}\n"
    text += f"✅ Завершено заказов: {completed_orders}\n"
    text += f"💰 Общая выручка: {total_revenue} ₽\n\n"
    text += f"🔑 Статистика ключей:\n"
    
    for product, stats in keys_stats.items():
        text += f"└ {product}: {stats['available']}/{stats['total']} ({stats['percentage']:.1f}% использовано)\n"
    
    await query.edit_message_text(text)

async def admin_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начать рассылку"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    if user_id != ADMIN_ID:
        await query.edit_message_text("⛔ У вас нет доступа.")
        return
    
    context.user_data["broadcast_mode"] = True
    await query.edit_message_text("✍️ Отправьте сообщение для рассылки всем пользователям:")
    return WAITING_RATING  # Переиспользуем состояние для ожидания сообщения

async def send_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправить рассылку"""
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        return
    
    message = update.message.text
    successful = 0
    failed = 0
    
    await update.message.reply_text(f"📢 Начинаю рассылку для {len(user_data)} пользователей...")
    
    for uid in user_data.keys():
        try:
            await context.bot.send_message(
                chat_id=uid,
                text=f"📢 ОБЪЯВЛЕНИЕ ОТ АДМИНИСТРАЦИИ:\n\n{message}"
            )
            successful += 1
        except:
            failed += 1
    
    del context.user_data["broadcast_mode"]
    
    await update.message.reply_text(
        f"✅ Рассылка завершена!\n"
        f"✓ Успешно: {successful}\n"
        f"✗ Не удалось: {failed}"
    )
    return ConversationHandler.END

async def admin_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Список пользователей"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    if user_id != ADMIN_ID:
        await query.edit_message_text("⛔ У вас нет доступа.")
        return
    
    if not user_data:
        await query.edit_message_text("📭 Пользователей пока нет.")
        return
    
    text = f"👥 ПОЛЬЗОВАТЕЛИ ({len(user_data)}):\n\n"
    for i, (uid, user) in enumerate(list(user_data.items())[:20], 1):
        orders_count = len(user.get('orders', []))
        text += f"{i}. @{user.get('username', 'N/A')} (ID: {uid})\n"
        text += f"   📦 Заказов: {orders_count}\n"
        text += f"   💰 Баланс: {user.get('balance', 0)} ₽\n\n"
    
    if len(user_data) > 20:
        text += f"... и еще {len(user_data) - 20} пользователей\n"
    
    await query.edit_message_text(text)

async def admin_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Все заказы"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    if user_id != ADMIN_ID:
        await query.edit_message_text("⛔ У вас нет доступа.")
        return
    
    if not orders:
        await query.edit_message_text("📭 Заказов пока нет.")
        return
    
    text = f"📦 ВСЕ ЗАКАЗЫ ({len(orders)}):\n\n"
    for order_id, order in list(orders.items())[:10]:
        status_text = {
            'pending': '⏳ Ожидание',
            'waiting_payment': '🔄 Ожидает оплаты',
            'completed': '✅ Завершен',
            'cancelled': '❌ Отменен'
        }.get(order.get('status'), order.get('status', 'N/A'))
        
        text += f"📋 Заказ: #{order_id}\n"
        text += f"🛍️ Товар: {order.get('product', 'N/A')}\n"
        text += f"👤 Пользователь: @{order.get('username', 'N/A')}\n"
        text += f"💰 Сумма: {order.get('total_price', 0)} ₽\n"
        text += f"📊 Статус: {status_text}\n"
        text += f"📅 Дата: {order.get('timestamp', '').strftime('%d.%m.%Y %H:%M') if isinstance(order.get('timestamp'), datetime) else 'N/A'}\n\n"
    
    if len(orders) > 10:
        text += f"... и еще {len(orders) - 10} заказов\n"
    
    await query.edit_message_text(text)

async def admin_keys(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Проверка ключей"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    if user_id != ADMIN_ID:
        await query.edit_message_text("⛔ У вас нет доступа.")
        return
    
    text = "🔑 СТАТУС КЛЮЧЕЙ\n\n"
    for product, keys in KEYS_DATABASE.items():
        used = len(used_keys.get(product, []))
        total = len(keys)
        available = total - used
        percentage = (used / total * 100) if total > 0 else 0
        
        text += f"📦 {product}:\n"
        text += f"   Всего: {total}\n"
        text += f"   Использовано: {used}\n"
        text += f"   Доступно: {available}\n"
        text += f"   Заполненность: {percentage:.1f}%\n\n"
    
    keyboard = [[InlineKeyboardButton("Назад", callback_data="admin_back")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup)

async def admin_feedbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Просмотр отзывов"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    if user_id != ADMIN_ID:
        await query.edit_message_text("⛔ У вас нет доступа.")
        return
    
    if not feedbacks:
        await query.edit_message_text("⭐ Отзывов пока нет.")
        return
    
    text = f"⭐ ОТЗЫВЫ ({len(feedbacks)}):\n\n"
    for i, feedback in enumerate(feedbacks[:10], 1):
        stars = '★' * feedback.get('rating', 0) + '☆' * (5 - feedback.get('rating', 0))
        text += f"{i}. Рейтинг: {stars}\n"
        text += f"   От: @{feedback.get('username', 'N/A')}\n"
        text += f"   Текст: {feedback.get('text', 'Без текста')[:50]}...\n"
        text += f"   Дата: {feedback.get('date', '').strftime('%d.%m.%Y')}\n\n"
    
    if len(feedbacks) > 10:
        text += f"... и еще {len(feedbacks) - 10} отзывов\n"
    
    await query.edit_message_text(text)

async def ask_for_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Запросить отзыв после успешной покупки"""
    keyboard = [
        [
            InlineKeyboardButton("⭐", callback_data="rating_1"),
            InlineKeyboardButton("⭐⭐", callback_data="rating_2"),
            InlineKeyboardButton("⭐⭐⭐", callback_data="rating_3"),
            InlineKeyboardButton("⭐⭐⭐⭐", callback_data="rating_4"),
            InlineKeyboardButton("⭐⭐⭐⭐⭐", callback_data="rating_5"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🌟 Пожалуйста, оцените работу нашего бота:\n"
        "Выберите количество звезд (1-5):",
        reply_markup=reply_markup
    )
    return WAITING_RATING

async def handle_rating(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка выбора рейтинга"""
    query = update.callback_query
    await query.answer()
    
    rating = int(query.data.split("_")[1])
    context.user_data["rating"] = rating
    
    await query.edit_message_text(
        f"⭐ Спасибо за {rating} звезд!\n"
        f"✍️ Теперь напишите ваш отзыв (можно просто нажать отправить без текста):"
    )
    return WAITING_FEEDBACK

async def handle_feedback_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка текста отзыва"""
    user_id = update.effective_user.id
    rating = context.user_data.get("rating", 0)
    feedback_text = update.message.text or "Без текста"
    username = update.effective_user.username or update.effective_user.first_name
    
    # Сохраняем отзыв
    feedback = {
        'user_id': user_id,
        'username': username,
        'rating': rating,
        'text': feedback_text,
        'date': datetime.now()
    }
    feedbacks.append(feedback)
    save_data()
    
    # Уведомляем админа
    stars = '★' * rating + '☆' * (5 - rating)
    admin_text = f"⭐ НОВЫЙ ОТЗЫВ!\n\nРейтинг: {stars}\nОт: @{username}\nТекст: {feedback_text}"
    
    try:
        await context.bot.send_message(chat_id=ADMIN_ID, text=admin_text)
    except:
        pass
    
    await update.message.reply_text("🙏 Спасибо за ваш отзыв! Ваше мнение очень важно для нас!")
    
    # Очищаем данные
    if "rating" in context.user_data:
        del context.user_data["rating"]
    
    return ConversationHandler.END

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    
    # Загружаем данные при старте
    load_data()
    
    if user_id not in user_data:
        user_data[user_id] = {
            "username": user.username or user.first_name,
            "balance": 0.0,
            "referral_code": generate_referral_code(user_id),
            "orders": [],
            "joined": datetime.now()
        }
        save_data()
    
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
            "orders": [],
            "joined": datetime.now()
        }
    user_data[user_id]["orders"].append(order_data)
    save_data()
    
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
            save_data()
        
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
                    
                    save_data()
                    
                    # Запрашиваем отзыв
                    await context.bot.send_message(
                        chat_id=user_id,
                        text="🎉 Спасибо за покупку! Ваши ключи отправлены выше."
                    )
                    await ask_for_feedback(update, context)
                    
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
        save_data()
    
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
        save_data()

async def my_account(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = user_data.get(user_id, {})
    
    text = (
        f"❤️ Имя: {user.get('username', 'N/A')}\n"
        f"🔑 ID: {user_id}\n"
        f"💰 Ваш баланс: {user.get('balance', 0)} ₽\n"
        f"📅 Регистрация: {user.get('joined', 'N/A').strftime('%d.%m.%Y') if isinstance(user.get('joined'), datetime) else 'N/A'}"
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
    
    # Админ команды
    if data == "admin_stats":
        await admin_stats(update, context)
    elif data == "admin_broadcast":
        await admin_broadcast(update, context)
    elif data == "admin_users":
        await admin_users(update, context)
    elif data == "admin_orders":
        await admin_orders(update, context)
    elif data == "admin_keys":
        await admin_keys(update, context)
    elif data == "admin_feedbacks":
        await admin_feedbacks(update, context)
    elif data == "admin_back":
        await admin_panel(update, context)
    
    # Рейтинги
    elif data.startswith("rating_"):
        await handle_rating(update, context)
    
    # Основные команды
    elif data.startswith("confirm_order_"):
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
    # Загружаем данные при запуске
    load_data()
    
    application = Application.builder().token(TOKEN).build()
    
    # Команды
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("admin", admin_panel))
    
    # Conversation Handler для оплаты
    conv_handler_payment = ConversationHandler(
        entry_points=[CallbackQueryHandler(paid, pattern="^paid$")],
        states={
            SELECTING_PAYMENT: [CallbackQueryHandler(paid, pattern="^paid$")],
            UPLOAD_RECEIPT: [
                CallbackQueryHandler(cancel_payment, pattern="^cancel_payment$"),
                MessageHandler(filters.PHOTO, handle_receipt)
            ]
        },
        fallbacks=[]
    )
    application.add_handler(conv_handler_payment)
    
    # Conversation Handler для отзывов
    conv_handler_feedback = ConversationHandler(
        entry_points=[CallbackQueryHandler(handle_rating, pattern="^rating_")],
        states={
            WAITING_RATING: [
                CallbackQueryHandler(handle_rating, pattern="^rating_"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, send_broadcast)
            ],
            WAITING_FEEDBACK: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_feedback_text)
            ]
        },
        fallbacks=[]
    )
    application.add_handler(conv_handler_feedback)
    
    # Обработчики
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_error_handler(error_handler)
    
    print("✅ Бот запущен успешно!")
    print(f"🤖 Админ ID: {ADMIN_ID}")
    print(f"👥 Пользователей в базе: {len(user_data)}")
    print(f"📦 Заказов в базе: {len(orders)}")
    print("🎮 Готов к работе!")
    application.run_polling()

if __name__ == "__main__":
    main()
