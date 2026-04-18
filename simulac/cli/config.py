from __future__ import annotations

import os

import typer

from simulac.base.envvar.envvar_service import EnvvarKeyValue, EnvvarService

from .common import collect_config_snapshot, mask_secret


def show_config() -> None:
    payload = collect_config_snapshot(EnvvarService())
    max_key_length = max(len(key) for key in payload.keys())

    for key in payload.keys():
        label = key.replace("_", " ").title()
        typer.echo(f"{label:<{max_key_length}}: {payload[key]}")


def show_envvars() -> None:
    payload: dict[str, str | None] = {}
    max_key_length = max(len(key.value) for key in EnvvarKeyValue)

    for env_var in EnvvarKeyValue:
        variable_name = env_var.value
        raw_value = os.environ.get(variable_name)
        display_value = (
            mask_secret(raw_value.strip())
            if variable_name == EnvvarKeyValue.SIMULAC_API_KEY.value and raw_value
            else raw_value
        )
        payload[variable_name] = display_value

    for env_var in EnvvarKeyValue:
        variable_name = env_var.value
        variable = payload[variable_name]
        value = variable if variable is not None else "<unset>"
        typer.echo(f"{variable_name:<{max_key_length}}: {value}")
