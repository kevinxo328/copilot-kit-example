#!/usr/bin/env python3

from __future__ import annotations

import os
import signal
import subprocess
import sys
import threading
from dataclasses import dataclass
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class Command:
    prefix: str
    argv: list[str]
    cwd: Path
    env: dict[str, str]


def should_skip_line(prefix: str, line: str, interrupted: threading.Event) -> bool:
    if not interrupted.is_set():
        return False

    stripped = line.strip()
    if prefix == 'frontend' and (
        'ELIFECYCLE' in stripped or 'Interrupt: 2' in stripped
    ):
        return True

    return False


def stream_output(
    prefix: str, process: subprocess.Popen[str], interrupted: threading.Event
) -> None:
    assert process.stdout is not None
    for line in process.stdout:
        if should_skip_line(prefix, line, interrupted):
            continue
        sys.stdout.write(f'[{prefix}] {line}')
        sys.stdout.flush()
    process.stdout.close()


def terminate(processes: list[subprocess.Popen[str]], sig: int) -> None:
    for process in processes:
        if process.poll() is None:
            try:
                os.killpg(process.pid, sig)
            except ProcessLookupError:
                pass


def main() -> int:
    processes: list[subprocess.Popen[str]] = []
    interrupted = threading.Event()

    def handle_signal(signum: int, _frame: object) -> None:
        if interrupted.is_set():
            return
        interrupted.set()
        terminate(processes, signum)

    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, handle_signal)

    commands = [
        Command(
            prefix='backend',
            argv=['uv', 'run', 'task', 'dev'],
            cwd=ROOT_DIR / 'backend',
            env={},
        ),
        Command(prefix='frontend', argv=['pnpm', 'dev'], cwd=ROOT_DIR / 'frontend', env={}),
    ]

    threads: list[threading.Thread] = []
    exit_code = 0

    try:
        for command in commands:
            env = os.environ.copy()
            env.update(command.env)
            process = subprocess.Popen(
                command.argv,
                cwd=command.cwd,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                start_new_session=True,
            )
            processes.append(process)
            thread = threading.Thread(
                target=stream_output,
                args=(command.prefix, process, interrupted),
                daemon=True,
            )
            thread.start()
            threads.append(thread)

        while processes:
            for process in processes:
                status = process.poll()
                if status is None:
                    continue

                if not interrupted.is_set():
                    exit_code = status
                    interrupted.set()
                    terminate(processes, signal.SIGTERM)
                processes = [proc for proc in processes if proc.poll() is None]
                break

        for thread in threads:
            thread.join()

        if interrupted.is_set() and exit_code in (0, -signal.SIGINT, -signal.SIGTERM):
            return 0
        return exit_code
    finally:
        terminate(processes, signal.SIGTERM)
        for process in processes:
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass


if __name__ == '__main__':
    raise SystemExit(main())
