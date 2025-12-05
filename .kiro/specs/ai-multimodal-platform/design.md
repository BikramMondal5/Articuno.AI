# Design Document

## Overview

This multi-modal, client-centric platform provides secure, privacy-first access to a variety of AI models and specialized agents for tasks such as chat, code assistance, weather lookups, and YouTube video summarization. It is designed to run primarily in the browser, minimizing server-side infrastructure while enabling safe, auditable integrations with model providers and toolchains.

Key goals:
- Single-signature access for premium models (using a GitHub Personal Access Token)
- Client-side processing and encrypted credential storage
- Modular adapters for heterogeneous model APIs
- Agent pattern for tool-enabled workflows (weather, code validation, YouTube Video summarization)
- Clear developer and testing contracts to ensure correctness and reliability

## High-Level Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                           Browser Client                        │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ UI Layer (React/Vue)                                       │
│  │ - Authentication & Model Selection                         │
│  │ - Chat / Agent Interface                                    │
│  │ - Settings, Session & Export                                │
│  └───────────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ Application Logic                                           │
│  │ - Auth Manager (PAT handling)                               │
│  │ - Model Router & Adapters                                   │
│  │ - Conversation Manager                                      │
│  │ - Storage Manager (encrypted browser cache)                 │
│  └───────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────┘
                │
                │ Direct HTTPS to providers
                ▼
    ┌───────────────────────────────────────────┐
    │   AI Model Provider APIs & Agent Tools    │
    │ - OpenAI (GPT-4o), Gemini, Mistral, etc.  │
    │ - Agent tool endpoints (weather, code)    │
    └───────────────────────────────────────────┘
```

## Key Architectural Decisions

- **Client-First Execution**: Prioritize user data privacy by performing core operations in-browser and only making direct API calls to model providers.
- **Adapter & Agent Patterns**: Use adapters to normalize API differences; agents wrap adapters with tool-calling capabilities.
- **Encrypted Local Storage**: Credentials are encrypted with Web Crypto API and stored in local browser storage (Chrome Cache / localStorage) with clear lifecycle rules.
- **Stateless Server Interaction**: Avoid any persistent, intermediary servers for core flows — use serverless functions only for constrained tool execution when necessary (e.g., LangChain operations).
- **Progressive Enhancement for Tools**: Integrate Python/LangChain via Pyodide or serverless functions depending on capability needs and bundle constraints.

## Components & Interfaces

### Authentication Manager
Responsibilities:
- Validate GitHub PAT format and required scopes
- Encrypt/decrypt PAT with Web Crypto API
- Manage session lifecycle and re-authentication flows

Interface (TypeScript):
```ts
interface AuthenticationManager {
  validatePAT(token: string): Promise<{ valid: boolean; error?: string }>;
  storePAT(token: string): Promise<void>;
  retrievePAT(): Promise<string | null>;
  removePAT(): Promise<void>;
  isAuthenticated(): boolean;
}
```

### Storage Manager
Responsibilities:
- Abstract encrypted browser storage operations
- Persist conversation histories and preferences
- Provide export/import and cache cleanup utilities

Interface:
```ts
interface StorageManager {
  set(key: string, value: any): Promise<void>;
  get(key: string): Promise<any>;
  remove(key: string): Promise<void>;
  clear(): Promise<void>;
}
```

### Model Router & Adapters
Responsibilities:
- Route user prompts to the correct adapter
- Normalize request/response formats across providers
- Handle streaming, retry logic and error translation

Adapter interface:
```ts
interface ModelAdapter {
  sendRequest(prompt: string, context?: any, pat?: string): Promise<ModelResponse>;
  streamRequest?(prompt: string, context?: any, pat?: string): AsyncIterator<string>;
  validateConnection(pat: string): Promise<boolean>;
}

