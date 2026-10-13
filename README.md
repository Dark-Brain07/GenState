# GenState ⚖️🌐

> **Decentralized Semantic State & Truth Adjudication Protocol on GenLayer GenVM**

GenState is an intelligent state consensus protocol built natively on GenLayer's GenVM. It establishes a verifiable bridge between off-chain reality and on-chain state by turning unstructured public web evidence into cryptographically settled semantic state records.

---

## 🚀 Live StudioNet Deployment

| Parameter | Value |
| :--- | :--- |
| **Network** | **GenLayer StudioNet** (Chain ID: `4224`) |
| **Contract Name** | `GenState` |
| **Deployed Contract Address** | [`0xae97EC507454Db2ABA53ef53cA97b7F308801cb1`](https://explorer-studio.genlayer.com/address/0xae97EC507454Db2ABA53ef53cA97b7F308801cb1) |
| **Deployment Transaction Hash** | `0x9e02d698082b22e847d5c292ab59a2f997cb8aa72a70a364579241fdfee54b89` |
| **Genesis Attestation Tx Hash** | `0x3157648fa5cdbc222e568b372d760490f5e0f7fbbe372db641f868a8fc91a262` |
| **Consensus Round** | Round 0 (Finalized with 5/5 validator quorum) |
| **Explorer Link** | [View on GenLayer Studio Explorer](https://explorer-studio.genlayer.com/address/0xae97EC507454Db2ABA53ef53cA97b7F308801cb1) |

---

## 💡 How GenState Works

Traditional smart contracts cannot read the open web or evaluate subjective real-world conditions without centralized oracles. GenState solves this using GenLayer's multi-validator Intelligent Contract capabilities:

1. **Structured State Assertion**:
   - A participant registers a formal claim (`subject`, `predicate`, `asserted_value`, `reference_date`).
   - The creator binds the claim to an immutable **Admissibility Policy** and freezes it.
2. **Open Evidence Collection**:
   - Public contributors attach verifiable web sources (`source_url`, explanation).
   - Anyone can attach an escrowed bounty reward in GEN for evidence submitters.
3. **Multi-Validator AI Consensus**:
   - Validators independently fetch external web pages defensively (`gl.nondet.web.get`).
   - An LLM evaluation prompt scores the evidence against the frozen policy and predicate.
   - Validators reach agreement on the primary verdict via `gl.eq_principle.prompt_comparative`.
4. **Deterministic State Settlement**:
   - Terminal state is recorded (`CONFIRMED`, `REFUTED`, `CONFLICTED`, `INSUFFICIENT_EVIDENCE`).
   - Escrowed bounties are released deterministically upon resolution.

```
[DRAFT] ──> [REGISTERED] ──> [EVIDENCE_OPEN] ──> [ADJUDICATING] ──> [RESOLVED] ──> [SETTLED]
     │                                                                   │
     └──> [CANCELLED]                                                   └──> [CONFIRMED / REFUTED / CONFLICTED]
```

---

## 🛡️ Admissibility Policies

- **`OFFICIAL_REGISTRY`**: Requires proof grounded in official municipal, land, corporate, or state registry endpoints.
- **`REGULATORY_FILING`**: Requires statutory notices, SEC bulletins, or gazette filings.
- **`MULTI_SOURCE_INDEPENDENT`**: Requires at least 2 distinct independent news/telemetry records.
- **`PRIMARY_PLUS_CORROBORATION`**: Requires primary originating announcement plus third-party verification.
- **`OPEN_PUBLIC`**: Admissible across credible public web domains.

---

## 🏗️ Project Architecture

```
GenState/
├── contracts/
│   └── gen_state.py           # GenVM Intelligent Contract (Strict AST & Pre-Extraction Compliant)
├── scripts/
│   ├── deploy_studionet.py    # Automated StudioNet deployment pipeline
│   ├── lint_contract.py       # GenVM Linter validation runner
│   └── test_live_interaction.py # Live on-chain interaction script
├── tests/
│   └── test_gen_state.py      # Contract syntax, storage purity, and schema test suite
├── frontend/                  # Modern Cyber-Emerald Glassmorphism Web App
│   ├── src/
│   │   ├── types/             # Protocol type definitions
│   │   ├── lib/               # GenState client & StudioNet config
│   │   ├── App.tsx            # Interactive state explorer & adjudication terminal
│   │   └── index.css          # Vanilla CSS design system
│   └── package.json
└── docs/
    └── deployment.json        # Live on-chain deployment receipt & metadata
```

---

## ⚡ Quickstart & Setup

### 1. Smart Contract Verification & Tests

```bash
# Verify GenVM AST safety & SDK semantics
python scripts/lint_contract.py contracts/gen_state.py

# Run test suite
python -m pytest tests/ -v
```

### 2. Deploy to StudioNet

```bash
python scripts/deploy_studionet.py
```

### 3. Run the Frontend

```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:5173/` in your browser.

---

## 🔬 GenVM Compliance & Audit Highlights

- **Storage Pre-Extraction**: All contract state is pre-extracted into local primitives prior to `leader_fn` execution; zero `self` references exist in non-deterministic closures.
- **Pinned Runner**: Pinned to `# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }`.
- **Zero Revert Web Fallback**: External network queries gracefully downgrade without reverting transactions.
- **Strict AST Sandbox**: Exclusively uses `from genlayer import *` and `import json` with zero forbidden standard libraries.
