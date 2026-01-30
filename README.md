<div align="center">
  
# Issue2Idea 😈➡️💡

从「一堆吵吵闹闹的 GitHub Issues」中，自动提炼出**清晰、有优先级的产品需求文档**。  

</div>

`Issue2Idea` 是一个为「产品经理 / 创始人 / 独立开发者」打造的命令行小工具：  

- 你给它一个 GitHub 仓库地址  
- 它自动拉取最近的 Issues（含 title / body / comments）  
- 调用大模型，帮你回答三个关键问题：  
  - 用户**到底在抱怨什么**？（超越模板化 feature request）  
  - 哪些是**高频真实痛点**？（自动聚类语义相近的需求）  
  - 这些需求应该**按什么优先级排进 Roadmap**？  
- 最后生成一份结构化的 `requirements.md` ✨

---

## 项目亮点 ✨

- **一键从 Issues ➜ 产品需求文档**
  - 支持传入 GitHub 仓库 URL（`https://github.com/owner/repo` 或 `git@github.com:owner/repo.git`）
  - 自动获取最近的 Issues：标题、正文、评论全部拉取
  - 支持通过 `GITHUB_TOKEN` 鉴权，避免 API 频率受限

- **真正关注“用户在痛什么”而不是“提了什么 feature”**
  - 对模板化 issue（bug 模板 / feature 模板）做语义抽取
  - 聚焦：用户卡在哪、为什么卡、什么场景下频繁出现

- **自动聚类 + 优先级排序**
  - 合并语义重复/相似的需求，形成**合并后的 Feature 机会点**
  - 为每个 pain point / feature 给出 `High / Medium / Low` 优先级
  - 按优先级输出「Suggested Roadmap」

- **输出即文档，可直接贴给团队**
  - 统一生成标准结构的 `requirements.md`，方便版本对比 / PR 审阅
  - 适合写进 Roadmap、RFC、产品评审文档

---

## 安装 🛠

在项目根目录（包含 `pyproject.toml` 的那个目录）执行：

```bash
pip install -e .
```

未来如果发布到 PyPI，可以直接：

```bash
pip install Issue2Idea
```

---

## 环境变量配置 🔑

`Issue2Idea` 需要两个关键配置：

- **GitHub 访问令牌（可选但强烈推荐）**
  - 作用：提高 GitHub API 访问频率限制 & 访问私有仓库

```bash
export GITHUB_TOKEN="ghp_xxx"  # Windows PowerShell: $env:GITHUB_TOKEN="ghp_xxx"
```

- **OpenAI API Key（默认 LLM 后端）**

```bash
export OPENAI_API_KEY="sk-xxx"
```

你也可以在项目根目录创建一个 `.env` 文件（推荐）：

```env
GITHUB_TOKEN=ghp_xxx
OPENAI_API_KEY=sk-xxx
```

`cli.py` 会通过 `python-dotenv` 自动加载这些配置。

---

## 快速上手 🚀

最常见的调用方式：

```bash
Issue2Idea https://github.com/owner/repo --max-issues 200 --output requirements.md
```

**参数说明：**

- **`repo_url`**：位置参数，GitHub 仓库地址，例如：  
  - `https://github.com/pallets/flask`  
  - `git@github.com:pallets/flask.git`
- **`--max-issues`**：最多抓取多少条最近的 Issues（默认 `100`）
- **`--state`**：Issue 状态，`open` / `closed` / `all`（默认：`open`）
- **`--output`**：输出 Markdown 文件路径（默认：`requirements.md`）
- **`--model`**：使用的 LLM 模型名称（例如：`gpt-4.1-mini`）

执行成功后，你会在当前目录看到一个类似 `examples/requirements.md` 的报告文件。

---

## 输出长什么样？📄

一个典型的自动生成 `requirements.md` 会包含四大模块：

