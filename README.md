# AI-iMediLink 🏥

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28.0-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 项目简介

AI-iMediLink 是一个基于人工智能的医疗咨询系统，提供智能诊疗服务。系统集成了多种大模型，支持多科室智能助手，为用户提供专业的医疗咨询服务。

### 核心特色
- 🤖 **多模型支持**: 集成OpenAI GPT、DeepSeek等主流大模型
- 🏥 **多科室覆盖**: 支持内科、外科、妇产科、儿科、肿瘤科、男科等专业科室
- 📚 **知识库增强**: 基于RAG技术的医疗知识检索系统
- 💬 **流式对话**: 实时流式输出，提升用户交互体验
- 🎨 **现代界面**: 响应式设计，支持多设备访问

## 技术栈

- **前端框架**: Streamlit
- **AI模型**: OpenAI GPT, DeepSeek
- **向量数据库**: ChromaDB
- **知识检索**: LangChain + RAG
- **数据处理**: Pandas, NumPy
- **可视化**: Matplotlib, Plotly

## 项目结构

```
AI-iMediLink/
├── 📁 data/                    # 数据目录
│   ├── 📁 Prompt/              # 各科室提示词模板
│   │   ├── 内科.md
│   │   ├── 外科.md
│   │   └── ...
│   ├── 📁 RAG/                 # 医疗知识库文档
│   │   ├── 📁 内科/
│   │   ├── 📁 外科/
│   │   └── ...
│   └── 📁 chroma_data/         # ChromaDB向量数据库
├── 📁 pages/                   # 页面模块
│   └── 1_医脉通.py             # 医疗咨询主页面
├── 📁 utils/                   # 工具模块
│   ├── config.json            # 模型配置文件
│   └── tools.py               # 核心工具函数
├── 📁 code/                    # 开发文档
├── 📄 首页.py                   # 应用主入口
├── 📄 requirements.txt         # 依赖包列表
└── 📄 README.md               # 项目说明文档
```

## 功能特点

### 🏥 专业医疗服务
- **多科室覆盖**: 内科、外科、妇产科、儿科、肿瘤科、男科等6大专业科室
- **专业知识库**: 基于医疗文献和临床指南的专业知识检索
- **症状分析**: 智能症状识别和初步诊断建议
- **用药指导**: 提供药物信息和用药建议

### 🤖 AI技术特性
- **多模型支持**: 集成OpenAI GPT-3.5/4、DeepSeek等主流大模型
- **RAG增强**: 检索增强生成技术，确保回答的专业性和准确性
- **流式输出**: 实时流式响应，提升交互体验
- **上下文记忆**: 支持多轮对话的上下文理解

### ⚙️ 系统特性
- **灵活配置**: 支持模型切换、温度调节、Token数量控制
- **响应式界面**: 现代化UI设计，支持多设备访问
- **数据安全**: 本地部署，保护用户隐私
- **易于扩展**: 模块化设计，便于功能扩展

## 系统要求

- **操作系统**: Windows 10+, macOS 10.14+, Linux (Ubuntu 18.04+)
- **Python版本**: 3.8 或更高版本
- **内存**: 建议 8GB 以上
- **存储空间**: 至少 2GB 可用空间
- **网络**: 需要互联网连接以访问AI模型API

## 快速开始

### 1. 克隆项目
```bash
git clone https://github.com/your_username/AI-iMediLink.git
cd AI-iMediLink
```

### 2. 创建虚拟环境（推荐）
```bash
# 使用 conda
conda create -n ai-medilink python=3.8
conda activate ai-medilink

# 或使用 venv
python -m venv ai-medilink
# Windows
ai-medilink\Scripts\activate
# macOS/Linux
source ai-medilink/bin/activate
```

### 3. 安装依赖
```bash
pip install -r requirements.txt
```

### 4. 配置API密钥

#### 方法一：环境变量（推荐）
```bash
# Windows
set OPENAI_API_KEY=your_openai_api_key
set DEEPSEEK_API_KEY=your_deepseek_api_key

# macOS/Linux
export OPENAI_API_KEY=your_openai_api_key
export DEEPSEEK_API_KEY=your_deepseek_api_key
```

#### 方法二：.env文件
在项目根目录创建 `.env` 文件：
```env
OPENAI_API_KEY=your_openai_api_key
DEEPSEEK_API_KEY=your_deepseek_api_key
```

