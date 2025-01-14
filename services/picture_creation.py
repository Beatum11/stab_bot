import os
import httpx
import aiofiles
from config import STABILITY_KEY
from services.prompt_enhancing import PromptEnhancer
from services.user_service import UserService


class PictureCreator:

    def __init__(self, user_service: UserService):
        self.stability_key = STABILITY_KEY
        self.user_service = user_service
        if not self.stability_key:
            raise ValueError("STABILITY_KEY is missing in the environment variables")

    async def generate_picture(self, prompt: str, user_id: int, output_path: str = "./data/picture.png"):
        """
        Генерация изображения на основе промпта.
        :param prompt: Текстовое описание для генерации изображения.
        :param output_path: Путь для сохранения изображения.
        :return: Путь к сохранённому изображению.
        """

        pro_enhancer = PromptEnhancer()
        fin_prompt = await pro_enhancer.enhance_prompt(prompt)

        headers = {
            "authorization": f"Bearer {self.stability_key}",
            "accept": "image/*"
        }

        # Подготавливаем данные в том же формате, что и в документации
        files = {"none": ""}
        data = {
            "prompt": fin_prompt,
            "output_format": "png"
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    "https://api.stability.ai/v2beta/stable-image/generate/ultra",
                    headers=headers,
                    files=files,
                    data=data,
                    timeout=25.0  # Добавляем таймаут, так как генерация может занять время
                )

                if response.status_code == 200:
                    print('получили успешный ответ')
                    # Убедимся, что директория для сохранения существует
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)

                    # Асинхронно сохраняем изображение в файл
                    async with aiofiles.open(output_path, 'wb') as file:
                        await file.write(response.content)
                    await self.user_service.subtract_coins(user_id=user_id, amount=5)
                    return output_path
                else:
                    error_text = response.text
                    print(f"Response headers: {response.headers}")
                    print(f"Response status: {response.status_code}")
                    raise Exception(f"API Error: {response.status_code}, {error_text}")

            except httpx.TimeoutException:
                raise Exception("Запрос превысил время ожидания")
            except Exception as e:
                raise Exception(f"Unexpected error: {str(e)}")
