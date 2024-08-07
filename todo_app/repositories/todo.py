from ..core.database import Database
from ..models.todo import Todo


class TodoRepository:
    def __init__(self, database: Database) -> None:
        self.database = database
        self.session_factory = self.database.session

    def get(self, instance_id: str) -> Todo:
        with self.session_factory() as session:
            return session.query(Todo).filter(Todo.id == instance_id).one()

    def find_all(self) -> list[Todo]:
        with self.session_factory() as session:
            return session.query(Todo).all()

    def store(self, instance: Todo) -> Todo:
        with self.session_factory() as session:
            session.add(instance)
            session.commit()
            session.refresh(instance)
            return instance

    def delete(self, instance_id: str) -> None:
        with self.session_factory() as session:
            instance = session.query(Todo).filter(Todo.id == instance_id).one()
            session.delete(instance)
            session.commit()
