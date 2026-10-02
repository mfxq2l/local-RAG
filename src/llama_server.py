"""llama-server 子进程的通用生命周期管理。

embedding 服务和生成式 chat 服务都需要：

    拉起 llama-server.exe
        ↓
    等待 /health 就绪
        ↓
    暴露一个 httpx.Client 供调用
        ↓
    进程退出时自动清理

这段逻辑此前只存在于 ``src/embedding/base.py``，新增 chat provider 后会被
用到两次，因此抽出为本模块，两处共用。

设计约定
--------
* **端口已被占用时假定外部已经起好了服务**，只连接、不接管、不结束它。
  这让用户可以手动 ``llama-server ... --port 8080`` 复用同一份模型。
* 子进程 stdout/stderr 落盘到 ``data/logs/llama_<name>_<port>.log``，便于排错。
* ``trust_env=False``：绕过系统/环境代理，确保到 127.0.0.1 的请求不被代理拦截。
* 所有实例注册到模块级列表，解释器退出时统一 stop。
"""

from __future__ import annotations

import atexit
import socket
import subprocess
import sys
import threading
import time
from pathlib import Path

import httpx

from src.config import DATA_DIR, LLAMA_CPP_DIR


# 进程内所有受管的 llama-server 实例
_instances: list["LlamaServerProcess"] = []
_registry_lock = threading.Lock()


def is_port_in_use(port: int, host: str = "127.0.0.1") -> bool:
    """探测端口是否已被监听。"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.3)
        return sock.connect_ex((host, port)) == 0


def stop_all() -> None:
    """停止本进程管理的全部 llama-server 子进程。"""
    with _registry_lock:
        instances = list(_instances)
        _instances.clear()

    for instance in instances:
        instance.stop()


atexit.register(stop_all)


class LlamaServerProcess:
    """管理单个 llama-server 子进程。

    只负责「进程 + 健康检查 + HTTP 客户端」，
    具体业务（embedding / chat）由上层封装。
    """

    def __init__(
        self,
        name: str,
        port: int,
        model_path: Path,
        extra_args: list[str] | None = None,
        *,
        exe_dir: Path | None = None,
        executable: str = "llama-server.exe",
        health_timeout: float = 600.0,
        request_timeout: float = 180.0,
    ) -> None:
        self.name = name
        self.port = port
        self.model_path = Path(model_path)
        self.extra_args = list(extra_args or [])

        self.exe_dir = Path(exe_dir or LLAMA_CPP_DIR)
        self.executable = executable

        self.health_timeout = health_timeout
        self._request_timeout = request_timeout

        self._process: subprocess.Popen | None = None
        self._client: httpx.Client | None = None
        self._log_handle = None
        self._ready = False
        self._owns_process = False   # 端口已被占用时为 False

        with _registry_lock:
            _instances.append(self)

    # ------------------------------------------------------------------
    # 属性
    # ------------------------------------------------------------------

    @property
    def base_url(self) -> str:
        return f"http://127.0.0.1:{self.port}"

    @property
    def ready(self) -> bool:
        return self._ready

    @property
    def log_path(self) -> Path:
        return DATA_DIR / "logs" / f"llama_{self.name}_{self.port}.log"

    @property
    def client(self) -> httpx.Client:
        """返回已就绪的 HTTP 客户端（会自动确保服务已启动）。"""
        self.start()
        assert self._client is not None
        return self._client

    # ------------------------------------------------------------------
    # 命令行
    # ------------------------------------------------------------------

    def _executable_path(self) -> Path:
        exe = self.exe_dir / self.executable
        if not exe.exists():
            raise FileNotFoundError(
                f"找不到 {self.executable}: {exe}\n"
                f"请确认 runtime/llama.cpp 已解压。"
            )
        return exe

    def build_command(self) -> list[str]:
        """构造完整命令行。"""
        return [str(self._executable_path()), *self.extra_args]

    # ------------------------------------------------------------------
    # 启动 / 停止
    # ------------------------------------------------------------------

    def start(self, timeout: float | None = None) -> None:
        """确保服务已启动并就绪（幂等）。"""
        if self._ready:
            return

        timeout = timeout if timeout is not None else self.health_timeout

        if not self.model_path.exists():
            raise FileNotFoundError(f"模型不存在: {self.model_path}")

        if not is_port_in_use(self.port):
            self._spawn()
            self._owns_process = True

        self._client = httpx.Client(
            timeout=self._request_timeout,
            trust_env=False,
        )

        self._wait_ready(timeout)

    def _spawn(self) -> None:
        cmd = self.build_command()

        creationflags = 0
        if sys.platform == "win32":
            creationflags = subprocess.CREATE_NO_WINDOW  # type: ignore[attr-defined]

        print(f"[llama] 启动 {self.name} @ {self.base_url}")
        print(f"[llama] 命令: {' '.join(cmd)}")

        log_file = self.log_path
        log_file.parent.mkdir(parents=True, exist_ok=True)

        handle = log_file.open("a", encoding="utf-8", errors="replace")
        handle.write(
            f"\n===== {time.strftime('%Y-%m-%d %H:%M:%S')} 启动 =====\n"
        )
        handle.flush()
        self._log_handle = handle

        self._process = subprocess.Popen(
            cmd,
            cwd=str(self.exe_dir),
            stdout=handle,
            stderr=handle,
            creationflags=creationflags,
        )

    def _wait_ready(self, timeout: float) -> None:
        deadline = time.time() + timeout
        last_error: Exception | None = None

        while time.time() < deadline:
            try:
                response = self._client.get(f"{self.base_url}/health")
                if response.status_code == 200:
                    self._ready = True
                    print(f"[llama] {self.name} 就绪")
                    return
            except Exception as exc:  # noqa: BLE001
                last_error = exc

            # 自己拉起的进程提前退出 → 立刻失败，不要白等
            if (
                self._owns_process
                and self._process is not None
                and self._process.poll() is not None
            ):
                raise RuntimeError(
                    f"{self.name} 启动失败，llama-server 提前退出，返回码 "
                    f"{self._process.returncode}\n"
                    f"完整日志见: {self.log_path}"
                )

            time.sleep(1.0)

        raise TimeoutError(
            f"等待 {self.name} 就绪超时（{timeout}s）。最后错误: {last_error}"
        )

    def stop(self) -> None:
        """停止服务并释放资源。外部接管的端口不会被杀进程。"""
        if self._client is not None:
            try:
                self._client.close()
            except Exception:  # noqa: BLE001
                pass
            self._client = None

        if self._log_handle is not None:
            try:
                self._log_handle.flush()
                self._log_handle.close()
            except Exception:  # noqa: BLE001
                pass
            self._log_handle = None

        if self._process is not None and self._owns_process:
            try:
                self._process.terminate()
                self._process.wait(timeout=10)
            except Exception:  # noqa: BLE001
                try:
                    self._process.kill()
                except Exception:  # noqa: BLE001
                    pass

        self._process = None
        self._owns_process = False
        self._ready = False


__all__ = [
    "LlamaServerProcess",
    "is_port_in_use",
    "stop_all",
]
