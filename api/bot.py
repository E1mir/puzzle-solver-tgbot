import os
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ContentType, FSInputFile
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from .image_processor import solve_puzzle

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

class Form(StatesGroup):
    waiting_for_photo = State()

@dp.message(F.text == '/start')
async def send_welcome(message: Message, state: FSMContext):
    await message.answer("Send me an image of the game field, and I'll process it for you!")
    await state.set_state(Form.waiting_for_photo)

@dp.message(Form.waiting_for_photo, F.content_type == ContentType.PHOTO)
async def handle_image(message: Message, state: FSMContext):
    photo = message.photo[-1]
    file_path = await bot.download(photo)
    input_path = f"input_{message.from_user.id}.jpg"
    output_path = f"output_{message.from_user.id}.jpg"

    with open(input_path, "wb") as file:
        file.write(file_path.read())

    processed_path = await solve_puzzle(input_path, output_path)

    if processed_path:
        await message.answer_photo(FSInputFile(processed_path))

        os.remove(input_path)
        os.remove(output_path)
    else:
        await message.answer("Failed to process the image. Please try again with a different one.")

    await state.set_state(Form.waiting_for_photo)

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
