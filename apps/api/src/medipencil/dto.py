"""Read contracts are distinct from storage. Family contracts forbid extra fields."""
from typing import Generic,TypeVar,Literal
from pydantic import BaseModel,ConfigDict
T=TypeVar('T')
class DTO(BaseModel):model_config=ConfigDict(extra='forbid')
class Meta(DTO):
    request_id:str
    server_time:str
class Response(DTO,Generic[T]):
    data:T
    meta:Meta
class Person(DTO):
    actor_id:str
    display_name:str
class Subject(DTO):
    subject_id:str
    display_name:str
class PublicItem(DTO):
    item_id:str
    topic:str
    statement:str
    status:Literal['observed','confirmed','none']
    claim_type:Literal['unattributed_statement','resident_statement','staff_observation','sensor_observation','plan','contact_plan']
    observed_at:str
    action_status:Literal['planned','confirmed']|None
    evidence_handle:str
class Tile(DTO):
    topic:str
    display_state:Literal['available','no_record','not_shared','awaiting_review']
    items:list[PublicItem]
class Answer(DTO):
    question_id:str
    item_ids:list[str]
class FamilyBoardDTO(DTO):
    subject:Subject
    viewer:Person
    lang:Literal['fi','sv','en']
    display_timezone:str
    board_state:Literal['ready','awaiting_review','empty']
    language_state:Literal['available','unavailable']
    tiles:list[Tile]
    answers:list[Answer]
    publication_id:str|None
    published_at:str|None
    can_ask:bool
    execution:dict
class QuestionReplyItem(DTO):
    statement:str
    claim_type:str
class QuestionReply(DTO):
    author_display:str
    published_at:str
    items:list[QuestionReplyItem]
class QuestionDTO(DTO):
    question_id:str
    subject_id:str
    text:str
    status:Literal['received','scheduled','unanswered','answered']
    review_due:str|None
    updated_at:str
    revision:int
    answer_available:bool
    display_state:str
    assigned_to_display:str|None=None
    created_at:str
    author_display:str
    reply:QuestionReply|None=None
class Page(DTO,Generic[T]):
    items:list[T]
    next_cursor:str|None
class EvidencePreviewDTO(DTO):
    item_id:str
    source_label:str
    occurred_at:str
    excerpt:str
    evidence_state:Literal['valid']
class JobDTO(DTO):
    job_id:str
    job_type:str
    status:Literal['queued','running','succeeded','failed','canceled']
    result_ref:dict|None
    progress_stage:str
    started_at:str|None
    finished_at:str|None
    error_code:str|None
    retryable:bool
    execution:dict
