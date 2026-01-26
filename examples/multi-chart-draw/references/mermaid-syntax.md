# Mermaid 语法参考

## 目录
1. [基础语法](#基础语法)
2. [流程图](#流程图)
3. [序列图](#序列图)
4. [类图](#类图)
5. [状态图](#状态图)
6. [甘特图](#甘特图)
7. [ER图](#er图)
8. [常见示例](#常见示例)

## 概览
Mermaid 是一种基于文本的图表描述语言，支持多种图表类型，适合快速绘制流程图、序列图等。

## 基础语法

### 代码块格式
```mermaid
graph TD
    A[开始] --> B[处理]
    B --> C[结束]
```

### 方向声明
- `TB` / `TD` - Top to Bottom（从上到下）
- `BT` - Bottom to Top（从下到上）
- `RL` - Right to Left（从右到左）
- `LR` - Left to Right（从左到右）

## 流程图

### 基本节点
```mermaid
graph LR
    id1[矩形节点]
    id2(圆角节点)
    id3[圆形节点]
    id4>非对称节点]
    id5{菱形节点}
```

### 连接关系
```mermaid
graph LR
    A --> B          # 箭头
    A --- B          # 无箭头线
    A -->|标签| B    # 带标签的箭头
    A ==>|标签| B    # 粗箭头
    A -.->|标签| B   # 虚线箭头
```

### 子图
```mermaid
graph LR
    subgraph 子图1
        A --> B
    end
    subgraph 子图2
        C --> D
    end
    B --> C
```

## 序列图

### 基本语法
```mermaid
sequenceDiagram
    participant Alice
    participant Bob
    Alice->>Bob: Hello Bob, how are you?
    Bob-->>Alice: I am good thanks!
```

### 激活框
```mermaid
sequenceDiagram
    A->>B: 激活 B
    activate B
    B-->>A: 响应
    deactivate B
```

### 循环和条件
```mermaid
sequenceDiagram
    A->>B: 请求
    loop 检查条件
        B-->>A: 检查结果
    end
    alt 条件满足
        B->>A: 成功响应
    else 条件不满足
        B->>A: 失败响应
    end
```

## 类图

### 基本语法
```mermaid
classDiagram
    class Animal{
        +String name
        +int age
        +eat()
        +sleep()
    }
    class Dog{
        +bark()
    }
    Animal <|-- Dog
```

### 关系类型
- `<|--` - 继承
- `*--` - 组合
- `o--` - 聚合
- `-->` - 关联
- `..>` - 依赖

## 状态图

### 基本语法
```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> Processing
    Processing --> Success
    Processing --> Failure
    Success --> [*]
    Failure --> Idle
```

## 甘特图

### 基本语法
```mermaid
gantt
    title 项目甘特图
    dateFormat  YYYY-MM-DD
    section 设计
    需求分析       :a1, 2024-01-01, 3d
    UI 设计        :a2, after a1, 5d
    section 开发
    后端开发       :b1, after a2, 7d
    前端开发       :b2, after a2, 6d
```

## ER图

### 基本语法
```mermaid
erDiagram
    CUSTOMER ||--o{ ORDER : places
    ORDER ||--|{ LINE_ITEM : contains
    PRODUCT ||--o{ LINE_ITEM : "is in"
```

### 关系类型
- `||--||` - 一对一
- `||--|{` - 一对多
- `||--o{` - 一对多（可选）
- `}|--||` - 多对一
- `}o--||` - 多对一（可选）

## 常见示例

### 示例 1：用户注册流程
```mermaid
flowchart TD
    A[开始] --> B{是否已有账号}
    B -->|是| C[登录]
    B -->|否| D[填写注册信息]
    D --> E{信息是否完整}
    E -->|否| D
    E -->|是| F[发送验证码]
    F --> G[输入验证码]
    G --> H{验证码是否正确}
    H -->|否| F
    H -->|是| I[注册成功]
    C --> J[跳转首页]
    I --> J
```

### 示例 2：API 调用序列
```mermaid
sequenceDiagram
    autonumber
    Client->>API: 发起请求
    API->>Auth: 验证令牌
    Auth-->>API: 验证结果
    alt 令牌有效
        API->>Database: 查询数据
        Database-->>API: 返回数据
        API-->>Client: 200 OK
    else 令牌无效
        API-->>Client: 401 Unauthorized
    end
```

### 示例 3：系统架构
```mermaid
graph TB
    subgraph 前端
        Web[Web应用]
        Mobile[移动应用]
    end
    subgraph 后端
        API[API网关]
        Service1[用户服务]
        Service2[订单服务]
    end
    subgraph 数据层
        Redis[Redis缓存]
        DB[(MySQL数据库)]
    end
    
    Web --> API
    Mobile --> API
    API --> Service1
    API --> Service2
    Service1 --> Redis
    Service2 --> Redis
    Service1 --> DB
    Service2 --> DB
```

### 示例 4：项目进度甘特图
```mermaid
gantt
    title 软件开发项目进度
    dateFormat  YYYY-MM-DD
    section 需求阶段
    需求调研       :done, req1, 2024-01-01, 5d
    需求分析       :done, req2, after req1, 3d
    需求评审       :active, req3, after req2, 2d
    section 设计阶段
    概要设计       :des1, after req3, 4d
    详细设计       :des2, after des1, 5d
    section 开发阶段
    后端开发       :dev1, after des2, 10d
    前端开发       :dev2, after des2, 8d
    section 测试阶段
    单元测试       :test1, after dev1, 3d
    集成测试       :test2, after test1, 4d
    section 部署
    上线部署       :deploy, after test2, 2d
```

## 注意事项
- 节点名称必须唯一
- 箭头方向要符合逻辑
- 复杂图表建议使用子图组织
- 中文支持：Mermaid 原生支持中文
- 输出格式：推荐 SVG（矢量图）或 PNG（位图）
