import { createAccount, createClient, generatePrivateKey } from "genlayer-js";
import { studionet } from "genlayer-js/chains";
import { TransactionStatus } from "genlayer-js/types";
import { GENSTATE_CONFIG } from "./config";
import type {
  StateClaim,
  EvidenceRecord,
  AdjudicationResult,
  ProtocolStats,
} from "../types/genstate";

class LiveGenStateService {
  private readClient: any;
  private client: any = null;
  private account: any = null;
  private connectedType: "studionet" | "browser" | null = null;
  private browserAddress: string = "";

  constructor() {
    this.readClient = createClient({ chain: studionet });
  }

  public isConnected(): boolean {
    return !!this.account || !!this.browserAddress;
  }

  public getAccountAddress(): string {
    return this.browserAddress || this.account?.address || "";
  }

  public getConnectedType(): "studionet" | "browser" | null {
    return this.connectedType;
  }

  /**
   * Request browser wallet to switch to or register GenLayer StudioNet (Chain ID 61999).
   */
  public async switchOrAddStudioNet(): Promise<void> {
    if (typeof window === "undefined" || !(window as any).ethereum) return;
    const ethereum = (window as any).ethereum;
    try {
      await ethereum.request({
        method: "wallet_switchEthereumChain",
        params: [{ chainId: GENSTATE_CONFIG.chainIdHex }], // 0xf22f (61999)
      });
    } catch (switchError: any) {
      if (switchError.code === 4902 || switchError.data?.originalError?.code === 4902) {
        try {
          await ethereum.request({
            method: "wallet_addEthereumChain",
            params: [
              {
                chainId: GENSTATE_CONFIG.chainIdHex,
                chainName: "Genlayer Studio Network",
                nativeCurrency: { name: "GEN Token", symbol: "GEN", decimals: 18 },
                rpcUrls: [GENSTATE_CONFIG.rpcUrl],
                blockExplorerUrls: ["https://explorer-studio.genlayer.com"],
              },
            ],
          });
        } catch (addError) {
          console.warn("Could not register GenLayer StudioNet with wallet:", addError);
        }
      }
    }
  }

  /**
   * Connect wallet on explicit user action.
   * Explicitly configures connected browser wallet provider (EIP-1193 window.ethereum).
   */
  public async connectWallet(
    type: "studionet" | "browser" = "studionet"
  ): Promise<{ address: string; balance: string }> {
    if (type === "browser" && typeof window !== "undefined" && (window as any).ethereum) {
      try {
        const ethereum = (window as any).ethereum;
        const accounts = await ethereum.request({ method: "eth_requestAccounts" });
        if (!accounts || accounts.length === 0) {
          throw new Error("No accounts authorized in browser wallet.");
        }
        this.browserAddress = accounts[0];
        this.connectedType = "browser";
        this.account = null;

        // Try switching or registering GenLayer StudioNet in browser wallet
        try {
          await this.switchOrAddStudioNet();
        } catch {
          // Gracefully continue even if switch rejected
        }

        // Initialize client explicitly configured with browser wallet provider
        this.client = createClient({
          chain: studionet,
          account: this.browserAddress as `0x${string}`,
          provider: ethereum,
        });

        const balance = await this.ensureBalance();
        return { address: this.browserAddress, balance };
      } catch (err: any) {
        console.error("Browser wallet connection error:", err);
        throw err;
      }
    }

    // Default: Native GenLayer StudioNet Account
    let storedKey = localStorage.getItem("genstate_session_key");
    if (!storedKey) {
      storedKey = generatePrivateKey();
      localStorage.setItem("genstate_session_key", storedKey);
    }
    this.account = createAccount(storedKey as `0x${string}`);
    this.client = createClient({ chain: studionet, account: this.account });
    this.connectedType = "studionet";
    this.browserAddress = "";

    const balance = await this.ensureBalance();
    return { address: this.account.address, balance };
  }

  /**
   * Dynamically update active browser wallet account upon accountsChanged event.
   */
  public async setBrowserAccount(newAddress: string): Promise<string> {
    if (!newAddress) {
      this.disconnectWallet();
      return "0.0000 GEN";
    }
    this.browserAddress = newAddress;
    this.connectedType = "browser";
    this.account = null;

    if (typeof window !== "undefined" && (window as any).ethereum) {
      this.client = createClient({
        chain: studionet,
        account: this.browserAddress as `0x${string}`,
        provider: (window as any).ethereum,
      });
    }

    return await this.ensureBalance();
  }

