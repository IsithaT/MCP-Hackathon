$claudePath = "C:\Users\colem\AppData\Local\AnthropicClaude\claude.exe"

# Get all processes named "claude"
$processes = Get-Process -Name "claude" -ErrorAction SilentlyContinue

foreach ($proc in $processes) {
    try {
        Write-Output "Killing process: $($proc.Name) (ID: $($proc.Id))"
        Stop-Process -Id $proc.Id -Force -ErrorAction Stop
        Start-Sleep -Milliseconds 300
    }
    catch {
        Write-Output "Process with ID $($proc.Id) already exited or could not be terminated."
    }
}

# Start the application again
if (Test-Path $claudePath) {
    Write-Output "Restarting Claude..."
    Start-Process $claudePath
}
else {
    Write-Output "Error: Claude executable not found at $claudePath"
}
