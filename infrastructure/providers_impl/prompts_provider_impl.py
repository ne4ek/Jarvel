from application.providers.prompts_provider import PromptsProvider


class PromptsProviderImpl(PromptsProvider):
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)