import openai


class OpenAIClient:
    _instance = None

    @classmethod
    def get_instance(cls, **kwargs):
        if cls._instance is None:
            cls._instance = openai.OpenAI(**kwargs)

        return cls._instance