  /**
   * Enforces that the browser wallet is connected to GenLayer StudioNet before permitting write transactions.
   */
  public async assertCorrectNetwork(): Promise<void> {
    if (this.connectedType === "browser" && typeof window !== "undefined" && (window as any).ethereum) {
      try {
        const chainId = await (window as any).ethereum.request({ method: "eth_chainId" });
        const isStudioNet = chainId === "0xf22f" || chainId === "61999" || chainId === 61999;
        if (!isStudioNet) {
          await this.switchOrAddStudioNet();
          const recheck = await (window as any).ethereum.request({ method: "eth_chainId" });
          const recheckIsStudio = recheck === "0xf22f" || recheck === "61999" || recheck === 61999;
          if (!recheckIsStudio) {
            throw new Error("Active network must be GenLayer StudioNet (Chain ID: 61999 / 0xf22f). Please switch networks in your wallet.");
          }
        }
      } catch (err: any) {
        throw new Error(err.message || "Failed to verify or switch active network to GenLayer StudioNet.");
      }
    }
  }

  /**
   * Disconnect the active wallet session.
   */
  public disconnectWallet(): void {
    this.account = null;
    this.client = null;
    this.connectedType = null;
    this.browserAddress = "";
  }

  /**
   * Format balance in wei to a clean human-readable GEN string with comma separators.
   */
  public formatWeiToGen(wei: bigint): string {
    const oneGen = 1000000000000000000n;
    const whole = wei / oneGen;
    const fraction = wei % oneGen;
    const fractionStr = fraction.toString().padStart(18, "0").slice(0, 4);
    return `${whole.toLocaleString()}.${fractionStr} GEN`;
  }

