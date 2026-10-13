import type {
  StateClaim,
  EvidenceRecord,
  AdjudicationResult,
  ProtocolStats,
} from "../types/genstate";

// Real seed state matching on-chain genesis assertion
const INITIAL_CLAIMS: StateClaim[] = [
  {
    id: "CLAIM-1",
    creator: "0x9463103F0F1fC9472e097AfF5d33f2Bd29eaFA60",
    claim_type: "REGISTRY_RECORD",
    subject: "GenState Protocol Genesis Deployment",
    predicate: "is_deployed_on_studionet",
    asserted_value: "Verified Active",
    reference_date: "2026-10-13",
    source_policy: "OFFICIAL_REGISTRY",
    window_seconds: 86400,
    status: "RESOLVED",
    verdict: "CONFIRMED",
    verdict_reason:
      "Contract successfully deployed, attested by 5 validator quorum nodes on StudioNet round 0.",
    adjudication_time: "CONSENSUS_FINALIZED",
    evidence_count: 2,
    bounty_amount: "1000000000000000000",
  },
  {
    id: "CLAIM-2",
    creator: "0x3A21Db08Fe8F19280b271E072b25B93E9B712A88",
    claim_type: "STATE_TRANSITION",
    subject: "Ethereum Dencun EIP-4844 Blob Settlement Rate",
    predicate: "average_daily_blob_throughput_exceeded_threshold",
    asserted_value: "> 2.5 MB/block",
    reference_date: "2026-10-10",
    source_policy: "MULTI_SOURCE_INDEPENDENT",
    window_seconds: 43200,
    status: "EVIDENCE_OPEN",
    evidence_count: 1,
    bounty_amount: "500000000000000000",
  },
  {
    id: "CLAIM-3",
    creator: "0x78E99B4c25FeD40361C97A14d436F76c8c4Acf21",
    claim_type: "COMPLIANCE_STATUS",
    subject: "Decentralized Autonomous Escrow Audit v2.4",
    predicate: "formal_verification_flaw_count",
    asserted_value: "0 Critical / 0 High",
    reference_date: "2026-10-08",
    source_policy: "PRIMARY_PLUS_CORROBORATION",
    window_seconds: 172800,
    status: "RESOLVED",
    verdict: "CONFIRMED",
    verdict_reason:
      "Formal verification mathematical proofs verified by independent audit consortia.",
    adjudication_time: "CONSENSUS_FINALIZED",
    evidence_count: 2,
    bounty_amount: "2500000000000000000",
  },
  {
    id: "CLAIM-4",
    creator: "0xFe12B6291a134A291c9006Ba236B15cD54117822",
    claim_type: "FACTUAL_EVENT",
    subject: "Commercial Quantum Circuit 128-Qubit Coherence Milestone",
    predicate: "room_temperature_error_rate_sub_1pct",
    asserted_value: "True",
    reference_date: "2026-10-12",
    source_policy: "REGULATORY_FILING",
    window_seconds: 604800,
    status: "EVIDENCE_OPEN",
    evidence_count: 0,
    bounty_amount: "750000000000000000",
  },
];

const INITIAL_EVIDENCE: Record<string, EvidenceRecord[]> = {
  "CLAIM-1": [
    {
      id: "EVID-1",
      claim_id: "CLAIM-1",
      submitter: "0x9463103F0F1fC9472e097AfF5d33f2Bd29eaFA60",
      source_url:
        "https://explorer-studio.genlayer.com/address/0xae97EC507454Db2ABA53ef53cA97b7F308801cb1",
      explanation:
        "Live deployed contract address verified on GenLayer official StudioNet Explorer.",
    },
    {
      id: "EVID-2",
      claim_id: "CLAIM-1",
      submitter: "0x8e5Bd026227CC93169Df51BD9C1b6CA82292F0D2",
      source_url: "https://studio.genlayer.com/api",
      explanation:
        "Genesis write transaction receipt 0x3157648fa5cdbc222e568b372d760490f5e0f7fbbe372db641f868a8fc91a262 confirmed with Status 7 (Finalized).",
    },
  ],
  "CLAIM-2": [
    {
      id: "EVID-3",
      claim_id: "CLAIM-2",
      submitter: "0x43Da18EbE97A612d7c0f1883F05C3109a25B2039",
      source_url: "https://dune.com/queries/ethereum/blobs",
      explanation:
        "Telemetry query indicates continuous average throughput metrics above 2.7 MB during target epoch window.",
    },
  ],
  "CLAIM-3": [
    {
      id: "EVID-4",
      claim_id: "CLAIM-3",
      submitter: "0x78E99B4c25FeD40361C97A14d436F76c8c4Acf21",
      source_url: "https://certik.com/reports/genstate-escrow",
      explanation: "Security review final attestation certificate.",
    },
    {
      id: "EVID-5",
      claim_id: "CLAIM-3",
      submitter: "0x981C5389d47B782a1789c623Bf3e6912384AC701",
      source_url: "https://openzeppelin.com/audits/genstate",
      explanation: "Corroborating second security assessment.",
    },
  ],
};

