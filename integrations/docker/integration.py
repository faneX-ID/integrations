"""
Docker Integration for faneX-ID.
Docker integration for managing containers and images on remote Docker hosts.
"""

import logging
from typing import Any, Dict, Optional

import docker
from services.integration_base import Integration
from services.service_registry import service_registry

logger = logging.getLogger(__name__)


class DockerIntegration(Integration):
    """Docker integration for container management."""

    def __init__(
        self, core=None, config: Dict[str, Any] = None, manifest: Dict[str, Any] = None
    ):
        super().__init__(core, config, manifest)
        self._default_timeout = 60
        self._clients: Dict[str, docker.DockerClient] = {}

    async def async_setup(self) -> bool:
        """Set up the Docker integration and register services."""
        self.logger.info("Setting up Docker Integration")

        # Load configuration
        self._default_timeout = int(self.config.get("default_timeout", 60))

        # Register services
        self.register_service(
            "list_containers",
            self.list_containers,
            schema={
                "host": {"type": "string"},
                "all": {"type": "boolean", "default": False},
            },
            description="List containers on a Docker host",
        )

        self.register_service(
            "start_container",
            self.start_container,
            schema={
                "host": {"type": "string"},
                "container_id": {"type": "string"},
            },
            description="Start a container",
        )

        self.register_service(
            "stop_container",
            self.stop_container,
            schema={
                "host": {"type": "string"},
                "container_id": {"type": "string"},
                "timeout": {"type": "integer", "nullable": True},
            },
            description="Stop a container",
        )

        self.register_service(
            "restart_container",
            self.restart_container,
            schema={
                "host": {"type": "string"},
                "container_id": {"type": "string"},
                "timeout": {"type": "integer", "nullable": True},
            },
            description="Restart a container",
        )

        self.register_service(
            "get_container_stats",
            self.get_container_stats,
            schema={
                "host": {"type": "string"},
                "container_id": {"type": "string"},
            },
            description="Get container statistics",
        )

        self.register_service(
            "get_container_logs",
            self.get_container_logs,
            schema={
                "host": {"type": "string"},
                "container_id": {"type": "string"},
                "tail": {"type": "integer", "default": 100},
                "since": {"type": "string", "nullable": True},
            },
            description="Get container logs",
        )

        return True

    def _get_client(self, host: str) -> docker.DockerClient:
        """Get or create a Docker client for a host."""
        if host not in self._clients:
            # Determine base_url
            if host.startswith("unix://") or host.startswith("tcp://") or host.startswith("http://") or host.startswith("https://"):
                base_url = host
            elif host == "local" or host == "localhost":
                base_url = "unix:///var/run/docker.sock"
            else:
                # Assume TCP connection
                if ":" in host:
                    base_url = f"tcp://{host}"
                else:
                    base_url = f"tcp://{host}:2375"

            try:
                self._clients[host] = docker.DockerClient(base_url=base_url, timeout=self._default_timeout)
            except Exception as e:
                self.logger.error(f"Failed to create Docker client for {host}: {e}")
                raise

        return self._clients[host]

    def list_containers(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """List containers on a Docker host."""
        host = data.get("host", "local")
        show_all = data.get("all", False)

        try:
            client = self._get_client(host)
            containers = client.containers.list(all=show_all)

            container_list = []
            for container in containers:
                container_list.append(
                    {
                        "id": container.id,
                        "name": container.name,
                        "status": container.status,
                        "image": container.image.tags[0] if container.image.tags else "unknown",
                    }
                )

            return {"success": True, "containers": container_list, "count": len(container_list)}
        except Exception as e:
            self.logger.error(f"Failed to list containers on {host}: {e}")
            return {"success": False, "error": str(e)}

    def start_container(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Start a container."""
        host = data.get("host", "local")
        container_id = data.get("container_id")

        if not container_id:
            return {"success": False, "error": "container_id is required"}

        try:
            client = self._get_client(host)
            container = client.containers.get(container_id)
            container.start()

            return {"success": True, "message": f"Container {container_id} started"}
        except docker.errors.NotFound:
            return {"success": False, "error": f"Container {container_id} not found"}
        except Exception as e:
            self.logger.error(f"Failed to start container {container_id} on {host}: {e}")
            return {"success": False, "error": str(e)}

    def stop_container(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Stop a container."""
        host = data.get("host", "local")
        container_id = data.get("container_id")
        timeout = data.get("timeout")

        if not container_id:
            return {"success": False, "error": "container_id is required"}

        try:
            client = self._get_client(host)
            container = client.containers.get(container_id)
            container.stop(timeout=timeout)

            return {"success": True, "message": f"Container {container_id} stopped"}
        except docker.errors.NotFound:
            return {"success": False, "error": f"Container {container_id} not found"}
        except Exception as e:
            self.logger.error(f"Failed to stop container {container_id} on {host}: {e}")
            return {"success": False, "error": str(e)}

    def restart_container(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Restart a container."""
        host = data.get("host", "local")
        container_id = data.get("container_id")
        timeout = data.get("timeout")

        if not container_id:
            return {"success": False, "error": "container_id is required"}

        try:
            client = self._get_client(host)
            container = client.containers.get(container_id)
            container.restart(timeout=timeout)

            return {"success": True, "message": f"Container {container_id} restarted"}
        except docker.errors.NotFound:
            return {"success": False, "error": f"Container {container_id} not found"}
        except Exception as e:
            self.logger.error(f"Failed to restart container {container_id} on {host}: {e}")
            return {"success": False, "error": str(e)}

    def get_container_stats(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Get container statistics."""
        host = data.get("host", "local")
        container_id = data.get("container_id")

        if not container_id:
            return {"success": False, "error": "container_id is required"}

        try:
            client = self._get_client(host)
            container = client.containers.get(container_id)
            stats = container.stats(stream=False)

            return {
                "success": True,
                "container_id": container_id,
                "stats": {
                    "cpu_percent": stats.get("cpu_stats", {}).get("cpu_usage", {}).get("total_usage", 0),
                    "memory_usage": stats.get("memory_stats", {}).get("usage", 0),
                    "memory_limit": stats.get("memory_stats", {}).get("limit", 0),
                    "network_rx": stats.get("networks", {}).get("eth0", {}).get("rx_bytes", 0) if stats.get("networks") else 0,
                    "network_tx": stats.get("networks", {}).get("eth0", {}).get("tx_bytes", 0) if stats.get("networks") else 0,
                },
            }
        except docker.errors.NotFound:
            return {"success": False, "error": f"Container {container_id} not found"}
        except Exception as e:
            self.logger.error(f"Failed to get stats for container {container_id} on {host}: {e}")
            return {"success": False, "error": str(e)}

    def get_container_logs(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Get container logs."""
        host = data.get("host", "local")
        container_id = data.get("container_id")
        tail = data.get("tail", 100)
        since = data.get("since")

        if not container_id:
            return {"success": False, "error": "container_id is required"}

        try:
            client = self._get_client(host)
            container = client.containers.get(container_id)
            logs = container.logs(tail=tail, since=since, timestamps=True).decode("utf-8")

            return {
                "success": True,
                "container_id": container_id,
                "logs": logs.split("\n") if logs else [],
            }
        except docker.errors.NotFound:
            return {"success": False, "error": f"Container {container_id} not found"}
        except Exception as e:
            self.logger.error(f"Failed to get logs for container {container_id} on {host}: {e}")
            return {"success": False, "error": str(e)}


