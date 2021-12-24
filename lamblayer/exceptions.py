class LamblayerBaseError(Exception):
    def __init__(self, message="-"):
        self.message = message

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f"{self.message}"


class LamblayerInvalidOptionError(LamblayerBaseError):
    def __init__(self, message="-"):
        super().__init__(message)


class LamblayerParamValidationError(LamblayerBaseError):
    def __init__(self, param_name, param_value, valid_type):
        message = "ParamValidationError: Parameter validation failed:\n"
        f"Invalid type for parameter {param_name}, value: {param_value},"
        f"type: {param_value.__class__}, valid types: {valid_type}"
        super().__init__(message)


class LamblayerCreateLayerError(LamblayerBaseError):
    def __init__(self, message="-"):
        super().__init__(message)
