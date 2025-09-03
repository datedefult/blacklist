# 黑名单/白名单接口文档

本文件汇总黑名单类别、黑名单用户、白名单用户相关接口，包括接口地址、请求参数、请求示例、返回结果。

接口地址：无

---

## 一、黑名单类别管理（category）

### 1. 查询类别

- **接口地址**：`GET /blacklist/category/`
- **请求参数（Query）**：

  | 参数名         | 类型 | 是否必填 | 说明         |
  |----------------|------|----------|--------------|
  | id             | int  | 否       | 类别ID       |
  | classification | int  | 否       | 类别分类     |
  | offset         | int  | 否       | 分页偏移量    |
  | limit          | int  | 否       | 分页条数      |


- **黑名单类别枚举说明（classification）**

    | 值 | 名称         | 说明       |
    |----|--------------|------------|
    | 0  | OTHER        | 其他       |
    | 1  | EDM          | EDM        |
    | 2  | IM           | 即时通讯   |
    | 3  | COMMUNITY    | 社区       |
    | 4  | OA           | OA系统     |
    | 5  | PROFILE      | 画像类     |




- **请求示例**：

  ```
  GET /blacklist/category/?classification=1&offset=0&limit=10
  ```

- **返回结果**：

  ```json
  {
    "message": "Successfully retrieved categories",
    "data": [
      {
        "id": 1,
        "classification": 1,
        "cls_name": "EDM",
        "entry_name": "邮件黑名单",
        "describe": "EDM相关黑名单",
        "create_time": "2024-06-01T12:00:00",
        "update_time": "2024-06-01T12:00:00"
      }
    ],
    "code": 200
  }
  ```

---

### 2. 创建类别

- **接口地址**：`POST /blacklist/category/`
- **请求参数（Body, JSON）**：

  | 参数名         | 类型   | 是否必填 | 说明     |
  |----------------|--------|----------|----------|
  | entry_name     | string | 是       | 类别名称 |
  | classification | int    | 是       | 类别分类 |
  | describe       | string | 否       | 描述     |

- **请求示例**：

  ```json
  {
    "entry_name": "example",
    "classification": 1,
    "describe": "描述信息"
  }
  ```

- **返回结果**：

  ```json
  {
    "message": "Category insert successfully",
    "data": {
      "id": 2,
      "classification": 1,
      "cls_name": "EDM",
      "entry_name": "example",
      "describe": "描述信息",
      "create_time": "2024-06-01T12:10:00",
      "update_time": "2024-06-01T12:10:00"
    },
    "code": 200
  }
  ```

---

### 3. 删除类别

- **接口地址**：`DELETE /blacklist/category/{cat_id}`
- **请求参数（Path）**：

  | 参数名 | 类型 | 是否必填 | 说明   |
  |--------|------|----------|--------|
  | cat_id | int  | 是       | 类别ID |

- **请求示例**：

  ```
  DELETE /blacklist/category/2
  ```

- **返回结果**：

  ```json
  {
    "message": "Category with ID 2 has been successfully deleted",
    "data": {
      "id": 2,
      "classification": 1,
      "cls_name": "EDM",
      "entry_name": "example",
      "describe": "描述信息",
      "create_time": "2024-06-01T12:10:00",
      "update_time": "2024-06-01T12:10:00"
    },
    "code": 200
  }
  ```

---

### 4. 更新类别

- **接口地址**：`PUT /blacklist/category/{cat_id}`
- **请求参数（Path）**：

  | 参数名 | 类型 | 是否必填 | 说明   |
  |--------|------|----------|--------|
  | cat_id | int  | 是       | 类别ID |

- **请求参数（Body, JSON）**：

  | 参数名         | 类型   | 是否必填 | 说明     |
  |----------------|--------|----------|----------|
  | entry_name     | string | 否       | 新类别名 |
  | classification | int    | 否       | 新分类   |
  | describe       | string | 否       | 新描述   |

- **请求示例**：

  ```json
  {
    "entry_name": "new_name",
    "classification": 2,
    "describe": "更新描述"
  }
  ```

- **返回结果**：

  ```json
  {
    "message": "Category updated successfully",
    "data": {
      "id": 2,
      "classification": 2,
      "cls_name": "IM",
      "entry_name": "new_name",
      "describe": "更新描述",
      "create_time": "2024-06-01T12:10:00",
      "update_time": "2024-06-01T12:20:00"
    },
    "code": 200
  }
  ```

---

## 二、黑名单用户管理（user）

### 1. 批量创建黑名单

- **接口地址**：`POST /blacklist/user/`
- **请求参数（Body, JSON）**：

  | 参数名       | 类型   | 是否必填 | 说明         |
  |--------------|--------|----------|--------------|
  | target_id    | int    | 是       | 目标类型     |
  | target_value | string | 是       | 目标值       |
  | category_id  | int    | 是       | 类别ID       |
