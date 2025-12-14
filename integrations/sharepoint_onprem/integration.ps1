#requires -Version 7.0
# SharePoint On-Premises Integration for faneX-ID
# Uses SharePoint PnP PowerShell for native SharePoint operations

param(
    [Parameter(Mandatory = $true)]
    [string]$Action,

    [Parameter(Mandatory = $false)]
    [hashtable]$Data = @{},

    [Parameter(Mandatory = $false)]
    [hashtable]$Config = @{}
)

# Import SharePoint PnP module
try {
    Import-Module SharePointPnPPowerShellOnline -ErrorAction Stop
}
catch {
    Write-Error "SharePointPnPPowerShellOnline module not available. Please install: Install-Module SharePointPnPPowerShellOnline"
    exit 1
}

# Connect to SharePoint
function Connect-SharePointSite {
    param([string]$SiteUrl)

    $username = $Config.username
    $password = $Config.password

    if (-not $username -or -not $password) {
        throw "SharePoint credentials not configured"
    }

    $securePassword = ConvertTo-SecureString $password -AsPlainText -Force
    $credentials = New-Object System.Management.Automation.PSCredential($username, $securePassword)

    try {
        Connect-PnPOnline -Url $SiteUrl -Credentials $credentials -ErrorAction Stop
        return $true
    }
    catch {
        throw "Failed to connect to SharePoint: $_"
    }
}

# Convert result to JSON
function ConvertTo-Result {
    param([object]$Result, [bool]$Success = $true, [string]$Error = "")

    $output = @{
        success = $Success
    }

    if ($Success) {
        if ($Result) {
            $output.result = $Result
        }
    }
    else {
        $output.error = $Error
    }

    return $output | ConvertTo-Json -Depth 10
}

try {
    if ($null -ne $Data.site_url) {
        $siteUrl = $Data.site_url
    }
    elseif ($null -ne $Config.default_site) {
        $siteUrl = $Config.default_site
    }
    elseif ($null -ne $Config.server_url) {
        $siteUrl = $Config.server_url
    }
    else {
        $siteUrl = $null
    }

    if (-not $siteUrl) {
        throw "site_url or default_site required"
    }

    Connect-SharePointSite -SiteUrl $siteUrl

    switch ($Action) {
        "get_site" {
            $web = Get-PnPWeb
            $result = @{
                title       = $web.Title
                url         = $web.Url
                description = $web.Description
            }
            Write-Output (ConvertTo-Result -Result $result)
        }

        "get_list" {
            $listName = $Data.list_name
            if (-not $listName) {
                throw "list_name required"
            }

            $list = Get-PnPList -Identity $listName -ErrorAction Stop
            $result = @{
                title      = $list.Title
                item_count = $list.ItemCount
                id         = $list.Id
            }
            Write-Output (ConvertTo-Result -Result $result)
        }

        "create_list_item" {
            $listName = $Data.list_name
            if ($null -eq $Data.fields) {
                $fields = @{}
            }
            else {
                $fields = $Data.fields
            }

            if (-not $listName) {
                throw "list_name required"
            }

            $item = Add-PnPListItem -List $listName -Values $fields -ErrorAction Stop
            $result = @{
                id      = $item.Id
                message = "List item created"
            }
            Write-Output (ConvertTo-Result -Result $result)
        }

        "upload_file" {
            $libraryName = $Data.library_name
            $filePath = $Data.file_path
            $fileContent = $Data.file_content

            if (-not $libraryName -or -not $filePath -or -not $fileContent) {
                throw "library_name, file_path, and file_content required"
            }

            # Decode base64 content
            try {
                $bytes = [Convert]::FromBase64String($fileContent)
            }
            catch {
                $bytes = [System.Text.Encoding]::UTF8.GetBytes($fileContent)
            }

            $tempFile = [System.IO.Path]::GetTempFileName()
            [System.IO.File]::WriteAllBytes($tempFile, $bytes)

            try {
                Add-PnPFile -Path $tempFile -Folder $libraryName -NewFileName $filePath -ErrorAction Stop
                $result = @{
                    path    = $filePath
                    message = "File uploaded"
                }
                Write-Output (ConvertTo-Result -Result $result)
            }
            finally {
                Remove-Item $tempFile -ErrorAction SilentlyContinue
            }
        }

        "set_permissions" {
            $itemPath = $Data.item_path
            $user = $Data.user
            $permissionLevel = $Data.permission_level

            if (-not $itemPath -or -not $user -or -not $permissionLevel) {
                throw "item_path, user, and permission_level required"
            }

            $file = Get-PnPFile -Url $itemPath -ErrorAction Stop
            Set-PnPListItemPermission -List $file.ListItemAllFields["ListId"] -Identity $file.ListItemAllFields.Id -User $user -AddRole $permissionLevel -ErrorAction Stop

            $result = @{
                message = "Permissions set"
            }
            Write-Output (ConvertTo-Result -Result $result)
        }

        default {
            throw "Unknown action: $Action"
        }
    }

    Disconnect-PnPOnline
}
catch {
    Write-Output (ConvertTo-Result -Success $false -Error $_.Exception.Message)
    exit 1
}



