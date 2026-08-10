# DL-01: LLM Foundations

## 📘 Course Description

Foundations and practical applications of **Artificial Intelligence (AI)** and **Large Language Models (LLMs)** — from the evolution of Natural Language Processing (NLP) to modern Transformer-based language models.

---

## 📊 Assessment Methods

| Component | Points | Description |
| --- | ---: | --- |
| **Class Participation** | 10 | Attendance, activity engagement, and sharing opinions |
| **Hands-on Projects** | 30 | Practical work with LLMs and AI tools for programming tasks and mini-projects |
| **Midterm Exam** | 30 | Tests understanding of key concepts, including LLMs, AI techniques, and applications |
| **Final Exam** | 30 | Assesses overall learning outcomes and the ability to apply knowledge to solve problems |
| **Total** | **100** | |

---

## 🛠️ Software / Tools

| Software / Tool | Description |
| --- | --- |
| **Python** | Programming language widely used for AI, machine learning, and data processing |
| **TensorFlow** | Open-source framework for building and training machine learning models |
| **PyTorch** | Deep learning framework widely used for research and model development |
| **Visual Studio Code** | Lightweight code editor with extensions and integrated development tools |

---

# 🧠 1. Introduction to Large Language Models

## What is a Large Language Model?

A **Large Language Model (LLM)** is a neural language model trained on large-scale data to learn patterns and relationships in language. Modern LLMs are primarily based on the **Transformer architecture** and can perform a wide range of language-related tasks.

### Key Characteristics

| Characteristic | Description |
| --- | --- |
| **Large-Scale Data** | Trained on large collections of text, code, documents, and other data |
| **Large Number of Parameters** | Uses many trainable parameters to learn complex patterns |
| **Transformer Architecture** | Uses Attention mechanisms to model relationships between tokens |
| **General-Purpose Capability** | A single model can support many different language tasks |
| **Scalability** | Capabilities can improve with appropriate increases in data, model capacity, and compute |

# 🕰️ 2. Evolution of NLP

Natural Language Processing has evolved from manually designed linguistic rules to large-scale neural language models.