- 说明：
    - 目标类型：1-uid,2-设备,3-...
- **请求示例**：

  ```json
  [
    {"target_id": 1, "target_value": "123", "category_id": 1},
    {"target_id": 1, "target_value": "456", "category_id": 2}
  ]
  ```

- **返回结果**：

  ```json
  {
    "code": 201,
    "message": "操作结果描述",
    "data": {
      "success_count": 1,
      "failed_count": 0,
      "skipped_count": 1,
      "skipped_items": [
        {"data": {"target_id": 1, "target_value": "456", "category_id": 2}, "reason": "已存在相同黑名单记录"}
      ],
      "failed_items": [
        {
          "data": {"target_id": 1, "target_value": "789", "category_id": 3},
          "reason": "分类ID不存在"
        }
      ]
    }
  }
  ```

---

### 2. 查询黑名单

- **接口地址**：`GET /blacklist/user/`
- **请求参数（Query）**：

  | 参数名         | 类型   | 是否必填 | 说明         |
  |----------------|--------|----------|--------------|
  | target_id      | int    | 否       | 目标类型     |
  | target_value   | string | 否       | 目标值       |
  | category_id    | int    | 否       | 类别ID       |
  | classification | int    | 否       | 类别分类     |
  | offset         | int    | 否       | 分页偏移量   |
  | limit          | int    | 否       | 分页条数     |

- **请求示例**：

  ```
  GET /blacklist/user/?target_id=1&target_value=123&category_id=1
  ```

- **返回结果**：

  ```json
  {
    "message": "Successfully retrieved blacklist records",
    "data": [
      {
        "id": 1,
        "target_id": 1,
        "target_value": "123",
        "category_id": 1,
        "create_time": "2024-06-01T12:00:00"
      }
    ],
    "code": 200
  }
  ```

---

### 3. 批量检查黑名单

- **接口地址**：`POST /blacklist/user/bulk-check-optimized`
- **请求参数（Body, JSON）**：

  | 参数名       | 类型   | 是否必填 | 说明         |
  |--------------|--------|----------|--------------|
  | target_id    | int    | 是       | 目标类型     |
  | target_value | string | 是       | 目标值       |
  | category_id  | int    | 是       | 类别ID       |

- **请求示例**：

  ```json
  [
    {"target_id": 1, "target_value": "123", "category_id": 1},
    {"target_id": 1, "target_value": "456", "category_id": 2}
  ]
  ```

- **返回结果**：

  ```json
  {
    "code": 200,
    "message": "Success",
    "data": [true, false]
  }
  ```

---

### 4. 删除黑名单

- **接口地址**：`DELETE /blacklist/user/`
- **请求参数（Body, JSON）**：

  | 参数名       | 类型   | 是否必填 | 说明         |
  |--------------|--------|----------|--------------|
  | id           | int    | 否       | 记录ID       |
  | target_id    | int    | 否       | 目标类型     |
  | target_value | string | 否       | 目标值       |
  | category_id  | int    | 否       | 类别ID       |

- **请求示例**：

  ```json
  [
    {"id": 1},
    {"target_id": 1, "target_value": "123", "category_id": 1}
  ]
  ```

- **返回结果**：

  ```json
  {
    "code": 200,
    "message": "Successfully deleted 1 records",
    "data": {
      "success_count": 1,
      "failed_count": 0,
      "skipped_count": 1,
      "skipped_items": [
        {"target_id": 1, "target_value": "123", "category_id": 1}
      ],
      "failed_items": [
        {
          "request": {"target_id": 1, "target_value": "456", "category_id": 2},
          "reason": "xxx错误"
        }
      ],
      "deleted_items": [
        {
          "id": 1,
          "target_id": 1,
          "target_value": "123",
          "category_id": 1,
          "create_time": "2024-06-01T12:00:00"
        }
      ]
    }
  }
  ```

---

## 三、白名单管理（exclusion）

### 1. 批量创建白名单

- **接口地址**：`POST /blacklist/exclusion/`
- **请求参数（Body, JSON）**：

  | 参数名       | 类型   | 是否必填 | 说明         |
  |--------------|--------|----------|--------------|
  | target_id    | int    | 是       | 目标类型     |
  | target_value | string | 是       | 目标值       |
  | category_id  | int    | 是       | 类别ID       |
  | describe     | string | 否       | 描述         |
  | level        | int    | 否       | 清理级别（默认3）     |

- 说明：
    - 目标类型：1-uid,2-设备,3-...
    - 黑名单级别：1-全部过滤，2-按照所属的classification过滤，3-仅按照category过滤(默认级别)
