from aiogram.fsm.storage.redis import RedisStorage
from aioredis import Redis
from config import BOT_TOKEN, REDIS_HOST
from loguru import logger
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import Command
from routes import pictures_r, paying_route
from routes.pictures_r import user_service

redis: Redis = Redis(host=REDIS_HOST, port=6379, decode_responses=True)
storage: RedisStorage = RedisStorage(redis)

logger.add(
    "app.log",
    rotation="50 MB",
    retention="10 days",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=storage)


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Добро пожаловать. Здесь вы можете создать картинку ")
    await user_service.create_user_with_coins(user_id=message.from_user.id)


dp.include_router(pictures_r.router)
dp.include_router(paying_route.router)


async def main():
    try:
        logger.info("Bot started")
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f'Unexpected error: {e}')
    finally:
        await bot.session.close()
        await redis.close()


if __name__ == "__main__":
    asyncio.run(main())
