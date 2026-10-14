# GenState ⚖️🌐

> **Decentralized Semantic State & Truth Adjudication Protocol on GenLayer GenVM**

GenState is an intelligent state consensus protocol built natively on GenLayer's GenVM. It establishes a verifiable bridge between off-chain reality and on-chain state by turning unstructured public web evidence into cryptographically settled semantic state records.

---

## 🚀 Live StudioNet Deployment

| Parameter | Value |
| :--- | :--- |
| **Network** | **GenLayer StudioNet** (Chain ID: `61999` / `0xf22f`) |
| **Contract Name** | `GenState` (v1.1.0) |
| **Deployed Contract Address** | [`0x7e131cDcCd7CfFB2E78A527a369c88BCEd770cf6`](https://explorer-studio.genlayer.com/address/0x7e131cDcCd7CfFB2E78A527a369c88BCEd770cf6) |
| **Deployment Transaction Hash** | [`0xc7d41232dcdfdd518aa4793297e1b02468242a2a2a55991cd9e8bbccb05726ea`](https://explorer-studio.genlayer.com/tx/0xc7d41232dcdfdd518aa4793297e1b02468242a2a2a55991cd9e8bbccb05726ea) |
| **Live Declare Tx (CLAIM-1)** | [`0x6063c0d9c30d521f6673534ec261c44a30412874a6b7e9b7faac7b3f024a9465`](https://explorer-studio.genlayer.com/tx/0x6063c0d9c30d521f6673534ec261c44a30412874a6b7e9b7faac7b3f024a9465) |
| **Live Fund Bounty Tx (0.5 GEN)** | [`0x88a8e980fd8d844f9ae4183a673fe8339262815e3354cd194b1888ceb0771300`](https://explorer-studio.genlayer.com/tx/0x88a8e980fd8d844f9ae4183a673fe8339262815e3354cd194b1888ceb0771300) |
| **Live Freeze Claim Tx (60s Window)** | [`0xcfb12b04462169569b9cfe0bd4b097b29b480eecaa2ee57cc5a99855711ee53e`](https://explorer-studio.genlayer.com/tx/0xcfb12b04462169569b9cfe0bd4b097b29b480eecaa2ee57cc5a99855711ee53e) |
| **Live Evidence Submit Tx (EVID-1)** | [`0xc46628961bc87aa0f037fa235b134c61f90d1a4d3d0a33267d61f6aad45feb05`](https://explorer-studio.genlayer.com/tx/0xc46628961bc87aa0f037fa235b134c61f90d1a4d3d0a33267d61f6aad45feb05) |
| **Live Consensus Adjudication Tx (CONFIRMED)** | [`0x861a3248e7abf6e830f09394ecfccda2ceb550a9aabd51e888d8189c3da68bb6`](https://explorer-studio.genlayer.com/tx/0x861a3248e7abf6e830f09394ecfccda2ceb550a9aabd51e888d8189c3da68bb6) |
| **Live Native GEN Settlement Tx (+0.5 GEN)** | [`0x1ccf5ece4a8a92c5f394980d2b965f405880e39df18584d78f946a7df4935d1c`](https://explorer-studio.genlayer.com/tx/0x1ccf5ece4a8a92c5f394980d2b965f405880e39df18584d78f946a7df4935d1c) |
| **Live Draft Cancellation Refund Tx** | [`0xa1d852cd3627f2ed05835a8006974a62894b82850e14fb8c93ee49872a2c7076`](https://explorer-studio.genlayer.com/tx/0xa1d852cd3627f2ed05835a8006974a62894b82850e14fb8c93ee49872a2c7076) |
| **Consensus Finality** | Finalized (Status: 7, multi-validator quorum agree) |
| **Live Vercel DApp** | [https://genstate.vercel.app](https://genstate.vercel.app) |
| **Medium Article** | [Read on Medium](https://medium.com/@engraju007/introducing-genstate-decentralized-semantic-state-adjudication-on-genlayer-c1363386f7cc) |
| **Explorer Link** | [View on GenLayer Studio Explorer](https://explorer-studio.genlayer.com/address/0x7e131cDcCd7CfFB2E78A527a369c88BCEd770cf6) |

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
- **Active On-Chain Verified**: Confirmed with live read/write transactions on GenLayer StudioNet.
