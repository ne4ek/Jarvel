from application.providers.usecases_provider import UseCasesProvider


class UseCaseProviderImpl(UseCasesProvider):
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
