# GenState ⚖️🌐

> **Decentralized Semantic State & Truth Adjudication Protocol on GenLayer GenVM**

GenState is an intelligent state consensus protocol built natively on GenLayer's GenVM. It establishes a verifiable bridge between off-chain reality and on-chain state by turning unstructured public web evidence into cryptographically settled semantic state records.

---

## 🚀 Live StudioNet Deployment (v1.2.0)

| Parameter | Value |
| :--- | :--- |
| **Network** | **GenLayer StudioNet** (Chain ID: `61999` / `0xf22f`) |
| **Contract Name** | `GenState` (v1.2.0) |
| **Deployed Contract Address** | [`0x619C7880ADF334Ee402A6140ee3f4fC1942059bD`](https://explorer-studio.genlayer.com/address/0x619C7880ADF334Ee402A6140ee3f4fC1942059bD) |
| **Deployment Transaction Hash** | [`0x0e9be6998c1e98b7e35e3aecfc5a18be8688a741bf56983aaa6218b2eff825f2`](https://explorer-studio.genlayer.com/tx/0x0e9be6998c1e98b7e35e3aecfc5a18be8688a741bf56983aaa6218b2eff825f2) |
| **Deployer / Admin Address** | `0x8EBFC0d85233F56f777F8e16793bC758608019bE` |
| **Live Vercel DApp** | [https://genstate.vercel.app](https://genstate.vercel.app) |
| **GitHub Repository** | [https://github.com/Dark-Brain07/GenState](https://github.com/Dark-Brain07/GenState) |
| **Medium Article** | [Read on Medium](https://medium.com/@engraju007/introducing-genstate-decentralized-semantic-state-adjudication-on-genlayer-c1363386f7cc) |
| **GenVM Runner Pin** | `py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6` |

---

## 📜 Verified Live StudioNet Transaction Proofs (v1.2.0)

Every operation below was executed, mined, and finalized by GenLayer validators on StudioNet (Chain ID `61999`):

### 1. Multi-Funder Deposit & Deterministic Settlement Lifecycle (`CLAIM-2`)

| Operation | Participant / Details | Tx Hash / Explorer Link | Finality |
| :--- | :--- | :--- | :--- |
| **Claim Registration** | Factual Assertion registered in `DRAFT` status | [`0x135c17fbdf6dab6890963e6ed3c2e2a2c1939099413efb141387ec6af9208c94`](https://explorer-studio.genlayer.com/tx/0x135c17fbdf6dab6890963e6ed3c2e2a2c1939099413efb141387ec6af9208c94) | Finalized (Status: 7) |
| **Funder 1 Deposit** | Alice (`0x49Dc...2B4`) deposits **0.20 GEN** | [`0x71552992aa06438f78836191b086830e432223ad4c8374205d9d66a8a63e3b77`](https://explorer-studio.genlayer.com/tx/0x71552992aa06438f78836191b086830e432223ad4c8374205d9d66a8a63e3b77) | Finalized (Status: 7) |
| **Funder 2 Deposit** | Bob (`0xaBFA...685`) deposits **0.10 GEN** (Total Escrow: 0.30 GEN) | [`0xc77f9dca1125dbc1323d387b0dd4397602968cdda4cf3bc1c2d3b3a26c0f6415`](https://explorer-studio.genlayer.com/tx/0xc77f9dca1125dbc1323d387b0dd4397602968cdda4cf3bc1c2d3b3a26c0f6415) | Finalized (Status: 7) |
| **Freeze Claim** | Opens 60s timed window with `OPEN_PUBLIC` policy | [`0x78041f0e6b49b78558918e91171e6ec31c922e5e600d184a4348c9e6cca0ecd6`](https://explorer-studio.genlayer.com/tx/0x78041f0e6b49b78558918e91171e6ec31c922e5e600d184a4348c9e6cca0ecd6) | Finalized (Status: 7) |
| **Qualifying Evidence** | Charlie submits `https://example.com` with verbatim quote | [`0x94c5ead50afb0733007bb70e2ad2a59cef2cbf493f1fbfd94922e710abdd68d9`](https://explorer-studio.genlayer.com/tx/0x94c5ead50afb0733007bb70e2ad2a59cef2cbf493f1fbfd94922e710abdd68d9) | Finalized (Status: 7) |
| **Non-Qualifying Evidence** | Dave submits unrelated evidence (`https://example.org`) | [`0x51569249289a7b0972bb3db795e372c68135c658153980922e289596ec0163a7`](https://explorer-studio.genlayer.com/tx/0x51569249289a7b0972bb3db795e372c68135c658153980922e289596ec0163a7) | Finalized (Status: 7) |
| **Validator Consensus Adjudication** | Multi-validator quorum: SHA-256 fingerprint saved, verbatim quote verified, Dave excluded, Charlie designated qualifying recipient | [`0x5a2965916083e77d768ba24e0343602146a119c7d5e310d1d01a8130a75d9192`](https://explorer-studio.genlayer.com/tx/0x5a2965916083e77d768ba24e0343602146a119c7d5e310d1d01a8130a75d9192) | Finalized (Status: 7) |
| **Native GEN Settlement Payout** | Genuine GEN transfer via `_Recipient.emit_transfer()` to Charlie: **+0.30 GEN delivered** | [`0x14ea39cbb3e7c5682f317342d5a6c82be7ef8627b8cec05ada75541d8643f406`](https://explorer-studio.genlayer.com/tx/0x14ea39cbb3e7c5682f317342d5a6c82be7ef8627b8cec05ada75541d8643f406) | Finalized (Status: 7) |

#### Verified Settlement Balance Movement:
- **Charlie Wallet Before Settlement**: `100,000,000,000,000,000 wei` (0.10 GEN)
- **Charlie Wallet After Settlement**: `400,000,000,000,000,000 wei` (0.40 GEN)
- **Net Genuine Payout**: **`+300,000,000,000,000,000 wei` (+0.30 GEN exact delivery)**

---

### 2. Multi-Funder Cancellation & Exact Individual Refunds (`CLAIM-3`)

Demonstrates that cancellation or refund **never** sends all funds to the first funder, but accurately returns each contributor's deposited GEN:

| Operation | Participant / Details | Tx Hash / Explorer Link | Finality |
| :--- | :--- | :--- | :--- |
| **Claim Registration** | Registered in `DRAFT` status | [`0xf8ed623435f028a936f8053e141b93f65efff84e145a98a7a0752c85f43e75b7`](https://explorer-studio.genlayer.com/tx/0xf8ed623435f028a936f8053e141b93f65efff84e145a98a7a0752c85f43e75b7) | Finalized (Status: 7) |
| **Funder 1 Deposit** | Alice deposits **0.15 GEN** (`150,000,000,000,000,000 wei`) | [`0x89809b215d69fb0fa2b971eabeee60611e4946b07fe5e0ea788920c09ba84d0f`](https://explorer-studio.genlayer.com/tx/0x89809b215d69fb0fa2b971eabeee60611e4946b07fe5e0ea788920c09ba84d0f) | Finalized (Status: 7) |
| **Funder 2 Deposit** | Bob deposits **0.10 GEN** (`100,000,000,000,000,000 wei`) | [`0xb568a8d4aed4fb393eab7e3202923886589f9912d6b9607d2b61aa0c8bf00e0a`](https://explorer-studio.genlayer.com/tx/0xb568a8d4aed4fb393eab7e3202923886589f9912d6b9607d2b61aa0c8bf00e0a) | Finalized (Status: 7) |
| **Claim Cancellation & Refunds** | Alice cancels claim; individual refunds automatically returned to both funders | [`0x78ed4fe04dc6ee04a6b27d4d8e049b6c7b5dc42455e1ddbe0d23340046b529a6`](https://explorer-studio.genlayer.com/tx/0x78ed4fe04dc6ee04a6b27d4d8e049b6c7b5dc42455e1ddbe0d23340046b529a6) | Finalized (Status: 7) |

#### Verified Multi-Funder Refund Balance Restitution:
- **Alice Before Refund**: `650,000,000,000,000,000 wei` ──> **After Refund**: `800,000,000,000,000,000 wei` (**`+0.15 GEN` exact restitution**)
- **Bob Before Refund**: `800,000,000,000,000,000 wei` ──> **After Refund**: `900,000,000,000,000,000 wei` (**`+0.10 GEN` exact restitution**)
- **Contract Cumulative Refund Counter**: Recorded exactly `250,000,000,000,000,000 wei` (0.25 GEN).

---

## 💡 How GenState Works

Traditional smart contracts cannot read the open web or evaluate subjective real-world conditions without centralized oracles. GenState solves this using GenLayer's multi-validator Intelligent Contract capabilities:

```
[DRAFT] ──> [REGISTERED] ──> [EVIDENCE_OPEN] ──> [ADJUDICATING] ──> [RESOLVED] ──> [SETTLED]
     │                                                                   │
     └──> [CANCELLED] (100% individual refunds)                         └──> [CONFIRMED / REFUTED / CONFLICTED]
```

### 1. Multi-Funder Contributor Accounting
- Any contributor can deposit native GEN into a claim bounty using `fund_bounty(claim_id)`.
- Each contributor's address and exact deposited amount is tracked in `claim_funders: TreeMap[str, str]` and `funder_deposits: TreeMap[str, u256]`.
- Upon cancellation (`cancel_claim`) or inconclusive adjudication refund (`refund_bounty`), the contract iterates through all recorded contributors and returns each participant's exact deposited funds. Zero GEN is incorrectly pooled to the first funder.

### 2. Deterministic Reward Eligibility
- Merely submitting an evidence URL does **not** make a participant eligible for bounty rewards.
- During consensus adjudication, validators evaluate every evidence submission and designate only those index numbers that provided genuine, qualifying corroborating proof as `qualifying_indices`.
- These indices map to `qualifying_recipients` submitter addresses stored permanently on-chain.
- `settle_bounty(claim_id, recipient)` verifies that the recipient is in `qualifying_recipients`. Calls attempting to settle to non-qualifying submitters or attackers are rejected with `gl.vm.UserError`.
- If multiple qualifying submitters exist, the escrow is deterministically divided among them using proportional unsettled share division (`total_bounty_remaining // unsettled_count`), distributing 100% of escrow with zero lost dust.
- Double-settlement protection prevents any recipient from receiving duplicate payouts.

### 3. Evidence Integrity & Cryptographic Content Fingerprinting
- **SHA-256 Fingerprint Persistence**: Each fetched web page is fingerprinted using SHA-256 and stored permanently in `claim_adjudications` on-chain.
- **Verbatim Quotation Verification**: Validators extract an exact supporting quotation and check that it appears verbatim within the retrieved text sample (`quotation_verified: bool`).
- **Publisher Independence & Apex Domain Enforcement**: Domains are normalized to registered apex domains (handling ccTLDs like `.gov.uk`, `.co.uk`, `.gov.au`). Subdomains cannot be spoofed to satisfy multi-source policies.
- **Mirror Source Detection**: If two distinct URLs return identical SHA-256 hashes, the second is flagged as `MIRROR_DUPLICATE` and excluded from multi-source counts.
- **Temporal Reference-Date Adjudication**: Claims require a validated `reference_date` (`YYYY-MM-DD`). The adjudication prompt strictly instructs validators to judge whether the assertion was true as of that historical date, preventing historical claims from being corrupted by later state changes.
- **Zero-Revert Web Fallback**: External network queries gracefully downgrade without reverting transactions. If all sources are unreachable, the contract resolves `SOURCE_UNAVAILABLE`.

---

## 🛡️ Admissibility Policies

- **`OFFICIAL_REGISTRY`**: Requires proof grounded in official municipal, land, corporate, or state registry endpoints (`.gov`, `.mil`, `.int`, or verified registries like `sec.gov`, `companieshouse.gov.uk`).
- **`REGULATORY_FILING`**: Requires statutory notices, SEC bulletins, or gazette filings.
- **`MULTI_SOURCE_INDEPENDENT`**: Requires at least 2 distinct independent apex domains with non-colliding content fingerprints.
- **`PRIMARY_PLUS_CORROBORATION`**: Requires primary originating announcement plus third-party verification.
- **`OPEN_PUBLIC`**: Admissible across credible public web domains.

---

## 🧪 Executable Behavioral Test Suite (GenVM Direct Mode)

GenState includes an executable test suite running natively in GenLayer Direct Mode (`pytest tests/test_direct_gen_state.py`):

```bash
python -m pytest tests/test_direct_gen_state.py -v
```

### Test Coverage (14/14 Passed in 0.73s):
1. `test_access_control_freeze_and_cancel`: Creator authorization and draft state transition enforcement.
2. `test_reference_date_validation`: Strict format validation for `YYYY-MM-DD`.
3. `test_evidence_window_deadlines`: Rejection of premature adjudication before deadline expiration.
4. `test_multi_funder_accounting_and_individual_draft_refunds`: Multi-contributor deposits and exact individual refund delivery.
5. `test_multi_funder_inconclusive_adjudication_refunds`: Proportional multi-funder refunds for `INSUFFICIENT_EVIDENCE` outcomes.
6. `test_deterministic_reward_eligibility_and_settlement`: Rejection of non-qualifying submitters, authorized settlement, proportional division, and duplicate-settlement prevention.
7. `test_fingerprint_persistence_and_quotation_verification`: Verifies SHA-256 fingerprints and quotation verification in persistent on-chain record.
8. `test_apex_domain_publisher_independence_enforcement`: Confirms subdomains of same apex domain do not count as independent.
9. `test_official_registry_policy_enforcement`: Rejection of non-official domains under `OFFICIAL_REGISTRY`.
10. `test_regulatory_filing_policy_enforcement`: Enforcement of regulatory domains under `REGULATORY_FILING`.
11. `test_conflicting_observations_consensus`: Conservative `CONFLICTED` ruling when sources dispute assertions.
12. `test_malformed_llm_response_handling`: Defensive JSON recovery and schema validation without contract crashes.
13. `test_all_sources_unreachable_resolves_source_unavailable`: Safe fallback preventing self-reported text from generating conclusive verdicts.
14. `test_refuted_verdict_bounty_settlement`: Legitimate reward settlement on `REFUTED` findings.

---

## 💻 Frontend Application

Built with React 19, TypeScript, Vite, and Vanilla CSS glassmorphism:
- **Active Network Guard**: Detects connected wallet chain and enforces GenLayer StudioNet (`61999` / `0xf22f`). Shows a warning banner with one-click network switch if mismatched.
- **Multi-Funder Funding Modal**: Allows any connected wallet to deposit native GEN with real-time balance checks.
- **Deterministic Settlement Modal**: Inspects qualifying recipients designated by consensus and enables one-click authorized settlement.
- **Refund & Cancellation Controls**: Interactive triggers for creator draft cancellations and contributor refunds.
- **Evidence Integrity Badges**: Renders quotation verification status (`VERIFIED QUOTE` / `UNVERIFIED`) and persistent SHA-256 source fingerprints.
- **Live URL**: [https://genstate.vercel.app](https://genstate.vercel.app)

```bash
cd frontend
npm install
npm run build
npm run dev
```

---

## 🔬 GenVM Compliance & Audit Highlights

- **Storage Pre-Extraction Audit**: All contract state is pre-extracted into local primitives prior to `leader_fn` execution; zero `self` references exist in non-deterministic closures.
- **Pinned Runner Audit**: Pinned to `# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }`.
- **Zero-Revert Web Fallback Audit**: External network queries gracefully downgrade without reverting transactions.
- **Strict AST Sandbox Audit**: Exclusively uses `from genlayer import *` and `import json` with zero forbidden standard libraries (`genvm-lint`: 0 errors).
- **Active On-Chain Verified**: Confirmed with live multi-funder deposits, payouts, and refunds on GenLayer StudioNet.
