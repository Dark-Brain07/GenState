import React, { useState, useEffect } from 'react';
import {
  ShieldCheck,
  Scale,
  FileCheck2,
  ExternalLink,
  Coins,
  Send,
  Search,
  CheckCircle2,
  HelpCircle,
  XCircle,
  X,
  Copy,
  PlusCircle,
  Lock,
  Layers,
  Activity,
  Wallet,
  Sparkles,
  BookOpen,
  RefreshCw,
  Loader2,
  AlertTriangle,
  Award,
} from 'lucide-react';
import genstateLogo from './assets/genstate-logo.jpg';
import { GENSTATE_CONFIG } from './lib/config';
import { genStateService } from './lib/genstate-service';
import type {
  StateClaim,
  EvidenceRecord,
  AdjudicationResult,
  ProtocolStats,
  ClaimType,
  AdmissibilityPolicy,
} from './types/genstate';

export function App() {
  const [activeTab, setActiveTab] = useState<'explorer' | 'declare' | 'evidence' | 'adjudicate' | 'docs'>('explorer');
  const [claims, setClaims] = useState<StateClaim[]>([]);
  const [selectedClaimId, setSelectedClaimId] = useState<string>('');
  const [stats, setStats] = useState<ProtocolStats | null>(null);
  const [selectedEvidence, setSelectedEvidence] = useState<EvidenceRecord[]>([]);
  const [selectedAdjudication, setSelectedAdjudication] = useState<AdjudicationResult | null>(null);

  const [loading, setLoading] = useState<boolean>(true);
  const [refreshing, setRefreshing] = useState<boolean>(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterPolicy, setFilterPolicy] = useState('ALL');
  const [filterStatus, setFilterStatus] = useState('ALL');

  // Wallet State - Starts DISCONNECTED by default
  const [walletConnected, setWalletConnected] = useState<boolean>(false);
  const [walletAddress, setWalletAddress] = useState<string>('');
  const [walletBalance, setWalletBalance] = useState<string>('0.0000 GEN');
  const [showWalletModal, setShowWalletModal] = useState<boolean>(false);
  const [connectingWallet, setConnectingWallet] = useState<boolean>(false);
  const [copyFeedback, setCopyFeedback] = useState(false);

  // Declare Form State
  const [newClaimType, setNewClaimType] = useState<ClaimType>('REGISTRY_RECORD');
  const [newSubject, setNewSubject] = useState('');
  const [newPredicate, setNewPredicate] = useState('');
  const [newAssertedValue, setNewAssertedValue] = useState('');
  const [newReferenceDate, setNewReferenceDate] = useState(new Date().toISOString().split('T')[0]);
  const [newPolicy, setNewPolicy] = useState<AdmissibilityPolicy>('OFFICIAL_REGISTRY');
  const [freezeImmediately, setFreezeImmediately] = useState(true);
  const [isDeclaring, setIsDeclaring] = useState(false);
  const [declareSuccess, setDeclareSuccess] = useState<{ txHash: string; claimId: string } | null>(null);

  // Evidence Form State
  const [targetClaimId, setTargetClaimId] = useState<string>('');
  const [sourceUrl, setSourceUrl] = useState('');
  const [explanation, setExplanation] = useState('');
  const [isSubmittingEvidence, setIsSubmittingEvidence] = useState(false);
  const [evidenceSuccess, setEvidenceSuccess] = useState<{ txHash: string } | null>(null);

  // Adjudication Console State
  const [adjClaimId, setAdjClaimId] = useState<string>('');
  const [isAdjudicating, setIsAdjudicating] = useState<boolean>(false);
  const [adjudicationSuccess, setAdjudicationSuccess] = useState<{ txHash: string; verdict: string } | null>(null);

  // Network Guard & Financial Settlement State
  const [isWrongNetwork, setIsWrongNetwork] = useState<boolean>(false);
  const [showFundModal, setShowFundModal] = useState<boolean>(false);
  const [fundAmountGen, setFundAmountGen] = useState<string>('0.2');
  const [isFunding, setIsFunding] = useState<boolean>(false);
  const [showSettleModal, setShowSettleModal] = useState<boolean>(false);
  const [selectedRecipient, setSelectedRecipient] = useState<string>('');
  const [isSettling, setIsSettling] = useState<boolean>(false);
  const [isRefunding, setIsRefunding] = useState<boolean>(false);
  const [isCancelling, setIsCancelling] = useState<boolean>(false);
  const [isFreezing, setIsFreezing] = useState<boolean>(false);

  // Failed-Transfer Recovery State (v1.3.0)
  const [pendingRecoveryWei, setPendingRecoveryWei] = useState<string>('0');
  const [isRecovering, setIsRecovering] = useState<boolean>(false);

  // Load Real Data from StudioNet
  const loadBlockchainData = async (silent = false) => {
    if (!silent) setLoading(true);
    setRefreshing(true);
    try {
      if (genStateService.isConnected()) {
        const addr = genStateService.getAccountAddress();
        setWalletAddress(addr);
        const bal = await genStateService.ensureBalance();
        setWalletBalance(bal);
        setWalletConnected(true);
        const pending = await genStateService.getPendingRecovery(addr);
        setPendingRecoveryWei(pending);
      }

      const [protocolStats, claimsList] = await Promise.all([
        genStateService.fetchProtocolStats(),
        genStateService.fetchClaims(0, 50),
      ]);

      setStats(protocolStats);
      setClaims(claimsList);

      if (claimsList.length > 0 && !selectedClaimId) {
        setSelectedClaimId(claimsList[0].id);
        setTargetClaimId(claimsList[0].id);
        setAdjClaimId(claimsList[0].id);
      }
    } catch (err) {
      console.error('Failed to load on-chain state from StudioNet:', err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    loadBlockchainData();
  }, []);

  // Fetch Evidence and Adjudication when selected claim changes
  useEffect(() => {
    if (!selectedClaimId) return;
    const fetchDetails = async () => {
      try {
        const [evList, adjRes] = await Promise.all([
          genStateService.fetchEvidence(selectedClaimId),
          genStateService.fetchAdjudication(selectedClaimId),
        ]);
        setSelectedEvidence(evList);
        setSelectedAdjudication(adjRes);
      } catch (e) {
        console.error('Error fetching claim details:', e);
      }
    };
    fetchDetails();
  }, [selectedClaimId]);

  const selectedClaim = claims.find((c) => c.id === selectedClaimId);

  const handleCopyContract = () => {
    navigator.clipboard.writeText(GENSTATE_CONFIG.contractAddress);
    setCopyFeedback(true);
    setTimeout(() => setCopyFeedback(false), 2000);
  };

  const handleConnect = async (type: 'studionet' | 'browser') => {
    setConnectingWallet(true);
    try {
      const res = await genStateService.connectWallet(type);
      setWalletAddress(res.address);
      setWalletBalance(res.balance);
      setWalletConnected(true);
      setShowWalletModal(false);
    } catch (err: any) {
      alert(`Wallet connection failed: ${err.message || err}`);
    } finally {
      setConnectingWallet(false);
    }
  };

  const handleDisconnect = () => {
    genStateService.disconnectWallet();
    setWalletConnected(false);
    setWalletAddress('');
    setWalletBalance('0.0000 GEN');
  };

  // Synchronize browser wallet account or network switch dynamically
  useEffect(() => {
    if (typeof window === 'undefined' || !(window as any).ethereum) return;
    const ethereum = (window as any).ethereum;

    const checkNetwork = async () => {
      if (typeof window !== 'undefined' && (window as any).ethereum && walletConnected && genStateService.getConnectedType() === 'browser') {
        try {
          const chainId = await (window as any).ethereum.request({ method: 'eth_chainId' });
          const isStudioNet = chainId === '0xf22f' || chainId === '61999' || chainId === 61999;
          setIsWrongNetwork(!isStudioNet);
        } catch {
          setIsWrongNetwork(false);
        }
      } else {
        setIsWrongNetwork(false);
      }
    };
    checkNetwork();

    const handleAccountsChanged = async (accounts: string[]) => {
      if (!accounts || accounts.length === 0) {
        handleDisconnect();
      } else {
        const newAddr = accounts[0];
        setWalletAddress(newAddr);
        setWalletConnected(true);
        const bal = await genStateService.setBrowserAccount(newAddr);
        setWalletBalance(bal);
        await checkNetwork();
        await loadBlockchainData(true);
      }
    };

    const handleChainChanged = async () => {
      await checkNetwork();
      if (walletConnected) {
        const bal = await genStateService.ensureBalance();
        setWalletBalance(bal);
        await loadBlockchainData(true);
      }
    };

    ethereum.on?.('accountsChanged', handleAccountsChanged);
    ethereum.on?.('chainChanged', handleChainChanged);

    return () => {
      ethereum.removeListener?.('accountsChanged', handleAccountsChanged);
      ethereum.removeListener?.('chainChanged', handleChainChanged);
    };
  }, [walletConnected]);

  // Real On-Chain Failed Transfer Recovery Handler (v1.3.0)
  const handleRecoverFunds = async () => {
    if (isWrongNetwork) {
      alert("Please switch your wallet network to GenLayer StudioNet before submitting transactions.");
      await genStateService.switchOrAddStudioNet();
      return;
    }
    setIsRecovering(true);
    try {
      const res = await genStateService.recoverFailedTransfer();
      alert(`Recovery transaction successful! Recovered un-transferred funds.\nTx Hash: ${res.txHash}`);
      await loadBlockchainData(true);
    } catch (err: any) {
      alert(`Recovery error: ${err.message || err}`);
    } finally {
      setIsRecovering(false);
    }
  };

  // Real On-Chain Fund Bounty Handler
  const handleFundBountySubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (isWrongNetwork) {
      alert("Please switch to GenLayer StudioNet (Chain ID 61999) before submitting transactions.");
      await genStateService.switchOrAddStudioNet();
      return;
    }
    if (!selectedClaimId || !fundAmountGen || parseFloat(fundAmountGen) <= 0) return;

    setIsFunding(true);
    try {
      const amountWei = BigInt(Math.floor(parseFloat(fundAmountGen) * 1e18));
      await genStateService.fundBounty(selectedClaimId, amountWei);
      alert(`Bounty of ${fundAmountGen} GEN successfully funded into escrow!`);
      setShowFundModal(false);
      await loadBlockchainData(true);
    } catch (err: any) {
      alert(`Funding transaction error: ${err.message || err}`);
    } finally {
      setIsFunding(false);
    }
  };

  // Real On-Chain Settle Bounty Handler
  const handleSettleBountySubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (isWrongNetwork) {
      alert("Please switch to GenLayer StudioNet (Chain ID 61999) before submitting transactions.");
      await genStateService.switchOrAddStudioNet();
      return;
    }
    if (!selectedClaimId || !selectedRecipient) return;

    setIsSettling(true);
    try {
      await genStateService.settleBounty(selectedClaimId, selectedRecipient);
      alert(`Bounty share successfully settled on-chain to ${selectedRecipient}!`);
      setShowSettleModal(false);
      await loadBlockchainData(true);
    } catch (err: any) {
      alert(`Settlement transaction error: ${err.message || err}`);
    } finally {
      setIsSettling(false);
    }
  };

  // Real On-Chain Refund Bounty Handler
  const handleRefundBounty = async (claimId: string) => {
    if (isWrongNetwork) {
      alert("Please switch to GenLayer StudioNet (Chain ID 61999) before submitting transactions.");
      await genStateService.switchOrAddStudioNet();
      return;
    }
    if (!confirm("Are you sure you want to refund this claim's escrowed bounty to contributors?")) return;

    setIsRefunding(true);
    try {
      await genStateService.refundBounty(claimId);
      alert("Escrowed bounty successfully refunded to contributors on StudioNet!");
      await loadBlockchainData(true);
    } catch (err: any) {
      alert(`Refund transaction error: ${err.message || err}`);
    } finally {
      setIsRefunding(false);
    }
  };

  // Real On-Chain Cancel Claim Handler
  const handleCancelClaim = async (claimId: string) => {
    if (isWrongNetwork) {
      alert("Please switch to GenLayer StudioNet (Chain ID 61999) before submitting transactions.");
      await genStateService.switchOrAddStudioNet();
      return;
    }
    if (!confirm("Are you sure you want to cancel this DRAFT claim? Deposited GEN will be automatically refunded.")) return;

    setIsCancelling(true);
    try {
      await genStateService.cancelClaim(claimId);
      alert("Claim successfully cancelled and deposited GEN refunded on StudioNet!");
      await loadBlockchainData(true);
    } catch (err: any) {
      alert(`Cancellation transaction error: ${err.message || err}`);
    } finally {
      setIsCancelling(false);
    }
  };

  // Real On-Chain Freeze Claim Handler
  const handleFreezeClaim = async (claimId: string, policy: string, windowSeconds = 86400) => {
    if (isWrongNetwork) {
      alert("Please switch to GenLayer StudioNet (Chain ID 61999) before submitting transactions.");
      await genStateService.switchOrAddStudioNet();
      return;
    }

    setIsFreezing(true);
    try {
      await genStateService.freezeClaim(claimId, policy, windowSeconds);
      alert(`Claim ${claimId} successfully frozen with ${policy} policy and evidence window opened!`);
      await loadBlockchainData(true);
    } catch (err: any) {
      alert(`Freeze transaction error: ${err.message || err}`);
    } finally {
      setIsFreezing(false);
    }
  };

  // Real On-Chain Declare Handler
  const handleDeclareSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (isWrongNetwork) {
      alert("Please switch to GenLayer StudioNet (Chain ID 61999) before submitting transactions.");
      await genStateService.switchOrAddStudioNet();
      return;
    }
    if (!newSubject || !newPredicate || !newAssertedValue) return;

    setIsDeclaring(true);
    setDeclareSuccess(null);

    try {
      const res = await genStateService.declareClaim(
        newClaimType,
        newSubject,
        newPredicate,
        newAssertedValue,
        newReferenceDate
      );

      if (freezeImmediately) {
        await genStateService.freezeClaim(res.claimId, newPolicy, 86400);
      }

      setDeclareSuccess(res);
      setNewSubject('');
      setNewPredicate('');
      setNewAssertedValue('');
      await loadBlockchainData(true);
      setSelectedClaimId(res.claimId);
      setTargetClaimId(res.claimId);
      setAdjClaimId(res.claimId);
      alert(`Claim ${res.claimId} successfully registered on GenLayer StudioNet!\nTx Hash: ${res.txHash}`);
    } catch (err: any) {
      alert(`On-chain transaction error: ${err.message || err}`);
    } finally {
      setIsDeclaring(false);
    }
  };

  // Real On-Chain Submit Evidence Handler
  const handleEvidenceSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (isWrongNetwork) {
      alert("Please switch to GenLayer StudioNet (Chain ID 61999) before submitting transactions.");
      await genStateService.switchOrAddStudioNet();
      return;
    }
    if (!sourceUrl || !explanation || !targetClaimId) return;

    setIsSubmittingEvidence(true);
    setEvidenceSuccess(null);

    try {
      const res = await genStateService.submitEvidence(targetClaimId, sourceUrl, explanation);
      setEvidenceSuccess(res);
      setSourceUrl('');
      setExplanation('');
      await loadBlockchainData(true);
      if (selectedClaimId === targetClaimId) {
        const evs = await genStateService.fetchEvidence(targetClaimId);
        setSelectedEvidence(evs);
      }
    } catch (err: any) {
      alert(`Evidence submission error: ${err.message || err}`);
    } finally {
      setIsSubmittingEvidence(false);
    }
  };

  // Real On-Chain Run Adjudication Handler
  const handleRunAdjudication = async (claimId: string) => {
    if (isWrongNetwork) {
      alert("Please switch to GenLayer StudioNet (Chain ID 61999) before submitting transactions.");
      await genStateService.switchOrAddStudioNet();
      return;
    }
    setIsAdjudicating(true);
    setAdjudicationSuccess(null);

    try {
      const res = await genStateService.adjudicateClaim(claimId);
      setAdjudicationSuccess(res);
      await loadBlockchainData(true);
      if (selectedClaimId === claimId) {
        const adj = await genStateService.fetchAdjudication(claimId);
        setSelectedAdjudication(adj);
      }
    } catch (err: any) {
      alert(`Adjudication error: ${err.message || err}`);
    } finally {
      setIsAdjudicating(false);
    }
  };

  // Filtered claims
  const filteredClaims = claims.filter((c) => {
    const matchesSearch =
      c.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      c.subject.toLowerCase().includes(searchQuery.toLowerCase()) ||
      c.predicate.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesPolicy = filterPolicy === 'ALL' || c.source_policy === filterPolicy;
    const matchesStatus = filterStatus === 'ALL' || c.status === filterStatus;
    return matchesSearch && matchesPolicy && matchesStatus;
  });

  return (
    <div className="min-h-screen">
      {/* Top Navbar */}
      <header className="top-navbar">
        <div className="nav-inner">
          <div className="nav-brand">
            <div className="brand-icon-box">
              <img src={genstateLogo} alt="GenState Protocol Emblem" className="brand-logo-img" />
            </div>
            <div>
              <div className="brand-title">
                GEN<span>STATE</span>
              </div>
              <div className="brand-subtitle">Semantic State Adjudication</div>
            </div>
          </div>

          <div className="nav-actions">
            <button
              id="btn-sync-chain"
              onClick={() => loadBlockchainData(true)}
              className="network-pill"
              style={{ cursor: 'pointer', background: 'rgba(255, 255, 255, 0.05)', color: '#38bdf8' }}
              title="Refresh from StudioNet"
            >
              <RefreshCw size={13} className={refreshing ? 'animate-spin' : ''} />
              <span>Sync Chain</span>
            </button>

            <div className="network-pill">
              <span className="status-dot"></span>
              <span>StudioNet (Chain {GENSTATE_CONFIG.chainId})</span>
            </div>

            <button
              onClick={handleCopyContract}
              className="network-pill"
              title="Click to copy contract address"
              style={{ cursor: 'pointer', background: 'rgba(255, 255, 255, 0.05)', color: '#94a3b8' }}
            >
              <Copy size={13} />
              <span>
                {GENSTATE_CONFIG.contractAddress.slice(0, 6)}...{GENSTATE_CONFIG.contractAddress.slice(-4)}
              </span>
              {copyFeedback && <span style={{ color: '#10b981' }}>Copied!</span>}
            </button>

            <a
              href={GENSTATE_CONFIG.explorerUrl}
              target="_blank"
              rel="noreferrer"
              className="wallet-btn"
              title="View on GenLayer Explorer"
            >
              <ExternalLink size={15} />
              <span>Explorer</span>
            </a>

            {walletConnected ? (
              <div className="wallet-group">
                <div className="wallet-pill-connected">
                  <span className="status-dot"></span>
                  <span>
                    {walletAddress.slice(0, 6)}...{walletAddress.slice(-4)}
                  </span>
                  <span style={{ color: '#38bdf8', fontSize: '11px', marginLeft: '4px' }}>
                    ({walletBalance})
                  </span>
                </div>
                <button
                  id="btn-disconnect-wallet"
                  onClick={handleDisconnect}
                  className="disconnect-btn"
                  title="Disconnect active wallet"
                >
                  Disconnect
                </button>
              </div>
            ) : (
              <button
                id="btn-connect-wallet"
                onClick={() => setShowWalletModal(true)}
                className="wallet-btn connect-glow"
              >
                <Wallet size={16} />
                <span>Connect Wallet</span>
              </button>
            )}
          </div>
        </div>
      </header>

      {/* Main Container */}
      <main className="app-container">
        {/* Network Mismatch Banner */}
        {isWrongNetwork && (
          <div
            style={{
              background: 'rgba(239, 68, 68, 0.15)',
              border: '1px solid #ef4444',
              borderRadius: '8px',
              padding: '12px 18px',
              marginBottom: '20px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              gap: '12px',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <AlertTriangle size={20} color="#f87171" />
              <span style={{ fontSize: '13px', color: '#fecaca' }}>
                <strong>Network Mismatch:</strong> Your browser wallet is not connected to GenLayer StudioNet (Chain ID 61999). Transactions will revert unless switched.
              </span>
            </div>
            <button
              className="btn-primary"
              style={{ padding: '6px 14px', fontSize: '12px', background: '#dc2626', borderColor: '#ef4444', whiteSpace: 'nowrap' }}
              onClick={() => genStateService.switchOrAddStudioNet()}
            >
              Switch to StudioNet
            </button>
          </div>
        )}

        {/* Failed-Transfer Recovery Banner (v1.3.0) */}
        {BigInt(pendingRecoveryWei || '0') > 0n && (
          <div
            style={{
              background: 'rgba(234, 179, 8, 0.15)',
              border: '1px solid #eab308',
              borderRadius: '8px',
              padding: '12px 18px',
              marginBottom: '20px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              gap: '12px',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <Coins size={20} color="#facc15" />
              <span style={{ fontSize: '13px', color: '#fef08a' }}>
                <strong>Pending Recoverable Balance:</strong> You have{' '}
                <strong>{(Number(pendingRecoveryWei) / 1e18).toFixed(4)} GEN</strong> in failed-transfer escrow. Click below to pull and recover your funds.
              </span>
            </div>
            <button
              id="btn-recover-funds"
              className="btn-primary"
              disabled={isRecovering || isWrongNetwork}
              style={{
                padding: '6px 14px',
                fontSize: '12px',
                background: '#ca8a04',
                borderColor: '#eab308',
                whiteSpace: 'nowrap',
              }}
              onClick={handleRecoverFunds}
            >
              {isRecovering ? 'Recovering...' : 'Claim Recoverable GEN'}
            </button>
          </div>
        )}

        {/* Real Telemetry Grid */}
        <section className="telemetry-grid">
          <div className="telemetry-card">
            <div className="telemetry-header">
              <span className="telemetry-label">On-Chain State Claims</span>
              <Layers size={18} className="telemetry-icon" />
            </div>
            <div className="telemetry-value">{stats ? stats.total_claims : '--'}</div>
            <div className="telemetry-sub">
              <span>Direct from StudioNet RPC</span>
            </div>
          </div>

          <div className="telemetry-card">
            <div className="telemetry-header">
              <span className="telemetry-label">Evidence Submissions</span>
              <FileCheck2 size={18} className="telemetry-icon" style={{ color: '#06b6d4' }} />
            </div>
            <div className="telemetry-value" style={{ color: '#06b6d4' }}>
              {stats ? stats.total_evidence : '--'}
            </div>
            <div className="telemetry-sub">
              <span>Indexed on-chain records</span>
            </div>
          </div>

          <div className="telemetry-card">
            <div className="telemetry-header">
              <span className="telemetry-label">Escrowed Bounties</span>
              <Coins size={18} className="telemetry-icon" style={{ color: '#fbbf24' }} />
            </div>
            <div className="telemetry-value" style={{ color: '#fbbf24' }}>
              {stats ? (Number(stats.total_escrowed) / 1e18).toFixed(2) : '0.00'} GEN
            </div>
            <div className="telemetry-sub">
              <span>Settlement truth pool</span>
            </div>
          </div>

          <div className="telemetry-card">
            <div className="telemetry-header">
              <span className="telemetry-label">Validator Consensus</span>
              <ShieldCheck size={18} className="telemetry-icon" style={{ color: '#10b981' }} />
            </div>
            <div className="telemetry-value" style={{ color: '#10b981' }}>
              Active
            </div>
            <div className="telemetry-sub">
              <span>Equivalence Quorum Verified</span>
            </div>
          </div>
        </section>

        {/* Navigation Tabs */}
        <div className="tabs-wrapper">
          <button
            id="tab-explorer"
            onClick={() => setActiveTab('explorer')}
            className={`tab-button ${activeTab === 'explorer' ? 'active' : ''}`}
          >
            <Search size={16} />
            <span>State Explorer</span>
          </button>
          <button
            id="tab-declare"
            onClick={() => setActiveTab('declare')}
            className={`tab-button ${activeTab === 'declare' ? 'active' : ''}`}
          >
            <PlusCircle size={16} />
            <span>Declare Assertion</span>
          </button>
          <button
            id="tab-evidence"
            onClick={() => setActiveTab('evidence')}
            className={`tab-button ${activeTab === 'evidence' ? 'active' : ''}`}
          >
            <Send size={16} />
            <span>Submit Evidence</span>
          </button>
          <button
            id="tab-adjudicate"
            onClick={() => setActiveTab('adjudicate')}
            className={`tab-button ${activeTab === 'adjudicate' ? 'active' : ''}`}
          >
            <Scale size={16} />
            <span>Adjudication Console</span>
          </button>
          <button
            id="tab-docs"
            onClick={() => setActiveTab('docs')}
            className={`tab-button ${activeTab === 'docs' ? 'active' : ''}`}
          >
            <BookOpen size={16} />
            <span>Protocol Architecture</span>
          </button>
        </div>

        {/* Loading Indicator */}
        {loading && (
          <div className="glass-panel" style={{ textAlign: 'center', padding: '36px' }}>
            <Loader2 size={32} className="animate-spin" style={{ margin: '0 auto 12px', color: '#10b981' }} />
            <p style={{ color: '#94a3b8' }}>Querying live contract state on GenLayer StudioNet...</p>
          </div>
        )}

        {/* TAB 1: EXPLORER */}
        {!loading && activeTab === 'explorer' && (
          <div className="content-layout">
            <div>
              {/* Filter Bar */}
              <div className="glass-panel" style={{ padding: '16px 20px', marginBottom: '16px' }}>
                <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
                  <div style={{ flex: '1', minWidth: '220px', position: 'relative' }}>
                    <input
                      type="text"
                      className="form-input"
                      placeholder="Search subject, predicate, or claim ID..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                    />
                  </div>

                  <select
                    className="form-select"
                    style={{ width: 'auto' }}
                    value={filterPolicy}
                    onChange={(e) => setFilterPolicy(e.target.value)}
                  >
                    <option value="ALL">All Policies</option>
                    <option value="OFFICIAL_REGISTRY">Official Registry</option>
                    <option value="REGULATORY_FILING">Regulatory Filing</option>
                    <option value="MULTI_SOURCE_INDEPENDENT">Multi-Source</option>
                    <option value="PRIMARY_PLUS_CORROBORATION">Primary + Corroboration</option>
                    <option value="OPEN_PUBLIC">Open Public</option>
                  </select>

                  <select
                    className="form-select"
                    style={{ width: 'auto' }}
                    value={filterStatus}
                    onChange={(e) => setFilterStatus(e.target.value)}
                  >
                    <option value="ALL">All Statuses</option>
                    <option value="EVIDENCE_OPEN">Evidence Open</option>
                    <option value="RESOLVED">Resolved</option>
                    <option value="DRAFT">Draft</option>
                  </select>
                </div>
              </div>

              {/* Claims List */}
              <div className="claims-grid">
                {filteredClaims.length === 0 ? (
                  <div className="glass-panel" style={{ textAlign: 'center', padding: '48px' }}>
                    <HelpCircle size={36} color="#64748b" style={{ margin: '0 auto 12px' }} />
                    <p style={{ color: '#94a3b8' }}>No state claims found matching filter criteria.</p>
                  </div>
                ) : (
                  filteredClaims.map((c) => {
                    const isSelected = c.id === selectedClaimId;
                    return (
                      <div
                        key={c.id}
                        className={`claim-card ${isSelected ? 'selected' : ''}`}
                        onClick={() => setSelectedClaimId(c.id)}
                      >
                        <div className="claim-card-header">
                          <span className="claim-id">{c.id}</span>
                          <div style={{ display: 'flex', gap: '8px' }}>
                            <span className="badge badge-cyan">{c.claim_type}</span>
                            {c.verdict === 'CONFIRMED' && (
                              <span className="badge badge-emerald">
                                <CheckCircle2 size={12} /> CONFIRMED
                              </span>
                            )}
                            {c.verdict === 'REFUTED' && (
                              <span className="badge badge-red">
                                <XCircle size={12} /> REFUTED
                              </span>
                            )}
                            {c.status === 'EVIDENCE_OPEN' && (
                              <span className="badge badge-amber">
                                <Activity size={12} /> OPEN FOR EVIDENCE
                              </span>
                            )}
                            {c.status === 'DRAFT' && (
                              <span className="badge badge-muted">DRAFT</span>
                            )}
                          </div>
                        </div>

                        <h3 className="claim-subject">{c.subject}</h3>

                        <div className="claim-predicate-box">
                          <span className="predicate-key">ASSERTION: </span>
                          <span className="predicate-val">
                            {c.predicate} ➔ {c.asserted_value}
                          </span>
                        </div>

                        <div className="claim-meta-row">
                          <span>
                            Policy: <strong>{c.source_policy || 'Pending Freeze'}</strong>
                          </span>
                          <span>
                            Evidence Count: <strong>{c.evidence_count}</strong>
                          </span>
                          <span>
                            Bounty: <strong>{(Number(c.bounty_amount) / 1e18).toFixed(2)} GEN</strong>
                          </span>
                        </div>
                      </div>
                    );
                  })
                )}
              </div>
            </div>

            {/* Side Detail Inspector */}
            <div>
              {selectedClaim ? (
                <div className="detail-drawer">
                  <div className="drawer-section">
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span className="claim-id" style={{ fontSize: '15px' }}>
                        {selectedClaim.id}
                      </span>
                      <span className={`badge ${selectedClaim.status === 'RESOLVED' ? 'badge-emerald' : 'badge-amber'}`}>
                        {selectedClaim.status}
                      </span>
                    </div>
                    <h2 style={{ fontSize: '18px', fontWeight: '700', marginTop: '10px' }}>
                      {selectedClaim.subject}
                    </h2>
                    <p style={{ fontSize: '12px', color: '#94a3b8', marginTop: '4px' }}>
                      Creator: {selectedClaim.creator.slice(0, 8)}...{selectedClaim.creator.slice(-6)}
                    </p>
                  </div>

                  {/* Assertion Spec */}
                  <div className="drawer-section">
                    <div className="section-subtitle">Assertion Specifications</div>
                    <div className="claim-predicate-box" style={{ background: '#070b14' }}>
                      <div style={{ marginBottom: '6px' }}>
                        <span className="predicate-key">Predicate: </span>
                        <span style={{ color: '#f8fafc' }}>{selectedClaim.predicate}</span>
                      </div>
                      <div style={{ marginBottom: '6px' }}>
                        <span className="predicate-key">Claimed State: </span>
                        <span style={{ color: '#10b981', fontWeight: '700' }}>
                          {selectedClaim.asserted_value}
                        </span>
                      </div>
                      <div>
                        <span className="predicate-key">Reference Date: </span>
                        <span style={{ color: '#94a3b8' }}>{selectedClaim.reference_date}</span>
                      </div>
                    </div>
                  </div>

                  {/* Bounty & Escrow Pool Section */}
                  <div className="drawer-section">
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                      <div className="section-subtitle" style={{ margin: 0 }}>Native GEN Escrow Bounty</div>
                      <button
                        className="btn-secondary"
                        style={{ padding: '4px 10px', fontSize: '11px', display: 'flex', alignItems: 'center', gap: '4px' }}
                        onClick={() => setShowFundModal(true)}
                        disabled={['SETTLED', 'CANCELLED', 'REFUNDED'].includes(selectedClaim.status) || isWrongNetwork}
                      >
                        <Coins size={12} color="#fbbf24" /> Fund Bounty
                      </button>
                    </div>
                    <div className="claim-predicate-box" style={{ background: '#0a0f1d', border: '1px solid rgba(251, 191, 36, 0.2)' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span style={{ fontSize: '12px', color: '#94a3b8' }}>Escrowed Truth Reward:</span>
                        <span style={{ fontSize: '16px', fontWeight: '800', color: '#fbbf24' }}>
                          {(Number(selectedClaim.bounty_amount) / 1e18).toFixed(4)} GEN
                        </span>
                      </div>
                      {selectedClaim.funders && selectedClaim.funders.length > 0 && (
                        <div style={{ fontSize: '11px', color: '#64748b', marginTop: '6px' }}>
                          Contributors: {selectedClaim.funders.length} funder(s) tracked individually
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Consensus Adjudication Result */}
                  {selectedAdjudication && (
                    <div className="drawer-section">
                      <div className="section-subtitle">Multi-Validator Consensus Outcome</div>
                      <div
                        className={`verdict-box ${
                          selectedAdjudication.verdict === 'CONFIRMED'
                            ? 'confirmed'
                            : selectedAdjudication.verdict === 'REFUTED'
                            ? 'refuted'
                            : 'conflicted'
                        }`}
                      >
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <span style={{ fontWeight: '800', fontSize: '15px' }}>
                            {selectedAdjudication.verdict}
                          </span>
                          <span className="badge badge-emerald">
                            {selectedAdjudication.confidence_score}% Confidence
                          </span>
                        </div>
                        <p style={{ fontSize: '12px', marginTop: '8px', lineHeight: '1.5' }}>
                          {selectedAdjudication.reason}
                        </p>

                        {/* Supporting Quotation Verification */}
                        {selectedAdjudication.supporting_quotation && (
                          <div style={{ marginTop: '10px', padding: '8px 10px', background: 'rgba(0,0,0,0.3)', borderRadius: '6px' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                              <span style={{ fontSize: '11px', color: '#94a3b8', fontWeight: '600' }}>Supporting Quotation:</span>
                              {selectedAdjudication.quotation_verified ? (
                                <span className="badge badge-emerald" style={{ fontSize: '10px', padding: '2px 6px' }}>✓ Verified in Source</span>
                              ) : (
                                <span className="badge badge-muted" style={{ fontSize: '10px', padding: '2px 6px' }}>Unverified Quote</span>
                              )}
                            </div>
                            <blockquote style={{ fontSize: '11px', fontStyle: 'italic', color: '#cbd5e1', borderLeft: '2px solid #10b981', paddingLeft: '8px', margin: '4px 0' }}>
                              "{selectedAdjudication.supporting_quotation}"
                            </blockquote>
                          </div>
                        )}

                        {/* Source Fingerprints */}
                        {selectedAdjudication.source_fingerprints && selectedAdjudication.source_fingerprints.length > 0 && (
                          <div style={{ marginTop: '10px' }}>
                            <span style={{ fontSize: '11px', color: '#94a3b8', fontWeight: '600' }}>
                              Authoritative Fingerprints ({selectedAdjudication.source_fingerprints.length}):
                            </span>
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', marginTop: '4px' }}>
                              {selectedAdjudication.source_fingerprints.map((fp, i) => (
                                <div key={i} style={{ fontSize: '10px', background: '#050811', padding: '4px 8px', borderRadius: '4px', border: '1px solid #1e293b' }}>
                                  <div style={{ color: '#38bdf8', fontWeight: '600' }}>{fp.domain} ({fp.apex_domain})</div>
                                  <div style={{ color: '#64748b', fontFamily: 'monospace' }}>SHA256: {fp.sha256_fingerprint?.slice(0, 16)}...</div>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}

                        {/* Qualifying Recipients */}
                        {selectedAdjudication.qualifying_recipients && selectedAdjudication.qualifying_recipients.length > 0 && (
                          <div style={{ marginTop: '10px' }}>
                            <span style={{ fontSize: '11px', color: '#94a3b8', fontWeight: '600' }}>
                              Qualifying Recipients ({selectedAdjudication.qualifying_recipients.length}):
                            </span>
                            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px', marginTop: '4px' }}>
                              {selectedAdjudication.qualifying_recipients.map((r, i) => (
                                <span key={i} className="badge badge-emerald" style={{ fontSize: '10px' }}>
                                  {r.slice(0, 6)}...{r.slice(-4)}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Attached Evidence */}
                  <div className="drawer-section">
                    <div className="section-subtitle">
                      Submitted Evidence ({selectedEvidence.length})
                    </div>
                    {selectedEvidence.length === 0 ? (
                      <p style={{ fontSize: '12px', color: '#64748b' }}>
                        No evidence records attached yet on-chain. Submit evidence to trigger consensus.
                      </p>
                    ) : (
                      selectedEvidence.map((ev) => (
                        <div key={ev.id} className="evidence-card">
                          <a
                            href={ev.source_url}
                            target="_blank"
                            rel="noreferrer"
                            className="evidence-url"
                          >
                            <ExternalLink size={12} />
                            {ev.source_url}
                          </a>
                          <div className="evidence-text">{ev.explanation}</div>
                          <div style={{ fontSize: '10px', color: '#64748b', marginTop: '4px' }}>
                            Submitter: {ev.submitter.slice(0, 6)}...{ev.submitter.slice(-4)}
                          </div>
                        </div>
                      ))
                    )}
                  </div>

                  {/* Action Buttons */}
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginTop: '16px' }}>
                    <div style={{ display: 'flex', gap: '8px' }}>
                      {selectedClaim.status === 'EVIDENCE_OPEN' && (
                        <>
                          <button
                            className="btn-primary"
                            style={{ flex: 1, padding: '10px 14px', fontSize: '13px' }}
                            onClick={() => {
                              setTargetClaimId(selectedClaim.id);
                              setActiveTab('evidence');
                            }}
                          >
                            <PlusCircle size={15} /> Attach Evidence
                          </button>
                          <button
                            className="btn-secondary"
                            style={{ padding: '10px 14px', fontSize: '13px' }}
                            onClick={() => {
                              setAdjClaimId(selectedClaim.id);
                              setActiveTab('adjudicate');
                            }}
                          >
                            <Scale size={15} /> Adjudicate
                          </button>
                        </>
                      )}
                    </div>

                    {/* Settle Bounty Button */}
                    {(selectedClaim.status === 'RESOLVED' || selectedClaim.status === 'PARTIALLY_SETTLED') &&
                      (selectedClaim.verdict === 'CONFIRMED' || selectedClaim.verdict === 'REFUTED') &&
                      BigInt(selectedClaim.bounty_amount || '0') > 0n && (
                        <button
                          className="btn-primary"
                          disabled={isSettling || isWrongNetwork}
                          style={{ width: '100%', padding: '10px 14px', fontSize: '13px', background: '#059669', borderColor: '#10b981' }}
                          onClick={() => {
                            const recipients = selectedClaim.qualifying_recipients || selectedAdjudication?.qualifying_recipients || [];
                            setSelectedRecipient(recipients[0] || '');
                            setShowSettleModal(true);
                          }}
                        >
                          <Award size={15} /> Settle Bounty to Qualifying Recipient
                        </button>
                      )}

                    {/* Refund Bounty Button */}
                    {selectedClaim.status === 'RESOLVED' &&
                      ['INSUFFICIENT_EVIDENCE', 'SOURCE_UNAVAILABLE', 'CONFLICTED'].includes(selectedClaim.verdict || '') &&
                      BigInt(selectedClaim.bounty_amount || '0') > 0n && (
                        <button
                          className="btn-secondary"
                          style={{ width: '100%', padding: '10px 14px', fontSize: '13px', color: '#f59e0b', borderColor: '#f59e0b' }}
                          onClick={() => handleRefundBounty(selectedClaim.id)}
                          disabled={isRefunding || isWrongNetwork}
                        >
                          {isRefunding ? <Loader2 size={15} className="animate-spin" /> : <RefreshCw size={15} />}
                          <span>Refund Escrowed Bounty to Contributors</span>
                        </button>
                      )}

                    {/* DRAFT Actions: Freeze Claim & Cancel Claim */}
                    {selectedClaim.status === 'DRAFT' && (
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                        <button
                          className="btn-primary"
                          style={{ width: '100%', padding: '10px 14px', fontSize: '13px' }}
                          onClick={() => handleFreezeClaim(selectedClaim.id, selectedClaim.source_policy || 'OPEN_PUBLIC', selectedClaim.window_seconds || 86400)}
                          disabled={isFreezing || isWrongNetwork}
                        >
                          {isFreezing ? <Loader2 size={15} className="animate-spin" /> : <Lock size={15} />}
                          <span>Freeze Claim & Open Evidence Window</span>
                        </button>
                        <button
                          className="btn-secondary"
                          style={{ width: '100%', padding: '10px 14px', fontSize: '13px', color: '#ef4444', borderColor: '#ef4444' }}
                          onClick={() => handleCancelClaim(selectedClaim.id)}
                          disabled={isCancelling || isWrongNetwork}
                        >
                          {isCancelling ? <Loader2 size={15} className="animate-spin" /> : <XCircle size={15} />}
                          <span>Cancel Claim & Auto-Refund Deposited GEN</span>
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              ) : (
                <div className="detail-drawer" style={{ textAlign: 'center', color: '#64748b' }}>
                  Select a state claim to inspect details
                </div>
              )}
            </div>
          </div>
        )}

        {/* TAB 2: DECLARE ASSERTION */}
        {activeTab === 'declare' && (
          <div className="glass-panel" style={{ maxWidth: '780px', margin: '0 auto' }}>
            <div className="panel-header">
              <div>
                <h2 className="panel-title">Declare Verifiable State Claim (On-Chain)</h2>
                <p className="panel-desc">
                  Broadcasts a real transaction to the deployed GenState contract on StudioNet.
                </p>
              </div>
            </div>

            {declareSuccess && (
              <div
                style={{
                  background: 'rgba(16, 185, 129, 0.15)',
                  border: '1px solid #10b981',
                  color: '#34d399',
                  padding: '14px 18px',
                  borderRadius: '8px',
                  marginBottom: '20px',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontWeight: '700' }}>
                  <CheckCircle2 size={18} />
                  <span>On-Chain Claim Created: {declareSuccess.claimId}</span>
                </div>
                <div style={{ fontSize: '12px', marginTop: '6px', wordBreak: 'break-all' }}>
                  Tx Hash: {declareSuccess.txHash}
                </div>
              </div>
            )}

            {!walletConnected ? (
              <div className="wallet-required-banner">
                <div className="wallet-required-icon">
                  <Lock size={28} />
                </div>
                <h3 style={{ fontSize: '18px', fontWeight: '700', color: '#f8fafc', marginBottom: '8px' }}>
                  Wallet Connection Required
                </h3>
                <p style={{ fontSize: '13px', color: '#94a3b8', maxWidth: '440px', margin: '0 auto 20px' }}>
                  Connect your Web3 wallet or GenLayer StudioNet account to declare and freeze verifiable state assertions.
                </p>
                <button
                  id="btn-declare-connect-wallet"
                  onClick={() => setShowWalletModal(true)}
                  className="wallet-btn connect-glow"
                  style={{ margin: '0 auto', padding: '10px 24px', fontSize: '14px' }}
                >
                  <Wallet size={16} />
                  <span>Connect Wallet to Declare</span>
                </button>
              </div>
            ) : (
              <form onSubmit={handleDeclareSubmit}>
                <div className="form-group">
                  <label className="form-label">Domain Category</label>
                  <select
                    id="select-declare-type"
                    className="form-select"
                    value={newClaimType}
                    onChange={(e) => setNewClaimType(e.target.value as ClaimType)}
                  >
                    <option value="REGISTRY_RECORD">REGISTRY_RECORD (Land, corporate, public registries)</option>
                    <option value="STATE_TRANSITION">STATE_TRANSITION (Blockchain milestones, telemetry state)</option>
                    <option value="FACTUAL_EVENT">FACTUAL_EVENT (Verifiable real-world events)</option>
                    <option value="GOVERNANCE_EXECUTION">GOVERNANCE_EXECUTION (DAO execution, council votes)</option>
                    <option value="COMPLIANCE_STATUS">COMPLIANCE_STATUS (Audits, certifications, licenses)</option>
                  </select>
                </div>

                <div className="form-group">
                  <label className="form-label">Subject</label>
                  <input
                    id="input-declare-subject"
                    type="text"
                    className="form-input"
                    placeholder="e.g. Delaware Entity Registry #749102 / OpenZeppelin v5.0 Audit"
                    value={newSubject}
                    onChange={(e) => setNewSubject(e.target.value)}
                    required
                  />
                  <div className="form-help">The specific entity, asset, or event being asserted.</div>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                  <div className="form-group">
                    <label className="form-label">Predicate</label>
                    <input
                      id="input-declare-predicate"
                      type="text"
                      className="form-input"
                      placeholder="e.g. audit_certified_zero_critical_vulnerabilities"
                      value={newPredicate}
                      onChange={(e) => setNewPredicate(e.target.value)}
                      required
                    />
                    <div className="form-help">Structured attribute to be verified.</div>
                  </div>

                  <div className="form-group">
                    <label className="form-label">Asserted Value</label>
                    <input
                      id="input-declare-asserted-value"
                      type="text"
                      className="form-input"
                      placeholder="e.g. TRUE / CERTIFIED"
                      value={newAssertedValue}
                      onChange={(e) => setNewAssertedValue(e.target.value)}
                      required
                    />
                    <div className="form-help">The exact claimed target state.</div>
                  </div>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                  <div className="form-group">
                    <label className="form-label">Reference Date</label>
                    <input
                      id="input-declare-reference-date"
                      type="date"
                      className="form-input"
                      value={newReferenceDate}
                      onChange={(e) => setNewReferenceDate(e.target.value)}
                      required
                    />
                  </div>

                  <div className="form-group">
                    <label className="form-label">Admissibility Policy</label>
                    <select
                      id="select-declare-policy"
                      className="form-select"
                      value={newPolicy}
                      onChange={(e) => setNewPolicy(e.target.value as AdmissibilityPolicy)}
                    >
                      <option value="OFFICIAL_REGISTRY">OFFICIAL_REGISTRY (Government / official records)</option>
                      <option value="REGULATORY_FILING">REGULATORY_FILING (SEC / statutory reports)</option>
                      <option value="MULTI_SOURCE_INDEPENDENT">MULTI_SOURCE_INDEPENDENT (Min 2 sources)</option>
                      <option value="PRIMARY_PLUS_CORROBORATION">PRIMARY_PLUS_CORROBORATION</option>
                      <option value="OPEN_PUBLIC">OPEN_PUBLIC (General verified web evidence)</option>
                    </select>
                  </div>
                </div>

                <div className="form-group" style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <input
                    type="checkbox"
                    id="freezeCheck"
                    checked={freezeImmediately}
                    onChange={(e) => setFreezeImmediately(e.target.checked)}
                    style={{ width: '16px', height: '16px', accentColor: '#10b981' }}
                  />
                  <label htmlFor="freezeCheck" style={{ fontSize: '13px', color: '#cbd5e1', cursor: 'pointer' }}>
                    Freeze claim on-chain immediately and open evidence submission window
                  </label>
                </div>

                <button
                  id="btn-broadcast-declare"
                  type="submit"
                  disabled={isDeclaring || isWrongNetwork}
                  className="btn-primary"
                  style={{ width: '100%', marginTop: '12px' }}
                >
                  {isDeclaring ? (
                    <>
                      <Loader2 size={16} className="animate-spin" />
                      <span>Broadcasting & Awaiting Validator Consensus...</span>
                    </>
                  ) : (
                    <>
                      <Lock size={16} /> Broadcast On-Chain Assertion to StudioNet
                    </>
                  )}
                </button>
              </form>
            )}
          </div>
        )}

        {/* TAB 3: SUBMIT EVIDENCE */}
        {activeTab === 'evidence' && (
          <div className="glass-panel" style={{ maxWidth: '780px', margin: '0 auto' }}>
            <div className="panel-header">
              <div>
                <h2 className="panel-title">Submit Evidence Record (On-Chain)</h2>
                <p className="panel-desc">
                  Supply public web URLs and documentation to prove or refute frozen state assertions.
                </p>
              </div>
            </div>

            {evidenceSuccess && (
              <div
                style={{
                  background: 'rgba(6, 182, 212, 0.15)',
                  border: '1px solid #06b6d4',
                  color: '#38bdf8',
                  padding: '14px 18px',
                  borderRadius: '8px',
                  marginBottom: '20px',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontWeight: '700' }}>
                  <CheckCircle2 size={18} />
                  <span>Evidence Finalized on StudioNet!</span>
                </div>
                <div style={{ fontSize: '12px', marginTop: '6px', wordBreak: 'break-all' }}>
                  Tx Hash: {evidenceSuccess.txHash}
                </div>
              </div>
            )}

            {!walletConnected ? (
              <div className="wallet-required-banner">
                <div className="wallet-required-icon">
                  <Lock size={28} />
                </div>
                <h3 style={{ fontSize: '18px', fontWeight: '700', color: '#f8fafc', marginBottom: '8px' }}>
                  Wallet Connection Required
                </h3>
                <p style={{ fontSize: '13px', color: '#94a3b8', maxWidth: '440px', margin: '0 auto 20px' }}>
                  Please connect your Web3 wallet or GenLayer StudioNet account to submit verifiable web evidence on-chain.
                </p>
                <button
                  id="btn-evidence-connect-wallet"
                  onClick={() => setShowWalletModal(true)}
                  className="wallet-btn connect-glow"
                  style={{ margin: '0 auto', padding: '10px 24px', fontSize: '14px' }}
                >
                  <Wallet size={16} />
                  <span>Connect Wallet to Submit Evidence</span>
                </button>
              </div>
            ) : (
              <form onSubmit={handleEvidenceSubmit}>
                <div className="form-group">
                  <label className="form-label">Select Target State Claim</label>
                  <select
                    id="select-evidence-target-claim"
                    className="form-select"
                    value={targetClaimId}
                    onChange={(e) => setTargetClaimId(e.target.value)}
                  >
                    {claims.length === 0 ? (
                      <option value="">No claims found on-chain</option>
                    ) : (
                      claims.map((c) => (
                        <option key={c.id} value={c.id}>
                          {c.id} - {c.subject} ({c.status})
                        </option>
                      ))
                    )}
                  </select>
                </div>

                <div className="form-group">
                  <label className="form-label">Source URL (HTTP / HTTPS)</label>
                  <input
                    id="input-evidence-source-url"
                    type="url"
                    className="form-input"
                    placeholder="https://github.com/OpenZeppelin/openzeppelin-contracts/releases/tag/v5.0.0"
                    value={sourceUrl}
                    onChange={(e) => setSourceUrl(e.target.value)}
                    required
                  />
                  <div className="form-help">Validators will fetch this web page defensively during consensus.</div>
                </div>

                <div className="form-group">
                  <label className="form-label">Contextual Rationale & Excerpt</label>
                  <textarea
                    id="input-evidence-explanation"
                    className="form-textarea"
                    rows={4}
                    placeholder="Provide objective proof and source excerpt linking this URL to the asserted state predicate..."
                    value={explanation}
                    onChange={(e) => setExplanation(e.target.value)}
                    required
                  />
                </div>

                <button
                  id="btn-broadcast-evidence"
                  type="submit"
                  disabled={isSubmittingEvidence || !targetClaimId || isWrongNetwork}
                  className="btn-primary"
                  style={{ width: '100%', marginTop: '8px' }}
                >
                  {isSubmittingEvidence ? (
                    <>
                      <Loader2 size={16} className="animate-spin" />
                      <span>Broadcasting Evidence Transaction to StudioNet...</span>
                    </>
                  ) : (
                    <>
                      <Send size={16} /> Broadcast Evidence Transaction
                    </>
                  )}
                </button>
              </form>
            )}
          </div>
        )}

        {/* TAB 4: ADJUDICATION CONSOLE */}
        {activeTab === 'adjudicate' && (
          <div className="glass-panel" style={{ maxWidth: '820px', margin: '0 auto' }}>
            <div className="panel-header">
              <div>
                <h2 className="panel-title">Multi-Validator Adjudication Console (Live Consensus)</h2>
                <p className="panel-desc">
                  Executes the intelligent contract's <code>adjudicate()</code> method on GenLayer StudioNet.
                </p>
              </div>
            </div>

            {!walletConnected ? (
              <div className="wallet-required-banner">
                <div className="wallet-required-icon">
                  <Lock size={28} />
                </div>
                <h3 style={{ fontSize: '18px', fontWeight: '700', color: '#f8fafc', marginBottom: '8px' }}>
                  Wallet Connection Required
                </h3>
                <p style={{ fontSize: '13px', color: '#94a3b8', maxWidth: '440px', margin: '0 auto 20px' }}>
                  Please connect your Web3 wallet or GenLayer StudioNet account to trigger multi-validator LLM consensus adjudication.
                </p>
                <button
                  id="btn-adjudicate-connect-wallet"
                  onClick={() => setShowWalletModal(true)}
                  className="wallet-btn connect-glow"
                  style={{ margin: '0 auto', padding: '10px 24px', fontSize: '14px' }}
                >
                  <Wallet size={16} />
                  <span>Connect Wallet to Adjudicate</span>
                </button>
              </div>
            ) : (
              <>
                <div className="form-group">
                  <label className="form-label">Select Claim to Adjudicate</label>
                  <select
                    id="select-adjudicate-claim"
                    className="form-select"
                    value={adjClaimId}
                    onChange={(e) => {
                      setAdjClaimId(e.target.value);
                      setAdjudicationSuccess(null);
                    }}
                  >
                    {claims.length === 0 ? (
                      <option value="">No claims found on-chain</option>
                    ) : (
                      claims.map((c) => (
                        <option key={c.id} value={c.id}>
                          {c.id} - {c.subject} (Evidence: {c.evidence_count}, Status: {c.status})
                        </option>
                      ))
                    )}
                  </select>
                </div>

                {/* Claim Quick Summary */}
                {(() => {
                  const currentClaim = claims.find((c) => c.id === adjClaimId);
                  if (!currentClaim) return null;
                  return (
                    <div
                      style={{
                        background: '#070b14',
                        border: '1px solid rgba(255, 255, 255, 0.08)',
                        borderRadius: '12px',
                        padding: '16px 20px',
                        marginBottom: '20px',
                      }}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                        <span style={{ fontFamily: 'var(--font-mono)', color: '#06b6d4', fontWeight: '700' }}>
                          {currentClaim.id}
                        </span>
                        <span className="badge badge-cyan">{currentClaim.source_policy || 'Policy Pending'}</span>
                      </div>
                      <h4 style={{ fontSize: '16px', fontWeight: '700' }}>{currentClaim.subject}</h4>
                      <div style={{ fontSize: '13px', color: '#94a3b8', marginTop: '6px' }}>
                        Predicate: <strong style={{ color: '#10b981' }}>{currentClaim.predicate}</strong> ➔{' '}
                        <strong style={{ color: '#f8fafc' }}>{currentClaim.asserted_value}</strong>
                      </div>
                      <div style={{ fontSize: '12px', color: '#64748b', marginTop: '6px' }}>
                        Status: <strong>{currentClaim.status}</strong> | Evidence Records: <strong>{currentClaim.evidence_count}</strong>
                      </div>
                    </div>
                  );
                })()}

                <button
                  id="btn-trigger-adjudicate"
                  onClick={() => handleRunAdjudication(adjClaimId)}
                  disabled={isAdjudicating || !adjClaimId || isWrongNetwork}
                  className="btn-primary"
                  style={{ width: '100%', marginBottom: '24px' }}
                >
                  {isAdjudicating ? (
                    <>
                      <Sparkles size={16} className="animate-spin" />
                      <span>GenLayer Validators Performing Consensus Round on StudioNet...</span>
                    </>
                  ) : (
                    <>
                      <Scale size={16} />
                      <span>Trigger Multi-Validator LLM Consensus Transaction</span>
                    </>
                  )}
                </button>

                {/* Adjudication Outcome Box */}
                {adjudicationSuccess && (
                  <div
                    className="verdict-box confirmed"
                    style={{
                      border: '1px solid #10b981',
                      background: 'rgba(16, 185, 129, 0.1)',
                      padding: '24px',
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                        <CheckCircle2 size={24} color="#10b981" />
                        <span style={{ fontSize: '18px', fontWeight: '800', color: '#10b981' }}>
                          ON-CHAIN VERDICT: {adjudicationSuccess.verdict}
                        </span>
                      </div>
                    </div>

                    <div style={{ marginTop: '12px', fontSize: '13px', color: '#94a3b8', wordBreak: 'break-all' }}>
                      Consensus Tx Hash: {adjudicationSuccess.txHash}
                    </div>
                  </div>
                )}
              </>
            )}
          </div>
        )}

        {/* TAB 5: PROTOCOL ARCHITECTURE & DOCS */}
        {activeTab === 'docs' && (
          <div className="glass-panel" style={{ maxWidth: '860px', margin: '0 auto' }}>
            <div className="panel-header">
              <div>
                <h2 className="panel-title">GenState Protocol Architecture</h2>
                <p className="panel-desc">
                  Decentralized semantic state consensus powered by GenLayer's GenVM.
                </p>
              </div>
            </div>

            <div style={{ lineHeight: '1.7', fontSize: '14px', color: '#cbd5e1' }}>
              <h3 style={{ color: '#10b981', fontSize: '16px', marginBottom: '8px' }}>
                1. Real On-Chain Execution
              </h3>
              <p style={{ marginBottom: '16px' }}>
                Every action in this terminal executes live smart contract calls via <code>genlayer-js</code> to
                the GenState contract deployed on StudioNet. No mock arrays, no simulated storage, and no dummy timers.
              </p>

              <h3 style={{ color: '#06b6d4', fontSize: '16px', marginBottom: '8px' }}>
                2. Storage Pre-Extraction Rule
              </h3>
              <p style={{ marginBottom: '16px' }}>
                All smart contract storage attributes (<code>self.claims</code>, <code>self.evidence</code>, etc.)
                are pre-extracted into pure Python primitives outside the non-deterministic closures (
                <code>leader_fn</code>), preventing pickling desynchronization and consensus execution failure.
              </p>

              <h3 style={{ color: '#fbbf24', fontSize: '16px', marginBottom: '8px' }}>
                3. Equivalence Principle & Comparative Validation
              </h3>
              <p style={{ marginBottom: '16px' }}>
                Validators independently fetch external web pages using <code>gl.nondet.web.get()</code> with
                defensive fallback mechanisms. Multi-validator consensus is reached via{' '}
                <code>gl.eq_principle.prompt_comparative</code> over the primary verdict enum (
                <code>CONFIRMED</code>, <code>REFUTED</code>, <code>CONFLICTED</code>,{' '}
                <code>INSUFFICIENT_EVIDENCE</code>, <code>SOURCE_UNAVAILABLE</code>).
              </p>

              <div
                style={{
                  background: '#070b14',
                  padding: '16px',
                  borderRadius: '8px',
                  border: '1px solid rgba(255, 255, 255, 0.08)',
                  fontFamily: 'var(--font-mono)',
                  fontSize: '12px',
                  marginTop: '16px',
                }}
              >
                <div># Live Deployed Contract Information:</div>
                <div style={{ color: '#10b981', marginTop: '6px' }}>
                  Contract Address: {GENSTATE_CONFIG.contractAddress}
                </div>
                <div style={{ color: '#06b6d4', marginTop: '4px' }}>
                  Deploy Tx Hash:   {GENSTATE_CONFIG.deploymentTxHash}
                </div>
                <div style={{ color: '#fbbf24', marginTop: '4px' }}>
                  Target Network:   StudioNet (Chain ID: {GENSTATE_CONFIG.chainId})
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Wallet Connection Modal */}
        {showWalletModal && (
          <div className="wallet-modal-overlay" onClick={() => !connectingWallet && setShowWalletModal(false)}>
            <div className="wallet-modal-box" onClick={(e) => e.stopPropagation()}>
              <div className="wallet-modal-header">
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <div className="wallet-icon-badge">
                    <Wallet size={18} color="#10b981" />
                  </div>
                  <h3 className="wallet-modal-title">Connect Wallet</h3>
                </div>
                <button
                  className="wallet-modal-close"
                  onClick={() => !connectingWallet && setShowWalletModal(false)}
                  disabled={connectingWallet}
                >
                  <X size={18} />
                </button>
              </div>

              <div className="wallet-modal-body">
                <p className="wallet-modal-subtitle">
                  Select your preferred connection method to interact with GenState on GenLayer StudioNet.
                </p>

                <div className="wallet-choices-list">
                  <div
                    className="wallet-choice-card"
                    onClick={() => !connectingWallet && handleConnect('studionet')}
                    id="connect-studionet-option"
                  >
                    <div className="wallet-choice-icon studionet">
                      <Sparkles size={22} color="#10b981" />
                    </div>
                    <div className="wallet-choice-info">
                      <div className="wallet-choice-name">
                        GenLayer StudioNet Account
                        <span className="wallet-pill-recommended">Recommended</span>
                      </div>
                      <div className="wallet-choice-desc">
                        Instant 1-click testnet account pre-funded with GEN for transactions.
                      </div>
                    </div>
                  </div>

                  <div
                    className="wallet-choice-card"
                    onClick={() => !connectingWallet && handleConnect('browser')}
                    id="connect-browser-option"
                  >
                    <div className="wallet-choice-icon injected">
                      <Wallet size={22} color="#06b6d4" />
                    </div>
                    <div className="wallet-choice-info">
                      <div className="wallet-choice-name">Browser Extension Wallet</div>
                      <div className="wallet-choice-desc">
                        Connect via MetaMask or other injected Web3 wallet provider.
                      </div>
                    </div>
                  </div>
                </div>

                {connectingWallet && (
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '10px', marginTop: '16px', color: '#10b981', fontSize: '13px' }}>
                    <Loader2 size={16} className="animate-spin" />
                    <span>Connecting wallet & synchronizing balance...</span>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Fund Bounty Modal */}
        {showFundModal && (
          <div className="wallet-modal-overlay" onClick={() => !isFunding && setShowFundModal(false)}>
            <div className="wallet-modal-box" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '440px' }}>
              <div className="wallet-modal-header">
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <div className="wallet-icon-badge" style={{ background: 'rgba(251, 191, 36, 0.15)', borderColor: '#fbbf24' }}>
                    <Coins size={18} color="#fbbf24" />
                  </div>
                  <h3 className="wallet-modal-title">Fund State Assertion Bounty</h3>
                </div>
                <button
                  className="wallet-modal-close"
                  onClick={() => !isFunding && setShowFundModal(false)}
                  disabled={isFunding}
                >
                  <X size={18} />
                </button>
              </div>

              <form onSubmit={handleFundBountySubmit} className="wallet-modal-body">
                <p className="wallet-modal-subtitle">
                  Deposit native GEN into the protocol truth pool for claim <strong>{selectedClaimId}</strong>.
                  Individual contributor accounting tracks your exact deposit for safe refund recovery.
                </p>

                <div style={{ marginTop: '16px' }}>
                  <label style={{ fontSize: '12px', fontWeight: '600', color: '#94a3b8', display: 'block', marginBottom: '6px' }}>
                    Deposit Amount (GEN):
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    min="0.01"
                    className="form-input"
                    value={fundAmountGen}
                    onChange={(e) => setFundAmountGen(e.target.value)}
                    placeholder="e.g. 0.5"
                    required
                    disabled={isFunding}
                  />
                  <div style={{ fontSize: '11px', color: '#64748b', marginTop: '4px' }}>
                    Estimated wei: {fundAmountGen ? `${(parseFloat(fundAmountGen) * 1e18).toLocaleString('fullwide', { useGrouping: false })} wei` : '0 wei'}
                  </div>
                </div>

                <div style={{ display: 'flex', gap: '10px', marginTop: '24px' }}>
                  <button
                    type="button"
                    className="btn-secondary"
                    style={{ flex: 1, padding: '10px', fontSize: '13px' }}
                    onClick={() => setShowFundModal(false)}
                    disabled={isFunding}
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="btn-primary"
                    style={{ flex: 2, padding: '10px', fontSize: '13px', background: '#d97706', borderColor: '#f59e0b' }}
                    disabled={isFunding || isWrongNetwork}
                  >
                    {isFunding ? (
                      <span style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>
                        <Loader2 size={15} className="animate-spin" />
                        Depositing GEN...
                      </span>
                    ) : (
                      <span>Deposit Bounty into Escrow</span>
                    )}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Settle Bounty Modal */}
        {showSettleModal && (
          <div className="wallet-modal-overlay" onClick={() => !isSettling && setShowSettleModal(false)}>
            <div className="wallet-modal-box" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '460px' }}>
              <div className="wallet-modal-header">
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <div className="wallet-icon-badge" style={{ background: 'rgba(16, 185, 129, 0.15)', borderColor: '#10b981' }}>
                    <Award size={18} color="#10b981" />
                  </div>
                  <h3 className="wallet-modal-title">Settle Bounty to Qualifying Participant</h3>
                </div>
                <button
                  className="wallet-modal-close"
                  onClick={() => !isSettling && setShowSettleModal(false)}
                  disabled={isSettling}
                >
                  <X size={18} />
                </button>
              </div>

              <form onSubmit={handleSettleBountySubmit} className="wallet-modal-body">
                <p className="wallet-modal-subtitle">
                  Executes genuine native GEN transfer from the protocol contract to an authenticated qualifying recipient.
                  Deterministic eligibility requires that the recipient submitted evidence verified during consensus.
                </p>

                <div style={{ marginTop: '16px' }}>
                  <label style={{ fontSize: '12px', fontWeight: '600', color: '#94a3b8', display: 'block', marginBottom: '6px' }}>
                    Select Qualifying Recipient:
                  </label>
                  {selectedClaim?.qualifying_recipients && selectedClaim.qualifying_recipients.length > 0 ? (
                    <select
                      className="form-select"
                      value={selectedRecipient}
                      onChange={(e) => setSelectedRecipient(e.target.value)}
                      required
                      disabled={isSettling}
                    >
                      {selectedClaim.qualifying_recipients.map((recip, idx) => (
                        <option key={idx} value={recip}>
                          {recip} (Qualifying Submitter #{idx + 1})
                        </option>
                      ))}
                    </select>
                  ) : (
                    <input
                      type="text"
                      className="form-input"
                      value={selectedRecipient}
                      onChange={(e) => setSelectedRecipient(e.target.value)}
                      placeholder="0x..."
                      required
                      disabled={isSettling}
                    />
                  )}
                  <div style={{ fontSize: '11px', color: '#10b981', marginTop: '6px' }}>
                    Escrow Balance: {(Number(selectedClaim?.bounty_amount || 0) / 1e18).toFixed(4)} GEN
                  </div>
                </div>

                <div style={{ display: 'flex', gap: '10px', marginTop: '24px' }}>
                  <button
                    type="button"
                    className="btn-secondary"
                    style={{ flex: 1, padding: '10px', fontSize: '13px' }}
                    onClick={() => setShowSettleModal(false)}
                    disabled={isSettling}
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="btn-primary"
                    style={{ flex: 2, padding: '10px', fontSize: '13px', background: '#059669', borderColor: '#10b981' }}
                    disabled={isSettling || isWrongNetwork || !selectedRecipient}
                  >
                    {isSettling ? (
                      <span style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>
                        <Loader2 size={15} className="animate-spin" />
                        Executing GEN Transfer...
                      </span>
                    ) : (
                      <span>Transfer Bounty Share</span>
                    )}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