  /**
   * Get the real balance of the currently active account.
   */
  public async ensureBalance(): Promise<string> {
    const activeAddress = this.getAccountAddress();
    if (!activeAddress) return "0.0000 GEN";

    let balanceWei = 0n;

    // 1. If connected via browser wallet, query user's extension directly
    if (this.connectedType === "browser" && typeof window !== "undefined" && (window as any).ethereum) {
      try {
        const rawHex = await (window as any).ethereum.request({
          method: "eth_getBalance",
          params: [activeAddress, "latest"],
        });
        if (rawHex && rawHex !== "0x" && rawHex !== "0x0") {
          const b = BigInt(rawHex);
          if (b > balanceWei) balanceWei = b;
        }
      } catch (err) {
        console.warn("eth_getBalance via window.ethereum failed:", err);
      }
    }

    // 2. Query GenLayer StudioNet RPC for active address
    try {
      const rpcBal = await this.readClient.getBalance({ address: activeAddress });
      if (rpcBal) {
        const b = BigInt(rpcBal);
        if (b > balanceWei) balanceWei = b;
      }
    } catch (err) {
      console.warn("readClient getBalance failed:", err);
    }

    // 3. If Native StudioNet account and has 0 or low balance, auto-fund via testnet faucet RPC
    if (this.connectedType === "studionet" && balanceWei < 100000000000000000n && this.account) {
      try {
        await fetch(GENSTATE_CONFIG.rpcUrl, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            jsonrpc: "2.0",
            id: Date.now(),
            method: "sim_fundAccount",
            params: [this.account.address, 10000000000000000000], // 10 GEN
          }),
        });
        const updated = await this.readClient.getBalance({ address: this.account.address });
        balanceWei = BigInt(updated);
      } catch (err) {
        console.warn("Auto-funding failed:", err);
      }
    }

    return this.formatWeiToGen(balanceWei);
  }

  /**
   * Fetch protocol-level telemetry metrics live from deployed contract.
   */
  public async fetchProtocolStats(): Promise<ProtocolStats> {
    const runner = this.client || this.readClient;
    const raw = await runner.readContract({
      address: GENSTATE_CONFIG.contractAddress,
      functionName: "get_protocol_stats",
      args: [],
    });

    return {
      protocol_name: String(raw.protocol_name || "GenState"),
      version: String(raw.version || "1.2.0"),
      admin: String(raw.admin || ""),
      total_claims: Number(raw.total_claims || 0),
      total_evidence: Number(raw.total_evidence || 0),
      total_escrowed: String(raw.total_escrowed || "0"),
      total_settled: String(raw.total_settled || "0"),
      total_refunded: String(raw.total_refunded || "0"),
      supported_policies: (raw.supported_policies || []) as string[],
      supported_claim_types: (raw.supported_claim_types || []) as string[],
    };
  }

  /**
   * Fetch paginated state claims live from deployed contract.
   */
  public async fetchClaims(offset = 0, limit = 50): Promise<StateClaim[]> {
    const runner = this.client || this.readClient;
    const list = await runner.readContract({
      address: GENSTATE_CONFIG.contractAddress,
      functionName: "list_claims",
      args: [offset, limit],
    });

    if (!Array.isArray(list)) return [];

    return list.map((item: any) => ({
      id: String(item.id || ""),
      creator: String(item.creator || ""),
      claim_type: String(item.claim_type || "REGISTRY_RECORD"),
      subject: String(item.subject || ""),
      predicate: String(item.predicate || ""),
      asserted_value: String(item.asserted_value || ""),
      reference_date: String(item.reference_date || ""),
      source_policy: String(item.source_policy || ""),
      window_seconds: Number(item.window_seconds || 0),
      opened_at: Number(item.opened_at || 0),
      evidence_deadline: Number(item.evidence_deadline || 0),
      status: String(item.status || "DRAFT") as any,
      verdict: item.verdict ? String(item.verdict) : undefined,
      verdict_reason: item.verdict_reason ? String(item.verdict_reason) : undefined,
      adjudication_time: item.adjudication_time ? String(item.adjudication_time) : undefined,
      evidence_count: Number(item.evidence_count || 0),
      bounty_amount: String(item.bounty_amount || "0"),
      funders: (item.funders || []) as string[],
      qualifying_recipients: (item.qualifying_recipients || []) as string[],
      bounty_settled_recipients: (item.bounty_settled_recipients || []) as string[],
    }));
  }

  /**
   * Fetch a single claim by ID live from deployed contract.
   */
  public async fetchClaim(claimId: string): Promise<StateClaim> {
    const runner = this.client || this.readClient;
    const item = await runner.readContract({
      address: GENSTATE_CONFIG.contractAddress,
      functionName: "get_claim",
      args: [claimId],
    });

    return {
      id: String(item.id || ""),
      creator: String(item.creator || ""),
      claim_type: String(item.claim_type || "REGISTRY_RECORD"),
      subject: String(item.subject || ""),
      predicate: String(item.predicate || ""),
      asserted_value: String(item.asserted_value || ""),
      reference_date: String(item.reference_date || ""),
      source_policy: String(item.source_policy || ""),
      window_seconds: Number(item.window_seconds || 0),
      opened_at: Number(item.opened_at || 0),
      evidence_deadline: Number(item.evidence_deadline || 0),
      status: String(item.status || "DRAFT") as any,
      verdict: item.verdict ? String(item.verdict) : undefined,
      verdict_reason: item.verdict_reason ? String(item.verdict_reason) : undefined,
      adjudication_time: item.adjudication_time ? String(item.adjudication_time) : undefined,
      evidence_count: Number(item.evidence_count || 0),
      bounty_amount: String(item.bounty_amount || "0"),
      funders: (item.funders || []) as string[],
      qualifying_recipients: (item.qualifying_recipients || []) as string[],
      bounty_settled_recipients: (item.bounty_settled_recipients || []) as string[],
    };
  }

  /**
   * Fetch all evidence records for a claim live from deployed contract.
   */
  public async fetchEvidence(claimId: string): Promise<EvidenceRecord[]> {
    const runner = this.client || this.readClient;
    const list = await runner.readContract({
      address: GENSTATE_CONFIG.contractAddress,
      functionName: "get_evidence_for_claim",
      args: [claimId],
    });

    if (!Array.isArray(list)) return [];

    return list.map((e: any) => ({
      id: String(e.id || ""),
      claim_id: String(e.claim_id || claimId),
      submitter: String(e.submitter || ""),
      source_url: String(e.source_url || ""),
      explanation: String(e.explanation || ""),
    }));
  }

  /**
   * Fetch individual contributor funding records for a claim.
   */
  public async fetchClaimFunders(claimId: string): Promise<{ funder: string; amount: string }[]> {
    const runner = this.client || this.readClient;
    const list = await runner.readContract({
      address: GENSTATE_CONFIG.contractAddress,
      functionName: "get_claim_funders",
      args: [claimId],
    });

    if (!Array.isArray(list)) return [];

    return list.map((item: any) => ({
      funder: String(item.funder || ""),
      amount: String(item.amount || "0"),
    }));
  }

  /**
   * Fetch consensus adjudication ruling live from deployed contract.
   */
  public async fetchAdjudication(claimId: string): Promise<AdjudicationResult | null> {
    const runner = this.client || this.readClient;
    const res = await runner.readContract({
      address: GENSTATE_CONFIG.contractAddress,
      functionName: "get_adjudication",
      args: [claimId],
    });

    if (!res || res.verdict === "NOT_ADJUDICATED") {
      return null;
    }

    return {
      claim_id: String(res.claim_id || claimId),
      verdict: String(res.verdict || ""),
      reason: String(res.reason || ""),
      confidence_score: Number(res.confidence_score || 0),
      adjudicated_at: String(res.adjudicated_at || ""),
      evidence_count: Number(res.evidence_count || 0),
      source_fingerprints: (res.source_fingerprints || []) as any[],
      quotation_verified: Boolean(res.quotation_verified),
      supporting_quotation: String(res.supporting_quotation || ""),
      qualifying_recipients: (res.qualifying_recipients || []) as string[],
    };
  }

  private requireConnectedClient() {
    if (!this.client || (!this.account && !this.browserAddress)) {
      throw new Error("Please connect your wallet first to execute on-chain transactions.");
    }
  }

  /**
   * Authoritative transaction finalization check:
   * Verifies both that transaction reached FINALIZED and that GenVM execution succeeded.
   */
  public async waitForFinalizedSuccess(
    txHash: string,
    retries = 60,
    interval = 3000
  ): Promise<any> {
    const runner = this.client || this.readClient;
    const receipt = await runner.waitForTransactionReceipt({
      hash: txHash,
      status: TransactionStatus.FINALIZED,
      retries,
      interval,
    });

    const finalized =
      receipt.statusName === TransactionStatus.FINALIZED ||
      Number(receipt.status) === 7 ||
      String(receipt.status).toLowerCase() === "finalized";

    const leaderReceiptRaw = (receipt as any).consensus_data?.leader_receipt;
    const leaderReceipts = Array.isArray(leaderReceiptRaw)
      ? leaderReceiptRaw
      : leaderReceiptRaw
        ? [leaderReceiptRaw]
        : [];

    const succeeded =
      receipt.txExecutionResultName === "FINISHED_WITH_RETURN" ||
      Number(receipt.txExecutionResult) === 1 ||
      leaderReceipts.some((item: any) => item?.execution_result === "SUCCESS");

    if (!finalized || !succeeded) {
      throw new Error(
        `GenLayer transaction finalized without success. Status: ${receipt.statusName ?? receipt.status}, Result: ${receipt.txExecutionResultName ?? receipt.txExecutionResult ?? "FAILED"}`
      );
    }

    return receipt;
  }

  /**
   * Broadcast real on-chain transaction: declare_claim.
   * Deterministically queries created claim instead of deriving solely from counter.
   */
  public async declareClaim(
    claimType: string,
    subject: string,
    predicate: string,
    assertedValue: string,
    referenceDate: string
  ): Promise<{ txHash: string; claimId: string }> {
    this.requireConnectedClient();
    await this.assertCorrectNetwork();
    await this.ensureBalance();

    const txHash = await this.client.writeContract({
      address: GENSTATE_CONFIG.contractAddress,
      functionName: "declare_claim",
      args: [claimType, subject, predicate, assertedValue, referenceDate],
    });

    const receipt = await this.waitForFinalizedSuccess(txHash);

    // Retrieve deterministic claim ID from receipt return value or authoritative stats
    let claimId = "";
    if (receipt && receipt.returnValue && typeof receipt.returnValue === "string" && receipt.returnValue.startsWith("CLAIM-")) {
      claimId = receipt.returnValue;
    } else {
      const stats = await this.fetchProtocolStats();
      claimId = `CLAIM-${stats.total_claims}`;
    }

    return { txHash, claimId };
  }

  /**
   * Broadcast real on-chain transaction: freeze_claim.
   */
  public async freezeClaim(
    claimId: string,
    sourcePolicy: string,
    windowSeconds = 86400
  ): Promise<{ txHash: string }> {
    this.requireConnectedClient();
    await this.assertCorrectNetwork();
    await this.ensureBalance();

    const txHash = await this.client.writeContract({
      address: GENSTATE_CONFIG.contractAddress,
      functionName: "freeze_claim",
      args: [claimId, sourcePolicy, windowSeconds],
    });

    await this.waitForFinalizedSuccess(txHash);
    return { txHash };
  }

  /**
   * Broadcast real on-chain transaction: fund_bounty with genuine native GEN.
   */
  public async fundBounty(
    claimId: string,
    amountWei: bigint | string
  ): Promise<{ txHash: string; newBounty: string }> {
    this.requireConnectedClient();
    await this.assertCorrectNetwork();
    await this.ensureBalance();

    const value = BigInt(amountWei);
    const txHash = await this.client.writeContract({
      address: GENSTATE_CONFIG.contractAddress,
      functionName: "fund_bounty",
      args: [claimId],
      value,
    });

    await this.waitForFinalizedSuccess(txHash);
    const claim = await this.fetchClaim(claimId);
    return { txHash, newBounty: claim.bounty_amount };
  }

  /**
   * Broadcast real on-chain transaction: submit_evidence.
   */
  public async submitEvidence(
    claimId: string,
    sourceUrl: string,
    explanation: string
  ): Promise<{ txHash: string }> {
    this.requireConnectedClient();
    await this.assertCorrectNetwork();
    await this.ensureBalance();

    const txHash = await this.client.writeContract({
      address: GENSTATE_CONFIG.contractAddress,
      functionName: "submit_evidence",
      args: [claimId, sourceUrl, explanation],
    });

    await this.waitForFinalizedSuccess(txHash);
    return { txHash };
  }

  /**
   * Broadcast real on-chain transaction: adjudicate.
   * Invokes GenLayer multi-validator LLM consensus round.
   */
  public async adjudicateClaim(claimId: string): Promise<{ txHash: string; verdict: string }> {
    this.requireConnectedClient();
    await this.assertCorrectNetwork();
    await this.ensureBalance();

    const txHash = await this.client.writeContract({
      address: GENSTATE_CONFIG.contractAddress,
      functionName: "adjudicate",
      args: [claimId],
    });

    await this.waitForFinalizedSuccess(txHash, 90, 3000);
    const claim = await this.fetchClaim(claimId);
    return { txHash, verdict: claim.verdict || "RESOLVED" };
  }

  /**
   * Broadcast real on-chain transaction: settle_bounty.
   * Executes genuine native GEN movement to eligible recipient.
   */
  public async settleBounty(
    claimId: string,
    recipientAddress: string
  ): Promise<{ txHash: string }> {
    this.requireConnectedClient();
    await this.assertCorrectNetwork();
    await this.ensureBalance();

    const txHash = await this.client.writeContract({
      address: GENSTATE_CONFIG.contractAddress,
      functionName: "settle_bounty",
      args: [claimId, recipientAddress],
    });

    await this.waitForFinalizedSuccess(txHash);
    return { txHash };
  }

  /**
   * Broadcast real on-chain transaction: refund_bounty.
   */
  public async refundBounty(claimId: string): Promise<{ txHash: string }> {
    this.requireConnectedClient();
    await this.assertCorrectNetwork();
    await this.ensureBalance();

    const txHash = await this.client.writeContract({
      address: GENSTATE_CONFIG.contractAddress,
      functionName: "refund_bounty",
      args: [claimId],
    });

    await this.waitForFinalizedSuccess(txHash);
    return { txHash };
  }

  /**
   * Broadcast real on-chain transaction: cancel_claim.
   */
  public async cancelClaim(claimId: string): Promise<{ txHash: string }> {
    this.requireConnectedClient();
    await this.assertCorrectNetwork();
    await this.ensureBalance();

    const txHash = await this.client.writeContract({
      address: GENSTATE_CONFIG.contractAddress,
      functionName: "cancel_claim",
      args: [claimId],
    });

    await this.waitForFinalizedSuccess(txHash);
    return { txHash };
  }

  /**
   * Query pending recoverable balance for an address in wei.
   */
  public async getPendingRecovery(recipient?: string): Promise<string> {
    const target = recipient || this.getAccountAddress();
    if (!target) return "0";
    try {
      const runner = this.client || this.readClient;
      const res = await runner.readContract({
        address: GENSTATE_CONFIG.contractAddress,
        functionName: "get_pending_recovery",
        args: [target],
      });
      return String(res || "0");
    } catch (err) {
      console.warn("get_pending_recovery query error:", err);
      return "0";
    }
  }

  /**
   * Broadcast real on-chain transaction: recover_failed_transfer.
   * Allows claiming accumulated un-transferred balances via pull-recovery.
   */
  public async recoverFailedTransfer(recipient?: string): Promise<{ txHash: string; recoveredAmount: string }> {
    this.requireConnectedClient();
    await this.assertCorrectNetwork();
    await this.ensureBalance();

    const target = recipient || this.getAccountAddress();
    const txHash = await this.client.writeContract({
      address: GENSTATE_CONFIG.contractAddress,
      functionName: "recover_failed_transfer",
      args: [target],
    });

    const receipt = await this.waitForFinalizedSuccess(txHash);
    return {
      txHash,
      recoveredAmount: receipt.returnValue ? String(receipt.returnValue) : "Recovered",
    };
  }
}

export const genStateService = new LiveGenStateService();
