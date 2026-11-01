"""Учебный FastAPI CRUD. Запуск из practice: python -m uvicorn api:app --reload."""

import os
from collections.abc import Iterator
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query, Response
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from models import Base, Task, User, make_engine


class UserCreate(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    email: str = Field(min_length=3, max_length=200)
    age: int = Field(ge=0)


class UserOut(UserCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    active: bool


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=120)


class TaskPut(TaskCreate):
    completed: bool


class TaskOut(TaskPut):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int


class UserWithTasks(UserOut):
    tasks: list[TaskOut]


def create_app(database_url=None):
    database_url = database_url or os.getenv("STUDY_DATABASE_URL", "sqlite+pysqlite:///study.db")
    engine = make_engine(database_url)

    @asynccontextmanager
    async def lifespan(app):
        # Только для учебного запуска. При использовании Alembic уберите create_all.
        Base.metadata.create_all(engine)
        try:
            yield
        finally:
            engine.dispose()

    app = FastAPI(title="SQLAlchemy study CRUD", lifespan=lifespan)

    def get_session() -> Iterator[Session]:
        with Session(engine) as session:
            yield session

    SessionDep = Annotated[Session, Depends(get_session)]

    @app.post("/users", response_model=UserOut, status_code=201)
    def create_user(body: UserCreate, session: SessionDep):
        user = User(**body.model_dump())
        session.add(user)
        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            raise HTTPException(status_code=409, detail="Email already exists") from None
        session.refresh(user)
        return user

    @app.get("/users", response_model=list[UserOut])
    def list_users(session: SessionDep, limit: Annotated[int, Query(ge=1, le=100)] = 20):
        return session.scalars(select(User).order_by(User.id).limit(limit)).all()

    @app.get("/users/{user_id}", response_model=UserWithTasks)
    def read_user(user_id: int, session: SessionDep):
        user = session.scalar(
            select(User).where(User.id == user_id).options(selectinload(User.tasks))
        )
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    @app.post("/users/{user_id}/tasks", response_model=TaskOut, status_code=201)
    def create_task(user_id: int, body: TaskCreate, session: SessionDep):
        if session.get(User, user_id) is None:
            raise HTTPException(status_code=404, detail="User not found")
        task = Task(user_id=user_id, **body.model_dump())
        session.add(task)
        session.commit()
        session.refresh(task)
        return task

    @app.put("/tasks/{task_id}", response_model=TaskOut)
    def replace_task(task_id: int, body: TaskPut, session: SessionDep):
        task = session.get(Task, task_id)
        if task is None:
            raise HTTPException(status_code=404, detail="Task not found")
        task.title = body.title
        task.completed = body.completed
        session.commit()
        session.refresh(task)
        return task

    @app.delete("/tasks/{task_id}", status_code=204)
    def delete_task(task_id: int, session: SessionDep):
        task = session.get(Task, task_id)
        if task is None:
            raise HTTPException(status_code=404, detail="Task not found")
        session.delete(task)
        session.commit()
        return Response(status_code=204)

    return app


app = create_app()
