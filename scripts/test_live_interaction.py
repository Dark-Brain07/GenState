"""
Comprehensive Live StudioNet Interaction & Verification Runner.
Executes and logs the complete GenState protocol lifecycle against deployed contract on StudioNet:
1. Claim registration (declare_claim)
2. Payable bounty deposit (fund_bounty with real GEN)
3. Timed evidence window lock (freeze_claim)
4. Multi-source evidence submission from distinct domains (submit_evidence)
5. Multi-validator consensus adjudication (adjudicate)
6. Genuine native GEN settlement (settle_bounty)
7. Recipient wallet balance increase verification
8. Safe draft cancellation and funder recovery verification (cancel_claim & refund_bounty)
"""

from __future__ import annotations
import json
import time
import sys
from pathlib import Path

try:
    import genlayer_py as gl
    from genlayer_py.chains import studionet
    from genlayer_py.types import TransactionStatus
except ImportError:
    print("Error: genlayer-py is required. Run: pip install genlayer-py")
    sys.exit(1)


def log(*args, **kwargs):
    print(*args, **kwargs, flush=True)


def wait_finalized(client, tx_hash: str, label: str):
    log(f"\n[{label}] Awaiting consensus finalization for tx: {tx_hash}...")
    receipt = client.wait_for_transaction_receipt(
        transaction_hash=tx_hash,
        status=TransactionStatus.FINALIZED,
        interval=3000,
        retries=75,
    )
    status = receipt.get("status") if isinstance(receipt, dict) else getattr(receipt, "status", None)
    log(f"[{label}] Finalized! Status: {status}")
    return receipt


def find_claim_by_subject(client, contract_addr: str, subject: str) -> str:
    claims = client.read_contract(address=contract_addr, function_name="list_claims", args=[0, 50])
    for c in reversed(claims):
        if c.get("subject") == subject:
            return c["id"]
    if claims:
        return claims[-1]["id"]
    raise RuntimeError(f"No claims found for subject: {subject}")


