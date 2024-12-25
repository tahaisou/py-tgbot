-- 创建数据库
CREATE DATABASE py_admin CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 使用数据库
USE py_admin;

-- 创建用户表
DROP TABLE IF EXISTS users;
CREATE TABLE users (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '用户ID',
    username VARCHAR(50) COMMENT '用户名',
    nickname VARCHAR(50) COMMENT '昵称',
    avatar_url VARCHAR(255) COMMENT '头像URL',
    platform VARCHAR(20) DEFAULT 'telegram' COMMENT '平台',
    platform_user_id VARCHAR(50) NOT NULL COMMENT 'Telegram用户ID',
    status BOOLEAN DEFAULT TRUE COMMENT '用户状态',
    
    -- Telegram 特有字段
    tg_first_name VARCHAR(64) COMMENT 'Telegram名',
    tg_last_name VARCHAR(64) COMMENT 'Telegram姓',
    tg_language_code VARCHAR(10) COMMENT '语言代码',
    tg_is_bot BOOLEAN DEFAULT FALSE COMMENT '是否是机器人',
    last_interaction TIMESTAMP COMMENT '最后交互时间',
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    UNIQUE KEY uk_platform_user_id (platform, platform_user_id),
    INDEX idx_last_interaction (last_interaction)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户信息表'; 

-- 添加备注字段到用户表
ALTER TABLE users ADD COLUMN note TEXT COMMENT '用户备注';

-- 创建标签表
CREATE TABLE tags (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '标签ID',
    name VARCHAR(50) NOT NULL COMMENT '标签名称',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    UNIQUE KEY uk_tag_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='标签表';

-- 创建用户-标签关联表
CREATE TABLE user_tags (
    user_id BIGINT NOT NULL COMMENT '用户ID',
    tag_id BIGINT NOT NULL COMMENT '标签ID',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (user_id, tag_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户-标签关联表'; 

-- 创建服务器信息表
CREATE TABLE server_info (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '服务器信息ID',
    user_id BIGINT NOT NULL COMMENT '用户ID',
    raw_content TEXT NOT NULL COMMENT '原始信息文本',
    -- 四要素（必填）
    server_ips TEXT NOT NULL COMMENT '服务器IP列表（JSON格式）',
    server_port VARCHAR(10) NOT NULL COMMENT '远程端口',
    server_username VARCHAR(50) NOT NULL COMMENT '登录用户名',
    server_password VARCHAR(255) NOT NULL COMMENT '登录密码',
    -- 可选信息（JSON格式存储）
    extra_info JSON COMMENT '额外信息，如系统类型、配置等',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='服务器信息表'; 

-- 修改服务器信息表，添加时间管理字段
ALTER TABLE server_info 
ADD COLUMN start_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '服务起始时间',
ADD COLUMN expire_date TIMESTAMP NOT NULL COMMENT '服务到期时间',
ADD COLUMN status VARCHAR(20) NOT NULL DEFAULT 'normal' COMMENT '状态：normal-正常/pending-待续费/expiring-即将到期/expired-已过期'; 

-- 创建续期记录表
CREATE TABLE server_renewals (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '续期记录ID',
    server_id BIGINT NOT NULL COMMENT '服务器ID',
    renew_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '续期时间',
    old_expire_date TIMESTAMP NOT NULL COMMENT '原到期时间',
    new_expire_date TIMESTAMP NOT NULL COMMENT '新到期时间',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (server_id) REFERENCES server_info(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='服务器续期记录表'; 

-- 创建机器人配置表
CREATE TABLE bot_config (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '配置ID',
    bot_name VARCHAR(100) NOT NULL COMMENT '机器人名称',
    bot_token VARCHAR(255) NOT NULL COMMENT '机器人Token',
    bot_username VARCHAR(100) COMMENT '机器人用户名',
    webhook_url VARCHAR(255) COMMENT 'Webhook URL',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否激活',
    last_check_time TIMESTAMP COMMENT '最后检查时间',
    status VARCHAR(50) DEFAULT 'pending' COMMENT '状态：pending-待验证/active-正常/error-错误',
    error_message TEXT COMMENT '错误信息',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='机器人配置表'; 

-- 创建定时任务配置表
CREATE TABLE task_config (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '配置ID',
    task_name VARCHAR(100) NOT NULL COMMENT '任务名称',
    task_type VARCHAR(50) NOT NULL COMMENT '任务类型：cron/interval',
    cron_expression VARCHAR(100) COMMENT 'Cron表达式',
    interval_seconds INT COMMENT '间隔秒数',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否激活',
    last_run_time TIMESTAMP COMMENT '上次运行时间',
    next_run_time TIMESTAMP COMMENT '下次运行时间',
    description TEXT COMMENT '任务描述',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='定时任务配置表';

-- 插入默认配置
INSERT INTO task_config (task_name, task_type, cron_expression, description) VALUES
('update_server_status', 'cron', '0 * * * *', '每小时更新服务器状态'),
('send_expiration_notices', 'cron', '0 9 * * *', '每天早上9点发送到期提醒'); 