const INITIAL_ADJUDICATIONS: Record<string, AdjudicationResult> = {
  "CLAIM-1": {
    claim_id: "CLAIM-1",
    verdict: "CONFIRMED",
    reason:
      "All 5 validators independently fetched transaction logs and attested that GenState contract address is active and responding to state queries.",
    confidence_score: 99,
    adjudicated_at: "2026-10-13T02:30:55Z",
    evidence_count: 2,
  },
  "CLAIM-3": {
    claim_id: "CLAIM-3",
    verdict: "CONFIRMED",
    reason:
      "Both independent audit reports confirm zero critical and high issues. Policy requirements for primary plus corroboration are fully satisfied.",
    confidence_score: 96,
    adjudicated_at: "2026-10-11T18:42:10Z",
    evidence_count: 2,
  },
};

// In-browser state management synchronized with local storage
class GenStateStore {
  private claims: StateClaim[] = [];
  private evidence: Record<string, EvidenceRecord[]> = {};
  private adjudications: Record<string, AdjudicationResult> = {};

  constructor() {
    this.load();
  }

  private load() {
    try {
      const savedClaims = localStorage.getItem("genstate_claims");
      const savedEvidence = localStorage.getItem("genstate_evidence");
      const savedAdjudications = localStorage.getItem("genstate_adjudications");

      this.claims = savedClaims ? JSON.parse(savedClaims) : [...INITIAL_CLAIMS];
      this.evidence = savedEvidence
        ? JSON.parse(savedEvidence)
        : { ...INITIAL_EVIDENCE };
      this.adjudications = savedAdjudications
        ? JSON.parse(savedAdjudications)
        : { ...INITIAL_ADJUDICATIONS };
    } catch {
      this.claims = [...INITIAL_CLAIMS];
      this.evidence = { ...INITIAL_EVIDENCE };
      this.adjudications = { ...INITIAL_ADJUDICATIONS };
    }
  }

  private save() {
    try {
      localStorage.setItem("genstate_claims", JSON.stringify(this.claims));
      localStorage.setItem("genstate_evidence", JSON.stringify(this.evidence));
      localStorage.setItem(
        "genstate_adjudications",
        JSON.stringify(this.adjudications)
      );
    } catch (e) {
      console.warn("Storage sync error:", e);
    }
  }

  public getStats(): ProtocolStats {
    let totalEscrowedWei = BigInt(0);
    let totalSettledWei = BigInt(0);

    for (const c of this.claims) {
      const val = BigInt(c.bounty_amount || "0");
      if (c.status === "SETTLED") {
        totalSettledWei += val;
      } else {
        totalEscrowedWei += val;
      }
    }

    let totalEv = 0;
    for (const list of Object.values(this.evidence)) {
      totalEv += list.length;
    }

    return {
      protocol_name: "GenState",
      version: "1.0.0",
      admin: "0x9463103F0F1fC9472e097AfF5d33f2Bd29eaFA60",
      total_claims: this.claims.length,
      total_evidence: totalEv,
      total_escrowed: totalEscrowedWei.toString(),
      total_settled: totalSettledWei.toString(),
      supported_policies: [
        "OFFICIAL_REGISTRY",
        "REGULATORY_FILING",
        "MULTI_SOURCE_INDEPENDENT",
        "PRIMARY_PLUS_CORROBORATION",
        "OPEN_PUBLIC",
      ],
      supported_claim_types: [
        "STATE_TRANSITION",
        "REGISTRY_RECORD",
        "FACTUAL_EVENT",
        "GOVERNANCE_EXECUTION",
        "COMPLIANCE_STATUS",
      ],
    };
  }

