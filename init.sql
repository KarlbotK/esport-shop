-- =============================================
-- ShopAgent — 电竞设备商城 数据库初始化脚本
-- =============================================

CREATE DATABASE IF NOT EXISTS shop_agent DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE shop_agent;

-- ==================== 用户域 ====================

DROP TABLE IF EXISTS ums_user;
CREATE TABLE ums_user (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(64) NOT NULL UNIQUE COMMENT '用户名',
    password VARCHAR(256) NOT NULL COMMENT 'BCrypt加密密码',
    email VARCHAR(128) COMMENT '邮箱',
    phone VARCHAR(20) COMMENT '手机号',
    role VARCHAR(20) NOT NULL DEFAULT 'CUSTOMER' COMMENT '角色: CUSTOMER/SALES/ADMIN',
    deleted TINYINT NOT NULL DEFAULT 0 COMMENT '逻辑删除: 0正常 1已删除',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_role (role)
) ENGINE=InnoDB COMMENT '用户表';

DROP TABLE IF EXISTS ums_login_log;
CREATE TABLE ums_login_log (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    login_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '登录时间',
    ip_address VARCHAR(64) COMMENT 'IP地址',
    INDEX idx_user_id (user_id),
    INDEX idx_login_time (login_time)
) ENGINE=InnoDB COMMENT '用户登录日志';

DROP TABLE IF EXISTS sms_operation_log;
CREATE TABLE sms_operation_log (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    sales_id BIGINT NOT NULL COMMENT '操作人ID',
    operation_type VARCHAR(64) NOT NULL COMMENT '操作类型',
    content VARCHAR(512) COMMENT '操作内容',
    ip_address VARCHAR(64) COMMENT 'IP地址',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_sales_id (sales_id),
    INDEX idx_create_time (create_time)
) ENGINE=InnoDB COMMENT '操作日志表';

-- ==================== 商品域 ====================

