# 后端API接口文档

## 基础信息

- 基础URL: `http://your-api-domain/api/v1`
- 所有请求需要在header中携带认证token：
  ```
  Authorization: Bearer your_access_token
  ```

## 1. 认证相关 API

### 1.1 管理员登录
- **接口**: `/auth/login`
- **方法**: POST
- **Content-Type**: `application/x-www-form-urlencoded`
- **参数**:
  ```json
  {
    "username": "管理员用户名",
    "password": "管理员密码"
  }
  ```
- **响应**:
  ```json
  {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1...",
    "token_type": "bearer"
  }
  ```

## 2. 用户管理 API

### 2.1 获取用户列表
- **接口**: `/users`
- **方法**: GET
- **参数**:
  - `skip`: 分页起始位置（可选，默认0）
  - `limit`: 每页数量（可选，默认10）
- **响应**:
  ```json
  [
    {
      "id": 1,
      "platform_user_id": "123456789",
      "username": "user1",
      "tg_first_name": "First",
      "tg_last_name": "Last",
      "tg_language_code": "en",
      "tg_is_bot": false,
      "last_interaction": "2023-12-24T10:00:00",
      "created_at": "2023-12-24T10:00:00",
      "note": "用户备注",
      "tags": [
        {
          "id": 1,
          "name": "VIP"
        }
      ]
    }
  ]
  ```

### 2.2 同步Telegram用户
- **接口**: `/users/sync`
- **方法**: GET
- **响应**:
  ```json
  {
    "new_users": 5,
    "updated_users": 10,
    "total_updates": 15
  }
  ```

### 2.3 获取用户统计
- **接口**: `/users/stats`
- **方法**: GET
- **响应**:
  ```json
  {
    "total_users": 100,
    "active_users_today": 50
  }
  ```

### 2.4 搜索用户
- **接口**: `/users/search`
- **方法**: GET
- **参数**:
  - `keyword`: 搜索关键词
- **响应**: 同用户列表格式

### 2.5 获取用户增长图表数据
- **接口**: `/users/stats/chart`
- **方法**: GET
- **参数**:
  - `days`: 天数（可选，默认7）
- **响应**:
  ```json
  {
    "data": [
      {
        "date": "2023-12-24",
        "count": 10
      }
    ]
  }
  ```

### 2.6 更新用户备注
- **接口**: `/users/{user_id}/note`
- **方法**: PUT
- **参数**:
  - `note`: 备注内容
- **响应**: 更新后的用户信息

### 2.7 添加用户标签
- **接口**: `/users/{user_id}/tags`
- **方法**: POST
- **参数**:
  ```json
  {
    "tags": ["VIP", "新用户"]
  }
  ```
- **响应**: 更新后的用户信息

### 2.8 发送消息给用户
- **接口**: `/users/{user_id}/message`
- **方法**: POST
- **参数**:
  ```json
  {
    "text": "消息内容",
    "parse_mode": "HTML"  // 可选：HTML, Markdown
  }
  ```

## 3. 服务器管理 API

### 3.1 添加服务器信息
- **接口**: `/servers/{user_id}`
- **方法**: POST
- **参数**:
  ```json
  {
    "product_type": "VPS",
    "system": "Ubuntu 20.04",
    "configs": ["2核4G", "100Mbps"],
    "server_ips": ["1.2.3.4", "5.6.7.8"],
    "server_port": 22,
    "server_username": "root",
    "server_password": "password123",
    "start_date": "2023-12-24T00:00:00",  // 可选
    "extra_info": {}  // 可选的额外信息
  }
  ```
- **响应**: 创建的服务器信息

### 3.2 续期服务器
- **接口**: `/servers/{user_id}/{server_id}/renew`
- **方法**: POST
- **参数**:
  ```json
  {
    "admin_password": "管理员密码"
  }
  ```
- **响应**:
  ```json
  {
    "status": "success",
    "message": "续期成功",
    "old_expire_date": "2023-12-24T00:00:00",
    "new_expire_date": "2024-01-24T00:00:00"
  }
  ```

### 3.3 删除服务器
- **接口**: `/servers/{user_id}/{server_id}`
- **方法**: DELETE
- **参数**:
  - `admin_password`: 管理员密码
- **响应**:
  ```json
  {
    "status": "success",
    "message": "服务器已删除"
  }
  ```

### 3.4 获取服务器信息汇总
- **接口**: `/servers/summary`
- **方法**: GET
- **响应**:
  ```json
  {
    "total_servers": 100,
    "users": [
      {
        "user_id": 1,
        "username": "user1",
        "server_count": 2,
        "servers": [
          {
            "id": 1,
            "ips": ["1.2.3.4"],
            "port": 22,
            "username": "root",
            "product_type": "VPS",
            "system": "Ubuntu 20.04",
            "configs": ["2核4G"],
            "created_at": "2023-12-24T00:00:00"
          }
        ]
      }
    ],
    "systems": {
      "Ubuntu 20.04": 50,
      "CentOS 7": 30
    },
    "configs": {
      "2核4G": 40,
      "4核8G": 30
    }
  }
  ```

