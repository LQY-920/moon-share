# 子系统设计模板：12 节目录逐节讲透

> 本文是"moon-share"系列第 04 篇。姊妹篇是 [01 四层设计法](../01-四层设计法/gzh.md)。

## 一、先看母本

我上个月写了一份 S1.1（账户与身份）子系统的设计文档。它的目录是这样的：

```
一、定位与边界
二、关键决策
三、项目结构
四、数据模型
五、API 契约
六、会话机制
七、安全与审计
八、错误处理
九、测试策略
十、依赖清单
十一、演进路径
十二、未决项
```

写完这份文档之后，我意识到它可以当模板用——下次设计任何子系统，套这个目录，比从零想快得多。

这篇文章逐节讲：**每一节在防什么坑、少了哪节会出什么问题**。

## 二、第一原则：Design 不是 Plan，Design 不是代码

Design 层只回答"长什么样"，不回答"怎么做"。Plan 层才回答"先做什么、按什么顺序"。Implementation 层才开始写代码。

最容易犯的错误是 Design 层直接跳进代码细节：先想怎么写、想用什么库、想用什么框架。这叫"从实现倒推设计"，设计出来的文档一定带着技术栈偏见。

Design 层要从**业务语义**出发：先想这个子系统服务什么用户、提供什么能力、数据怎么流转。然后到了 Plan 层才问"用什么技术栈、什么顺序实现"。

这句话是整个 Design 层的方法论锚点，记住它，后面的每一节都在服务于这个原则。

## 三、第一节：定位与边界

### 这一节在防什么

防 AI 把邻居子系统的功能夹带进来。

防自己时间久了忘了"这个子系统该做什么、不该做什么"。

### 标准结构

**三部分**：

1. **M0 现实目标**：这次要解决什么问题，只做一版还是完整版。限定粒度，比如"只服务一个账号（作者本人），代码按多用户平台形状预留"。
2. **不在本子系统做的事**：一张表，列出所有会被误认为属于本子系统的事项，明确归谁。
3. **明确的前置依赖和后置依赖**：本模块依赖谁、谁依赖本模块。

### 为什么要单独写"不在本子系统做的事"

这是 [03 明确不做什么](../03-明确不做什么/gzh.md) 的具体落地。

S1.1 Identity 文档的 1.2 小节有 7 项：

```
| 事项                         | 归属                         |
|-----------------------------|------------------------------|
| 角色/权限策略引擎            | S1.2 Policy                  |
| 审计事件的订阅与存储         | S1.3 Audit (S1.1 只发布事件)  |
| 计费与配额采集               | S1.4 Billing                 |
| OAuth/SSO 具体 provider 接入 | 延后子系统 (S1.1 只留接口层)  |
| 邮箱发送服务                 | 延后（M0 只留占位路由）       |
| 前端登录/设置页面            | 前端形态（L4）负责            |
```

每一项都写"归谁做"，不只说"不是我做"。

### 少了这一节会怎样

- AI 在 Design 阶段会不自觉地往里面塞邻居子系统的功能
- 三周后你回看，不知道边界在哪，两边各做一半，数据重复

## 四、第二节：关键决策

### 这一节在防什么

防 Design 文档变成"技术细节清单"而不是"设计决策记录"。

防 AI 把"用什么"当成答案，把"为什么选这个"当废话。

### 标准结构

三列表：维度 | 决策 | 排除的替代

（见 [02 关键决策表](../02-关键决策表/gzh.md) 全文）

### 这一节和定位与边界的区别

"定位与边界"回答的是**子系统层面的边界**（本子系统做什么、不做什么）。

"关键决策"回答的是**子系统内部的技术选择**（用这个不用那个、因为 X 所以选 Y）。

两者是不同的抽象层次。定位与边界 L2 层，关键决策 L3 层。

### 少了这一节会怎样

- 换了技术栈设计文档就废了
- 三个月后你忘记为什么选这个，AI 在 Plan 阶段重新打开讨论
- 排除了什么没有记录，未来 AI 把排除项偷偷加回来

## 五、第三节：项目结构

### 这一节在防什么

防设计与实现脱节——文档写的是一套目录结构，代码写的是另一套。

