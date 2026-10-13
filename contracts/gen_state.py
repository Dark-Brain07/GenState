# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

from genlayer import *
import json

# ==============================================================================
# GenState Protocol: Decentralized Semantic State & Truth Adjudication
# ==============================================================================
# An intelligent state consensus contract operating on GenLayer's GenVM.
# Participants register structured state claims, bind them to deterministic
# admissibility policies, attach evidence from public web sources, and execute
# multi-validator LLM consensus to establish verifiable on-chain truth.
# ==============================================================================

VERSION = "1.0.0"

# Supported claim domain categories
CLAIM_TYPES = [
    "STATE_TRANSITION",
    "REGISTRY_RECORD",
    "FACTUAL_EVENT",
    "GOVERNANCE_EXECUTION",
    "COMPLIANCE_STATUS",
]

# Source admissibility policies
POLICIES = [
    "OFFICIAL_REGISTRY",
    "REGULATORY_FILING",
    "MULTI_SOURCE_INDEPENDENT",
    "PRIMARY_PLUS_CORROBORATION",
    "OPEN_PUBLIC",
]

# Claim state lifecycle
STATE_DRAFT = "DRAFT"
STATE_EVIDENCE_OPEN = "EVIDENCE_OPEN"
STATE_ADJUDICATING = "ADJUDICATING"
STATE_RESOLVED = "RESOLVED"
STATE_SETTLED = "SETTLED"
STATE_CANCELLED = "CANCELLED"

# Terminal verdict classifications
VERDICT_CONFIRMED = "CONFIRMED"
VERDICT_REFUTED = "REFUTED"
VERDICT_CONFLICTED = "CONFLICTED"
VERDICT_INSUFFICIENT = "INSUFFICIENT_EVIDENCE"
VERDICT_UNAVAILABLE = "SOURCE_UNAVAILABLE"

ALLOWED_VERDICTS = [
    VERDICT_CONFIRMED,
    VERDICT_REFUTED,
    VERDICT_CONFLICTED,
    VERDICT_INSUFFICIENT,
    VERDICT_UNAVAILABLE,
]


