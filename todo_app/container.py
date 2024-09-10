from dependency_injector import containers, providers
from passlib.context import CryptContext

from . import routers
from .core import Database
from .core.config import settings
from .repositories import TodoRepository
from .services import TodoService
from .services.user_auth import UserAuthService

DATABASE_URL = settings.database.url


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(packages=[routers.__name__])

    database = providers.Singleton(Database, db_url=DATABASE_URL)
    todo_repository = providers.Singleton(TodoRepository, database=database)
    todo_service = providers.Singleton(TodoService, todo_repository=todo_repository)
    pwd_context = providers.Singleton(CryptContext, schemes=["bcrypt"], deprecated="auto")
    user_service = providers.Singleton(UserAuthService, pwd_context=pwd_context, todo_service=todo_service)