防多人协作时没有"模块内依赖方向"的约定，各自按自己的理解写，最后耦合成一团。

### 标准结构

文件树 + 每层含义说明 + 关键约束

S1.1 Identity 的项目结构（部分）：

```
apps/api/src/
├── modules/
│   └── identity/               # 本模块对外只暴露 routes.ts、events.ts、require-session.ts
│       ├── routes.ts
│       ├── controllers/        # HTTP 入口
│       ├── services/           # 业务用例，不互相调用
│       ├── repositories/       # Kysely 查询
│       ├── domain/             # 纯类型/值对象/错误
│       └── events.ts           # EventEmitter + AuthEvent 定义
├── core/
│   ├── db.ts                   # MySQL 连接池
│   ├── config.ts               # .env 读取 + Zod 校验
│   └── errors.ts               # 基类 AppError
└── middleware/
    └── require-session.ts      # 守卫中间件，给其他模块用
```

关键约束：
- 依赖方向：`routes → controllers → services → repositories → db`，只下行，不反向
- 本模块对外只暴露三个文件（`routes.ts`、`events.ts`、`require-session.ts`）

### 为什么要单独列"对外暴露"

这是设计文档，不是代码。Design 阶段就定好"哪些东西是公共 API"，可以让别的模块放心依赖，让不该依赖的别依赖。

### 少了这一节会怎样

- 每个人按自己喜好组织目录，最后模块边界模糊
- 没有依赖方向约束，循环依赖悄悄长出来
- 其他模块不知道能依赖什么、不能依赖什么

## 六、第四节：数据模型

### 这一节在防什么

防 DDL 只写字段，不写设计意图。

防字段名产生歧义（比如 `status` 字段是 ENUM 还是布尔？值有哪些？）。

防迁移策略没有提前想好。

### 标准结构

**1. 表结构 + 约束**（直接贴 DDL）

