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

🕰️ Historical Context
Evolution of NLP Timeline
Era	Stage	Main Idea
1950s–1970s	Rule-Based NLP	The earliest era of NLP, using hand-written rules and linguistic expertise for language processing
1980s–1990s	Statistical NLP	Uses statistical models and probability for analyzing data and generating language
1990s–2000s	Machine Learning	ML methods are applied to NLP and become widely adopted
2000s	Word Embedding	Words are represented as high-dimensional dense vectors to capture meaning and semantic relationships
2000s–2010s	RNN (Recurrent Neural Network)	Sequential models process data while accounting for context and relationships between words
2010s	LSTM	Improves RNNs' ability to retain long-term information, solving the forgetting problem
2014	Attention Mechanism	Lets models focus efficiently on the important parts of the input
2017	Transformer Architecture	Uses Self-Attention with massive data and compute — enables deeper language understanding (Vaswani et al., 2017)
2018–present	Large Language Models (LLM)	The era of large-scale language models and their widespread application
---
🧠 What is a Large Language Model?
> A Large Language Model (LLM) is a type of AI model — built on the Transformer architecture — trained on massive amounts of text data to understand and generate human-like language.
How an LLM Works
Stage	Description
Training Data	The model is trained on massive amounts of text from books, articles, websites, code, and more
Training Process	The model learns language patterns, grammar, facts, and reasoning by predicting the next word in a sentence
Understanding	The model builds a deep understanding of language, context, and relationships between words
Generation	Given an instruction, the model predicts and generates the response that best fits the context
Key Characteristics of LLMs
#	Characteristic	Description
1	Large-Scale Data	Trained on massive text from the internet, books, articles, code, and other sources
2	Massive Parameters	Contains huge numbers of parameters that let the model learn complex language patterns
3	Transformer Architecture	Uses Self-Attention to understand context and word relationships more effectively
4	Scaling Law	Performance improves predictably as model size, data, and compute increase
5	Diverse Capabilities	Performs many tasks — Q&A, writing, reasoning, summarization — with few or no examples (zero-shot / few-shot)
Example models: GPT-4 / GPT-4o (OpenAI) · Llama 3 (Meta) · Gemini (Google) · Mistral AI · Claude (Anthropic) · DeepSeek
Key Takeaway: LLMs combine large-scale data, massive parameters, the Transformer architecture, and scaling laws to achieve powerful language understanding and generation across a wide range of tasks.
Common Use Cases
#	Application	Description
1	Chatbot	Natural-language conversation, question answering, and 24/7 user assistance
2	Programming	Generating, explaining, fixing, and improving code
3	Education	Personalized tutoring, content creation, and learning support
4	Healthcare	Supporting medical decisions and summarizing clinical documents
5	Translation	Translating text between languages while preserving meaning and context
6	Document Analysis	Extracting, summarizing, and analyzing information from documents
7	Research Assistant	Searching, summarizing, and compiling information quickly and accurately
8	Robotics	Helping robots understand instructions, plan tasks, and interact with their environment
---
❓ What is a Language Model?
> A Language Model (LM) is a mathematical model that estimates the probability of a sequence of words: **P(w₁, w₂, ..., wₙ)**
Goal: given a partial sequence of words, predict the word most likely to come next.
```text
w₁ → w₂ → w₃ → ... → wₙ₋₁ → [predicted next word]
```
Traditional NLP vs. Large Language Models
	Traditional NLP	Large Language Models (LLMs)
