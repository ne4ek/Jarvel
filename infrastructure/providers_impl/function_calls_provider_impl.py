from application.providers.function_calls_provider import FunctionCallsProvider


class FunctionCallsProviderImpl(FunctionCallsProvider):
    def __init__(self):
        self.function_calls = {}

    def add_function_calls(self, function_call: dict):
        for key, value in function_call.items():
            self.function_calls[key] = value

    def get_function_call(self, function_name: str) -> dict:
        if function_name in self.function_calls.keys():
            return self.function_calls.get(function_name)
        raise ValueError(f"Function '{function_name}' is not registered")
