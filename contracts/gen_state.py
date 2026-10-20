# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

from genlayer import *
import json
import datetime
import hashlib

# ==============================================================================
# GenState Protocol: Decentralized Semantic State & Truth Adjudication
# ==============================================================================
# An intelligent state consensus contract operating on GenLayer's GenVM.
# Participants register structured state claims, bind them to deterministic
# admissibility policies, attach evidence from public web sources, and execute
# multi-validator LLM consensus to establish verifiable on-chain truth.
# ==============================================================================

VERSION = "1.4.0"

# Supported claim domain categories
CLAIM_TYPES = [
    "STATE_TRANSITION",
    "REGISTRY_RECORD",
    "FACTUAL_EVENT",
    "GOVERNANCE_EXECUTION",
    "COMPLIANCE_STATUS",
]

# Source admissibility policies
POLICY_OFFICIAL_REGISTRY = "OFFICIAL_REGISTRY"
POLICY_REGULATORY_FILING = "REGULATORY_FILING"
POLICY_MULTI_SOURCE = "MULTI_SOURCE_INDEPENDENT"
POLICY_PRIMARY_CORROB = "PRIMARY_PLUS_CORROBORATION"
POLICY_OPEN = "OPEN_PUBLIC"

POLICIES = [
    POLICY_OFFICIAL_REGISTRY,
    POLICY_REGULATORY_FILING,
    POLICY_MULTI_SOURCE,
    POLICY_PRIMARY_CORROB,
    POLICY_OPEN,
]

# Claim state lifecycle
STATE_DRAFT = "DRAFT"
STATE_EVIDENCE_OPEN = "EVIDENCE_OPEN"
STATE_ADJUDICATING = "ADJUDICATING"
STATE_RESOLVED = "RESOLVED"
STATE_SETTLED = "SETTLED"
STATE_PARTIALLY_SETTLED = "PARTIALLY_SETTLED"
STATE_CANCELLED = "CANCELLED"
STATE_REFUNDED = "REFUNDED"

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

MIN_WINDOW_SECONDS = 60
MAX_WINDOW_SECONDS = 30 * 24 * 60 * 60  # 30 days
MAX_EVIDENCE_PER_CLAIM = 10
MAX_URL_LENGTH = 500
MAX_EXPLANATION_LENGTH = 1000


@gl.evm.contract_interface
class _Recipient:
    class View:
        pass

    class Write:
        pass


def _extract_domain(url: str) -> str:
    """Extract clean lowercase domain hostname from a URL."""
    if not isinstance(url, str):
        return ""
    stripped = url.strip()
    if "://" in stripped:
        stripped = stripped.split("://", 1)[1]
    host = stripped.split("/", 1)[0].split(":", 1)[0].split("?", 1)[0].lower()
    return host


def _extract_apex_domain(url: str) -> str:
    """
    Extract registered apex domain (effective 2nd-level domain) to prevent
    treating subdomains of the same publisher as independent sources.
    Example: 'docs.example.com' -> 'example.com', 'sec.gov' -> 'sec.gov'.
    """
    host = _extract_domain(url)
    if not host:
        return ""
    parts = host.split(".")
    if len(parts) <= 2:
        return host

    # Common multi-part ccTLDs
    cctlds = (
        "co.uk", "gov.uk", "ac.uk", "org.uk",
        "gov.au", "com.au", "edu.au",
        "gov.in", "co.in", "nic.in",
        "com.br", "gov.br",
    )
    last_two = f"{parts[-2]}.{parts[-1]}"
    if last_two in cctlds and len(parts) >= 3:
        return f"{parts[-3]}.{last_two}"

    return f"{parts[-2]}.{parts[-1]}"


def _is_official_registry_domain(domain: str) -> bool:
    """Deterministic check for official government and institutional registry domains."""
    if domain.endswith(".gov") or domain.endswith(".mil") or domain.endswith(".int"):
        return True
    if domain.endswith(".gov.uk") or domain.endswith(".gov.au") or domain.endswith(".gov.in"):
        return True
    trusted = (
        "who.int", "un.org", "europa.eu", "sec.gov", "treasury.gov",
        "companieshouse.gov.uk", "justice.gov", "fda.gov", "iso.org",
        "wipo.int", "bis.org", "worldbank.org", "imf.org"
    )
    return any(domain == t or domain.endswith("." + t) for t in trusted)


def _is_regulatory_domain(domain: str) -> bool:
    """Deterministic check for official regulatory and financial filing repository domains."""
    if _is_official_registry_domain(domain):
        return True
    regulatory = (
        "sec.gov", "esma.europa.eu", "fca.org.uk", "finra.org",
        "cftc.gov", "bafin.de", "amf-france.org", "mas.gov.sg",
        "sfc.hk", "asic.gov.au", "edgar-online.com"
    )
    return any(domain == r or domain.endswith("." + r) for r in regulatory)


def _addr_str(addr) -> str:
    """Normalize Address or bytes representation to consistent lowercase hex string."""
    if isinstance(addr, bytes):
        return "0x" + addr.hex().lower()
    if hasattr(addr, "as_hex"):
        return addr.as_hex.lower()
    if hasattr(addr, "as_bytes"):
        return "0x" + addr.as_bytes.hex().lower()
    s = str(addr).lower()
    return s


