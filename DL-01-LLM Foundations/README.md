# DL-01-LLM Foundations
LLM-01: Foundations of Large Language Models (LLM)

📘 Course Description
Foundations and practical applications of Artificial Intelligence (AI) and Large Language Models (LLMs) — how language models evolved from traditional NLP, the Transformer architecture, tokenization, embeddings, Self-Attention, pretraining, fine-tuning, inference, real-world applications, and the limitations of modern LLMs.

## 📊 Assessment Methods

| Component | Points | Description |
| --- | ---: | --- |
| **Class Participation** | 10 | Attendance, activity engagement, and sharing opinions |
| **Hands-on Projects** | 30 | Practical work with LLMs and AI tools for programming tasks and mini-projects |
| **Midterm Exam** | 30 | Tests understanding of key concepts, including LLMs, AI techniques, and applications |
| **Final Exam** | 30 | Assesses overall learning outcomes and the ability to apply knowledge to solve problems |
| **Total** | **100** |  |

## 🛠️ Software / Tools

| Software / Tool | Description |
| --- | --- |
| **Python** | Versatile programming language with rich libraries for data science, AI, and machine learning |
| **TensorFlow** | Open-source platform for building and deploying machine learning and deep learning models |
| **PyTorch** | Flexible deep learning framework with strong support for AI research and model development |
| **Visual Studio Code** | Lightweight and powerful code editor with extensions and integrated development tools |
---

### 🕰️ NLP Timeline

