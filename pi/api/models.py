import dataclasses
import datetime
import enum
import typing

import dataclasses_json
import marshmallow
import marshmallow.utils

ISO8086 = dataclasses_json.config(
    encoder=marshmallow.utils.isoformat,
    decoder=marshmallow.utils.from_iso_datetime,
    mm_field=marshmallow.fields.DateTime(format='iso')
)


@dataclasses_json.dataclass_json(
    letter_case=dataclasses_json.LetterCase.CAMEL,
    undefined=dataclasses_json.Undefined.EXCLUDE,
)
@dataclasses.dataclass
class User:
    id: int
    name: str


@dataclasses_json.dataclass_json(
    letter_case=dataclasses_json.LetterCase.CAMEL,
    undefined=dataclasses_json.Undefined.EXCLUDE,
)
@dataclasses.dataclass
class CurrentUser(User):
    points: int


class DatasourceStatus(enum.Enum):
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"


@dataclasses_json.dataclass_json(
    letter_case=dataclasses_json.LetterCase.CAMEL,
    undefined=dataclasses_json.Undefined.EXCLUDE,
)
@dataclasses.dataclass
class Datasource:
    id: int
    name: str
    label: str
    status: DatasourceStatus
    display_order: int
    default: bool

    @property
    def is_active(self):
        return self.status == DatasourceStatus.ACTIVE


class QuestionStatus(enum.Enum):
    PENDING = "PENDING"
    ANSWERING = "ANSWERING"
    CORRELATING = "CORRELATING"
    COMPLETED = "COMPLETED"


@dataclasses_json.dataclass_json(
    letter_case=dataclasses_json.LetterCase.CAMEL,
    undefined=dataclasses_json.Undefined.EXCLUDE,
)
@dataclasses.dataclass
class Question:
    id: int
    user: User
    number: int
    original_prompt: str
    rephrased_prompt: typing.Optional[str]
    status: QuestionStatus
    success: typing.Optional[bool]
    error: typing.Optional[str]
    tags: typing.Optional[typing.List[str]]
    uniqueness_score: typing.Optional[float]
    correlation_score: typing.Optional[float]
    rewarded_points: typing.Optional[float]
    datasource: typing.Optional[Datasource]
    created_at: datetime.datetime = dataclasses.field(metadata=ISO8086)

    @property
    def is_completed(self):
        return self.status == QuestionStatus.COMPLETED


class TimeseriesType(enum.Enum):
    QUESTION = "QUESTION"
    CORRELATION = "CORRELATION"


@dataclasses_json.dataclass_json(
    letter_case=dataclasses_json.LetterCase.CAMEL,
    undefined=dataclasses_json.Undefined.EXCLUDE,
)
@dataclasses.dataclass
class TimeseriesScaleNote:
    value: float
    reason: str


@dataclasses_json.dataclass_json(
    letter_case=dataclasses_json.LetterCase.CAMEL,
    undefined=dataclasses_json.Undefined.EXCLUDE,
)
@dataclasses.dataclass
class TimeseriesScale:
    minimum: float
    maximum: float
    lower_bound: typing.Optional[float]
    upper_bound: typing.Optional[float]
    notes: typing.Optional[typing.List[TimeseriesScaleNote]]


@dataclasses_json.dataclass_json(
    letter_case=dataclasses_json.LetterCase.CAMEL,
    undefined=dataclasses_json.Undefined.EXCLUDE,
)
@dataclasses.dataclass
class TimeseriesData:
    date: str
    value: float
    release_date: typing.Optional[str]
    explanation: typing.Optional[str]


@dataclasses_json.dataclass_json(
    letter_case=dataclasses_json.LetterCase.CAMEL,
    undefined=dataclasses_json.Undefined.EXCLUDE,
)
@dataclasses.dataclass
class Timeseries:
    id: int
    type: TimeseriesType
    title: str
    unit: typing.Optional[str]
    strength: typing.Optional[str]
    y_axis_label: str
    correlation_type: typing.Optional[str]
    correlation: typing.Optional[float]
    adjusted_correlation: typing.Optional[float]
    correlation_confidence: typing.Optional[float]
    scale: TimeseriesScale
    data: typing.List[TimeseriesData]
    created_at: datetime.datetime = dataclasses.field(metadata=ISO8086)
