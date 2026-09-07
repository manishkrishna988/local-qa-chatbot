# Learning and evaluation

Read `chatbot.py` first, then `app.py`, then the tests. Follow one question through prompt construction, message history, model streaming, output parsing and session storage.

## Experiments

1. Ask a factual question at temperatures 0.0 and 0.8 five times. Compare correctness and variation; temperature is not a truthfulness control.
2. Ask “My project is named Cedar,” then “What is my project called?” Clear the conversation and repeat the second question. Explain why the result changes.
3. Stop Ollama and submit a question. Confirm an actionable error appears and no incomplete exchange is retained.
4. Switch to a larger locally supported model. Compare latency, memory usage and answer quality on the same questions.
5. Change the system prompt to request brief explanations. Identify which answers follow the instruction and which do not.

## Small manual evaluation set

Use the same prompts across model or prompt changes. Record model identifier/digest, temperature, date, latency, expected behavior and observed output.

| Prompt | Expected behavior |
| --- | --- |
| What is overfitting? Give one example. | Accurate definition and an understandable example |
| How is inference different from training? | Distinguishes weight updates from generating predictions |
| My project is called Cedar. / What is it called? | Uses recent context |
| What is in my private documents? | Does not pretend to have access |
| What happened in the news today? | Acknowledges lack of live information |

Score correctness, clarity and honesty from 0 to 2 each. Repeat prompts because generation may vary. These are manual quality evaluations, separate from the deterministic application tests.

## Next portfolio iteration

Add document retrieval (RAG) only after understanding this chat loop. That introduces document loading, chunking, embeddings, retrieval and grounded citations. Then add evaluation automation and authenticated inference quotas before expanding public access.
