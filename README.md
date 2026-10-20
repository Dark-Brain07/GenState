# GenState ⚖️🌐

> **Decentralized Semantic State & Truth Adjudication Protocol on GenLayer GenVM**

GenState is an intelligent state consensus protocol built natively on GenLayer's GenVM. It establishes a verifiable bridge between off-chain reality and on-chain state by turning unstructured public web evidence into cryptographically settled semantic state records.

> 📋 **Official Steward Review Resolution**: Complete requirement-by-requirement audit matrix, code locations, and verified on-chain proofs are documented in [docs/STEWARD_REVIEW_RESOLUTION_REPORT.md](docs/STEWARD_REVIEW_RESOLUTION_REPORT.md).

---

## 🚀 Live StudioNet Deployment (v1.4.0)

| Parameter | Value |
| :--- | :--- |
| **Network** | **GenLayer StudioNet** (Chain ID: `61999` / `0xf22f`) |
| **Contract Name** | `GenState` (v1.4.0) |
| **Deployed Contract Address** | [`0xFcf0d6c093470a008e2C9A6E1cE95698bC96Fe76`](https://explorer-studio.genlayer.com/address/0xFcf0d6c093470a008e2C9A6E1cE95698bC96Fe76) |
| **Deployment Transaction Hash** | [`0x5c752f8355dd88128e836aabf49b0cc17d07d49c45b2d96662f3b763a07506fd`](https://explorer-studio.genlayer.com/tx/0x5c752f8355dd88128e836aabf49b0cc17d07d49c45b2d96662f3b763a07506fd) |
| **Deployer Address** | `0x3252f04b1923B6fe4e53396f1FC80A0Db1CB3C17` |
| **Live Production DApp** | [https://genstate.vercel.app](https://genstate.vercel.app) |
| **GitHub Repository** | [https://github.com/Dark-Brain07/GenState](https://github.com/Dark-Brain07/GenState) |
| **Steward Review Resolution Report** | [docs/STEWARD_REVIEW_RESOLUTION_REPORT.md](docs/STEWARD_REVIEW_RESOLUTION_REPORT.md) |
| **GenVM Runner Pin** | `py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6` |

---

## 📜 Verified Live StudioNet Transaction Proofs (v1.4.0)

Every operation below was executed, mined, and finalized by GenLayer validators on StudioNet (Chain ID `61999`):

### 1. 100% Race-Free Concurrent Identical Declarations from Same Wallet (Steward Oct 20 Requirement)

Demonstrates that two concurrent declarations from the **SAME wallet** (`0xd2431CA38735C2fd438e2cAa23F094191D89675b`) with **IDENTICAL parameters** resolve unambiguously with zero misidentification:

| Operation | Request ID / Details | Tx Hash / Explorer Link | Finality |
| :--- | :--- | :--- | :--- |
| **Declaration A** | `REQ-ALICE-CONCURRENT-1792467234-A` ──> Resolved: `CLAIM-3` | [`0x047a1c776faa33dfafae14a18e49d3b32be1e01e0f3deca84cd084541dd81b02`](https://explorer-studio.genlayer.com/tx/0x047a1c776faa33dfafae14a18e49d3b32be1e01e0f3deca84cd084541dd81b02) | Finalized (Status: 7) |
| **Declaration B (CONCURRENT IDENTICAL)** | `REQ-ALICE-CONCURRENT-1792467234-B` ──> Resolved: `CLAIM-4` | [`0xd1928c6288a14a3a35d75b6926bc5baf6426d7ade845bae85893b9f8f01a176d`](https://explorer-studio.genlayer.com/tx/0xd1928c6288a14a3a35d75b6926bc5baf6426d7ade845bae85893b9f8f01a176d) | Finalized (Status: 7) |

- **Deterministic Query Verification (`get_claim_by_request_id`)**:
  - `get_claim_by_request_id(Alice, "REQ-ALICE-CONCURRENT-1792467234-A")` ──> Returns `CLAIM-3` (`REQ-ALICE-CONCURRENT-1792467234-A`)
  - `get_claim_by_request_id(Alice, "REQ-ALICE-CONCURRENT-1792467234-B")` ──> Returns `CLAIM-4` (`REQ-ALICE-CONCURRENT-1792467234-B`)

---

### 2. Multi-Funder Deposit & Deterministic Settlement Lifecycle (`CLAIM-3`)

| Operation | Participant / Details | Tx Hash / Explorer Link | Finality |
| :--- | :--- | :--- | :--- |
| **Funder 1 Deposit** | Alice deposits **0.20 GEN** | [`0xf74b6217b323c5ef40e38cc0e95ae61c3ddb3d4af4d80ac978b9d930d8228622`](https://explorer-studio.genlayer.com/tx/0xf74b6217b323c5ef40e38cc0e95ae61c3ddb3d4af4d80ac978b9d930d8228622) | Finalized (Status: 7) |
| **Funder 2 Deposit** | Bob deposits **0.10 GEN** (Total Escrow: 0.30 GEN) | [`0x2084c88a1d733a84b1e041019d0228fc71604f12c35a8d6351a4974f832a65ff`](https://explorer-studio.genlayer.com/tx/0x2084c88a1d733a84b1e041019d0228fc71604f12c35a8d6351a4974f832a65ff) | Finalized (Status: 7) |
| **Freeze Claim** | Opens 60s timed window with `OPEN_PUBLIC` policy | [`0x9796d2502a55fa0fb086007163daed85974017fc4187b0395d8c13f74237605f`](https://explorer-studio.genlayer.com/tx/0x9796d2502a55fa0fb086007163daed85974017fc4187b0395d8c13f74237605f) | Finalized (Status: 7) |
| **Qualifying Evidence** | Charlie submits `https://example.com` with verbatim quote | [`0x0b3a7308d9adeedf5b7550be9159767e22a9b475b7dbf17929c718cdc4236532`](https://explorer-studio.genlayer.com/tx/0x0b3a7308d9adeedf5b7550be9159767e22a9b475b7dbf17929c718cdc4236532) | Finalized (Status: 7) |
| **Validator Consensus Adjudication** | Multi-validator quorum: SHA-256 fingerprint saved, verbatim quote verified, Charlie designated qualifying recipient | [`0x4431e332d4dcc609f5f8fe5e94764ec75148845a808efe3dd94a8bd454ff1322`](https://explorer-studio.genlayer.com/tx/0x4431e332d4dcc609f5f8fe5e94764ec75148845a808efe3dd94a8bd454ff1322) | Finalized (Status: 7) |
| **Native GEN Settlement Payout** | Genuine GEN transfer via `_Recipient.emit_transfer()` to Charlie: **+0.30 GEN delivered** | [`0x1fc848a062eb4fac463669033cb86d6c8c77d63c9979deed9a38d3fc628cc4c3`](https://explorer-studio.genlayer.com/tx/0x1fc848a062eb4fac463669033cb86d6c8c77d63c9979deed9a38d3fc628cc4c3) | Finalized (Status: 7) |

#### Verified Settlement Balance Movement:
- **Charlie Wallet Before Settlement**: `1,000,000,000,000,000,000 wei` (1.0000 GEN)
- **Charlie Wallet After Settlement**: `1,300,000,000,000,000,000 wei` (1.3000 GEN)
- **Net Genuine Payout**: **`+300,000,000,000,000,000 wei` (+0.3000 GEN exact delivery)**

---

### 3. Multi-Funder Cancellation & Exact Individual Refunds (`CLAIM-4`)

| Operation | Participant / Details | Tx Hash / Explorer Link | Finality |
| :--- | :--- | :--- | :--- |
| **Funder 1 Deposit** | Alice deposits **0.15 GEN** (`150,000,000,000,000,000 wei`) | [`0xf45ec9a532787b61798e452c91ebd5d8b30291d0babc384957ccdc02cc93bf57`](https://explorer-studio.genlayer.com/tx/0xf45ec9a532787b61798e452c91ebd5d8b30291d0babc384957ccdc02cc93bf57) | Finalized (Status: 7) |
| **Funder 2 Deposit** | Bob deposits **0.10 GEN** (`100,000,000,000,000,000 wei`) | [`0xcd926d8fb095a59de770bc6208bf345326c6c999ce069310eaff29a5e68da18c`](https://explorer-studio.genlayer.com/tx/0xcd926d8fb095a59de770bc6208bf345326c6c999ce069310eaff29a5e68da18c) | Finalized (Status: 7) |
| **Draft Cancellation** | Alice cancels claim; contract executes multi-funder restitution loop | [`0xef1d008445f76ed1ccbe4937413bbe75925cafb06b650523c4cb87bb599cbff6`](https://explorer-studio.genlayer.com/tx/0xef1d008445f76ed1ccbe4937413bbe75925cafb06b650523c4cb87bb599cbff6) | Finalized (Status: 7) |

#### Exact Individual Restitution Proof:
- **Alice Refund Delta**: `+150,000,000,000,000,000 wei` (**+0.15 GEN exact refund**)
- **Bob Refund Delta (non-cancelling contributor)**: `+100,000,000,000,000,000 wei` (**+0.10 GEN exact refund**)

---

### 4. Real Failed-Transfer Recovery Pattern

- Un-transferred balances resulting from any failed native push transfer are safely captured in `pending_recoveries: TreeMap[str, u256]`.
- Enforces pull-recovery via `recover_failed_transfer(recipient)` and public inspection via `get_pending_recovery(recipient)`.
- Verified in Direct Mode Tests 16 & 17 through the REAL production `_send_gen()` helper with zero monkeypatching of contract helpers, covering both settlement and cancellation refund failure paths.

---

## 🧪 Executable Behavioral Test Suite (22 Direct Tests, 27/27 Total)

Run with `python -m pytest tests/test_direct_gen_state.py -v`:

```
============================= test session starts =============================
platform win32 -- Python 3.13.7, pytest-8.4.2, pluggy-1.6.0
collected 22 items

tests/test_direct_gen_state.py::test_access_control_freeze_and_cancel PASSED [  4%]
tests/test_direct_gen_state.py::test_reference_date_validation PASSED        [  9%]
tests/test_direct_gen_state.py::test_evidence_window_deadlines PASSED        [ 13%]
tests/test_direct_gen_state.py::test_multi_funder_accounting_and_individual_draft_refunds PASSED [ 18%]
tests/test_direct_gen_state.py::test_multi_funder_inconclusive_adjudication_refunds PASSED [ 22%]
tests/test_direct_gen_state.py::test_deterministic_reward_eligibility_and_settlement PASSED [ 27%]
tests/test_direct_gen_state.py::test_fingerprint_persistence_and_quotation_verification PASSED [ 31%]
tests/test_direct_gen_state.py::test_apex_domain_publisher_independence_enforcement PASSED [ 36%]
tests/test_direct_gen_state.py::test_official_registry_policy_enforcement PASSED [ 40%]
tests/test_direct_gen_state.py::test_regulatory_filing_policy_enforcement PASSED [ 45%]
tests/test_direct_gen_state.py::test_conflicting_observations_consensus PASSED [ 50%]
tests/test_direct_gen_state.py::test_malformed_llm_response_handling PASSED     [ 54%]
tests/test_direct_gen_state.py::test_all_sources_unreachable_resolves_source_unavailable PASSED [ 59%]
tests/test_direct_gen_state.py::test_refuted_verdict_bounty_settlement PASSED   [ 63%]
tests/test_direct_gen_state.py::test_validator_disagreement_rolls_back_safely PASSED [ 68%]
tests/test_direct_gen_state.py::test_failed_transfer_recovery_mechanism PASSED  [ 72%]
tests/test_direct_gen_state.py::test_failed_refund_transfer_recovery_mechanism PASSED [ 77%]
tests/test_direct_gen_state.py::test_unsupported_conclusive_outcome_blocked_by_quotation_check PASSED [ 81%]
tests/test_direct_gen_state.py::test_unsupported_conclusive_outcome_blocked_by_mirror_source_check PASSED [ 86%]
tests/test_direct_gen_state.py::test_concurrent_identical_declarations_disambiguated_by_request_id PASSED [ 90%]
tests/test_direct_gen_state.py::test_duplicate_request_id_replay_rejected PASSED [ 95%]
tests/test_direct_gen_state.py::test_concurrent_identical_declarations_without_request_id_prevent_race PASSED [100%]

============================= 22 passed in 1.48s ==============================
```

Full repository test suite across all modules (`python -m pytest tests/ -v`): **27 passed in 1.52s (100% pass rate)**.



---

## 🏛️ Architecture Overview

```
                      ┌────────────────────────────────────────┐
                      │          GenState Intelligent          │
                      │          Adjudication Pipeline         │
                      └──────────────────┬─────────────────────┘
                                         │
                 ┌───────────────────────┴───────────────────────┐
                 ▼                                               ▼
     ┌───────────────────────┐                       ┌───────────────────────┐
     │  Admissibility Policy │                       │   Consensus Leader    │
     │  & Source Integrity   │                       │   GenVM Execution     │
     └───────────┬───────────┘                       └───────────┬───────────┘
                 │                                               │
   ┌─────────────┴─────────────┐                   ┌─────────────┴─────────────┐
   │ Apex Domain Normalization │                   │ Non-Det Safe Data Extract │
   │ Mirror Duplicate Hash     │                   │ Verbatim Quote Check      │
   │ Official Registry Check   │                   │ Equivalence Comparator    │
   └───────────────────────────┘                   └───────────────────────────┘
                 │                                               │
                 └───────────────────────┬───────────────────────┘
                                         ▼
                      ┌────────────────────────────────────────┐
                      │        Deterministic Settlement        │
                      ├────────────────────────────────────────┤
                      │ • Conclusive Outcome Verification      │
                      │ • Qualifying Recipient Allocation      │
                      │ • Multi-Funder Proportional Refunds    │
                      │ • Push + Pull Failed-Transfer Safety   │
                      └────────────────────────────────────────┘
```

---

## 📦 Project Structure

```
GenState/
├── contracts/
│   └── gen_state.py             # GenState Intelligent Contract v1.3.0
├── frontend/
│   ├── src/
│   │   ├── App.tsx              # React UI with Network Guard & Direct Lookup
│   │   ├── lib/
│   │   │   ├── config.ts        # Contract address & StudioNet chain config
│   │   │   └── genstate-service.ts # genlayer-js service with provider sync
│   └── package.json
├── docs/
│   ├── deployment.json          # Deployment transaction metadata
│   ├── live_verification_proofs_v1_3.json # Live StudioNet transaction proofs
│   └── STEWARD_REVIEW_RESOLUTION_REPORT.md # Official resolution audit report
├── scripts/
│   ├── deploy_studionet.py      # Automated StudioNet deployment pipeline
│   ├── lint_contract.py         # AST validator for GenVM compliance
│   └── test_live_studionet_v1_3.py # Live StudioNet verification runner
└── tests/
    └── test_direct_gen_state.py # 18 GenVM Direct Mode behavioral tests
```
