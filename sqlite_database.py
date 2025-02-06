import aiosqlite

async def create_table():
    # Создаем соединение с базой данных (если она не существует, она будет создана)
    async with aiosqlite.connect("quiz_bot.db") as db:
        # Создаем таблицу
        await db.execute('''CREATE TABLE IF NOT EXISTS quiz_state (user_id INTEGER PRIMARY KEY, question_index INTEGER, statistic_user INTEGER)''')
        # Сохраняем изменения
        await db.commit()

async def update_stat(user_id: int, stat: int):
    # Создаем соединение с базой данных (если она не существует, она будет создана)
    async with aiosqlite.connect('quiz_bot.db') as db:
        # Вставляем новую запись или заменяем ее, если с данным user_id уже существует
        await db.execute('UPDATE quiz_state SET statistic_user = ? WHERE user_id = ?', (stat, user_id))
        # Сохраняем изменения
        await db.commit()

# async def db_edit_table(user_id: int, index: int, stat: int):
#     async with aiosqlite.connect('quiz_bot.db') as db:
#         user_general = await db.execute(f"""SELECT id FROM quiz_state WHERE user_id = {user_id};""").fetchone()
#         if not await user_general:
#             await db.execute("""INSERT INTO quiz_state (user_id, index, stat)
#                                     VALUES (?, ?, ?);""",
#                        (user_id, index, stat))
#             await db.commit()
#         else:
#             print("Такой пользователь в таблице TABLE_REMINDER существует")

async def db_edit_table(user_id: int, index: int, stat: int):
    async with aiosqlite.connect('quiz_bot.db') as db:
        async with db.execute(f"""SELECT user_id FROM quiz_state WHERE user_id = {user_id};""") as cursor:
            user_general = await cursor.fetchone()

        if user_general is None: # Проверка на None, а не на truthiness await user_general
            await db.execute("""INSERT INTO quiz_state (user_id, question_index, statistic_user) VALUES (?, ?, ?);""", (user_id, index, stat))
            await db.commit()
            print(f"Пользователь {user_id} добавлен в quiz_state.")
        else:
            print(f"Пользователь {user_id} уже существует в quiz_state.")

async def update_zero(user_id, index, stat):
    # Создаем соединение с базой данных (если она не существует, она будет создана)
    async with aiosqlite.connect('quiz_bot.db') as db:
        # Вставляем новую запись или заменяем ее, если с данным user_id уже существует
        await db.execute('UPDATE quiz_state SET question_index = ?, statistic_user = ? WHERE user_id = ?', (index, stat, user_id))
        # Сохраняем изменения
        await db.commit()
async def update_quiz_index(user_id, index):
    # Создаем соединение с базой данных (если она не существует, она будет создана)
    async with aiosqlite.connect('quiz_bot.db') as db:
        # Вставляем новую запись или заменяем ее, если с данным user_id уже существует
        await db.execute('UPDATE quiz_state SET question_index = ? WHERE user_id = ?', (index, user_id))
        # Сохраняем изменения
        await db.commit()


async def get_quiz_index(user_id):
    # Подключаемся к базе данных
    async with aiosqlite.connect('quiz_bot.db') as db:
        # Получаем запись для заданного пользователя
        async with db.execute('SELECT question_index FROM quiz_state WHERE user_id = (?)', (user_id,)) as cursor:
            # Возвращаем результат
            results = await cursor.fetchone()
            if results is not None:
                return results[0]
            else:
                return 0

async def get_statistic(user_id):
    # Подключаемся к базе данных
    async with aiosqlite.connect('quiz_bot.db') as db:
        # Получаем запись для заданного пользователя
        async with db.execute('SELECT statistic_user FROM quiz_state WHERE user_id = (?)', (user_id,)) as cursor:
            # Возвращаем результат
            results = await cursor.fetchone()
            if results is not None:
                return results[0]
            else:
                return 0


# Проверка статистики у всех

async def get_all_user_ids():
    async with aiosqlite.connect('quiz_bot.db') as db:
        async with db.execute("SELECT user_id FROM quiz_state") as cursor:
            user_ids = [row[0] for row in await cursor.fetchall()]
            return user_ids

