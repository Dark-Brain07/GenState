"""
GenState StudioNet Deployment Pipeline.
Automates deployment of the GenState intelligent contract to GenLayer StudioNet,
waits for validator consensus and finality, tests view methods, and outputs receipt.
"""

from __future__ import annotations
import json
import os
import sys
import time
from pathlib import Path

try:
    import genlayer_py as gl
    from genlayer_py.chains import studionet
    from genlayer_py.types import TransactionStatus
except ImportError:
    print("Error: genlayer-py is required. Run: pip install genlayer-py")
    sys.exit(1)


def main():
    root = Path(__file__).resolve().parents[1]
    contract_path = root / "contracts" / "gen_state.py"

    if not contract_path.exists():
        print(f"Error: Contract not found at {contract_path}")
        sys.exit(1)

    print("=" * 70, flush=True)
    print("  GENSTATE INTELLIGENT CONTRACT - STUDIONET DEPLOYMENT PIPELINE  ", flush=True)
    print("=" * 70, flush=True)

    # 1. Setup Deployer Account
    raw_key = os.environ.get("DEPLOYER_PRIVATE_KEY", "").strip()
    if raw_key:
        account = gl.create_account(raw_key if raw_key.startswith("0x") else f"0x{raw_key}")
        print(f"Using configured account from DEPLOYER_PRIVATE_KEY: {account.address}", flush=True)
    else:
        account = gl.create_account()
        print(f"Generated fresh deployment account: {account.address}", flush=True)

    client = gl.create_client(chain=studionet, account=account)

    # 2. Check and Fund Balance
    balance = client.get_balance(account.address)
    print(f"Initial Account Balance: {balance} wei", flush=True)
    if balance < 10**17:
        print("Requesting testnet funds via StudioNet faucet...", flush=True)
        try:
            client.fund_account(account.address, 10**18)
            time.sleep(3)
            balance = client.get_balance(account.address)
            print(f"Updated Account Balance: {balance} wei (1 GEN)", flush=True)
        except Exception as e:
            print(f"Faucet note: {e}", flush=True)

    # 3. Read contract code
    contract_code = contract_path.read_text(encoding="utf-8")
    print("\nDeploying GenState intelligent contract to StudioNet...", flush=True)

    try:
        tx_hash = client.deploy_contract(code=contract_code, args=[])
        print(f"Deployment Transaction Hash: {tx_hash}", flush=True)
        print("Waiting for GenLayer validator consensus and finality (interval: 3s)...", flush=True)

        receipt = client.wait_for_transaction_receipt(
            transaction_hash=tx_hash,
            status=TransactionStatus.FINALIZED,
            interval=3000,
            retries=90,
        )

        print("\n" + "=" * 70, flush=True)
        print("  DEPLOYMENT FINALIZED SUCCESSFULLY!  ", flush=True)
        print("=" * 70, flush=True)

        # Extract address safely
        contract_address = None
        if isinstance(receipt, dict):
            contract_address = (
                receipt.get("data", {}).get("contract_address")
                or receipt.get("contract_address")
            )
        elif hasattr(receipt, "contract_address"):
            contract_address = receipt.contract_address

        if not contract_address and isinstance(receipt, dict) and "data" in receipt:
            contract_address = receipt["data"].get("address")

        print(f"Deployed Contract Address: {contract_address}")
        print(f"Transaction Hash:          {tx_hash}")
        explorer_url = f"https://explorer-studio.genlayer.com/address/{contract_address}"
        print(f"Explorer Studio Link:      {explorer_url}")

        # 4. Save deployment metadata
        deploy_meta = {
            "network": "studionet",
            "chain_id": studionet.id,
            "contract_name": "GenState",
            "contract_address": contract_address,
            "deploy_tx_hash": tx_hash,
            "deployer_address": account.address,
            "explorer_url": explorer_url,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }

        docs_dir = root / "docs"
        docs_dir.mkdir(exist_ok=True)
        meta_file = docs_dir / "deployment.json"
        meta_file.write_text(json.dumps(deploy_meta, indent=2), encoding="utf-8")
        print(f"Saved deployment metadata to {meta_file}")

        # 5. Verify View Call on live deployed contract
        print("\nVerifying live contract via read_contract...")
        try:
            stats = client.read_contract(
                address=contract_address,
                function_name="get_protocol_stats",
                args=[],
            )
            print(f"Verified Live Protocol Stats: {stats}")
        except Exception as err:
            print(f"Read contract note: {err}")

        return deploy_meta

    except Exception as e:
        print(f"\nDeployment error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
