# 游戏模块创建脚本
# Game Module Creation Script

# 设置错误时停止执行
$ErrorActionPreference = "Stop"

# 定义基础路径
$basePath = "src"

# 定义需要创建的目录结构
$directories = @(
    # 领域层 (Domain Layer)
    "$basePath\domains\game\entities",
    "$basePath\domains\game\value_objects",
    "$basePath\domains\game\aggregates",
    "$basePath\domains\game\services",
    "$basePath\domains\game\repositories",
    
    # 基础设施层 (Infrastructure Layer)
    "$basePath\infrastructure\game\repositories",
    "$basePath\infrastructure\game\services",
    
    # 应用层 (Application Layer)
    "$basePath\application\game\services",
    "$basePath\application\game\dtos",
    
    # 接口层 (Interface Layer)
    "$basePath\interfaces\api\game",
    "$basePath\interfaces\cli\game"
)

# 创建目录的函数
function Create-Directories {
    param (
        [string[]]$dirs
    )
    
    foreach ($dir in $dirs) {
        if (-not (Test-Path $dir)) {
            try {
                New-Item -ItemType Directory -Path $dir -Force
                Write-Host "创建目录成功: $dir" -ForegroundColor Green
            }
            catch {
                Write-Host "创建目录失败: $dir" -ForegroundColor Red
                Write-Host "错误信息: $_" -ForegroundColor Red
                throw
            }
        }
        else {
            Write-Host "目录已存在: $dir" -ForegroundColor Yellow
        }
    }
}

# 创建__init__.py文件的函数
function Create-InitFiles {
    param (
        [string[]]$dirs
    )
    
    foreach ($dir in $dirs) {
        $initFile = Join-Path $dir "__init__.py"
        if (-not (Test-Path $initFile)) {
            try {
                New-Item -ItemType File -Path $initFile -Force
                Write-Host "创建__init__.py成功: $initFile" -ForegroundColor Green
            }
            catch {
                Write-Host "创建__init__.py失败: $initFile" -ForegroundColor Red
                Write-Host "错误信息: $_" -ForegroundColor Red
                throw
            }
        }
        else {
            Write-Host "__init__.py已存在: $initFile" -ForegroundColor Yellow
        }
    }
}

