# bot_manager.py
from aiogram import Bot
import logging

class BotManager:
    def __init__(self, tokens: list):
        self.bots = {token: Bot(token) for token in tokens}
        self.current_token = tokens[0]
        logging.info(f"Инициализирован бот с токеном: {self.current_token[:10]}...")

    def get_current_bot(self) -> Bot:
        return self.bots[self.current_token]
