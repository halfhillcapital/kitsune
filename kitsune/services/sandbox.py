"""Docker sandbox manager for per-user marimo instances."""

from __future__ import annotations

import asyncio
import shutil
import time
from dataclasses import dataclass, field
from pathlib import Path

import docker
from docker.errors import NotFound

from kitsune.config import get_config


@dataclass
class ContainerInfo:
    container_id: str
    session_id: str
    host_port: int
    created_at: float = field(default_factory=time.time)
    last_activity: float = field(default_factory=time.time)

    def touch(self) -> None:
        self.last_activity = time.time()


class SandboxManager:
    def __init__(self) -> None:
        config = get_config()
        self._client = docker.from_env()
        self._image = config.MARIMO_IMAGE
        self._port_start = config.MARIMO_PORT_START
        self._port_end = config.MARIMO_PORT_END
        self._timeout = config.MARIMO_CONTAINER_TIMEOUT
        self._data_dir = Path(config.NOTEBOOK_DATA_DIR)
        # Host-side base path for Docker volume mounts. When Kitsune runs inside a
        # container, this must point to the same directory on the *host* filesystem so
        # that sibling sandbox containers can mount it. Falls back to _data_dir when
        # running directly on the host (paths are identical in that case).
        self._host_dir = Path(config.NOTEBOOK_HOST_DIR) if config.NOTEBOOK_HOST_DIR else self._data_dir
        self._seed_dir = Path("notebooks")
        self._containers: dict[str, ContainerInfo] = {}
        self._cleanup_task: asyncio.Task | None = None

    # -- lifecycle --

    async def startup(self) -> None:
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())

    async def shutdown(self) -> None:
        if self._cleanup_task:
            self._cleanup_task.cancel()
        for session_id in list(self._containers):
            await self.destroy(session_id)

    # -- public API --

    async def get_or_create(self, session_id: str) -> ContainerInfo:
        if session_id in self._containers:
            self._containers[session_id].touch()
            return self._containers[session_id]

        user_dir = self._data_dir / session_id
        user_dir.mkdir(parents=True, exist_ok=True)

        # Seed with template notebooks if user dir is empty
        if not any(user_dir.iterdir()) and self._seed_dir.exists():
            for nb in self._seed_dir.glob("*.py"):
                shutil.copy2(nb, user_dir / nb.name)

        port = self._allocate_port()
        container = self._client.containers.run(
            self._image,
            detach=True,
            ports={"2718/tcp": port},
            volumes={
                str((self._host_dir / session_id).resolve()): {"bind": "/notebooks", "mode": "rw"},
            },
            labels={"kitsune.session": session_id},
            name=f"kitsune-marimo-{session_id}",
            remove=True,
        )

        if not container or not container.id:
            raise RuntimeError("Failed to create sandbox container")

        info = ContainerInfo(
            container_id=container.id,
            session_id=session_id,
            host_port=port,
        )
        self._containers[session_id] = info
        await self._wait_until_ready(container, timeout=30)
        return info

    async def destroy(self, session_id: str) -> None:
        info = self._containers.pop(session_id, None)
        if info is None:
            return
        try:
            container = self._client.containers.get(info.container_id)
            container.stop(timeout=5)
        except NotFound:
            pass

    def get_info(self, session_id: str) -> ContainerInfo | None:
        info = self._containers.get(session_id)
        if info:
            info.touch()
        return info

    def get_user_dir(self, session_id: str) -> Path:
        return self._data_dir / session_id

    async def exec_in_container(self, session_id: str, command: list[str]) -> str:
        """Run a command inside the user's container, return stdout."""
        info = self._containers.get(session_id)
        if info is None:
            raise RuntimeError(f"No container for session {session_id}")
        info.touch()
        container = self._client.containers.get(info.container_id)
        exit_code, output = container.exec_run(command)
        text = output.decode("utf-8", errors="replace")
        if exit_code != 0:
            raise RuntimeError(f"Command exited {exit_code}: {text}")
        return text

    # -- internal --

    async def _wait_until_ready(self, container, timeout: int = 30) -> None:
        """Poll the container until marimo is accepting connections."""
        import httpx

        port = container.ports.get("2718/tcp")
        if port:
            host_port = port[0]["HostPort"]
        else:
            host_port = None

        if not host_port:
            # Fallback: just wait a fixed interval
            await asyncio.sleep(3)
            return

        url = f"http://localhost:{host_port}/api/status"
        async with httpx.AsyncClient() as client:
            deadline = time.time() + timeout
            while time.time() < deadline:
                try:
                    resp = await client.get(url, timeout=2)
                    if resp.status_code < 500:
                        return
                except (httpx.ConnectError, httpx.ReadTimeout):
                    pass
                await asyncio.sleep(0.5)
        raise RuntimeError(f"Marimo container not ready after {timeout}s")

    def _allocate_port(self) -> int:
        used = {info.host_port for info in self._containers.values()}
        for port in range(self._port_start, self._port_end):
            if port not in used:
                return port
        raise RuntimeError("No available ports in sandbox range")

    async def _cleanup_loop(self) -> None:
        while True:
            await asyncio.sleep(300)  # every 5 minutes
            await self._cleanup_stale()

    async def _cleanup_stale(self) -> None:
        now = time.time()
        cutoff = now - (self._timeout * 60)
        stale = [
            sid for sid, info in self._containers.items()
            if info.last_activity < cutoff
        ]
        for sid in stale:
            await self.destroy(sid)
