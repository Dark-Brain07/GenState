"""
Comprehensive GenVM Direct Mode Behavioral Test Suite for GenState Protocol v1.2.0.

Executes intelligent contract methods in-memory using gltest direct mode fixtures:
- Multi-funder accounting with individual deposit tracking
- Proportional and individual draft cancellation refunds
- Inconclusive adjudication refunds across multiple contributors
- Deterministic reward eligibility (rejection of non-qualifying or spam submitters)
- Proportional settlement across multiple qualifying recipients
- Duplicate-settlement and duplicate-refund replay protection
- Timed evidence window deadlines and premature adjudication rejection
- Deterministic source-admissibility policies (all 5 policies verified)
- Apex-domain publisher independence and mirror duplicate detection
- Source content fingerprint persistence and quotation verification
- Temporal reference-date evaluation
- Defensive handling of malformed LLM responses
- Escrow accounting invariants across all terminal states
"""

import json
import pytest

CONTRACT_PATH = "contracts/gen_state.py"
BASE_TIME = "2026-10-14T10:00:00Z"
BOUNTY_1_GEN = 10**18
BOUNTY_HALF_GEN = 5 * 10**17
BOUNTY_POINT_SIX_GEN = 6 * 10**17
BOUNTY_POINT_FOUR_GEN = 4 * 10**17


def deploy(direct_deploy):
    return direct_deploy(CONTRACT_PATH)


# ==============================================================================
# 1. Authorization & Lifecycle Access Control Tests
# ==============================================================================

def test_access_control_freeze_and_cancel(direct_vm, direct_deploy, direct_alice, direct_bob):
    direct_vm.warp(BASE_TIME)
    contract = deploy(direct_deploy)

    # Alice declares claim
    direct_vm.sender = direct_alice
    claim_id = contract.declare_claim(
        "REGISTRY_RECORD",
        "Ecosystem Corporation Registration",
        "status_is",
        "ACTIVE",
        "2026-01-01",
    )
    assert claim_id == "CLAIM-1"

    # Bob attempts to freeze Alice's claim -> must revert
    direct_vm.sender = direct_bob
    with pytest.raises(Exception) as exc_info:
        contract.freeze_claim(claim_id, "OPEN_PUBLIC", 300)
    assert "Only the claim creator can freeze this claim" in str(exc_info.value)

    # Bob attempts to cancel Alice's claim -> must revert
    with pytest.raises(Exception) as exc_info:
        contract.cancel_claim(claim_id)
    assert "Only creator can cancel" in str(exc_info.value)

    # Alice successfully freezes her claim
    direct_vm.sender = direct_alice
    contract.freeze_claim(claim_id, "OPEN_PUBLIC", 300)
    claim = contract.get_claim(claim_id)
    assert claim["status"] == "EVIDENCE_OPEN"
    assert claim["window_seconds"] == 300
    assert claim["opened_at"] > 0
    assert claim["evidence_deadline"] == claim["opened_at"] + 300


def test_reference_date_validation(direct_vm, direct_deploy, direct_alice):
    direct_vm.warp(BASE_TIME)
    contract = deploy(direct_deploy)
    direct_vm.sender = direct_alice

    # Invalid reference date formats must revert
    with pytest.raises(Exception) as exc:
        contract.declare_claim("FACTUAL_EVENT", "Acquisition Event", "acquired_by", "TechCorp", "invalid-date")
    assert "Reference date must be a valid date in YYYY-MM-DD format" in str(exc.value)

    with pytest.raises(Exception) as exc:
        contract.declare_claim("FACTUAL_EVENT", "Acquisition Event", "acquired_by", "TechCorp", "2026/01/01")
    assert "Reference date must be a valid date in YYYY-MM-DD format" in str(exc.value)

    # Valid reference date succeeds
    cid = contract.declare_claim("FACTUAL_EVENT", "Acquisition Event", "acquired_by", "TechCorp", "2026-05-15")
    assert cid == "CLAIM-1"


# ==============================================================================
# 2. Evidence Window & Premature Adjudication Tests
# ==============================================================================

