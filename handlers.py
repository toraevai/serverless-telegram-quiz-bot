from aiogram import types, F, Router
from aiogram.filters.command import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from database import quiz_data
from service import get_question, new_quiz, get_quiz_index, update_user_info, get_quiz_result

router = Router()


@router.callback_query()
async def bot_answer(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    await callback.bot.edit_message_reply_markup(
        chat_id=user_id,
        message_id=callback.message.message_id,
        reply_markup=None
    )
    current_question_index = await get_quiz_index(user_id)
    right_answers = await get_quiz_result(user_id)
    correct_index = quiz_data[current_question_index]['correct_option']
    opts = quiz_data[current_question_index]['options']
    if callback.data == opts[correct_index]:
        await callback.message.answer("Верно!")
        right_answers += 1
    else:
        await callback.message.answer(
            f"Неправильно. Правильный ответ: {quiz_data[current_question_index]['options'][correct_index]}.")

    current_question_index += 1
    await update_user_info(callback.from_user.id, current_question_index, right_answers)

    if current_question_index < len(quiz_data):
        await get_question(callback.message, callback.from_user.id)
    else:
        right_answers = await get_quiz_result(callback.from_user.id)
        await callback.message.answer("Это был последний вопрос. Квиз завершен!")
        await callback.message.answer(f"Вы ответили правильно на {right_answers} из {len(quiz_data)} вопросов.")


# Хэндлер на команду /start
@router.message(Command("start"))
async def cmd_start(message: types.Message):
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="Начать игру"))
    await message.answer_photo("https://storage.yandexcloud.net/quiz-bot-data-storage/quiz_cover.png")
    await message.answer("Добро пожаловать в квиз!", reply_markup=builder.as_markup(resize_keyboard=True))


# Хэндлер на команду /quiz
@router.message(F.text == "Начать игру")
@router.message(Command("quiz"))
async def cmd_quiz(message: types.Message):
    await message.answer(f"Давайте начнем квиз!")
    await new_quiz(message)
