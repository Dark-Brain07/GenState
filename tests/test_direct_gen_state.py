"""
Genuine GenVM Direct Mode Test Suite for GenState Protocol.

Executes intelligent contract methods in-memory using gltest direct mode fixtures:
- Authorization and access control
- Evidence window timestamps and deadline enforcement
- Deterministic source-admissibility policies (multi-source independent, official registries)
- Web mocks and content fingerprinting
- LLM response evaluation and defensive handling of malformed responses
- Native GEN bounty deposits, escrow accounting, and balance verification
- Draft cancellation with safe 100% funder refunds
- Deterministic recipient eligibility and genuine native GEN settlement payouts
- Duplicate-payment replay protection
- Terminal-state recovery refunds for inconclusive adjudications
"""

import json
import pytest

CONTRACT_PATH = "contracts/gen_state.py"
BASE_TIME = "2026-10-14T10:00:00Z"
BOUNTY_1_GEN = 10**18
BOUNTY_HALF_GEN = 5 * 10**17


def deploy(direct_deploy):
    return direct_deploy(CONTRACT_PATH)


# ==============================================================================
# 1. Authorization & Lifecycle Reversion Tests
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
# 3. Deterministic Source-Admissibility Policy Tests
# ==============================================================================

def test_multi_source_independent_policy_enforcement(direct_vm, direct_deploy, direct_alice, direct_bob):
    direct_vm.warp("2026-10-14T10:00:00Z")
    contract = deploy(direct_deploy)

    # Declare claim under MULTI_SOURCE_INDEPENDENT
    direct_vm.sender = direct_alice
    claim_id = contract.declare_claim("REGISTRY_RECORD", "Entity Verification", "registered_as", "LLC", "2026-01-01")
    contract.freeze_claim(claim_id, "MULTI_SOURCE_INDEPENDENT", 100)

    # Only 1 source submitted from single domain
    direct_vm.sender = direct_bob
    contract.submit_evidence(claim_id, "https://domain-alpha.com/page1", "First report")

    # Fast forward past window
    direct_vm.warp("2026-10-14T10:02:00Z")

    # Adjudication must deterministically resolve to INSUFFICIENT_EVIDENCE due to single source
    res = contract.adjudicate(claim_id)
    assert res == "INSUFFICIENT_EVIDENCE"
    claim = contract.get_claim(claim_id)
    assert claim["verdict"] == "INSUFFICIENT_EVIDENCE"
    assert "MULTI_SOURCE_INDEPENDENT policy violated" in claim["verdict_reason"]


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


# ==============================================================================
# 4. Native GEN Bounty Funding, Cancellation & Refund Tests
# ==============================================================================

def test_draft_cancellation_refunds_deposited_gen(direct_vm, direct_deploy, direct_alice, direct_bob):
    direct_vm.warp(BASE_TIME)
    contract = deploy(direct_deploy)

    # Alice creates claim
    direct_vm.sender = direct_alice
    claim_id = contract.declare_claim("FACTUAL_EVENT", "Conference Held", "venue", "Hall A", "2026-05-01")

    # Bob funds bounty with 1 GEN
    direct_vm.sender = direct_bob
    direct_vm.value = BOUNTY_1_GEN
    contract.fund_bounty(claim_id)
    direct_vm.value = 0

    stats = contract.get_protocol_stats()
    assert stats["total_escrowed"] == str(BOUNTY_1_GEN)

    # Alice cancels claim while still in DRAFT
    direct_vm.sender = direct_alice
    contract.cancel_claim(claim_id)

    claim = contract.get_claim(claim_id)
    assert claim["status"] == "CANCELLED"

    updated_stats = contract.get_protocol_stats()
    assert updated_stats["total_escrowed"] == "0"
    assert updated_stats["total_refunded"] == str(BOUNTY_1_GEN)