  public getClaims(): StateClaim[] {
    return [...this.claims];
  }

  public getClaim(id: string): StateClaim | undefined {
    return this.claims.find((c) => c.id === id);
  }

  public getEvidence(claimId: string): EvidenceRecord[] {
    return this.evidence[claimId] || [];
  }

  public getAdjudication(claimId: string): AdjudicationResult | undefined {
    return this.adjudications[claimId];
  }

  public declareClaim(
    claimType: string,
    subject: string,
    predicate: string,
    assertedValue: string,
    referenceDate: string,
    creatorAddress: string
  ): StateClaim {
    const nextId = `CLAIM-${this.claims.length + 1}`;
    const newClaim: StateClaim = {
      id: nextId,
      creator: creatorAddress,
      claim_type: claimType,
      subject,
      predicate,
      asserted_value: assertedValue,
      reference_date: referenceDate,
      source_policy: "",
      window_seconds: 0,
      status: "DRAFT",
      evidence_count: 0,
      bounty_amount: "0",
    };

    this.claims.unshift(newClaim);
    this.evidence[nextId] = [];
    this.save();
    return newClaim;
  }

  public freezeClaim(
    claimId: string,
    policy: string,
    windowSeconds: number
  ): StateClaim {
    const claim = this.getClaim(claimId);
    if (!claim) throw new Error("Claim not found");
    claim.source_policy = policy;
    claim.window_seconds = windowSeconds;
    claim.status = "EVIDENCE_OPEN";
    this.save();
    return claim;
  }

  public fundBounty(claimId: string, amountWei: string): StateClaim {
    const claim = this.getClaim(claimId);
    if (!claim) throw new Error("Claim not found");
    const current = BigInt(claim.bounty_amount || "0");
    const added = BigInt(amountWei || "0");
    claim.bounty_amount = (current + added).toString();
    this.save();
    return claim;
  }

  public submitEvidence(
    claimId: string,
    sourceUrl: string,
    explanation: string,
    submitterAddress: string
  ): EvidenceRecord {
    const claim = this.getClaim(claimId);
    if (!claim) throw new Error("Claim not found");

    if (!this.evidence[claimId]) {
      this.evidence[claimId] = [];
    }

    const nextEvId = `EVID-${Date.now().toString().slice(-4)}`;
    const newRecord: EvidenceRecord = {
      id: nextEvId,
      claim_id: claimId,
      submitter: submitterAddress,
      source_url: sourceUrl,
      explanation,
    };

    this.evidence[claimId].push(newRecord);
    claim.evidence_count = this.evidence[claimId].length;
    this.save();
    return newRecord;
  }

  public adjudicateClaim(
    claimId: string,
    verdict: string,
    reason: string,
    confidence: number
  ): AdjudicationResult {
    const claim = this.getClaim(claimId);
    if (!claim) throw new Error("Claim not found");

    claim.status = "RESOLVED";
    claim.verdict = verdict;
    claim.verdict_reason = reason;
    claim.adjudication_time = new Date().toISOString();

    const evCount = (this.evidence[claimId] || []).length;
    const adjResult: AdjudicationResult = {
      claim_id: claimId,
      verdict,
      reason,
      confidence_score: confidence,
      adjudicated_at: new Date().toISOString(),
      evidence_count: evCount,
    };

    this.adjudications[claimId] = adjResult;
    this.save();
    return adjResult;
  }

  public settleClaim(claimId: string): StateClaim {
    const claim = this.getClaim(claimId);
    if (!claim) throw new Error("Claim not found");
    claim.status = "SETTLED";
    this.save();
    return claim;
  }
}

export const genStateService = new GenStateStore();
