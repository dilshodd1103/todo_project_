import importlib
import pkgutil
from types import ModuleType

from fastapi import FastAPI

from . import routers
from .container import Container


def create_app() -> FastAPI:
    container = Container()
    container.wire(packages=[routers.__name__])

    app = FastAPI()
    app.container = container

    include_routers(app, routers)

    return app


def include_routers(app: FastAPI, pkg: ModuleType) -> None:
    for router_modinfo in pkgutil.walk_packages(pkg.__path__):
        if router_modinfo.name.startswith(("_", "__")):
            continue

        router_module = importlib.import_module(f".{router_modinfo.name}", pkg.__name__)

        if router_modinfo.ispkg:
            include_routers(app, router_module)

        app.include_router(router_module.router)


app = create_app()
