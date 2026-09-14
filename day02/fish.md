# 渔获秀小程序开发文档

## 1. 项目概述

### 1.1 项目背景

“渔获秀”是一款面向钓鱼爱好者的小程序，核心目标是：

- 记录与展示用户渔获成果
- 结合地图、天气、水域信息提升钓鱼体验
- 构建钓友社区，形成内容分享与互动

### 1.2 核心定位

- **产品形态**：微信小程序
- **核心关键词**：渔获记录、地图定位、钓点推荐、社区分享
- **目标用户**：休闲 / 竞技钓鱼爱好者

### 1.3 技术栈选型

| 层级     | 技术选型                   |
| -------- | -------------------------- |
| 前端     | UniApp + Vue3 + TypeScript |
| 后端     | FastAPI                    |
| 数据库   | PostgreSQL（推荐）         |
| 对象存储 | 腾讯云 COS（数据万象）     |
| 地图     | 高德地图 SDK               |
| 服务器   | 腾讯云 Centeros 9（Linux） |
| 鉴权     | JWT + 微信登录             |

---

## 2. 视觉与交互说明

### 2.1 整体风格

- 地图为核心视觉主体（卫星 / 地形风格）
- 强户外感、自然色系
- 信息层级清晰，避免复杂操作

### 2.2 首页结构（参考视觉稿）

1. 顶部区域

   - 当前城市 / 区域（如：杭州·西湖区）
   - 搜索入口
   - 消息 / 通知入口

2. 地图区域（核心）

   - 当前定位
   - 钓点标记（支持点击）
   - 当前选中钓点高亮

3. 钓点信息卡片

   - 钓点名称
   - 距离 / 所属区域
   - 主钓鱼种
   - 当前气压 / 天气
   - 【推荐前往】标签

4. 核心操作按钮

   - 查看详情并导航

5. 底部 Tab
   - 发现钓点
   - 渔获秀
   - 我的

### 三、用户体系模块（强化社交属性）

### 1.1 用户表优化设计