```markdown
## Overview

- **Repository**: https://github.com/owner/repo
- **Analyzed Issues**: 120
- 用户在首次配置中经常卡住，依赖文档 &  GitHub Issue 寻求帮助。
- 高级用户在排查问题时缺乏统一视图，日志零散、难以追踪。

## Top User Pain Points

### pp_1 — 首次安装 / 配置路径太复杂
- **Priority**: High
- **Evidence Issues**: 12, 27, 41, 89

新用户在阅读 README + 官方文档后仍然无法顺利完成安装配置，
常见失败点包括环境变量配置、依赖版本不兼容等。

### pp_2 — 调试失败时缺乏足够的日志与可观测性
- **Priority**: Medium
- **Evidence Issues**: 3, 51, 73

用户在生产环境遇到错误时，很难在现有的日志中找到对应的上下文，
导致问题定位耗时、需要反复询问维护者。

## Feature Requests (Merged)

### fr_1 — 提供「一步一步」的交互式安装 / 配置向导
- **Priority**: High
- **Related Pain Points**: pp_1

通过 CLI / Web UI 提供引导式配置流程：运行前检查环境、明确给出缺失依赖、
对常见错误给出「一键修复」或链接到文档的跳转。

### fr_2 — 统一诊断与日志面板
- **Priority**: Medium
- **Related Pain Points**: pp_2

在一个统一的视图中展示最近错误、关键日志、请求上下文以及建议排查步骤，
帮助用户更快定位问题。

## Suggested Roadmap

### Step 1: 解决初次体验的「拦路虎」
- **Feature Requests**: fr_1

优先交付安装/配置向导，降低用户从 0 到 1 的门槛，提高转化率。

### Step 2: 提升现有用户的运维效率
- **Feature Requests**: fr_2

围绕诊断与可观测性进行迭代，减少重复问答、降低维护成本。
```

这份文档可以直接丢给团队讨论、贴到 Roadmap Issue、或者作为产品评审的输入材料。  

---

## 内部结构与代码解析 🧠

### 整体目录

```text
Issue2Idea/
├── Issue2Idea/
│   ├── __init__.py
│   ├── github_client.py     # GitHub API 封装
│   ├── issue_parser.py      # Issue 清洗与格式化
│   ├── demand_extractor.py  # LLM 需求提炼逻辑
│   ├── prompt.py            # Prompt 模板
│   ├── reporter.py          # Markdown 报告生成
│   ├── llm.py               # LLM 调用封装
│   └── cli.py               # CLI 入口
├── examples/
│   └── requirements.md
├── README.md
├── requirements.txt
└── pyproject.toml
```

---

### GitHub API 封装：`github_client.py` 🌐

核心目标：**把「各种形式的仓库地址」和「复杂的 REST API 响应」压平为简单的 Python 对象**。

```python
from dataclasses import dataclass
from typing import List, Optional
import requests

GITHUB_API_BASE = "https://api.github.com"

@dataclass
class IssueComment:
    id: int
    body: str
    user: Optional[str] = None

@dataclass
class Issue:
    id: int
    number: int
    title: str
    body: str
    state: str
    html_url: str
    user: Optional[str] = None
    comments: List[IssueComment] | None = None
```

- **为什么要 dataclass？**
  - 更接近业务语义（`Issue` / `IssueComment`），比直接用 dict 易读易维护
  - 便于在后续模块（如 `issue_parser.py`）中做类型提示和重构

封装 URL 解析与 Issue 列表获取：

```python
class GitHubClient:
    def __init__(self, token: Optional[str] = None):
        self.session = requests.Session()
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "demandlens/0.1.0",
        }
        if token:
            headers["Authorization"] = f"Bearer {token}"
        self.session.headers.update(headers)

    @staticmethod
    def parse_repo_url(repo_url: str) -> tuple[str, str]:
        # 支持 https://github.com/owner/repo 和 git@github.com:owner/repo.git
        ...

    def list_issues(self, owner: str, repo: str, state: str = "open", max_issues: int = 100):
        # 通过 /repos/{owner}/{repo}/issues 拉取最近的 Issue
        ...
```