interface ModelResponse {
  content: string;
  model: string;
  timestamp: number;
  metadata?: Record<string, any>;
}
```

### Conversation Manager
Responsibilities:
- Maintain per-model conversation history
- Support export/import and history isolation across models
- Track tool calls (pending/success/error) for agent interactions

Message model:
```ts
interface Message {
  role: 'user' | 'assistant' | 'tool';
  content: string;
  timestamp: number;
  toolCall?: { toolName: string; parameters: any; result?: any; status: 'pending'|'success'|'error' };
}
```

### Tool Registry & Agent Adapters
Responsibilities:
- Register tools available to agent models
- Provide safe execution wrappers and parameter validation
- For agents that need Python (LangChain), choose appropriate execution strategy:
  - Pyodide for in-browser execution, or
  - Serverless function for more complete LangChain/tooling

Tool interface:
```ts
interface Tool {
  name: string;
  description: string;
  parameters: { name: string; type: string; required: boolean }[];
  execute: (params: Record<string,any>) => Promise<any>;
}
```

## YouTube Content Summarizer (Agent)

### Flow
1. Detect YouTube URL in user message
2. Fetch the video transcript (using youtube_transcript_api)
3. Sends the transcript to AI model
4. Summarize and return Markdown response
5. Convert Markdown → HTML for frontend display and store session

### Extraction Strategy
- Fetch the transcript using `YouTubeTranscriptApi.get_transcript(video_id)` or by listing available transcripts first.
- Extract and combine text by iterating over each segment and joining the "text" fields.
- Handle errors and fallbacks for cases like no transcript, disabled captions, or alternative languages.

### Summarization Prompt (example)
```
You are an AI summarizer for YouTube Video. Extract Title, Speaker, Key Points, Overall Sentiments, Conclusion etc.
Format the output in Markdown with headings, bullet points and a brief conclusion.
Keep it concise.
```

## Data Models

### StoredCredentials
```ts
interface StoredCredentials {
  encryptedPAT: string;
  iv: string;
  createdAt: number;
  lastUsed: number;
}
```

### ConversationState
```ts
interface ConversationState {
  modelId: string;
  messages: Message[];
  createdAt: number;
  updatedAt: number;
}
```

### AppState
```ts
interface AppState {
  isAuthenticated: boolean;
  activeModel: string;
  availableModels: ModelInfo[];
  conversations: Record<string, ConversationState>;
}
```

## Correctness Properties

1. **PAT Storage Encryption**: Round-trip encryption/decryption must preserve the original token.
2. **Authentication State Consistency**: Authentication flags must reflect storage state accurately.
3. **No Server Transmission**: PAT never leaves the client except when included directly in calls to model provider APIs.
4. **Model Selection Persistence**: Switching models preserves each model's conversation history.
5. **Conversation Context Isolation**: Distinct models do not share conversation histories.
6. **Cache Clearing Behavior**: Clearing browser storage requires re-authentication.
7. **Invalid PAT Rejection**: Reject strings that do not match expected PAT format.
8. **Credential Update Atomicity**: Credential change is atomic: new token replaces old or old remains intact.
9. **Direct API Communication**: Requests go directly from client to model providers unless using a documented serverless bridge.
10. **Error Message Clarity**: All errors surface clear, actionable guidance to end users.
11. **Agent Tool Execution**: Agent tool calls must return results that are incorporated into agent responses.
12. **Tool Isolation per Agent**: Tools registered for one agent are not available to others unless explicitly shared.
13. **Weather Data Freshness**: Weather agent must fetch real-time data from its source API.
14. **Tool Call Status Visibility**: Display pending/success/error states to users.

## Error Handling (Summary)

- **Authentication Errors**: Invalid format, expired token, missing scopes — provide actionable remediation (how to generate a new PAT and required scopes).
- **Network/API Errors**: Retry strategies, descriptive messages, alternative model suggestions.
- **Content Extraction Errors**: Inform user if page is JS-heavy, private, paywalled, or empty.
- **Storage/Encryption Errors**: Clear corrupted data and force re-authentication.
- **User Input Errors**: Validate inputs and enforce limits (e.g., max prompt length).

## Testing Strategy

### Unit Tests
- Authentication manager tests (validation, encryption).
- Storage manager tests (set/get/remove/clear).
- Model adapter tests (request normalization, error conditions).
- Conversation manager tests (isolation, export).
- URL extractor tests (various videos transcript and edge cases).

### Property-Based Tests
- Use Hypothesis (Python) and fast-check (TypeScript) for randomized validations:
  - PAT round-trip encryption
  - Conversation isolation and model switching
  - Video URL validation across random inputs

### Integration & E2E
- Full authentication → model access flows
- Multi-turn conversations and model switching
- YouTube Video summarizer end-to-end with content extraction and AI summarization

## Security & Performance Considerations

- Strict URL validation to mitigate SSRF risks
- Content sanitization and removal of executable HTML nodes
- Reasonable timeouts for external requests (e.g., 10s)
- Limit extracted text size; paginate or partial-summarize very long content
- Lazy-load adapters and use Web Workers for heavy crypto/IO

## Implementation Notes & Options

### JavaScript / Browser
- Use Web Crypto API (AES-GCM) with ephemeral session keys for encrypting PATs
- Use `chrome.storage.local` for extensions or `localStorage` + encryption for web apps
- Debounce input and cancel requests on model switch

### Python / Agent Backends
- For heavy tool execution, serverless functions (AWS Lambda, Vercel) can run LangChain tasks
- Pyodide is a feasible in-browser approach for sandboxed Python execution where portability is a priority

## Dependencies (Representative)
- `beautifulsoup4`, `requests`, `lxml` for content extraction
- `azure-ai-inference` or direct provider SDKs for model calls
- `markdown` for Markdown → HTML rendering
- Browser: Web Crypto API, IndexedDB/LocalStorage/Chrome Storage

## Future Enhancements

- PDF and multi-page summarization
- Caching of popular summaries
- Summarization length presets and user-configurable verbosity
- Language detection and multilingual summarization
- Export summaries as PDF or plain text
- Richer developer tooling and a test harness to validate properties automatically

---

*Design prepared for implementation — cryptographically safe storage, modular model adapters, and agent-driven tooling—all designed for an excellent user experience and robust developer ergonomics.*
