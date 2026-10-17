# GenLayer Points Portal Submissions

## Project Submission (Projects & Milestones)

**Title:** GenState: Decentralized Semantic State & Truth Adjudication Protocol
**Category:** Projects & Milestones (Full DApp, Repository & MVP)
**Primary Tag:** `AI & Agents`
**Tag 1:** `Dataset Verification`
**Tag 2:** `Workflow Automation`

**Description:**
GenState is a decentralized truth and state consensus protocol built natively on GenLayer's GenVM. It transforms unstructured public web evidence into cryptographically settled semantic state records. Participants declare structured assertions (e.g. land deeds, corporate acquisitions, compliance milestones, protocol telemetry) and lock them under frozen admissibility policies. During adjudication, GenLayer validators independently fetch web sources defensively, evaluate the evidence against the frozen predicate using an LLM evaluation prompt, and reach consensus via the comparative equivalence principle. Escrowed bounties are released deterministically upon settlement, and un-transferred funds are safely captured in pull-recovery escrow.

- **Contract Address:** `0xeD9b8ef621c57d8eeFBF45124D1535f5874A4be6`
- **Explorer Link:** [View on GenLayer Studio](https://explorer-studio.genlayer.com/address/0xeD9b8ef621c57d8eeFBF45124D1535f5874A4be6)
- **Deployment Transaction:** `0xd3850e5cb6b88846bbf0010717524e4660a7c94f2b1dfa888cc7cd261f25305b`
- **Live Assertion Declare Tx (CLAIM-1):** `0x8e206f673d4da22008a2df8efa59465569cd8e3ccbb4d5e0e44316501eaebe1d`
- **Live Multi-Funder Funding Txs:** `0x707ca0f4d1d22e50b5eb09931337efa37ada52d498fcef07835c13a83e969e78` (0.20 GEN) & `0x189e0e7ac428ac62e67a21527fd46b3b54d1736f2303fc8a8e7949fabc349c5a` (0.10 GEN)
- **Live Evidence Submission Tx (EVID-1):** `0x845f3f187dc4268fec625c0c7768c84cdc112042e847af21d39b999272b60852`
- **Live LLM Consensus Adjudication Tx:** `0xd8c2f4506dcf2608d0fe0476d98118d4111ad163278f849f00bd0a890b9f0f9e`
- **Live Native GEN Bounty Settlement Tx:** `0x4012d1f3d18626aa61278e06bc1094cdb3dfa816c3d90d7e1a0c0904d5e25f7b` (+0.30 GEN delivered)
- **Live Quotation Check Blocking Tx (CLAIM-2):** `0x082b8354d8ec7e54d946f2b3e938e6220fddc9b313c21e35e0cdd254fda2f663`
- **Live Multi-Funder Draft Cancellation & Refund Tx (CLAIM-3):** `0x55314b8aa385959216efd83790959991d7f99b3010e6c3f6dc3fa1d5138866b9` (+0.15 GEN / +0.10 GEN)
- **GitHub Repository:** [https://github.com/Dark-Brain07/GenState](https://github.com/Dark-Brain07/GenState)
- **Live Production DApp:** [https://genstate.vercel.app](https://genstate.vercel.app)
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
Core GenLayer Intelligent Contract running on GenVM with pinned runner version hash (`py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6`). Implements genuine native GEN settlement, multi-funder contribution tracking with exact individual draft refunds, pull-pattern failed-transfer recovery (`pending_recoveries`), timed evidence submission windows, quotation verification blocking of unsupported conclusive verdicts, duplicate mirror source detection with apex domain normalization, SHA-256 evidence fingerprint persistence, strict closure storage pre-extraction, defensive zero-revert web fetching, strict AST sandbox compliance (zero forbidden imports), and multi-validator comparative consensus (`gl.eq_principle.prompt_comparative`).

- **Contract Address:** `0xeD9b8ef621c57d8eeFBF45124D1535f5874A4be6`
- **Explorer Link:** [View on GenLayer Studio](https://explorer-studio.genlayer.com/address/0xeD9b8ef621c57d8eeFBF45124D1535f5874A4be6)
- **Deployment Transaction:** `0xd3850e5cb6b88846bbf0010717524e4660a7c94f2b1dfa888cc7cd261f25305b`
- **Source File:** `contracts/gen_state.py`
