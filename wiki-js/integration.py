from services.integration_base import Integration
from services.service_registry import service_registry
import logging
import requests

class WikiJSIntegration(Integration):
    async def async_setup(self):
        self.logger.info("Setting up Wiki.js Integration")

        service_registry.register(
            domain=self.domain,
            service="create_page",
            service_func=self.create_page,
            schema={
                "title": str,
                "content": str,
                "path": str,
                "description": str
            },
            description="Create a new page"
        )

        service_registry.register(
            domain=self.domain,
            service="get_page",
            service_func=self.get_page,
            schema={"page_id": int},
            description="Get a page"
        )

        service_registry.register(
            domain=self.domain,
            service="update_page",
            service_func=self.update_page,
            schema={"page_id": int, "content": str, "title": str},
            description="Update a page"
        )

        service_registry.register(
            domain=self.domain,
            service="search_pages",
            service_func=self.search_pages,
            schema={"query": str, "limit": int},
            description="Search for pages"
        )

        return True

    def _get_headers(self):
        """Get API headers."""
        api_token = self.config.get("api_token")
        if not api_token:
            raise ValueError("Wiki.js API token not configured")
        return {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }

    def _get_base_url(self):
        """Get base Wiki.js URL."""
        url = self.config.get("server_url", "").rstrip("/")
        if not url:
            raise ValueError("Wiki.js server URL not configured")
        return url

    async def create_page(self, data: dict):
        """Create a new page."""
        base_url = self._get_base_url()
        title = data.get("title", "")
        content = data.get("content", "")
        path = data.get("path", "")
        description = data.get("description")

        page_data = {
            "title": title,
            "content": content,
            "path": path,
            "description": description
        }

        try:
            response = requests.post(
                f"{base_url}/api/pages",
                json=page_data,
                headers=self._get_headers(),
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            page_id = result.get("id")
            self.logger.info(f"Wiki.js page created: {page_id}")
            return {"success": True, "page_id": page_id, "path": result.get("path")}
        except Exception as e:
            self.logger.error(f"Failed to create Wiki.js page: {e}")
            raise

    async def get_page(self, data: dict):
        """Get a page."""
        base_url = self._get_base_url()
        page_id = data.get("page_id")
        if not page_id:
            raise ValueError("page_id required")

        try:
            response = requests.get(
                f"{base_url}/api/pages/{page_id}",
                headers=self._get_headers(),
                timeout=30
            )
            response.raise_for_status()
            return {"success": True, "page": response.json()}
        except Exception as e:
            self.logger.error(f"Failed to get Wiki.js page: {e}")
            raise

    async def update_page(self, data: dict):
        """Update a page."""
        base_url = self._get_base_url()
        page_id = data.get("page_id")
        content = data.get("content", "")
        title = data.get("title")

        if not page_id:
            raise ValueError("page_id required")

        update_data = {"content": content}
        if title:
            update_data["title"] = title

        try:
            response = requests.put(
                f"{base_url}/api/pages/{page_id}",
                json=update_data,
                headers=self._get_headers(),
                timeout=30
            )
            response.raise_for_status()
            self.logger.info(f"Wiki.js page updated: {page_id}")
            return {"success": True, "page_id": page_id}
        except Exception as e:
            self.logger.error(f"Failed to update Wiki.js page: {e}")
            raise

    async def search_pages(self, data: dict):
        """Search for pages."""
        base_url = self._get_base_url()
        query = data.get("query", "")
        limit = data.get("limit", 10)

        try:
            response = requests.get(
                f"{base_url}/api/search",
                params={"q": query, "limit": limit},
                headers=self._get_headers(),
                timeout=30
            )
            response.raise_for_status()
            results = response.json()
            return {"success": True, "count": len(results), "pages": results}
        except Exception as e:
            self.logger.error(f"Failed to search Wiki.js pages: {e}")
            raise


