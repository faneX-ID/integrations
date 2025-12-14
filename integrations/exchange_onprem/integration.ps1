#requires -Version 7.0
# Exchange On-Premises Integration for faneX-ID
# Uses Exchange Management Shell for native Exchange operations

param(
    [Parameter(Mandatory = $true)]
    [string]$Action,

    [Parameter(Mandatory = $false)]
    [hashtable]$Data = @{},

    [Parameter(Mandatory = $false)]
    [hashtable]$Config = @{}
)

# Import Exchange Management Shell
# Note: For Exchange OnPrem, this requires Exchange Management Shell to be installed on the server
# For remote connections, use Exchange Web Services or Exchange Online Management module

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

# Connect to Exchange (OnPrem or Online)
function Connect-Exchange {
    $serverUrl = $Config.server_url
    $username = $Config.username
    $password = $Config.password

    if (-not $username -or -not $password) {
        throw "Exchange credentials not configured"
    }

    $securePassword = ConvertTo-SecureString $password -AsPlainText -Force
    $credentials = New-Object System.Management.Automation.PSCredential($username, $securePassword)

    # For Exchange OnPrem, use Exchange Management Shell
    # For Exchange Online, use ExchangeOnlineManagement module
    if ($serverUrl -like "*outlook.office365.com*" -or $serverUrl -like "*outlook.office.com*") {
        # Exchange Online
        try {
            Import-Module ExchangeOnlineManagement -ErrorAction Stop
            Connect-ExchangeOnline -Credential $credentials -ShowProgress $false -ErrorAction Stop
            return $true
        }
        catch {
            throw "Failed to connect to Exchange Online: $_"
        }
    }
    else {
        # Exchange OnPrem - requires Exchange Management Shell
        # This typically needs to run on Exchange server or with Exchange Management Tools installed
        try {
            $session = New-PSSession -ConfigurationName Microsoft.Exchange -ConnectionUri $serverUrl -Credential $credentials -Authentication Kerberos -ErrorAction Stop
            Import-PSSession $session -DisableNameChecking -ErrorAction Stop
            return $true
        }
        catch {
            throw "Failed to connect to Exchange OnPrem. Ensure Exchange Management Shell is available: $_"
        }
    }
}

try {
    Connect-Exchange

    switch ($Action) {
        "send_email" {
            if ($null -eq $Data.to) {
                $to = @()
            }
            else {
                $to = $Data.to
            }
            if ($null -eq $Data.subject) {
                $subject = ""
            }
            else {
                $subject = $Data.subject
            }
            if ($null -eq $Data.body) {
                $body = ""
            }
            else {
                $body = $Data.body
            }
            if ($null -eq $Data.cc) {
                $cc = @()
            }
            else {
                $cc = $Data.cc
            }
            if ($null -eq $Data.from) {
                if ($null -eq $Config.default_from) {
                    $from = $null
                }
                else {
                    $from = $Config.default_from
                }
            }
            else {
                $from = $Data.from
            }

            if (-not $to -or $to.Count -eq 0) {
                throw "to recipients required"
            }

            $mailParams = @{
                To         = $to
                Subject    = $subject
                Body       = $body
                BodyAsHtml = $true
            }

            if ($from) {
                $mailParams.From = $from
            }

            if ($cc -and $cc.Count -gt 0) {
                $mailParams.Cc = $cc
            }

            Send-MailMessage @mailParams -ErrorAction Stop

            $result = @{
                message = "Email sent"
            }
            Write-Output (ConvertTo-Result -Result $result)
        }

        "get_mailbox" {
            $email = $Data.email
            if (-not $email) {
                throw "email required"
            }

            $mailbox = Get-Mailbox -Identity $email -ErrorAction Stop
            $stats = Get-MailboxStatistics -Identity $email -ErrorAction Stop

            $result = @{
                email        = $mailbox.PrimarySmtpAddress
                display_name = $mailbox.DisplayName
                total_items  = $stats.ItemCount
                total_size   = $stats.TotalItemSize.Value
            }
            Write-Output (ConvertTo-Result -Result $result)
        }

        "create_calendar_event" {
            if ($null -eq $Data.subject) {
                $subject = ""
            }
            else {
                $subject = $Data.subject
            }
            $start = $Data.start
            $end = $Data.end
            if ($null -eq $Data.attendees) {
                $attendees = @()
            }
            else {
                $attendees = $Data.attendees
            }
            if ($null -eq $Data.organizer) {
                if ($null -eq $Config.username) {
                    $organizer = $null
                }
                else {
                    $organizer = $Config.username
                }
            }
            else {
                $organizer = $Data.organizer
            }

            if (-not $start -or -not $end) {
                throw "start and end required"
            }

            # Convert ISO datetime strings to DateTime
            $startDate = [DateTime]::Parse($start)
            $endDate = [DateTime]::Parse($end)

            # Create calendar event using EWS or Exchange cmdlets
            # Note: Full calendar management requires EWS or Exchange Web Services
            # This is a simplified version using basic Exchange cmdlets

            $result = @{
                message = "Calendar event creation requires EWS or Exchange Web Services API"
                note    = "For full calendar management, use Exchange Web Services or Microsoft Graph"
            }
            Write-Output (ConvertTo-Result -Result $result)
        }

        "get_calendar_events" {
            $startDateStr = $Data.start_date
            $endDateStr = $Data.end_date
            if ($null -eq $Data.email) {
                if ($null -eq $Config.username) {
                    $email = $null
                }
                else {
                    $email = $Config.username
                }
            }
            else {
                $email = $Data.email
            }

            if (-not $startDateStr -or -not $endDateStr) {
                throw "start_date and end_date required"
            }

            $startDate = [DateTime]::Parse($startDateStr)
            $endDate = [DateTime]::Parse($endDateStr)

            # Calendar access requires EWS or Exchange Web Services
            $result = @{
                message = "Calendar event retrieval requires EWS or Exchange Web Services API"
                note    = "For full calendar management, use Exchange Web Services or Microsoft Graph"
            }
            Write-Output (ConvertTo-Result -Result $result)
        }

        default {
            throw "Unknown action: $Action"
        }
    }

    # Disconnect if using Exchange Online
    if ($Config.server_url -like "*outlook.office365.com*" -or $Config.server_url -like "*outlook.office.com*") {
        Disconnect-ExchangeOnline -Confirm:$false -ErrorAction SilentlyContinue
    }
}
catch {
    Write-Output (ConvertTo-Result -Success $false -Error $_.Exception.Message)
    exit 1
}



