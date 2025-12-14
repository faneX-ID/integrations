# Wiki.js Integration

Integration with Wiki.js API for managing content, users, and pages.

## Features

- Create and manage pages
- Search pages
- Update page content
- Full Wiki.js REST API support

## Requirements

- `requests>=2.28.0` - HTTP library

## Configuration

### Connection Parameters

- **server_url**: Base URL of your Wiki.js instance
- **api_token**: Wiki.js API token (generate in Wiki.js admin panel)

## Usage

### Create Page

```python
await service_registry.call("wiki_js.create_page", {
    "title": "Employee Handbook",
    "content": "# Employee Handbook\n\nWelcome to our company...",
    "path": "/handbook",
    "description": "Company employee handbook"
})
```

### Get Page

```python
await service_registry.call("wiki_js.get_page", {
    "page_id": 123
})
```

### Search Pages

```python
await service_registry.call("wiki_js.search_pages", {
    "query": "onboarding",
    "limit": 20
})
```

## Notes

- Requires Wiki.js API token (generate in Admin > API Access)
- Wiki.js is an open-source wiki platform
- Supports Markdown and other content formats