```sql
CREATE TABLE users (
  id              CHAR(26)      NOT NULL,  -- ULID
  email           VARCHAR(255)  NOT NULL,
  email_verified  TINYINT(1)    NOT NULL DEFAULT 0,
  password_hash   VARCHAR(255)  NULL,       -- 纯 OAuth 账户可为 NULL
  display_name    VARCHAR(64)   NOT NULL,
  status          ENUM('active','disabled','deleted') NOT NULL DEFAULT 'active',
  created_at      DATETIME(3)   NOT NULL,
  updated_at      DATETIME(3)   NOT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uq_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

**2. 约定与理由**（每个字段 + 每条约束都有解释）

```
- 主键 ULID：按时间自然排序，URL 安全，不泄露规模。
- 时间列统一 DATETIME(3)：毫秒精度，审计够用；避免 TIMESTAMP 时区坑。
- password_hash 允许 NULL：为未来纯 OAuth 账户预留。
- sessions.token_hash 只存哈希：泄库时 token 不可逆推。
- sessions.revoked_at 软删：保留审计轨迹，30 天后由清理任务物理删除。
```

**3. 迁移策略**

- 工具选型（比如 Kysely migration）
- 命名规范（比如 `YYYYMMDD_NNN_<desc>.ts`）
- 手动执行 vs 自动执行（启动时是否自动迁移）
- up/down 成对

### 为什么要加"约定与理由"

AI 写 DDL 很快，但"为什么这么设计"它不主动写。

比如 `password_hash` 为什么允许 NULL？因为纯 OAuth 账户没有密码。如果不写清楚，未来有人看到字段可以 NULL，就以为密码可以留空，偷偷加一条 `NOT NULL` 约束。

**每个字段的解释，都是未来的防线**。

### 少了这一节会怎样

- 字段名歧义（`status` 是什么意思？）
- 约束被随意改（有人觉得 `email_verified` 不用也行，删掉）
- 迁移时没有约定，各自按自己的习惯做

## 七、第五节：API 契约

### 这一节在防什么

防"写完数据库再想 API"。

防 API 设计时没有统一的错误码约定，各端点自行其是。

### 标准结构

**1. 统一错误响应格式**

所有非 2xx 返回同一个结构：

```json
{ "error": { "code": "INVALID_CREDENTIALS", "message": "邮箱或密码错误" } }
```

**2. 端点清单**（含 HTTP 方法、路径、认证要求、M0 状态）

| Method | Path | 认证 | M0 状态 |
|---|---|---|---|
| POST | `/api/auth/login` | 无 | ✅ 实现 |
| POST | `/api/auth/logout` | 需 | ✅ 实现 |
| GET | `/api/me` | 需 | ✅ 实现 |
| POST | `/api/auth/register` | 无 | ⛔ 返回 501，CLI 替代 |

**3. 错误码字典**

```
INVALID_CREDENTIALS  401  登录失败的唯一外显原因
UNAUTHENTICATED      401  没 Cookie 或 Cookie 无效
FORBIDDEN            403  鉴权通过但无权
NOT_FOUND            404  资源不存在（含"踢别人会话"场景，不泄露存在性）
VALIDATION_FAILED    400  Zod 校验失败，details 带字段级错误
RATE_LIMITED         429  限流，带 retryAfter
NOT_IMPLEMENTED      501  占位接口
INTERNAL             500  兜底，带 requestId
```

### 为什么要单独列"错误码字典"

API 设计最容易产生"不一致的错"：登录失败返 401，参数错误返 400，会话失效返 401，服务器错误返 500——看起来有规律，但实际上每个端点可能用自己的 `message`。

错误码字典是整个子系统的统一规范。把它固化下来，每个端点照着走，集成测试时断言一致。

### 少了这一节会怎样

- 各端点错误码不一致，客户端难处理
- 401 外显不区分"邮箱不存在"与"密码错误"的防枚举设计没有被记录，后来者不知道为什么要这样做

## 八、第六节：会话机制

### 这一节在防什么

防会话逻辑散落在多处（auth、login、logout 各写各的）。

防会话策略没有一致性（比如 cookie 参数不一致、过期策略互相矛盾）。

### 标准结构

**每个关键流程画一遍**：

- Token 生成（原始 token 怎么生成、hash 怎么存）
- Cookie 参数（名字、HttpOnly、Secure、SameSite、Max-Age）
- 验证流程（`require-session` 中间件的执行步骤）
- 过期策略（绝对过期 vs 滑动过期）
- 踢下线流程
- 改密码 = 踢光所有会话
- 清理任务（频率、SQL）

**每一步都要写清楚状态转换**：

```
踢下线流程：
1. SELECT * FROM sessions WHERE id = ? AND user_id = <当前>
   命中 0 行 → 404（不区分"不存在"还是"不属于你"）
2. 若 revoked_at 已有值 → 204（幂等，不再发事件）
3. 否则 UPDATE sessions SET revoked_at = now() WHERE id = ?
   发布 session_revoked(by='user') 事件；返回 204
4. 如踢的是当前会话，响应加 Set-Cookie 清空 mao_sess
```

### 为什么要画状态转换

会话管理是 bug 重灾区。状态（登录/登出/过期/被踢/主动注销）之间的转换如果没写清楚，边界情况就会漏掉。

比如"踢别人的会话返回 404"这个设计——是为了不泄露"这个用户是否存在"这个信息。如果不写清楚，后来者可能会改成返回 403（更"合理"），结果引入信息泄露。

### 少了这一节会怎样

- 状态转换边界情况没人管
- 有人改 Cookie 参数导致安全漏洞
- 清理任务没人写，生产环境 sessions 表无限膨胀

## 九、第七节：安全与审计

### 这一节在防什么

防安全设计散落在各处，今天加一个检查、明天加一个策略，最后不知道整体策略是什么。

防 EventEmitter 机制没有被记录，S1.3 审计接入时找不到接口。

### 标准结构

**安全设计**：

- 密码哈希（参数、为什么选这个、升级策略）
- 密码策略（长度、复杂度、NIST 建议）
- 限流（两层独立、滑动窗口、仅计失败、不做账户锁定）
- 其他护栏（helmet、CORS、payload 大小限制）

**审计事件接口**：

```ts
export type AuthEvent =
  | { type: 'login_success'; userId: string; sessionId: string; ip?: string; ua?: string }
  | { type: 'login_failure'; email?: string; ip?: string; reason: 'bad_password'|'unknown_email'|'rate_limited' }
  | { type: 'logout'; userId: string; sessionId: string }
  | { type: 'session_revoked'; userId: string; sessionId: string; by: 'user'|'password_change'|'expiry' }
  | { type: 'password_changed'; userId: string }
  | { type: 'user_created'; userId: string; via: 'cli'|'register' };