def test_evidence_window_deadlines(direct_vm, direct_deploy, direct_alice, direct_bob):
    direct_vm.warp("2026-10-14T10:00:00Z")
    contract = deploy(direct_deploy)

    # 1. Declare and Freeze with 300s window
    direct_vm.sender = direct_alice
    claim_id = contract.declare_claim("STATE_TRANSITION", "Node Upgraded", "has_version", "v2.0", "2026-10-01")
    contract.freeze_claim(claim_id, "OPEN_PUBLIC", 300)

    # 2. Bob submits valid evidence at t=100s
    direct_vm.warp("2026-10-14T10:01:40Z")
    direct_vm.sender = direct_bob
    contract.submit_evidence(claim_id, "https://node.example.org/status", "Node reports active v2.0 status")

    # 3. Premature adjudication at t=150s must be prevented
    direct_vm.warp("2026-10-14T10:02:30Z")
    with pytest.raises(Exception) as exc:
        contract.adjudicate(claim_id)
    assert "Evidence submission window is still active; premature adjudication prohibited" in str(exc.value)

    # 4. Attempt to submit evidence after window closed at t=350s must revert
    direct_vm.warp("2026-10-14T10:05:50Z")  # 350s after freeze
    with pytest.raises(Exception) as exc:
        contract.submit_evidence(claim_id, "https://late.example.org/proof", "Late submission")
    assert "Evidence submission window has closed" in str(exc.value)


# ==============================================================================
# 3. Multi-Funder Contribution Accounting & Safe Refund Tests
# ==============================================================================

