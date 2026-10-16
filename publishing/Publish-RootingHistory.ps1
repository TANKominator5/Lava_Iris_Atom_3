[CmdletBinding()]
param(
    [switch] $CreateCommits,
    [switch] $Push,
    [switch] $ConfirmPublish,
    [string] $Branch = 'main',
    [string] $AuthorName = 'TANKominator5',
    [string] $AuthorEmail = 'TANKominator5@users.noreply.github.com',
    [string] $Python = 'python'
)
$ErrorActionPreference = 'Stop'
$script = Join-Path $PSScriptRoot 'publish_history.py'
$arguments = @($script, '--branch', $Branch, '--author-name', $AuthorName, '--author-email', $AuthorEmail)
if ($CreateCommits) { $arguments += '--create-commits' }
if ($Push) { $arguments += '--push' }
if ($ConfirmPublish) { $arguments += '--confirm-publish' }
& $Python @arguments
if ($LASTEXITCODE -ne 0) { throw "Publication tool stopped with exit code $LASTEXITCODE" }