export const authEvents = new EventEmitter();
```

M0 默认订阅者只有 logger。S1.3 实现时，只需在 `main.ts` 新增订阅者即可。

### 为什么要把 EventEmitter 定义在 Design 文档里

这是 [01 四层设计法](../01-四层设计法/gzh.md) 里 L1 说的"契约"。S1.1 负责发布，S1.3 负责订阅，这个接口是跨子系统的契约。Design 文档负责把契约写清楚，Plan 文档负责按这个契约实现。

### 少了这一节会怎样

- 安全设计没有整体视图
- S1.3 实现时不知道从哪订阅
- 安全配置被后来者随意修改（"helmet 好像不用开"）

## 十、第八节：错误处理

### 这一节在防什么

防三层策略（domain / service / Express）没有统一约定。

防错误响应泄露敏感信息（SQL 片段、栈信息）。

### 标准结构

三层策略 + 每层职责：

```
1. domain 层抛 typed error：
     class InvalidCredentialsError extends AppError {
       code = 'INVALID_CREDENTIALS'; status = 401;
     }
2. service 层不 try/catch 这些 typed error，让其冒泡。
3. Express 错误中间件（main.ts 最末注册）统一翻译：
     err instanceof AppError → res.status(err.status).json({ error: {...} })
     ZodError                → 400 VALIDATION_FAILED + details
     其他                     → 500 INTERNAL（日志完整栈；响应仅含 requestId）
