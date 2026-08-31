#Requires -RunAsAdministrator
$ErrorActionPreference = 'Stop'

foreach ($ruleName in @('BedrockParty LAN Proxy UDP')) {
    $existing = Get-NetFirewallRule -DisplayName $ruleName -ErrorAction SilentlyContinue
    if ($existing) {
        $existing | Remove-NetFirewallRule
        Write-Host "Rule removed: $ruleName"
    }
}