| Era | Stage | Main Idea | Reference |
| --- | --- | --- | --- |
| **1950s–1970s** | **Rule-Based NLP** | The earliest era of NLP, using hand-written rules and linguistic expertise for language processing | [Turing, 1950](https://doi.org/10.1093/mind/LIX.236.433) |
| **1980s–1990s** | **Statistical NLP** | Uses statistical models and probability for analyzing and processing natural language | [Manning & Schütze, 1999](https://nlp.stanford.edu/fsnlp/) |
| **1990s–2000s** | **Machine Learning** | Machine learning methods are increasingly applied to NLP tasks and language processing | [Mitchell, 1997](https://www.cs.cmu.edu/~tom/mlbook.html) |
| **2000s** | **Word Embedding** | Words are represented as dense numerical vectors to capture meaning and semantic relationships | [Bengio et al., 2003](https://www.jmlr.org/papers/v3/bengio03a.html) |
| **2000s–2010s** | **RNN (Recurrent Neural Network)** | Sequential models process language while capturing dependencies between words over time | [Mikolov et al., 2010](https://www.fit.vut.cz/research/group/speech/public/publi/2010/mikolov_interspeech2010_IS100722.pdf) |
| **2010s** | **LSTM** | Improves the ability of recurrent networks to learn long-term dependencies | [Hochreiter & Schmidhuber, 1997](https://doi.org/10.1162/neco.1997.9.8.1735) |
| **2014** | **Attention Mechanism** | Allows a model to focus on relevant parts of an input sequence when generating an output | [Bahdanau et al., 2014](https://arxiv.org/abs/1409.0473) |
| **2017** | **Transformer Architecture** | Uses Self-Attention to model relationships between tokens and enables highly parallel sequence processing | [Vaswani et al., 2017](https://arxiv.org/abs/1706.03762) |
| **2018–Present** | **Large Language Models (LLMs)** | Large-scale pretrained Transformer-based language models become widely developed and applied | [Devlin et al., 2018](https://arxiv.org/abs/1810.04805) / [Brown et al., 2020](https://arxiv.org/abs/2005.14165) |

---

# 🧠 Large Language Model (LLM) Foundations

This chapter introduces the foundations of **Large Language Models (LLMs)**, including Language Models, Transformer architecture, model training, fine-tuning, inference, applications, and limitations.

---

## 🧠 What is a Large Language Model?

> A **Large Language Model (LLM)** is a type of AI model built on the Transformer architecture and trained on massive amounts of text data to understand and generate human-like language.

### LLM: How It Works

| Step | Stage | Description |
| ---: | --- | --- |
| **1** | **Training Data** | The model is trained on massive amounts of text from books, articles, websites, code, and other sources |
| **2** | **Training Process** | The model learns language patterns, grammar, facts, and reasoning through prediction tasks |
| **3** | **Understanding** | The model learns context and relationships between tokens |
| **4** | **Generation** | Given an instruction, the model predicts and generates a response that fits the context |

### LLM: Key Characteristics

| # | Characteristic | Description |
| ---: | --- | --- |
| **1** | **Large-Scale Data** | Trained on massive collections of text, code, documents, and other data |
| **2** | **Massive Parameters** | Contains large numbers of parameters that allow the model to learn complex language patterns |
| **3** | **Transformer Architecture** | Uses Self-Attention to understand context and token relationships |
| **4** | **Scaling Law** | Performance can improve as model size, training data, and compute increase |
| **5** | **Diverse Capabilities** | Supports Q&A, writing, reasoning, summarization, coding, and many other tasks |

### LLM: Example Models

| Model Family | Organization |
| --- | --- |
| **GPT** | OpenAI |
| **Llama** | Meta |
| **Gemini** | Google |
| **Mistral** | Mistral AI |
| **Claude** | Anthropic |
| **DeepSeek** | DeepSeek |

### LLM: Common Use Cases

| Application | Description |
| --- | --- |
| **Chatbot** | Natural-language conversation and question answering |
| **Programming** | Generating, explaining, fixing, and improving code |
| **Education** | Personalized tutoring, content creation, and learning support |
| **Healthcare** | Supporting information processing and clinical document summarization |
| **Translation** | Translating text while preserving meaning and context |
| **Document Analysis** | Extracting, summarizing, and analyzing information from documents |
| **Research Assistant** | Searching, summarizing, and compiling research information |
| **Robotics** | Understanding instructions, planning tasks, and interacting with an environment |

> **Key Takeaway:** LLMs combine large-scale data, massive parameters, Transformer architecture, and large-scale training to achieve powerful language understanding and generation.

---

## 🕰️ Historical Context

### Evolution of NLP Timeline

Natural Language Processing has evolved from manually defined linguistic rules to large-scale Transformer-based models.

| Era | Stage | Main Idea | Reference |
| --- | --- | --- | --- |
| **1950s–1970s** | **Rule-Based NLP** | Uses manually designed rules and linguistic knowledge for language processing | [Turing, 1950](https://doi.org/10.1093/mind/LIX.236.433) |
| **1980s–1990s** | **Statistical NLP** | Uses statistical and probabilistic approaches for language processing | [Manning & Schütze, 1999](https://nlp.stanford.edu/fsnlp/) |
| **1990s–2000s** | **Machine Learning** | Applies machine learning algorithms to NLP tasks | [Mitchell, 1997](https://www.cs.cmu.edu/~tom/mlbook.html) |
| **2000s** | **Neural Language Models** | Uses neural networks to learn distributed representations of language | [Bengio et al., 2003](https://www.jmlr.org/papers/v3/bengio03a.html) |
| **2000s–2010s** | **RNN** | Processes sequential information and learns dependencies over time | [Mikolov et al., 2010](https://www.fit.vut.cz/research/group/speech/public/publi/2010/mikolov_interspeech2010_IS100722.pdf) |
| **2010s** | **LSTM** | Improves the ability of recurrent networks to learn long-term dependencies | [Hochreiter & Schmidhuber, 1997](https://doi.org/10.1162/neco.1997.9.8.1735) |
| **2014** | **Attention Mechanism** | Allows models to focus on relevant parts of an input sequence | [Bahdanau et al., 2014](https://arxiv.org/abs/1409.0473) |
| **2017** | **Transformer Architecture** | Uses Self-Attention to model relationships between tokens | [Vaswani et al., 2017](https://arxiv.org/abs/1706.03762) |
| **2018–Present** | **Large Language Models** | Large-scale pretrained Transformer models enable general-purpose language capabilities | [Devlin et al., 2018](https://arxiv.org/abs/1810.04805) / [Brown et al., 2020](https://arxiv.org/abs/2005.14165) |

---

## ❓ What is a Language Model?

> A **Language Model (LM)** is a mathematical model that estimates the probability of a sequence of words: **P(w₁, w₂, ..., wₙ)**

The goal of a Language Model is to use the previous context to predict the word or token most likely to come next.

### LM: How It Works

| Step | Process | Description |
| ---: | --- | --- |
| **1** | **Input Sequence** | The model receives a sequence of words or tokens |
| **2** | **Context Processing** | The model analyzes the previous tokens and their relationships |
| **3** | **Probability Estimation** | Probabilities are calculated for possible next tokens |
| **4** | **Prediction** | The model selects or predicts the next token |
| **5** | **Continuation** | The predicted token becomes part of the context for further prediction |

### LM: Example

Given the input:

`I love machine`

the model may estimate:

| Possible Next Token | Example Probability |
| --- | ---: |
| **learning** | High |
| **vision** | Medium |
| **car** | Low |

> **Key Takeaway:** A Language Model learns patterns in language and uses the previous context to estimate what is likely to come next.

---

## ⚖️ Traditional NLP vs. Large Language Models

| Feature | Traditional NLP | Large Language Models |
| --- | --- | --- |
| **Feature Design** | Requires manually designed features and domain expertise | Learns representations automatically |
| **Vocabulary** | Often limited and affected by Out-of-Vocabulary (OOV) words | Handles broad vocabularies through tokenization |
| **Context Understanding** | Often limited in capturing complex or long-range context | Provides stronger contextual modeling |
| **Generalization** | Often requires task-specific systems | Can perform multiple tasks from instructions and examples |
| **Output** | Rule-based or statistical output | Natural and fluent language generation |

### Why LLMs?

**Advantages**

- Understand complex context
- Generate natural and fluent language
- Support many tasks with the same model
- Perform zero-shot and few-shot tasks
- Benefit from scaling data, model size, and compute

**Limitations**

- May generate hallucinations
- May reflect bias in training data
- Internal knowledge may become outdated
- Require significant computational resources
- Raise privacy and security concerns
- Can be difficult to explain

---

## 🧩 Core Components of an LLM System

An LLM system contains several important components, from text processing to final response generation.

| Step | Component | Input / Learns | Output |
| ---: | --- | --- | --- |
| **01** | **Tokenization** | Raw text | Sequence of tokens |
| **02** | **Embedding** | Tokens | Dense numerical vectors |
| **03** | **Self-Attention** | Token relationships in context | Contextualized representations |
| **04** | **Pretraining** | Large-scale training data | Foundation Model |
| **05** | **Fine-Tuning** | Task/domain-specific data | Adapted Model |
| **06** | **Inference** | User prompt | Generated text |

### How the Components Work Together

1. **Tokenization** converts raw text into tokens.
2. **Embedding** converts tokens into numerical representations.
3. **Self-Attention** learns relationships between tokens in context.
4. **Pretraining** builds general language capabilities.
5. **Fine-Tuning** adapts the model to specific tasks or domains.
6. **Inference** uses the trained model to generate responses.

> **Key Takeaway:** LLM systems transform text into numerical representations, learn contextual relationships, build general capabilities through pretraining, and generate responses during inference.

---

# 1️⃣ Transformer Architecture

> The **Transformer** uses an Encoder–Decoder structure with Attention mechanisms to process sequences. — **[Vaswani et al., 2017](https://arxiv.org/abs/1706.03762)**

## Transformer: Processing a Sequence

| Step | Component | Function |
| ---: | --- | --- |
| **1** | **Input** | Receives the input text or sequence |
| **2** | **Tokenization** | Converts the input text into tokens |
| **3** | **Token Embedding** | Converts tokens into numerical vector representations |
| **4** | **Positional Encoding** | Adds information about the position of each token |
| **5** | **Encoder** | Extracts contextual information from the input |
| **6** | **Decoder** | Generates the output using Encoder information and previously generated tokens |
| **7** | **Output** | Produces the final output sequence |

---

## Transformer: The Problem It Solves

RNNs process sequence elements one step at a time. This creates several challenges when processing long sequences.

| RNN Limitation | Transformer Approach |
| --- | --- |
| **Sequential Processing** | Self-Attention allows token representations to be computed in parallel during training |
| **Slow Training** | Parallel computation improves training efficiency |
| **Long-Range Dependencies** | Attention directly connects information across different positions |
| **Gradient Problems** | Avoids long recurrent computational paths |
| **Limited Scalability** | Transformer architectures scale effectively to large models and datasets |

### Transformer: Goals

1. **Process in parallel** — process token representations efficiently using Self-Attention
2. **Understand context holistically** — learn relationships among tokens
3. **Capture long-range dependencies** — connect information across distant positions
4. **Improve training efficiency** — reduce dependence on recurrent computation
5. **Enable large-scale models** — support training with massive datasets and model sizes

---

## Transformer: Key Components

| Component | Function |
| --- | --- |
| **Token Embedding** | Converts tokens into dense numerical vectors |
| **Positional Encoding** | Adds information about token order and position |
| **Multi-Head Self-Attention** | Allows the model to learn different relationships between tokens |
| **Masked Multi-Head Self-Attention** | Prevents the decoder from attending to future tokens |
| **Multi-Head Cross-Attention** | Allows the decoder to use information from the Encoder |
| **Feed Forward Network** | Applies nonlinear transformations to token representations |
| **Add & Norm** | Uses residual connections and normalization to support stable training |

### Transformer: Main Architectures

| Architecture | Main Structure | Example |
| --- | --- | --- |
| **Encoder-Only** | Uses the Transformer Encoder | BERT |
| **Decoder-Only** | Uses causal Transformer blocks for autoregressive generation | GPT-style models |
| **Encoder–Decoder** | Uses both Encoder and Decoder | Original Transformer, T5 |

### Transformer: Summary

- Uses **Self-Attention** to learn relationships between tokens
- Supports parallel computation during training
- Captures long-range contextual relationships
- Reduces dependence on sequential recurrent processing
- Forms the foundation of many modern language models

---

# 2️⃣ LLM Training Pipeline

> **LLM Training** uses large-scale data to build a general-purpose Foundation Model and can then adapt that model to specific tasks or domains through Fine-Tuning.

## Training: From Data to Adapted Model

| Step | Stage | Description | Result |
| ---: | --- | --- | --- |
| **1** | **Training Data** | Collect large-scale text, code, documents, and other training data | Training corpus |
| **2** | **Pretraining** | Train the model to learn general language patterns and knowledge | Learned parameters |
| **3** | **Foundation Model** | General-purpose model obtained after pretraining | Base model |
| **4** | **Fine-Tuning** | Adapt the model using task-, domain-, or instruction-specific data | Specialized capabilities |
| **5** | **Adapted Model** | Model optimized for a particular application | Application-ready model |

---

## Training: Pretraining Process

| Step | Process | Description |
| ---: | --- | --- |
| **1** | **Training Data** | Collect large-scale training data |
| **2** | **Tokenization** | Convert training text into token sequences |
| **3** | **Model Processing** | Process token sequences through the Transformer |
| **4** | **Prediction** | Produce predictions according to the training objective |
| **5** | **Loss Calculation** | Measure the difference between predictions and targets |
| **6** | **Backpropagation** | Calculate gradients through the neural network |
| **7** | **Parameter Update** | Update model parameters using an optimizer |
| **8** | **Repeat** | Repeat training across the dataset |

### Training: Goals

1. **Learn general language knowledge** — learn grammar, patterns, semantics, and contextual relationships
2. **Predict tokens accurately** — improve performance on the training objective
3. **Build general capabilities** — create a reusable Foundation Model
4. **Adapt to specific tasks** — specialize the model for target applications
5. **Improve instruction following** — align responses with intended tasks and instructions

---

## Pretraining vs. Fine-Tuning

| Feature | Pretraining | Fine-Tuning |
| --- | --- | --- |
| **Purpose** | Learn general language capabilities | Adapt the model to a particular task or domain |
| **Data** | Large-scale general training data | Task-, domain-, or instruction-specific data |
| **Starting Point** | Base neural network | Pretrained Foundation Model |
| **Training Scale** | Very large | Usually smaller than pretraining |
| **Output** | Foundation Model | Adapted Model |
| **Example Goal** | Next-token prediction | Instruction following or domain specialization |

---

## Training: Popular Fine-Tuning Methods

| Method | Purpose | Example |
| --- | --- | --- |
| **Instruction Tuning** | Teaches the model to follow instructions and generate appropriate responses | Instruction → Response |
| **Domain Tuning** | Specializes the model in a particular domain | Medical, legal, financial |
| **Task Tuning** | Adapts the model to a specific task objective | Classification, summarization |

### Training: Real-World Applications

| Domain | Example Applications |
| --- | --- |
| **Healthcare** | Medical Q&A, clinical document summarization |
| **Legal** | Contract analysis, document processing |
| **Finance** | Financial reporting, market and risk analysis |

### Training: Summary

- **Pretraining** builds general language capabilities
- The result of pretraining is a **Foundation Model**
- **Fine-Tuning** adapts the Foundation Model
- Fine-tuning can focus on instructions, domains, or tasks
- The result is an **Adapted Model**

> **Key Takeaway:** Pretraining builds general capabilities, while Fine-Tuning adapts those capabilities to a specific purpose.

---

# 3️⃣ Inference Pipeline

> **Inference** is the process of using a trained LLM to generate output from a user prompt.

## Inference: From Prompt to Generated Text

| Step | Stage | Description |
| ---: | --- | --- |
| **1** | **Prompt** | The user provides an instruction or input text |
| **2** | **Tokenizer** | Converts the prompt into tokens and token IDs |
| **3** | **LLM Processing** | Processes the current context and predicts probabilities for the next token |
| **4** | **Sampling** | Selects a token according to the generation strategy |
| **5** | **Context Update** | Adds the selected token to the current context |
| **6** | **Generation** | Repeats prediction and token selection |
| **7** | **Decoding** | Converts generated tokens into readable text |

---

## Inference: Token-by-Token Generation

LLMs commonly generate text **autoregressively**, meaning that each generated token becomes part of the context for predicting the next token.

| Generation Step | Current Context | Model Action |
| ---: | --- | --- |
| **1** | Original prompt | Predict the first new token |
| **2** | Prompt + Token 1 | Predict Token 2 |
| **3** | Prompt + Tokens 1–2 | Predict Token 3 |
| **4** | Prompt + Tokens 1–3 | Predict Token 4 |
| **...** | Updated context | Continue until a stopping condition |

### Inference: Goals

1. **Understand the prompt** — correctly process the user's input
2. **Predict the next token** — compute probabilities over possible tokens
3. **Select tokens appropriately** — use a suitable generation strategy
4. **Maintain context** — use previously generated tokens as part of the current context
5. **Generate coherent text** — produce fluent and contextually consistent output
6. **Stop appropriately** — terminate generation when a stopping condition is reached

---

## Inference: Popular Sampling Settings

| Setting | Function |
| --- | --- |
| **Temperature** | Controls randomness or creativity in token selection |
| **Top-k** | Limits token selection to the k most probable candidates |
| **Top-p** | Selects from the smallest token set whose cumulative probability reaches a threshold |
| **Max Tokens** | Limits the maximum number of generated tokens |
| **Repetition Penalty** | Discourages excessive repetition |
| **Stop Sequences** | Defines sequences that terminate generation |

### Inference: Example

**Prompt**

> Artificial Intelligence is ...

**Possible Next Tokens**

| Token | Probability |
| --- | ---: |
| **a** | 0.42 |
| **the** | 0.25 |
| **changing** | 0.12 |
| **used** | 0.08 |
| **Others** | 0.13 |

The generation strategy selects one of the candidate tokens. The selected token is then added to the context before the model predicts the next token.

### Inference: Summary

- Receives a **Prompt**
- Converts the prompt into **Tokens**
- Predicts probabilities for the **Next Token**
- Uses a sampling strategy to select a token
- Adds each generated token back into the context
- Continues until a stopping condition is reached
- Decodes the generated tokens into readable text

---

# 📊 Transformer, Pretraining, Fine-Tuning & Inference

| Feature | Transformer Architecture | Pretraining | Fine-Tuning | Inference |
| --- | --- | --- | --- | --- |
| **Input** | Tokens + positional information | Large-scale training data | Task/domain-specific data | User prompt |
| **Core Mechanism** | Self-Attention | Training objective | Task/domain/instruction adaptation | Prediction and token selection |
| **Main Goal** | Build contextual representations | Learn general capabilities | Adapt to a specific purpose | Generate a response |
| **Model Parameters** | Defines the network architecture | Parameters are learned extensively | Parameters are adapted | Parameters are used for prediction |
| **Output** | Contextual representations | Foundation Model | Adapted Model | Generated text |
| **Example** | BERT / GPT-style Transformer | Base language model | Instruction-tuned model | Chatbot response |

---

# 🌍 Applications of LLMs by Example

| Example | Application | Input | Output |
| --- | --- | --- | --- |
| **Customer Support Chatbot** | Chatbot | User question | Conversational answer |
| **Code Generation Assistant** | Programming | Natural-language request | Generated or corrected code |
| **Personalized Tutor** | Education | Student question or topic | Explanation or learning content |
| **Clinical Document Summarizer** | Healthcare | Medical records | Document summary |
| **English–Thai Translator** | Translation | Source-language text | Translated text |
| **PDF Report Analyzer** | Document Analysis | Report or document | Extracted insights or summary |
| **Literature Review Assistant** | Research Assistant | Research topic | Compiled and summarized findings |
| **Instruction-Following Robot** | Robotics | Spoken or text instruction | Planned action sequence |

---

# ⚠️ Limitations of LLMs

## Major Challenges

| Challenge | Description | Why It Matters |
| --- | --- | --- |
| **Hallucination** | May generate incorrect or unsupported information | Outputs cannot always be treated as factual |
| **Bias** | May reproduce biases present in training data | Can affect fairness and reliability |
| **Knowledge Freshness** | Internal model knowledge may not contain recent information | Answers may become outdated |
| **Computational Cost** | Large models require substantial compute | Increases training and deployment costs |
| **Memory Requirements** | Large models require significant memory | Makes deployment on limited hardware difficult |
| **Privacy** | Sensitive information requires careful handling | Important for private and confidential data |
| **Security** | LLM applications can face attacks such as prompt injection | Can affect system reliability and safety |
| **Explainability** | Model behavior can be difficult to fully interpret | Makes decisions harder to audit |
| **Energy Consumption** | Training and inference require energy | Important for cost and sustainability |

---

## LLM Challenges

1. How can we build **smaller, faster, and more efficient LLMs** without losing quality?
2. How can we make LLMs **more accurate and reliable**?
3. How can we improve **reasoning capabilities**?
4. How can we reduce **hallucinations and bias**?
5. How can we ensure LLM systems are **private, secure, and responsible**?
6. What new applications can we build using LLM technologies?

---

# ✅ Summary

## Conclusion

In this chapter:

- We learned what **Large Language Models** are and how they work
- We explored the evolution of **NLP to modern LLMs**
- We learned the role of **Transformer and Self-Attention**
- We studied **Pretraining and Fine-Tuning**
- We explored the **Inference Pipeline**
- We examined real-world **LLM applications**
- We discussed important **limitations and challenges**

## Key Takeaways

| Topic | Input | Main Process | Result |
| --- | --- | --- | --- |
| **Transformer** | Tokens | Self-Attention | Contextual representations |
| **Pretraining** | Large-scale data | Model training | Foundation Model |
| **Fine-Tuning** | Task/domain data | Model adaptation | Adapted Model |
| **Inference** | User prompt | Token prediction and generation | Generated response |

---

## 🚀 What's Next?

| Chapter | Topic | Main Focus |
| ---: | --- | --- |
| **1** | **LLM Foundations** | Transformer, training, and inference |
| **2** | **Prompt Engineering** | Designing effective LLM instructions |
| **3** | **RAG** | Connecting LLMs with external knowledge |
| **4** | **Fine-Tuning** | Adapting models to specific tasks and domains |
| **5** | **AI Agents** | LLM-based reasoning, tools, and actions |
| **6** | **Multimodal AI** | Combining text, image, audio, and other modalities |

---

👤 Instructor
Anuruk Prommakhot (P'Ball), Ph.D.
📧 anuruk.p@en.rmutt.ac.th
🏢 Signal Processing Research Laboratory (SPRL), Rajamangala University of Technology Thanyaburi (RMUTT)
🔬 Research Areas: Optimization Algorithms, Machine Learning, AI Vision, RAG Systems, Agentic AI