#### 方法三：修改配置文件
编辑 `utils/config.json` 文件，填入您的API密钥。

### 5. 启动应用
```bash
streamlit run 首页.py
```

应用将在浏览器中自动打开，默认地址：`http://localhost:8501`

## 使用指南

### 基本操作
1. **启动应用**: 运行 `streamlit run 首页.py`
2. **选择科室**: 在侧边栏选择相应的医疗科室
3. **配置模型**: 选择AI模型并调整参数（温度、最大Token数等）
4. **开始咨询**: 在输入框中描述症状或医疗问题
5. **获取建议**: 系统将提供专业的医疗咨询建议

### 功能说明
- **科室选择**: 根据问题类型选择合适的科室，获得更专业的回答
- **模型配置**: 
  - **温度**: 控制回答的创造性（0.1-1.0，越高越有创造性）
  - **最大Token**: 控制回答长度（建议500-2000）
- **知识库检索**: 系统会自动从相关医疗知识库中检索信息
- **流式输出**: 实时显示AI生成的回答过程

### 注意事项
⚠️ **重要提醒**：
- 本系统仅供医疗咨询参考，不能替代专业医生诊断
- 如有严重症状，请及时就医
- 系统建议仅供参考，具体治疗方案请咨询专业医生

## API密钥获取

