# 黑名单/白名单 API 详细说明文档

## 目录

- [黑名单类别管理（category）](#黑名单类别管理category)
- [黑名单用户管理（user）](#黑名单用户管理user)
- [白名单用户管理（exclusion）](#白名单用户管理exclusion)
- [数据结构说明（schemas）](#数据结构说明schemas)
- [通用返回结构](#通用返回结构)

---

## 黑名单类别管理（category）

### 1. 查询类别

- **接口**：`GET /blacklist/category/`
- **参数**（Query）：
  - `id`（可选，int）：类别ID，指定时返回单个条目
  - `classification`（可选，int）：类别分类（见[分类枚举](#分类枚举categoryenum)）
  - `offset`（可选，int）：分页偏移量，默认0
  - `limit`（可选，int）：分页条数，默认100
- **请求示例**：
  - 查询所有：`GET /blacklist/category/`
  - 查询ID：`GET /blacklist/category/?id=1`
  - 查询分类：`GET /blacklist/category/?classification=1`
  - 分页：`GET /blacklist/category/?offset=10&limit=20`
- **返回**：
  - 通过ID查询返回单个条目，其他情况返回列表

---

### 2. 创建类别

- **接口**：`POST /blacklist/category/`
- **Body**（JSON）：
    ```json
    {
      "entry_name": "example",
      "classification": 1,
      "describe": "描述信息"
    }
    ```
- **返回**：
  - 成功返回新类别信息
  - entry_name已存在返回错误

---

### 3. 删除类别

- **接口**：`DELETE /blacklist/category/{cat_id}`
- **参数**：
  - `cat_id`：类别ID
- **返回**：
  - 成功返回被删除的类别信息
  - ID不存在返回错误

---

### 4. 更新类别

- **接口**：`PUT /blacklist/category/{cat_id}`
- **Body**（JSON）：
    ```json
    {
      "entry_name": "new_name",
      "classification": 2,
      "describe": "更新描述"
    }
    ```
- **返回**：
  - 成功返回更新后的类别信息
  - ID不存在或参数无效返回错误

---

## 黑名单用户管理（user）

### 1. 批量创建黑名单用户

- **接口**：`POST /blacklist/user/`
- **Body**（JSON）：
    ```json
    [
      {"uid": 123, "category_id": 1},
      {"uid": 456, "category_id": 2}
    ]
    ```
- **返回**：
    ```json
    {
      "code": 201,
      "message": "All records created successfully",
      "data": {
        "success_count": 1,
        "failed_count": 0,
        "skipped_count": 1,
        "skipped_items": [
          {"uid": 456, "category_id": 2}
        ],
        "failed_items": [
          {
            "data": {"uid": 789, "category_id": 3},
            "reason": "xxx错误"
          }
        ]
      }
    }
    ```
- **说明**：
  - 跳过的情况包括：已存在于白名单或黑名单

---

### 2. 查询黑名单用户

- **接口**：`GET /blacklist/user/`
- **参数**（Query）：
  - `uid`（可选）：用户ID
  - `category_id`（可选）：类别ID
  - `classification`（可选）：类别分类（int）
  - `offset`（可选）：分页偏移量
  - `limit`（可选）：分页条数
- **请求示例**：
  - 查询所有：`GET /blacklist/user/`
  - 查询指定用户：`GET /blacklist/user/?uid=123`
  - 查询指定分类：`GET /blacklist/user/?category_id=1`
  - 查询指定分类（通过classification）：`GET /blacklist/user/?classification=1`
  - 查询指定用户和分类：`GET /blacklist/user/?uid=123&category_id=1`
  - 查询指定用户和分类（通过classification）：`GET /blacklist/user/?uid=123&classification=1`
  - 分页：`GET /blacklist/user/?offset=10&limit=20`
- **返回**：
  - 返回符合条件的黑名单记录列表
  - 无记录返回错误

---

### 3. 优化版批量黑名单检查

- **接口**：`POST /blacklist/user/bulk-check-optimized`
- **Body**（JSON）：
    ```json
    [
      {"uid": 123, "category_id": 1},
      {"uid": 456, "category_id": 2}
    ]
    ```
- **返回**：
    ```json
    {
      "code": 200,
      "message": "Success",
      "data": [true, false]
    }
    ```
- **说明**：
  - 返回数组，顺序与请求顺序一致，表示每个用户是否在黑名单中

---

### 4. 删除黑名单用户

- **接口**：`DELETE /blacklist/user/`
- **Body**（JSON）：
    ```json
    [
      {"id": 1},
      {"uid": 123, "category_id": 1}
    ]
    ```
- **返回**：
    ```json
    {
      "code": 200,
      "message": "Successfully deleted 1 records",
      "data": {
        "success_count": 1,
        "failed_count": 0,
        "skipped_count": 1,
        "skipped_items": [
          {"uid": 123, "category_id": 1}
        ],
        "failed_items": [
          {
            "request": {"uid": 456, "category_id": 2},
            "reason": "xxx错误"
          }
        ],
        "deleted_items": [
          {
            "id": 1,
            "uid": 123,
            "category_id": 1,
            "create_time": "2024-06-01T12:00:00"
          }
        ]
      }
    }
    ```

---

## 白名单用户管理（exclusion）

### 1. 批量创建白名单用户

- **接口**：`POST /blacklist/exclusion/`
- **Body**（JSON）：
    ```json
    [
      {"uid": 123, "category_id": 1, "describe": "测试用户1"},
      {"uid": 456, "category_id": 2, "describe": "测试用户2"}
    ]
    ```
- **返回**：
    ```json
    {
      "code": 201,
      "message": "All records created successfully",
      "data": {
        "success_count": 1,
        "failed_count": 0,
        "skipped_count": 1,
        "skipped_items": [
          {"uid": 456, "category_id": 2, "describe": "测试用户2"}
        ],
        "failed_items": [
          {
            "data": {"uid": 789, "category_id": 3, "describe": "xxx"},
            "reason": "xxx错误"
          }
        ],
        "removed_from_blacklist": 1
      }
    }
    ```
- **说明**：
  - 创建白名单时会自动从黑名单移除同样的用户

---

### 2. 查询白名单用户

- **接口**：`GET /blacklist/exclusion/`
- **参数**（Query）：
  - `uid`（可选）：用户ID
  - `category_id`（可选）：类别ID
  - `offset`（可选）：分页偏移量
  - `limit`（可选）：分页条数
- **请求示例**：
  - 查询所有：`GET /blacklist/exclusion/`
  - 查询指定用户：`GET /blacklist/exclusion/?uid=123`
  - 查询指定分类：`GET /blacklist/exclusion/?category_id=1`
  - 查询指定用户和分类：`GET /blacklist/exclusion/?uid=123&category_id=1`
  - 分页：`GET /blacklist/exclusion/?offset=10&limit=20`
- **返回**：
  - 返回符合条件的白名单记录列表
  - 无记录返回错误

---

### 3. 删除白名单用户

- **接口**：`DELETE /blacklist/exclusion/`
- **Body**（JSON）：
    ```json
    [
      {"id": 1},
      {"uid": 123, "category_id": 1}
    ]
    ```
- **返回**：
    ```json
    {
      "code": 200,
      "message": "Record deleted successfully",
      "data": {
        "success_count": 1,
        "failed_count": 0,
        "skipped_count": 1,
        "skipped_items": [
          {"uid": 123, "category_id": 1}
        ],
        "failed_items": [
          {
            "request": {"uid": 456, "category_id": 2},
            "reason": "xxx错误"
          }
        ],
        "deleted_items": [
          {
            "id": 1,
            "uid": 123,
            "category_id": 1,
            "describe": "xxx",
            "create_time": "2024-06-01T12:00:00"
          }
        ]
      }
    }
    ```

---

### 4. 更新白名单用户描述

- **接口**：`PUT /blacklist/exclusion/`
- **Body**（JSON）：
    ```json
    {
      "id": 1,
      "describe": "更新后的描述内容"
    }
    ```
    或
    ```json
    {
      "uid": 123,
      "category_id": 1,
      "describe": "更新后的描述内容"
    }
    ```
- **返回**：
    ```json
    {
      "message": "Record updated successfully",
      "data": {
        "updated_record": {
          "id": 1,
          "uid": 123,
          "category_id": 1,
          "describe": "更新后的描述内容",
          "create_time": "2024-06-01T12:00:00"
        }
      },
      "code": 200
    }
    ```

---

## 数据结构说明（schemas）

### 分类枚举（CategoryEnum）

| 值 | 名称         | 说明       |
|----|--------------|------------|
| 0  | OTHER        | 其他       |
| 1  | EDM          | EDM        |
| 2  | IM           | 即时通讯   |
| 3  | COMMUNITY    | 社区       |
| 4  | OA           | OA系统     |
| 5  | PROFILE      | 画像类     |

---


## 通用返回结构

所有接口均返回如下结构：

```json
{
  "message": "操作结果描述",
  "data": { ... },   // 具体数据内容
  "code": 200        // HTTP状态码
}
```

- 批量操作时，部分成功会返回 `HTTP_207_MULTI_STATUS`。
- 错误时返回详细错误信息。
