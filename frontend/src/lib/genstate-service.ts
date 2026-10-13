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
   * Connect wallet on explicit user action.
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

        // For GenLayer transaction execution on StudioNet, initialize paired signer
        let storedKey = localStorage.getItem("genstate_session_key");
        if (!storedKey) {
          storedKey = generatePrivateKey();
          localStorage.setItem("genstate_session_key", storedKey);
        }
        this.account = createAccount(storedKey as `0x${string}`);
        this.client = createClient({ chain: studionet, account: this.account });

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
   * Disconnect the active wallet session.
   */
  public disconnectWallet(): void {
    this.account = null;
    this.client = null;
    this.connectedType = null;
    this.browserAddress = "";
  }

  public async ensureBalance(): Promise<string> {
    if (!this.account) return "0.0000 GEN";
    try {
      const balance = await this.readClient.getBalance({ address: this.account.address });
      if (balance < 100000000000000000n) {
        // Request funds via StudioNet sim_fundAccount RPC
        await fetch(GENSTATE_CONFIG.rpcUrl, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            jsonrpc: "2.0",
            id: Date.now(),
            method: "sim_fundAccount",
            params: [this.account.address, 1000000000000000000],
          }),
        });
      }
      const updated = await this.readClient.getBalance({ address: this.account.address });
      return (Number(updated) / 1e18).toFixed(4) + " GEN";
    } catch {
      try {
        const bal = await this.readClient.getBalance({ address: this.account.address });
        return (Number(bal) / 1e18).toFixed(4) + " GEN";
      } catch {
        return "0.0000 GEN";
      }
    }
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
      version: String(raw.version || "1.0.0"),
      admin: String(raw.admin || ""),
      total_claims: Number(raw.total_claims || 0),
      total_evidence: Number(raw.total_evidence || 0),
      total_escrowed: String(raw.total_escrowed || "0"),
      total_settled: String(raw.total_settled || "0"),
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
      status: String(item.status || "DRAFT") as any,
      verdict: item.verdict ? String(item.verdict) : undefined,
      verdict_reason: item.verdict_reason ? String(item.verdict_reason) : undefined,
      adjudication_time: item.adjudication_time ? String(item.adjudication_time) : undefined,
      evidence_count: Number(item.evidence_count || 0),
      bounty_amount: String(item.bounty_amount || "0"),
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
      status: String(item.status || "DRAFT") as any,
      verdict: item.verdict ? String(item.verdict) : undefined,
      verdict_reason: item.verdict_reason ? String(item.verdict_reason) : undefined,
      adjudication_time: item.adjudication_time ? String(item.adjudication_time) : undefined,
      evidence_count: Number(item.evidence_count || 0),
      bounty_amount: String(item.bounty_amount || "0"),
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
    };
  }

  private requireConnectedClient() {
    if (!this.client || !this.account) {
      throw new Error("Please connect your wallet first to execute on-chain transactions.");
    }
  }

  /**
   * Broadcast real on-chain transaction: declare_claim.
   */
  public async declareClaim(
    claimType: string,
    subject: string,
    predicate: string,
    assertedValue: string,
    referenceDate: string
  ): Promise<{ txHash: string; claimId: string }> {
    this.requireConnectedClient();
    await this.ensureBalance();

    const txHash = await this.client.writeContract({
      address: GENSTATE_CONFIG.contractAddress,
      functionName: "declare_claim",
      args: [claimType, subject, predicate, assertedValue, referenceDate],
    });

    await this.client.waitForTransactionReceipt({
      hash: txHash,
      status: TransactionStatus.FINALIZED,
      retries: 50,
      interval: 3000,
    });

    const stats = await this.fetchProtocolStats();
    const claimId = `CLAIM-${stats.total_claims}`;

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
    await this.ensureBalance();

    const txHash = await this.client.writeContract({
      address: GENSTATE_CONFIG.contractAddress,
      functionName: "freeze_claim",
      args: [claimId, sourcePolicy, windowSeconds],
    });

    await this.client.waitForTransactionReceipt({
      hash: txHash,
      status: TransactionStatus.FINALIZED,
      retries: 50,
      interval: 3000,
    });

    return { txHash };
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
    await this.ensureBalance();

    const txHash = await this.client.writeContract({
      address: GENSTATE_CONFIG.contractAddress,
      functionName: "submit_evidence",
      args: [claimId, sourceUrl, explanation],
    });

    await this.client.waitForTransactionReceipt({
      hash: txHash,
      status: TransactionStatus.FINALIZED,
      retries: 50,
      interval: 3000,
    });

    return { txHash };
  }

  /**
   * Broadcast real on-chain transaction: adjudicate.
   * Invokes GenLayer multi-validator LLM consensus round.
   */
  public async adjudicateClaim(claimId: string): Promise<{ txHash: string; verdict: string }> {
    this.requireConnectedClient();
    await this.ensureBalance();

    const txHash = await this.client.writeContract({
      address: GENSTATE_CONFIG.contractAddress,
      functionName: "adjudicate",
      args: [claimId],
    });

    await this.client.waitForTransactionReceipt({
      hash: txHash,
      status: TransactionStatus.FINALIZED,
      retries: 60,
      interval: 3000,
    });

    const claim = await this.fetchClaim(claimId);
    return { txHash, verdict: claim.verdict || "RESOLVED" };
  }

  /**
   * Broadcast real on-chain transaction: settle_bounty.
   */
  public async settleBounty(
    claimId: string,
    recipientAddress: string
  ): Promise<{ txHash: string }> {
    this.requireConnectedClient();
    await this.ensureBalance();

    const txHash = await this.client.writeContract({
      address: GENSTATE_CONFIG.contractAddress,
      functionName: "settle_bounty",
      args: [claimId, recipientAddress],
    });

    await this.client.waitForTransactionReceipt({
      hash: txHash,
      status: TransactionStatus.FINALIZED,
      retries: 50,
      interval: 3000,
    });

    return { txHash };
  }
}

export const genStateService = new LiveGenStateService();
