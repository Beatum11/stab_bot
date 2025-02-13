import motor.motor_asyncio as motorio
from typing import Optional


class MongoDB:
    _instance: Optional[motorio.AsyncIOMotorClient] = None

    @staticmethod
    def get_instance(connection_string: str = None) -> motorio.AsyncIOMotorClient:

        if MongoDB._instance is None:
            MongoDB(connection_string)
        return MongoDB._instance

    def __init__(self, connection_string: str):
        if MongoDB._instance is not None:
            raise Exception('Singleton instance already exists')
        try:
            MongoDB._instance = motorio.AsyncIOMotorClient(connection_string)
        except Exception as e:
            raise Exception(f'MongoDB connection error: {e}')
