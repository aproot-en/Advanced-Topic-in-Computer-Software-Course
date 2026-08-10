# DL-01: LLM Foundations

## 📘 Course Description

New academic study in computer software.

The course follows the official course description and is enhanced with modern AI topics, including Large Language Models (LLMs), Retrieval-Augmented Generation (RAG), and Agentic AI. It also features hands-on laboratories, projects, and real-world applications. A complete list of topics is provided in the Course Contents section.

---

## 📊 Assessment Methods

| Component | Points | Description |
| --- | ---: | --- |
| **Class Participation** | 10 | Attendance, participation in class activities, and sharing ideas |
| **Hands-on Projects** | 30 | Practical work with LLMs, AI tools, programming tasks, and mini-projects |
| **Midterm Exam** | 30 | Tests understanding of LLM concepts, AI techniques, and their applications |
| **Final Exam** | 30 | Evaluates overall understanding and the ability to apply knowledge to solve problems |
| **Total** | **100** | |

---

## 🛠️ Software / Tools

| Software / Tool | Description |
| --- | --- |
| **Python** | A widely used programming language for AI, machine learning, and data processing |
| **TensorFlow** | An open-source framework for building and training machine learning and deep learning models |
| **PyTorch** | A flexible deep learning framework commonly used for research and model development |
| **Visual Studio Code** | A lightweight code editor with extensions and integrated development tools |

---

# 🧠 1. Introduction to Large Language Models

## What is a Large Language Model?

A **Large Language Model (LLM)** is a type of neural language model trained on large amounts of data to learn language patterns, relationships, and context.

Most modern LLMs are based on the **Transformer architecture**, which allows them to process language efficiently and perform many different tasks such as answering questions, generating text, summarizing documents, translating languages, and assisting with programming.

### Key Characteristics

