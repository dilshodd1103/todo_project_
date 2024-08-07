from dynaconf import Dynaconf

settings = Dynaconf(
    root_path="todo_app/core",
    settings_files=["settings.toml", ".secrets.toml"],
    secrets=".secrets.toml",
)
