"""Запуск: python demo.py. Все данные находятся во временной SQLite in-memory."""

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload, selectinload, subqueryload

from models import Base, Profile, Tag, Task, User, make_engine


def main():
    engine = make_engine()
    Base.metadata.create_all(engine)

    try:
        # CREATE: один commit для всего связанного графа.
        with Session(engine) as session, session.begin():
            python = Tag(name="python")
            anna = User(name="Anna", email="anna@example.test", age=24)
            anna.profile = Profile(bio="Backend developer")
            anna.tasks = [
                Task(title="Study ORM", tags=[python]),
                Task(title="Write tests", tags=[python], completed=True),
            ]
            boris = User(name="Boris", email="boris@example.test", age=30)
            session.add_all([anna, boris])
            session.flush()
            anna_id, boris_id = anna.id, boris.id
            task_id = anna.tasks[0].id
            print("CREATE:", anna_id, boris_id)

        # READ + identity map.
        with Session(engine) as session:
            anna = session.get(User, anna_id)
            print("READ:", anna.name)
            print("IDENTITY MAP:", anna is session.get(User, anna_id))
            statement = (
                select(User)
                .where(User.age >= 18, User.active.is_(True))
                .order_by(User.age.desc(), User.id)
                .limit(10)
            )
            print("FILTER:", [user.name for user in session.scalars(statement)])

            joined = select(User.name, Task.title).join(User.tasks).order_by(Task.id)
            print("JOIN:", session.execute(joined).all())
            aggregate = (
                select(User.name, func.count(Task.id).label("task_count"))
                .outerjoin(User.tasks)
                .group_by(User.id, User.name)
                .having(func.count(Task.id) >= 0)
                .order_by(User.id)
            )
            print("AGGREGATE:", session.execute(aggregate).all())
            counts = (
                select(Task.user_id, func.count(Task.id).label("n"))
                .group_by(Task.user_id)
                .subquery()
            )
            print(
                "SUBQUERY:",
                session.scalars(
                    select(User).join(counts, User.id == counts.c.user_id).where(counts.c.n >= 2)
                ).all(),
            )
            legacy = (
                session.query(User.name, func.count(Task.id))
                .join(User.tasks)
                .filter(User.age >= 18)
                .group_by(User.id, User.name)
                .having(func.count(Task.id) >= 1)
                .order_by(User.name)
                .all()
            )
            print("LEGACY QUERY:", legacy)

        # Свежая Session для каждого способа: ранее загруженная коллекция не скрывает SQL.
        for label, loader in [
            ("SELECT IN", selectinload(User.tasks)),
            ("JOINED", joinedload(User.tasks)),
            ("SUBQUERY LOAD", subqueryload(User.tasks)),
        ]:
            with Session(engine) as session:
                users = session.scalars(select(User).options(loader).order_by(User.id)).unique().all()
                print(label, [(user.name, len(user.tasks)) for user in users])

        # UPDATE: отслеживание изменений объекта.
        with Session(engine) as session, session.begin():
            task = session.get(Task, task_id)
            task.completed = True
        with Session(engine) as session:
            print("UPDATE:", session.get(Task, task_id).completed)

        # Ошибка UNIQUE: rollback восстанавливает пригодность Session к работе.
        with Session(engine) as session:
            session.add(User(name="Duplicate", email="anna@example.test", age=20))
            try:
                session.commit()
            except IntegrityError:
                session.rollback()
                print("ROLLBACK:", session.scalar(select(func.count(User.id))))

        # DELETE и каскадное удаление профиля/задач; общий тег остаётся.
        with Session(engine) as session, session.begin():
            session.delete(session.get(User, anna_id))
        with Session(engine) as session:
            print("DELETE:", session.get(User, anna_id))
            print("REMAINING TASKS:", session.scalar(select(func.count(Task.id))))
            print("REMAINING TAGS:", session.scalar(select(func.count(Tag.id))))
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