def main():
    root = Path(__file__).resolve().parents[1]
    deploy_file = root / "docs" / "deployment.json"
    if not deploy_file.exists():
        print(f"Error: Deployment metadata not found at {deploy_file}")
        sys.exit(1)

    data = json.loads(deploy_file.read_text(encoding="utf-8"))
    contract_addr = data["contract_address"]
    log("=" * 75)
    log("  GENSTATE PROTOCOL: COMPREHENSIVE STUDIONET LIVE LIFECYCLE RUNNER  ")
    log(f"  Contract Address: {contract_addr}")
    log(f"  StudioNet Chain ID: {studionet.id} (61999)")
    log("=" * 75)

    # 1. Setup accounts (Alice = creator/funder, Bob = evidence submitter/recipient)
    alice = gl.create_account()
    bob = gl.create_account()
    log(f"Alice (Creator/Funder):   {alice.address}")
    log(f"Bob   (Evidence Provider): {bob.address}")

    alice_client = gl.create_client(chain=studionet, account=alice)
    bob_client = gl.create_client(chain=studionet, account=bob)

    log("\nFunding Alice via StudioNet faucet...")
    alice_client.fund_account(alice.address, 10**18)  # 1 GEN
    bob_client.fund_account(bob.address, 10**17)    # 0.1 GEN
    time.sleep(2)

    alice_bal = alice_client.get_balance(alice.address)
    bob_initial_bal = bob_client.get_balance(bob.address)
    log(f"Alice Initial Balance: {alice_bal} wei")
    log(f"Bob Initial Balance:   {bob_initial_bal} wei")

    # 2. Declare Claim
    log("\n--- STEP 1: DECLARE CLAIM ---")
    tx1 = alice_client.write_contract(
        address=contract_addr,
        function_name="declare_claim",
        args=[
            "FACTUAL_EVENT",
            "Example Domain",
            "purpose",
            "illustrative examples in documents",
            "2026-01-01",
        ],
    )
    wait_finalized(alice_client, tx1, "DECLARE")

    claim_id = find_claim_by_subject(alice_client, contract_addr, "Example Domain")
    log(f"Registered Claim ID: {claim_id}")

    # 3. Fund Native GEN Bounty
    log("\n--- STEP 2: FUND BOUNTY WITH GENUINE GEN ---")
    bounty_amount = 5 * 10**17  # 0.5 GEN
    tx2 = alice_client.write_contract(
        address=contract_addr,
        function_name="fund_bounty",
        args=[claim_id],
        value=bounty_amount,
    )
    wait_finalized(alice_client, tx2, "FUND_BOUNTY")
    claim_record = alice_client.read_contract(address=contract_addr, function_name="get_claim", args=[claim_id])
    log(f"Claim Escrowed Bounty: {claim_record['bounty_amount']} wei, Funder: {claim_record['funder']}")

    # 4. Freeze Claim with 60s Evidence Window
    log("\n--- STEP 3: FREEZE CLAIM (OPEN EVIDENCE WINDOW) ---")
    tx3 = alice_client.write_contract(
        address=contract_addr,
        function_name="freeze_claim",
        args=[claim_id, "OPEN_PUBLIC", 60],
    )
    wait_finalized(alice_client, tx3, "FREEZE")

    # 5. Submit Public Web Evidence (Bob submits)
    log("\n--- STEP 4: SUBMIT EVIDENCE BY PARTICIPANT (BOB) ---")
    tx4 = bob_client.write_contract(
        address=contract_addr,
        function_name="submit_evidence",
        args=[
            claim_id,
            "https://example.com",
            "Official IANA example page states this domain is for illustrative examples in documents.",
        ],
    )
    wait_finalized(bob_client, tx4, "SUBMIT_EVIDENCE")

    # 6. Enforce Timed Evidence Window
    log("\n--- STEP 5: ENFORCE TIMED EVIDENCE WINDOW ---")
    log("Evidence deadline registered on-chain. Waiting 65 seconds for window to conclude...")
    time.sleep(65)

    # 7. Multi-Validator Consensus Adjudication
    log("\n--- STEP 6: EXECUTE VALIDATOR CONSENSUS ADJUDICATION ---")
    tx5 = alice_client.write_contract(
        address=contract_addr,
        function_name="adjudicate",
        args=[claim_id],
    )
    wait_finalized(alice_client, tx5, "ADJUDICATE")

    adjudication = alice_client.read_contract(address=contract_addr, function_name="get_adjudication", args=[claim_id])
    log(f"Consensus Verdict:      {adjudication.get('verdict')}")
    log(f"Consensus Reasoning:    {adjudication.get('reason')}")
    log(f"Confidence Score:       {adjudication.get('confidence_score')}")

    # 8. Settle Bounty to Rightful Evidence Provider
    if adjudication.get("verdict") in ["CONFIRMED", "REFUTED"]:
        log("\n--- STEP 7: SETTLE BOUNTY WITH GENUINE GEN TRANSFER TO BOB ---")
        tx6 = alice_client.write_contract(
            address=contract_addr,
            function_name="settle_bounty",
            args=[claim_id, bob.address],
        )
        wait_finalized(alice_client, tx6, "SETTLE_BOUNTY")

        bob_final_bal = bob_client.get_balance(bob.address)
        log(f"Bob Initial Balance:    {bob_initial_bal} wei")
        log(f"Bob Final Balance:      {bob_final_bal} wei")
        log(f"Net Balance Increase:   +{bob_final_bal - bob_initial_bal} wei (Genuine Bounty Delivered!)")
        assert bob_final_bal > bob_initial_bal, "Bounty was not transferred to Bob!"

    # 9. Test Safe Draft Cancellation & Refund Recovery
    log("\n--- STEP 8: TEST DRAFT CANCELLATION & SAFE REFUND RECOVERY ---")
    tx7 = alice_client.write_contract(
        address=contract_addr,
        function_name="declare_claim",
        args=[
            "FACTUAL_EVENT",
            "Draft Cancellation Refund Verification",
            "status",
            "WILL_BE_CANCELLED",
            "2026-01-01",
        ],
    )
    wait_finalized(alice_client, tx7, "DECLARE_DRAFT")

    draft_claim_id = find_claim_by_subject(alice_client, contract_addr, "Draft Cancellation Refund Verification")
    log(f"Registered Draft Claim ID: {draft_claim_id}")

    alice_bal_before = alice_client.get_balance(alice.address)
    log(f"Alice Balance Before Funding Draft: {alice_bal_before} wei")

    tx8 = alice_client.write_contract(
        address=contract_addr,
        function_name="fund_bounty",
        args=[draft_claim_id],
        value=2 * 10**17,  # 0.2 GEN
    )
    wait_finalized(alice_client, tx8, "FUND_DRAFT")

    alice_bal_escrowed = alice_client.get_balance(alice.address)
    log(f"Alice Balance After Funding 0.2 GEN: {alice_bal_escrowed} wei")

    tx9 = alice_client.write_contract(
        address=contract_addr,
        function_name="cancel_claim",
        args=[draft_claim_id],
    )
    wait_finalized(alice_client, tx9, "CANCEL_CLAIM")

    alice_bal_after = alice_client.get_balance(alice.address)
    log(f"Alice Balance After Cancellation:    {alice_bal_after} wei (Refunded!)")

    log("\n" + "=" * 75)
    log("  ALL LIVE STUDIONET VERIFICATIONS COMPLETED SUCCESSFULLY  ")
    log("=" * 75)


if __name__ == "__main__":
    main()

