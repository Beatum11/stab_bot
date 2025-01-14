from aiogram import Router, F
from aiogram.types import Message, LabeledPrice, PreCheckoutQuery
from aiogram.filters import Command
from routes.pictures_r import UserService

router = Router()
user_service = UserService()


@router.message(Command('pay'))
async def sub_start_handler(message: Message) -> None:
    greet_msg: str = ('Чтобы оплатить новые картинки, используйте одну из следующих команд\n\n'
                      '/coins_50\n\n'
                      '/coins_100')
    await message.answer(greet_msg)


@router.message(Command('coins_50'))
@router.message(Command('coins_100'))
async def sub_pay_handler(message: Message) -> None:
    total: int = int(message.text.split('_')[1])

    prices = [LabeledPrice(label="XTR", amount=total)]
    await message.answer_invoice(
        title="Оплата подписки",
        description=f"Вы платите {total} stars и получаете возможность дополнительно пользоваться ботом.",
        prices=prices,
        # provider_token Должен быть пустым
        provider_token="",
        payload=f"{total}_stars",
        currency="XTR"
    )


@router.pre_checkout_query()
async def on_pre_checkout_query(pre_checkout_query: PreCheckoutQuery) -> None:
    await pre_checkout_query.answer(ok=True)


@router.message(F.successful_payment)
async def on_successful_payment(message: Message) -> None:
    payment_info = message.successful_payment
    amount = int(payment_info.total_amount)
    
    new_balance = await user_service.add_coins(
        user_id=message.from_user.id,
        amount=amount
    )
    
    await message.answer(
        f"Оплата прошла успешно!\n"
        f"Добавлено {amount} монет.\n"
        f"Ваш текущий баланс: {new_balance} монет."
    )
