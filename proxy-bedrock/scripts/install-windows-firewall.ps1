#Requires -RunAsAdministrator
[CmdletBinding()]
param(
    [string]$LanSubnet = '192.168.1.0/24'
)

$ErrorActionPreference = 'Stop'
$ruleName = 'BedrockParty LAN Proxy UDP'
foreach ($name in @($ruleName)) {
    $existing = Get-NetFirewallRule -DisplayName $name -ErrorAction SilentlyContinue
    if ($existing) {
        $existing | Remove-NetFirewallRule
    }
}

New-NetFirewallRule `
    -DisplayName $ruleName `
    -Description 'Allows BedrockParty RakNet, discovery, and NetherNet WebRTC sessions only from the LAN.' `
    -Direction Inbound `
    -Action Allow `
    -Protocol UDP `
    -LocalPort 19132, 7551, 50000 `
    -RemoteAddress $LanSubnet `
    -Profile Public, Private

Write-Host "Rule created. Scope: UDP/19132, UDP/7551, and UDP/50000 from $LanSubnet on Public and Private profiles."
