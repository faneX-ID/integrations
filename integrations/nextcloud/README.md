# Nextcloud Integration

Integration with Nextcloud file sharing and collaboration platform via WebDAV and REST API.

## Features

- Upload files to Nextcloud
- Create file shares
- Get user information
- Full Nextcloud OCS API support

## Requirements

- `requests>=2.28.0` - HTTP library

## Configuration

### Connection Parameters

- **server_url**: Base URL of your Nextcloud instance
- **username**: Nextcloud username
- **password**: Nextcloud password or app password

## Usage

### Upload File

```python
await service_registry.call("nextcloud.upload_file", {
    "remote_path": "Documents/report.pdf",
    "file_content": "<base64_encoded_content>"
})
```

### Create Share

```python
await service_registry.call("nextcloud.create_share", {
    "path": "Documents/report.pdf",
    "share_type": 3,
    "permissions": 1
})
```

## Notes

- Nextcloud is an open-source file sharing platform
- Uses WebDAV for file operations and OCS API for sharing
- App passwords are recommended for API access


