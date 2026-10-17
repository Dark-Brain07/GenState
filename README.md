# GenState ⚖️🌐

> **Decentralized Semantic State & Truth Adjudication Protocol on GenLayer GenVM**

GenState is an intelligent state consensus protocol built natively on GenLayer's GenVM. It establishes a verifiable bridge between off-chain reality and on-chain state by turning unstructured public web evidence into cryptographically settled semantic state records.

> 📋 **Official Steward Review Resolution**: Complete requirement-by-requirement audit matrix, code locations, and verified on-chain proofs are documented in [docs/STEWARD_REVIEW_RESOLUTION_REPORT.md](docs/STEWARD_REVIEW_RESOLUTION_REPORT.md).

---

## 🚀 Live StudioNet Deployment (v1.3.0)

| Parameter | Value |
| :--- | :--- |
| **Network** | **GenLayer StudioNet** (Chain ID: `61999` / `0xf22f`) |
| **Contract Name** | `GenState` (v1.3.0) |
| **Deployed Contract Address** | [`0xeD9b8ef621c57d8eeFBF45124D1535f5874A4be6`](https://explorer-studio.genlayer.com/address/0xeD9b8ef621c57d8eeFBF45124D1535f5874A4be6) |
| **Deployment Transaction Hash** | [`0xd3850e5cb6b88846bbf0010717524e4660a7c94f2b1dfa888cc7cd261f25305b`](https://explorer-studio.genlayer.com/tx/0xd3850e5cb6b88846bbf0010717524e4660a7c94f2b1dfa888cc7cd261f25305b) |
| **Deployer / Admin Address** | `0xC602f93dF0F6e6b3403b6e8Ce719CfEB3D8C2E7C` |
| **Live Production DApp** | [https://genstate.vercel.app](https://genstate.vercel.app) |
| **GitHub Repository** | [https://github.com/Dark-Brain07/GenState](https://github.com/Dark-Brain07/GenState) |
| **Steward Review Resolution Report** | [docs/STEWARD_REVIEW_RESOLUTION_REPORT.md](docs/STEWARD_REVIEW_RESOLUTION_REPORT.md) |
| **GenVM Runner Pin** | `py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6` |

---

## 📜 Verified Live StudioNet Transaction Proofs (v1.3.0)

Every operation below was executed, mined, and finalized by GenLayer validators on StudioNet (Chain ID `61999`):

### 1. Multi-Funder Deposit & Deterministic Settlement Lifecycle (`CLAIM-1`)

| Operation | Participant / Details | Tx Hash / Explorer Link | Finality |
| :--- | :--- | :--- | :--- |
| **Claim Registration** | Factual Assertion registered in `DRAFT` status | [`0x8e206f673d4da22008a2df8efa59465569cd8e3ccbb4d5e0e44316501eaebe1d`](https://explorer-studio.genlayer.com/tx/0x8e206f673d4da22008a2df8efa59465569cd8e3ccbb4d5e0e44316501eaebe1d) | Finalized (Status: 7) |
| **Funder 1 Deposit** | Alice deposits **0.20 GEN** | [`0x707ca0f4d1d22e50b5eb09931337efa37ada52d498fcef07835c13a83e969e78`](https://explorer-studio.genlayer.com/tx/0x707ca0f4d1d22e50b5eb09931337efa37ada52d498fcef07835c13a83e969e78) | Finalized (Status: 7) |
| **Funder 2 Deposit** | Bob deposits **0.10 GEN** (Total Escrow: 0.30 GEN) | [`0x189e0e7ac428ac62e67a21527fd46b3b54d1736f2303fc8a8e7949fabc349c5a`](https://explorer-studio.genlayer.com/tx/0x189e0e7ac428ac62e67a21527fd46b3b54d1736f2303fc8a8e7949fabc349c5a) | Finalized (Status: 7) |
| **Freeze Claim** | Opens 60s timed window with `OPEN_PUBLIC` policy | [`0x6d40ed781f05786b3689f2f27bf6b64ccb223b6af456a818875720dc42f69961`](https://explorer-studio.genlayer.com/tx/0x6d40ed781f05786b3689f2f27bf6b64ccb223b6af456a818875720dc42f69961) | Finalized (Status: 7) |
| **Qualifying Evidence** | Charlie submits `https://example.com` with verbatim quote | [`0x845f3f187dc4268fec625c0c7768c84cdc112042e847af21d39b999272b60852`](https://explorer-studio.genlayer.com/tx/0x845f3f187dc4268fec625c0c7768c84cdc112042e847af21d39b999272b60852) | Finalized (Status: 7) |
| **Validator Consensus Adjudication** | Multi-validator quorum: SHA-256 fingerprint saved, verbatim quote verified, Charlie designated qualifying recipient | [`0xd8c2f4506dcf2608d0fe0476d98118d4111ad163278f849f00bd0a890b9f0f9e`](https://explorer-studio.genlayer.com/tx/0xd8c2f4506dcf2608d0fe0476d98118d4111ad163278f849f00bd0a890b9f0f9e) | Finalized (Status: 7) |
| **Native GEN Settlement Payout** | Genuine GEN transfer via `_Recipient.emit_transfer()` to Charlie: **+0.30 GEN delivered** | [`0x4012d1f3d18626aa61278e06bc1094cdb3dfa816c3d90d7e1a0c0904d5e25f7b`](https://explorer-studio.genlayer.com/tx/0x4012d1f3d18626aa61278e06bc1094cdb3dfa816c3d90d7e1a0c0904d5e25f7b) | Finalized (Status: 7) |

#### Verified Settlement Balance Movement:
- **Charlie Wallet Before Settlement**: `100,000,000,000,000,000 wei` (0.10 GEN)
- **Charlie Wallet After Settlement**: `400,000,000,000,000,000 wei` (0.40 GEN)
- **Net Genuine Payout**: **`+300,000,000,000,000,000 wei` (+0.30 GEN exact delivery)**

---

### 2. Quotation Check Blocks Unsupported Conclusive Outcome (`CLAIM-2`)

Demonstrates that evidence with unverified or fabricated quotations is strictly prevented from receiving conclusive verdicts (`CONFIRMED` or `REFUTED`):

| Operation | Participant / Details | Tx Hash / Explorer Link | Finality |
| :--- | :--- | :--- | :--- |
| **Claim Registration** | Registered in `DRAFT` status | [`0x38d8fecb06a1c69dfb42b62464fcd3942443202521ff732f9ab6d5b0d8998b39`](https://explorer-studio.genlayer.com/tx/0x38d8fecb06a1c69dfb42b62464fcd3942443202521ff732f9ab6d5b0d8998b39) | Finalized (Status: 7) |
| **Freeze Claim** | Opens 60s timed window | [`0xc33e7e5d15ba15449ea2c51f444e62a242e441eb89c7845fea4e5a9ce3cc3703`](https://explorer-studio.genlayer.com/tx/0xc33e7e5d15ba15449ea2c51f444e62a242e441eb89c7845fea4e5a9ce3cc3703) | Finalized (Status: 7) |
| **Fabricated Quote Submission** | Charlie submits quote not present in source page | [`0x80192981ce02262a58703ea12231edeb91a3a0db1b51bb2f80caa5bc55784681`](https://explorer-studio.genlayer.com/tx/0x80192981ce02262a58703ea12231edeb91a3a0db1b51bb2f80caa5bc55784681) | Finalized (Status: 7) |
| **Consensus Adjudication** | Conclusive verdict blocked; downgraded to `INSUFFICIENT_EVIDENCE`; qualifying recipients cleared | [`0x082b8354d8ec7e54d946f2b3e938e6220fddc9b313c21e35e0cdd254fda2f663`](https://explorer-studio.genlayer.com/tx/0x082b8354d8ec7e54d946f2b3e938e6220fddc9b313c21e35e0cdd254fda2f663) | Finalized (Status: 7) |

---

### 3. Multi-Funder Cancellation & Exact Individual Refunds (`CLAIM-3`)

Demonstrates that cancellation or refund **never** sends all funds to the first funder, but accurately returns each contributor's deposited GEN:

| Operation | Participant / Details | Tx Hash / Explorer Link | Finality |
| :--- | :--- | :--- | :--- |
| **Claim Registration** | Registered in `DRAFT` status | [`0x10b26cbf105e21fe6ecbae34f55557ae05568c056b09459ed38b15622d615a2f`](https://explorer-studio.genlayer.com/tx/0x10b26cbf105e21fe6ecbae34f55557ae05568c056b09459ed38b15622d615a2f) | Finalized (Status: 7) |
| **Funder 1 Deposit** | Alice deposits **0.15 GEN** (`150,000,000,000,000,000 wei`) | [`0x5337780c9d085074d21c5ca296ab8b1b82b24a1357c10bb5d684e2da7f7483a0`](https://explorer-studio.genlayer.com/tx/0x5337780c9d085074d21c5ca296ab8b1b82b24a1357c10bb5d684e2da7f7483a0) | Finalized (Status: 7) |
| **Funder 2 Deposit** | Bob deposits **0.10 GEN** (`100,000,000,000,000,000 wei`) | [`0x50a8c9c8dbe64ac6e6285c25f5ad645217279bfebad319c4ce4fd36bae6172a7`](https://explorer-studio.genlayer.com/tx/0x50a8c9c8dbe64ac6e6285c25f5ad645217279bfebad319c4ce4fd36bae6172a7) | Finalized (Status: 7) |
| **Draft Cancellation** | Admin cancels claim; contract executes multi-funder restitution loop | [`0x55314b8aa385959216efd83790959991d7f99b3010e6c3f6dc3fa1d5138866b9`](https://explorer-studio.genlayer.com/tx/0x55314b8aa385959216efd83790959991d7f99b3010e6c3f6dc3fa1d5138866b9) | Finalized (Status: 7) |

#### Exact Individual Restitution Proof:
- **Alice Refund Delta**: `+150,000,000,000,000,000 wei` (**+0.15 GEN exact refund**)
- **Bob Refund Delta**: `+100,000,000,000,000,000 wei` (**+0.10 GEN exact refund**)

---

### 4. Failed-Transfer Recovery Pattern

- Un-transferred balances resulting from any failed native push transfer are safely captured in `pending_recoveries: TreeMap[str, u256]`.
- Enforces pull-recovery via `recover_failed_transfer(recipient)` and public inspection via `get_pending_recovery(recipient)`.
- Verified in Direct Mode Test 16 and live StudioNet verification.

---

## 🧪 Executable Behavioral Test Suite (18 Tests, 100% Pass)

Run with `python -m pytest tests/test_direct_gen_state.py -v`:

```
============================= test session starts =============================
platform win32 -- Python 3.13.7, pytest-8.4.2, pluggy-1.6.0
collected 18 items

tests/test_direct_gen_state.py::test_access_control_freeze_and_cancel PASSED [  5%]
tests/test_direct_gen_state.py::test_reference_date_validation PASSED        [ 11%]
tests/test_direct_gen_state.py::test_evidence_window_deadlines PASSED        [ 16%]
tests/test_direct_gen_state.py::test_multi_funder_accounting_and_individual_draft_refunds PASSED [ 22%]
tests/test_direct_gen_state.py::test_multi_funder_inconclusive_adjudication_refunds PASSED [ 27%]
tests/test_direct_gen_state.py::test_deterministic_reward_eligibility_and_settlement PASSED [ 33%]
tests/test_direct_gen_state.py::test_fingerprint_persistence_and_quotation_verification PASSED [ 38%]
tests/test_direct_gen_state.py::test_apex_domain_publisher_independence_enforcement PASSED [ 44%]
tests/test_direct_gen_state.py::test_official_registry_policy_enforcement PASSED [ 50%]
tests/test_direct_gen_state.py::test_regulatory_filing_policy_enforcement PASSED [ 55%]
tests/test_direct_gen_state.py::test_conflicting_observations_consensus PASSED [ 61%]
tests/test_direct_gen_state.py::test_malformed_llm_response_handling PASSED     [ 66%]
tests/test_direct_gen_state.py::test_all_sources_unreachable_resolves_source_unavailable PASSED [ 72%]
tests/test_direct_gen_state.py::test_refuted_verdict_bounty_settlement PASSED   [ 77%]
tests/test_direct_gen_state.py::test_validator_disagreement_rolls_back_safely PASSED [ 83%]
tests/test_direct_gen_state.py::test_failed_transfer_recovery_mechanism PASSED  [ 88%]
tests/test_direct_gen_state.py::test_unsupported_conclusive_outcome_blocked_by_quotation_check PASSED [ 94%]
tests/test_direct_gen_state.py::test_unsupported_conclusive_outcome_blocked_by_mirror_source_check PASSED [100%]

============================= 18 passed in 1.05s ==============================
```

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
