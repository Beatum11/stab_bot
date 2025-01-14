from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase


class UserService:
    def __init__(self, client: AsyncIOMotorClient, db_name: str = "users"):
        self.db: AsyncIOMotorDatabase = client[db_name]
        self.users = self.db.users

    async def create_user_with_coins(self, user_id: int, coins: int = 0) -> bool:
        """Create new user with initial coins amount"""
        try:
            result = await self.users.insert_one({
                "_id": user_id,
                "coins": coins
            })
            return bool(result.inserted_id)
        except Exception as e:
            raise Exception(f"Error creating user: {e}")

    async def add_coins(self, user_id: int, amount: int):
        """Add coins to user balance and return new balance"""
        try:
            result = await self.users.find_one_and_update(
                {"_id": user_id},
                {"$inc": {"coins": amount}},
                return_document=True
            )
            return result["coins"] if result else None
        except Exception as e:
            raise Exception(f"Error adding coins: {e}")

    async def subtract_coins(self, user_id: int, amount: int):
        """Subtract coins from user balance and return new balance"""
        try:
            # Проверяем, достаточно ли монет
            user = await self.users.find_one({"_id": user_id})
            if not user or user["coins"] < amount:
                return None

            result = await self.users.find_one_and_update(
                {"_id": user_id},
                {"$inc": {"coins": -amount}},
                return_document=True
            )
            return result["coins"] if result else None
        except Exception as e:
            raise Exception(f"Error subtracting coins: {e}")