def _validate_date_string(date_str: str) -> bool:
    """Validate reference_date string conforms to YYYY-MM-DD format."""
    s = date_str.strip()
    if len(s) < 10:
        return False
    parts = s[:10].split("-")
    if len(parts) != 3:
        return False
    if not (len(parts[0]) == 4 and len(parts[1]) == 2 and len(parts[2]) == 2):
        return False
    if not (parts[0].isdigit() and parts[1].isdigit() and parts[2].isdigit()):
        return False
    month, day = int(parts[1]), int(parts[2])
    return 1 <= month <= 12 and 1 <= day <= 31


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
    total_bounties_refunded: u256
    # v1.2.0: Multi-funder contribution tracking & duplicate-settlement protection
    claim_funders: TreeMap[str, str]
    funder_deposits: TreeMap[str, u256]
    recipient_settled: TreeMap[str, u256]
    # v1.3.0: Failed-transfer recovery pull pattern
    pending_recoveries: TreeMap[str, u256]
    # v1.4.0: 100% Race-free claim identification & duplicate-declaration protection
    claims_by_request_id: TreeMap[str, str]
    active_draft_declarations: TreeMap[str, str]

    def __init__(self):
        self.admin = gl.message.sender_address
        self.claim_count = u256(0)
        self.evidence_count = u256(0)
        self.total_bounties_escrowed = u256(0)
        self.total_bounties_paid = u256(0)
        self.total_bounties_refunded = u256(0)

    # --------------------------------------------------------------------------
    # Internal Helpers
    # --------------------------------------------------------------------------

    def _now(self) -> int:
        """Authoritative block timestamp extracted from message datetime metadata."""
        try:
            raw_dt = gl.message_raw.get("datetime")
            if raw_dt:
                return int(datetime.datetime.fromisoformat(raw_dt).timestamp())
        except Exception:
            pass
        return 0

    def _send_gen(self, to: Address, amount: u256, recovery_key: str = ""):
        """
        Executes native GEN movement to an EVM recipient.
        If transfer fails (e.g. non-payable contract or execution fault), safely deposits
        the amount into pending_recoveries so funds are never locked or lost.
        """
        if amount > u256(0):
            try:
                target = to if isinstance(to, Address) else Address(to)
                _Recipient(target).emit_transfer(value=amount)
            except Exception:
                # Capture un-transferred funds into pending_recoveries for pull recovery
                key = recovery_key if recovery_key else _addr_str(to)
                current = (
                    self.pending_recoveries[key]
                    if key in self.pending_recoveries
                    else u256(0)
                )
                self.pending_recoveries[key] = current + amount

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

    def _get_funders_list(self, claim_id: str) -> list:
        if claim_id not in self.claim_funders:
            return []
        raw = self.claim_funders[claim_id]
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
        request_id: str = "",
    ) -> str:
        """
        Register a new structured state assertion in DRAFT status.
        Supports optional client request_id for 100% race-free deterministic resolution.
        If request_id is omitted, prevents concurrent identical declarations in DRAFT.
        """
        c_type = claim_type.strip().upper()
        if c_type not in CLAIM_TYPES:
            raise gl.vm.UserError(
                f"Invalid claim type '{claim_type}'. Allowed: {', '.join(CLAIM_TYPES)}"
            )

        subj = subject.strip()
        pred = predicate.strip()
        val = asserted_value.strip()
        ref_date = reference_date.strip()
        req_id = request_id.strip()

        if len(subj) < 3 or len(subj) > 300:
            raise gl.vm.UserError("Subject must be between 3 and 300 characters")
        if len(pred) < 3 or len(pred) > 200:
            raise gl.vm.UserError("Predicate must be between 3 and 200 characters")
        if len(val) < 1 or len(val) > 500:
            raise gl.vm.UserError("Asserted value must be between 1 and 500 characters")
        if not _validate_date_string(ref_date):
            raise gl.vm.UserError("Reference date must be a valid date in YYYY-MM-DD format")

        caller_str = _addr_str(gl.message.sender_address)

        # 1. If unique request_id provided: enforce replay protection per creator
        if req_id:
            req_key = f"{caller_str}:{req_id}"
            if req_key in self.claims_by_request_id:
                raise gl.vm.UserError(
                    f"Duplicate declaration request: request_id '{req_id}' has already been processed for this wallet"
                )

        # 2. If no request_id provided: prevent concurrent identical assertions in DRAFT
        # so untagged declarations cannot be misidentified or race against each other
        sig_key = f"{caller_str}:{c_type}:{subj}:{pred}:{val}:{ref_date}"
        if not req_id:
            if sig_key in self.active_draft_declarations:
                existing_cid = self.active_draft_declarations[sig_key]
                if existing_cid:
                    raise gl.vm.UserError(
                        f"Concurrent identical declaration rejected: claim '{existing_cid}' with identical fields is currently in DRAFT status for this wallet. Provide a unique request_id to declare independent concurrent assertions."
                    )

        new_count = int(self.claim_count) + 1
        self.claim_count = u256(new_count)
        claim_id = f"CLAIM-{new_count}"

        claim_data = {
            "id": claim_id,
            "creator": caller_str,
            "claim_type": c_type,
            "subject": subj,
            "predicate": pred,
            "asserted_value": val,
            "reference_date": ref_date,
            "request_id": req_id,
            "source_policy": "",
            "window_seconds": 0,
            "opened_at": 0,
            "evidence_deadline": 0,
            "status": STATE_DRAFT,
            "verdict": "",
            "verdict_reason": "",
            "adjudication_time": "",
            "evidence_count": 0,
            "bounty_amount": "0",
            "funders": [],
            "qualifying_recipients": [],
            "bounty_settled_recipients": [],
        }

        self._save_claim_dict(claim_id, claim_data)
        self.claim_ids.append(claim_id)
        self.claim_evidence_ids[claim_id] = json.dumps([])
        self.claim_funders[claim_id] = json.dumps([])
        self.bounties[claim_id] = u256(0)

        if req_id:
            self.claims_by_request_id[f"{caller_str}:{req_id}"] = claim_id
        else:
            self.active_draft_declarations[sig_key] = claim_id

        return claim_id

    @gl.public.write
    def freeze_claim(
        self, claim_id: str, source_policy: str, window_seconds: u256
    ) -> str:
        """Lock the claim parameters and enforce the timed evidence submission window."""
        claim = self._get_claim_dict(claim_id)

        if _addr_str(gl.message.sender_address) != _addr_str(claim["creator"]):
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

        win_sec = int(window_seconds)
        if win_sec < MIN_WINDOW_SECONDS or win_sec > MAX_WINDOW_SECONDS:
            raise gl.vm.UserError(
                f"Evidence window must be between {MIN_WINDOW_SECONDS} and {MAX_WINDOW_SECONDS} seconds"
            )

        now_ts = self._now()
        claim["source_policy"] = pol
        claim["window_seconds"] = win_sec
        claim["opened_at"] = now_ts
        claim["evidence_deadline"] = now_ts + win_sec
        claim["status"] = STATE_EVIDENCE_OPEN

        # Clean up untagged draft reservation if present
        sig_key = f"{_addr_str(claim['creator'])}:{claim['claim_type']}:{claim['subject']}:{claim['predicate']}:{claim['asserted_value']}:{claim['reference_date']}"
        if sig_key in self.active_draft_declarations and self.active_draft_declarations[sig_key] == claim_id:
            self.active_draft_declarations[sig_key] = ""

        self._save_claim_dict(claim_id, claim)
        return claim_id

    @gl.public.write.payable
    def fund_bounty(self, claim_id: str) -> str:
        """
        Fund an escrowed bounty reward for evidence providers.
        Supports multiple individual contributors, accurately tracking each contributor's
        deposited GEN for transparent proportional or individual refund accounting.
        """
        claim = self._get_claim_dict(claim_id)
        if claim["status"] in [STATE_RESOLVED, STATE_SETTLED, STATE_CANCELLED, STATE_REFUNDED]:
            raise gl.vm.UserError(
                f"Cannot fund bounty on claim with terminal status '{claim['status']}'"
            )

        added_val = gl.message.value
        if added_val == u256(0):
            raise gl.vm.UserError("Must send native GEN value to fund bounty")

        sender_str = _addr_str(gl.message.sender_address)

        # 1. Update individual contributor balance
        deposit_key = f"{claim_id}:{sender_str}"
        current_dep = (
            self.funder_deposits[deposit_key]
            if deposit_key in self.funder_deposits
            else u256(0)
        )
        self.funder_deposits[deposit_key] = current_dep + added_val

        # 2. Maintain list of contributors
        funders = self._get_funders_list(claim_id)
        if sender_str not in funders:
            funders.append(sender_str)
            self.claim_funders[claim_id] = json.dumps(funders)

        # 3. Update total claim bounty & protocol escrow
        current_bounty = (
            self.bounties[claim_id] if claim_id in self.bounties else u256(0)
        )
        new_bounty = current_bounty + added_val
        self.bounties[claim_id] = new_bounty
        self.total_bounties_escrowed = self.total_bounties_escrowed + added_val

        claim["bounty_amount"] = str(new_bounty)
        claim["funders"] = funders
        self._save_claim_dict(claim_id, claim)

        return str(new_bounty)

    @gl.public.write
    def submit_evidence(
        self, claim_id: str, source_url: str, explanation: str
    ) -> str:
        """Submit a public web evidence link with contextual explanation during the active window."""
        claim = self._get_claim_dict(claim_id)

        if claim["status"] not in [STATE_EVIDENCE_OPEN, STATE_ADJUDICATING]:
            raise gl.vm.UserError(
                f"Evidence submission not open for claim with status '{claim['status']}'"
            )

        now_ts = self._now()
        deadline = claim.get("evidence_deadline", 0)
        if deadline > 0 and now_ts > deadline:
            raise gl.vm.UserError("Evidence submission window has closed")

        ev_list = self._get_evidence_list(claim_id)
        if len(ev_list) >= MAX_EVIDENCE_PER_CLAIM:
            raise gl.vm.UserError(
                f"Evidence submission limit reached (maximum {MAX_EVIDENCE_PER_CLAIM} records allowed)"
            )

        url = source_url.strip()
        if not (url.startswith("http://") or url.startswith("https://")):
            raise gl.vm.UserError("Source URL must begin with http:// or https://")
        if len(url) > MAX_URL_LENGTH:
            raise gl.vm.UserError(f"Source URL exceeds maximum {MAX_URL_LENGTH} characters")

        notes = explanation.strip()
        if len(notes) < 5 or len(notes) > MAX_EXPLANATION_LENGTH:
            raise gl.vm.UserError(
                f"Explanation must be between 5 and {MAX_EXPLANATION_LENGTH} characters"
            )

        sender_str = _addr_str(gl.message.sender_address)

        new_ev_count = int(self.evidence_count) + 1
        self.evidence_count = u256(new_ev_count)
        evidence_id = f"EVID-{new_ev_count}"

        ev_data = {
            "id": evidence_id,
            "claim_id": claim_id,
            "submitter": sender_str,
            "source_url": url,
            "explanation": notes,
        }

        self.evidence_records[evidence_id] = json.dumps(ev_data)

        # Update claim's evidence collection
        ev_list.append(evidence_id)
        self.claim_evidence_ids[claim_id] = json.dumps(ev_list)
        claim["evidence_count"] = len(ev_list)
        self._save_claim_dict(claim_id, claim)

        return evidence_id

    @gl.public.write
    def adjudicate(self, claim_id: str) -> str:
        """
        Executes multi-validator intelligent consensus over submitted evidence.
        Enforces:
        - Timed evidence window expiration
        - Deterministic source admissibility policies & apex-domain publisher independence
        - Mirror detection via SHA-256 content hashes
        - Persistent source content fingerprinting in stored record
        - Verbatim supporting quotation verification against retrieved source text
        - Deterministic qualifying recipient selection (submitting spam does not make one eligible)
        - Strict temporal reference date evaluation
        - Storage pre-extraction purity (zero self in non-deterministic closure)
        """
        claim = self._get_claim_dict(claim_id)

        if claim["status"] not in [STATE_EVIDENCE_OPEN, STATE_ADJUDICATING]:
            raise gl.vm.UserError(
                f"Cannot adjudicate claim in status '{claim['status']}'"
            )

        now_ts = self._now()
        deadline = claim.get("evidence_deadline", 0)
        if deadline > 0 and now_ts < deadline:
            raise gl.vm.UserError(
                "Evidence submission window is still active; premature adjudication prohibited"
            )

        ev_ids = self._get_evidence_list(claim_id)
        if len(ev_ids) == 0:
            raise gl.vm.UserError(
                "Cannot adjudicate claim without at least one submitted evidence record"
            )

        evidence_items = []
        for eid in ev_ids:
            if eid in self.evidence_records:
                evidence_items.append(json.loads(self.evidence_records[eid]))

        # ----------------------------------------------------------------------
        # DETERMINISTIC SOURCE ADMISSIBILITY & PUBLISHER INDEPENDENCE CHECKS
        # ----------------------------------------------------------------------
        domains = [_extract_domain(item.get("source_url", "")) for item in evidence_items]
        apex_domains = [_extract_apex_domain(item.get("source_url", "")) for item in evidence_items]
        distinct_domains = set(d for d in domains if d)
        distinct_apex_domains = set(a for a in apex_domains if a)
        policy = claim["source_policy"]

        policy_failure_reason = ""
        if policy == "MULTI_SOURCE_INDEPENDENT":
            if len(distinct_apex_domains) < 2:
                policy_failure_reason = (
                    f"MULTI_SOURCE_INDEPENDENT policy violated: requires at least 2 distinct independent publisher apex domains, found {len(distinct_apex_domains)}"
                )
        elif policy == "PRIMARY_PLUS_CORROBORATION":
            if len(distinct_apex_domains) < 2:
                policy_failure_reason = (
                    f"PRIMARY_PLUS_CORROBORATION policy violated: requires distinct primary and corroborating publisher domains, found {len(distinct_apex_domains)}"
                )
        elif policy == "OFFICIAL_REGISTRY":
            if not any(_is_official_registry_domain(d) for d in distinct_domains):
                policy_failure_reason = (
                    "OFFICIAL_REGISTRY policy violated: no submitted source matches verified official registry or government domains (.gov, .mil, .int, etc.)"
                )
        elif policy == "REGULATORY_FILING":
            if not any(_is_regulatory_domain(d) for d in distinct_domains):
                policy_failure_reason = (
                    "REGULATORY_FILING policy violated: no submitted source matches recognized regulatory repositories (SEC, FCA, ESMA, etc.)"
                )

        if policy_failure_reason:
            claim["status"] = STATE_RESOLVED
            claim["verdict"] = VERDICT_INSUFFICIENT
            claim["verdict_reason"] = policy_failure_reason
            claim["adjudication_time"] = str(self._now())
            claim["qualifying_recipients"] = []
            self._save_claim_dict(claim_id, claim)

            adj_data = {
                "claim_id": claim_id,
                "verdict": VERDICT_INSUFFICIENT,
                "reason": policy_failure_reason,
                "confidence_score": 0,
                "adjudicated_at": str(self._now()),
                "evidence_count": len(evidence_items),
                "source_fingerprints": [],
                "quotation_verified": False,
                "supporting_quotation": "",
                "qualifying_recipients": [],
            }
            self.claim_adjudications[claim_id] = json.dumps(adj_data)
            return VERDICT_INSUFFICIENT

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
        frozen_policy = policy
        frozen_reference_date = claim.get("reference_date", "")
        frozen_evidence = list(evidence_items)

        def leader_fn() -> str:
            # 1. Fetch web content defensively & compute SHA256 fingerprints
            evidence_summaries = []
            fingerprint_records = []
            unreachable_count = 0
            seen_content_hashes = set()
            retrieved_texts = []

            for idx, item in enumerate(frozen_evidence):
                url = item.get("source_url", "")
                note = item.get("explanation", "")
                sub = item.get("submitter", "")
                eid = item.get("id", "")
                page_text = ""
                fingerprint = "NONE"
                fetch_status = "FETCH_SUCCESS"

                try:
                    res = gl.nondet.web.get(url)
                    if hasattr(res, "status") and res.status >= 400:
                        raise gl.vm.UserError(f"HTTP status error: {res.status}")
                    raw_body = res.body.decode("utf-8", errors="ignore")
                    fingerprint = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()
                    page_text = " ".join(raw_body.split())[:12000]
                    retrieved_texts.append(page_text)

                    # Mirror detection
                    if fingerprint in seen_content_hashes:
                        fetch_status = "MIRROR_DUPLICATE"
                    else:
                        seen_content_hashes.add(fingerprint)
                except Exception:
                    unreachable_count += 1
                    fetch_status = "SOURCE_UNREACHABLE"
                    page_text = "[Web source unreachable or timed out]"

                evidence_summaries.append(
                    {
                        "index": idx,
                        "evidence_id": eid,
                        "url": url,
                        "fetch_status": fetch_status,
                        "source_sha256_fingerprint": fingerprint,
                        "content_sample": page_text[:2000],
                    }
                )

                fingerprint_records.append(
                    {
                        "evidence_id": eid,
                        "url": url,
                        "domain": _extract_domain(url),
                        "apex_domain": _extract_apex_domain(url),
                        "sha256_fingerprint": fingerprint,
                        "fetch_status": fetch_status,
                    }
                )

            # Strict fallback: if all external sources are completely unreachable, resolve SOURCE_UNAVAILABLE
            if unreachable_count == len(frozen_evidence):
                fallback_res = {
                    "verdict": "SOURCE_UNAVAILABLE",
                    "reason": "All submitted external evidence links were unreachable or timed out; self-reported context is insufficient for conclusive judgment.",
                    "confidence_score": 0,
                    "supporting_quotation": "",
                    "quotation_verified": False,
                    "qualifying_indices": [],
                    "source_fingerprints": fingerprint_records,
                }
                return json.dumps(fallback_res, sort_keys=True)

            # 2. Formulate authoritative adjudication evaluation prompt
            prompt = f"""You are an authoritative validator node in the GenState decentralized adjudication network.
Your task is to independently examine submitted public evidence and evaluate a frozen state claim.

CLAIM INFORMATION:
- Claim ID: {frozen_claim_id}
- Domain Category: {frozen_claim_type}
- Subject: {frozen_subject}
- Predicate: {frozen_predicate}
- Asserted Value: {frozen_asserted_value}
- Admissibility Policy: {frozen_policy}
- Reference Date: {frozen_reference_date}

TEMPORAL EVALUATION RULE:
The claim is asserted as of reference date '{frozen_reference_date}'. You MUST verify whether the asserted value was true AT OR AS OF THIS SPECIFIC REFERENCE DATE. If an evidence source describes a subsequent state change that occurred AFTER the reference date, you must account for this historical distinction and judge strictly against '{frozen_reference_date}'.

EVALUATION CRITERIA:
- The fetched webpage content samples and fingerprints are authoritative evidence. Submitter notes are NOT factual proof.
- If web sources contradict each other, rule CONFLICTED.
- If web sources are inconclusive or insufficient to prove the assertion under policy '{frozen_policy}', rule INSUFFICIENT_EVIDENCE.
- Extract an exact verbatim supporting quotation from the content sample that supports your ruling.
- Identify which evidence index numbers (0, 1, ...) provided genuine, qualifying, corroborating facts that substantiated your verdict. Do not include irrelevant, failed, or mirror duplicate sources.

SUBMITTED EVIDENCE SOURCES:
{json.dumps(evidence_summaries, indent=2)}

VERDICT RULES:
Choose exactly ONE primary verdict:
- "CONFIRMED": The evidence convincingly validates the asserted value as of the reference date according to policy.
- "REFUTED": The evidence proves the assertion false or contradictory to reality as of the reference date.
- "CONFLICTED": Multiple sources offer contradictory, mutually exclusive conclusions.
- "INSUFFICIENT_EVIDENCE": Available source content is too sparse, ambiguous, or lacks proof of the asserted value.
- "SOURCE_UNAVAILABLE": External sources were unreachable.

You MUST respond strictly with a valid JSON object matching this schema:
{{
  "verdict": "CONFIRMED" | "REFUTED" | "CONFLICTED" | "INSUFFICIENT_EVIDENCE" | "SOURCE_UNAVAILABLE",
  "reason": "Clear objective rationale citing examined source facts (max 100 words)",
  "confidence_score": 0 to 100,
  "supporting_quotation": "Verbatim quote from source content sample (or empty string)",
  "qualifying_indices": [0, 1]
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
                        "supporting_quotation": "",
                        "qualifying_indices": [],
                    }
            else:
                parsed = raw_res

            v = str(parsed.get("verdict", "INSUFFICIENT_EVIDENCE")).strip().upper()
            if v not in ALLOWED_VERDICTS:
                v = "INSUFFICIENT_EVIDENCE"

            # 3. Deterministic Quotation Verification
            sq = str(parsed.get("supporting_quotation", "")).strip()[:300]
            quote_verified = False
            if sq and len(sq) >= 5:
                sq_lower = sq.lower()
                for txt in retrieved_texts:
                    if sq_lower in txt.lower():
                        quote_verified = True
                        break

            # 4. Deterministic Qualifying Indices Validation
            raw_indices = parsed.get("qualifying_indices", [])
            valid_qualifying = []
            if isinstance(raw_indices, list) and v in [VERDICT_CONFIRMED, VERDICT_REFUTED]:
                for idx in raw_indices:
                    if isinstance(idx, int) and 0 <= idx < len(frozen_evidence):
                        # Must have been successfully fetched and not a duplicate mirror
                        if evidence_summaries[idx]["fetch_status"] == "FETCH_SUCCESS":
                            if idx not in valid_qualifying:
                                valid_qualifying.append(idx)

            # 5. Strict Enforcement: Block Unsupported Conclusive Outcomes
            final_reason = str(parsed.get("reason", "Adjudication finalized")).strip()[:400]
            if v in [VERDICT_CONFIRMED, VERDICT_REFUTED]:
                # 5a. Block if supporting quotation could not be verified verbatim in fetched source text
                if not quote_verified:
                    v = VERDICT_INSUFFICIENT
                    final_reason = "Unsupported conclusive outcome blocked: supporting quotation could not be verified verbatim in fetched source text."
                    valid_qualifying = []

                # 5b. Block if MULTI_SOURCE_INDEPENDENT policy is violated by mirror duplicates or insufficient domains
                elif frozen_policy == POLICY_MULTI_SOURCE:
                    unique_non_mirror_apex = set()
                    for fp in fingerprint_records:
                        if fp["fetch_status"] == "FETCH_SUCCESS":
                            unique_non_mirror_apex.add(fp["apex_domain"])
                    if len(unique_non_mirror_apex) < 2:
                        v = VERDICT_INSUFFICIENT
                        final_reason = f"Unsupported conclusive outcome blocked: MULTI_SOURCE_INDEPENDENT policy requires at least 2 independent non-mirror apex domains (found {len(unique_non_mirror_apex)})."
                        valid_qualifying = []

                # 5c. Block if all successful sources are duplicate mirrors
                else:
                    successful_fps = [
                        fp["sha256_fingerprint"]
                        for fp in fingerprint_records
                        if fp["fetch_status"] in ["FETCH_SUCCESS", "MIRROR_DUPLICATE"]
                    ]
                    if len(successful_fps) > 1 and len(set(successful_fps)) <= 1:
                        v = VERDICT_INSUFFICIENT
                        final_reason = "Unsupported conclusive outcome blocked: all submitted sources are duplicate mirrors of identical content."
                        valid_qualifying = []

            clean_result = {
                "verdict": v,
                "reason": final_reason,
                "confidence_score": int(parsed.get("confidence_score", 75)),
                "supporting_quotation": sq,
                "quotation_verified": quote_verified,
                "qualifying_indices": valid_qualifying,
                "source_fingerprints": fingerprint_records,
            }
            return json.dumps(clean_result, sort_keys=True)

        # 3. Equivalence principle consensus comparative evaluation
        consensus_raw = gl.eq_principle.prompt_comparative(
            leader_fn,
            principle="Equal if validators agree on the primary verdict (CONFIRMED, REFUTED, CONFLICTED, INSUFFICIENT_EVIDENCE, or SOURCE_UNAVAILABLE), qualifying evidence indices, and inspected materially consistent source fingerprints. Minor variations in reason or confidence_score are acceptable.",
        )

        ruling = json.loads(consensus_raw)
        verdict = ruling.get("verdict", VERDICT_INSUFFICIENT)
        reason = ruling.get("reason", "")
        confidence = ruling.get("confidence_score", 0)
        supporting_quote = ruling.get("supporting_quotation", "")
        quote_verified = bool(ruling.get("quotation_verified", False))
        source_fps = ruling.get("source_fingerprints", [])
        qualifying_indices = ruling.get("qualifying_indices", [])

        # Defense-in-depth: Deterministically block unsupported conclusive outcomes on contract state level
        if verdict in [VERDICT_CONFIRMED, VERDICT_REFUTED]:
            if not quote_verified:
                verdict = VERDICT_INSUFFICIENT
                reason = "Unsupported conclusive outcome blocked: supporting quotation could not be verified verbatim in fetched source text."
                qualifying_indices = []
            elif policy == POLICY_MULTI_SOURCE:
                unique_non_mirror_apex = set()
                for fp in source_fps:
                    if fp.get("fetch_status") == "FETCH_SUCCESS":
                        unique_non_mirror_apex.add(fp.get("apex_domain", ""))
                if len(unique_non_mirror_apex) < 2:
                    verdict = VERDICT_INSUFFICIENT
                    reason = f"Unsupported conclusive outcome blocked: MULTI_SOURCE_INDEPENDENT policy requires at least 2 independent non-mirror apex domains (found {len(unique_non_mirror_apex)})."
                    qualifying_indices = []
            else:
                successful_fps = [
                    fp.get("sha256_fingerprint")
                    for fp in source_fps
                    if fp.get("fetch_status") in ["FETCH_SUCCESS", "MIRROR_DUPLICATE"]
                ]
                if len(successful_fps) > 1 and len(set(successful_fps)) <= 1:
                    verdict = VERDICT_INSUFFICIENT
                    reason = "Unsupported conclusive outcome blocked: all submitted sources are duplicate mirrors of identical content."
                    qualifying_indices = []

        # Map qualifying indices to submitter addresses
        qualifying_submitters = []
        for idx in qualifying_indices:
            if 0 <= idx < len(evidence_items):
                sub = _addr_str(evidence_items[idx].get("submitter", ""))
                if sub and sub not in qualifying_submitters:
                    qualifying_submitters.append(sub)

        # 4. Deterministic state transition
        claim["status"] = STATE_RESOLVED
        claim["verdict"] = verdict
        claim["verdict_reason"] = reason
        claim["adjudication_time"] = str(self._now())
        claim["qualifying_recipients"] = qualifying_submitters

        self._save_claim_dict(claim_id, claim)

        # Persist full authoritative adjudication record WITH fingerprints & quotation verification
        adj_data = {
            "claim_id": claim_id,
            "verdict": verdict,
            "reason": reason,
            "confidence_score": confidence,
            "adjudicated_at": str(self._now()),
            "evidence_count": len(evidence_items),
            "source_fingerprints": source_fps,  # PERSISTED ON-CHAIN
            "quotation_verified": quote_verified,  # PERSISTED ON-CHAIN
            "supporting_quotation": supporting_quote,
            "qualifying_recipients": qualifying_submitters,
        }
        self.claim_adjudications[claim_id] = json.dumps(adj_data)

        return verdict

    @gl.public.write
    def settle_bounty(self, claim_id: str, recipient: Address) -> str:
        """
        Settles the escrowed bounty on a conclusively resolved claim.
        Executes genuine native GEN transfer to the eligible evidence recipient.
        Enforces:
        - Conclusive verdict (CONFIRMED or REFUTED)
        - Caller authorization
        - Deterministic reward eligibility (recipient must have provided qualifying evidence)
        - Proportional allocation if multiple qualifying recipients exist
        - Duplicate-payment protection per recipient
        """
        claim = self._get_claim_dict(claim_id)
        if claim["status"] not in [STATE_RESOLVED, STATE_PARTIALLY_SETTLED]:
            raise gl.vm.UserError(
                f"Cannot settle bounty on claim in status '{claim['status']}', must be '{STATE_RESOLVED}' or '{STATE_PARTIALLY_SETTLED}'"
            )

        verdict = claim.get("verdict", "")
        if verdict not in [VERDICT_CONFIRMED, VERDICT_REFUTED]:
            raise gl.vm.UserError(
                f"Cannot settle bounty on claim with inconclusive verdict '{verdict}'. Call refund_bounty() instead."
            )

        caller_str = _addr_str(gl.message.sender_address)
        creator_str = _addr_str(claim.get("creator", ""))
        funders = self._get_funders_list(claim_id)
        recip_str = _addr_str(recipient)

        # Authorization: caller must be creator, one of the funders, or the recipient
        if caller_str != creator_str and caller_str not in funders and caller_str != recip_str:
            raise gl.vm.UserError("Caller is not authorized to settle bounty on this claim")

        # Deterministic recipient eligibility: recipient must have submitted qualifying evidence
        qualifying = claim.get("qualifying_recipients", [])
        if recip_str not in qualifying:
            raise gl.vm.UserError(
                "Proposed recipient did not provide qualifying evidence that supported the verdict"
            )

        # Duplicate payment protection
        settle_key = f"{claim_id}:{recip_str}"
        already_paid = (
            self.recipient_settled[settle_key]
            if settle_key in self.recipient_settled
            else u256(0)
        )
        if already_paid > u256(0):
            raise gl.vm.UserError("Bounty already settled to this recipient")

        total_bounty_remaining = (
            self.bounties[claim_id] if claim_id in self.bounties else u256(0)
        )
        if total_bounty_remaining == u256(0):
            raise gl.vm.UserError("No escrowed bounty remaining to settle")

        # Calculate recipient's deterministic allocation share
        num_qualifying = len(qualifying)
        settled_list = claim.get("bounty_settled_recipients", [])
        unsettled_count = num_qualifying - len(settled_list)
        if unsettled_count <= 1:
            payout_share = total_bounty_remaining
        else:
            payout_share = total_bounty_remaining // u256(unsettled_count)
        if payout_share == u256(0):
            payout_share = total_bounty_remaining

        # Checks-Effects: Update state FIRST to prevent duplicate payments
        self.recipient_settled[settle_key] = payout_share
        self.bounties[claim_id] = total_bounty_remaining - payout_share
        self.total_bounties_escrowed = self.total_bounties_escrowed - payout_share
        self.total_bounties_paid = self.total_bounties_paid + payout_share

        if recip_str not in settled_list:
            settled_list.append(recip_str)
        claim["bounty_settled_recipients"] = settled_list

        if self.bounties[claim_id] == u256(0) or len(settled_list) >= num_qualifying:
            claim["status"] = STATE_SETTLED
        else:
            claim["status"] = STATE_PARTIALLY_SETTLED

        claim["bounty_amount"] = str(self.bounties[claim_id])
        self._save_claim_dict(claim_id, claim)

        # Interactions: Execute native GEN movement
        self._send_gen(recipient, payout_share, recovery_key=recip_str)

        return str(payout_share)

    @gl.public.write
    def cancel_claim(self, claim_id: str) -> str:
        """
        Cancel a claim if still in DRAFT status, refunding 100% of deposited GEN
        to each individual contributor according to their exact recorded deposits.
        """
        claim = self._get_claim_dict(claim_id)
        if _addr_str(gl.message.sender_address) != _addr_str(claim["creator"]):
            raise gl.vm.UserError("Only creator can cancel")
        if claim["status"] != STATE_DRAFT:
            raise gl.vm.UserError("Cannot cancel an active or frozen claim")

        # Refund each contributor their exact deposit
        funders = self._get_funders_list(claim_id)
        total_refunded_here = u256(0)
        for f in funders:
            dep_key = f"{claim_id}:{f}"
            dep_val = (
                self.funder_deposits[dep_key]
                if dep_key in self.funder_deposits
                else u256(0)
            )
            if dep_val > u256(0):
                self.funder_deposits[dep_key] = u256(0)
                total_refunded_here = total_refunded_here + dep_val
                self._send_gen(Address(f), dep_val, recovery_key=f)

        if total_refunded_here > u256(0):
            self.bounties[claim_id] = u256(0)
            self.total_bounties_escrowed = self.total_bounties_escrowed - total_refunded_here
            self.total_bounties_refunded = self.total_bounties_refunded + total_refunded_here

        claim["bounty_amount"] = "0"
        claim["status"] = STATE_CANCELLED

        # Clean up untagged draft reservation if present
        sig_key = f"{_addr_str(claim['creator'])}:{claim['claim_type']}:{claim['subject']}:{claim['predicate']}:{claim['asserted_value']}:{claim['reference_date']}"
        if sig_key in self.active_draft_declarations and self.active_draft_declarations[sig_key] == claim_id:
            self.active_draft_declarations[sig_key] = ""

        self._save_claim_dict(claim_id, claim)
        return claim_id

    @gl.public.write
    def refund_bounty(self, claim_id: str) -> str:
        """
        Safely refunds escrowed bounty to contributors if the claim reached a terminal
        inconclusive state (CANCELLED, INSUFFICIENT_EVIDENCE, SOURCE_UNAVAILABLE, CONFLICTED)
        or if the evidence window expired without adjudication.
        Returns each contributor their exact individual deposited share.
        """
        claim = self._get_claim_dict(claim_id)
        caller_str = _addr_str(gl.message.sender_address)
        creator_str = _addr_str(claim.get("creator", ""))
        funders = self._get_funders_list(claim_id)

        if caller_str != creator_str and caller_str not in funders:
            raise gl.vm.UserError("Only a bounty contributor or claim creator can request a refund")

        total_bounty = (
            self.bounties[claim_id] if claim_id in self.bounties else u256(0)
        )
        if total_bounty == u256(0):
            raise gl.vm.UserError("No escrowed bounty available to refund")

        is_cancelled = claim["status"] == STATE_CANCELLED
        is_inconclusive = claim["status"] == STATE_RESOLVED and claim.get("verdict") in [
            VERDICT_INSUFFICIENT,
            VERDICT_UNAVAILABLE,
            VERDICT_CONFLICTED,
        ]
        deadline = claim.get("evidence_deadline", 0)
        is_expired = (
            claim["status"] == STATE_EVIDENCE_OPEN
            and deadline > 0
            and self._now() > deadline + 86400
        )

        if not (is_cancelled or is_inconclusive or is_expired):
            raise gl.vm.UserError(
                f"Cannot refund bounty on claim with status '{claim['status']}' and verdict '{claim.get('verdict')}'"
            )

        # Refund each contributor their exact deposit
        total_refunded_here = u256(0)
        for f in funders:
            dep_key = f"{claim_id}:{f}"
            dep_val = (
                self.funder_deposits[dep_key]
                if dep_key in self.funder_deposits
                else u256(0)
            )
            if dep_val > u256(0):
                self.funder_deposits[dep_key] = u256(0)
                total_refunded_here = total_refunded_here + dep_val
                self._send_gen(Address(f), dep_val, recovery_key=f)

        if total_refunded_here == u256(0):
            raise gl.vm.UserError("No remaining contributor balances to refund")

        # Checks-Effects: Update state
        self.bounties[claim_id] = u256(0)
        self.total_bounties_escrowed = self.total_bounties_escrowed - total_refunded_here
        self.total_bounties_refunded = self.total_bounties_refunded + total_refunded_here
        claim["bounty_amount"] = "0"
        claim["status"] = STATE_REFUNDED
        self._save_claim_dict(claim_id, claim)

        return str(total_refunded_here)

    @gl.public.write
    def recover_failed_transfer(self, recipient: Address) -> str:
        """
        Pull-pattern recovery for un-transferred funds resulting from a failed transfer.
        Enforces caller authorization: caller must be recipient or protocol admin.
        """
        recip_str = _addr_str(recipient)
        caller_str = _addr_str(gl.message.sender_address)
        admin_str = _addr_str(self.admin)
        if caller_str != recip_str and caller_str != admin_str:
            raise gl.vm.UserError("Only the recipient or protocol admin can recover failed transfers")

        pending = (
            self.pending_recoveries[recip_str]
            if recip_str in self.pending_recoveries
            else u256(0)
        )
        if pending == u256(0):
            raise gl.vm.UserError("No pending recoverable funds for this recipient")

        # Checks-Effects: Clear pending balance first
        self.pending_recoveries[recip_str] = u256(0)

        # Interactions: Execute native transfer directly
        target = recipient if isinstance(recipient, Address) else Address(recip_str)
        _Recipient(target).emit_transfer(value=pending)

        return str(pending)

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
            "total_refunded": str(self.total_bounties_refunded),
            "supported_policies": POLICIES,
            "supported_claim_types": CLAIM_TYPES,
        }

    @gl.public.view
    def get_claim(self, claim_id: str) -> dict:
        """Returns detailed claim record by ID."""
        claim = self._get_claim_dict(claim_id)
        if claim_id in self.bounties:
            claim["bounty_amount"] = str(self.bounties[claim_id])
        return claim

    @gl.public.view
    def get_claim_funders(self, claim_id: str) -> list:
        """Returns list of contributors and their deposited amounts for a claim."""
        funders = self._get_funders_list(claim_id)
        results = []
        for f in funders:
            dep_key = f"{claim_id}:{f}"
            amount = (
                str(self.funder_deposits[dep_key])
                if dep_key in self.funder_deposits
                else "0"
            )
            results.append({"funder": f, "amount": amount})
        return results

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
                "source_fingerprints": [],
                "quotation_verified": False,
                "supporting_quotation": "",
                "qualifying_recipients": [],
            }
        return json.loads(self.claim_adjudications[claim_id])

    @gl.public.view
    def get_pending_recovery(self, recipient: Address) -> str:
        """Returns pending recoverable balance for an address in wei."""
        recip_str = _addr_str(recipient)
        pending = (
            self.pending_recoveries[recip_str]
            if recip_str in self.pending_recoveries
            else u256(0)
        )
        return str(pending)

    @gl.public.view
    def get_claim_by_request_id(self, creator: Address, request_id: str) -> dict:
        """
        Deterministically queries claim by creator address and unique client request ID.
        Guarantees 100% race-free resolution even if identical declarations are submitted.
        """
        c_addr = _addr_str(creator)
        req = request_id.strip()
        key = f"{c_addr}:{req}"
        if key not in self.claims_by_request_id:
            raise gl.vm.UserError(
                f"No claim found for request_id '{request_id}' and creator '{c_addr}'"
            )
        claim_id = self.claims_by_request_id[key]
        return self._get_claim_dict(claim_id)


