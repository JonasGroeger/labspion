$workon_home_env__var_name = "WORKON_HOME"
$venv_file_name = ".venv"

$workon_home = $null

# Test if env-var exists
if(!(Test-Path Env:\$workon_home_env__var_name)) {
    $Host.UI.WriteErrorLine("You must set the environment variable '" + $workon_home_env__var_name + "'. It must point to your virtual environment folder.")
    Exit
}

# Test if env-var points to a existing folder
if(!(Test-Path (Get-ChildItem Env:\$workon_home_env__var_name).Value)) {
    $Host.UI.WriteErrorLine("The the environment variable '" + $workon_home_env__var_name + "' does not point to an existing folder.")
    Exit
}

# Workon home is existing
$workon_home = (Get-ChildItem Env:\$workon_home_env__var_name).Value

# Test if venv file exists
if(!(Test-Path $venv_file_name)) {
    $Host.UI.WriteErrorLine("You must have a file named '.venv' in this folder. It must contain the name of your virtual environment.")
    Exit
}

# TODO: Find $possible_venv_name in $folder_name = Split-Path (Get-Location) -leaf

# venv file is existing, get content
$possible_venv_name = (Get-Content $venv_file_name)
$possible_venv_directory = (Join-Path $workon_home $possible_venv_name)
if( # Empty file
    ($possible_venv_name -eq $null) -or
    # Spaces only file
    ($possible_venv_name.Trim() -eq "") -or
    # File pointing to non-existing folder
    !(Test-Path $possible_venv_directory)
    ) {
        $Host.UI.WriteErrorLine("The venv name inside '" + $venv_file_name + "' did not point to an existing virtual environment in '" + $workon_home + "'.")
        Exit
}

# Check if the folder is a virtual environment by looking for the Activate.ps1 file
$activate_ps1 = (Join-Path $possible_venv_directory "Scripts\Activate.ps1")
if(!(Test-Path $activate_ps1)) {
    $Host.UI.WriteErrorLine("Could not find a virtual environment inside '" + $possible_venv_directory + "'.")
} else {
    # Activate the virtual environment
    . $activate_ps1
    Write-Host("Activated virtual environment '" + $possible_venv_name + "'. Currently installed packages:")
    Write-Host("")
    pip freeze
    Write-Host("")
    Write-Host("Enter 'deactivate' to deactivate the active virtual environment.")
}