import motor.motor_asyncio as motorio
from typing import Optional


class MongoDB:
    _instance: Optional[motorio.AsyncIOMotorClient] = None

    @staticmethod
    def get_instance(connection_string: str = None) -> motorio.AsyncIOMotorClient:
        """Get or create MongoDB singleton instance"""
        if MongoDB._instance is None:
            if connection_string is None:
                raise ValueError("Connection string is required for first initialization")
            MongoDB(connection_string)
        return MongoDB._instance

    def __init__(self, connection_string: str):
        if MongoDB._instance is not None:
            raise Exception('Singleton instance already exists')
        try:
            MongoDB._instance = motorio.AsyncIOMotorClient(connection_string)
        except Exception as e:
            raise Exception(f'MongoDB connection error: {e}')
