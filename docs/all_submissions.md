# GenLayer Points Portal Submissions

## Project Submission (Projects & Milestones)

**Title:** GenState: Decentralized Semantic State & Truth Adjudication Protocol
**Category:** Projects & Milestones (Full DApp, Repository & MVP)
**Primary Tag:** `AI & Agents`
**Tag 1:** `Dataset Verification`
**Tag 2:** `Workflow Automation`

**Description:**
GenState is a decentralized truth and state consensus protocol built natively on GenLayer's GenVM. It transforms unstructured public web evidence into cryptographically settled semantic state records. Participants declare structured assertions (e.g. land deeds, corporate acquisitions, compliance milestones, protocol telemetry) and lock them under frozen admissibility policies. During adjudication, GenLayer validators independently fetch web sources defensively, evaluate the evidence against the frozen predicate using an LLM evaluation prompt, and reach consensus via the comparative equivalence principle. Escrowed bounties are released deterministically upon settlement.

- **Contract Address:** `0x7e131cDcCd7CfFB2E78A527a369c88BCEd770cf6`
- **Explorer Link:** [View on GenLayer Studio](https://explorer-studio.genlayer.com/address/0x7e131cDcCd7CfFB2E78A527a369c88BCEd770cf6)
- **Deployment Transaction:** `0xc7d41232dcdfdd518aa4793297e1b02468242a2a2a55991cd9e8bbccb05726ea`
- **Live Assertion Declare Tx (CLAIM-1):** `0x6063c0d9c30d521f6673534ec261c44a30412874a6b7e9b7faac7b3f024a9465`
- **Live Evidence Submission Tx (EVID-1):** `0xc46628961bc87aa0f037fa235b134c61f90d1a4d3d0a33267d61f6aad45feb05`
- **Live LLM Consensus Adjudication Tx:** `0x861a3248e7abf6e830f09394ecfccda2ceb550a9aabd51e888d8189c3da68bb6`
- **Live Native GEN Bounty Settlement Tx:** `0x1ccf5ece4a8a92c5f394980d2b965f405880e39df18584d78f946a7df4935d1c`
- **GitHub Repository:** [https://github.com/Dark-Brain07/GenState](https://github.com/Dark-Brain07/GenState)
- **Live Vercel DApp:** [https://genstate.vercel.app](https://genstate.vercel.app)
- **Network:** GenLayer StudioNet (Chain ID: 61999 / 0xf22f)

---

## Intelligent Contract Submission (Tools & Infrastructure)

#### GenState Intelligent Contract

**Title:** GenState Core State Consensus & Admissibility Gate
**Category:** Tools & Infrastructure (Intelligent Contract)
**Primary Tag:** `Dispute Resolution`
**Tag 1:** `Protocol Experiment`
**Tag 2:** `Workflow Automation`

**Description:**
Core GenLayer Intelligent Contract running on GenVM with pinned runner version hash (`py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6`). Implements genuine native GEN settlement, safe funder refunds, timed evidence windows, deterministic source admissibility policies, SHA-256 evidence fingerprinting, strict closure storage pre-extraction, defensive zero-revert web fetching, strict AST sandbox compliance (zero forbidden imports), and multi-validator comparative consensus (`gl.eq_principle.prompt_comparative`).

- **Contract Address:** `0x7e131cDcCd7CfFB2E78A527a369c88BCEd770cf6`
- **Explorer Link:** [View on GenLayer Studio](https://explorer-studio.genlayer.com/address/0x7e131cDcCd7CfFB2E78A527a369c88BCEd770cf6)
- **Deployment Transaction:** `0xc7d41232dcdfdd518aa4793297e1b02468242a2a2a55991cd9e8bbccb05726ea`
- **Source File:** `contracts/gen_state.py`

