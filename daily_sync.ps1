# daily_sync.ps1
# This script is scheduled to run daily on the Data Logger PC.
# It chains the Python consolidation, Git commit, and Git push to GitHub.

# --- Configuration ---
# 1. Define the repository directory. This MUST match the folder path.
$repoDir = "C:\Users\GROWTH\Desktop\visitor_counting"
$pythonScript = "consolidate_data.py"

# 2. Change directory to the repository folder
Set-Location -Path $repoDir

Write-Host "--- Starting Data Consolidation and Git Sync ---"
Write-Host "Current Directory: $repoDir"

# --- Step 1: Run Python Consolidation ---
# This executes 'consolidate_data.py', which reads new TXT files,
# updates data.csv, and deletes the processed TXT files.
Write-Host "Running Python script to update data.csv..."
try {
    # The '&' operator executes the external program/script
    & python $pythonScript
} catch {
    Write-Host "ERROR: Python script failed. Check if Python is installed and in PATH."
    exit 1
}


# --- Step 2: Git Operations ---

# Stage the updated data.csv file for commit
git add data.csv
Write-Host "Staged data.csv."

# Check if there are any pending changes to commit (status --porcelain returns non-empty if changes exist)
$status = git status --parcelain

if ($status) {
    # Changes detected, proceed with commit and push
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm"
    Write-Host "Changes detected. Committing data update..."

    # Commit the changes
    git commit -m "Automated Data Update: $timestamp"

    # Push to GitHub (Relies on the PAT embedded in the remote URL you set up earlier)
    Write-Host "Pushing changes to GitHub 'main' branch..."
    try {
        git push origin main
        Write-Host "SUCCESS: Data successfully pushed to GitHub at $timestamp."
    } catch {
        Write-Host "FATAL ERROR: Git push failed. Check your network connection and the PAT in the remote URL."
        exit 1
    }
} else {
    Write-Host "No new data detected in data.csv. Skipping commit and push."
}

Write-Host "--- Sync Finished ---"