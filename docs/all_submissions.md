# GenLayer Points Portal Submissions

## Project Submission (Projects & Milestones)

**Title:** GenState: Decentralized Semantic State & Truth Adjudication Protocol
**Category:** Projects & Milestones (Full DApp, Repository & MVP)
**Primary Tag:** `AI & Agents`
**Tag 1:** `Dataset Verification`
**Tag 2:** `Workflow Automation`

**Description:**
GenState is a decentralized truth and state consensus protocol built natively on GenLayer's GenVM. It transforms unstructured public web evidence into cryptographically settled semantic state records. Participants declare structured assertions (e.g. land deeds, corporate acquisitions, compliance milestones, protocol telemetry) and lock them under frozen admissibility policies. During adjudication, GenLayer validators independently fetch web sources defensively, evaluate the evidence against the frozen predicate using an LLM evaluation prompt, and reach consensus via the comparative equivalence principle. Escrowed bounties are released deterministically upon settlement.

- **Contract Address:** `0x61A4F2D9fCe50dC3Cb763fC455ae8c669739dd28`
- **Explorer Link:** [View on GenLayer Studio](https://explorer-studio.genlayer.com/address/0x61A4F2D9fCe50dC3Cb763fC455ae8c669739dd28)
- **Deployment Transaction:** `0x6f3a36dd106c295e7a1b7c8dc097f817ad0b59b860a8c0649c08c8030bc8e93f`
- **Genesis Write Transaction:** `0xf74536424a92c9c8e2311cea3357d58552df557593662e521bb3cc2f41f572d4`
- **Live Assertion Declare Tx (CLAIM-3):** `0x3e55be0e7929b7ae88fa77dcd7545a60f4120cb607ef6b6821a1f089915498e7`
- **Live Evidence Submission Tx (EVID-1):** `0x492c58a28459234b3bdc2052abb3c45437bde06125917f551b90e7dd32bd8bd2`
- **Live LLM Consensus Adjudication Tx:** `0x1b9d9cc5424efbff94be28ed71699841f6c4c4da7e98315868d6d385f0e1f505`
- **Network:** GenLayer StudioNet (Chain ID: 4224)

---

## Intelligent Contract Submission (Tools & Infrastructure)

#### GenState Intelligent Contract

**Title:** GenState Core State Consensus & Admissibility Gate
**Category:** Tools & Infrastructure (Intelligent Contract)
**Primary Tag:** `Dispute Resolution`
**Tag 1:** `Protocol Experiment`
**Tag 2:** `Workflow Automation`

**Description:**
Core GenLayer Intelligent Contract running on GenVM with pinned runner version hash (`py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6`). Implements strict closure storage pre-extraction, defensive zero-revert web fetching, strict AST sandbox compliance (zero forbidden imports), and multi-validator comparative consensus (`gl.eq_principle.prompt_comparative`).

- **Contract Address:** `0x61A4F2D9fCe50dC3Cb763fC455ae8c669739dd28`
- **Explorer Link:** [View on GenLayer Studio](https://explorer-studio.genlayer.com/address/0x61A4F2D9fCe50dC3Cb763fC455ae8c669739dd28)
- **Deployment Transaction:** `0x6f3a36dd106c295e7a1b7c8dc097f817ad0b59b860a8c0649c08c8030bc8e93f`
- **Source File:** `contracts/gen_state.py`