- **请求示例**：

  ```json
  [
    {"target_id": 1, "target_value": "123", "category_id": 1, "describe": "测试用户1"},
    {"target_id": 1, "target_value": "456", "category_id": 2, "describe": "测试用户2"}
  ]
  ```

- **返回结果**：

  ```json
  {
    "code": 201,
    "message": "All records created successfully",
    "data": {
      "success_count": 1,
      "failed_count": 0,
      "skipped_count": 1,
      "skipped_items": [
        {"target_id": 1, "target_value": "456", "category_id": 2, "describe": "测试用户2"}
      ],
      "failed_items": [
        {
          "data": {"target_id": 1, "target_value": "789", "category_id": 3, "describe": "xxx"},
          "reason": "xxx错误"
        }
      ],
      "removed_from_blacklist": 1
    }
  }
  ```

---

### 2. 查询白名单

- **接口地址**：`GET /blacklist/exclusion/`
- **请求参数（Query）**：

  | 参数名       | 类型   | 是否必填 | 说明         |
  |--------------|--------|----------|--------------|
  | target_id    | int    | 否       | 目标类型     |
  | target_value | string | 否       | 目标值       |
  | category_id  | int    | 否       | 类别ID       |
  | offset       | int    | 否       | 分页偏移量   |
  | limit        | int    | 否       | 分页条数     |

- **请求示例**：

  ```
  GET /blacklist/exclusion/?target_id=1&target_value=123&category_id=1
  ```

- **返回结果**：

  ```json
  {
    "message": "Successfully retrieved exclusion data",
    "data": [
      {
        "id": 1,
        "target_id": 1,
        "target_value": "123",
        "category_id": 1,
        "describe": "测试用户1",
        "level": 3,
        "create_time": "2024-06-01T12:00:00"
      }
    ],
    "code": 200
  }
  ```

---

### 3. 删除白名单

- **接口地址**：`DELETE /blacklist/exclusion/`
- **请求参数（Body, JSON）**：

  | 参数名       | 类型   | 是否必填 | 说明         |
  |--------------|--------|----------|--------------|
  | id           | int    | 否       | 记录ID       |
  | target_id    | int    | 否       | 目标类型     |
  | target_value | string | 否       | 目标值       |
  | category_id  | int    | 否       | 类别ID       |
    
   id或者（target_id,target_value）至少出现一个，全都出现则以id为准
- **请求示例**：

  ```json
  [
    {"id": 1},
    {"target_id": 1, "target_value": "123", "category_id": 1}
  ]
  ```

- **返回结果**：

  ```json
  {
    "code": 200,
    "message": "Record deleted successfully",
    "data": {
      "success_count": 1,
      "failed_count": 0,
      "skipped_count": 1,
      "skipped_items": [
        {"target_id": 1, "target_value": "123", "category_id": 1}
      ],
      "failed_items": [
        {
          "request": {"target_id": 1, "target_value": "456", "category_id": 2},
          "reason": "xxx错误"
        }
      ],
      "deleted_items": [
        {
          "id": 1,
          "target_id": 1,
          "target_value": "123",
          "category_id": 1,
          "describe": "xxx",
          "level": 3,
          "create_time": "2024-06-01T12:00:00"
        }
      ]
    }
  }
  ```

---

### 4. 更新白名单用户

- **接口地址**：`PUT /blacklist/exclusion/`
- **请求参数（Body, JSON）**：

  | 参数名       | 类型   | 是否必填 | 说明         |
  |--------------|--------|----------|--------------|
  | id           | int    | 否       | 记录ID       |
  | target_id    | int    | 否       | 目标类型     |
  | target_value | string | 否       | 目标值       |
  | category_id  | int    | 否       | 类别ID       |
  | describe     | string | 否       | 新描述       |
  | level        | int    | 否       | 新级别       |

  id或者（target_id,target_value）至少出现一个，全都出现则以id为准

- **请求示例**：

  ```json
  {
    "id": 1,
    "describe": "更新后的描述内容"
  }
  ```

  或

  ```json
  {
    "target_id": 1,
    "target_value": "123",
    "category_id": 1,
    "describe": "更新后的描述内容",
    "level": 2
  }
  ```

- **返回结果**：

  ```json
  {
    "message": "Update successful and cleaned 3 blacklist records",
    "data": {
      "updated_record": {
        "id": 1,
        "target_id": 1,
        "target_value": "123",
        "category_id": 1,
        "level": 2,
        "describe": "更新后的描述内容",
        "create_time": "2024-06-01T12:00:00"
      },
      "removed_from_blacklist": 3
    },
    "code": 200
  }
  ```