DROP TABLE IF EXISTS pms_category;
CREATE TABLE pms_category (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(64) NOT NULL COMMENT '分类名称',
    parent_id BIGINT DEFAULT 0 COMMENT '父分类ID',
    sort INT DEFAULT 0 COMMENT '排序',
    deleted TINYINT NOT NULL DEFAULT 0,
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB COMMENT '商品分类表';

DROP TABLE IF EXISTS pms_brand;
CREATE TABLE pms_brand (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(64) NOT NULL COMMENT '品牌名称',
    logo_url VARCHAR(256) COMMENT 'Logo地址',
    description VARCHAR(512) COMMENT '品牌描述',
    deleted TINYINT NOT NULL DEFAULT 0,
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB COMMENT '品牌表';

DROP TABLE IF EXISTS pms_spu;
CREATE TABLE pms_spu (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(256) NOT NULL COMMENT '商品名称',
    category_id BIGINT NOT NULL COMMENT '分类ID',
    brand_id BIGINT NOT NULL COMMENT '品牌ID',
    description TEXT COMMENT '图文详情',
    publish_status TINYINT DEFAULT 1 COMMENT '上架状态: 0下架 1上架',
    deleted TINYINT NOT NULL DEFAULT 0,
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_category (category_id),
    INDEX idx_brand (brand_id)
) ENGINE=InnoDB COMMENT 'SPU商品表';

DROP TABLE IF EXISTS pms_sku;
CREATE TABLE pms_sku (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    spu_id BIGINT NOT NULL COMMENT '关联SPU ID',
    sku_name VARCHAR(256) NOT NULL COMMENT '规格名称',
    price DECIMAL(10,2) NOT NULL COMMENT '单价',
    stock INT DEFAULT 0 COMMENT '库存',
    attributes VARCHAR(512) COMMENT '规格属性JSON',
    deleted TINYINT NOT NULL DEFAULT 0,
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_spu_id (spu_id)
) ENGINE=InnoDB COMMENT 'SKU库存表';

DROP TABLE IF EXISTS pms_browse_log;
CREATE TABLE pms_browse_log (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT COMMENT '用户ID(未登录为NULL)',
    spu_id BIGINT NOT NULL COMMENT '浏览商品ID',
    duration_seconds INT DEFAULT 0 COMMENT '停留时长(秒)',
    ip_address VARCHAR(64) COMMENT 'IP地址',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_spu_id (spu_id),
    INDEX idx_create_time (create_time)
) ENGINE=InnoDB COMMENT '浏览行为日志';

-- ==================== 订单域 ====================

DROP TABLE IF EXISTS oms_order;
CREATE TABLE oms_order (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL COMMENT '用户ID',
    total_amount DECIMAL(10,2) NOT NULL COMMENT '订单总金额',
    status TINYINT DEFAULT 0 COMMENT '0待付款 1已付款 2已发货 3已完成 4已取消',
    deleted TINYINT NOT NULL DEFAULT 0,
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_status (status)
) ENGINE=InnoDB COMMENT '订单表';

DROP TABLE IF EXISTS oms_order_item;
CREATE TABLE oms_order_item (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    order_id BIGINT NOT NULL COMMENT '订单ID',
    sku_id BIGINT NOT NULL COMMENT 'SKU ID',
    quantity INT NOT NULL COMMENT '数量',
    price DECIMAL(10,2) NOT NULL COMMENT '下单时单价',
    deleted TINYINT NOT NULL DEFAULT 0,
    INDEX idx_order_id (order_id)
) ENGINE=InnoDB COMMENT '订单明细表';

-- ==================== 种子数据 ====================

-- 分类
INSERT INTO pms_category (name, parent_id, sort) VALUES
('鼠标', 0, 1),
('键盘', 0, 2),
('耳机', 0, 3),
('鼠标垫', 0, 4),
('电竞椅', 0, 5);

-- 品牌
INSERT INTO pms_brand (name, description) VALUES
('罗技', '瑞士品牌，GPW系列无线鼠标享誉全球'),
('雷蛇', '新加坡品牌，外号"灯厂"，毒蝰/蝰蛇系列'),
('赛睿', '丹麦品牌，Arctis系列耳机广受好评'),
('海盗船', '美国品牌，K系列键盘知名'),
('卓威', '中国台湾品牌，FPS职业选手首选'),
('ROG', '华硕旗下电竞品牌'),
('HyperX', '金士顿旗下电竞品牌'),
('Wooting', '荷兰品牌，磁轴键盘先驱');

-- SPU: 鼠标
INSERT INTO pms_spu (name, category_id, brand_id, description) VALUES
('罗技 PRO X SUPERLIGHT 2', 1, 1, 'GPW3代，60g超轻量无线鼠标，HERO 2传感器，32000DPI，95小时续航'),
('雷蛇 毒蝰V3 Pro', 1, 2, '54g轻量无线鼠标，Focus Pro 35K传感器，8000Hz轮询率，90小时续航'),
('卓威 EC3-CW', 1, 5, '无线右手人体工学鼠标，3370传感器，专为FPS设计');

-- SPU: 键盘
INSERT INTO pms_spu (name, category_id, brand_id, description) VALUES
('Wooting 60HE+', 2, 8, '60%磁轴键盘，Lekker磁轴，Rapid Trigger功能，0.1mm精度'),
('罗技 G913 TKL', 2, 1, '87键无线机械键盘，Lightspeed无线，矮轴，RGB背光'),
('雷蛇 黑寡妇V4 Pro', 2, 2, '全尺寸机械键盘，雷蛇绿/橙轴，RGB，多媒体旋钮');

-- SPU: 耳机
INSERT INTO pms_spu (name, category_id, brand_id, description) VALUES
('HyperX Cloud III', 3, 7, '53mm驱动单元，DTS音效，可拆卸麦克风，轻量舒适'),
('赛睿 Arctis Nova Pro Wireless', 3, 3, '双无线连接，ANC主动降噪，热插拔电池，360°空间音频');

-- SKU: GPW3
INSERT INTO pms_sku (spu_id, sku_name, price, stock, attributes) VALUES
(1, 'GPW3 黑色', 1099.00, 50, '{"color": "黑色"}'),
(1, 'GPW3 白色', 1099.00, 30, '{"color": "白色"}'),
(1, 'GPW3 粉色', 1199.00, 20, '{"color": "粉色"}');

-- SKU: 毒蝰V3 Pro
INSERT INTO pms_sku (spu_id, sku_name, price, stock, attributes) VALUES
(2, '毒蝰V3 Pro 黑色', 1299.00, 40, '{"color": "黑色"}'),
(2, '毒蝰V3 Pro 白色', 1299.00, 25, '{"color": "白色"}');

-- SKU: EC3-CW
INSERT INTO pms_sku (spu_id, sku_name, price, stock, attributes) VALUES
(3, 'EC3-CW 黑色', 1099.00, 35, '{"color": "黑色"}');

-- SKU: Wooting 60HE+
INSERT INTO pms_sku (spu_id, sku_name, price, stock, attributes) VALUES
(4, '60HE+ 黑色', 1399.00, 15, '{"switch": "Lekker磁轴", "layout": "60%"}');

-- SKU: G913 TKL
INSERT INTO pms_sku (spu_id, sku_name, price, stock, attributes) VALUES
(5, 'G913 TKL 黑色 红轴', 999.00, 25, '{"switch": "红轴", "layout": "TKL", "color": "黑色"}'),
(5, 'G913 TKL 黑色 青轴', 999.00, 20, '{"switch": "青轴", "layout": "TKL", "color": "黑色"}'),
(5, 'G913 TKL 白色 红轴', 999.00, 15, '{"switch": "红轴", "layout": "TKL", "color": "白色"}');

-- SKU: 黑寡妇V4 Pro
INSERT INTO pms_sku (spu_id, sku_name, price, stock, attributes) VALUES
(6, '黑寡妇V4 Pro 绿轴', 1599.00, 20, '{"switch": "绿轴", "layout": "全尺寸"}'),
(6, '黑寡妇V4 Pro 橙轴', 1599.00, 15, '{"switch": "橙轴", "layout": "全尺寸"}');

-- SKU: HyperX Cloud III
INSERT INTO pms_sku (spu_id, sku_name, price, stock, attributes) VALUES
(7, 'Cloud III 黑色', 599.00, 60, '{"color": "黑色"}'),
(7, 'Cloud III 红黑', 629.00, 40, '{"color": "红黑"}');

-- SKU: Arctis Nova Pro
INSERT INTO pms_sku (spu_id, sku_name, price, stock, attributes) VALUES
(8, 'Arctis Nova Pro Wireless 黑色', 2699.00, 10, '{"connection": "无线", "color": "黑色"}'),
(8, 'Arctis Nova Pro Wireless 白色', 2699.00, 8, '{"connection": "无线", "color": "白色"}');

-- 默认管理员 (密码: admin123, BCrypt编码)
INSERT INTO ums_user (username, password, role) VALUES
('admin', '$2b$12$OgVLiNlRgJp0imZPy1gAte3XiZwgUq3/ZnoJdSqWXNXGeDjjJHamO', 'ADMIN');
