from dotenv import load_dotenv
import os

load_dotenv()

class Env:
    def __init__(self):
        self.VECTOR_SIZE = os.getenv("VECTOR_SIZE")

env = Env()