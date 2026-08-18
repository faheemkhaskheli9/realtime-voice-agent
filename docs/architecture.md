# Architecture Notes: Real-Time Voice AI Agent

## Pipeline

```text
User Speech -> STT (Whisper) -> LLM -> Tools/RAG -> TTS -> LiveKit Audio Output (with interrupt handling loop)
```

## Components

- LiveKit-based real-time audio pipeline
- Speech-to-text (Whisper)
- LLM reasoning turn
- Text-to-speech synthesis
- Interruption (barge-in) handling
- Conversation memory across turns
- Tool/function calling mid-conversation
- Latency measurement and reporting

## Design Notes

- Keep provider/model choices swappable behind interfaces (see `multi-llm-router`
  and similar projects in this portfolio for the general pattern).
- Prefer configuration-driven pipelines (YAML/JSON in `configs/`) over hardcoded
  parameters so experiments are reproducible.