| Era | Stage | Main Idea | Reference |
| --- | --- | --- | --- |
| **1950s–1970s** | **Rule-Based NLP** | Uses manually designed rules and linguistic knowledge | [Turing, 1950](https://doi.org/10.1093/mind/LIX.236.433) |
| **1980s–1990s** | **Statistical NLP** | Uses probability and statistical models for language processing | [Manning & Schütze, 1999](https://nlp.stanford.edu/fsnlp/) |
| **1990s–2000s** | **Machine Learning** | Applies machine learning algorithms to NLP tasks | [Mitchell, 1997](https://www.cs.cmu.edu/~tom/mlbook.html) |
| **2000s** | **Neural Language Models** | Neural networks learn distributed representations of language | [Bengio et al., 2003](https://www.jmlr.org/papers/v3/bengio03a.html) |
| **2000s–2010s** | **RNN** | Models sequential information and dependencies over time | [Mikolov et al., 2010](https://www.fit.vut.cz/research/group/speech/public/publi/2010/mikolov_interspeech2010_IS100722.pdf) |
| **2010s** | **LSTM** | Improves the learning of long-term dependencies | [Hochreiter & Schmidhuber, 1997](https://doi.org/10.1162/neco.1997.9.8.1735) |
| **2014** | **Attention Mechanism** | Allows models to focus on relevant parts of an input sequence | [Bahdanau et al., 2014](https://arxiv.org/abs/1409.0473) |
| **2017** | **Transformer** | Uses Self-Attention as the core mechanism for sequence modeling | [Vaswani et al., 2017](https://arxiv.org/abs/1706.03762) |
| **2018–Present** | **Large Language Models** | Large-scale pretrained Transformer models support general-purpose language tasks | [Devlin et al., 2018](https://arxiv.org/abs/1810.04805) / [Brown et al., 2020](https://arxiv.org/abs/2005.14165) |

---

# 📖 3. Language Models

## What is a Language Model?

A **Language Model (LM)** estimates the probability of a sequence of words or tokens:

**P(w₁, w₂, ..., wₙ)**

A common use of a language model is to predict the next token based on the previous context.

### How It Works

| Step | Process | Description |
| ---: | --- | --- |
| **1** | **Input Sequence** | Receives a sequence of words or tokens |
| **2** | **Context Processing** | Analyzes the previous tokens |
| **3** | **Probability Estimation** | Calculates probabilities for possible next tokens |
| **4** | **Prediction** | Selects or predicts the next token |
| **5** | **Continuation** | Uses the generated token as part of the next context |

### Example

Given:

`I love machine`

the model might produce:

| Next Token | Probability |
| --- | ---: |
| **learning** | 0.70 |
| **vision** | 0.20 |
| **car** | 0.10 |

The model therefore considers **learning** the most likely continuation in this simplified example.

---

# ⚖️ 4. Traditional NLP vs. LLMs

| Feature | Traditional NLP | Large Language Models |
| --- | --- | --- |
| **Feature Design** | Often requires manually designed features | Learns representations automatically |
| **Vocabulary** | Can suffer from Out-of-Vocabulary (OOV) problems | Uses tokenization to represent a broad range of text |
| **Context** | Often limited by the chosen method | Can model richer and longer contextual relationships |
| **Task Design** | Usually built for specific tasks | Can support multiple tasks using one model |
| **Adaptation** | Often requires a new model or pipeline | Can adapt through prompting or fine-tuning |
| **Generation** | Limited natural-language generation | Can generate fluent, context-aware text |

### Why LLMs?

LLMs are important because they can:

- Learn language representations automatically
- Capture complex contextual relationships
- Perform multiple tasks with the same model
- Support zero-shot and few-shot learning
- Generate natural-language responses
- Be adapted to specialized tasks and domains

---

# 🧩 5. Core Components of LLMs

| Component | Purpose | Result |
| --- | --- | --- |
| **Tokenization** | Splits text into processable units | Tokens / Token IDs |
| **Embedding** | Converts tokens into numerical vectors | Token representations |
| **Positional Information** | Represents token order or position | Position-aware representations |
| **Self-Attention** | Learns relationships between tokens | Contextual representations |
| **Transformer Blocks** | Repeatedly transform contextual information | Deep language representations |
| **Output Layer** | Produces scores or probabilities over tokens | Next-token probabilities |

### Tokenization

LLMs do not directly process raw text. A tokenizer converts text into smaller units called **tokens**.

Example:

| Original Text | Possible Tokens |
| --- | --- |
| `Artificial intelligence is powerful` | `Artificial`, `intelligence`, `is`, `powerful` |

Actual tokenization depends on the tokenizer used by each model.

### Embedding

Each token is converted into a numerical vector that can be processed by the neural network.

| Token | Example Representation |
| --- | --- |
| `cat` | `[0.21, 0.53, 0.18, ...]` |
| `dog` | `[0.24, 0.49, 0.20, ...]` |

---

# 🏗️ 6. Transformer Architecture

> The **Transformer** is a neural network architecture introduced by Vaswani et al. that relies primarily on Attention mechanisms for sequence modeling.  
> **[Vaswani et al., 2017](https://arxiv.org/abs/1706.03762)**

## Why Transformer?

Traditional recurrent models such as RNNs process sequences recurrently, which creates limitations for parallel computation and long-range dependency modeling.

| RNN Limitation | Transformer Approach |
| --- | --- |
| **Sequential computation** | Enables highly parallel computation during training |
| **Long dependency paths** | Attention directly connects different token positions |
| **Training efficiency** | Parallel processing improves hardware utilization |
| **Long-range context** | Attention can model relationships between distant tokens |
| **Scalability** | Architecture scales effectively to large models and datasets |

## Transformer Components

| Component | Function |
| --- | --- |
| **Token Embedding** | Converts tokens into numerical vectors |
| **Positional Encoding** | Provides information about token position |
| **Self-Attention** | Determines relationships between tokens in the same sequence |
| **Multi-Head Attention** | Learns multiple attention relationships simultaneously |
| **Feed Forward Network** | Applies nonlinear transformations to each token representation |
| **Residual Connection** | Preserves information across layers |
| **Layer Normalization** | Helps stabilize network training |
| **Masked Attention** | Prevents access to future tokens during autoregressive generation |
| **Cross-Attention** | Connects Decoder representations with Encoder outputs in Encoder–Decoder models |

## Main Transformer Architectures

| Architecture | Structure | Typical Purpose | Example |
| --- | --- | --- | --- |
| **Encoder-Only** | Transformer Encoder | Understanding and representation | BERT |
| **Decoder-Only** | Causal Transformer | Autoregressive text generation | GPT-style models |
| **Encoder–Decoder** | Encoder + Decoder | Sequence-to-sequence tasks | T5 |

---

# 🎯 7. Self-Attention

**Self-Attention** allows each token to consider other tokens in the same sequence when building its contextual representation.

For example, in the sentence:

> `The animal didn't cross the street because it was tired.`

the model needs contextual relationships to determine what **“it”** refers to.

### Main Elements

| Element | Purpose |
| --- | --- |
| **Query (Q)** | Represents what the current token is looking for |
| **Key (K)** | Represents information available from other tokens |
| **Value (V)** | Contains the information that can be passed to the output |
| **Attention Score** | Measures how strongly tokens should attend to one another |
| **Attention Weight** | Normalized importance assigned to each token |

Self-Attention is one of the key mechanisms that allows Transformers to build contextual representations.

---

# 🏋️ 8. LLM Training

LLM development commonly involves **Pretraining** followed by optional adaptation such as **Fine-Tuning**.

## Pretraining

Pretraining teaches the model general language patterns using large-scale datasets.

| Step | Process | Description |
| ---: | --- | --- |
| **1** | **Data Preparation** | Collect and prepare large-scale training data |
| **2** | **Tokenization** | Convert text into token sequences |
| **3** | **Forward Pass** | Process tokens through the model |
| **4** | **Prediction** | Generate predictions according to the training objective |
| **5** | **Loss Calculation** | Measure prediction error |
| **6** | **Backpropagation** | Calculate gradients |
| **7** | **Optimization** | Update model parameters |

The result of large-scale pretraining is commonly called a **Foundation Model**.

## Pretraining vs. Fine-Tuning

| Feature | Pretraining | Fine-Tuning |
| --- | --- | --- |
| **Purpose** | Learn general capabilities | Adapt existing capabilities |
| **Data** | Large-scale general data | Specialized data |
| **Starting Point** | Base model parameters | Pretrained model |
| **Training Scale** | Very large | Usually smaller |
| **Output** | Foundation Model | Adapted Model |

## Fine-Tuning Methods

| Method | Purpose | Example |
| --- | --- | --- |
| **Instruction Tuning** | Improve instruction-following behavior | Instruction–response datasets |
| **Domain Tuning** | Adapt language knowledge to a domain | Medical, legal, finance |
| **Task Tuning** | Optimize for a particular task | Classification, summarization |

---

# ⚙️ 9. LLM Inference

**Inference** is the process of using a trained model to generate an output from a prompt.

## Inference Process

| Step | Stage | Description |
| ---: | --- | --- |
| **1** | **Prompt** | User provides an instruction or input |
| **2** | **Tokenization** | Prompt is converted into token IDs |
| **3** | **Model Processing** | LLM processes the current context |
| **4** | **Prediction** | Model produces probabilities for possible next tokens |
| **5** | **Token Selection** | A generation strategy selects the next token |
| **6** | **Context Update** | Generated token is added to the current context |
| **7** | **Decoding** | Tokens are converted back into readable text |

LLMs commonly generate text **autoregressively**: each generated token becomes part of the context used to predict the next token.

## Generation Settings

| Setting | Function |
| --- | --- |
| **Temperature** | Controls randomness in token selection |
| **Top-k** | Restricts selection to the k highest-probability tokens |
| **Top-p** | Restricts selection using cumulative probability |
| **Max Tokens** | Sets the maximum generation length |
| **Repetition Penalty** | Reduces excessive repetition |
| **Stop Sequences** | Defines conditions that terminate generation |

### Example

**Prompt:** `Artificial Intelligence is ...`

| Candidate Token | Example Probability |
| --- | ---: |
| **a** | 0.42 |
| **the** | 0.25 |
| **changing** | 0.12 |
| **used** | 0.08 |
| **Others** | 0.13 |

The selected token is added to the context, and the model repeats the prediction process until generation stops.

---

# 🌍 10. Applications of LLMs

| Application | Example | Input | Output |
| --- | --- | --- | --- |
| **Chatbot** | Customer Support | User question | Conversational answer |
| **Programming** | Code Assistant | Programming request | Generated or corrected code |
| **Education** | AI Tutor | Student question | Explanation or learning content |
| **Healthcare** | Document Summarization | Clinical document | Summary |
| **Translation** | English–Thai Translation | Source text | Translated text |
| **Document Analysis** | Report Analyzer | Document | Extracted information |
| **Research** | Research Assistant | Research question | Summarized information |
| **Robotics** | Instruction Understanding | Natural-language instruction | Task representation or plan |

---

# ⚠️ 11. Limitations and Challenges

| Challenge | Description | Why It Matters |
| --- | --- | --- |
| **Hallucination** | May generate incorrect or unsupported information | Outputs require verification |
| **Bias** | May reproduce patterns and biases in training data | Can affect fairness and reliability |
| **Knowledge Freshness** | Internal knowledge may not include recent information | Responses can become outdated |
| **Computational Cost** | Large models require significant compute | Increases training and deployment costs |
| **Memory Requirements** | Large models require substantial memory | Limits deployment on smaller devices |
| **Privacy** | Sensitive information requires careful handling | Important for confidential data |
| **Security** | Applications may be vulnerable to attacks such as prompt injection | Can affect system integrity |
| **Explainability** | Internal model behavior can be difficult to interpret | Makes auditing and analysis harder |
| **Energy Consumption** | Training and inference consume computational resources | Affects cost and sustainability |

---

# ✅ 12. Summary

| Topic | Key Idea |
| --- | --- |
| **Language Model** | Predicts probabilities over language sequences and tokens |
| **Tokenization** | Converts text into tokens |
| **Embedding** | Represents tokens as numerical vectors |
| **Transformer** | Core architecture behind many modern LLMs |
| **Self-Attention** | Models contextual relationships between tokens |
| **Pretraining** | Builds general language capabilities from large-scale data |
| **Fine-Tuning** | Adapts a pretrained model to specific needs |
| **Inference** | Uses a trained model to generate responses |
| **Applications** | Applies LLMs to language, coding, education, research, and other tasks |
| **Limitations** | Includes hallucination, bias, cost, privacy, security, and explainability |

---