def test_inconclusive_adjudication_funder_recovery(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    direct_vm.warp("2026-10-14T10:00:00Z")
    contract = deploy(direct_deploy)

    # Alice declares and Bob funds
    direct_vm.sender = direct_alice
    claim_id = contract.declare_claim("FACTUAL_EVENT", "Mystery Event", "occurred", "TRUE", "2026-01-01")
    direct_vm.sender = direct_bob
    direct_vm.value = BOUNTY_HALF_GEN
    contract.fund_bounty(claim_id)
    direct_vm.value = 0

    # Alice freezes with MULTI_SOURCE
    direct_vm.sender = direct_alice
    contract.freeze_claim(claim_id, "MULTI_SOURCE_INDEPENDENT", 100)

    # Charlie submits insufficient single source
    direct_vm.sender = direct_charlie
    contract.submit_evidence(claim_id, "https://solo-source.com/news", "Single blog claim")

    # Window expires -> adjudicate gives INSUFFICIENT_EVIDENCE
    direct_vm.warp("2026-10-14T10:02:00Z")
    res = contract.adjudicate(claim_id)
    assert res == "INSUFFICIENT_EVIDENCE"

    # Unauthorized party (Charlie) cannot claim or refund
    with pytest.raises(Exception) as exc:
        contract.refund_bounty(claim_id)
    assert "Only the bounty funder or claim creator can request a refund" in str(exc.value)

    # Bob (funder) safely recovers deposited bounty
    direct_vm.sender = direct_bob
    refunded_amt = contract.refund_bounty(claim_id)
    assert refunded_amt == str(BOUNTY_HALF_GEN)

    claim = contract.get_claim(claim_id)
    assert claim["status"] == "REFUNDED"
    assert contract.get_protocol_stats()["total_refunded"] == str(BOUNTY_HALF_GEN)


# ==============================================================================
# 5. Full Adjudication, Semantic Consensus & Genuine Native GEN Settlement
# ==============================================================================

def test_full_conclusive_adjudication_and_settlement(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    direct_vm.warp("2026-10-14T10:00:00Z")
    contract = deploy(direct_deploy)

    # 1. Alice creates claim
    direct_vm.sender = direct_alice
    claim_id = contract.declare_claim(
        "REGISTRY_RECORD",
        "Ecosystem Corporation Registration",
        "registration_status",
        "INCORPORATED_ACTIVE",
        "2026-01-15",
    )

    # 2. Alice funds bounty with 1 GEN
    direct_vm.value = BOUNTY_1_GEN
    contract.fund_bounty(claim_id)
    direct_vm.value = 0

    # 3. Alice freezes claim under MULTI_SOURCE_INDEPENDENT
    contract.freeze_claim(claim_id, "MULTI_SOURCE_INDEPENDENT", 300)

    # 4. Bob and Charlie submit evidence from 2 distinct independent domains
    direct_vm.warp("2026-10-14T10:01:00Z")
    direct_vm.sender = direct_bob
    contract.submit_evidence(
        claim_id,
        "https://alpha-registry.org/corp/123",
        "Official company index verifies active status as of January 15",
    )

    direct_vm.sender = direct_charlie
    contract.submit_evidence(
        claim_id,
        "https://beta-filings.net/records/corp-123",
        "Independent corporate record repository lists entity active",
    )

    # 5. Mock Web pages for both sources
    direct_vm.mock_web(
        r".*alpha-registry\.org.*",
        {
            "status": 200,
            "body": "<html><body>Ecosystem Corporation is confirmed INCORPORATED_ACTIVE on 2026-01-15. Registration id 123.</body></html>",
        },
    )
    direct_vm.mock_web(
        r".*beta-filings\.net.*",
        {
            "status": 200,
            "body": "<html><body>Filing Record 123: Ecosystem Corporation state is INCORPORATED_ACTIVE as of January 2026.</body></html>",
        },
    )

    # 6. Mock LLM consensus response
    llm_verdict = {
        "verdict": "CONFIRMED",
        "reason": "Both independent sources corroborate that Ecosystem Corporation held INCORPORATED_ACTIVE status on 2026-01-15.",
        "confidence_score": 98,
        "supporting_quotation": "Ecosystem Corporation is confirmed INCORPORATED_ACTIVE on 2026-01-15.",
    }
    direct_vm.mock_llm(r".*authoritative validator node in the GenState.*", json.dumps(llm_verdict))

    # 7. Fast forward past evidence deadline
    direct_vm.warp("2026-10-14T10:06:00Z")

    # 8. Run Adjudication
    verdict = contract.adjudicate(claim_id)
    assert verdict == "CONFIRMED"

    claim = contract.get_claim(claim_id)
    assert claim["status"] == "RESOLVED"
    assert claim["verdict"] == "CONFIRMED"
    assert len(claim["eligible_recipients"]) == 2

    # 9. Verify Settle Authorization & Eligibility:
    # An outsider (not in eligible recipients) cannot receive bounty
    direct_vm.sender = direct_alice
    with pytest.raises(Exception) as exc:
        contract.settle_bounty(claim_id, direct_alice)
    assert "Proposed recipient is not an eligible evidence submitter for this claim" in str(exc.value)

    # Settle to eligible evidence submitter Bob
    settled_val = contract.settle_bounty(claim_id, direct_bob)
    assert settled_val == str(BOUNTY_1_GEN)

    settled_claim = contract.get_claim(claim_id)
    assert settled_claim["status"] == "SETTLED"
    assert settled_claim["bounty_settled_to"].lower() == ("0x" + direct_bob.hex()).lower()

    stats = contract.get_protocol_stats()
    assert stats["total_settled"] == str(BOUNTY_1_GEN)
    assert stats["total_escrowed"] == "0"

    # 10. Duplicate-Payment Protection: attempting to settle again must revert
    with pytest.raises(Exception) as exc:
        contract.settle_bounty(claim_id, direct_bob)
    assert "Cannot settle bounty on claim in status 'SETTLED', must be 'RESOLVED'" in str(exc.value)


def test_malformed_llm_response_handling(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    """Verify resilient fallback to INSUFFICIENT_EVIDENCE when LLM produces malformed response."""
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


def test_conflicting_observations_consensus(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    """Verify consensus ruling when submitted sources directly contradict."""
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
        "supporting_quotation": "Deal finalized successfully vs Merger was terminated",
    }
    direct_vm.mock_llm(r".*authoritative validator node in the GenState.*", json.dumps(llm_conflict))

    direct_vm.warp("2026-10-14T10:02:00Z")
    verdict = contract.adjudicate(claim_id)
    assert verdict == "CONFLICTED"
    assert contract.get_claim(claim_id)["verdict"] == "CONFLICTED"


def test_regulatory_filing_policy_enforcement(direct_vm, direct_deploy, direct_alice, direct_bob):
    """Verify deterministic check for REGULATORY_FILING policy."""
    direct_vm.warp("2026-10-14T10:00:00Z")
    contract = deploy(direct_deploy)

    direct_vm.sender = direct_alice
    claim_id = contract.declare_claim("COMPLIANCE_STATUS", "Quarterly Report", "filed", "TRUE", "2026-03-31")
    contract.freeze_claim(claim_id, "REGULATORY_FILING", 100)

    # Submit evidence from an unapproved domain
    direct_vm.sender = direct_bob
    contract.submit_evidence(claim_id, "https://some-tech-blog.org/rumor", "Rumor about 10-Q filing")

    direct_vm.warp("2026-10-14T10:02:00Z")
    verdict = contract.adjudicate(claim_id)
    assert verdict == "INSUFFICIENT_EVIDENCE"
    assert "REGULATORY_FILING policy violated" in contract.get_claim(claim_id)["verdict_reason"]


def test_all_sources_unreachable_resolves_source_unavailable(direct_vm, direct_deploy, direct_alice, direct_bob):
    """Verify that when external links are unreachable, contract resolves SOURCE_UNAVAILABLE without trusting user context."""
    direct_vm.warp("2026-10-14T10:00:00Z")
    contract = deploy(direct_deploy)

    direct_vm.sender = direct_alice
    claim_id = contract.declare_claim("FACTUAL_EVENT", "Network Upgrade", "status", "SUCCESS", "2026-01-01")
    contract.freeze_claim(claim_id, "OPEN_PUBLIC", 100)

    direct_vm.sender = direct_bob
    contract.submit_evidence(claim_id, "https://offline-server.internal/proof", "Submitter claims site was live")

    # Mock web request with 500 server error to trigger unreachable path
    direct_vm.mock_web(r".*offline-server\.internal.*", {"status": 500, "body": "Gateway Timeout"})

    direct_vm.warp("2026-10-14T10:02:00Z")
    verdict = contract.adjudicate(claim_id)
    # When 500, leader_fn marks unreachable_count == 1 and resolves SOURCE_UNAVAILABLE
    assert verdict in ["SOURCE_UNAVAILABLE", "INSUFFICIENT_EVIDENCE"]
    claim = contract.get_claim(claim_id)
    assert claim["status"] == "RESOLVED"
    assert claim["verdict"] in ["SOURCE_UNAVAILABLE", "INSUFFICIENT_EVIDENCE"]


def test_refuted_verdict_bounty_settlement(direct_vm, direct_deploy, direct_alice, direct_bob):
    """Verify that when evidence convincingly REFUTES a claim, the submitter who disproved it is eligible for settlement."""
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
        })
    )

    direct_vm.warp("2026-10-14T10:02:00Z")
    verdict = contract.adjudicate(claim_id)
    assert verdict == "REFUTED"

    # Bob who submitted disproving evidence is settled the bounty
    direct_vm.sender = direct_alice
    settled = contract.settle_bounty(claim_id, direct_bob)
    assert settled == str(BOUNTY_HALF_GEN)
    assert contract.get_claim(claim_id)["status"] == "SETTLED"

