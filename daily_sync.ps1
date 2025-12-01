# daily_sync.ps1
# This script is scheduled to run daily on the Data Logger PC.

# --- Configuration ---
$repoDir = "C:\Users\GROWTH\Desktop\visitor_counting"
$pythonScript = "consolidate_data.py"

# IMPORTANT: REPLACE THIS PLACEHOLDER with the path you found in Step 1 (e.g., C:\Program Files\Git\cmd\git.exe)
$gitPath = "C:\Program Files\Git\cmd\git.exe" 

# --- Execution ---

Write-Host "--- Starting Data Consolidation and Git Sync ---"
try {
    # Change directory
    Set-Location -Path $repoDir

    # 1. Run Python Consolidation
    Write-Host "Running Python script to update data.csv..."
    # The Python script handles TXT conversion and data.csv update
    & python $pythonScript
    Write-Host "Python execution complete."

    # 2. Check Git Executable Path
    if (-not (Test-Path $gitPath)) {
        Write-Host "FATAL ERROR: Git executable not found at specified path: $gitPath"
        exit 1
    }
    
    # Define a custom function to run Git using the full path
    function Run-Git {
        param([string]$ArgumentList)
        & $gitPath @ArgumentList
    }

    # 3. Git Operations
    
    # Stage the updated data.csv file
    Run-Git "add data.csv"
    
    # Check if there are any pending changes to commit
    $status = Run-Git "status --porcelain" | Out-String # Capture output for check

    if ($status -ne "") {
        # Changes detected, proceed with commit and push
        $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm"
        Write-Host "Changes detected. Committing data update..."
        
        # Commit the changes
        Run-Git "commit -m 'Automated Data Update: $timestamp'"
        
        # Push to GitHub
        Write-Host "Pushing changes to GitHub 'main' branch..."
        Run-Git "push origin main"
        
        Write-Host "SUCCESS: Data successfully pushed to GitHub at $timestamp."
    } else {
        Write-Host "No new data detected in data.csv. Skipping commit and push."
    }

} catch {
    Write-Host "CRITICAL FAILURE: An unhandled error occurred."
    $_.Exception | Write-Host
    exit 1
}

Write-Host "--- Sync Finished ---"
