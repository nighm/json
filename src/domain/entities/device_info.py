from dataclasses import dataclass

@dataclass
class DeviceInfo:
    """
    设备信息实体，字段与biz_device表结构匹配
    """
    # 核心标识字段
    id: int = 0
    device_id: str = ''  # 设备唯一标识
    device_serial_number: str = ''  # 设备序列号（对应原来的sn字段）
    
    # 基本信息字段
    device_name: str = ''  # 设备名称
    ip: str = ''  # IP地址
    mac: str = ''  # MAC地址
    macs: str = ''  # 多个MAC地址
    outside_ip: str = ''  # 外网IP
    
    # 硬件信息字段
    type: str = ''  # 设备类型
    model: str = ''  # 设备型号
    brand: str = ''  # 品牌
    supplier: str = ''  # 供应商
    processor: str = ''  # 处理器
    operating_system: str = ''  # 操作系统
    hard_disk: str = ''  # 硬盘
    memory: str = ''  # 内存
    main_board: str = ''  # 主板
    resolution: str = ''  # 分辨率
    
    # 状态字段
    online: str = '0'  # 在线状态
    status: str = '0'  # 设备状态
    last_heartbeat_time: str = ''  # 最后心跳时间
    last_login_time: str = ''  # 最后登录时间
    offline_time: str = ''  # 离线时间
    
    # 分组和用户字段
    device_group_id: int = -1  # 设备组ID
    device_user_group_id: int = -1  # 设备用户组ID
    user_id: int = -1  # 用户ID
    login_user_id: int = -1  # 登录用户ID
    login_status: int = 0  # 登录状态
    
    # 镜像相关字段
    image_id: int = -1  # 镜像ID
    image_snapshot_id: int = -1  # 镜像快照ID
    local_image_status: str = '0'  # 本地镜像状态
    image_backup_time: str = ''  # 镜像备份时间
    
    # 其他字段
    purchase_batch: str = ''  # 采购批次
    remark: str = ''  # 备注
    create_time: str = ''  # 创建时间
    create_by: str = ''  # 创建者
    update_time: str = ''  # 更新时间
    update_by: str = ''  # 更新者
    del_flag: str = '0'  # 删除标志
    
    # 兼容性字段（为了保持与原有代码的兼容性）
    @property
    def sn(self) -> str:
        """兼容性属性：返回设备序列号"""
        return self.device_serial_number
    
    @property
    def register_time(self) -> str:
        """兼容性属性：返回创建时间"""
        return self.create_time

    # 可根据实际表结构补充更多字段 