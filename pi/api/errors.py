class ApiError(RuntimeError):

    def __init__(self, message: str):
        super().__init__(message)


class CurrentUserNotFoundError(ApiError):
    pass


class DailyQuestionQuotaReachedError(ApiError):

    def __init__(
        self,
        message: str,
        user_id: int,
        limit_per_day: int,
        created_count: int,
        **kwargs
    ):
        super().__init__(message)

        self.user_id = user_id
        self.limit_per_day = limit_per_day
        self.created_count = created_count


class DiscordUserNotFoundError(ApiError):

    def __init__(self, message: str, **kwargs):
        super().__init__(message)

        self.properties = kwargs


class QuestionNotFoundError(ApiError):

    def __init__(self, message: str, question_id: int):
        super().__init__(message)

        self.question_id = question_id


class GenericApiError(ApiError):

    def __init__(self, code: str, message: str, **kwargs):
        super().__init__(message)

        self.code = code
        self.properties = kwargs
