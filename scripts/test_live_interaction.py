"""
Live verification script: interacts with the deployed GenState contract on StudioNet.
"""

from __future__ import annotations
import json
import time
from pathlib import Path
import genlayer_py as gl
from genlayer_py.chains import studionet
from genlayer_py.types import TransactionStatus

def main():
    root = Path(__file__).resolve().parents[1]
    deploy_file = root / "docs" / "deployment.json"
    data = json.loads(deploy_file.read_text(encoding="utf-8"))
    contract_addr = data["contract_address"]
    print(f"Interacting with deployed GenState at: {contract_addr}")

    account = gl.create_account()
    client = gl.create_client(chain=studionet, account=account)
    client.fund_account(account.address, 10**18)
    time.sleep(2)

    print("Declaring initial verifiable claim on-chain...")
    tx = client.write_contract(
        address=contract_addr,
        function_name="declare_claim",
        args=[
            "REGISTRY_RECORD",
            "GenState Protocol Genesis Deployment",
            "is_deployed_on_studionet",
            "Verified Active",
            "2026-10-13",
        ],
    )
    print(f"Transaction Hash: {tx}")
    print("Awaiting finality...")
    receipt = client.wait_for_transaction_receipt(
        transaction_hash=tx,
        status=TransactionStatus.FINALIZED,
        interval=3000,
        retries=60,
    )
    print("Transaction finalized! Status:", receipt.get("status") if isinstance(receipt, dict) else receipt)

if __name__ == "__main__":
    main()
