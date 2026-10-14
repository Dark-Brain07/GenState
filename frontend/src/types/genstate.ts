export type ClaimStatus =
  | "DRAFT"
  | "EVIDENCE_OPEN"
  | "ADJUDICATING"
  | "RESOLVED"
  | "PARTIALLY_SETTLED"
  | "SETTLED"
  | "CANCELLED"
  | "REFUNDED";

export type ClaimType =
  | "STATE_TRANSITION"
  | "REGISTRY_RECORD"
  | "FACTUAL_EVENT"
  | "GOVERNANCE_EXECUTION"
  | "COMPLIANCE_STATUS";

export type AdmissibilityPolicy =
  | "OFFICIAL_REGISTRY"
  | "REGULATORY_FILING"
  | "MULTI_SOURCE_INDEPENDENT"
  | "PRIMARY_PLUS_CORROBORATION"
  | "OPEN_PUBLIC";

export type AdjudicationVerdict =
  | "CONFIRMED"
  | "REFUTED"
  | "CONFLICTED"
  | "INSUFFICIENT_EVIDENCE"
  | "SOURCE_UNAVAILABLE"
  | "NOT_ADJUDICATED";

export interface StateClaim {
  id: string;
  creator: string;
  claim_type: ClaimType | string;
  subject: string;
  predicate: string;
  asserted_value: string;
  reference_date: string;
  source_policy: AdmissibilityPolicy | string;
  window_seconds: number;
  opened_at?: number;
  evidence_deadline?: number;
  status: ClaimStatus;
  verdict?: AdjudicationVerdict | string;
  verdict_reason?: string;
  adjudication_time?: string;
  evidence_count: number;
  bounty_amount: string;
  funders?: string[];
  qualifying_recipients?: string[];
  bounty_settled_recipients?: string[];
}

export interface EvidenceRecord {
  id: string;
  claim_id: string;
  submitter: string;
  source_url: string;
  explanation: string;
}

export interface SourceFingerprintRecord {
  evidence_id: string;
  url: string;
  domain: string;
  apex_domain: string;
  sha256_fingerprint: string;
  fetch_status: string;
}

export interface AdjudicationResult {
  claim_id: string;
  verdict: AdjudicationVerdict | string;
  reason: string;
  confidence_score: number;
  adjudicated_at: string;
  evidence_count: number;
  source_fingerprints?: SourceFingerprintRecord[];
  quotation_verified?: boolean;
  supporting_quotation?: string;
  qualifying_recipients?: string[];
}

export interface ProtocolStats {
  protocol_name: string;
  version: string;
  admin: string;
  total_claims: number;
  total_evidence: number;
  total_escrowed: string;
  total_settled: string;
  total_refunded?: string;
  supported_policies: string[];
  supported_claim_types: string[];
}