Feature design	Requires manually designed features and domain expertise	Learns representations automatically
Vocabulary	Limited vocabulary — frequent Out-Of-Vocabulary (OOV) words	Handles broad, open vocabulary
Context understanding	Struggles to capture long-range relationships and complex context	Deep, broad contextual understanding
Generalization	Often requires task-specific systems	Learns from few examples and performs multiple tasks (few-shot)
Output	Rule-based / statistical output	Natural, fluent, human-like language
---
⚖️ Why Large Language Models?
Advantages
Understands context deeply and generates natural, fluent language
Learns and performs well even with very few training examples (few-shot learning)
Works across many tasks without needing task-specific design
Improves predictably as data and compute scale up (Scaling Law)
Limitations
May hallucinate — generate incorrect or fabricated information
May reflect and amplify bias present in training data
Trained with a knowledge cutoff — unaware of recent events
Requires significant compute, memory, and energy to train and run
Raises privacy, security (e.g., prompt injection), and explainability concerns
Core Components of an LLM System
#	Component	Learns / Processes	Output
01	Tokenization	Raw text	Sequence of tokens
02	Embedding	Tokens	Dense numerical vectors
03	Self-Attention	Token relationships in context	Contextualized representations
04	Pretraining	Large-scale unlabeled text	Foundation Model
05	Fine-Tuning	Task/domain-specific data	Adapted Model
06	Inference	User prompt	Generated text
In Summary: an LLM system converts text into tokens, learns contextual relationships through Self-Attention, builds general knowledge through pretraining, specializes through fine-tuning, and generates responses through inference.
---
1️⃣ Transformer Architecture
The Transformer uses an Encoder–Decoder structure with a Self-Attention mechanism to process all tokens in parallel. — Vaswani et al., 2017
Transformer: Processing a Sequence
Stage	Description
Input	Words in the sentence are converted into tokens and fed into the model
Embedding	Tokens are converted into numerical vectors the model can process
Positional Encoding	Word-position information is added to the word vectors
Encoder	Contextual information is extracted from the text into a deep representation
Decoder	The output is generated word by word, using the Encoder's output and previously generated words
Output	The answer is generated as a sequence until the sentence is complete
Transformer: The Problem It Solves (vs. RNN)
Transformers overcome the limitations of RNNs, which process tokens sequentially, learn slowly over long sequences, suffer from vanishing gradients, and struggle to retain long-range context.
Goals:
Process in parallel — process every token simultaneously via Self-Attention, instead of step by step
Understand context holistically — let every word connect directly to every other word
Capture long-range dependencies — access distant words in a sentence efficiently
Avoid gradient vanishing — maintain strong gradients across long sequences
Enable faster training and inference — parallel computation speeds up both training and generation
Transformer: Key Components
Token Embedding — converts tokens into dense numerical vectors
Positional Encoding — injects word-order information into embeddings
Multi-Head Self-Attention — lets the model attend to different parts of the sequence simultaneously
Masked Multi-Head Self-Attention — used in the decoder to prevent attending to future tokens
Multi-Head Cross-Attention — lets the decoder attend to the encoder's output
Feed Forward Network — processes each position independently after attention
Add & Norm — residual connections and layer normalization for stable training
BERT — a real-world example using only the Encoder stack (12 layers)
Transformer: Summary
Uses Self-Attention to process all token positions simultaneously
Overcomes RNNs' sequential-processing, gradient-vanishing, and long-context limitations
Learns relationships between all tokens → context
Main components: Encoder, Decoder, Self-Attention, Positional Encoding
Powers real-world models such as BERT and modern LLMs
---
2️⃣ LLM Training Pipeline
Training an LLM proceeds from massive raw data to a general-purpose Foundation Model, then to a task- or domain-adapted model through fine-tuning.
Training: From Data to Adapted Model
Stage	Description
Training Data	Books, Wikipedia, websites, code, research, technical docs, and conversations
Pretraining	The model learns to predict the next token using Cross Entropy Loss on trillions of tokens
Foundation Model	The result of pretraining — a model with general language knowledge
Fine-Tuning	The Foundation Model is adapted using task-, domain-, or instruction-specific data
Adapted Model	A model specialized for a specific task, domain, or set of instructions
Training: The Goals
Learn general language knowledge — grammar, facts, reasoning, and world knowledge from large-scale pretraining
Predict the next token accurately — minimize Cross Entropy Loss across the training corpus
Adapt to specific tasks or domains — specialize a general model for a target use case
Follow instructions reliably — align model outputs with user intent (Instruction Tuning)
Become production-ready — improve accuracy, relevance, and reliability for real-world use
Training: Popular Fine-Tuning Methods
Instruction Tuning — teaches the model to understand instructions and generate helpful responses (instruction → response pairs)
Domain Tuning — specializes the model in a domain using domain-specific corpora (e.g., medical, legal, financial)
Task Tuning — adapts the model to a specific task's objective using labelled data
Real-world use cases: Healthcare (medical Q&A, clinical document summarization), Legal (contract drafting, case analysis), Finance (financial reporting, market and risk analysis)
Training: Summary
Two main stages: Pretraining and Fine-Tuning
Pretraining uses large-scale, unlabeled data to build a Foundation Model
Fine-tuning uses task/domain-specific data to build an Adapted Model
Objective: predict the next token (pretraining) → align with task/instruction (fine-tuning)
Result: a model that is accurate, on-point, and ready for real-world use
---
3️⃣ Inference Pipeline
Inference is the process of using a trained LLM to generate output from a user prompt.
Inference: From Prompt to Generated Text
Stage	Description
Prompt	The user provides an instruction or input text
Tokenizer	The prompt is converted into tokens and token IDs the model understands
LLM	The model processes the tokens and predicts probabilities for the next token
Sampling	A generation strategy selects the next token from the probability distribution
Generated Text	Generated tokens are decoded back into human-readable text
Inference: The Goals
Understand the prompt — correctly tokenize and interpret the user's instruction
Predict the next token — compute probabilities over the vocabulary given the context
Select tokens appropriately — balance coherence and diversity through sampling strategy
Generate coherent text — produce fluent, contextually consistent output, one token at a time
Stop appropriately — end generation at an EOS token or maximum length
Inference: Popular Sampling Settings
Temperature — controls randomness/creativity of the output
Top-k — samples from only the k most likely next tokens
Top-p (nucleus sampling) — samples from the smallest set of tokens whose cumulative probability exceeds p
Max Tokens — limits the maximum length of generated output
Repetition Penalty — discourages repeated tokens/phrases
Stop Sequences — defines strings that terminate generation early
Inference: Summary
Converts a Prompt → Tokens → Predictions → Generated Text
Generation happens token by token, feeding each new token back into the model
Main goal: coherent, contextually accurate text generation
Common settings: max tokens, temperature, top-p, top-k, repetition penalty, stop sequences
---
📌 Comparative Summary Table — Transformer, Pretraining & Fine-Tuning, Inference
Feature	Transformer Architecture	Pretraining	Fine-Tuning	Inference
Input	Tokens + positional info	Large-scale unlabeled text	Task/domain-specific data	User prompt
Core Mechanism	Self-Attention	Next-token prediction	Instruction/domain/task tuning	Sampling from predicted probabilities
Main Goal	Understand context in parallel	Learn general language knowledge	Adapt to a task or domain	Generate a response
Output	Contextual representations	Foundation Model	Adapted Model	Generated text
Example	BERT, GPT	GPT-3 base model	Instruction-tuned ChatGPT-style model	A chatbot's reply to a question
---
📌 Applications of LLMs by Example
Example	Application	Input	Output
Customer support chatbot	Chatbot	User question	Conversational answer
Code generation assistant	Programming	Natural-language request	Generated / fixed code
Personalized tutor	Education	Student question or topic	Explanation / learning content
Clinical document summarizer	Healthcare	Medical records	Summary for clinicians
English–Thai translator	Translation	Source-language text	Translated text
PDF report analyzer	Document Analysis	Report / document file	Extracted insights / summary
Literature review assistant	Research Assistant	Research topic	Compiled, summarized findings
Instruction-following robot	Robotics	Spoken/text command	Planned action sequence
---
✅ Summary
Conclusion
We learned what LLMs are and how they work
We learned the key components of LLMs: tokenization, Transformer, Self-Attention, model training, fine-tuning, and inference
We saw how LLMs are applied in real-world applications across many domains
We discussed the limitations of LLMs and the importance of using them responsibly
LLM Challenge
How can we build smaller, faster, and more efficient LLMs without losing quality?
How can we make LLMs more accurate, fair, and better at reasoning?
How can we ensure LLMs are private, safe, and ethical?
What new applications and innovations can we still build with LLMs?
Key Takeaways
Transformer: Tokens + Self-Attention → Contextual Understanding
Pretraining: Large-Scale Data → Foundation Model
Fine-Tuning: Task/Domain Data → Adapted Model
Inference: Prompt → Generated Text, Token by Token
---
🛣 Roadmap
```text
LLM Foundations → Prompt Engineering → RAG → Fine-Tuning → AI Agents → Multimodal AI
```
👤 Instructor
Anuruk Prommakhot (P'Ball), Ph.D.
📧 anuruk.p@en.rmutt.ac.th
🏢 Signal Processing Research Laboratory (SPRL), Rajamangala University of Technology Thanyaburi (RMUTT)
🔬 Research Areas: Optimization Algorithms, Machine Learning, AI Vision, RAG Systems, Agentic AI

