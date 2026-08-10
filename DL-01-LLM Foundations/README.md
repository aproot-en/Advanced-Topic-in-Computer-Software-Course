# DL-01-LLM Foundations

Advanced Topics in Computer Software — AI & LLM Course

📘 Course Description
New academic study in computer software.

The course follows the official course description and is enhanced with modern AI topics, including Large Language Models (LLMs), Retrieval-Augmented Generation (RAG), and Agentic AI. It also features hands-on laboratories, projects, and real-world applications. A complete list of topics is provided in the Course Contents section.
---

1️⃣ Chapter 1: LLM Foundations
Chapter 1 introduces the foundations of Large Language Models (LLMs) and traces how modern language models evolved from traditional Natural Language Processing (NLP). Students learn the core building blocks behind modern LLMs — Language Models, Neural Language Models, the Transformer architecture, tokenization, embeddings, Self-Attention, training, fine-tuning, and inference.
<details>
<summary><strong>📂 Click to expand full Chapter 1 content</strong></summary>
🧠 What is a Large Language Model?
A Large Language Model (LLM) is an AI model designed to understand and generate human language. LLMs learn patterns and relationships from large-scale training data and use that learned knowledge to understand input and generate new text.
  
Basic process:
```text
Large-Scale Training Data → Training → LLM → Understand & Generate Language
```

Example models: GPT · Llama · Gemini · Mistral · Claude · DeepSeek

