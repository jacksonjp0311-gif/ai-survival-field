param(
  [switch]$Geometry,
  [string]$Root = "."
)

$ErrorActionPreference = "Stop"
$repo = Resolve-Path -LiteralPath $Root
Set-Location -LiteralPath $repo

if ($Geometry) {
  python -m asf.full_loop --root . --geometry
} else {
  python -m asf.full_loop --root .
}
