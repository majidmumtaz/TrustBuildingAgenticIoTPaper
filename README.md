# Verifiable Trust Framework for Multi-Agent IoT Systems

A standardized benchmarking suite and experimental framework for evaluating trust, safety, and security mechanisms across heterogeneous multi-agent systems (MAS) interacting via the Model Context Protocol (MCP).

This project provides end-to-end tools to execute, evaluate, and statistically analyze multi-agent interactions under adversarial conditions. It benchmarks system resilience against key threats using empirical statistical metrics like Wilcoxon signed-rank tests with Holm-Bonferroni corrections, Cliff’s Delta effect sizes, and Krippendorff’s Alpha inter-rater reliability.

---

## Key Features

* **Multi-Framework Testbed**: Integrated support for agent orchestration using `AutoGen`, `CrewAI`, and `LangGraph` across diverse LLM backends (`Claude Opus 4.7`, `GPT-class`, `Llama-class`).


* **Adversarial Attack Corpus**: Automated generation of over 450 attack variants covering 8 distinct security threat categories:


* **A1**: Direct Prompt Injection


* **A2**: Indirect Prompt Injection


* **A3**: Inter-Agent Prompt Infection


* **A4**: Tool Poisoning


* **A5**: Capability Over-Claiming


* **A6**: Byzantine Agent Behavior


* **A7**: Sybil and Collusion Attacks


* **A8**: Data Exfiltration (Trifecta)




* **Baseline Configuration Comparisons**:
* `B1_unhardened`: Standard baseline without trust mechanisms.


* `B2_best_practice`: Standard safety filtering and sanitization.


* `B3_ARGUS`: High-assurance verifiable trust and provenance framework.




* **Rigorous Metric Suite**: Evaluates Attack Success Rate (ASR), Privacy Leakage Rate (PLR), Task Utility (TU), Communication Latency, Trust Convergence Time, and Rater Auditability Scores.


* **Statistical Analysis Pipeline**: Integrated automated statistical non-parametric hypothesis testing with effect size calculation and inter-rater reliability scoring.



---

## Project Architecture

```text
├── main.py                     # Primary execution script (Testbed, Attack Corpus, Evaluation)
├── requirements.txt            # Dependency configuration file
└── README.md                   # Project documentation and setup guide

```

---

## Setup Instructions

### Prerequisites

Ensure system requirements are met before proceeding:

* **Python**: `3.9` or higher
* **Package Manager**: `pip` (or `conda`)

### Step 1: Clone or Set Up the Project Directory

Create a directory for the project and navigate into it:

```bash
mkdir verifiable-trust-framework
cd verifiable-trust-framework

```

### Step 2: Set Up a Virtual Environment

It is recommended to use a virtual environment to manage dependencies cleanly.

**On Linux/macOS:**

```bash
python3 -m venv venv
source venv/bin/activate

```

**On Windows:**

```cmd
python -m venv venv
venv\Scripts\activate

```

### Step 3: Install Required Dependencies

Create a `requirements.txt` file in your root project directory with the following content:

```text
numpy>=1.22.0
scipy>=1.8.0
statsmodels>=0.13.0
krippendorff>=0.5.0

```

Install the required packages using `pip`:

```bash
pip install -r requirements.txt

```

---

## Running Experiments

Save the framework script as `main.py`.

### Quick Demonstration Run

By default, running the main file initializes a scaled-down attack corpus (2 variants per category = 16 attacks) for fast execution and validation:

```bash
python main.py

```

### Full Benchmark Execution

To run the complete benchmark suite matching the publication paper (~450 attacks across 8 categories over 30 independent trials):

1. Open `main.py` in an editor.


2. Locate the execution entry point near line 186:


```python
attacks = generate_attack_corpus(variants_per_category=2)

```


3. Change `variants_per_category=2` to `variants_per_category=50`:


```python
attacks = generate_attack_corpus(variants_per_category=50)

```


4. Re-run the main evaluation pipeline:


```bash
python main.py

```



---

## Output Metrics Explanation

The framework automatically reports:

1. **Krippendorff’s Alpha ($\alpha$)**: Evaluates inter-rater agreement on system auditability ratings across independent human/AI reviewers.


2. **Wilcoxon Signed-Rank Test ($p$-values)**: Measures statistical significance of performance differences between baseline pairs (`B1 vs B2`, `B1 vs B3`) corrected using the Holm-Bonferroni method.


3. **Cliff’s Delta ($\delta$)**: Non-parametric effect size quantifying the magnitude of difference between baselines (positive values indicate relative improvement).



4. **Metric Breakdown**: Summarized global and per-category stats across Attack Success Rate (ASR), Privacy Leakage Rate (PLR), Task Utility (TU), Trust Convergence Rounds, and Communication Overhead (latency in ms).
=======
4. **Metric Breakdown**: Summarized global and per-category stats across Attack Success Rate (ASR), Privacy Leakage Rate (PLR), Task Utility (TU), Trust Convergence Rounds, and Communication Overhead (latency in ms).

