# SharePoint On-Premises Integration

Integration with SharePoint On-Premises via REST API and CSOM (Client-Side Object Model).

## Features

- Get site and list information
- Create list items
- Upload files to document libraries
- Manage permissions (requires CSOM for full functionality)

## Requirements

- PowerShell with SharePointPnPPowerShellOnline module
- Install via: `Install-Module SharePointPnPPowerShellOnline`
- For OnPrem: SharePoint PnP PowerShell module

## Configuration

### Connection Parameters

- **server_url**: Base URL of SharePoint server
- **username**: SharePoint username (domain\\username)
- **password**: SharePoint password
- **default_site**: Default SharePoint site URL (optional)

## Usage

### Get Site

```python
await service_registry.call("sharepoint_onprem.get_site", {
    "site_url": "https://sharepoint.example.com/sites/mysite"
})
```

### Create List Item

```python
await service_registry.call("sharepoint_onprem.create_list_item", {
    "site_url": "https://sharepoint.example.com/sites/mysite",
    "list_name": "Employees",
    "fields": {
        "Title": "John Doe",
        "Email": "john.doe@example.com"
    }
})
```

### Upload File

```python
await service_registry.call("sharepoint_onprem.upload_file", {
    "site_url": "https://sharepoint.example.com/sites/mysite",
    "library_name": "Documents",
    "file_path": "report.pdf",
    "file_content": "<base64_encoded_content>"
})
```

## Notes

- Uses NTLM authentication for on-premises SharePoint
- Full permission management requires CSOM implementation
- REST API has limitations compared to CSOM for complex operations
