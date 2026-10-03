"""PoC-only review notes, isolated from family publications and care records."""
from typing import Literal
from fastapi import APIRouter, Request
from pydantic import Field
from .common import Input, Fault, uid, now, envelope
from .db import insert, many, need
from .security import session, execute

router = APIRouter(prefix='/api/v1/poc/comments')
Screen = Literal['general', 'family', 'questions', 'record', 'publication', 'consent']


class CommentCreate(Input):
    reviewer_alias: str = Field(min_length=1, max_length=40)
    screen: Screen
    body: str = Field(min_length=1, max_length=3000)


def reviewer(request, db):
    if not request.app.state.settings.poc_mode:
        raise Fault('RESOURCE_NOT_FOUND', 404)
    return session(request, db, 'staff')


@router.get('')
def listing(request: Request, screen: Screen | None = None):
    with request.app.state.store.transaction() as db:
        reviewer(request, db)
        rows = many(db, '''SELECT comment_id,reviewer_alias,screen,body,created_at
            FROM review_comments WHERE (? IS NULL OR screen=?)
            ORDER BY created_at DESC,comment_id DESC LIMIT 200''', (screen, screen))
        return envelope({'items': rows})


@router.post('', status_code=201)
def create(body: CommentCreate, request: Request):
    with request.app.state.store.transaction() as db:
        actor = reviewer(request, db)
        def operation():
            comment_id = uid()
            insert(db, 'review_comments', comment_id=comment_id,
                   actor_id=actor['actor_id'], **body.model_dump(), created_at=now())
            return {'id': comment_id}
        def render(ref):
            return need(db, '''SELECT comment_id,reviewer_alias,screen,body,created_at
                FROM review_comments WHERE comment_id=?''', (ref['id'],))
        return envelope(execute(request, db, actor, body.model_dump(), operation, render))