# 定义需要创建的文件
$files = @(
    # 实体类 (Entities)
    @{
        Path = "$basePath\domains\game\entities\player.py"
        Content = @"
# 玩家实体
# Player Entity

from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime

@dataclass
class Player:
    """玩家实体类
    Player Entity Class
    
    属性:
        player_id: 玩家ID
        name: 玩家名称
        score: 玩家分数
        created_at: 创建时间
        updated_at: 更新时间
    """
    player_id: str
    name: str
    score: int = 0
    created_at: datetime = None
    updated_at: datetime = None
"@
    },
    @{
        Path = "$basePath\domains\game\entities\game.py"
        Content = @"
# 游戏实体
# Game Entity

from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime

@dataclass
class Game:
    """游戏实体类
    Game Entity Class
    
    属性:
        game_id: 游戏ID
        players: 玩家列表
        current_round: 当前回合
        status: 游戏状态
        created_at: 创建时间
        updated_at: 更新时间
    """
    game_id: str
    players: List['Player']
    current_round: int = 0
    status: str = 'INITIALIZED'
    created_at: datetime = None
    updated_at: datetime = None
"@
    },
    @{
        Path = "$basePath\domains\game\entities\round.py"
        Content = @"
# 回合实体
# Round Entity

from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime

@dataclass
class Round:
    """回合实体类
    Round Entity Class
    
    属性:
        round_id: 回合ID
        game_id: 游戏ID
        round_number: 回合序号
        actions: 回合动作列表
        created_at: 创建时间
        updated_at: 更新时间
    """
    round_id: str
    game_id: str
    round_number: int
    actions: List[dict] = None
    created_at: datetime = None
    updated_at: datetime = None
"@
    },
    # 值对象 (Value Objects)
    @{
        Path = "$basePath\domains\game\value_objects\game_config.py"
        Content = @"
# 游戏配置值对象
# Game Configuration Value Object

from dataclasses import dataclass
from typing import Dict, Any

@dataclass(frozen=True)
class GameConfig:
    """游戏配置值对象
    Game Configuration Value Object
    
    属性:
        max_players: 最大玩家数
        min_players: 最小玩家数
        max_rounds: 最大回合数
        rules: 游戏规则配置
    """
    max_players: int
    min_players: int
    max_rounds: int
    rules: Dict[str, Any]
"@
    },
    @{
        Path = "$basePath\domains\game\value_objects\game_state.py"
        Content = @"
# 游戏状态值对象
# Game State Value Object

from enum import Enum, auto

class GameState(Enum):
    """游戏状态枚举
    Game State Enumeration
    
    状态:
        INITIALIZED: 已初始化
        WAITING_FOR_PLAYERS: 等待玩家加入
        IN_PROGRESS: 进行中
        FINISHED: 已结束
        CANCELLED: 已取消
    """
    INITIALIZED = auto()
    WAITING_FOR_PLAYERS = auto()
    IN_PROGRESS = auto()
    FINISHED = auto()
    CANCELLED = auto()
"@
    },
    # 聚合根 (Aggregates)
    @{
        Path = "$basePath\domains\game\aggregates\game_session.py"
        Content = @"
# 游戏会话聚合根
# Game Session Aggregate Root

from dataclasses import dataclass
from typing import List
from datetime import datetime

from ..entities.game import Game
from ..entities.player import Player
from ..value_objects.game_config import GameConfig
from ..value_objects.game_state import GameState

@dataclass
class GameSession:
    """游戏会话聚合根
    Game Session Aggregate Root
    
    属性:
        game: 游戏实体
        players: 玩家列表
        config: 游戏配置
        state: 游戏状态
    """
    game: Game
    players: List[Player]
    config: GameConfig
    state: GameState
"@
    },
    # 领域服务 (Domain Services)
    @{
        Path = "$basePath\domains\game\services\game_service.py"
        Content = @"
# 游戏领域服务
# Game Domain Service

from typing import List, Optional
from datetime import datetime

from ..entities.game import Game
from ..entities.player import Player
from ..value_objects.game_config import GameConfig
from ..repositories.game_repository import GameRepository

class GameService:
    """游戏领域服务
    Game Domain Service
    
    职责:
        - 创建游戏
        - 管理游戏状态
        - 执行游戏规则
    """
    
    def __init__(self, game_repository: GameRepository):
        self.game_repository = game_repository
"@
    },
    @{
        Path = "$basePath\domains\game\services\round_service.py"
        Content = @"
# 回合领域服务
# Round Domain Service

from typing import List, Optional
from datetime import datetime

from ..entities.round import Round
from ..entities.game import Game
from ..repositories.game_repository import GameRepository

class RoundService:
    """回合领域服务
    Round Domain Service
    
    职责:
        - 创建回合
        - 处理回合动作
        - 计算回合结果
    """
    
    def __init__(self, game_repository: GameRepository):
        self.game_repository = game_repository
"@
    },
    # 仓储接口 (Repository Interfaces)
    @{
        Path = "$basePath\domains\game\repositories\game_repository.py"
        Content = @"
# 游戏仓储接口
# Game Repository Interface

from abc import ABC, abstractmethod
from typing import List, Optional

from ..entities.game import Game
from ..entities.player import Player
from ..entities.round import Round

class GameRepository(ABC):
    """游戏仓储接口
    Game Repository Interface
    
    职责:
        - 保存游戏状态
        - 加载游戏状态
        - 查询游戏信息
    """
    
    @abstractmethod
    def save_game(self, game: Game) -> None:
        """保存游戏状态"""
        pass
        
    @abstractmethod
    def load_game(self, game_id: str) -> Optional[Game]:
        """加载游戏状态"""
        pass
        
    @abstractmethod
    def get_player_games(self, player_id: str) -> List[Game]:
        """获取玩家的游戏列表"""
        pass
"@
    }
)

# 创建文件的函数
function Create-Files {
    param (
        [array]$files
    )
    
    foreach ($file in $files) {
        $filePath = $file.Path
        $content = $file.Content
        
        if (-not (Test-Path $filePath)) {
            try {
                # 确保目录存在
                $directory = Split-Path $filePath -Parent
                if (-not (Test-Path $directory)) {
                    New-Item -ItemType Directory -Path $directory -Force | Out-Null
                }
                
                # 创建文件
                Set-Content -Path $filePath -Value $content -Encoding UTF8
                Write-Host "创建文件成功: $filePath" -ForegroundColor Green
            }
            catch {
                Write-Host "创建文件失败: $filePath" -ForegroundColor Red
                Write-Host "错误信息: $_" -ForegroundColor Red
                throw
            }
        }
        else {
            Write-Host "文件已存在: $filePath" -ForegroundColor Yellow
        }
    }
}

# 主函数
function Main {
    Write-Host "开始创建游戏模块..." -ForegroundColor Cyan
    
    # 创建目录
    Create-Directories -dirs $directories
    
    # 创建__init__.py文件
    Create-InitFiles -dirs $directories
    
    # 创建文件
    Create-Files -files $files
    
    Write-Host "游戏模块创建完成！" -ForegroundColor Cyan
}

# 执行主函数
Main 