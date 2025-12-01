# daily_sync.ps1
# This script uses absolute paths to ensure reliable execution via Task Scheduler.

# --- Configuration & Paths ---
$repoDir = "C:\Users\GROWTH\Desktop\visitor_counting"
$pythonScript = "consolidate_data.py"

# !!! REPLACE THESE PATHS WITH THE ABSOLUTE PATHS FOUND IN STEP 1 !!!
$pythonPath = "C:\Users\GROWTH\AppData\Local\Programs\Python\Python39\python.exe"
$gitPath = "C:\Program Files\Git\cmd\git.exe" 

# --- Execution ---

Write-Host "--- Starting Data Consolidation and Git Sync ---"

try {
    # Change directory to the repository folder
    Set-Location -Path $repoDir
    
    # Define a custom function to run Git using the full path
    function Run-Git {
        param([string]$ArgumentList)
        & $gitPath @ArgumentList
    }

    # 1. Run Python Consolidation (Using Absolute Path)
    Write-Host "Running Python script to update data.csv..."
    # We use the full path to python.exe to execute the consolidation script
    & $pythonPath $pythonScript
    Write-Host "Python execution complete. data.csv should be updated."

    # 2. Git Operations (Using Run-Git function with Absolute Path)

    # Stage the updated data.csv file
    Run-Git "add data.csv"
    Write-Host "Staged data.csv."

    # Check if there are any pending changes to commit
    # We use the Run-Git function to check status
    $status = Run-Git "status --porcelain" | Out-String 

    if ($status -ne "") {
        # Changes detected, proceed with commit and push
        $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm"
        Write-Host "Committing changes..."
        
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
