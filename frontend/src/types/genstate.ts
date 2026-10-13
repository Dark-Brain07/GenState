export type ClaimStatus =
  | "DRAFT"
  | "EVIDENCE_OPEN"
  | "ADJUDICATING"
  | "RESOLVED"
  | "SETTLED"
  | "CANCELLED";

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
  status: ClaimStatus;
  verdict?: AdjudicationVerdict | string;
  verdict_reason?: string;
  adjudication_time?: string;
  evidence_count: number;
  bounty_amount: string;
}

export interface EvidenceRecord {
  id: string;
  claim_id: string;
  submitter: string;
  source_url: string;
  explanation: string;
}

export interface AdjudicationResult {
  claim_id: string;
  verdict: AdjudicationVerdict | string;
  reason: string;
  confidence_score: number;
  adjudicated_at: string;
  evidence_count: number;
}

export interface ProtocolStats {
  protocol_name: string;
  version: string;
  admin: string;
  total_claims: number;
  total_evidence: number;
  total_escrowed: string;
  total_settled: string;
  supported_policies: string[];
  supported_claim_types: string[];
}
