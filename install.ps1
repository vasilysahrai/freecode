# FreeAgent installer — Windows PowerShell.
#   irm https://raw.githubusercontent.com/vasilysahrai/freeagent/main/install.ps1 | iex
$ErrorActionPreference = 'Stop'

$Repo   = 'vasilysahrai/freeagent'
$Source = "git+https://github.com/$Repo.git"

function Bold($s) { Write-Host $s -ForegroundColor White }
function Note($s) { Write-Host "  $s" }
function Fail($s) { Write-Host "error: $s" -ForegroundColor Red; exit 1 }

Bold 'Installing FreeAgent'

# ── Python ──────────────────────────────────────────────────────────────
$python = $null
foreach ($candidate in 'python', 'python3', 'py') {
  if (Get-Command $candidate -ErrorAction SilentlyContinue) { $python = $candidate; break }
}
if (-not $python) {
  Fail 'Python 3 is required. Install from https://www.python.org/downloads/ or "winget install Python.Python.3.12".'
}
$pyVer = & $python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")'
Note "python: $python ($pyVer)"

# ── pipx > pip --user ───────────────────────────────────────────────────
if (Get-Command pipx -ErrorAction SilentlyContinue) {
  Note 'using pipx'
  pipx install --force $Source
} else {
  Note "pipx not found — using 'pip install --user' (consider 'python -m pip install --user pipx' for cleaner installs)"
  & $python -m pip install --user --upgrade --quiet $Source
}

# ── PATH check ──────────────────────────────────────────────────────────
if (-not (Get-Command freeagent -ErrorAction SilentlyContinue)) {
  $userBase = & $python -c 'import site; print(site.getuserbase())'
  $scripts  = Join-Path $userBase 'Scripts'
  Write-Host ''
  Bold 'freeagent installed but not on PATH'
  Note 'add this folder to your User PATH (System Properties → Environment Variables):'
  Note "  $scripts"
  Note 'or for the current PowerShell session:'
  Note "  `$env:Path = `"$scripts;`" + `$env:Path"
  exit 0
}

Write-Host ''
Bold 'Done.'
Note 'next: set a key for any provider you want to use, e.g.:'
Note '  $env:ZAI_API_KEY  = "..."   # free GLM-4.5-flash · https://z.ai'
Note '  $env:GROQ_API_KEY = "..."   # free tier         · https://console.groq.com/keys'
Note 'then run:'
Note '  freeagent'
Note '  freeagent --list-models'
