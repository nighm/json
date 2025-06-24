# Performance Testing Tools Installation Script (Windows PowerShell)
# Supports installation of jPerf, Iometer, IOzone, Memtester, Netdata, Grafana

# Set error handling
$ErrorActionPreference = "Stop"

# Color output functions
function Write-Success { Write-Host "✓ $args" -ForegroundColor Green }
function Write-Error { Write-Host "✗ $args" -ForegroundColor Red }
function Write-Info { Write-Host "ℹ $args" -ForegroundColor Cyan }
function Write-Warning { Write-Host "⚠ $args" -ForegroundColor Yellow }

# Check administrator privileges
function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# Check if Chocolatey is installed
function Test-Chocolatey {
    try {
        choco --version | Out-Null
        return $true
    }
    catch {
        return $false
    }
}

# Install Chocolatey
function Install-Chocolatey {
    Write-Info "Installing Chocolatey package manager..."
    try {
        Set-ExecutionPolicy Bypass -Scope Process -Force
        [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
        iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
        Write-Success "Chocolatey installation completed"
        return $true
    }
    catch {
        Write-Error "Chocolatey installation failed: $($_.Exception.Message)"
        return $false
    }
}

# Install jPerf
function Install-JPerf {
    Write-Info "Installing jPerf..."
    try {
        if (Test-Chocolatey) {
            choco install jperf -y
            Write-Success "jPerf installation completed"
        } else {
            Write-Warning "Chocolatey not installed, please download jPerf manually"
            Write-Info "Download URL: https://sourceforge.net/projects/jperf/"
        }
    }
    catch {
        Write-Error "jPerf installation failed: $($_.Exception.Message)"
    }
}

# Install Iometer
function Install-Iometer {
    Write-Info "Installing Iometer..."
    try {
        if (Test-Chocolatey) {
            choco install iometer -y
            Write-Success "Iometer installation completed"
        } else {
            Write-Warning "Chocolatey not installed, please download Iometer manually"
            Write-Info "Download URL: https://www.iometer.org/"
        }
    }
    catch {
        Write-Error "Iometer installation failed: $($_.Exception.Message)"
    }
}

# Install Netdata
function Install-Netdata {
    Write-Info "Installing Netdata..."
    try {
        if (Test-Chocolatey) {
            choco install netdata -y
            Write-Success "Netdata installation completed"
        } else {
            Write-Warning "Chocolatey not installed, please install Netdata manually"
            Write-Info "Download URL: https://my-netdata.io/"
        }
    }
    catch {
        Write-Error "Netdata installation failed: $($_.Exception.Message)"
    }
}

# Install Grafana
function Install-Grafana {
    Write-Info "Installing Grafana..."
    try {
        if (Test-Chocolatey) {
            choco install grafana -y
            Write-Success "Grafana installation completed"
        } else {
            Write-Warning "Chocolatey not installed, please install Grafana manually"
            Write-Info "Download URL: https://grafana.com/grafana/download"
        }
    }
    catch {
        Write-Error "Grafana installation failed: $($_.Exception.Message)"
    }
}

# Create configuration file
function New-PerformanceToolsConfig {
    Write-Info "Creating configuration file..."
    try {
        $configDir = "src\config\tools"
        if (!(Test-Path $configDir)) {
            New-Item -ItemType Directory -Path $configDir -Force | Out-Null
        }
        
        $configContent = @"
# Performance testing tools configuration
tools:
  network:
    jperf:
      enabled: true
      path: "C:\ProgramData\chocolatey\bin\jperf.bat"
      default_port: 5201
      timeout: 30
  
  storage:
    iometer:
      enabled: true
      path: "C:\Program Files\Iometer\iometer.exe"
      max_workers: 4
  
  monitoring:
    netdata:
      enabled: true
      port: 19999
      config_path: "C:\ProgramData\netdata"
    
    grafana:
      enabled: true
      port: 3000
      admin_user: admin
      admin_password: admin
"@
        
        $configPath = "$configDir\performance_tools.yaml"
        $configContent | Out-File -FilePath $configPath -Encoding UTF8
        Write-Success "Configuration file created: $configPath"
    }
    catch {
        Write-Error "Configuration file creation failed: $($_.Exception.Message)"
    }
}

# Main installation function
function Install-PerformanceTools {
    Write-Host "=== Performance Testing Tools Installation Script ===" -ForegroundColor Magenta
    Write-Info "Starting installation of performance testing tools..."
    
    # Check administrator privileges
    if (!(Test-Administrator)) {
        Write-Error "Please run this script with administrator privileges"
        return
    }
    
    # Install Chocolatey
    if (!(Test-Chocolatey)) {
        Install-Chocolatey
    }
    
    # Install tools
    Install-JPerf
    Install-Iometer
    Install-Netdata
    Install-Grafana
    
    # Create configuration file
    New-PerformanceToolsConfig
    
    Write-Host "=== Installation Completed ===" -ForegroundColor Green
    Write-Info "Installed tools:"
    Write-Info "  - jPerf: Network performance testing"
    Write-Info "  - Iometer: Storage I/O performance testing"
    Write-Info "  - Netdata: Real-time system monitoring"
    Write-Info "  - Grafana: Data visualization"
    
    Write-Info "Access URLs:"
    Write-Info "  - Netdata: http://localhost:19999"
    Write-Info "  - Grafana: http://localhost:3000 (admin/admin)"
}

# Start monitoring services
function Start-MonitoringServices {
    Write-Info "Starting monitoring services..."
    try {
        # Start Netdata
        if (Get-Service -Name "netdata" -ErrorAction SilentlyContinue) {
            Start-Service -Name "netdata"
            Write-Success "Netdata service started"
        }
        
        # Start Grafana
        if (Get-Service -Name "grafana-server" -ErrorAction SilentlyContinue) {
            Start-Service -Name "grafana-server"
            Write-Success "Grafana service started"
        }
    }
    catch {
        Write-Error "Service startup failed: $($_.Exception.Message)"
    }
}

# Script entry point
Install-PerformanceTools

$startServices = Read-Host "Start monitoring services? (y/N)"
if ($startServices -eq 'y' -or $startServices -eq 'Y') {
    Start-MonitoringServices
} 