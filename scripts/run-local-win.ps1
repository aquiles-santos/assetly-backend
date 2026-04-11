[CmdletBinding()]
param(
	[switch]$SkipSeed,
	[switch]$NoRun,
	[string]$PythonCommand
)

$ErrorActionPreference = 'Stop'

function Test-PythonInvocation {
	param(
		[string]$Exe,
		[string[]]$PrefixArgs
	)

	try {
		$probeArgs = @($PrefixArgs + @('--version'))
		& $Exe @probeArgs *> $null
		return ($LASTEXITCODE -eq 0)
	}
	catch {
		return $false
	}
}

function Resolve-PythonCommand {
	param(
		[string]$RequestedCommand
	)

	if ($RequestedCommand) {
		if (Test-PythonInvocation -Exe $RequestedCommand -PrefixArgs @()) {
			return @{
				Exe = $RequestedCommand
				PrefixArgs = @()
			}
		}

		throw "Comando Python informado nao esta executavel: $RequestedCommand"
	}

	if (Test-PythonInvocation -Exe 'py' -PrefixArgs @('-3')) {
		return @{
			Exe = 'py'
			PrefixArgs = @('-3')
		}
	}

	if (Test-PythonInvocation -Exe 'python' -PrefixArgs @()) {
		return @{
			Exe = 'python'
			PrefixArgs = @()
		}
	}

	throw "Python nao encontrado ou nao executavel. Instale Python 3.8+ (com 'Add python.exe to PATH') e desative aliases da Microsoft Store para python/python3 em Configuracoes > Apps > App execution aliases."
}

function Invoke-Python {
	param(
		[string]$PythonExe,
		[string[]]$PrefixArgs,
		[string[]]$Arguments
	)

	$allArgs = @($PrefixArgs + $Arguments)
	Write-Host "-> $PythonExe $($allArgs -join ' ')" -ForegroundColor Cyan
	& $PythonExe @allArgs

	if ($LASTEXITCODE -ne 0) {
		throw "Comando falhou com codigo de saida ${LASTEXITCODE}: $PythonExe $($allArgs -join ' ')"
	}
}

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot '..')
Set-Location $repoRoot

$pythonInfo = Resolve-PythonCommand -RequestedCommand $PythonCommand
$pythonExe = $pythonInfo.Exe
$pythonPrefixArgs = $pythonInfo.PrefixArgs

Write-Host "[1/5] Atualizando ferramentas de empacotamento..." -ForegroundColor Yellow
Invoke-Python -PythonExe $pythonExe -PrefixArgs $pythonPrefixArgs -Arguments @('-m', 'pip', 'install', '--upgrade', 'pip', 'setuptools', 'wheel')

Write-Host "[2/5] Instalando dependencias do projeto..." -ForegroundColor Yellow
Invoke-Python -PythonExe $pythonExe -PrefixArgs $pythonPrefixArgs -Arguments @('-m', 'pip', 'install', '-r', 'requirements.txt')

Write-Host "[3/5] Inicializando banco SQLite..." -ForegroundColor Yellow
Invoke-Python -PythonExe $pythonExe -PrefixArgs $pythonPrefixArgs -Arguments @(
	'-c',
	'from app import create_app; from app.utils.db_init import init_db; app=create_app(); init_db(app)'
)

if (-not $SkipSeed) {
	Write-Host "[4/5] Aplicando seed inicial de ativos..." -ForegroundColor Yellow
	Invoke-Python -PythonExe $pythonExe -PrefixArgs $pythonPrefixArgs -Arguments @(
		'-c',
		'from app import create_app; from app.utils.db_init import seed_db; app=create_app(); seed_db(app)'
	)
}
else {
	Write-Host "[4/5] Seed ignorado (parametro -SkipSeed)." -ForegroundColor Yellow
}

if ($NoRun) {
	Write-Host "[5/5] Setup concluido. Execucao ignorada (parametro -NoRun)." -ForegroundColor Green
	exit 0
}

Write-Host "[5/5] Iniciando API em http://127.0.0.1:5000 ..." -ForegroundColor Green
Invoke-Python -PythonExe $pythonExe -PrefixArgs $pythonPrefixArgs -Arguments @('run.py')
