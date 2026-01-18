# Agent Chat UI

Agent Chat UI 是一个 Next.js 应用程序，通过聊天界面可以与任何具有 `messages` 键的 LangGraph 服务器进行聊天。

> [!NOTE]
> 🎥 观看视频设置指南 [这里](https://youtu.be/lInrwVnZ83o)。

## 设置

> [!TIP]
> 不想在本地运行应用？使用已部署的网站：[agentchat.vercel.app](https://agentchat.vercel.app)！

首先，克隆存储库，或运行 [`npx` 命令](https://www.npmjs.com/package/create-agent-chat-app)：

```bash
npx create-agent-chat-app
```

或

```bash
git clone https://github.com/langchain-ai/agent-chat-ui.git

cd agent-chat-ui
```

安装依赖：

```bash
pnpm install
```

运行应用：

```bash
pnpm dev
```

应用将在 `http://localhost:3000` 可用。

## 使用

应用运行后（或使用已部署的网站时），系统会提示您输入：

- **部署 URL**：您要与之聊天的 LangGraph 服务器的 URL。这可以是生产或开发 URL。
- **助手/图 ID**：在通过聊天界面获取和提交运行时要使用的图名称或助手 ID。
- **LangSmith API 密钥**：（仅连接到已部署的 LangGraph 服务器时需要）在对 LangGraph 服务器发送的请求进行身份验证时使用的 LangSmith API 密钥。

输入这些值后，点击 `Continue`。然后您将被重定向到聊天界面，在那里您可以开始与 LangGraph 服务器聊天。

## 环境变量

您可以通过设置以下环境变量绕过初始设置表单：

```bash
NEXT_PUBLIC_API_URL=http://localhost:2024
NEXT_PUBLIC_ASSISTANT_ID=agent
```

> [!TIP]
> 如果要连接到生产 LangGraph 服务器，请阅读 [进入生产环境](#进入生产环境) 部分。

要使用这些变量：

1. 将 `.env.example` 文件复制到名为 `.env` 的新文件
2. 在 `.env` 文件中填写值
3. 重新启动应用程序

设置这些环境变量后，应用程序将使用它们而不是显示设置表单。

## 在聊天中隐藏消息

您可以通过两种主要方式控制 Agent Chat UI 中消息的可见性：

**1. 防止实时流式传输：**

要阻止消息在从 LLM 调用流式传输时显示，请将 `langsmith:nostream` 标签添加到聊天模型的配置中。UI 通常使用 `on_chat_model_stream` 事件来渲染流式消息；此标签可防止为标记的模型发出这些事件。

_Python 示例：_

```python
from langchain_anthropic import ChatAnthropic

# 通过 .with_config 方法添加标签
model = ChatAnthropic().with_config(
    config={"tags": ["langsmith:nostream"]}
)
```

_TypeScript 示例：_

```typescript
import { ChatAnthropic } from "@langchain/anthropic";

const model = new ChatAnthropic()
  // 通过 .withConfig 方法添加标签
  .withConfig({ tags: ["langsmith:nostream"] });
```

**注意：** 即使通过这种方式隐藏了流式传输，如果消息在未经进一步修改的情况下保存到图的状态中，它仍然会在 LLM 调用完成后出现。

**2. 永久隐藏消息：**

要确保消息永远不会在聊天 UI 中显示（无论是在流式传输期间还是保存到状态后），在将消息添加到图的状态之前，在其 `id` 字段前加上 `do-not-render-`，并将 `langsmith:do-not-render` 标签添加到聊天模型的配置中。UI 会明确过滤掉所有 `id` 以此前缀开头的消息。

_Python 示例：_

```python
result = model.invoke([messages])
# 在保存到状态前为 ID 加前缀
result.id = f"do-not-render-{result.id}"
return {"messages": [result]}
```

_TypeScript 示例：_

```typescript
const result = await model.invoke([messages]);
// 在保存到状态前为 ID 加前缀
result.id = `do-not-render-${result.id}`;
return { messages: [result] };
```

这种方法保证消息在用户界面中完全隐藏。

## 渲染工件

Agent Chat UI 支持在聊天中渲染工件。工件在聊天右侧的侧边面板中渲染。要渲染工件，您可以从 `thread.meta.artifact` 字段获取工件上下文。以下是一个用于获取工件上下文的示例实用程序钩子：

```tsx
export function useArtifact<TContext = Record<string, unknown>>() {
  type Component = (props: {
    children: React.ReactNode;
    title?: React.ReactNode;
  }) => React.ReactNode;

  type Context = TContext | undefined;

  type Bag = {
    open: boolean;
    setOpen: (value: boolean | ((prev: boolean) => boolean)) => void;

    context: Context;
    setContext: (value: Context | ((prev: Context) => Context)) => void;
  };

  const thread = useStreamContext<
    { messages: Message[]; ui: UIMessage[] },
    { MetaType: { artifact: [Component, Bag] } }
  >();

  return thread.meta?.artifact;
}
```

之后，您可以使用 `useArtifact` 钩子中的 `Artifact` 组件渲染附加内容：

```tsx
import { useArtifact } from "../utils/use-artifact";
import { LoaderIcon } from "lucide-react";

export function Writer(props: {
  title?: string;
  content?: string;
  description?: string;
}) {
  const [Artifact, { open, setOpen }] = useArtifact();

  return (
    <>
      <div
        onClick={() => setOpen(!open)}
        className="cursor-pointer rounded-lg border p-4"
      >
        <p className="font-medium">{props.title}</p>
        <p className="text-sm text-gray-500">{props.description}</p>
      </div>

      <Artifact title={props.title}>
        <p className="p-4 whitespace-pre-wrap">{props.content}</p>
      </Artifact>
    </>
  );
}
```

## 进入生产环境

一旦准备好进入生产环境，您需要更新如何连接和认证对部署的请求。默认情况下，Agent Chat UI 为本地开发设置，并直接从客户端连接到您的 LangGraph 服务器。如果您想进入生产环境，这是不可能的，因为它要求每个用户都有自己的 LangSmith API 密钥，并自己设置 LangGraph 配置。

### 生产设置

要将 Agent Chat UI 投入生产，您需要选择两种方式之一来认证对 LangGraph 服务器的请求。下面我将概述这两个选项：

### 快速开始 - API 穿透

将 Agent Chat UI 投入生产的最快方法是使用 [API Passthrough](https://github.com/bracesproul/langgraph-nextjs-api-passthrough) 包（[NPM 链接在此](https://www.npmjs.com/package/langgraph-nextjs-api-passthrough)）。此包提供了一种简单的方法来代理请求到您的 LangGraph 服务器，并为您处理认证。

此存储库已经包含了使用此方法所需的所有代码。您需要做的唯一配置是设置适当的环境变量。

```bash
NEXT_PUBLIC_ASSISTANT_ID="agent"
# 这应该是您的 LangGraph 服务器的部署 URL
LANGGRAPH_API_URL="https://my-agent.default.us.langgraph.app"
# 这应该是您的网站 URL + "/api"。这是您连接到 API 代理的方式
NEXT_PUBLIC_API_URL="https://my-website.com/api"
# 您的 LangSmith API 密钥，在 API 代理内部注入到请求中
LANGSMITH_API_KEY="lsv2_..."
```

让我们介绍每个环境变量的作用：

- `NEXT_PUBLIC_ASSISTANT_ID`：您在通过聊天界面获取和提交运行时要使用的助手 ID。这仍然需要 `NEXT_PUBLIC_` 前缀，因为它不是秘密，我们在客户端提交请求时使用它。
- `LANGGRAPH_API_URL`：您的 LangGraph 服务器的 URL。这应该是生产部署 URL。
- `NEXT_PUBLIC_API_URL`：您的网站 URL + `/api`。这是您连接到 API 代理的方式。对于 [Agent Chat 演示](https://agentchat.vercel.app)，这将设置为 `https://agentchat.vercel.app/api`。您应该将其设置为您的生产 URL。
- `LANGSMITH_API_KEY`：在对 LangGraph 服务器发送的请求进行认证时使用的 LangSmith API 密钥。同样，不要为此添加 `NEXT_PUBLIC_` 前缀，因为它是一个秘密，仅在服务器上使用，当 API 代理将其注入到对已部署的 LangGraph 服务器的请求中时。

有关深入文档，请参考 [LangGraph Next.js API Passthrough](https://www.npmjs.com/package/langgraph-nextjs-api-passthrough) 文档。

### 高级设置 - 自定义认证

在您的 LangGraph 部署中使用自定义认证是一种高级且更强大的方式来认证对 LangGraph 服务器的请求。使用自定义认证，您可以允许从客户端发出请求，而无需 LangSmith API 密钥。此外，您可以在请求上指定自定义访问控制。

要在您的 LangGraph 部署中设置此功能，请阅读 LangGraph 自定义认证文档，适用于 [Python](https://langchain-ai.github.io/langgraph/tutorials/auth/getting_started/) 和 [TypeScript 这里](https://langchain-ai.github.io/langgraphjs/how-tos/auth/custom_auth/)。

在部署上设置好后，您应该对 Agent Chat UI 进行以下更改：

1. 配置任何额外的 API 请求，以从您的 LangGraph 部署获取认证令牌，该令牌将用于认证来自客户端的请求。
2. 将 `NEXT_PUBLIC_API_URL` 环境变量设置为您的生产 LangGraph 部署 URL。
3. 将 `NEXT_PUBLIC_ASSISTANT_ID` 环境变量设置为您在通过聊天界面获取和提交运行时要使用的助手 ID。
4. 修改 [`useTypedStream`](src/providers/Stream.tsx)（`useStream` 的扩展）钩子，通过头文件将您的认证令牌传递给 LangGraph 服务器：

```tsx
const streamValue = useTypedStream({
  apiUrl: process.env.NEXT_PUBLIC_API_URL,
  assistantId: process.env.NEXT_PUBLIC_ASSISTANT_ID,
  // ... 其他字段
  defaultHeaders: {
    Authentication: `Bearer ${addYourTokenHere}`, // 这是您传递认证令牌的地方
  },
});
```