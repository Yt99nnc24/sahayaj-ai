$projectDirectory = $PSScriptRoot
$dependencyDirectory = Join-Path $projectDirectory '..\..\work\deps'
if (Test-Path -LiteralPath $dependencyDirectory) {
    $env:PYTHONPATH = (Resolve-Path -LiteralPath $dependencyDirectory).Path
}
Set-Location -LiteralPath $projectDirectory
python backend.py