**设计取舍：**

- 使用 `list_issues + fetch_comments_for_issues` 两段式 API，而不是一次性把所有字段塞到一个函数里，方便以后扩展（例如：只要标题/只要评论）。

---

### Issue 预处理：`issue_parser.py` 🧹

LLM 不关心 HTTP 响应结构，它只需要**纯文本 + 少量上下文**。  
因此这里把 `Issue` 转成 `IssueText`：

```python
from dataclasses import dataclass
from typing import List

@dataclass
class IssueText:
    number: int
    title: str
    body: str
    comments: List[str]
    url: str
    state: str

    def to_prompt_block(self) -> str:
        comments_block = ""
        if self.comments:
            comments_block = "Comments:\\n" + "\\n---\\n".join(self.comments)
        return (
            f"Issue #{self.number}: {self.title}\\n"
            f"State: {self.state}\\n"
            f"URL: {self.url}\\n"
            f"Body:\\n{self.body or '(no body)'}\\n"
            f"{comments_block}"
        )
```

- 每个 Issue 在 Prompt 里都是一个「独立小块」：包含标题、状态、URL、正文、评论
- 评论前会附带作者名，帮助 LLM 理解「这是用户追问 / 作者回复 / 其他用户+1」

---

### Prompt 设计：`prompt.py` 🧾

`demandlens` 的灵魂是 Prompt：

- **SYSTEM_PROMPT**：告诉模型「你是资深产品经理 + 用户研究专家」
- **User Prompt**：给出严格的 JSON Schema，让输出结构可解析

示例（部分）：

```python
SYSTEM_PROMPT = """
You are a senior product manager and user research expert.
Your task is to read GitHub Issues and extract the real user needs and pain points,
not just the literal feature requests.
...
""".strip()

def build_user_prompt(issue_blocks: str) -> str:
    return f"""
    You are given a set of GitHub Issues (titles, bodies, and comments).

    Read all the issues carefully and then produce:
    1. A short overview...
    2. A list of top user pain points...
    3. A set of merged feature requests...
    4. A suggested implementation roadmap...

    Use the following JSON schema for your final answer (wrap it in a Markdown code block):
    ```json
    {{ ... JSON SCHEMA ... }}
    ```

    Here are the GitHub Issues:
    ---
    {issue_blocks}
    ---
    """.strip()
```

**价值点：**

- 强调「提炼真实用户需求」，减少模型倾向于机械罗列 feature
- 强制 `priority` 为 `High | Medium | Low`，便于后处理

---

### LLM 封装：`llm.py` 🤖

在这里我们做了两件事：

- 给 OpenAI 官方 SDK 包了一层薄薄的壳，方便未来换模型/厂商
- 提供 `extract_json_from_markdown`，从 LLM 输出的 Markdown 里安全地提取 JSON

```python
from openai import OpenAI

class LLMClient:
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4.1-mini"):
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        self._client = OpenAI(api_key=api_key)
        self.model = model

    def chat(self, system_prompt: str, user_prompt: str) -> str:
        resp = self._client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
        )
        return resp.choices[0].message.content or ""
```

然后解析 JSON：

```python
def extract_json_from_markdown(markdown_text: str) -> Dict[str, Any]:
    # 优先找 ```json ... ``` 代码块
    # 找不到就 fallback 到全文第一个 { ... } 的 JSON 对象
    ...
```

---

### 需求提炼核心：`demand_extractor.py` 🧩

真正把「Issues 列表」变成「结构化需求分析」的地方：

```python
class DemandExtractor:
    def __init__(self, llm_client: LLMClient) -> None:
        self._llm = llm_client

    def analyze(self, issues: Iterable[IssueText]) -> DemandAnalysis:
        blocks = [issue.to_prompt_block() for issue in issues]
        issue_blocks = "\\n\\n====================\\n\\n".join(blocks)

        user_prompt = build_user_prompt(issue_blocks)
        llm_output = self._llm.chat(SYSTEM_PROMPT, user_prompt)
        data = self._llm.extract_json_from_markdown(llm_output)
        ...
```

