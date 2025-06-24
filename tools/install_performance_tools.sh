#!/bin/bash

# 性能测试工具安装脚本 (Linux/macOS)
# 支持安装 jPerf, Iometer, IOzone, Memtester, Netdata, Grafana

set -e  # 遇到错误立即退出

# 颜色输出函数
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${CYAN}ℹ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_header() {
    echo -e "${BLUE}=== $1 ===${NC}"
}

# 检测操作系统
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
        if command -v apt-get &> /dev/null; then
            PACKAGE_MANAGER="apt"
        elif command -v yum &> /dev/null; then
            PACKAGE_MANAGER="yum"
        elif command -v dnf &> /dev/null; then
            PACKAGE_MANAGER="dnf"
        else
            print_error "不支持的Linux发行版"
            exit 1
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        PACKAGE_MANAGER="brew"
    else
        print_error "不支持的操作系统: $OSTYPE"
        exit 1
    fi
}

# 检查是否为root用户
check_root() {
    if [[ $EUID -eq 0 ]]; then
        print_warning "检测到root权限，建议使用普通用户运行"
    fi
}

# 安装包管理器
install_package_manager() {
    if [[ "$OS" == "macos" ]]; then
        if ! command -v brew &> /dev/null; then
            print_info "正在安装Homebrew..."
            /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
            print_success "Homebrew安装完成"
        fi
    fi
}

# 安装jPerf
install_jperf() {
    print_info "正在安装jPerf..."
    
    if [[ "$OS" == "linux" ]]; then
        if [[ "$PACKAGE_MANAGER" == "apt" ]]; then
            sudo apt update
            sudo apt install -y jperf
        elif [[ "$PACKAGE_MANAGER" == "yum" ]] || [[ "$PACKAGE_MANAGER" == "dnf" ]]; then
            sudo $PACKAGE_MANAGER install -y jperf
        fi
    elif [[ "$OS" == "macos" ]]; then
        brew install jperf
    fi
    
    print_success "jPerf安装完成"
}

# 安装Iometer
install_iometer() {
    print_info "正在安装Iometer..."
    
    if [[ "$OS" == "linux" ]]; then
        # Linux下需要编译安装
        print_warning "Linux下Iometer需要手动编译安装"
        print_info "请访问: https://www.iometer.org/"
        
        # 尝试安装依赖
        if [[ "$PACKAGE_MANAGER" == "apt" ]]; then
            sudo apt install -y build-essential libx11-dev libxext-dev
        fi
    elif [[ "$OS" == "macos" ]]; then
        brew install iometer
    fi
}

# 安装IOzone
install_iozone() {
    print_info "正在安装IOzone..."
    
    if [[ "$OS" == "linux" ]]; then
        if [[ "$PACKAGE_MANAGER" == "apt" ]]; then
            sudo apt install -y iozone3
        elif [[ "$PACKAGE_MANAGER" == "yum" ]] || [[ "$PACKAGE_MANAGER" == "dnf" ]]; then
            sudo $PACKAGE_MANAGER install -y iozone
        fi
    elif [[ "$OS" == "macos" ]]; then
        brew install iozone
    fi
    
    print_success "IOzone安装完成"
}

# 安装Memtester
install_memtester() {
    print_info "正在安装Memtester..."
    
    if [[ "$OS" == "linux" ]]; then
        if [[ "$PACKAGE_MANAGER" == "apt" ]]; then
            sudo apt install -y memtester
        elif [[ "$PACKAGE_MANAGER" == "yum" ]] || [[ "$PACKAGE_MANAGER" == "dnf" ]]; then
            sudo $PACKAGE_MANAGER install -y memtester
        fi
    elif [[ "$OS" == "macos" ]]; then
        brew install memtester
    fi
    
    print_success "Memtester安装完成"
}