## 4. 机器人配置 API

### 4.1 获取机器人配置列表
- **接口**: `/bot/config`
- **方法**: GET
- **响应**:
  ```json
  [
    {
      "id": 1,
      "bot_name": "TestBot",
      "bot_token": "123456:ABC-DEF...",
      "bot_username": "test_bot",
      "webhook_url": "https://example.com/webhook",
      "status": "active",
      "last_check_time": "2023-12-24T00:00:00",
      "error_message": null
    }
  ]
  ```

### 4.2 添加机器人配置
- **接口**: `/bot/config`
- **方法**: POST
- **参数**:
  ```json
  {
    "bot_name": "TestBot",
    "bot_token": "123456:ABC-DEF...",
    "webhook_url": "https://example.com/webhook"  // 可选
  }
  ```
- **响应**: 创建的机器人配置

### 4.3 测试机器人配置
- **接口**: `/bot/config/{config_id}/test`
- **方法**: POST
- **响应**:
  ```json
  {
    "ok": true,
    "result": {
      "username": "test_bot"
    }
  }
  ```

## 5. 定时任务 API

### 5.1 获取任务配置列表
- **接口**: `/tasks`
- **方法**: GET
- **响应**:
  ```json
  [
    {
      "id": 1,
      "task_name": "update_server_status",
      "cron_expression": "0 0 * * *",
      "is_active": true,
      "last_run_time": "2023-12-24T00:00:00"
    }
  ]
  ```

### 5.2 添加任务配置
- **接口**: `/tasks`
- **方法**: POST
- **参数**:
  ```json
  {
    "task_name": "update_server_status",
    "cron_expression": "0 0 * * *",
    "is_active": true
  }
  ```
- **响应**: 创建的任务配置

### 5.3 手动执行任务
- **接口**: `/tasks/{task_id}/run`
- **方法**: POST
- **响应**:
  ```json
  {
    "status": "success",
    "message": "任务执行完成"
  }
  ```

## 错误处理

所有API在发生错误时会返回以下格式的响应：

```json
{
  "detail": "错误信息描述"
}
```

常见HTTP状态码：
- 400: 请求参数错误
- 401: 未认证或认证失败
- 403: 权限不足
- 404: 资源不存在
- 500: 服务器内部错误

## 注意事项

1. 所有请求必须携带有效的认证token
2. 涉及敏感操作（如删除、续期）需要提供管理员密码
3. 日期时间格式统一使用ISO 8601格式
4. 分页接口默认每页10条数据
5. 文本消息支持HTML和Markdown格式
6. 服务器配置信息应当加密传输
7. 建议使用HTTPS协议确保数据传输安全

## 开发建议

1. 使用拦截器统一处理认证token
2. 实现请求重试机制
3. 添加请求超时处理
4. 实现错误统一处理
5. 添加请求/响应日志
6. 实现数据缓存机制
7. 添加请求节流/防抖处理

## 调试工具

推荐使用以下工具进行API调试：
1. Postman
2. curl
3. 浏览器开发者工具

## 示例代码

### JavaScript/TypeScript (Axios)

```typescript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://your-api-domain/api/v1',
  timeout: 5000,
});

// 添加认证token
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// 登录示例
async function login(username: string, password: string) {
  const formData = new FormData();
  formData.append('username', username);
  formData.append('password', password);
  
  const response = await api.post('/auth/login', formData);
  return response.data;
}

// 获取用户列表示例
async function getUsers(skip = 0, limit = 10) {
  const response = await api.get('/users', {
    params: { skip, limit }
  });
  return response.data;
}

// 添加服务器示例
async function addServer(userId: number, serverInfo: any) {
  const response = await api.post(`/servers/${userId}`, serverInfo);
  return response.data;
}
```

### Python (requests)

```python
import requests

class API:
    def __init__(self, base_url, token=None):
        self.base_url = base_url
        self.session = requests.Session()
        if token:
            self.session.headers.update({
                'Authorization': f'Bearer {token}'
            })

    def login(self, username, password):
        response = self.session.post(
            f'{self.base_url}/auth/login',
            data={'username': username, 'password': password}
        )
        return response.json()

    def get_users(self, skip=0, limit=10):
        response = self.session.get(
            f'{self.base_url}/users',
            params={'skip': skip, 'limit': limit}
        )
        return response.json()

    def add_server(self, user_id, server_info):
        response = self.session.post(
            f'{self.base_url}/servers/{user_id}',
            json=server_info
        )
        return response.json()
```

## 更新日志

### v1.0.0 (2023-12-24)
- 初始版本发布
- 完整的用户管理功能
- 服务器管理系统
- 机器人配置功能
- 定时任务管理

## 联系方式

如有API相关问题，请联系：
- 技术支持邮箱：support@example.com
- 技术支持电话：+1 234 567 890