```sql
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    -- 微信基础信息（必填）
    wx_openid VARCHAR(100) UNIQUE NOT NULL,
    wx_unionid VARCHAR(100),
    wx_session_key VARCHAR(100),

    -- 用户基础信息（微信授权获取）
    nickname VARCHAR(50) NOT NULL,
    avatar_url VARCHAR(500),
    gender TINYINT DEFAULT 0,  -- 0:未知 1:男 2:女
    language VARCHAR(10),

    -- 地理位置信息（用于个性化推荐）
    province VARCHAR(20),
    city VARCHAR(20),
    district VARCHAR(20),
    last_latitude DECIMAL(10,7),
    last_longitude DECIMAL(10,7),
    last_location_update TIMESTAMP,

    -- 钓鱼专业信息（用户手动填写）
    fishing_years INTEGER DEFAULT 0,           -- 钓龄（年）
    experience_level VARCHAR(20) DEFAULT 'beginner',  -- beginner/intermediate/advanced/master
    preferred_fishing_type VARCHAR(20),        -- 偏好钓法：台钓/路亚/传统钓
    preferred_fish_species JSONB DEFAULT '[]', -- 偏好鱼种 ["鲫鱼","鲤鱼"]
    personal_signature VARCHAR(100),           -- 个性签名

    -- 联系方式（选填）
    phone VARCHAR(20),
    wechat_id VARCHAR(50),

    -- 社交统计（冗余字段，减少联表查询）
    following_count INTEGER DEFAULT 0,         -- 关注数
    followers_count INTEGER DEFAULT 0,         -- 粉丝数
    total_catches INTEGER DEFAULT 0,           -- 总渔获数
    total_likes_received INTEGER DEFAULT 0,    -- 获赞总数
    total_comments_received INTEGER DEFAULT 0, -- 获评总数

    -- 成就系统（预留）
    badges JSONB DEFAULT '[]',                 -- 获得的徽章
    title VARCHAR(20),                         -- 称号：新手/钓手/达人/大师

    -- 账户状态
    status VARCHAR(20) DEFAULT 'active',       -- active/blocked/inactive
    is_verified BOOLEAN DEFAULT FALSE,         -- 是否认证用户
    verification_type VARCHAR(20),             -- 认证类型：expert/celebrity

    -- 隐私设置
    privacy_settings JSONB DEFAULT '{
        "show_location": true,
        "show_catches": true,
        "allow_follow": true,
        "allow_message": true
    }',

    -- 系统字段
    last_login_at TIMESTAMP,
    last_active_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- 索引优化
    INDEX idx_wx_openid (wx_openid),
    INDEX idx_city_district (city, district),
    INDEX idx_fishing_years (fishing_years DESC),
    INDEX idx_total_catches (total_catches DESC),
    INDEX idx_last_active (last_active_at DESC)
) COMMENT='用户表';

-- 扩展表：用户详细信息表（分离不常用字段）
CREATE TABLE user_profiles (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- 个人简介
    introduction TEXT,                         -- 详细自我介绍
    fishing_story TEXT,                        -- 钓鱼故事/经历

    -- 装备信息
    fishing_gear JSONB DEFAULT '[]',           -- 常用装备

    -- 统计数据详情
    catches_by_species JSONB DEFAULT '{}',     -- 按鱼种统计 {"鲫鱼": 15, "鲤鱼": 8}
    catches_by_month JSONB DEFAULT '{}',       -- 按月统计 {"2024-01": 5}
    favorite_spots JSONB DEFAULT '[]',         -- 常去钓点 [spot_id1, spot_id2]

    -- 成就详情
    personal_bests JSONB DEFAULT '{}',         -- 个人纪录 {"鲫鱼": 1.5, "鲤鱼": 3.2}
    fishing_goals JSONB DEFAULT '[]',          -- 钓鱼目标

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 1.2 用户相关功能接口

```python
# 1. 微信登录（支持静默登录和授权登录两种模式）
@router.post("/auth/wechat")
async def wechat_auth(
    code: str = Form(...),
    encrypted_data: Optional[str] = Form(None),
    iv: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    微信登录接口
    - 只有code：静默登录，仅获取openid
    - 有encrypted_data和iv：授权登录，获取用户信息
    """
    pass

# 2. 获取用户资料（三种模式）
@router.get("/users/{user_id}")
async def get_user_profile(
    user_id: int,
    detail_level: str = Query("basic", enum=["basic", "normal", "full"]),
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    获取用户资料
    - basic: 基础信息（公开可见）
    - normal: 正常信息（登录用户可见）
    - full: 完整信息（仅自己可见）
    """
    pass

# 3. 更新用户位置（用于个性化推荐）
@router.post("/users/me/location")
async def update_user_location(
    location: UserLocationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新用户位置
    用于：
    1. 推荐附近钓点
    2. 显示附近钓友
    3. 统计区域活跃度
    """
    pass

# 4. 用户数据统计
@router.get("/users/me/stats")
async def get_user_statistics(
    timeframe: str = Query("all", enum=["day", "week", "month", "year", "all"]),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取用户数据统计
    包括：
    - 渔获趋势
    - 活跃度分析
    - 成就进度
    """
    pass
```

## 二、钓点模块（强化实时性和实用性）

### 2.1 钓点表深度优化

```sql
CREATE TABLE fishing_spots (
    id BIGSERIAL PRIMARY KEY,

    -- 基础信息
    name VARCHAR(50) NOT NULL,
    description VARCHAR(500),
    cover_image VARCHAR(500),                   -- 封面图

    -- 地理位置（核心）
    latitude DECIMAL(10,7) NOT NULL,
    longitude DECIMAL(10,7) NOT NULL,
    geohash VARCHAR(12) NOT NULL,               -- Geohash编码，用于快速附近查询
    address VARCHAR(200),

    -- 行政区划
    province VARCHAR(20),
    city VARCHAR(20),
    district VARCHAR(20),
    street VARCHAR(50),

    -- 钓点属性分类
    spot_type VARCHAR(20) NOT NULL DEFAULT 'natural',  -- natural自然水域/commercial商业塘/competition竞技池
    water_type VARCHAR(20) DEFAULT 'freshwater',       -- freshwater淡水/saltwater海水
    water_body_type VARCHAR(20),                       -- river江/lake湖/reservoir水库/sea海/pond塘
    difficulty_level VARCHAR(10) DEFAULT 'medium',     -- easy/medium/hard

    -- 费用信息
    fee_type VARCHAR(20) DEFAULT 'free',               -- free免费/hourly按时收费/daily按天收费/fishing按斤收费
    fee_details JSONB DEFAULT '{}',                    -- 详细费用 {"hourly": 50, "daily": 200}
    payment_methods JSONB DEFAULT '[]',                -- 支付方式 ["wechat", "alipay", "cash"]

    -- 设施服务
    facilities JSONB DEFAULT '[]',                     -- 设施 ["parking", "restroom", "restaurant", "gear_rental", "boat_rental"]
    services JSONB DEFAULT '[]',                       -- 服务 ["fish_cleaning", "gear_repair", "guide_service"]

    -- 鱼种信息
    common_fish_species JSONB NOT NULL DEFAULT '[]',   -- 常见鱼种
    rare_fish_species JSONB DEFAULT '[]',              -- 稀有鱼种
    best_season VARCHAR(100),                          -- 最佳季节
    best_time_of_day VARCHAR(100),                     -- 最佳时段

    -- 安全信息
    safety_level VARCHAR(10) DEFAULT 'safe',           -- safe/warning/dangerous
    safety_notes TEXT,                                 -- 安全提示
    emergency_contact VARCHAR(20),                     -- 紧急联系人

    -- 实时状态（定期更新）
    current_weather JSONB,                             -- 当前天气
    water_temperature DECIMAL(4,1),                    -- 水温
    water_level VARCHAR(20),                           -- 水位
    water_clarity VARCHAR(20),                         -- 水质清澈度
    current_fishers_count INTEGER DEFAULT 0,           -- 当前钓鱼人数
    last_fisher_update TIMESTAMP,                      -- 最后人数更新时间

    -- 今日数据
    today_catches_count INTEGER DEFAULT 0,             -- 今日渔获总数
    today_fish_species JSONB DEFAULT '[]',             -- 今日钓到鱼种
    today_biggest_catch_weight DECIMAL(6,3),           -- 今日最大渔获重量

    -- 评分系统
    overall_rating DECIMAL(3,2) DEFAULT 0.0,           -- 综合评分
    environment_rating DECIMAL(3,2) DEFAULT 0.0,       -- 环境评分
    fish_density_rating DECIMAL(3,2) DEFAULT 0.0,      -- 鱼密度评分
    facility_rating DECIMAL(3,2) DEFAULT 0.0,          -- 设施评分
    service_rating DECIMAL(3,2) DEFAULT 0.0,           -- 服务评分
    total_reviews INTEGER DEFAULT 0,                   -- 评价总数

    -- 人气指数（算法计算）
    popularity_score INTEGER DEFAULT 0,                -- 综合人气分
    trending_score INTEGER DEFAULT 0,                  -- 趋势分（上升/下降）

    -- 验证状态
    verification_status VARCHAR(20) DEFAULT 'unverified',  -- unverified/verified/rejected
    verification_notes TEXT,                           -- 认证说明
    verified_by BIGINT REFERENCES users(id),           -- 认证人
    verified_at TIMESTAMP,

    -- 贡献和管理
    submitted_by BIGINT NOT NULL REFERENCES users(id), -- 提交者
    manager_id BIGINT REFERENCES users(id),            -- 管理者（如有）
    is_official BOOLEAN DEFAULT FALSE,                 -- 是否官方管理

    -- 图片和媒体
    image_gallery JSONB DEFAULT '[]',                  -- 图片库
    video_gallery JSONB DEFAULT '[]',                  -- 视频库

    -- 状态控制
    status VARCHAR(20) DEFAULT 'active',               -- active/inactive/closed/under_maintenance
    is_featured BOOLEAN DEFAULT FALSE,                 -- 是否精选推荐
    featured_expires_at TIMESTAMP,                     -- 推荐过期时间

    -- 访问统计
    total_views INTEGER DEFAULT 0,
    total_saves INTEGER DEFAULT 0,
    total_navigations INTEGER DEFAULT 0,

    -- 系统字段
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- 空间索引（必须）
    SPATIAL INDEX idx_geohash (geohash),
    SPATIAL INDEX idx_location (latitude, longitude),

    -- 查询优化索引
    INDEX idx_city_type_status (city, spot_type, status),
    INDEX idx_popularity_featured (popularity_score DESC, is_featured DESC),
    INDEX idx_verification (verification_status, city),
    INDEX idx_current_fishers (current_fishers_count DESC),
    INDEX idx_rating (overall_rating DESC),
    INDEX idx_created (created_at DESC)
) COMMENT='钓点表';
```

### 2.2 实时钓点状态表（高频更新）

```sql
CREATE TABLE spot_realtime_status (
    id BIGSERIAL PRIMARY KEY,
    spot_id BIGINT NOT NULL UNIQUE REFERENCES fishing_spots(id) ON DELETE CASCADE,
    date DATE NOT NULL,                               -- 日期分区

    -- 实时人数统计
    current_fishers_count INTEGER DEFAULT 0,
    fishers_gender_ratio JSONB DEFAULT '{"male": 0, "female": 0}',
    fishers_by_time JSONB DEFAULT '{}',               -- 时段人数分布

    -- 今日鱼情统计
    total_catches_today INTEGER DEFAULT 0,
    catches_by_species JSONB DEFAULT '{}',            -- 鱼种分布
    catches_by_hour JSONB DEFAULT '{}',               -- 时段分布
    avg_catch_weight DECIMAL(6,3) DEFAULT 0,

    -- 今日最佳
    biggest_catch_today JSONB,                        -- 今日最大鱼
    most_active_fisher JSONB,                         -- 今日最活跃钓友

    -- 天气数据
    current_weather JSONB,
    weather_forecast JSONB,

    -- 鱼情预测
    fishing_index TINYINT DEFAULT 50,                 -- 钓鱼指数 0-100
    fishing_tips JSONB DEFAULT '[]',                  -- 钓鱼建议

    -- 系统
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_count INTEGER DEFAULT 0,

    -- 复合主键
    PRIMARY KEY (date, spot_id),

    -- 索引
    INDEX idx_date_spot (date, spot_id),
    INDEX idx_fishing_index (fishing_index DESC),
    INDEX idx_catches_today (total_catches_today DESC)
) COMMENT='钓点实时状态表'
PARTITION BY RANGE (date);  -- 按日期分区，提高查询性能
```

### 2.3 钓点相关功能接口

```python
# 1. 地图页面数据接口（批量获取附近钓点）
@router.get("/map/nearby")
async def get_nearby_spots(
    latitude: float = Query(..., description="纬度"),
    longitude: float = Query(..., description="经度"),
    radius_km: int = Query(10, ge=1, le=100),
    limit: int = Query(20, ge=1, le=100),
    filter_type: Optional[str] = Query(None),
    min_rating: Optional[float] = Query(None, ge=0, le=5),
    db: Session = Depends(get_db)
):
    """
    获取附近钓点（地图页用）
    优化：使用Geohash快速查询 + 缓存
    """
    pass

# 2. 钓点详情页（聚合多表数据）
@router.get("/spots/{spot_id}")
async def get_spot_detail(
    spot_id: int,
    include: str = Query("basic", enum=["basic", "realtime", "reviews", "catches", "all"]),
    db: Session = Depends(get_db)
):
    """
    获取钓点详情
    - basic: 基础信息
    - realtime: 包含实时数据
    - reviews: 包含最新评价
    - catches: 包含最新渔获
    - all: 全部信息
    """
    pass

# 3. 实时状态上报接口
@router.post("/spots/{spot_id}/checkin")
async def spot_checkin(
    spot_id: int,
    action: str = Query(..., enum=["arrive", "leave", "catch"]),
    catch_data: Optional[dict] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    钓点签到/签出/上报渔获
    用于更新实时人数和鱼情
    """
    pass

# 4. 智能推荐钓点
@router.get("/spots/recommend")
async def recommend_spots(
    latitude: float = Query(None),
    longitude: float = Query(None),
    user_id: Optional[int] = Query(None),
    weather_condition: Optional[str] = Query(None),
    time_of_day: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    智能推荐钓点
    基于：
    1. 用户历史偏好
    2. 当前位置
    3. 天气情况
    4. 实时鱼情
    5. 相似用户选择
    """
    pass
```

## 三、渔获模块（强化内容和社区）

### 3.1 渔获表专业优化

```sql
CREATE TABLE catches (
    id BIGSERIAL PRIMARY KEY,

    -- 发布者信息
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    username VARCHAR(50) NOT NULL,                    -- 冗余字段，减少查询
    user_avatar VARCHAR(500),                         -- 冗余字段

    -- 关联钓点
    spot_id BIGINT REFERENCES fishing_spots(id) ON DELETE SET NULL,
    spot_name VARCHAR(50),                            -- 冗余字段
    spot_location JSONB,                              -- 冗余位置信息 {"lat": 30.25, "lng": 120.15}

    -- 渔获基本信息
    title VARCHAR(100) NOT NULL,
    content TEXT,                                     -- 详细描述

    -- 鱼信息
    fish_species VARCHAR(30) NOT NULL,                -- 鱼种
    fish_weight DECIMAL(6,3) NOT NULL,                -- 重量（kg）
    fish_length DECIMAL(6,2),                         -- 长度（cm）
    fish_girth DECIMAL(6,2),                          -- 胸围（cm）
    estimated_age INTEGER,                            -- 估计年龄

    -- 钓获详情
    catch_time TIMESTAMP NOT NULL,                    -- 上鱼时间
    fishing_duration_minutes INTEGER,                 -- 钓了多久
    fishing_method VARCHAR(20),                       -- 钓法
    water_depth DECIMAL(5,2),                         -- 水深

    -- 环境条件
    weather_condition VARCHAR(50),
    temperature DECIMAL(4,1),                         -- 气温
    water_temperature DECIMAL(4,1),                   -- 水温
    air_pressure DECIMAL(6,2),                        -- 气压
    wind_direction VARCHAR(10),
    wind_speed DECIMAL(4,1),
    moon_phase VARCHAR(20),                           -- 月相

    -- 装备信息
    rod_brand VARCHAR(50),
    rod_model VARCHAR(50),
    rod_length DECIMAL(4,2),                          -- 竿长（米）
    reel_brand VARCHAR(50),
    line_type VARCHAR(20),                            -- 线类型
    line_size VARCHAR(10),                            -- 线号
    hook_brand VARCHAR(50),
    hook_size VARCHAR(10),                            -- 钩号
    bait_type VARCHAR(50),                            -- 饵料类型
    bait_brand VARCHAR(50),

    -- 图片和视频
    images JSONB NOT NULL,                            -- 图片列表
    cover_image VARCHAR(500),                         -- 封面图
    videos JSONB DEFAULT '[]',                        -- 视频列表

    -- 标签系统
    tags JSONB DEFAULT '[]',                          -- 标签 ["破纪录", "大物", "新手首条"]
    is_record BOOLEAN DEFAULT FALSE,                  -- 是否个人纪录
    record_type VARCHAR(20),                          -- 纪录类型 weight重量/length长度

    -- 互动统计（冗余字段）
    view_count INTEGER DEFAULT 0,
    like_count INTEGER DEFAULT 0,
    comment_count INTEGER DEFAULT 0,
    share_count INTEGER DEFAULT 0,
    collect_count INTEGER DEFAULT 0,

    -- 审核状态
    audit_status VARCHAR(20) DEFAULT 'pending',       -- pending/approved/rejected
    audit_reason VARCHAR(200),
    audit_by BIGINT REFERENCES users(id),
    audit_at TIMESTAMP,

    -- 精选推荐
    is_featured BOOLEAN DEFAULT FALSE,
    featured_at TIMESTAMP,
    featured_position INTEGER,                        -- 推荐位置

    -- 可见性设置
    visibility VARCHAR(20) DEFAULT 'public',          -- public/private/friends_only
    allow_comments BOOLEAN DEFAULT TRUE,
    allow_sharing BOOLEAN DEFAULT TRUE,

    -- 系统字段
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- 索引优化
    INDEX idx_user_created (user_id, created_at DESC),
    INDEX idx_spot_time (spot_id, catch_time DESC),
    INDEX idx_fish_species (fish_species),
    INDEX idx_weight (fish_weight DESC),
    INDEX idx_featured (is_featured, created_at DESC),
    INDEX idx_hot (like_count DESC, created_at DESC),
    FULLTEXT INDEX idx_search_title (title),
    FULLTEXT INDEX idx_search_content (content),
    INDEX idx_audit_status (audit_status, created_at),

    -- 约束
    CONSTRAINT chk_weight CHECK (fish_weight > 0),
    CONSTRAINT chk_length CHECK (fish_length > 0)
) COMMENT='渔获记录表';

-- 分区表（按月份分区，提高查询性能）
PARTITION BY RANGE (DATE_FORMAT(catch_time, '%Y-%m'));
```

### 3.2 渔获扩展表

```sql
-- 渔获验证表（用于大物验证）
CREATE TABLE catch_verifications (
    id BIGSERIAL PRIMARY KEY,
    catch_id BIGINT NOT NULL UNIQUE REFERENCES catches(id) ON DELETE CASCADE,

    -- 验证信息
    verification_type VARCHAR(20) DEFAULT 'weight',  -- weight重量/length长度/species鱼种
    verification_method VARCHAR(20),                 -- photo照片/video视频/witness见证
    verified_by BIGINT REFERENCES users(id),         -- 验证人
    verified_at TIMESTAMP,

    -- 证据
    evidence_images JSONB DEFAULT '[]',
    witness_users JSONB DEFAULT '[]',                -- 见证人列表

    -- 验证结果
    is_verified BOOLEAN DEFAULT FALSE,
    verification_score INTEGER DEFAULT 0,            -- 可信度评分 0-100
    notes TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 渔获统计表（用于快速统计查询）
CREATE TABLE catch_statistics (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id),
    statistic_date DATE NOT NULL,                     -- 统计日期

    -- 日统计
    daily_catches INTEGER DEFAULT 0,
    daily_total_weight DECIMAL(10,3) DEFAULT 0,
    daily_species_count JSONB DEFAULT '{}',           -- 按鱼种统计

    -- 月统计（冗余）
    monthly_catches INTEGER DEFAULT 0,
    monthly_total_weight DECIMAL(10,3) DEFAULT 0,

    -- 年统计（冗余）
    yearly_catches INTEGER DEFAULT 0,
    yearly_total_weight DECIMAL(10,3) DEFAULT 0,

    -- 个人纪录
    personal_record_species VARCHAR(30),
    personal_record_weight DECIMAL(6,3),

    -- 系统
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE KEY uk_user_date (user_id, statistic_date),
    INDEX idx_date (statistic_date)
);
```

### 3.3 互动系统优化

```sql
-- 互动表（统一管理所有互动）
CREATE TABLE interactions (
    id BIGSERIAL PRIMARY KEY,

    -- 互动主体
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    target_type VARCHAR(20) NOT NULL,                -- catch渔获/comment评论/user用户
    target_id BIGINT NOT NULL,                       -- 目标ID

    -- 互动类型
    interaction_type VARCHAR(20) NOT NULL,           -- like点赞/comment评论/share转发/collect收藏/report举报
    interaction_value INTEGER DEFAULT 1,             -- 互动值（可用于权重计算）

    -- 内容
    content TEXT,                                    -- 评论内容
    metadata JSONB DEFAULT '{}',                     -- 扩展数据

    -- 状态
    is_active BOOLEAN DEFAULT TRUE,                  -- 是否有效（用于取消点赞）

    -- 系统
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- 唯一约束
    UNIQUE KEY uk_interaction (user_id, target_type, target_id, interaction_type),

    -- 索引
    INDEX idx_target (target_type, target_id, created_at DESC),
    INDEX idx_user_target (user_id, target_type),
    INDEX idx_type_created (interaction_type, created_at DESC)
) COMMENT='互动表';

-- 评论回复关系表
CREATE TABLE comment_replies (
    id BIGSERIAL PRIMARY KEY,
    comment_id BIGINT NOT NULL REFERENCES interactions(id) ON DELETE CASCADE,
    reply_to_comment_id BIGINT REFERENCES interactions(id),
    reply_to_user_id BIGINT REFERENCES users(id),

    -- 层级关系
    depth INTEGER DEFAULT 0,                         -- 评论深度
    path VARCHAR(500),                               -- 评论路径 1/2/3

    INDEX idx_comment (comment_id),
    INDEX idx_reply_to (reply_to_comment_id),
    INDEX idx_path (path)
);
```

### 3.4 渔获相关功能接口

```python
# 1. 发布渔获（支持多图、视频、详细数据）
@router.post("/catches")
@rate_limit(limit=10, period=60)  # 限流：60秒最多10次
async def create_catch(
    catch_data: CatchCreate,
    images: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    发布渔获
    特性：
    1. 图片自动压缩和水印
    2. 位置自动解析
    3. 天气数据自动获取
    4. 智能标签生成
    5. 纪录自动识别
    """
    pass

# 2. 渔获瀑布流（多种排序和筛选）
@router.get("/catches/feed")
async def get_catches_feed(
    feed_type: str = Query("latest", enum=["latest", "hot", "following", "nearby"]),
    user_id: Optional[int] = Query(None),
    spot_id: Optional[int] = Query(None),
    fish_species: Optional[str] = Query(None),
    min_weight: Optional[float] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """
    获取渔获瀑布流
    - latest: 最新发布
    - hot: 热门推荐（基于点赞、评论、时间衰减）
    - following: 关注的人
    - nearby: 附近的渔获
    """
    pass

# 3. 渔获详情页（聚合数据）
@router.get("/catches/{catch_id}")
async def get_catch_detail(
    catch_id: int,
    include_comments: bool = Query(True),
    include_related: bool = Query(True),
    db: Session = Depends(get_db)
):
    """
    获取渔获详情
    包括：
    1. 渔获基本信息
    2. 发布者信息
    3. 钓点信息
    4. 评论列表
    5. 相关推荐
    6. 验证信息（如是大物）
    """
    pass

# 4. 大物验证申请
@router.post("/catches/{catch_id}/verify")
async def request_catch_verification(
    catch_id: int,
    verification_data: CatchVerificationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    申请渔获验证
    用于：
    1. 破纪录渔获
    2. 稀有鱼种
    3. 比赛成绩
    """
    pass
```

## 四、需要补充的重要功能

### 4.1 实时通知系统

```sql
CREATE TABLE notifications (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id),
    notification_type VARCHAR(50) NOT NULL,
    title VARCHAR(100),
    content TEXT,
    data JSONB DEFAULT '{}',
    is_read BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMP,
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_user_unread (user_id, is_read, created_at DESC),
    INDEX idx_type_created (notification_type, created_at DESC)
);

-- 通知类型：
-- 1. like: 有人点赞你的渔获
-- 2. comment: 有人评论
-- 3. follow: 有人关注你
-- 4. mention: 有人@你
-- 5. system: 系统通知
-- 6. spot_update: 关注钓点更新
-- 7. record_broken: 纪录被打破
```

### 4.2 搜索服务

```python
# 搜索服务接口
@router.get("/search")
async def global_search(
    q: str = Query(..., min_length=1, max_length=100),
    search_type: str = Query("all", enum=["all", "spots", "catches", "users"]),
    location_filter: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    全局搜索
    支持：
    1. 钓点搜索（名称、地址、鱼种）
    2. 渔获搜索（标题、内容、鱼种）
    3. 用户搜索（昵称、签名）
    4. 智能建议
    """
    pass
```

### 4.3 数据统计和分析

```python
# 数据统计接口
@router.get("/analytics")
async def get_analytics(
    metric: str = Query(..., enum=["user_growth", "spot_popularity", "fish_species", "regional"]),
    timeframe: str = Query("7d", enum=["1d", "7d", "30d", "90d", "1y"]),
    region: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    数据统计和分析
    用于：
    1. 运营分析
    2. 用户行为分析
    3. 钓点热度分析
    4. 鱼种季节性分析
    """
    pass
```

1. **实时性**：钓点实时人数、鱼情
2. **专业性**：详细的渔获数据和环境信息
3. **可扩展性**：分区表、冗余字段、扩展表
4. **用户体验**：智能推荐、快速查询
5. **运营能力**：数据统计、内容管理
6. **性能优化**：索引策略、缓存机制

## 4. 前端架构设计（UniApp + Vue3）

### 4.1 项目结构建议

- 小程序准备
- WECHAT_APPID: "wx4adbe79a0790e1c6"
- WECHAT_SECRET: "68506e2fc25dac31cc043597f2381a36"
- loginUrl: 'https://api.weixin.qq.com/sns/jscode2session'
- 高德地图 key b4198ded17f81fd115b6aebb9411826c

```
├── pages
│   ├── map
│   ├── fishing-spot
│   ├── catch-show
│   ├── mine
├── components
├── api
├── store
├── utils
└── static
```

### 4.2 状态管理

- Pinia
- 用户信息、定位信息全局缓存

---

## 5. 后端架构设计（FastAPI）

### 5.1 项目结构

```
app/
├── main.py
├── core
│   ├── config.py
│   ├── security.py
├── modules
│   ├── user
│   ├── fishing_spot
│   ├── catch_show
├── models
├── schemas
└── services
```

## 8. 部署方案（腾讯云）

### 8.1 后端部署

- Nginx + Uvicorn
- Supervisor / systemd

### 8.2 数据库

- mysql
- 数据库信息
- DB_HOST: "119.45.128.43"
- DB_PORT: 5432
- DB_USER: "postgres"
- DB_PASSWORD: "xkl789."
- DB_NAME: "FishDataBase"
<!-- 表还没创建 -->

### 8.3 对象存储

- 腾讯云 COS
- 数据万象开启压缩
- 数据万象地址 https://fish-1317162040.cos.ap-nanjing.myqcloud.com/

---

## 9. 开发里程碑（建议）

| 阶段     | 内容               |
| -------- | ------------------ |
| 第一阶段 | 登录 + 地图 + 钓点 |
| 第二阶段 | 渔获发布 + 列表    |
| 第三阶段 | 点赞评论           |
| 第四阶段 | 推荐算法           |

---

## 10. 后续扩展方向

- 钓鱼天气模型
- AI 识别鱼种
- 数据分析（个人渔获报告）
- 商业化（钓点推广 / 装备推荐）

---

## 11. 总结

> 渔获秀的核心不是“记录”，而是**让钓鱼更有成就感和社交价值**。

该文档作为 **V1 开发蓝本**，支持持续迭代。