# 安装Netdata
install_netdata() {
    print_info "正在安装Netdata..."
    
    # 使用官方安装脚本
    bash <(curl -Ss https://my-netdata.io/kickstart.sh) --stable-channel --disable-telemetry
    
    print_success "Netdata安装完成"
}

# 安装Grafana
install_grafana() {
    print_info "正在安装Grafana..."
    
    if [[ "$OS" == "linux" ]]; then
        if [[ "$PACKAGE_MANAGER" == "apt" ]]; then
            # 添加Grafana仓库
            wget -q -O - https://packages.grafana.com/gpg.key | sudo apt-key add -
            echo "deb https://packages.grafana.com/oss/deb stable main" | sudo tee /etc/apt/sources.list.d/grafana.list
            sudo apt update
            sudo apt install -y grafana
        elif [[ "$PACKAGE_MANAGER" == "yum" ]] || [[ "$PACKAGE_MANAGER" == "dnf" ]]; then
            # 添加Grafana仓库
            sudo tee /etc/yum.repos.d/grafana.repo <<EOF
[grafana]
name=grafana
baseurl=https://packages.grafana.com/oss/rpm
repo_gpgcheck=1
enabled=1
gpgcheck=0
sslverify=0
gpgkey=https://packages.grafana.com/gpg.key
EOF
            sudo $PACKAGE_MANAGER install -y grafana
        fi
    elif [[ "$OS" == "macos" ]]; then
        brew install grafana
    fi
    
    print_success "Grafana安装完成"
}

# 创建配置文件
create_config() {
    print_info "正在创建配置文件..."
    
    local config_dir="src/config/tools"
    mkdir -p "$config_dir"
    
    cat > "$config_dir/performance_tools.yaml" << 'EOF'
# 性能测试工具配置文件
tools:
  network:
    jperf:
      enabled: true
      path: "/usr/bin/jperf"
      default_port: 5201
      timeout: 30
  
  storage:
    iometer:
      enabled: true
      path: "/usr/local/bin/iometer"
      max_workers: 4
    
    iozone:
      enabled: true
      path: "/usr/bin/iozone"
      test_size: "1G"
  
  memory:
    memtester:
      enabled: true
      path: "/usr/bin/memtester"
      memory_size: "1G"
  
  monitoring:
    netdata:
      enabled: true
      port: 19999
      config_path: "/etc/netdata"
    
    grafana:
      enabled: true
      port: 3000
      admin_user: admin
      admin_password: admin
EOF
    
    print_success "配置文件已创建: $config_dir/performance_tools.yaml"
}

# 启动监控服务
start_monitoring_services() {
    print_info "正在启动监控服务..."
    
    if [[ "$OS" == "linux" ]]; then
        # 启动Netdata
        if command -v systemctl &> /dev/null; then
            sudo systemctl start netdata
            sudo systemctl enable netdata
            print_success "Netdata服务已启动"
        fi
        
        # 启动Grafana
        if command -v systemctl &> /dev/null; then
            sudo systemctl start grafana-server
            sudo systemctl enable grafana-server
            print_success "Grafana服务已启动"
        fi
    elif [[ "$OS" == "macos" ]]; then
        # macOS下使用brew services
        brew services start netdata
        brew services start grafana
        print_success "监控服务已启动"
    fi
}

# 显示安装结果
show_installation_summary() {
    print_header "安装完成"
    print_info "安装的工具:"
    print_info "  - jPerf: 网络性能测试"
    print_info "  - Iometer: 存储I/O性能测试"
    print_info "  - IOzone: 文件系统性能测试"
    print_info "  - Memtester: 内存测试"
    print_info "  - Netdata: 实时系统监控"
    print_info "  - Grafana: 数据可视化"
    
    print_info "访问地址:"
    print_info "  - Netdata: http://localhost:19999"
    print_info "  - Grafana: http://localhost:3000 (admin/admin)"
    
    print_info "配置文件位置:"
    print_info "  - src/config/tools/performance_tools.yaml"
}

# 主安装函数
main() {
    print_header "性能测试工具安装脚本"
    print_info "开始安装性能测试工具..."
    
    # 检测操作系统
    detect_os
    print_info "检测到操作系统: $OS"
    
    # 检查权限
    check_root
    
    # 安装包管理器
    install_package_manager
    
    # 安装各个工具
    install_jperf
    install_iometer
    install_iozone
    install_memtester
    install_netdata
    install_grafana
    
    # 创建配置文件
    create_config
    
    # 显示安装结果
    show_installation_summary
    
    # 询问是否启动服务
    read -p "是否启动监控服务? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        start_monitoring_services
    fi
}

# 脚本入口
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi 