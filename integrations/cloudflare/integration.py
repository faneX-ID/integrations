"""
Cloudflare Integration for faneX-ID
Provides DNS management and Cloudflare API functionality.
"""

import logging
from typing import Any, Dict, List, Optional

try:
    import CloudFlare
except ImportError:
    CloudFlare = None

from services.integration_base import Integration
from services.service_registry import service_registry

logger = logging.getLogger(__name__)


class CloudflareIntegration(Integration):
    """Cloudflare integration for DNS and zone management."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cf: Optional[Any] = None
        self._api_token: Optional[str] = None
        self._api_key: Optional[str] = None
        self._email: Optional[str] = None

    async def async_setup(self) -> bool:
        """Set up the Cloudflare integration."""
        self.logger.info("Setting up Cloudflare Integration")

        if CloudFlare is None:
            self.logger.error("cloudflare library not installed")
            return False

        # Get configuration
        self._api_token = self.config.get("api_token")
        self._api_key = self.config.get("api_key")
        self._email = self.config.get("email")

        if not self._api_token and not (self._api_key and self._email):
            self.logger.error("Cloudflare api_token or (api_key and email) is required")
            return False

        try:
            # Initialize Cloudflare client
            if self._api_token:
                self._cf = CloudFlare.CloudFlare(token=self._api_token)
            else:
                self._cf = CloudFlare.CloudFlare(email=self._email, key=self._api_key)

            # Test connection
            zones = self._cf.zones.get()
            self.logger.info(f"Cloudflare connected, found {len(zones)} zones")

            # Register services
            self.register_service(
                "list_zones",
                self.list_zones,
                schema={
                    "name": {"type": "string", "nullable": True},
                    "status": {"type": "string", "enum": ["active", "pending", "initializing", "moved", "deleted", "deactivated"], "nullable": True},
                },
                description="List all Cloudflare zones",
            )

            self.register_service(
                "get_zone",
                self.get_zone,
                schema={"zone_id": {"type": "string"}},
                description="Get details of a specific zone",
            )

            self.register_service(
                "list_dns_records",
                self.list_dns_records,
                schema={
                    "zone_id": {"type": "string"},
                    "type": {"type": "string", "enum": ["A", "AAAA", "CNAME", "MX", "TXT", "NS", "SRV", "CAA"], "nullable": True},
                    "name": {"type": "string", "nullable": True},
                },
                description="List DNS records for a zone",
            )

            self.register_service(
                "create_dns_record",
                self.create_dns_record,
                schema={
                    "zone_id": {"type": "string"},
                    "type": {"type": "string", "enum": ["A", "AAAA", "CNAME", "MX", "TXT", "NS", "SRV", "CAA"]},
                    "name": {"type": "string"},
                    "content": {"type": "string"},
                    "ttl": {"type": "integer", "default": 1},
                    "priority": {"type": "integer", "nullable": True},
                    "proxied": {"type": "boolean", "default": False},
                },
                description="Create a new DNS record",
            )

            self.register_service(
                "update_dns_record",
                self.update_dns_record,
                schema={
                    "zone_id": {"type": "string"},
                    "record_id": {"type": "string"},
                    "type": {"type": "string", "enum": ["A", "AAAA", "CNAME", "MX", "TXT", "NS", "SRV", "CAA"], "nullable": True},
                    "name": {"type": "string", "nullable": True},
                    "content": {"type": "string", "nullable": True},
                    "ttl": {"type": "integer", "nullable": True},
                    "proxied": {"type": "boolean", "nullable": True},
                },
                description="Update an existing DNS record",
            )

            self.register_service(
                "delete_dns_record",
                self.delete_dns_record,
                schema={
                    "zone_id": {"type": "string"},
                    "record_id": {"type": "string"},
                },
                description="Delete a DNS record",
            )

            self.register_service(
                "purge_cache",
                self.purge_cache,
                schema={
                    "zone_id": {"type": "string"},
                    "purge_everything": {"type": "boolean", "default": False},
                    "files": {"type": "array", "items": {"type": "string"}, "nullable": True},
                    "tags": {"type": "array", "items": {"type": "string"}, "nullable": True},
                },
                description="Purge Cloudflare cache for a zone",
            )

            return True
        except Exception as e:
            self.logger.error(f"Failed to set up Cloudflare integration: {e}")
            return False

    def list_zones(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """List all Cloudflare zones."""
        if not self._cf:
            return {"success": False, "error": "Cloudflare client not initialized"}

        try:
            zones = self._cf.zones.get()

            # Apply filters
            name_filter = data.get("name")
            status_filter = data.get("status")

            filtered_zones = zones
            if name_filter:
                filtered_zones = [z for z in filtered_zones if name_filter.lower() in z.get("name", "").lower()]
            if status_filter:
                filtered_zones = [z for z in filtered_zones if z.get("status") == status_filter]

            return {
                "success": True,
                "zones": filtered_zones,
                "count": len(filtered_zones)
            }
        except Exception as e:
            self.logger.error(f"Failed to list zones: {e}")
            return {"success": False, "error": str(e)}

    def get_zone(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Get details of a specific zone."""
        if not self._cf:
            return {"success": False, "error": "Cloudflare client not initialized"}

        zone_id = data.get("zone_id")
        if not zone_id:
            return {"success": False, "error": "zone_id is required"}

        try:
            zone = self._cf.zones.get(zone_id)
            return {"success": True, "zone": zone}
        except Exception as e:
            self.logger.error(f"Failed to get zone: {e}")
            return {"success": False, "error": str(e)}

    def list_dns_records(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """List DNS records for a zone."""
        if not self._cf:
            return {"success": False, "error": "Cloudflare client not initialized"}

        zone_id = data.get("zone_id")
        if not zone_id:
            return {"success": False, "error": "zone_id is required"}

        try:
            records = self._cf.zones.dns_records.get(zone_id)

            # Apply filters
            type_filter = data.get("type")
            name_filter = data.get("name")

            filtered_records = records
            if type_filter:
                filtered_records = [r for r in filtered_records if r.get("type") == type_filter]
            if name_filter:
                filtered_records = [r for r in filtered_records if name_filter.lower() in r.get("name", "").lower()]

            return {
                "success": True,
                "records": filtered_records,
                "count": len(filtered_records)
            }
        except Exception as e:
            self.logger.error(f"Failed to list DNS records: {e}")
            return {"success": False, "error": str(e)}

    def create_dns_record(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new DNS record."""
        if not self._cf:
            return {"success": False, "error": "Cloudflare client not initialized"}

        zone_id = data.get("zone_id")
        record_type = data.get("type")
        name = data.get("name")
        content = data.get("content")
        ttl = data.get("ttl", 1)
        priority = data.get("priority")
        proxied = data.get("proxied", False)

        if not all([zone_id, record_type, name, content]):
            return {"success": False, "error": "zone_id, type, name, and content are required"}

        try:
            record_data = {
                "type": record_type,
                "name": name,
                "content": content,
                "ttl": ttl,
                "proxied": proxied
            }

            if priority is not None:
                record_data["priority"] = priority

            record = self._cf.zones.dns_records.post(zone_id, data=record_data)
            return {"success": True, "record": record}
        except Exception as e:
            self.logger.error(f"Failed to create DNS record: {e}")
            return {"success": False, "error": str(e)}

    def update_dns_record(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing DNS record."""
        if not self._cf:
            return {"success": False, "error": "Cloudflare client not initialized"}

        zone_id = data.get("zone_id")
        record_id = data.get("record_id")

        if not zone_id or not record_id:
            return {"success": False, "error": "zone_id and record_id are required"}

        try:
            # Get existing record first
            existing = self._cf.zones.dns_records.get(zone_id, record_id)

            # Update only provided fields
            update_data = {}
            if "type" in data and data["type"]:
                update_data["type"] = data["type"]
            else:
                update_data["type"] = existing.get("type")

            if "name" in data and data["name"]:
                update_data["name"] = data["name"]
            else:
                update_data["name"] = existing.get("name")

            if "content" in data and data["content"]:
                update_data["content"] = data["content"]
            else:
                update_data["content"] = existing.get("content")

            if "ttl" in data and data["ttl"] is not None:
                update_data["ttl"] = data["ttl"]
            else:
                update_data["ttl"] = existing.get("ttl", 1)

            if "proxied" in data and data["proxied"] is not None:
                update_data["proxied"] = data["proxied"]
            else:
                update_data["proxied"] = existing.get("proxied", False)

            record = self._cf.zones.dns_records.put(zone_id, record_id, data=update_data)
            return {"success": True, "record": record}
        except Exception as e:
            self.logger.error(f"Failed to update DNS record: {e}")
            return {"success": False, "error": str(e)}

    def delete_dns_record(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a DNS record."""
        if not self._cf:
            return {"success": False, "error": "Cloudflare client not initialized"}

        zone_id = data.get("zone_id")
        record_id = data.get("record_id")

        if not zone_id or not record_id:
            return {"success": False, "error": "zone_id and record_id are required"}

        try:
            self._cf.zones.dns_records.delete(zone_id, record_id)
            return {"success": True, "message": "DNS record deleted"}
        except Exception as e:
            self.logger.error(f"Failed to delete DNS record: {e}")
            return {"success": False, "error": str(e)}

    def purge_cache(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Purge Cloudflare cache for a zone."""
        if not self._cf:
            return {"success": False, "error": "Cloudflare client not initialized"}

        zone_id = data.get("zone_id")
        if not zone_id:
            return {"success": False, "error": "zone_id is required"}

        try:
            purge_everything = data.get("purge_everything", False)
            files = data.get("files")
            tags = data.get("tags")

            if purge_everything:
                result = self._cf.zones.purge_cache.delete(zone_id, data={"purge_everything": True})
            else:
                purge_data = {}
                if files:
                    purge_data["files"] = files
                if tags:
                    purge_data["tags"] = tags

                if not purge_data:
                    return {"success": False, "error": "Must provide files, tags, or set purge_everything to true"}

                result = self._cf.zones.purge_cache.delete(zone_id, data=purge_data)

            return {"success": True, "result": result}
        except Exception as e:
            self.logger.error(f"Failed to purge cache: {e}")
            return {"success": False, "error": str(e)}
