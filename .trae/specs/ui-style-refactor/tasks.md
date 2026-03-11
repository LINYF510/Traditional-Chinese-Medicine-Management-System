# 中医药管理系统 UI 风格重构 - 实施计划

## [x] Task 1: 引入 Tailwind CSS 和更新样式系统
- **Priority**: P0
- **Depends On**: None
- **Description**: 
  - 安装和配置 Tailwind CSS 到 Vue 项目
  - 将设计稿的国风配色方案定义为 CSS 自定义属性
  - 更新现有的 style.css 文件，引入 Tailwind 和新的颜色系统
  - 确保不影响现有样式的正常显示
- **Acceptance Criteria Addressed**: [AC-1]
- **Test Requirements**:
  - `human-judgement` TR-1.1: 检查 CSS 自定义属性是否正确定义
  - `human-judgement` TR-1.2: 验证 Tailwind CSS 正常加载且不破坏现有布局
- **Notes**: 可以先保留现有样式，逐步迁移

## [x] Task 2: 重构 AppLayout 组件 - 侧边栏
- **Priority**: P0
- **Depends On**: Task 1
- **Description**: 
  - 重构侧边栏，采用设计稿的墨绿色（#2D6A4F）背景
  - 更新 Logo 区域样式
  - 更新菜单导航样式，包括选中状态（#1B4332）
  - 更新底部用户区域样式
  - 保持现有的菜单数据和路由功能完全不变
- **Acceptance Criteria Addressed**: [AC-1, AC-2]
- **Test Requirements**:
  - `human-judgement` TR-2.1: 侧边栏颜色和样式符合设计稿
  - `programmatic` TR-2.2: 菜单点击和路由跳转功能正常
  - `programmatic` TR-2.3: 国际化菜单标签正常显示
- **Notes**: 保持现有的 menuItems 数据结构不变

## [x] Task 3: 重构 AppLayout 组件 - 顶部导航
- **Priority**: P0
- **Depends On**: Task 2
- **Description**: 
  - 重构顶部导航栏，采用设计稿的白色背景和简洁样式
  - 将语言切换器放在更合适的位置（顶部栏右侧）
  - 保持面包屑和权限显示功能
  - 更新用户信息和退出登录按钮样式
- **Acceptance Criteria Addressed**: [AC-1, AC-2, AC-4]
- **Test Requirements**:
  - `human-judgement` TR-3.1: 顶部导航栏样式符合设计稿
  - `programmatic` TR-3.2: 语言切换功能正常工作
  - `programmatic` TR-3.3: 退出登录功能正常
- **Notes**: 考虑是否添加面包屑导航（现有版本没有）

## [x] Task 4: 重构 LoginView.vue 登录页面
- **Priority**: P0
- **Depends On**: Task 1
- **Description**: 
  - 应用国风配色到登录页面
  - 更新卡片、按钮、输入框的样式
  - 保持语言切换器在合适位置（右下角）
  - 保持登录功能完全不变
- **Acceptance Criteria Addressed**: [AC-1, AC-3, AC-4]
- **Test Requirements**:
  - `human-judgement` TR-4.1: 登录页面样式符合设计稿风格
  - `programmatic` TR-4.2: 登录功能正常工作
  - `programmatic` TR-4.3: 语言切换在登录页面正常
- **Notes**: 保持现有的表单验证和错误处理

## [x] Task 5: 重构 DashboardView.vue 仪表板页面
- **Priority**: P1
- **Depends On**: Task 1
- **Description**: 
  - 应用国风配色到仪表板页面
  - 更新数据卡片样式（白色背景、圆角、阴影）
  - 更新表格样式
  - 保持所有现有数据加载和显示功能
  - 考虑是否添加设计稿中的图表（可选，现有版本没有）
- **Acceptance Criteria Addressed**: [AC-1, AC-3]
- **Test Requirements**:
  - `human-judgement` TR-5.1: 仪表板样式符合设计稿风格
  - `programmatic` TR-5.2: 数据加载和显示功能正常
- **Notes**: 图表功能属于增强功能，可作为可选项

## [x] Task 6: 重构 UsersView.vue 用户管理页面
- **Priority**: P1
- **Depends On**: Task 1
- **Description**: 
  - 应用国风配色到用户管理页面
  - 更新卡片、表格、按钮、表单样式
  - 保持所有 CRUD 操作功能
  - 保持权限控制功能
- **Acceptance Criteria Addressed**: [AC-1, AC-3, AC-4]
- **Test Requirements**:
  - `human-judgement` TR-6.1: 用户管理页面样式符合设计稿
  - `programmatic` TR-6.2: 创建、编辑、删除用户功能正常
  - `programmatic` TR-6.3: 国际化文本正常显示
- **Notes**: 保持所有表单验证和错误处理

## [x] Task 7: 重构 HerbsView.vue 中药管理页面
- **Priority**: P1
- **Depends On**: Task 1
- **Description**: 
  - 应用国风配色到中药管理页面
  - 更新卡片、表格、按钮、表单样式
  - 保持所有 CRUD 操作和搜索功能
- **Acceptance Criteria Addressed**: [AC-1, AC-3, AC-4]
- **Test Requirements**:
  - `human-judgement` TR-7.1: 中药管理页面样式符合设计稿
  - `programmatic` TR-7.2: CRUD 和搜索功能正常
  - `programmatic` TR-7.3: 国际化文本正常显示
- **Notes**: 保持所有表单验证和错误处理

## [x] Task 8: 重构 FormulasView.vue 药方管理页面
- **Priority**: P1
- **Depends On**: Task 1
- **Description**: 
  - 应用国风配色到药方管理页面
  - 更新卡片、表格、按钮、表单样式
  - 更新药方组成部分的样式
  - 保持所有 CRUD 操作功能
- **Acceptance Criteria Addressed**: [AC-1, AC-3, AC-4]
- **Test Requirements**:
  - `human-judgement` TR-8.1: 药方管理页面样式符合设计稿
  - `programmatic` TR-8.2: CRUD 功能正常
  - `programmatic` TR-8.3: 国际化文本正常显示
- **Notes**: 保持药方组成的动态添加/删除功能

## [x] Task 9: 重构 InventoryView.vue 库存管理页面
- **Priority**: P1
- **Depends On**: Task 1
- **Description**: 
  - 应用国风配色到库存管理页面
  - 更新卡片、表格、按钮、表单样式
  - 更新库存警告列表的样式（正常状态为绿色）
  - 保持所有库存操作功能
- **Acceptance Criteria Addressed**: [AC-1, AC-3, AC-4]
- **Test Requirements**:
  - `human-judgement` TR-9.1: 库存管理页面样式符合设计稿
  - `programmatic` TR-9.2: 入库、出库、盘点功能正常
  - `programmatic` TR-9.3: 国际化文本正常显示
- **Notes**: 保持"没有活动警告"的绿色样式

## [x] Task 10: 响应式优化和测试
- **Priority**: P2
- **Depends On**: Tasks 4-9
- **Description**: 
  - 确保所有页面在不同屏幕尺寸下正常显示
  - 优化移动端的侧边栏和顶部导航
  - 全面测试所有功能
- **Acceptance Criteria Addressed**: [AC-3, AC-5]
- **Test Requirements**:
  - `human-judgement` TR-10.1: 在桌面、平板、手机尺寸下检查布局
  - `programmatic` TR-10.2: 所有页面功能回归测试通过
  - `human-judgement` TR-10.3: 整体风格一致性检查
- **Notes**: 可以使用浏览器的设备模拟功能测试
