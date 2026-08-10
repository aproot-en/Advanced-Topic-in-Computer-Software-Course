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
| **Visual Studio Code** | A lightweight code editor with extensions and integrated development tools |

---

# 🧠 1. Introduction to Large Language Models

## What is a Large Language Model?

A **Large Language Model (LLM)** is basically a neural network trained on huge amounts of text so it can pick up patterns in language, understand how words relate to each other, and make sense of context.

Most LLMs today are built on the **Transformer architecture**, which lets them handle language efficiently and take on all kinds of tasks — answering questions, writing text, summarizing documents, translating, or even helping with code.

### Key Characteristics

| Characteristic | Description | Reference |
| --- | --- | --- |
| **Trained on Massive Data** | Learns from huge collections of text, code, documents, and more | [Brown et al., 2020](https://arxiv.org/abs/2005.14165) |
| **Huge Number of Parameters** | Has millions to billions of trainable parameters, which is how it captures complex language patterns | [Brown et al., 2020](https://arxiv.org/abs/2005.14165) |
| **Built on the Transformer** | Uses Attention to figure out how tokens relate to each other | [Vaswani et al., 2017](https://arxiv.org/abs/1706.03762) |
| **Handles Many Tasks** | One model can be used for a wide range of language tasks | [Brown et al., 2020](https://arxiv.org/abs/2005.14165) |
| **Scales Well** | Gets better as you throw more data, bigger models, and more compute at it | [Kaplan et al., 2020](https://arxiv.org/abs/2001.08361) |

---

# 🕰️ 2. Evolution of NLP

NLP has come a long way — from hand-written language rules to massive neural models that can understand and write text on their own.

| Era | Stage | Main Idea | Reference |
| --- | --- | --- | --- |
| **1950s–1970s** | **Rule-Based NLP** | Language was processed using hand-crafted rules built from linguistic knowledge | [Chomsky, 1957](https://doi.org/10.1515/9783112316009) |
| **1980s–1990s** | **Statistical NLP** | Language analysis shifted toward probability and statistics | [Manning & Schütze, 1999](https://nlp.stanford.edu/fsnlp/) |
| **1990s–2000s** | **Machine Learning** | ML methods started getting applied to NLP tasks | [Mitchell, 1997](https://www.cs.cmu.edu/~tom/mlbook.html) |
| **2000s** | **Neural Language Models** | Neural networks were used to learn language representations directly | [Bengio et al., 2003](https://www.jmlr.org/papers/v3/bengio03a.html) |
| **2000s–2010s** | **RNN** | Models started processing sequences and learning relationships across time | [Mikolov et al., 2010](https://www.fit.vut.cz/research/group/speech/public/publi/2010/mikolov_interspeech2010_IS100722.pdf) |
| **2010s** | **LSTM** | Recurrent networks got better at remembering information over longer stretches of text | [Hochreiter & Schmidhuber, 1997](https://doi.org/10.1162/neco.1997.9.8.1735) |
| **2014** | **Attention Mechanism** | Models learned to focus on the most relevant parts of the input | [Bahdanau et al., 2014](https://arxiv.org/abs/1409.0473) |
| **2017** | **Transformer** | Self-Attention took over as the way to model relationships between tokens | [Vaswani et al., 2017](https://arxiv.org/abs/1706.03762) |
| **2018–Present** | **Large Language Models** | Big pretrained Transformer models became the go-to tool for almost any language task | [Devlin et al., 2018](https://arxiv.org/abs/1810.04805) / [Brown et al., 2020](https://arxiv.org/abs/2005.14165) |

---

# 📖 3. Language Models

## What is a Language Model?

A **Language Model (LM)** is a model that estimates how likely a sequence of words or tokens is to occur:

**P(w₁, w₂, ..., wₙ)**

One of the most common jobs of a language model is predicting what token comes next, based on everything that came before it.

> **Reference:** [Bengio et al., 2003](https://www.jmlr.org/papers/v3/bengio03a.html)

### How It Works

| Step | Process | Description |
| ---: | --- | --- |
| **1** | **Input Sequence** | The model takes in a sequence of words or tokens |
| **2** | **Context Processing** | It looks at everything that came before |
| **3** | **Probability Estimation** | It works out how likely each possible next token is |
| **4** | **Prediction** | It picks (or predicts) the next token |
| **5** | **Continuation** | That predicted token gets added back into the context for the next round |

### Example

Given:

`I love machine`

the model might come up with:

| Next Token | Example Probability |
| --- | ---: |
| **learning** | 0.70 |
| **vision** | 0.20 |
| **car** | 0.10 |

In this simplified example, **learning** is the model's best guess.

---

# ⚖️ 4. NLP vs. LLMs

| Feature | Traditional NLP | Large Language Models | Reference |
| --- | --- | --- | --- |
| **Feature Design** | Usually needed features designed by hand | Learns useful representations on its own | [Bengio et al., 2003](https://www.jmlr.org/papers/v3/bengio03a.html) |
| **Context** | Context handling was limited and depended on the method | Can model much richer relationships between tokens | [Vaswani et al., 2017](https://arxiv.org/abs/1706.03762) |
| **Task Design** | Usually built for one specific job | A single model can handle many different tasks | [Devlin et al., 2018](https://arxiv.org/abs/1810.04805) |
| **Few-Shot Learning** | Usually needed task-specific training | Can pick up tasks from just instructions or a few examples | [Brown et al., 2020](https://arxiv.org/abs/2005.14165) |
| **Adaptation** | Often needed a whole new model or pipeline | Can be adapted just by prompting or fine-tuning | [Brown et al., 2020](https://arxiv.org/abs/2005.14165) |
| **Generation** | Open-ended text generation was pretty limited | Can generate long, fluent, natural-sounding text | [Brown et al., 2020](https://arxiv.org/abs/2005.14165) |

### Why LLMs?

LLMs are useful because they can:

- Pick up language patterns on their own, without hand-coded rules
- Understand context that spans many tokens
- Handle a wide range of tasks using the same model
- Work reasonably well with zero examples or just a handful of them
- Write natural, human-sounding responses
- Be adapted to different domains and use cases

---

# 🧩 5. Core Components of LLMs

| Component | Purpose | Result | Reference |
| --- | --- | --- | --- |
| **Tokenization** | Breaks text down into smaller pieces the model can actually work with | Tokens / Token IDs | [Sennrich et al., 2016](https://arxiv.org/abs/1508.07909) |
| **Embedding** | Turns tokens into numerical vectors | Token representations | [Bengio et al., 2003](https://www.jmlr.org/papers/v3/bengio03a.html) |
| **Positional Information** | Adds info about where each token sits in the sequence | Position-aware representations | [Vaswani et al., 2017](https://arxiv.org/abs/1706.03762) |
| **Self-Attention** | Learns how tokens in the same context relate to one another | Contextual representations | [Vaswani et al., 2017](https://arxiv.org/abs/1706.03762) |
| **Transformer Blocks** | Repeatedly refine and build up token representations | Deep contextual representations | [Vaswani et al., 2017](https://arxiv.org/abs/1706.03762) |
| **Output Layer** | Turns everything into scores/probabilities for the next possible tokens | Token probabilities | [Vaswani et al., 2017](https://arxiv.org/abs/1706.03762) |

## Tokenization

LLMs can't work with raw text directly. A tokenizer breaks text down into smaller pieces called **tokens**.

| Original Text | Example Tokens |
| --- | --- |
| `Artificial intelligence is powerful` | `Artificial`, `intelligence`, `is`, `powerful` |

How exactly text gets split up depends on the tokenizer each model uses.

## Embedding

Every token gets turned into a numerical vector so a neural network can actually work with it.

| Token | Example Representation |
| --- | --- |
| `cat` | `[0.21, 0.53, 0.18, ...]` |
| `dog` | `[0.24, 0.49, 0.20, ...]` |

---

# 🏗️ 6. Transformer Architecture

The **Transformer** is the neural network architecture introduced by Vaswani et al. Instead of leaning mainly on recurrent processing like older models, it uses Attention.

> **Reference:** [Vaswani et al., 2017](https://arxiv.org/abs/1706.03762)

## Why Transformer?

| RNN Limitation | Transformer's Fix | Reference |
| --- | --- | --- |
| **Sequential Processing** | Lets much more of the training run in parallel | [Vaswani et al., 2017](https://arxiv.org/abs/1706.03762) |
| **Long Dependency Paths** | Attention connects any two token positions directly | [Vaswani et al., 2017](https://arxiv.org/abs/1706.03762) |
| **Training Speed** | Parallel processing makes training a lot faster | [Vaswani et al., 2017](https://arxiv.org/abs/1706.03762) |
| **Long-Range Relationships** | Attention can link up information from far apart in a sequence | [Vaswani et al., 2017](https://arxiv.org/abs/1706.03762) |
| **Scalability** | Transformer models scale up to huge sizes surprisingly well | [Kaplan et al., 2020](https://arxiv.org/abs/2001.08361) |

## Transformer Components

| Component | Function | Reference |
| --- | --- | --- |
| **Token Embedding** | Turns tokens into numerical vectors | [Vaswani et al., 2017](https://arxiv.org/abs/1706.03762) |
| **Positional Encoding** | Adds info about where a token sits in the sequence | [Vaswani et al., 2017](https://arxiv.org/abs/1706.03762) |
| **Self-Attention** | Learns how tokens relate to each other | [Vaswani et al., 2017](https://arxiv.org/abs/1706.03762) |
| **Multi-Head Attention** | Picks up several different kinds of relationships at once | [Vaswani et al., 2017](https://arxiv.org/abs/1706.03762) |
| **Feed Forward Network** | Applies extra processing to each token's representation | [Vaswani et al., 2017](https://arxiv.org/abs/1706.03762) |
| **Residual Connection** | Helps information survive as it passes through many layers | [Vaswani et al., 2017](https://arxiv.org/abs/1706.03762) |
| **Layer Normalization** | Helps keep training stable | [Vaswani et al., 2017](https://arxiv.org/abs/1706.03762) |
| **Masked Attention** | Stops the model from peeking at future tokens while generating | [Vaswani et al., 2017](https://arxiv.org/abs/1706.03762) |
| **Cross-Attention** | Lets the Decoder pull in information from the Encoder | [Vaswani et al., 2017](https://arxiv.org/abs/1706.03762) |

## Main Transformer Architectures

| Architecture | Structure | Typical Purpose | Example | Reference |
| --- | --- | --- | --- | --- |
| **Encoder-Only** | Transformer Encoder | Understanding and representing text | BERT | [Devlin et al., 2018](https://arxiv.org/abs/1810.04805) |
| **Decoder-Only** | Causal Transformer | Generating text one token at a time | GPT-3 | [Brown et al., 2020](https://arxiv.org/abs/2005.14165) |
| **Encoder–Decoder** | Encoder + Decoder | Sequence-to-sequence tasks like translation | Transformer | [Vaswani et al., 2017](https://arxiv.org/abs/1706.03762) |

---

# 🎯 7. Self-Attention

**Self-Attention** lets each token pull in information from every other token in the sequence while building its own representation.

For example:

> `The animal didn't cross the street because it was tired.`

To figure out what **"it"** refers to, the model needs the surrounding context.

> **Reference:** [Vaswani et al., 2017](https://arxiv.org/abs/1706.03762)

## Main Elements

| Element | Purpose | Reference |
| --- | --- | --- |
| **Query (Q)** | What the current token is "asking for" | [Vaswani et al., 2017](https://arxiv.org/abs/1706.03762) |
| **Key (K)** | What each token has to "offer" when matched against a Query | [Vaswani et al., 2017](https://arxiv.org/abs/1706.03762) |
| **Value (V)** | The actual information used to build the output | [Vaswani et al., 2017](https://arxiv.org/abs/1706.03762) |
| **Attention Score** | How much one token should pay attention to another | [Vaswani et al., 2017](https://arxiv.org/abs/1706.03762) |
| **Attention Weight** | The normalized version of that score — how much weight each token actually gets | [Vaswani et al., 2017](https://arxiv.org/abs/1706.03762) |

---

# 🏋️ 8. LLM Training

Building an LLM usually starts with **Pretraining**, and often continues with **Fine-Tuning** to adapt it for a specific task or domain.

## Pretraining

Pretraining teaches the model general language skills using massive datasets.

| Step | Process | Description |
| ---: | --- | --- |
| **1** | **Data Preparation** | Gather and clean up large-scale training data |
| **2** | **Tokenization** | Turn the text into sequences of tokens |
| **3** | **Forward Pass** | Run the tokens through the model |
| **4** | **Prediction** | Get predictions based on the training objective |
| **5** | **Loss Calculation** | Measure how wrong those predictions were |
| **6** | **Backpropagation** | Work out how to adjust the model |
| **7** | **Optimization** | Update the model's parameters |

> **Reference:** [Brown et al., 2020](https://arxiv.org/abs/2005.14165)

The result of all this large-scale pretraining is usually called a **Foundation Model**.

## Pre-training vs. Fine-Tuning

| Feature | Pretraining | Fine-Tuning | Reference |
| --- | --- | --- | --- |
| **Purpose** | Build up general language ability | Adapt the model to a specific task or domain | [Devlin et al., 2018](https://arxiv.org/abs/1810.04805) |
| **Data** | Huge, general-purpose data | Data specific to a task or domain | [Devlin et al., 2018](https://arxiv.org/abs/1810.04805) |
| **Starting Point** | Base model | Already-pretrained model | [Devlin et al., 2018](https://arxiv.org/abs/1810.04805) |
| **Training Scale** | Usually massive | Usually much smaller | [Devlin et al., 2018](https://arxiv.org/abs/1810.04805) |
| **Output** | Foundation Model | Adapted Model | [Devlin et al., 2018](https://arxiv.org/abs/1810.04805) |

## Fine-Tuning Methods

| Method | Purpose | Example | Reference |
| --- | --- | --- | --- |
| **Instruction Tuning** | Teaches the model to actually follow instructions written in plain language | Instruction–response datasets | [Wei et al., 2021](https://arxiv.org/abs/2109.01652) |
| **Domain Tuning** | Makes the model more knowledgeable in a specific field | Medical, legal, finance | [Gururangan et al., 2020](https://arxiv.org/abs/2004.10964) |
| **Task Tuning** | Adapts the model to do one specific job well | Classification, QA, summarization | [Devlin et al., 2018](https://arxiv.org/abs/1810.04805) |

---

# ⚙️ 9. LLM Inference

**Inference** is just using a trained LLM to turn a prompt into an actual output.

Most LLMs generate text one token at a time — each new token gets added to the context and used to predict the next one.

> **Reference:** [Brown et al., 2020](https://arxiv.org/abs/2005.14165)

## Inference Process

| Step | Stage | Description |
| ---: | --- | --- |
| **1** | **Prompt** | The user types in an instruction or some input |
| **2** | **Tokenization** | The prompt gets converted into token IDs |
| **3** | **Model Processing** | The model processes the current context |
| **4** | **Prediction** | It works out probabilities for what could come next |
| **5** | **Token Selection** | A sampling method picks the next token |
| **6** | **Context Update** | That token gets added to the running context |
| **7** | **Decoding** | The generated tokens get turned back into readable text |

## Generation Settings

| Setting | Function | Reference |
| --- | --- | --- |
| **Temperature** | Controls how random vs. focused the token choices are | --------------- |
| **Top-k** | Only samples from the k most likely tokens | [Fan et al., 2018](https://arxiv.org/abs/1805.04833) |
| **Top-p** | Samples from the smallest group of tokens whose combined probability hits a set threshold | [Holtzman et al., 2019](https://arxiv.org/abs/1904.09751) |
| **Max Tokens** | Caps how many tokens can be generated | --------------- |
| **Repetition Penalty** | Discourages the model from repeating itself | --------------- |
| **Stop Sequences** | Stops generation as soon as a chosen sequence shows up | --------------- |

### Example

**Prompt:** `Artificial Intelligence is ...`

| Candidate Token | Example Probability |
| --- | ---: |
| **a** | 0.42 |
| **the** | 0.25 |
| **changing** | 0.12 |
| **used** | 0.08 |
| **Others** | 0.13 |

Whichever token gets picked is added to the context, and the model keeps predicting the next one until generation stops.

---

# 🌍 10. Applications

| Application | Example | Input | Output |
| --- | --- | --- | --- |
| **Chatbot** | Customer Support | User question | Conversational answer |
| **Programming** | Code Assistant | Programming request | Generated or fixed code |
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
| **Hallucination** | The model can produce answers that sound convincing but are actually wrong | Important info should always be double-checked | [Ji et al., 2022](https://arxiv.org/abs/2202.03629) |
| **Bias** | The model can pick up unwanted patterns or bias baked into its training data | Affects fairness and how much you can trust the output | [Bender et al., 2021](https://doi.org/10.1145/3442188.3445922) |
| **Knowledge Freshness** | The model has no idea about anything that happened after its training data was collected | Answers can end up outdated | [Lewis et al., 2020](https://arxiv.org/abs/2005.11401) |
| **Computational Cost** | Big models need a lot of computing power | Drives up training and deployment costs | [Kaplan et al., 2020](https://arxiv.org/abs/2001.08361) |
| **Memory Requirements** | Big models can eat up a huge amount of memory | Makes it hard to run on smaller hardware | [Dettmers et al., 2022](https://arxiv.org/abs/2208.07339) |
| **Privacy** | Models can sometimes memorize bits of their training data | Sensitive data needs to be handled carefully | [Carlini et al., 2020](https://arxiv.org/abs/2012.07805) |
| **Security** | LLM apps can be tricked by malicious prompts or prompt injection | Can mess with how the system behaves | [Perez & Ribeiro, 2022](https://arxiv.org/abs/2211.09527) |
| **Explainability** | It's often hard to fully explain why a model gave a particular answer | Makes the model's behavior harder to audit or trust | [Lipton, 2016](https://arxiv.org/abs/1606.03490) |
| **Energy Consumption** | Training and running big models takes a lot of compute | Affects cost and environmental impact | [Strubell et al., 2019](https://arxiv.org/abs/1906.02243) |

---

# ✅ 12. Summary

| Topic | Key Idea |
| --- | --- |
| **Language Model** | Estimates the probability of a sequence of words or tokens |
| **Tokenization** | Breaks text down into tokens |
| **Embedding** | Turns tokens into numerical vectors |
| **Transformer** | The core architecture behind most modern LLMs |
| **Self-Attention** | Learns how tokens relate to each other in context |
| **Pretraining** | Builds general language ability from massive amounts of data |
| **Fine-Tuning** | Adapts a pretrained model to a specific task or domain |
| **Inference** | Uses a trained model to actually generate a response |
| **Applications** | Chatbots, coding help, education, research, and more |
| **Limitations** | Hallucination, bias, cost, privacy, security, and explainability |

---

## 🚀 What's Next?

| Chapter | Topic | Main Focus |
| ---: | --- | --- |
| **1** | **LLM Foundations** | Transformer, training, and inference |
| **2** | **Prompt Engineering** | Writing effective prompts and instructions |
| **3** | **RAG** | Connecting LLMs to outside knowledge |
| **4** | **Fine-Tuning** | Adapting models to specific tasks and domains |
| **5** | **AI Agents** | Reasoning, tools, and taking action |
| **6** | **Multimodal AI** | Working with text, images, audio, and more |

---

