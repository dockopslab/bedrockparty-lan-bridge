#Requires -RunAsAdministrator
param(
    [Parameter(Mandatory = $true)]
    [string]$PythonPath,

    [Parameter(Mandatory = $true)]
    [string]$InterfaceAddress,

    [Parameter(Mandatory = $true)]
    [string]$OutputPath,

    [double]$Duration = 30,

    [string[]]$TargetAddress = @(),

    [switch]$AllUdp
)

$ErrorActionPreference = 'Stop'
$captureScript = Join-Path $PSScriptRoot 'capture-bedrock-windows.py'

$captureArguments = @(
    $captureScript,
    '--interface', $InterfaceAddress,
    '--output', $OutputPath,
    '--duration', $Duration
)
foreach ($address in $TargetAddress) {
    $captureArguments += @('--ip', $address)
}
if ($AllUdp) {
    $captureArguments += '--all-udp'
}

& $PythonPath @captureArguments

exit $LASTEXITCODE