class GenState(gl.Contract):
    admin: Address
    claim_count: u256
    evidence_count: u256
    claims: TreeMap[str, str]
    claim_ids: DynArray[str]
    claim_evidence_ids: TreeMap[str, str]
    evidence_records: TreeMap[str, str]
    claim_adjudications: TreeMap[str, str]
    bounties: TreeMap[str, u256]
    total_bounties_escrowed: u256
    total_bounties_paid: u256

    def __init__(self):
        self.admin = gl.message.sender_address
        self.claim_count = u256(0)
        self.evidence_count = u256(0)
        self.total_bounties_escrowed = u256(0)
        self.total_bounties_paid = u256(0)

    # --------------------------------------------------------------------------
    # Internal Helpers
    # --------------------------------------------------------------------------

    def _require_admin(self):
        if gl.message.sender_address != self.admin:
            raise gl.vm.UserError("Only protocol admin can call this method")

    def _get_claim_dict(self, claim_id: str) -> dict:
        if claim_id not in self.claims:
            raise gl.vm.UserError(f"Claim with id '{claim_id}' not found")
        return json.loads(self.claims[claim_id])

    def _save_claim_dict(self, claim_id: str, data: dict):
        self.claims[claim_id] = json.dumps(data)

    def _get_evidence_list(self, claim_id: str) -> list:
        if claim_id not in self.claim_evidence_ids:
            return []
        raw = self.claim_evidence_ids[claim_id]
        if not raw:
            return []
        return json.loads(raw)

    # --------------------------------------------------------------------------
    # Public State Writing Methods
    # --------------------------------------------------------------------------

    @gl.public.write
    def declare_claim(
        self,
        claim_type: str,
        subject: str,
        predicate: str,
        asserted_value: str,
        reference_date: str,
    ) -> str:
        """Register a new structured state assertion in DRAFT status."""
        c_type = claim_type.strip().upper()
        if c_type not in CLAIM_TYPES:
            raise gl.vm.UserError(
                f"Invalid claim type '{claim_type}'. Allowed: {', '.join(CLAIM_TYPES)}"
            )

        subj = subject.strip()
        pred = predicate.strip()
        val = asserted_value.strip()

        if len(subj) < 3 or len(subj) > 300:
            raise gl.vm.UserError("Subject must be between 3 and 300 characters")
        if len(pred) < 3 or len(pred) > 200:
            raise gl.vm.UserError("Predicate must be between 3 and 200 characters")
        if len(val) < 1 or len(val) > 500:
            raise gl.vm.UserError(
                "Asserted value must be between 1 and 500 characters"
            )

        new_count = int(self.claim_count) + 1
        self.claim_count = u256(new_count)
        claim_id = f"CLAIM-{new_count}"

        claim_data = {
            "id": claim_id,
            "creator": str(gl.message.sender_address),
            "claim_type": c_type,
            "subject": subj,
            "predicate": pred,
            "asserted_value": val,
            "reference_date": reference_date.strip(),
            "source_policy": "",
            "window_seconds": 0,
            "status": STATE_DRAFT,
            "verdict": "",
            "verdict_reason": "",
            "adjudication_time": "",
            "evidence_count": 0,
            "bounty_amount": "0",
        }

        self._save_claim_dict(claim_id, claim_data)
        self.claim_ids.append(claim_id)
        self.claim_evidence_ids[claim_id] = json.dumps([])
        self.bounties[claim_id] = u256(0)

        return claim_id

    @gl.public.write
    def freeze_claim(
        self, claim_id: str, source_policy: str, window_seconds: u256
    ) -> str:
        """Lock the claim parameters and open the window for public evidence submission."""
        claim = self._get_claim_dict(claim_id)

        if str(gl.message.sender_address).lower() != claim["creator"].lower():
            raise gl.vm.UserError("Only the claim creator can freeze this claim")
        if claim["status"] != STATE_DRAFT:
            raise gl.vm.UserError(
                f"Claim is in status '{claim['status']}', expected '{STATE_DRAFT}'"
            )

        pol = source_policy.strip().upper()
        if pol not in POLICIES:
            raise gl.vm.UserError(
                f"Invalid source policy '{source_policy}'. Allowed: {', '.join(POLICIES)}"
            )

        claim["source_policy"] = pol
        claim["window_seconds"] = int(window_seconds)
        claim["status"] = STATE_EVIDENCE_OPEN

        self._save_claim_dict(claim_id, claim)
        return claim_id

    @gl.public.write.payable
    def fund_bounty(self, claim_id: str) -> str:
        """Fund an escrowed bounty reward for evidence providers and adjudication settlement."""
        claim = self._get_claim_dict(claim_id)
        if claim["status"] in [STATE_RESOLVED, STATE_SETTLED, STATE_CANCELLED]:
            raise gl.vm.UserError(
                f"Cannot fund bounty on claim with status '{claim['status']}'"
            )

        added_val = gl.message.value
        current_bounty = (
            self.bounties[claim_id] if claim_id in self.bounties else u256(0)
        )
        new_bounty = current_bounty + added_val
        self.bounties[claim_id] = new_bounty

        self.total_bounties_escrowed = (
            self.total_bounties_escrowed + added_val
        )
        claim["bounty_amount"] = str(new_bounty)
        self._save_claim_dict(claim_id, claim)

        return str(new_bounty)

    @gl.public.write
    def submit_evidence(
        self, claim_id: str, source_url: str, explanation: str
    ) -> str:
        """Submit a public web evidence link with contextual explanation."""
        claim = self._get_claim_dict(claim_id)

        if claim["status"] not in [STATE_EVIDENCE_OPEN, STATE_ADJUDICATING]:
            raise gl.vm.UserError(
                f"Evidence submission not open for claim with status '{claim['status']}'"
            )

        url = source_url.strip()
        if not (url.startswith("http://") or url.startswith("https://")):
            raise gl.vm.UserError("Source URL must begin with http:// or https://")
        if len(url) > 500:
            raise gl.vm.UserError("Source URL exceeds maximum 500 characters")

        notes = explanation.strip()
        if len(notes) < 5 or len(notes) > 1000:
            raise gl.vm.UserError("Explanation must be between 5 and 1000 characters")

        new_ev_count = int(self.evidence_count) + 1
        self.evidence_count = u256(new_ev_count)
        evidence_id = f"EVID-{new_ev_count}"

        ev_data = {
            "id": evidence_id,
            "claim_id": claim_id,
            "submitter": str(gl.message.sender_address),
            "source_url": url,
            "explanation": notes,
        }

        self.evidence_records[evidence_id] = json.dumps(ev_data)

        # Update claim's evidence collection
        ev_list = self._get_evidence_list(claim_id)
        ev_list.append(evidence_id)
        self.claim_evidence_ids[claim_id] = json.dumps(ev_list)

        claim["evidence_count"] = len(ev_list)
        self._save_claim_dict(claim_id, claim)

        return evidence_id

    @gl.public.write
    def adjudicate(self, claim_id: str) -> str:
        """
        Executes multi-validator intelligent consensus over submitted evidence.
        Strictly satisfies Storage Pre-Extraction Rule and Equivalence Principle.
        """
        claim = self._get_claim_dict(claim_id)

        if claim["status"] not in [STATE_EVIDENCE_OPEN, STATE_ADJUDICATING]:
            raise gl.vm.UserError(
                f"Cannot adjudicate claim in status '{claim['status']}'"
            )

        ev_ids = self._get_evidence_list(claim_id)
        if len(ev_ids) == 0:
            raise gl.vm.UserError(
                "Cannot adjudicate claim without at least one submitted evidence record"
            )

        # ----------------------------------------------------------------------
        # MANDATORY STORAGE PRE-EXTRACTION:
        # Pre-extract all contract storage into pure local Python primitives.
        # NEVER reference self inside leader() or equivalence closures!
        # ----------------------------------------------------------------------
        frozen_claim_id = claim_id
        frozen_subject = claim["subject"]
        frozen_predicate = claim["predicate"]
        frozen_asserted_value = claim["asserted_value"]
        frozen_claim_type = claim["claim_type"]
        frozen_policy = claim["source_policy"]

        evidence_items = []
        for eid in ev_ids:
            if eid in self.evidence_records:
                evidence_items.append(json.loads(self.evidence_records[eid]))

        # Define non-deterministic leader execution
        def leader_fn() -> str:
            # 1. Fetch web content defensively
            evidence_summaries = []
            for item in evidence_items:
                url = item.get("source_url", "")
                note = item.get("explanation", "")
                page_text = ""
                try:
                    res = gl.nondet.web.get(url)
                    raw_body = res.body.decode("utf-8", errors="ignore")
                    # Clean and truncate page text to essential window
                    page_text = " ".join(raw_body.split())[:12000]
                except Exception:
                    page_text = "[External web source unreachable or fetch timed out - fallback to submission context]"

                evidence_summaries.append(
                    {
                        "evidence_id": item.get("id", ""),
                        "url": url,
                        "submitter_explanation": note,
                        "fetched_content_sample": page_text[:1500],
                    }
                )

            # 2. Formulate adjudication evaluation prompt
            prompt = f"""You are an authoritative validator node in the GenState decentralized adjudication network.
Your task is to independently examine submitted public evidence and evaluate a frozen state claim.

CLAIM INFORMATION:
- Claim ID: {frozen_claim_id}
- Domain Category: {frozen_claim_type}
- Subject: {frozen_subject}
- Predicate: {frozen_predicate}
- Asserted Value: {frozen_asserted_value}
- Admissibility Policy: {frozen_policy}

SUBMITTED EVIDENCE SOURCES:
{json.dumps(evidence_summaries, indent=2)}

POLICY ADMISSIBILITY REQUIREMENTS:
- OFFICIAL_REGISTRY: High standard of proof. Must reflect authoritative or direct official registry confirmation.
- REGULATORY_FILING: Must be grounded in official regulatory notices, corporate reports, or verifiable legal filings.
- MULTI_SOURCE_INDEPENDENT: Requires multiple distinct sources corroborating the state.
- PRIMARY_PLUS_CORROBORATION: Requires primary evidence plus corroborating context.
- OPEN_PUBLIC: Any credible, verifiable public reporting.

VERDICT RULES:
Choose exactly ONE primary verdict:
- "CONFIRMED": The evidence convincingly validates the asserted value according to the policy.
- "REFUTED": The evidence proves the assertion false or indicates an opposing state.
- "CONFLICTED": Multiple sources offer contradictory, mutually exclusive conclusions.
- "INSUFFICIENT_EVIDENCE": Available sources are too sparse, ambiguous, or speculative to confirm.
- "SOURCE_UNAVAILABLE": External links were completely inaccessible and insufficient context exists.

You MUST respond strictly with a valid JSON object with the following schema:
{{
  "verdict": "CONFIRMED" | "REFUTED" | "CONFLICTED" | "INSUFFICIENT_EVIDENCE" | "SOURCE_UNAVAILABLE",
  "reason": "Clear, concise objective rationale for the verdict (max 100 words)",
  "confidence_score": 0 to 100
}}"""

            raw_res = gl.nondet.exec_prompt(prompt, response_format="json")
            if isinstance(raw_res, str):
                try:
                    parsed = json.loads(raw_res)
                except Exception:
                    parsed = {
                        "verdict": "INSUFFICIENT_EVIDENCE",
                        "reason": "Malformed LLM payload",
                        "confidence_score": 0,
                    }
            else:
                parsed = raw_res

            v = str(parsed.get("verdict", "INSUFFICIENT_EVIDENCE")).strip().upper()
            if v not in ALLOWED_VERDICTS:
                v = "INSUFFICIENT_EVIDENCE"

            clean_result = {
                "verdict": v,
                "reason": str(parsed.get("reason", "Adjudication finalized")).strip()[:400],
                "confidence_score": int(parsed.get("confidence_score", 75)),
            }
            return json.dumps(clean_result, sort_keys=True)

        # 3. Equivalence principle consensus comparative evaluation
        consensus_raw = gl.eq_principle.prompt_comparative(
            leader_fn,
            principle="Equal if validators agree on the primary verdict (CONFIRMED, REFUTED, CONFLICTED, INSUFFICIENT_EVIDENCE, or SOURCE_UNAVAILABLE). Minor variations in reason or confidence_score are acceptable.",
        )

        ruling = json.loads(consensus_raw)
        verdict = ruling.get("verdict", VERDICT_INSUFFICIENT)
        reason = ruling.get("reason", "")
        confidence = ruling.get("confidence_score", 0)

        # 4. Deterministic state transition
        claim["status"] = STATE_RESOLVED
        claim["verdict"] = verdict
        claim["verdict_reason"] = reason

        self._save_claim_dict(claim_id, claim)

        adj_data = {
            "claim_id": claim_id,
            "verdict": verdict,
            "reason": reason,
            "confidence_score": confidence,
            "adjudicated_at": "CONSENSUS_FINALIZED",
            "evidence_count": len(evidence_items),
        }
        self.claim_adjudications[claim_id] = json.dumps(adj_data)

        return verdict

    @gl.public.write
    def settle_bounty(self, claim_id: str, recipient: Address) -> str:
        """
        Settles the escrowed bounty on a resolved claim.
        Deterministic settlement rule: only callable once claim reaches RESOLVED.
        """
        claim = self._get_claim_dict(claim_id)
        if claim["status"] != STATE_RESOLVED:
            raise gl.vm.UserError(
                f"Cannot settle bounty on claim in status '{claim['status']}', must be '{STATE_RESOLVED}'"
            )

        bounty_val = (
            self.bounties[claim_id] if claim_id in self.bounties else u256(0)
        )
        if bounty_val == u256(0):
            claim["status"] = STATE_SETTLED
            self._save_claim_dict(claim_id, claim)
            return "0"

        # Mark bounty settled
        self.bounties[claim_id] = u256(0)
        self.total_bounties_paid = self.total_bounties_paid + bounty_val
        claim["status"] = STATE_SETTLED
        self._save_claim_dict(claim_id, claim)

        return str(bounty_val)

    @gl.public.write
    def cancel_claim(self, claim_id: str) -> str:
        """Cancel a claim if still in DRAFT status."""
        claim = self._get_claim_dict(claim_id)
        if str(gl.message.sender_address).lower() != claim["creator"].lower():
            raise gl.vm.UserError("Only creator can cancel")
        if claim["status"] != STATE_DRAFT:
            raise gl.vm.UserError("Cannot cancel an active or frozen claim")

        claim["status"] = STATE_CANCELLED
        self._save_claim_dict(claim_id, claim)
        return claim_id

    # --------------------------------------------------------------------------
    # Public Read / View Methods
    # --------------------------------------------------------------------------

    @gl.public.view
    def get_protocol_stats(self) -> dict:
        """Returns protocol-level metrics and runtime status."""
        return {
            "protocol_name": "GenState",
            "version": VERSION,
            "admin": str(self.admin),
            "total_claims": int(self.claim_count),
            "total_evidence": int(self.evidence_count),
            "total_escrowed": str(self.total_bounties_escrowed),
            "total_settled": str(self.total_bounties_paid),
            "supported_policies": POLICIES,
            "supported_claim_types": CLAIM_TYPES,
        }

    @gl.public.view
    def get_claim(self, claim_id: str) -> dict:
        """Returns detailed claim record by ID."""
        return self._get_claim_dict(claim_id)

    @gl.public.view
    def list_claims(self, offset: u256, limit: u256) -> list:
        """Returns paginated list of claims."""
        total = len(self.claim_ids)
        start = int(offset)
        size = int(limit)
        if start >= total:
            return []

        end = min(total, start + size)
        results = []
        for i in range(start, end):
            cid = self.claim_ids[i]
            if cid in self.claims:
                results.append(json.loads(self.claims[cid]))
        return results

    @gl.public.view
    def get_evidence_for_claim(self, claim_id: str) -> list:
        """Returns all evidence items attached to a claim."""
        ev_ids = self._get_evidence_list(claim_id)
        items = []
        for eid in ev_ids:
            if eid in self.evidence_records:
                items.append(json.loads(self.evidence_records[eid]))
        return items

    @gl.public.view
    def get_adjudication(self, claim_id: str) -> dict:
        """Returns the consensus adjudication details for a claim."""
        if claim_id not in self.claim_adjudications:
            return {
                "claim_id": claim_id,
                "verdict": "NOT_ADJUDICATED",
                "reason": "Adjudication has not been performed yet.",
            }
        return json.loads(self.claim_adjudications[claim_id])