- **关键点：**
  - 所有 Issue 以统一格式拼接，分隔符清晰
  - LLM 输出通过单一函数解析为 `DemandAnalysis`，便于后续 reporter 使用

---

### 报告生成：`reporter.py` 📝

把 `DemandAnalysis` 渲染成最终的 Markdown：

```python
def render_markdown_report(repo_url: str, issue_count: int, analysis: DemandAnalysis) -> str:
    overview_md = _format_overview(analysis.raw_overview)
    pain_points_md = _format_pain_points(analysis.pain_points)
    features_md = _format_feature_requests(analysis.merged_feature_requests)
    roadmap_md = _format_roadmap(analysis.roadmap)

    return (
        f"## Overview\\n\\n"
        f"- **Repository**: {repo_url}\\n"
        f"- **Analyzed Issues**: {issue_count}\\n"
        f"\\n"
        f"{overview_md}\\n\\n"
        f"## Top User Pain Points\\n\\n"
        f"{pain_points_md}\\n\\n"
        f"## Feature Requests (Merged)\\n\\n"
        f"{features_md}\\n\\n"
        f"## Suggested Roadmap\\n\\n"
        f"{roadmap_md}\\n"
    )
```

- 把模型输出的结构化 JSON 变成一个**可读性很强的产品需求文档**

---

### CLI 入口：`cli.py` 💻

CLI 代码把上面所有模块串起来：

```python
def main(argv: list[str] | None = None) -> int:
    load_dotenv()
    args = parse_args(argv)

    owner, repo = GitHubClient.parse_repo_url(args.repo_url)
    client = GitHubClient(token=os.getenv("GITHUB_TOKEN"))

    issues = client.list_issues(owner, repo, state=args.state, max_issues=args.max_issues)
    issues = client.fetch_comments_for_issues(owner, repo, issues)

    issue_texts = bulk_issues_to_text(issues)

    llm_client = LLMClient(model=args.model or "gpt-4.1-mini")
    extractor = DemandExtractor(llm_client)
    analysis = extractor.analyze(issue_texts)

    output_md = render_markdown_report(args.repo_url, len(issue_texts), analysis)
    Path(args.output).write_text(output_md, encoding="utf-8")
```

从命令行入口到最终 `requirements.md`，中间大致是这样的数据流：

`repo_url ➜ issues(json) ➜ Issue(dataclass) ➜ IssueText ➜ LLM(JSON) ➜ DemandAnalysis ➜ Markdown`  

---

## Roadmap & 想法 💭

一些未来可以一起玩的方向：

- **支持多 LLM 后端（如本地大模型 / 其他云厂商）**
- **支持「时间窗口」或「标签过滤」（例如只看最近 30 天 / label=bug）**
- **导出多种格式：Confluence / Notion / HTML 报告**
- **把同一个仓库多次分析结果做 diff，对比需求变化趋势**

如果你对这些方向有兴趣，欢迎开 Issue 一起设计 🙌

---

## 开发与贡献 🤝

```bash
git clone https://github.com/yourname/Issue2Idea.git
cd Issue2Idea
pip install -e ".[dev]"
```

- **欢迎贡献：**
  - 更好的 Prompt 设计 / 模型选择
  - 更智能的需求聚类、相似度合并算法
  - 新的导出格式（HTML、Notion、Confluence 等）
  - 真实项目的案例（加到 `examples/`）

欢迎通过 Issue / PR 的方式参与，一起把「Issue 混沌」变成「Roadmap 清晰」💡

--- 

## 👤 作者 (Author)

**Haoze Zheng**

*   🎓 **School**: Xinjiang University (XJU)
*   📧 **Email**: zhenghaoze@stu.xju.edu.cn
*   🐱 **GitHub**: [mire403](https://github.com/mire403)

---

<div align="center">
  <sub>Made by Haoze Zheng. 2026 Issue2Idea.</sub>
</div>







