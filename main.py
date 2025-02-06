import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram import F
from sqlite_database import (update_quiz_index, get_quiz_index, create_table, get_statistic, update_stat, db_edit_table,
                             update_zero, get_all_user_ids)
from quiz import quiz_data

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)

# Замените "YOUR_BOT_TOKEN" на токен, который вы получили от BotFather
API_TOKEN = '7890008278:AAHZeZjXozfuL0pbA5fGblLR7S_0aFMJpo4'

# Объект бота
bot = Bot(token=API_TOKEN)
# Диспетчер
dp = Dispatcher()

async def get_question(message: types.Message, user_id):
    current_question_index = await get_quiz_index(user_id)
    question_data = quiz_data[current_question_index]

    question_text = question_data['question']
    options = question_data['options']
    builder = InlineKeyboardBuilder()
    for option in options:
        builder.add(types.InlineKeyboardButton(text=option, callback_data=f"answer_{option}"))

    builder.adjust(1)
    await message.answer(question_text, reply_markup=builder.as_markup())


# Хэндлер на команду /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="Начать игру"))
    builder.add(types.KeyboardButton(text="Статистика"))
    await message.answer("Добро пожаловать в квиз(Сделано для обучения)!\n\n"
                         "Есть такие команды как: \n"
                         "/quiz - для того, что бы начать квиз\n"
                         "/statistic - для того, что бы посмотреть статистику\n\n"
                         "Для большего удобства сделаны кнопки😉", reply_markup=builder.as_markup(resize_keyboard=True))

@dp.message(F.text=="Начать игру")
@dp.message(Command("quiz"))
async def cmd_quiz(message: types.Message):
    await message.answer(f"Давайте начнем квиз!")
    await db_edit_table(user_id=message.from_user.id, index=0, stat=0)
    await new_quiz(message)

async def new_quiz(message):
    user_id = message.from_user.id
    await update_zero(user_id=user_id, index=0, stat=0)
    await get_question(message, user_id)

@dp.callback_query(F.data.startswith("answer_"))
async def answer(callback: types.CallbackQuery):
    # Получаем текст кнопки, на которую нажал пользователь
    user_answer = callback.data.split("_", 1)[1]  # Получаем текст после "answer_"

    # Получаем индекс текущего вопроса
    current_question_index = await get_quiz_index(callback.from_user.id)

    # Получаем правильный ответ из данных вопроса
    correct_option = quiz_data[current_question_index]['correct_option']
    correct_answer = quiz_data[current_question_index]['options'][correct_option]

    # Проверяем, правильный ли ответ
    if user_answer == correct_answer:
        await callback.message.answer("Верно!")
        statist = await get_statistic(callback.from_user.id)
        print(type(statist))
        new_statistic = int(statist) + 1
        print(new_statistic)
        await update_stat(callback.from_user.id, int(new_statistic))
    else:
        await callback.message.answer(f"Неправильно. Правильный ответ: {correct_answer}")

    await callback.message.answer(f"Ваш ответ: {user_answer}")

    # Удаляем кнопки
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )

    # Обновляем индекс текущего вопроса
    current_question_index += 1
    await update_quiz_index(callback.from_user.id, current_question_index)

    # Задаем следующий вопрос или завершаем квиз
    if current_question_index < len(quiz_data):
        await get_question(callback.message, callback.from_user.id)
    else:
        await callback.message.answer("Это был последний вопрос. Квиз завершен!")




@dp.message(F.text == "Статистика")
@dp.message(Command("statistic"))
async def statistic(message):
    statist = await get_statistic(message.from_user.id)
    my_id = message.from_user.id
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="Начать игру"))
    builder.add(types.KeyboardButton(text="Статистика"))
    user_ids = await get_all_user_ids()
    print(f"Все user_id в базе данных: {user_ids}")
    await message.answer(f"Ваш рекорд: {statist}", reply_markup=builder.as_markup(resize_keyboard=True))
    for i in user_ids:
        if i != my_id:
            await bot.send_message(chat_id=message.from_user.id,
                                   text=f"ID: {i} / Рекорд: - {await get_statistic(i)}")




# Запуск процесса поллинга новых апдейтов
async def main():

    # Запускаем создание таблицы базы данных
    await create_table()

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
