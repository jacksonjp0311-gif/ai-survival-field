from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


@dataclass(frozen=True)
class ObservedCommand:
    command: list[str]
    cwd: str
    exit_code: int
    stdout: str
    stderr: str
    mutation_performed: bool = False
    mode: str = "read_only_observe"

    def as_dict(self) -> dict:
        return dict(self.__dict__)


def observe_command(command: Sequence[str], *, cwd: str | Path = ".", timeout: int = 60) -> ObservedCommand:
    result = subprocess.run(
        list(command),
        cwd=Path(cwd),
        text=True,
        capture_output=True,
        timeout=timeout,
    )
    return ObservedCommand(
        command=list(command),
        cwd=str(Path(cwd)),
        exit_code=result.returncode,
        stdout=result.stdout,
        stderr=result.stderr,
    )
