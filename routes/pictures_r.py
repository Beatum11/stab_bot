from aiogram import Router, F
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, FSInputFile
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from services.picture_creation import PictureCreator
from services.prompt_enhancing import PromptEnhancer
from services.user_service import UserService

router = Router()
user_service = UserService()
picture_creator = PictureCreator(user_service=user_service)
prompt_enhancer = PromptEnhancer()


class PromptState(StatesGroup):
    first_question = State()
    second_question = State()
    third_question = State()
    finalizing_prompt = State()


async def ask_middle_question(message: Message, state: FSMContext):
    data = await state.get_data()
    temp_prompt_list = [
        data.get('main_prompt', ''),
        data.get('additional_info_1', ''),
        data.get('additional_info_2', ''),
    ]
    temp_prompt = ' '.join(temp_prompt_list)
    question = await prompt_enhancer.ask_question(part_of_the_prompt=temp_prompt)
    if not question:
        await message.answer('Произошла ошибка, давайте попробуем заново: /image')
    await message.answer(question)


@router.message(Command('image'))
async def pic_root(message: Message, state: FSMContext):
    await state.clear()  # Сброс состояния
    await message.answer('Введите промпт для создания картинки')
    await state.set_state(PromptState.first_question)


@router.message(PromptState.first_question)
async def question_handler(message: Message, state: FSMContext):
    try:
        await state.update_data(main_prompt=message.text)

        await ask_middle_question(message=message, state=state)

        await state.set_state(PromptState.second_question)
    except Exception as e:
        await message.answer(f'Произошла ошибка, попробуйте чуть позже!, {e}')


@router.message(PromptState.second_question)
async def question_handler(message: Message, state: FSMContext):
    try:
        await state.update_data(additional_info_1=message.text)

        await ask_middle_question(message=message, state=state)

        await state.set_state(PromptState.third_question)
    except Exception as e:
        await message.answer(f'Произошла ошибка, попробуйте чуть позже!, {e}')


@router.message(PromptState.third_question)
async def question_handler(message: Message, state: FSMContext):
    try:
        await state.update_data(additional_info_2=message.text)

        await ask_middle_question(message=message, state=state)

        await state.set_state(PromptState.finalizing_prompt)
    except Exception as e:
        await message.answer(f'Произошла ошибка, попробуйте чуть позже!, {e}')


@router.message(PromptState.finalizing_prompt)
async def prompt_handler(message: Message, state: FSMContext):
    try:

        data = await state.get_data()
        final_prompt = f"{data.get('main_prompt', '')} {data.get('additional_info_1', '')} {data.get('additional_info_2', '')} {message.text}"

        pic_path = await picture_creator.generate_picture(prompt=final_prompt)
        if not pic_path:
            await message.answer('Картинка пока не получается, попробуйте ЧУТЬ позже')
            return

        photo = FSInputFile(pic_path)
        await message.answer_photo(photo)

    except Exception as e:
        await message.answer(f'Произошла ошибка, попробуйте чуть позже!, {e}')
    finally:
        await state.clear()