| Characteristic | Description | Reference |
| --- | --- | --- |
| **Large-Scale Data** | Trained on large collections of text, code, documents, and other data | [Brown et al., 2020](https://arxiv.org/abs/2005.14165) |
| **Large Number of Parameters** | Uses many trainable parameters to learn complex language patterns | [Brown et al., 2020](https://arxiv.org/abs/2005.14165) |
| **Transformer Architecture** | Uses Attention mechanisms to understand relationships between tokens | [Vaswani et al., 2017](https://arxiv.org/abs/1706.03762) |
| **General-Purpose Capability** | One model can support many different language tasks | [Brown et al., 2020](https://arxiv.org/abs/2005.14165) |
| **Scalability** | Model performance can improve when data, model size, and computing resources increase | [Kaplan et al., 2020](https://arxiv.org/abs/2001.08361) |

### Example LLM Families

| Model Family | Organization |
| --- | --- |
| **GPT** | OpenAI |
| **Llama** | Meta |
| **Gemini** | Google |
| **Claude** | Anthropic |
| **Mistral** | Mistral AI |
| **DeepSeek** | DeepSeek |

---

# 🕰️ 2. Evolution of NLP

Natural Language Processing has developed from manually written language rules to large-scale neural models that can understand and generate text.

| Era | Stage | Main Idea | Reference |
| --- | --- | --- | --- |
| **1950s–1970s** | **Rule-Based NLP** | Uses manually created rules and linguistic knowledge to process language | [Turing, 1950](https://doi.org/10.1093/mind/LIX.236.433) |
| **1980s–1990s** | **Statistical NLP** | Uses probability and statistical methods to analyze language | [Manning & Schütze, 1999](https://nlp.stanford.edu/fsnlp/) |
| **1990s–2000s** | **Machine Learning** | Applies machine learning methods to NLP tasks | [Mitchell, 1997](https://www.cs.cmu.edu/~tom/mlbook.html) |
| **2000s** | **Neural Language Models** | Uses neural networks to learn language representations | [Bengio et al., 2003](https://www.jmlr.org/papers/v3/bengio03a.html) |
| **2000s–2010s** | **RNN** | Processes sequential information and learns relationships over time | [Mikolov et al., 2010](https://www.fit.vut.cz/research/group/speech/public/publi/2010/mikolov_interspeech2010_IS100722.pdf) |
| **2010s** | **LSTM** | Improves the ability of recurrent networks to remember information over longer sequences | [Hochreiter & Schmidhuber, 1997](https://doi.org/10.1162/neco.1997.9.8.1735) |
| **2014** | **Attention Mechanism** | Allows models to focus on important parts of the input | [Bahdanau et al., 2014](https://arxiv.org/abs/1409.0473) |
| **2017** | **Transformer** | Uses Self-Attention to model relationships between tokens | [Vaswani et al., 2017](https://arxiv.org/abs/1706.03762) |
| **2018–Present** | **Large Language Models** | Large pretrained Transformer models are used for many different language tasks | [Devlin et al., 2018](https://arxiv.org/abs/1810.04805) / [Brown et al., 2020](https://arxiv.org/abs/2005.14165) |

---

# 📖 3. Language Models

## What is a Language Model?

A **Language Model (LM)** is a model that estimates the probability of a sequence of words or tokens.

**P(w₁, w₂, ..., wₙ)**

One common task of a Language Model is to predict the next token based on the previous context.

> **Reference:** [Bengio et al., 2003](https://www.jmlr.org/papers/v3/bengio03a.html)

### How It Works

| Step | Process | Description |
| ---: | --- | --- |
| **1** | **Input Sequence** | The model receives a sequence of words or tokens |
| **2** | **Context Processing** | The model analyzes the previous tokens |
| **3** | **Probability Estimation** | The model calculates probabilities for possible next tokens |
| **4** | **Prediction** | The model selects or predicts the next token |
| **5** | **Continuation** | The predicted token becomes part of the next input context |

### Example

Given:

`I love machine`

the model might produce:

| Next Token | Example Probability |
| --- | ---: |
| **learning** | 0.70 |
| **vision** | 0.20 |
| **car** | 0.10 |

The model considers **learning** the most likely continuation in this simplified example.

---

# ⚖️ 4. Traditional NLP vs. LLMs

| Feature | Traditional NLP | Large Language Models | Reference |
| --- | --- | --- | --- |
| **Feature Design** | Often requires manually designed features | Learns useful representations automatically | [Bengio et al., 2003](https://www.jmlr.org/papers/v3/bengio03a.html) |
| **Context** | Context handling depends on the method and is often limited | Can model richer relationships between tokens | [Vaswani et al., 2017](https://arxiv.org/abs/1706.03762) |
| **Task Design** | Often built for one specific task | One model can support many different tasks | [Devlin et al., 2018](https://arxiv.org/abs/1810.04805) |
| **Few-Shot Learning** | Usually needs task-specific training | Can perform some tasks from instructions or a few examples | [Brown et al., 2020](https://arxiv.org/abs/2005.14165) |
| **Adaptation** | Often requires a new model or pipeline | Can be adapted using prompting or fine-tuning | [Brown et al., 2020](https://arxiv.org/abs/2005.14165) |
| **Generation** | Limited open-ended text generation | Can generate long and fluent text | [Brown et al., 2020](https://arxiv.org/abs/2005.14165) |

### Why LLMs?

LLMs are useful because they can:

- Learn language patterns automatically
- Understand context across multiple tokens
- Perform many tasks using the same model
- Work with zero-shot and few-shot examples
- Generate natural-language responses
- Be adapted to different domains and applications

---

# 🧩 5. Core Components of LLMs

| Component | Purpose | Result | Reference |
| --- | --- | --- | --- |
| **Tokenization** | Breaks text into smaller units that the model can process | Tokens / Token IDs | [Sennrich et al., 2016](https://arxiv.org/abs/1508.07909) |
| **Embedding** | Converts tokens into numerical vectors | Token representations | [Bengio et al., 2003](https://www.jmlr.org/papers/v3/bengio03a.html) |
| **Positional Information** | Adds information about token order or position | Position-aware representations | [Vaswani et al., 2017](https://arxiv.org/abs/1706.03762) |
| **Self-Attention** | Learns relationships between tokens in the same context | Contextual representations | [Vaswani et al., 2017](https://arxiv.org/abs/1706.03762) |
| **Transformer Blocks** | Repeatedly process and improve token representations | Deep contextual representations | [Vaswani et al., 2017](https://arxiv.org/abs/1706.03762) |
| **Output Layer** | Produces scores or probabilities for possible next tokens | Token probabilities | [Vaswani et al., 2017](https://arxiv.org/abs/1706.03762) |

## Tokenization

LLMs do not directly process raw text. A tokenizer converts text into smaller units called **tokens**.

| Original Text | Example Tokens |
| --- | --- |
| `Artificial intelligence is powerful` | `Artificial`, `intelligence`, `is`, `powerful` |

Actual tokenization depends on the tokenizer used by each model.

## Embedding

Each token is converted into a numerical vector that can be processed by a neural network.

| Token | Example Representation |
| --- | --- |
| `cat` | `[0.21, 0.53, 0.18, ...]` |
| `dog` | `[0.24, 0.49, 0.20, ...]` |

---

# 🏗️ 6. Transformer Architecture

The **Transformer** is a neural network architecture introduced by Vaswani et al. It uses Attention mechanisms instead of relying mainly on recurrent processing.

> **Reference:** [Vaswani et al., 2017](https://arxiv.org/abs/1706.03762)

## Why Transformer?

| RNN Limitation | Transformer Approach | Reference |
| --- | --- | --- |
| **Sequential Processing** | Allows more parallel computation during training | [Vaswani et al., 2017](https://arxiv.org/abs/1706.03762) |
| **Long Dependency Paths** | Attention connects different token positions directly | [Vaswani et al., 2017](https://arxiv.org/abs/1706.03762) |
| **Training Speed** | Parallel processing improves training efficiency | [Vaswani et al., 2017](https://arxiv.org/abs/1706.03762) |
| **Long-Range Relationships** | Attention can connect information across distant parts of a sequence | [Vaswani et al., 2017](https://arxiv.org/abs/1706.03762) |
| **Scalability** | Transformer models can be scaled to very large sizes | [Kaplan et al., 2020](https://arxiv.org/abs/2001.08361) |

## Transformer Components

| Component | Function | Reference |
| --- | --- | --- |
| **Token Embedding** | Converts tokens into numerical vectors | [Vaswani et al., 2017](https://arxiv.org/abs/1706.03762) |
| **Positional Encoding** | Adds information about token position | [Vaswani et al., 2017](https://arxiv.org/abs/1706.03762) |
| **Self-Attention** | Learns relationships between tokens | [Vaswani et al., 2017](https://arxiv.org/abs/1706.03762) |
| **Multi-Head Attention** | Learns different types of relationships at the same time | [Vaswani et al., 2017](https://arxiv.org/abs/1706.03762) |
| **Feed Forward Network** | Applies additional transformations to token representations | [Vaswani et al., 2017](https://arxiv.org/abs/1706.03762) |
| **Residual Connection** | Helps preserve information across layers | [Vaswani et al., 2017](https://arxiv.org/abs/1706.03762) |
| **Layer Normalization** | Helps stabilize model training | [Vaswani et al., 2017](https://arxiv.org/abs/1706.03762) |
| **Masked Attention** | Prevents the model from seeing future tokens during autoregressive generation | [Vaswani et al., 2017](https://arxiv.org/abs/1706.03762) |
| **Cross-Attention** | Lets the Decoder use information from the Encoder | [Vaswani et al., 2017](https://arxiv.org/abs/1706.03762) |

## Main Transformer Architectures

| Architecture | Structure | Typical Purpose | Example | Reference |
| --- | --- | --- | --- | --- |
| **Encoder-Only** | Transformer Encoder | Text understanding and representation | BERT | [Devlin et al., 2018](https://arxiv.org/abs/1810.04805) |
| **Decoder-Only** | Causal Transformer | Autoregressive text generation | GPT-3 | [Brown et al., 2020](https://arxiv.org/abs/2005.14165) |
| **Encoder–Decoder** | Encoder + Decoder | Sequence-to-sequence tasks | Original Transformer | [Vaswani et al., 2017](https://arxiv.org/abs/1706.03762) |

---

# 🎯 7. Self-Attention

**Self-Attention** allows each token to use information from other tokens in the same sequence when building its representation.

For example:

> `The animal didn't cross the street because it was tired.`

The model needs context to understand what **“it”** refers to.

> **Reference:** [Vaswani et al., 2017](https://arxiv.org/abs/1706.03762)

## Main Elements

| Element | Purpose | Reference |
| --- | --- | --- |
| **Query (Q)** | Represents what information the current token is looking for | [Vaswani et al., 2017](https://arxiv.org/abs/1706.03762) |
| **Key (K)** | Represents information that can be matched with a Query | [Vaswani et al., 2017](https://arxiv.org/abs/1706.03762) |
| **Value (V)** | Contains the information used to build the output | [Vaswani et al., 2017](https://arxiv.org/abs/1706.03762) |
| **Attention Score** | Measures how strongly one token should pay attention to another | [Vaswani et al., 2017](https://arxiv.org/abs/1706.03762) |
| **Attention Weight** | Normalized importance assigned to each token | [Vaswani et al., 2017](https://arxiv.org/abs/1706.03762) |

---

# 🏋️ 8. LLM Training

LLM development usually starts with **Pretraining** and may continue with **Fine-Tuning** to adapt the model for a specific task or domain.

## Pretraining

Pretraining teaches the model general language patterns using large-scale datasets.

| Step | Process | Description |
| ---: | --- | --- |
| **1** | **Data Preparation** | Collect and prepare large-scale training data |
| **2** | **Tokenization** | Convert text into token sequences |
| **3** | **Forward Pass** | Process tokens through the model |
| **4** | **Prediction** | Produce predictions based on the training objective |
| **5** | **Loss Calculation** | Measure prediction error |
| **6** | **Backpropagation** | Calculate gradients |
| **7** | **Optimization** | Update model parameters |

> **Reference:** [Brown et al., 2020](https://arxiv.org/abs/2005.14165)

The result of large-scale pretraining is commonly called a **Foundation Model**.

## Pretraining vs. Fine-Tuning

| Feature | Pretraining | Fine-Tuning | Reference |
| --- | --- | --- | --- |
| **Purpose** | Learn general language capabilities | Adapt the model to a specific task or domain | [Devlin et al., 2018](https://arxiv.org/abs/1810.04805) |
| **Data** | Large-scale general data | Task- or domain-specific data | [Devlin et al., 2018](https://arxiv.org/abs/1810.04805) |
| **Starting Point** | Base model | Pretrained model | [Devlin et al., 2018](https://arxiv.org/abs/1810.04805) |
| **Training Scale** | Usually very large | Usually smaller | [Devlin et al., 2018](https://arxiv.org/abs/1810.04805) |
| **Output** | Foundation Model | Adapted Model | [Devlin et al., 2018](https://arxiv.org/abs/1810.04805) |

## Fine-Tuning Methods

| Method | Purpose | Example | Reference |
| --- | --- | --- | --- |
| **Instruction Tuning** | Teaches the model to follow natural-language instructions | Instruction–response datasets | [Wei et al., 2021](https://arxiv.org/abs/2109.01652) |
| **Domain Tuning** | Adapts the model to a specific area of knowledge | Medical, legal, finance | [Gururangan et al., 2020](https://arxiv.org/abs/2004.10964) |
| **Task Tuning** | Adapts the model to a specific task | Classification, QA, summarization | [Devlin et al., 2018](https://arxiv.org/abs/1810.04805) |

---

# ⚙️ 9. LLM Inference

**Inference** is the process of using a trained LLM to generate an output from a prompt.

Autoregressive LLMs generate text one token at a time. Each generated token becomes part of the context used to predict the next token.

> **Reference:** [Brown et al., 2020](https://arxiv.org/abs/2005.14165)

## Inference Process

| Step | Stage | Description |
| ---: | --- | --- |
| **1** | **Prompt** | The user provides an instruction or input |
| **2** | **Tokenization** | The prompt is converted into token IDs |
| **3** | **Model Processing** | The model processes the current context |
| **4** | **Prediction** | The model produces probabilities for possible next tokens |
| **5** | **Token Selection** | A generation method selects the next token |
| **6** | **Context Update** | The selected token is added to the current context |
| **7** | **Decoding** | Generated tokens are converted back into readable text |

## Generation Settings

| Setting | Function | Reference |
| --- | --- | --- |
| **Temperature** | Controls how random or focused the token selection is | [Holtzman et al., 2019](https://arxiv.org/abs/1904.09751) |
| **Top-k** | Limits sampling to the k most likely tokens | [Fan et al., 2018](https://arxiv.org/abs/1805.04833) |
| **Top-p** | Samples from a group of tokens whose total probability reaches a selected threshold | [Holtzman et al., 2019](https://arxiv.org/abs/1904.09751) |
| **Max Tokens** | Sets the maximum number of tokens that can be generated | Implementation setting |
| **Repetition Penalty** | Helps reduce repeated words or phrases | Implementation setting |
| **Stop Sequences** | Stops generation when a specified sequence appears | Implementation setting |

### Example

**Prompt:** `Artificial Intelligence is ...`

| Candidate Token | Example Probability |
| --- | ---: |
| **a** | 0.42 |
| **the** | 0.25 |
| **changing** | 0.12 |
| **used** | 0.08 |
| **Others** | 0.13 |

The selected token is added to the context, and the model continues predicting the next token until generation stops.

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

| Challenge | Description | Why It Matters | Reference |
| --- | --- | --- | --- |
| **Hallucination** | The model may generate information that sounds correct but is actually wrong | Important information should be verified | [Ji et al., 2022](https://arxiv.org/abs/2202.03629) |
| **Bias** | The model may learn unwanted patterns or bias from training data | Can affect fairness and reliability | [Bender et al., 2021](https://doi.org/10.1145/3442188.3445922) |
| **Knowledge Freshness** | The model does not automatically know information that appeared after its training data | Responses may become outdated | [Lewis et al., 2020](https://arxiv.org/abs/2005.11401) |
| **Computational Cost** | Large models require significant computing resources | Increases training and deployment costs | [Kaplan et al., 2020](https://arxiv.org/abs/2001.08361) |
| **Memory Requirements** | Large models can require a large amount of memory | Makes deployment on smaller hardware difficult | [Dettmers et al., 2022](https://arxiv.org/abs/2208.07339) |
| **Privacy** | Models may memorize some information from training data | Sensitive data must be handled carefully | [Carlini et al., 2020](https://arxiv.org/abs/2012.07805) |
| **Security** | LLM applications may be affected by malicious prompts or prompt injection | Can affect system behavior and reliability | [Perez & Ribeiro, 2022](https://arxiv.org/abs/2211.09527) |
| **Explainability** | It can be difficult to fully explain why a model produces a particular answer | Makes model behavior harder to audit | [Bender et al., 2021](https://doi.org/10.1145/3442188.3445922) |
| **Energy Consumption** | Training and running large models requires substantial computing resources | Affects cost and sustainability | [Strubell et al., 2019](https://arxiv.org/abs/1906.02243) |

---

# ✅ 12. Summary

| Topic | Key Idea |
| --- | --- |
| **Language Model** | Estimates probabilities over words or tokens |
| **Tokenization** | Converts text into tokens |
| **Embedding** | Converts tokens into numerical vectors |
| **Transformer** | Core architecture behind many modern LLMs |
| **Self-Attention** | Learns relationships between tokens in context |
| **Pretraining** | Builds general language capabilities from large-scale data |
| **Fine-Tuning** | Adapts a pretrained model to specific tasks or domains |
| **Inference** | Uses a trained model to generate responses |
| **Applications** | Uses LLMs for chatbots, coding, education, research, and other tasks |
| **Limitations** | Includes hallucination, bias, cost, privacy, security, and explainability |

---

## 🚀 What's Next?

| Chapter | Topic | Main Focus |
| ---: | --- | --- |
| **1** | **LLM Foundations** | Transformer, training, and inference |
| **2** | **Prompt Engineering** | Designing effective prompts and instructions |
| **3** | **RAG** | Connecting LLMs with external knowledge |
| **4** | **Fine-Tuning** | Adapting models to specific tasks and domains |
| **5** | **AI Agents** | Reasoning, tools, and actions |
| **6** | **Multimodal AI** | Working with text, image, audio, and other data types |

---
