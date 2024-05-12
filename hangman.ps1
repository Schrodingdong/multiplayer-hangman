# Function to check if ngrok is installed
function Check-NgrokInstalled {
    if (-not (Test-Path (Join-Path $env:ProgramFiles "ngrok\ngrok.exe"))) {
        return $false
    }
    return $true
}

# Prompt the user to select between two choices
$choice = Read-Host "Select an option (1 or 2):
1. Host
2. Player
?> " 

# Validate the user input
if ($choice -eq "1") {
    # start ngrok in a new terminal window
    Start-Process -FilePath "cmd.exe" -ArgumentList "/c ngrok http 8000"
}

# start application
python .\python_impl\src\main.py

# Install pip dependencies
pip install -r ./requirements.txt