### OpenAI API
1. 访问 [OpenAI官网](https://platform.openai.com/)
2. 注册并登录账户
3. 进入 API Keys 页面
4. 创建新的API密钥
5. 复制密钥并妥善保存

### DeepSeek API
1. 访问 [DeepSeek官网](https://platform.deepseek.com/)
2. 注册并登录账户
3. 进入API管理页面
4. 创建新的API密钥
5. 复制密钥并妥善保存

## 故障排除

### 常见问题

1. **ModuleNotFoundError: No module named 'distutils'**
   - 这是 Python 3.12+ 的兼容性问题
   - 解决方案：使用 Python 3.9-3.11 或安装兼容包
   ```bash
   pip install setuptools>=68.0.0 wheel>=0.41.0
   ```

**Q: 启动时提示模块未找到**
```bash
A: 确保已激活虚拟环境并安装所有依赖：
pip install -r requirements.txt
```

**Q: API调用失败**
```bash
A: 检查API密钥是否正确配置：
1. 验证密钥格式是否正确
2. 确认账户余额充足
3. 检查网络连接
```

**Q: 页面无法访问**
```bash
A: 检查端口是否被占用：
streamlit run 首页.py --server.port 8502
```

**Q: 知识库检索失败**
```bash
A: 确保ChromaDB数据已正确初始化：
1. 检查 data/chroma_data 目录是否存在
2. 重新运行应用以初始化向量数据库
```

### 服务器部署

如果需要在服务器上部署应用，请参考详细的 [部署指南](DEPLOYMENT.md)，其中包含：
- 环境配置要求
- Docker 部署方案
- 常见部署问题解决
- 性能优化建议

### 日志查看
应用运行时的详细日志会显示在终端中，包括：
- API调用状态
- 知识库检索结果
- 错误信息和堆栈跟踪

```bash
# 查看详细错误信息
streamlit run 首页.py --logger.level debug
```

## 开发指南

### 项目架构
- `首页.py`: 主应用入口，包含UI布局和核心功能
- `pages/1_医脉通.py`: 医疗咨询页面的具体实现
- `utils/tools.py`: 核心工具函数，包含RAG检索和模型调用
- `utils/config.json`: 模型配置文件
- `data/`: 知识库和提示词数据

### 添加新科室
1. 在 `data/Prompt/` 目录下添加新科室的提示词文件
2. 在 `data/RAG/` 目录下添加相应的知识库文档
3. 更新 `utils/tools.py` 中的科室列表
4. 重新运行应用以更新向量数据库

### 集成新模型
1. 在 `utils/config.json` 中添加新模型配置
2. 在 `utils/tools.py` 中实现模型调用逻辑
3. 更新UI中的模型选择选项
## 未来规划

### 用户体验优化
- **用户系统**: 增加用户注册、登录、个人资料管理功能
- **历史记录**: 实现对话历史保存、搜索和管理
- **个性化设置**: 支持用户自定义界面主题、字体大小等偏好设置
- **多语言支持**: 增加英文、繁体中文等多语言界面
- **移动端适配**: 优化移动设备访问体验，开发PWA应用

### 智能功能增强
- **多模态交互**: 支持语音输入输出、图像识别诊断
- **智能推荐**: 基于用户历史和症状的个性化内容推荐
- **症状自检**: 开发智能症状评估和初步诊断工具
- **用药提醒**: 集成用药指导和提醒功能
- **健康档案**: 建立个人健康数据管理系统

### 数据与分析
- **知识库扩展**: 持续更新医疗知识库，增加更多专科内容
- **数据分析**: 实现用户行为分析和系统使用统计
- **质量监控**: 建立回答质量评估和持续改进机制
- **A/B测试**: 支持功能迭代的A/B测试框架

### 安全与合规
- **数据加密**: 实现端到端数据加密保护
- **访问控制**: 建立细粒度的权限管理系统
- **审计日志**: 完善操作日志记录和审计功能
- **合规认证**: 符合医疗数据保护相关法规要求

### 系统架构优化
- **微服务架构**: 重构为微服务架构，提升系统可扩展性
- **缓存优化**: 实现Redis缓存，提升响应速度
- **负载均衡**: 支持高并发访问的负载均衡
- **容器化部署**: 支持Docker容器化部署
- **监控告警**: 建立完善的系统监控和告警机制

### 内容与服务扩展
- **专家咨询**: 集成真人医生在线咨询服务
- **健康科普**: 增加医疗健康科普文章和视频
- **药品查询**: 建立药品信息查询和相互作用检查
- **医院导航**: 集成医院信息和预约挂号功能

### 社区与互动
- **用户评论系统**: 收集用户反馈和评价
- **问答社区**: 建立用户互助问答平台
- **专家问答**: 定期邀请医疗专家在线答疑
- **健康打卡**: 增加健康习惯养成和打卡功能
## 贡献指南

我们欢迎所有形式的贡献！无论是报告bug、提出新功能建议，还是提交代码改进。

### 如何贡献

1. **Fork 项目**
   ```bash
   git fork https://github.com/your_username/AI-iMediLink.git
   ```

2. **创建功能分支**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **提交更改**
   ```bash
   git commit -m "Add: 描述你的更改"
   ```

4. **推送到分支**
   ```bash
   git push origin feature/your-feature-name
   ```

5. **创建 Pull Request**

### 贡献类型

- 🐛 **Bug修复**: 报告或修复系统bug
- ✨ **新功能**: 提出或实现新功能
- 📚 **文档改进**: 完善文档和注释
- 🎨 **UI优化**: 改进用户界面和体验
- 🔧 **代码重构**: 优化代码结构和性能
- 🧪 **测试**: 添加或改进测试用例

### 代码规范

- 遵循 PEP 8 Python 代码规范
- 添加必要的注释和文档字符串
- 确保代码通过现有测试
- 新功能需要添加相应测试

### 问题报告

提交Issue时，请包含：
- 详细的问题描述
- 复现步骤
- 系统环境信息
- 错误日志（如有）

## 更新日志

### v1.0.0 (2024-01-01)
- ✨ 初始版本发布
- 🏥 支持6大医疗科室
- 🤖 集成OpenAI和DeepSeek模型
- 📚 实现RAG知识检索
- 🎨 现代化UI界面

## 致谢

感谢以下开源项目和贡献者：
- [Streamlit](https://streamlit.io/) - Web应用框架
- [LangChain](https://langchain.com/) - AI应用开发框架
- [ChromaDB](https://www.trychroma.com/) - 向量数据库
- [OpenAI](https://openai.com/) - GPT模型API
- [DeepSeek](https://www.deepseek.com/) - 开源大模型

## 联系我们

- 📧 邮箱: your-email@example.com
- 🐛 问题反馈: [GitHub Issues](https://github.com/your_username/AI-iMediLink/issues)
- 💬 讨论交流: [GitHub Discussions](https://github.com/your_username/AI-iMediLink/discussions)

## 许可证

本项目采用 [MIT 许可证](LICENSE)。

```
MIT License

Copyright (c) 2024 AI-iMediLink

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

<div align="center">
  <p>⭐ 如果这个项目对你有帮助，请给我们一个星标！</p>
  <p>Made with ❤️ by AI-iMediLink Team</p>
</div>