```

约定：
- 每请求生成 `x-request-id`
- 500 响应只带 `requestId`，不带 `error.message`
- 数据库错误在 repository 层写日志后重抛

### 少了这一节会怎样

- service 层吞掉错误（`try { } catch { }`），调试时不知道哪错了
- 500 响应把 SQL 错误信息透给客户端

## 十一、第九节：测试策略

### 这一节在防什么

防测试没有分层（单元/集成/E2E 各测什么不测什么）。

防安全路径被漏测。

### 标准结构

**测试分层表**：

| 层 | 目标 | 工具 | 数据库 |
|---|---|---|---|
| 单元 | domain、services 纯逻辑 | Vitest | 不起 DB |
| 集成 | repositories + migration | Vitest + testcontainers | 真实容器，每 test 重建 |
| E2E | 端到端 HTTP 行为 | supertest | 真实 app + DB |

**M0 通过条件**（必须有的 case）：

```
- 密码错误返 401，响应体不区分邮箱/密码错。
- 限流命中返 429，带 Retry-After。
- 过期 session 第二次用立即失效。
- 改密码后所有旧会话失效。
- 踢别人会话返 404 而非 403。
```

**明确不做的测试**：
- CI 安全扫描器（单人项目过度）
- Fuzzing
- Benchmark（M0 不是瓶颈）

### 为什么要单独列"M0 通过条件"

Design 不是 Plan，不写"怎么实现"，但要写"怎么验证"。M0 通过条件就是验收标准的雏形——到了 Plan 层，这些条件会被拆成具体的测试用例。

### 少了这一节会怎样

- 没有通过条件，Plan 层不知道做到什么程度算完成
- 安全路径被漏测
- 明确不做测试，测试范围无限扩张

## 十二、第十节：依赖清单

### 这一节在防什么

防 Plan 层不知道该装什么包。

防依赖版本冲突没有被发现。

### 标准结构

**运行时依赖**（分项列出 + 版本约束）

**开发依赖**（分项列出）

**不引入但需要知道的替代方案**（可选，解释为什么选了 A 没选 B）

这个节是 Design 层和 Plan/Implementation 层的接口——Design 阶段决定"用什么"，Plan 阶段按这个清单装包。

### 少了这一节会怎样

- Plan 阶段选包时重复做决策（已经在 Design 阶段做过的）
- 依赖版本冲突在 Plan 阶段才暴露（Design 阶段没考虑过）

## 十三、第十一节：演进路径

### 这一节在防什么

防子系统被设计成"死结构"——不能演进，一动就要改所有地方。

防未来扩展时不知道哪些地方会动、哪些不会动。

### 标准结构

一张表：未来动作 | 需要修改 | 不需要修改

```sql
| 开放客户自助注册       | /auth/register 从 501 换实现     | users 表结构      |
| 接入 GitHub OAuth      | 新增 providers/github.ts          | users 表、session 机制 |
| 加组织/团队概念        | 新增 organizations 表              | users / sessions 不动 |
| 多实例部署             | 限流存储从内存换 Redis            | API 契约、表结构不动 |
```

### 这是 Design 层最重要的节

演进路径表强制你现在就想清楚：**哪些是决定死的、哪些是可以演化的**。

如果写不出来（某个"未来动作"需要修改的地方太多），说明数据模型设计还有问题。

如果演进路径表里的"需要修改"列很短、很明确，说明设计质量高——核心契约（API 契约、表结构）在扩展时保持稳定。

### 少了这一节会怎样

- 子系统被设计成"死结构"，每次扩展都伤筋动骨
- 未来接手的人不知道哪些是稳定的、哪些是临时的

## 十四、第十二节：未决项

### 这一节在防什么

防 Design 文档假装"所有事情都定死了"。

防那些"现在没想清楚但不解决就动不了工"的问题没有记录，导致 Plan 阶段卡住。

### 标准结构

逐条列出，格式：

```
| 未决项 | 当前状态 | 决定方式 |
```

比如 S1.1 文档里的：

```
| 是否引入 pnpm workspace | 单仓 vs monorepo 未定 | 先按 monorepo 布，后续调整位置不变 |
| express-rate-limit 存储后端 | 内存够用 vs 未来切 Redis | M0 用内存，Plan 阶段评估 |
```

### 为什么要写这一节

它告诉 Plan 阶段的人：这些地方要留好扩展点，不要假设死。

也告诉自己：这些地方还没想清楚，下一次 brainstorm 要先解决这些问题。

### 少了这一节会怎样

- Plan 阶段不知道哪些地方要留扩展点，按"最简单的方式"直接做死
- 下次看文档，不知道当时哪些没想清楚、哪些故意留着没做

## 十五、把模板压缩成自检清单

如果你不想读上面的逐节讲解，只想拿一个清单对着勾，这个清单就是精华版：

```
□ 定位与边界
  □ 写了 M0 现实目标
  □ 有"不在本模块做的事"表（每项带归属）
  □ 有前置/后置依赖

□ 关键决策
  □ 有"维度 | 决策 | 排除的替代"三列表
  □ 每个排除项带理由

□ 项目结构
  □ 有文件树
  □ 有依赖方向约束（只下行不反向）
  □ 有"对外暴露"清单

□ 数据模型
  □ 有 DDL
  □ 每个字段/约束都有"为什么"
  □ 有迁移策略

□ API 契约
  □ 有统一错误响应格式
  □ 有端点清单（含 M0 状态）
  □ 有错误码字典

□ 会话机制（或本子系统特有的核心流程）
  □ 每个关键流程都有状态转换描写

□ 安全与审计
  □ 安全设计有整体视图
  □ 有 EventEmitter 定义和发布事件清单

□ 错误处理
  □ 三层策略明确（domain/service/express）
  □ 防信息泄露的约定

□ 测试策略
  □ 三层测试分层明确
  □ 有 M0 通过条件
  □ 有"明确不做的测试"

□ 依赖清单
  □ 运行时依赖完整
  □ 开发依赖完整

□ 演进路径
  □ 有"未来动作 | 需要修改 | 不需要修改"表
  □ 每项"需要修改"列够短够明确

□ 未决项
  □ 有"现在没想清楚但不解决就动不了工"的清单
  □ 每项有决定方式
```

12 节 × 若干检查项。每一项都对应一个真实的坑。

---

*本文的母本是 moon-agent-os 的 [S1.1 Identity 设计文档](https://github.com/LQY-920/moon-agent-os/blob/main/docs/superpowers/specs/2026-04-23-s1-1-identity-design.md)，可以在那看到完整的原始文档。*