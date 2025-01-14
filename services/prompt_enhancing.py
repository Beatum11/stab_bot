import aiohttp

from config import OPENAI_KEY
from loguru import logger
from openai import AsyncOpenAI


class PromptEnhancer:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=OPENAI_KEY)

    async def openai_request(self, max_tokens: int, request: str):
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": request}
                ],
                max_tokens=max_tokens,
                temperature=0.7,
                top_p=1,
            )
            if response is None or not hasattr(response, "choices"):
                logger.warning("Некорректный ответ от OpenAI.")
                return "временная ошибка"

            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.warning(f"Ошибка при обработке промпта: {e}")
            return 'временная ошибка, простите'

    # ---------------------------------------------------------------------------
    async def ask_question(self, part_of_the_prompt: str):
        request = (f"Сейчас я дам тебе промпт для создания картинки. Твоя задача – задать один уточняющий вопрос, "
                   f"чтобы улучшить промпт и создать картинку, которая максимально понравится пользователю."
                   f"Промпт: {part_of_the_prompt}")

        return await self.openai_request(max_tokens=100, request=request)

    # ----------------------------------------------------------------------------
    async def enhance_prompt(self, prompt: str):

        request_prompt = (f'Ты помогаешь улучшать промпты для генерации изображений ИИ. '
                          f'Переведи следующий промпт на английский, добавив детали для лучшего результата + ответь '
                          f'только промптом: \n\n{prompt}')

        return await self.openai_request(max_tokens=300, request=request_prompt)
