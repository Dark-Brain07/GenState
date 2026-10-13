# GenLayer Points Portal Submissions

## Project Submission (Projects & Milestones)

**Title:** GenState: Decentralized Semantic State & Truth Adjudication Protocol
**Category:** Projects & Milestones (Full DApp, Repository & MVP)
**Primary Tag:** `AI & Agents`
**Tag 1:** `Dataset Verification`
**Tag 2:** `Workflow Automation`

**Description:**
GenState is a decentralized truth and state consensus protocol built natively on GenLayer's GenVM. It transforms unstructured public web evidence into cryptographically settled semantic state records. Participants declare structured assertions (e.g. land deeds, corporate acquisitions, compliance milestones, protocol telemetry) and lock them under frozen admissibility policies. During adjudication, GenLayer validators independently fetch web sources defensively, evaluate the evidence against the frozen predicate using an LLM evaluation prompt, and reach consensus via the comparative equivalence principle. Escrowed bounties are released deterministically upon settlement.

- **Contract Address:** `0xae97EC507454Db2ABA53ef53cA97b7F308801cb1`
- **Explorer Link:** [View on GenLayer Studio](https://explorer-studio.genlayer.com/address/0xae97EC507454Db2ABA53ef53cA97b7F308801cb1)
- **Deployment Transaction:** `0x9e02d698082b22e847d5c292ab59a2f997cb8aa72a70a364579241fdfee54b89`
- **Genesis Attestation Tx:** `0x3157648fa5cdbc222e568b372d760490f5e0f7fbbe372db641f868a8fc91a262`
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

- **Contract Address:** `0xae97EC507454Db2ABA53ef53cA97b7F308801cb1`
- **Explorer Link:** [View on GenLayer Studio](https://explorer-studio.genlayer.com/address/0xae97EC507454Db2ABA53ef53cA97b7F308801cb1)
- **Deployment Transaction:** `0x9e02d698082b22e847d5c292ab59a2f997cb8aa72a70a364579241fdfee54b89`
- **Source File:** `contracts/gen_state.py`
