# Generic Webhook Integration for faneX-ID (PowerShell implementation)

param(
    [Parameter(Mandatory=$true)]
    [string]$Action,

    [Parameter(Mandatory=$false)]
    [hashtable]$Data = @{},

    [Parameter(Mandatory=$false)]
    [hashtable]$Config = @{}
)

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
    } else {
        $output.error = $Error
    }

    return $output | ConvertTo-Json -Depth 10
}

try {
    switch ($Action) {
        "send_webhook" {
            $url = $Data.url ?? $Config.default_url
            $method = ($Data.method ?? "POST").ToUpper()
            $payload = $Data.payload ?? @{}
            $headers = $Data.headers ?? @{}
            $timeout = $Data.timeout ?? $Config.timeout ?? 30

            if (-not $url) {
                throw "webhook URL not provided and no default_url configured"
            }

            # Merge default headers
            $allHeaders = $Config.default_headers ?? @{}
            foreach ($key in $headers.Keys) {
                $allHeaders[$key] = $headers[$key]
            }

            # Set Content-Type if not specified
            if (-not $allHeaders.ContainsKey("Content-Type") -and $method -in @("POST", "PUT", "PATCH")) {
                $allHeaders["Content-Type"] = "application/json"
            }

            $params = @{
                Uri = $url
                Method = $method
                TimeoutSec = $timeout
            }

            if ($allHeaders.Count -gt 0) {
                $params.Headers = $allHeaders
            }

            if ($method -eq "GET") {
                $params.Body = ($payload | ConvertTo-Json -Compress)
            } else {
                $params.Body = ($payload | ConvertTo-Json -Depth 10)
            }

            $response = Invoke-WebRequest @params -ErrorAction Stop

            $result = @{
                status = "sent"
                status_code = $response.StatusCode
                response = if ($response.Content.Length -gt 500) { $response.Content.Substring(0, 500) } else { $response.Content }
            }

            Write-Output (ConvertTo-Result -Result $result)
        }

        default {
            throw "Unknown action: $Action"
        }
    }
} catch {
    Write-Output (ConvertTo-Result -Success $false -Error $_.Exception.Message)
    exit 1
}


