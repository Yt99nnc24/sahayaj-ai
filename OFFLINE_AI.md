# Local offline assistant — no paid API

The assistant no longer calls OpenAI or any hosted model service. Old OPENAI_API_KEY settings are ignored. Never commit .env.

## Works immediately
Start the app with start-demo.cmd or start.cmd. In default auto mode, if no downloaded local model is available, the bundled **Basic offline helper** answers limited workflow, report, visit-preparation, branch and symptom-documentation questions. It has English, Hindi and Punjabi guidance. It explicitly admits unknown answers. It is rule-based, not an LLM or a trained medical expert.

For zero model/network calls, use SAHAYAJ_AI_MODE=basic in .env. No model install or key is required for this mode.

## Open-ended local AI (one-time setup)
1. Install Ollama from https://ollama.com/download/windows.
2. Quit Ollama from its tray icon. In a new CMD, run:
   set "OLLAMA_NO_CLOUD=1"
   ollama serve
   Keep this terminal running. If the port is already in use, quit the older Ollama tray process first; do not expose port 11434 publicly.
3. Double-click setup-offline.cmd. It downloads qwen2.5:1.5b once (about 986 MB, plus Ollama runtime).
4. Start SAHAYAJ. After downloading, the local model can run with internet disconnected. No API key or cloud login is required.

Default .env:
SAHAYAJ_AI_MODE=auto
SAHAYAJ_LOCAL_MODEL=qwen2.5:1.5b

Modes: auto tries local Ollama then labels its basic-helper fallback; basic never contacts a model; ollama requires the downloaded model and shows an actionable setup error instead of falling back. Supported downloaded models: qwen2.5:0.5b, :1.5b, :3b, :7b. Smaller models may be less capable; larger models need more memory. The included setup downloads the default only. Language quality and speed depend on model/hardware; the small model is not clinically validated.

## Data and behavior
Flask contacts only http://127.0.0.1:11434/api/show and /api/chat, with environment proxies and redirects disabled. Cloud-tagged models and models exposing remote-host metadata are rejected. Disable Ollama cloud features as instructed above. No online fallback, model tools or autonomous actions are enabled. The app never pulls models during a chat. Model downloads are an explicit setup step.

Doctor case context remains a separate opt-in with ownership checks. Patient records are not automatically attached. Chat suggestions never change or finalize records. Names are excluded from doctor context but free text may still identify someone. Chat is held in page memory; only request metadata is audited. Urgency phrases use immediate deterministic guidance rather than waiting for inference. This is not emergency triage, diagnosis or prescribing software.

The model download/runtime are not bundled in the GitHub ZIP. Initial installation/download needs internet and disk space; runtime does not require paid tokens. Browser voice dictation is a separate feature and may still require your browser vendor's online speech service. Use typed chat to keep the AI interaction offline.

## Verification
Offline tests cover no-network basic replies, language variants, unknown answers, urgent-message bypass, local model payload, cloud/redirect/proxy rejection, explicit fallback labels and authenticated chat without an API key. Synthetic CI uses basic mode and mocked Ollama; it does not download a model. A successful CI run does not establish real model quality or microphone behavior.

References:
- https://docs.ollama.com/api/chat
- https://docs.ollama.com/faq
- https://docs.ollama.com/windows
- https://ollama.com/library/qwen2.5:1.5b