Common capabilities: text generation, question answering, summarization, translation, programming, document analysis, research assistance.
---
📜 Evolution of NLP
```text
Rule-Based NLP → Statistical NLP → Machine Learning → Word Embedding
→ RNN → LSTM → Attention → Transformer → Large Language Models
```
Stage	Main Idea
Rule-Based NLP	Uses manually defined linguistic rules
Statistical NLP	Uses probabilities and statistical methods
Machine Learning	Learns language patterns from data
Word Embedding	Represents words as numerical vectors
RNN	Processes sequential language information
LSTM	Improves learning of long-term dependencies
Attention	Focuses on important information in a sequence
Transformer	Uses Self-Attention for language processing
LLM	Learns large-scale language knowledge using Transformer architectures
---
📖 What is a Language Model?
A Language Model (LM) estimates the probability of a sequence of words or tokens:
```text
P(w₁, w₂, ..., wₙ)
```
Goal: given previous words or tokens, predict what is likely to come next.
```text
w₁ → w₂ → w₃ → ... → wₙ
```
Example: `I → enjoy → learning → ...`
---
❓ Why Large Language Models?
Traditional NLP	Large Language Models
Requires manually designed features	Learn representations automatically
Limited vocabulary	Understand broader context
Difficulty understanding complex context	Generate natural language
Often requires task-specific systems	Learn from few examples and perform multiple tasks
```text
Traditional NLP:  Rules + Features → Task-Specific Model → Output
LLM:              Large-Scale Data → Transformer → Multiple Language Tasks
```
---
🧠 Neural Language Model
A Neural Language Model uses neural networks to learn language patterns and predict the next word or token.
```text
Input → Embedding Layer → Hidden Layer → Softmax Output Layer → Next-Word Probability
```
Embedding Layer — transforms words into dense numerical vectors (e.g., `cat → [0.21, 0.53, 0.18, ...]`)
Hidden Layer — processes representations and learns relationships between input features
Softmax Output Layer — produces a probability distribution over possible next tokens
Limitation: traditional neural language models struggle to capture long-range relationships due to limited or fixed context windows.
---
⚡ Why Transformer?
Problems with RNNs: sequential computation, slow processing of long sequences, limited parallelization, difficulty learning long-range dependencies, vanishing gradients.
Transformer's solution: Self-Attention captures relationships between all tokens directly.
```text
RNN:          Token → Token → Token → Token   (sequential)
Transformer:  Token ↔ Token ↔ Token ↔ Token   (Self-Attention, parallel)
```
Advantages: parallel processing, faster training, better long-range dependency modeling, improved contextual understanding.
> **Key takeaway:** Transformer uses Self-Attention to capture relationships between tokens, overcoming many limitations of sequential RNN architectures.
---
🏗 Transformer Architecture
The original Transformer consists of an Encoder and a Decoder.
```text
Input Tokens → Embedding → Positional Encoding → Encoder → Decoder → Linear → Softmax → Output Probabilities
```
Encoder: `Input → Multi-Head Self-Attention → Add & Norm → Feed Forward Network → Add & Norm → Output`
Decoder: `Output Tokens → Masked Multi-Head Self-Attention → Add & Norm → Multi-Head Cross-Attention → Add & Norm → Feed Forward Network → Add & Norm → Linear → Softmax`
Key components: Token Embedding, Positional Encoding, Self-Attention, Multi-Head Attention, Masked Multi-Head Attention, Cross-Attention, Feed Forward Network, Add & Norm, Linear Layer, Softmax.
---
🔤 Token In → Token Out
LLMs process text as tokens, which must be created before the model can process any input.
```text
Text → Tokenization → Token IDs → Embedding → LLM
     → Next-Token Prediction → Token ID → Decode → Generated Text
```
Example:
```text
"ChatGPT is amazing!" → Tokenization → Tokens/Token IDs → Embedding → LLM → Next-Token Prediction → Token Out
```
The generated token is appended to the sequence and used to predict the next token — this repeats until the response is complete.
---
✨ What Makes an LLM "Large"?
```text
Large-Scale Data + Neural Networks + Transformer + Self-Attention + Large-Scale Training = LLM
```
Characteristic	Description
Large-Scale Data	Learns from large collections of language data
Large Neural Networks	Uses architectures with large numbers of trainable parameters
Transformer Architecture	Uses Transformer-based architectures for language processing
Self-Attention	Captures relationships between tokens within the context
Large-Scale Training	Learns general language knowledge through large-scale pretraining
---
🏋️ LLM Training Pipeline
```text
Training Data → Pretraining → Foundation Model → Fine-Tuning → Adapted Model
```
1. Training Data — books, websites, articles, code, documents, conversations (potentially billions or trillions of tokens).
2. Pretraining — the model learns general language patterns from large-scale data:
```text
Training Data → Tokenization → Transformer → Prediction → Loss → Backpropagation → Parameter Update
```
The result is a Foundation Model.
3. Fine-Tuning — adapts the pretrained model to a specific task or domain (Instruction Tuning, Domain Tuning, Task Tuning):
```text
Foundation Model + Specific Dataset → Fine-Tuning → Adapted Model
```
---
⚙️ Inference Pipeline
Inference is the process of using a trained LLM to generate output from a user prompt.
```text
Prompt → Tokenizer → LLM → Sampling → Generated Text
```
Prompt — the user provides an instruction or input text
Tokenizer — the prompt is converted into tokens and Token IDs
LLM — the model processes tokens and generates probabilities for possible next tokens
Sampling — a generation strategy selects the next token (Temperature, Top-k, Top-p, Max Tokens, Repetition Penalty, Stop Sequences)
Generated Text — generated tokens are decoded back into human-readable text
---
🚀 Applications of LLMs
Application	Description
🤖 Chatbot	Conversation and question answering
💻 Programming	Code generation and programming assistance
🎓 Education	Learning support and educational content
🏥 Healthcare	Medical information and documentation support
🌐 Translation	Translation between languages
📄 Document Analysis	Summarization and information extraction
🔍 Research Assistant	Searching, analyzing, and organizing information
🦾 Robotics	Language interaction and intelligent decision support
---
⚠️ Limitations of LLMs
Limitation	Description
Hallucination	May generate incorrect or unsupported information
Bias	May reflect biases present in training data
High Cost	Training and inference can require significant resources
Computational Resources	Large models require substantial memory and compute power
Privacy	Sensitive information must be handled carefully
Security	Susceptible to attacks such as prompt injection
Explainability	Model decisions can be difficult to explain
Energy Consumption	Large-scale training and inference consume significant energy
> **Key takeaway:** LLMs are powerful tools, but their outputs must be evaluated carefully and used responsibly.
---