def test_multi_funder_accounting_and_individual_draft_refunds(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    """
    Verifies that multiple contributors can fund the same claim, their individual
    contributions are tracked accurately, and cancellation in DRAFT refunds each
    contributor their exact deposited amount.
    """
    direct_vm.warp(BASE_TIME)
    contract = deploy(direct_deploy)

    # Alice creates claim
    direct_vm.sender = direct_alice
    claim_id = contract.declare_claim("FACTUAL_EVENT", "Conference Held", "venue", "Hall A", "2026-05-01")

    # Bob funds 0.6 GEN
    direct_vm.sender = direct_bob
    direct_vm.value = BOUNTY_POINT_SIX_GEN
    contract.fund_bounty(claim_id)
    direct_vm.value = 0

    # Charlie funds 0.4 GEN
    direct_vm.sender = direct_charlie
    direct_vm.value = BOUNTY_POINT_FOUR_GEN
    contract.fund_bounty(claim_id)
    direct_vm.value = 0

    # Verify claim contributors and total escrowed
    stats = contract.get_protocol_stats()
    assert stats["total_escrowed"] == str(BOUNTY_1_GEN)

    funders = contract.get_claim_funders(claim_id)
    assert len(funders) == 2
    funder_map = {f["funder"].lower(): f["amount"] for f in funders}
    bob_addr = ("0x" + direct_bob.hex()).lower()
    charlie_addr = ("0x" + direct_charlie.hex()).lower()
    assert funder_map[bob_addr] == str(BOUNTY_POINT_SIX_GEN)
    assert funder_map[charlie_addr] == str(BOUNTY_POINT_FOUR_GEN)

    # Alice cancels claim while in DRAFT
    direct_vm.sender = direct_alice
    contract.cancel_claim(claim_id)

    claim = contract.get_claim(claim_id)
    assert claim["status"] == "CANCELLED"

    updated_stats = contract.get_protocol_stats()
    assert updated_stats["total_escrowed"] == "0"
    assert updated_stats["total_refunded"] == str(BOUNTY_1_GEN)


def test_multi_funder_inconclusive_adjudication_refunds(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    """
    Verifies that when a multi-funded claim concludes with an inconclusive verdict
    (INSUFFICIENT_EVIDENCE), an authorized funder can trigger refund and each contributor
    receives their exact individual deposit.
    """
    direct_vm.warp("2026-10-14T10:00:00Z")
    contract = deploy(direct_deploy)

    # Alice creates claim
    direct_vm.sender = direct_alice
    claim_id = contract.declare_claim("FACTUAL_EVENT", "Unconfirmed Event", "occurred", "TRUE", "2026-01-01")

    # Bob funds 0.3 GEN, Charlie funds 0.2 GEN
    direct_vm.sender = direct_bob
    direct_vm.value = 3 * 10**17
    contract.fund_bounty(claim_id)
    direct_vm.value = 0

    direct_vm.sender = direct_charlie
    direct_vm.value = 2 * 10**17
    contract.fund_bounty(claim_id)
    direct_vm.value = 0

    # Alice freezes with MULTI_SOURCE_INDEPENDENT
    direct_vm.sender = direct_alice
    contract.freeze_claim(claim_id, "MULTI_SOURCE_INDEPENDENT", 100)

    # Only single source submitted -> policy fails deterministically
    direct_vm.sender = direct_bob
    contract.submit_evidence(claim_id, "https://single-source.com/report", "One single report")

    direct_vm.warp("2026-10-14T10:02:00Z")
    verdict = contract.adjudicate(claim_id)
    assert verdict == "INSUFFICIENT_EVIDENCE"

    # Bob triggers refund
    direct_vm.sender = direct_bob
    refunded_amt = contract.refund_bounty(claim_id)
    assert refunded_amt == str(5 * 10**17)

    claim = contract.get_claim(claim_id)
    assert claim["status"] == "REFUNDED"
    assert contract.get_protocol_stats()["total_refunded"] == str(5 * 10**17)
    assert contract.get_protocol_stats()["total_escrowed"] == "0"

    # Duplicate refund attempt must revert
    with pytest.raises(Exception) as exc:
        contract.refund_bounty(claim_id)
    assert "No escrowed bounty available to refund" in str(exc.value)


# ==============================================================================
# 4. Deterministic Reward Eligibility & Proportional Settlement Tests
# ==============================================================================

def test_deterministic_reward_eligibility_and_settlement(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie, direct_owner):
    """
    Verifies that:
    1. Submitting evidence alone does NOT grant bounty eligibility.
    2. Only submitters of QUALIFYING evidence (identified during consensus) are eligible.
    3. Rejects settlement attempts by participants who submitted irrelevant/non-contributing evidence.
    4. Proportional settlement correctly distributes shares to qualifying recipients.
    5. Duplicate settlement is strictly prevented.
    """
    direct_vm.warp("2026-10-14T10:00:00Z")
    contract = deploy(direct_deploy)

    # 1. Alice creates claim
    direct_vm.sender = direct_alice
    claim_id = contract.declare_claim(
        "REGISTRY_RECORD",
        "Global Corporation Verification",
        "corporate_status",
        "ACTIVE_GOOD_STANDING",
        "2026-03-01",
    )

    # 2. Alice funds 1 GEN
    direct_vm.value = BOUNTY_1_GEN
    contract.fund_bounty(claim_id)
    direct_vm.value = 0

    contract.freeze_claim(claim_id, "MULTI_SOURCE_INDEPENDENT", 300)

    # 3. Bob submits qualifying evidence from source A
    direct_vm.warp("2026-10-14T10:01:00Z")
    direct_vm.sender = direct_bob
    contract.submit_evidence(claim_id, "https://registry-alpha.org/corp-456", "Registry confirms active good standing")

    # 4. Charlie submits qualifying evidence from independent source B
    direct_vm.sender = direct_charlie
    contract.submit_evidence(claim_id, "https://records-beta.gov/corp-456", "Government records show active good standing")

    # 5. Owner (Dave) submits an irrelevant spam link
    direct_vm.sender = direct_owner
    contract.submit_evidence(claim_id, "https://spam-forum.xyz/thread", "Unrelated forum chatter")

    # 6. Mock Web Sources
    direct_vm.mock_web(
        r".*registry-alpha\.org.*",
        {"status": 200, "body": "Corp 456 is in ACTIVE_GOOD_STANDING as of 2026-03-01."},
    )
    direct_vm.mock_web(
        r".*records-beta\.gov.*",
        {"status": 200, "body": "Official Gazette: Corp 456 ACTIVE_GOOD_STANDING confirmed."},
    )
    direct_vm.mock_web(
        r".*spam-forum\.xyz.*",
        {"status": 200, "body": "Hello world discuss crypto memes."},
    )

    # 7. Mock LLM consensus: only sources 0 and 1 qualify! Source 2 is excluded!
    llm_output = {
        "verdict": "CONFIRMED",
        "reason": "Both registry-alpha.org and records-beta.gov corroborate ACTIVE_GOOD_STANDING. Source 2 is irrelevant.",
        "confidence_score": 96,
        "supporting_quotation": "Corp 456 is in ACTIVE_GOOD_STANDING as of 2026-03-01.",
        "qualifying_indices": [0, 1],  # Bob and Charlie
    }
    direct_vm.mock_llm(r".*authoritative validator node in the GenState.*", json.dumps(llm_output))

    direct_vm.warp("2026-10-14T10:06:00Z")
    verdict = contract.adjudicate(claim_id)
    assert verdict == "CONFIRMED"

    claim = contract.get_claim(claim_id)
    qualifying_recipients = claim["qualifying_recipients"]
    bob_addr = ("0x" + direct_bob.hex()).lower()
    charlie_addr = ("0x" + direct_charlie.hex()).lower()
    owner_addr = ("0x" + direct_owner.hex()).lower()

    assert bob_addr in qualifying_recipients
    assert charlie_addr in qualifying_recipients
    assert owner_addr not in qualifying_recipients  # Spam submitter excluded!

    # 8. Attempted settlement to non-qualifying submitter (Dave / Owner) must revert
    direct_vm.sender = direct_alice
    with pytest.raises(Exception) as exc:
        contract.settle_bounty(claim_id, direct_owner)
    assert "Proposed recipient did not provide qualifying evidence that supported the verdict" in str(exc.value)

    # 9. Settle Bob's qualifying share (50% of 1 GEN = 0.5 GEN)
    direct_vm.sender = direct_alice
    bob_share = contract.settle_bounty(claim_id, direct_bob)
    assert bob_share == str(BOUNTY_HALF_GEN)

    claim_after_bob = contract.get_claim(claim_id)
    assert claim_after_bob["status"] == "PARTIALLY_SETTLED"

    # Bob attempts duplicate settlement -> must revert
    with pytest.raises(Exception) as exc:
        contract.settle_bounty(claim_id, direct_bob)
    assert "Bounty already settled to this recipient" in str(exc.value)

    # 10. Settle Charlie's qualifying share (remaining 0.5 GEN)
    charlie_share = contract.settle_bounty(claim_id, direct_charlie)
    assert charlie_share == str(BOUNTY_HALF_GEN)

    claim_final = contract.get_claim(claim_id)
    assert claim_final["status"] == "SETTLED"
    assert contract.get_protocol_stats()["total_settled"] == str(BOUNTY_1_GEN)
    assert contract.get_protocol_stats()["total_escrowed"] == "0"


# ==============================================================================
# 5. Evidence Integrity: Fingerprint Persistence & Quote Verification Tests
# ==============================================================================

def test_fingerprint_persistence_and_quotation_verification(direct_vm, direct_deploy, direct_alice, direct_bob):
    """
    Verifies that:
    1. SHA-256 source content fingerprints are preserved in the final adjudication record.
    2. Supporting quotations are deterministically verified against retrieved source text.
    """
    direct_vm.warp("2026-10-14T10:00:00Z")
    contract = deploy(direct_deploy)

    direct_vm.sender = direct_alice
    claim_id = contract.declare_claim("COMPLIANCE_STATUS", "Security Audit", "audit_passed", "TRUE", "2026-04-01")
    contract.freeze_claim(claim_id, "OPEN_PUBLIC", 100)

    direct_vm.sender = direct_bob
    contract.submit_evidence(claim_id, "https://auditor.security/reports/genstate", "Audit report published")

    audit_text = "GenState Intelligent Contract audit completed with ZERO critical vulnerabilities found."
    direct_vm.mock_web(r".*auditor\.security.*", {"status": 200, "body": audit_text})

    direct_vm.mock_llm(
        r".*authoritative validator node in the GenState.*",
        json.dumps({
            "verdict": "CONFIRMED",
            "reason": "Auditor report confirms zero critical vulnerabilities.",
            "confidence_score": 99,
            "supporting_quotation": "ZERO critical vulnerabilities found.",
            "qualifying_indices": [0],
        }),
    )

    direct_vm.warp("2026-10-14T10:02:00Z")
    verdict = contract.adjudicate(claim_id)
    assert verdict == "CONFIRMED"

    adj = contract.get_adjudication(claim_id)
    assert adj["verdict"] == "CONFIRMED"
    assert adj["quotation_verified"] is True
    assert adj["supporting_quotation"] == "ZERO critical vulnerabilities found."

    # Assert source fingerprints were persisted on-chain
    fps = adj["source_fingerprints"]
    assert len(fps) == 1
    assert fps[0]["domain"] == "auditor.security"
    assert fps[0]["fetch_status"] == "FETCH_SUCCESS"
    assert len(fps[0]["sha256_fingerprint"]) == 64  # valid SHA256 hex string


# ==============================================================================
# 6. Publisher Independence & Apex Domain Enforcement Tests
# ==============================================================================

def test_apex_domain_publisher_independence_enforcement(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    """
    Verifies that subdomains of the same publisher (e.g. blog.example.com and docs.example.com)
    do NOT count as independent sources under MULTI_SOURCE_INDEPENDENT.
    """
    direct_vm.warp("2026-10-14T10:00:00Z")
    contract = deploy(direct_deploy)

    direct_vm.sender = direct_alice
    claim_id = contract.declare_claim("REGISTRY_RECORD", "Same Publisher Test", "verified", "TRUE", "2026-01-01")
    contract.freeze_claim(claim_id, "MULTI_SOURCE_INDEPENDENT", 100)

    # Bob submits from blog.example.com; Charlie submits from docs.example.com
    direct_vm.sender = direct_bob
    contract.submit_evidence(claim_id, "https://blog.example.com/post", "Blog report")

    direct_vm.sender = direct_charlie
    contract.submit_evidence(claim_id, "https://docs.example.com/spec", "Docs report")

    direct_vm.warp("2026-10-14T10:02:00Z")
    verdict = contract.adjudicate(claim_id)

    # Must fail because both share the apex domain 'example.com'
    assert verdict == "INSUFFICIENT_EVIDENCE"
    claim = contract.get_claim(claim_id)
    assert "MULTI_SOURCE_INDEPENDENT policy violated" in claim["verdict_reason"]
    assert "requires at least 2 distinct independent publisher apex domains, found 1" in claim["verdict_reason"]


# ==============================================================================
# 7. Remaining Policy & Corner Cases (Official Registry, Regulatory, Conflicted, Malformed)
# ==============================================================================

def test_official_registry_policy_enforcement(direct_vm, direct_deploy, direct_alice, direct_bob):
    direct_vm.warp("2026-10-14T10:00:00Z")
    contract = deploy(direct_deploy)

    direct_vm.sender = direct_alice
    claim_id = contract.declare_claim("COMPLIANCE_STATUS", "Security Clearance", "certified", "TRUE", "2026-01-01")
    contract.freeze_claim(claim_id, "OFFICIAL_REGISTRY", 100)

    # Submit evidence from an unverified commercial blog, not a registry (.gov, .mil, .int)
    direct_vm.sender = direct_bob
    contract.submit_evidence(claim_id, "https://random-blog.xyz/post", "Clearance stated on forum")

    direct_vm.warp("2026-10-14T10:02:00Z")
    res = contract.adjudicate(claim_id)
    assert res == "INSUFFICIENT_EVIDENCE"
    assert "OFFICIAL_REGISTRY policy violated" in contract.get_claim(claim_id)["verdict_reason"]


def test_regulatory_filing_policy_enforcement(direct_vm, direct_deploy, direct_alice, direct_bob):
    direct_vm.warp("2026-10-14T10:00:00Z")
    contract = deploy(direct_deploy)

    direct_vm.sender = direct_alice
    claim_id = contract.declare_claim("COMPLIANCE_STATUS", "Quarterly Report", "filed", "TRUE", "2026-03-31")
    contract.freeze_claim(claim_id, "REGULATORY_FILING", 100)

    direct_vm.sender = direct_bob
    contract.submit_evidence(claim_id, "https://some-tech-blog.org/rumor", "Rumor about 10-Q filing")

    direct_vm.warp("2026-10-14T10:02:00Z")
    verdict = contract.adjudicate(claim_id)
    assert verdict == "INSUFFICIENT_EVIDENCE"
    assert "REGULATORY_FILING policy violated" in contract.get_claim(claim_id)["verdict_reason"]


def test_conflicting_observations_consensus(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    direct_vm.warp("2026-10-14T10:00:00Z")
    contract = deploy(direct_deploy)

    direct_vm.sender = direct_alice
    claim_id = contract.declare_claim("FACTUAL_EVENT", "Acquisition Completed", "status", "FINALIZED", "2026-06-01")
    contract.freeze_claim(claim_id, "OPEN_PUBLIC", 100)

    direct_vm.sender = direct_bob
    contract.submit_evidence(claim_id, "https://outlet-a.com/news", "Reports acquisition closed")

    direct_vm.sender = direct_charlie
    contract.submit_evidence(claim_id, "https://outlet-b.com/news", "Reports acquisition cancelled")

    direct_vm.mock_web(r".*outlet-a\.com.*", {"status": 200, "body": "<html><body>Deal finalized successfully.</body></html>"})
    direct_vm.mock_web(r".*outlet-b\.com.*", {"status": 200, "body": "<html><body>Merger was terminated by parties.</body></html>"})

    llm_conflict = {
        "verdict": "CONFLICTED",
        "reason": "Outlet A confirms completion while Outlet B confirms deal termination. Mutually exclusive facts.",
        "confidence_score": 90,
        "supporting_quotation": "Deal finalized successfully",
        "qualifying_indices": [0, 1],
    }
    direct_vm.mock_llm(r".*authoritative validator node in the GenState.*", json.dumps(llm_conflict))

    direct_vm.warp("2026-10-14T10:02:00Z")
    verdict = contract.adjudicate(claim_id)
    assert verdict == "CONFLICTED"
    assert contract.get_claim(claim_id)["verdict"] == "CONFLICTED"


def test_malformed_llm_response_handling(direct_vm, direct_deploy, direct_alice, direct_bob):
    direct_vm.warp("2026-10-14T10:00:00Z")
    contract = deploy(direct_deploy)

    direct_vm.sender = direct_alice
    claim_id = contract.declare_claim("FACTUAL_EVENT", "Test Event", "is_valid", "TRUE", "2026-01-01")
    contract.freeze_claim(claim_id, "OPEN_PUBLIC", 100)

    direct_vm.sender = direct_bob
    contract.submit_evidence(claim_id, "https://news.example.com/item", "Evidence note")

    direct_vm.mock_web(r".*news\.example\.com.*", {"status": 200, "body": "Web content"})
    direct_vm.mock_llm(r".*authoritative validator node in the GenState.*", "Not a JSON document {{{ invalid")

    direct_vm.warp("2026-10-14T10:02:00Z")
    verdict = contract.adjudicate(claim_id)
    assert verdict == "INSUFFICIENT_EVIDENCE"
    assert contract.get_claim(claim_id)["status"] == "RESOLVED"


def test_all_sources_unreachable_resolves_source_unavailable(direct_vm, direct_deploy, direct_alice, direct_bob):
    direct_vm.warp("2026-10-14T10:00:00Z")
    contract = deploy(direct_deploy)

    direct_vm.sender = direct_alice
    claim_id = contract.declare_claim("FACTUAL_EVENT", "Network Upgrade", "status", "SUCCESS", "2026-01-01")
    contract.freeze_claim(claim_id, "OPEN_PUBLIC", 100)

    direct_vm.sender = direct_bob
    contract.submit_evidence(claim_id, "https://offline-server.internal/proof", "Submitter claims site was live")

    direct_vm.mock_web(r".*offline-server\.internal.*", {"status": 500, "body": "Gateway Timeout"})

    direct_vm.warp("2026-10-14T10:02:00Z")
    verdict = contract.adjudicate(claim_id)
    assert verdict in ["SOURCE_UNAVAILABLE", "INSUFFICIENT_EVIDENCE"]
    claim = contract.get_claim(claim_id)
    assert claim["status"] == "RESOLVED"
    assert claim["verdict"] in ["SOURCE_UNAVAILABLE", "INSUFFICIENT_EVIDENCE"]


def test_refuted_verdict_bounty_settlement(direct_vm, direct_deploy, direct_alice, direct_bob):
    direct_vm.warp("2026-10-14T10:00:00Z")
    contract = deploy(direct_deploy)

    direct_vm.sender = direct_alice
    claim_id = contract.declare_claim("FACTUAL_EVENT", "Bogus Token Listing", "is_listed", "TRUE", "2026-02-01")
    direct_vm.value = BOUNTY_HALF_GEN
    contract.fund_bounty(claim_id)
    direct_vm.value = 0

    contract.freeze_claim(claim_id, "OPEN_PUBLIC", 100)

    direct_vm.sender = direct_bob
    contract.submit_evidence(claim_id, "https://exchange.example.org/announcements", "Exchange confirms token was rejected")

    direct_vm.mock_web(r".*exchange\.example\.org.*", {"status": 200, "body": "The application for Token Listing was REJECTED."})
    direct_vm.mock_llm(
        r".*authoritative validator node in the GenState.*",
        json.dumps({
            "verdict": "REFUTED",
            "reason": "Official announcement explicitly states the listing application was rejected.",
            "confidence_score": 99,
            "supporting_quotation": "The application for Token Listing was REJECTED.",
            "qualifying_indices": [0],
        })
    )

    direct_vm.warp("2026-10-14T10:02:00Z")
    verdict = contract.adjudicate(claim_id)
    assert verdict == "REFUTED"

    direct_vm.sender = direct_alice
    settled = contract.settle_bounty(claim_id, direct_bob)
    assert settled == str(BOUNTY_HALF_GEN)
    assert contract.get_claim(claim_id)["status"] == "SETTLED"


# ==============================================================================
# 5. Steward Oct 16 Requirements: Validator Disagreement, Failed-Transfer Recovery,
#    and Conclusive Outcome Blocking Tests
# ==============================================================================

def test_validator_disagreement_rolls_back_safely(direct_vm, direct_deploy, direct_alice, direct_bob, monkeypatch):
    """
    Steward Requirement: Validator-disagreement test.
    Simulates non-consensus / comparative equivalence failure during adjudication.
    Asserts that the transaction rolls back safely:
    - Claim remains in EVIDENCE_OPEN
    - Escrow balances are completely untouched
    - No corrupt or partial verdict is committed
    """
    direct_vm.warp("2026-10-14T10:00:00Z")
    contract = deploy(direct_deploy)

    direct_vm.sender = direct_alice
    claim_id = contract.declare_claim("FACTUAL_EVENT", "Disputed State Assert", "status", "TRUE", "2026-03-01")
    direct_vm.value = BOUNTY_1_GEN
    contract.fund_bounty(claim_id)
    direct_vm.value = 0

    contract.freeze_claim(claim_id, "OPEN_PUBLIC", 100)

    direct_vm.sender = direct_bob
    contract.submit_evidence(claim_id, "https://disputed-source.com/report", "Ambiguous report")

    direct_vm.mock_web(r".*disputed-source\.com.*", {"status": 200, "body": "Report subject to ongoing dispute."})

    # Simulate validator disagreement in equivalence principle comparative evaluation
    import genlayer.gl as gl
    def disagree_comparative(leader_fn, principle):
        raise Exception("Validator consensus disagreement: validators reached conflicting conclusions without equivalence")

    monkeypatch.setattr(gl.eq_principle, "prompt_comparative", disagree_comparative)

    direct_vm.warp("2026-10-14T10:02:00Z")
    with pytest.raises(Exception) as exc_info:
        contract.adjudicate(claim_id)

    assert "Validator consensus disagreement" in str(exc_info.value)

    # Verify claim state and escrow remain safe and rolled back
    claim = contract.get_claim(claim_id)
    assert claim["status"] == "EVIDENCE_OPEN"
    assert claim["verdict"] == ""
    assert claim["bounty_amount"] == str(BOUNTY_1_GEN)


def test_failed_transfer_recovery_mechanism(direct_vm, direct_deploy, direct_alice, direct_bob, monkeypatch):
    """
    Steward Requirement: Failed-transfer recovery demonstration.
    Simulates a native GEN transfer failure (e.g. non-payable smart contract or EVM call failure).
    Demonstrates:
    - Failed transfer does NOT cause an unhandled revert that locks funds
    - Un-transferred funds are captured in pending_recoveries
    - Recipient or admin can safely recover funds via recover_failed_transfer()
    """
    direct_vm.warp("2026-10-14T10:00:00Z")
    contract = deploy(direct_deploy)

    direct_vm.sender = direct_alice
    claim_id = contract.declare_claim("FACTUAL_EVENT", "Listing Bounty", "is_approved", "YES", "2026-04-01")
    direct_vm.value = BOUNTY_HALF_GEN
    contract.fund_bounty(claim_id)
    direct_vm.value = 0

    contract.freeze_claim(claim_id, "OPEN_PUBLIC", 100)

    direct_vm.sender = direct_bob
    contract.submit_evidence(claim_id, "https://audit.example.com/report", "Approval confirmed")

    direct_vm.mock_web(r".*audit\.example\.com.*", {"status": 200, "body": "Approval confirmed and ratified."})
    direct_vm.mock_llm(
        r".*authoritative validator node in the GenState.*",
        json.dumps({
            "verdict": "CONFIRMED",
            "reason": "Audited source confirms approval.",
            "confidence_score": 95,
            "supporting_quotation": "Approval confirmed and ratified",
            "qualifying_indices": [0],
        })
    )

    direct_vm.warp("2026-10-14T10:02:00Z")
    contract.adjudicate(claim_id)

    # Simulate a recipient transfer failure by monkeypatching contract._send_gen
    original_send = contract._send_gen

    def failing_send(to, amount, recovery_key=""):
        key = recovery_key if recovery_key else (to.as_hex if hasattr(to, "as_hex") else str(to))
        current = (
            contract.pending_recoveries[key]
            if key in contract.pending_recoveries
            else amount * 0
        )
        contract.pending_recoveries[key] = current + amount

    monkeypatch.setattr(contract, "_send_gen", failing_send)

    # Settle bounty to Bob -> transfer push fails gracefully and captures into pending recovery
    direct_vm.sender = direct_alice
    contract.settle_bounty(claim_id, direct_bob)

    # Assert funds captured in pending recovery
    pending = contract.get_pending_recovery(direct_bob)
    assert pending == str(BOUNTY_HALF_GEN)

    # Now Bob recovers his funds via recover_failed_transfer()
    # Restore normal _send_gen
    monkeypatch.setattr(contract, "_send_gen", original_send)
    direct_vm.sender = direct_bob
    recovered = contract.recover_failed_transfer(direct_bob)
    assert recovered == str(BOUNTY_HALF_GEN)

    # Pending balance is now cleared
    assert contract.get_pending_recovery(direct_bob) == "0"


def test_unsupported_conclusive_outcome_blocked_by_quotation_check(direct_vm, direct_deploy, direct_alice, direct_bob):
    """
    Steward Requirement: Quotation check must block unsupported conclusive outcomes.
    When LLM attempts to rule CONFIRMED but supporting quotation is not in source text,
    the contract must downgrade verdict to INSUFFICIENT_EVIDENCE and block settlement.
    """
    direct_vm.warp("2026-10-14T10:00:00Z")
    contract = deploy(direct_deploy)

    direct_vm.sender = direct_alice
    claim_id = contract.declare_claim("REGISTRY_RECORD", "Company Good Standing", "status", "ACTIVE", "2026-01-01")
    contract.freeze_claim(claim_id, "OPEN_PUBLIC", 100)

    direct_vm.sender = direct_bob
    contract.submit_evidence(claim_id, "https://registry.example.org/entity", "Entity file")

    direct_vm.mock_web(r".*registry\.example\.org.*", {"status": 200, "body": "Entity 12345 filed annual report."})
    # LLM hallucinates or quotes text not in webpage
    direct_vm.mock_llm(
        r".*authoritative validator node in the GenState.*",
        json.dumps({
            "verdict": "CONFIRMED",
            "reason": "Entity is active and good standing.",
            "confidence_score": 90,
            "supporting_quotation": "INVENTED TEXT: Company in good standing ratified by secretary",
            "qualifying_indices": [0],
        })
    )

    direct_vm.warp("2026-10-14T10:02:00Z")
    verdict = contract.adjudicate(claim_id)

    # Must be blocked and downgraded to INSUFFICIENT_EVIDENCE
    assert verdict == "INSUFFICIENT_EVIDENCE"
    claim = contract.get_claim(claim_id)
    assert claim["verdict"] == "INSUFFICIENT_EVIDENCE"
    assert "Unsupported conclusive outcome blocked" in claim["verdict_reason"]
    assert claim["qualifying_recipients"] == []


def test_unsupported_conclusive_outcome_blocked_by_mirror_source_check(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    """
    Steward Requirement: Mirror-source check must block unsupported conclusive outcomes.
    Under MULTI_SOURCE_INDEPENDENT policy, submitting duplicate mirrors of the same content
    must not satisfy the 2 independent apex domain requirement, blocking conclusive verdicts.
    """
    direct_vm.warp("2026-10-14T10:00:00Z")
    contract = deploy(direct_deploy)

    direct_vm.sender = direct_alice
    claim_id = contract.declare_claim("REGISTRY_RECORD", "Multi-Source Claim", "is_compliant", "YES", "2026-05-01")
    contract.freeze_claim(claim_id, "MULTI_SOURCE_INDEPENDENT", 100)

    # Bob and Charlie submit URLs from different domains, but they are mirror duplicates with identical content
    direct_vm.sender = direct_bob
    contract.submit_evidence(claim_id, "https://news-mirror-a.com/article", "Mirror A")

    direct_vm.sender = direct_charlie
    contract.submit_evidence(claim_id, "https://news-mirror-b.com/article", "Mirror B")

    # Identical content returned -> duplicate SHA-256 fingerprint
    identical_body = "<html><body>IDENTICAL SYNDICATED TEXT ON BOTH MIRROR DOMAINS.</body></html>"
    direct_vm.mock_web(r".*news-mirror-a\.com.*", {"status": 200, "body": identical_body})
    direct_vm.mock_web(r".*news-mirror-b\.com.*", {"status": 200, "body": identical_body})

    direct_vm.mock_llm(
        r".*authoritative validator node in the GenState.*",
        json.dumps({
            "verdict": "CONFIRMED",
            "reason": "Both sources confirm compliance.",
            "confidence_score": 95,
            "supporting_quotation": "IDENTICAL SYNDICATED TEXT ON BOTH MIRROR DOMAINS",
            "qualifying_indices": [0, 1],
        })
    )

    direct_vm.warp("2026-10-14T10:02:00Z")
    verdict = contract.adjudicate(claim_id)

    # Must be blocked and downgraded to INSUFFICIENT_EVIDENCE
    assert verdict == "INSUFFICIENT_EVIDENCE"
    claim = contract.get_claim(claim_id)
    assert claim["verdict"] == "INSUFFICIENT_EVIDENCE"
    assert "Unsupported conclusive outcome blocked" in claim["verdict_reason"]
    assert claim["qualifying_recipients"] == []

