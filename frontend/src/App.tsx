import { useState, useEffect, useRef } from 'react';
import { 
  Mic, MicOff, Send, Shield, User, Volume2, RefreshCw, 
  AlertTriangle, CheckCircle, FileText, Check, Edit2, XCircle, Play, Sparkles
} from 'lucide-react';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface QueryResult {
  query_id: string;
  status: 'safe' | 'escalated' | 'resolved';
  final_answer: string;
  escalation_reason: string | null;
  confidence: number;
  guardrail_flags: {
    keyword_blocked?: boolean;
    pii_detected?: boolean;
    fact_mismatch?: boolean;
    policy_violation?: boolean;
    [key: string]: boolean | undefined;
  };
  citations: string[];
}

interface EscalationItem {
  id: string;
  query_id: string;
  reason: string;
  status: string;
  rm_id: string;
  transcript: string;
  draft_answer: string;
  guardrail_flags: any;
}

export default function App() {
  const [activeView, setActiveView] = useState<'rm' | 'compliance'>('rm');
  const rmId = 'RM_007';
  
  // RM State
  const [transcript, setTranscript] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [queryResult, setQueryResult] = useState<QueryResult | null>(null);
  const [textMode, setTextMode] = useState(true);
  const [speechSupported, setSpeechSupported] = useState(false);
  const [pollingActive, setPollingActive] = useState(false);
  
  // Compliance State
  const [escalations, setEscalations] = useState<EscalationItem[]>([]);
  const [resolvingId, setResolvingId] = useState<string | null>(null);
  const [complianceEdits, setComplianceEdits] = useState<{ [key: string]: string }>({});

  const recognitionRef = useRef<any>(null);

  // Initialize Speech Recognition
  useEffect(() => {
    const SpeechRecognition = 
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (SpeechRecognition) {
      setSpeechSupported(true);
      const rec = new SpeechRecognition();
      rec.continuous = false;
      rec.interimResults = false;
      rec.lang = 'en-US';
      
      rec.onstart = () => setIsRecording(true);
      rec.onend = () => setIsRecording(false);
      rec.onresult = (event: any) => {
        const text = event.results[0][0].transcript;
        setTranscript(text);
        handleQuerySubmit(text);
      };
      rec.onerror = (e: any) => {
        console.error('Speech recognition error:', e);
        setIsRecording(false);
      };
      
      recognitionRef.current = rec;
    }
  }, []);

  // Poll for resolved escalation if the RM's query was escalated
  useEffect(() => {
    let intervalId: any;
    if (pollingActive && queryResult && queryResult.status === 'escalated') {
      intervalId = setInterval(async () => {
        try {
          const res = await fetch(`${API_URL}/escalations`);
          if (res.ok) {
            const queue: EscalationItem[] = await res.json();
            const isPending = queue.some(item => item.query_id === queryResult.query_id);
            if (!isPending) {
              const auditRes = await fetch(`${API_URL}/audit/${queryResult.query_id}`);
              if (auditRes.ok) {
                const logs = await auditRes.json();
                const resolutionLog = logs.find((l: any) => l.step === 'resolution');
                if (resolutionLog) {
                  const detail = JSON.parse(resolutionLog.detail);
                  setQueryResult(prev => prev ? {
                    ...prev,
                    status: 'resolved',
                    final_answer: detail.reviewer_response || 'Approved as-is'
                  } : null);
                  setPollingActive(false);
                  playAudioResponse(detail.reviewer_response || 'Approved as-is');
                }
              }
            }
          }
        } catch (err) {
          console.error('Polling error:', err);
        }
      }, 3000);
    }
    return () => clearInterval(intervalId);
  }, [pollingActive, queryResult]);

  // Load Compliance Escalation Queue
  const fetchEscalations = async () => {
    try {
      const res = await fetch(`${API_URL}/escalations`);
      if (res.ok) {
        const data = await res.json();
        const flattened = data.map((item: any) => ({
          id: item.id,
          query_id: item.query_id,
          reason: item.reason,
          status: item.status,
          rm_id: item.queries.rm_id,
          transcript: item.queries.transcript,
          draft_answer: item.queries.draft_answer,
          guardrail_flags: typeof item.queries.guardrail_flags === 'string' 
            ? JSON.parse(item.queries.guardrail_flags) 
            : item.queries.guardrail_flags
        }));
        setEscalations(flattened);
        
        const edits: any = {};
        flattened.forEach((e: EscalationItem) => {
          edits[e.id] = e.draft_answer;
        });
        setComplianceEdits(edits);
      }
    } catch (err) {
      console.error('Failed to fetch escalations:', err);
    }
  };

  useEffect(() => {
    if (activeView === 'compliance') {
      fetchEscalations();
    }
  }, [activeView]);

  const toggleRecording = () => {
    if (!speechSupported) return;
    if (isRecording) {
      recognitionRef.current.stop();
    } else {
      setTranscript('');
      recognitionRef.current.start();
    }
  };

  const handleQuerySubmit = async (queryText: string) => {
    if (!queryText.trim()) return;
    setIsProcessing(true);
    setQueryResult(null);
    setPollingActive(false);
    
    try {
      const res = await fetch(`${API_URL}/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ transcript: queryText, rm_id: rmId })
      });
      
      if (res.ok) {
        const data: QueryResult = await res.json();
        setQueryResult(data);
        
        if (data.status === 'safe') {
          playAudioResponse(data.final_answer);
        } else if (data.status === 'escalated') {
          setPollingActive(true);
        }
      } else {
        console.error('Query request failed:', await res.text());
      }
    } catch (err) {
      console.error('Network error posting query:', err);
    } finally {
      setIsProcessing(false);
    }
  };

  const playAudioResponse = async (text: string) => {
    try {
      const res = await fetch(`${API_URL}/query/tts`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text })
      });
      if (res.ok) {
        const audioBlob = await res.blob();
        const audioUrl = URL.createObjectURL(audioBlob);
        const audio = new Audio(audioUrl);
        audio.play();
      }
    } catch (err) {
      console.error('TTS Audio streaming failed:', err);
    }
  };

  const handleResolve = async (id: string, decision: 'approved' | 'edited' | 'rejected') => {
    setResolvingId(id);
    const reviewer_response = complianceEdits[id] || '';
    
    try {
      const res = await fetch(`${API_URL}/escalations/${id}/resolve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          decision,
          reviewer_id: 'COMP_REV_007',
          reviewer_response: decision === 'rejected' ? 'Rejected by Compliance.' : reviewer_response
        })
      });
      if (res.ok) {
        await fetchEscalations();
      }
    } catch (err) {
      console.error('Failed to resolve escalation:', err);
    } finally {
      setResolvingId(null);
    }
  };

  // Helper to color code confidence
  const getConfidenceClass = (conf: number) => {
    if (conf >= 0.6) return 'high';
    if (conf >= 0.45) return 'med';
    return 'low';
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* ── HEADER ──────────────────────────────────────────────────────── */}
      <header className="app-header">
        <div className="brand-section">
          <Shield style={{ width: '32px', height: '32px', color: '#eab308' }} />
          <div>
            <h1 className="brand-title">SahayakAI</h1>
            <p className="brand-subtitle">Voice Banking Copilot & Compliance Layer</p>
          </div>
        </div>

        {/* View Switcher Tabs */}
        <div className="view-switcher">
          <button 
            onClick={() => setActiveView('rm')}
            className={`view-tab ${activeView === 'rm' ? 'active' : ''}`}
          >
            <User style={{ width: '16px', height: '16px' }} />
            RM Workspace
          </button>
          <button 
            onClick={() => setActiveView('compliance')}
            className={`view-tab ${activeView === 'compliance' ? 'active' : ''}`}
          >
            <Shield style={{ width: '16px', height: '16px' }} />
            Compliance Queue
            {escalations.length > 0 && (
              <span className="badge-count">
                {escalations.length}
              </span>
            )}
          </button>
        </div>

        <div style={{ fontSize: '14px', color: '#94a3b8' }}>
          RM ID: <span style={{ fontFamily: 'Fira Code, monospace', color: '#f1f5f9' }}>{rmId}</span>
        </div>
      </header>

      {/* ── WORKSPACE CONTENT ───────────────────────────────────────────── */}
      <main className="workspace-container">
        
        {/* ==================== RELATIONSHIP MANAGER VIEW ==================== */}
        {activeView === 'rm' && (
          <>
            {/* Left Panel: Query Input */}
            <div className="card" style={{ gridColumn: 'span 5', minHeight: '400px' }}>
              <div>
                <h2 className="card-title">
                  <User style={{ color: '#64748b', width: '20px', height: '20px' }} />
                  Ask Copilot
                </h2>
                <p className="card-desc">
                  Speak or type queries about banking products, interest rates, customer policy, or compliance guidelines.
                </p>

                {/* Speech Toggle Button & Area */}
                {speechSupported && (
                  <div className="mode-banner">
                    <span className="banner-label">Voice Input Mode</span>
                    <button 
                      onClick={() => setTextMode(!textMode)}
                      className={`banner-btn ${!textMode ? 'active' : ''}`}
                    >
                      {!textMode ? 'Voice Mode Active' : 'Switch to Voice'}
                    </button>
                  </div>
                )}

                {/* Input Fields */}
                {textMode ? (
                  <div className="input-section" style={{ marginTop: '16px' }}>
                    <textarea 
                      value={transcript}
                      onChange={(e) => setTranscript(e.target.value)}
                      placeholder="Type your question here (e.g. What is the interest rate for a 1-year FD?)..."
                      className="text-area-input"
                    />
                    <button
                      onClick={() => handleQuerySubmit(transcript)}
                      disabled={isProcessing || !transcript.trim()}
                      className="btn-primary"
                    >
                      {isProcessing ? <RefreshCw className="animate-spin" style={{ width: '16px', height: '16px' }} /> : <Send style={{ width: '16px', height: '16px' }} />}
                      Submit Query
                    </button>
                  </div>
                ) : (
                  <div className="recording-wrapper">
                    <button 
                      onClick={toggleRecording}
                      className={`mic-button ${isRecording ? 'recording' : ''}`}
                    >
                      {isRecording ? <MicOff style={{ width: '40px', height: '40px' }} /> : <Mic style={{ width: '40px', height: '40px' }} />}
                    </button>
                    <p className="rec-state-label">
                      {isRecording ? 'Listening... Speak now.' : 'Click to start recording voice query'}
                    </p>
                    {transcript && (
                      <div className="live-transcript">
                        "{transcript}"
                      </div>
                    )}
                  </div>
                )}
              </div>

              {/* Status Banner */}
              {isProcessing && (
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '12px', padding: '12px', border: '1px solid #e2e8f0', borderRadius: '8px', marginTop: '16px', backgroundColor: '#f8fafc' }}>
                  <RefreshCw className="animate-spin" style={{ width: '20px', height: '20px', color: '#475569' }} />
                  <span style={{ fontSize: '14px', fontWeight: '500' }}>Invoking LangGraph copilot pipeline...</span>
                </div>
              )}
            </div>

            {/* Right Panel: AI Results & Pipeline Output */}
            <div style={{ gridColumn: 'span 7', display: 'flex', flexDirection: 'column', gap: '24px' }}>
              
              {!queryResult && !isProcessing && (
                <div className="card" style={{ minHeight: '400px', display: 'flex', alignItems: 'center', justifyContent: 'center', textAlign: 'center' }}>
                  <Sparkles style={{ width: '48px', height: '48px', color: '#cbd5e1', marginBottom: '16px' }} />
                  <h3 style={{ margin: '0 0 8px 0', fontSize: '18px', fontWeight: '700' }}>No Query Submitted</h3>
                  <p style={{ margin: '0', fontSize: '14px', color: '#64748b', maxWidth: '320px' }}>
                    Ask a question to see real-time guardrail checks, RAG content citations, and the Compliance Officer queue behavior.
                  </p>
                </div>
              )}

              {queryResult && (
                <div className="card" style={{ gap: '24px' }}>
                  {/* Pipeline Header Status Card */}
                  <div className="pipeline-header">
                    <div>
                      {queryResult.status === 'safe' && (
                        <div className="status-pill safe">
                          <CheckCircle style={{ width: '16px', height: '16px' }} />
                          Safe Response Approved
                        </div>
                      )}
                      {queryResult.status === 'escalated' && (
                        <div className="status-pill escalated">
                          <AlertTriangle style={{ width: '16px', height: '16px' }} />
                          Escalated to Compliance Queue
                        </div>
                      )}
                      {queryResult.status === 'resolved' && (
                        <div className="status-pill resolved">
                          <Check style={{ width: '16px', height: '16px' }} />
                          Resolved by Compliance
                        </div>
                      )}
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <span style={{ fontSize: '12px', fontWeight: '700', color: '#64748b' }}>CONFIDENCE:</span>
                      <span className={`confidence-badge ${getConfidenceClass(queryResult.confidence)}`}>
                        {queryResult.confidence.toFixed(2)}
                      </span>
                    </div>
                  </div>

                  {/* Main Content Area */}
                  <div>
                    <h3 className="section-label">Final Answer</h3>
                    {queryResult.status === 'safe' || queryResult.status === 'resolved' ? (
                      <div className="final-answer-box">
                        {queryResult.final_answer}
                      </div>
                    ) : (
                      <div className="escalation-card">
                        <p className="escalation-warning-title">
                          <AlertTriangle style={{ width: '20px', height: '20px', color: '#d97706' }} />
                          HUMAN REVIEW REQUIRED
                        </p>
                        <p style={{ margin: '0', fontSize: '14px', color: '#78350f' }}>
                          This query triggered our compliance filters. The Relationship Manager is not authorized to deliver this answer directly to the customer.
                        </p>
                        <div className="escalation-reason-box">
                          REASON: {queryResult.escalation_reason}
                        </div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '12px', color: '#64748b', marginTop: '8px' }}>
                          <RefreshCw className="animate-spin" style={{ width: '14px', height: '14px' }} />
                          Waiting for Compliance Officer resolution... (Auto-polling)
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Citations */}
                  {queryResult.citations.length > 0 && (
                    <div>
                      <h4 className="section-label">Trusted Citations</h4>
                      <div style={{ display: 'flex', flexWrap: 'wrap' }}>
                        {queryResult.citations.map((cite, index) => (
                          <span key={index} className="citation-chip">
                            <FileText style={{ width: '14px', height: '14px', color: '#64748b' }} />
                            {cite}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* TTS Speaker Output */}
                  {(queryResult.status === 'safe' || queryResult.status === 'resolved') && (
                    <div className="tts-bar">
                      <span style={{ fontSize: '12px', color: '#64748b', display: 'flex', alignItems: 'center', gap: '6px' }}>
                        <Volume2 style={{ width: '16px', height: '16px' }} />
                        OpenAI TTS audio auto-played
                      </span>
                      <button 
                        onClick={() => playAudioResponse(queryResult.final_answer)}
                        className="btn-secondary"
                      >
                        <Play style={{ width: '14px', height: '14px', fill: '#334155' }} />
                        Replay Audio
                      </button>
                    </div>
                  )}

                  {/* Guardrail Flag Audit */}
                  <div style={{ borderTop: '1px solid #f1f5f9', paddingTop: '16px' }}>
                    <h4 className="section-label" style={{ marginBottom: '12px' }}>Guardrail Logs</h4>
                    <div className="guardrails-grid">
                      
                      <div className={`guardrail-card ${queryResult.guardrail_flags.keyword_blocked ? 'flagged' : ''}`}>
                        <span className="guardrail-card-title">1. Keyword Block</span>
                        <span className="guardrail-card-status">
                          {queryResult.guardrail_flags.keyword_blocked ? 'TRIGGERED' : 'PASS'}
                        </span>
                      </div>

                      <div className={`guardrail-card ${queryResult.guardrail_flags.pii_detected ? 'flagged' : ''}`}>
                        <span className="guardrail-card-title">2. PII Redaction</span>
                        <span className="guardrail-card-status">
                          {queryResult.guardrail_flags.pii_detected ? 'REDACTED' : 'PASS'}
                        </span>
                      </div>

                      <div className={`guardrail-card ${queryResult.guardrail_flags.fact_mismatch ? 'flagged' : ''}`}>
                        <span className="guardrail-card-title">3. Fact Check</span>
                        <span className="guardrail-card-status">
                          {queryResult.guardrail_flags.fact_mismatch ? 'MISMATCH' : 'PASS'}
                        </span>
                      </div>

                      <div className={`guardrail-card ${queryResult.guardrail_flags.policy_violation ? 'flagged' : ''}`}>
                        <span className="guardrail-card-title">4. Policy Advice</span>
                        <span className="guardrail-card-status">
                          {queryResult.guardrail_flags.policy_violation ? 'UNSAFE ADVICE' : 'PASS'}
                        </span>
                      </div>

                    </div>
                  </div>

                </div>
              )}

            </div>
          </>
        )}

        {/* ==================== COMPLIANCE OFFICER QUEUE VIEW ==================== */}
        {activeView === 'compliance' && (
          <div style={{ gridColumn: 'span 12', display: 'flex', flexDirection: 'column', gap: '24px' }}>
            
            {/* Header section with count */}
            <div className="card" style={{ display: 'flex', flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' }}>
              <div>
                <h2 className="card-title" style={{ fontSize: '20px' }}>
                  <Shield style={{ width: '24px', height: '24px', color: '#475569' }} />
                  Compliance Verification Queue
                </h2>
                <p style={{ margin: '4px 0 0 0', fontSize: '14px', color: '#64748b' }}>
                  Review and resolve inquiries from RMs that triggered advice policies, fact mismatch rules, or keyword blocks.
                </p>
              </div>
              <button 
                onClick={fetchEscalations}
                className="btn-secondary"
                style={{ padding: '8px 16px' }}
              >
                <RefreshCw style={{ width: '14px', height: '14px' }} />
                Refresh Queue
              </button>
            </div>

            {/* Queue List */}
            {escalations.length === 0 ? (
              <div className="card" style={{ padding: '48px', alignItems: 'center', justifyContent: 'center', textAlign: 'center' }}>
                <CheckCircle style={{ width: '48px', height: '48px', color: '#10b981', marginBottom: '16px' }} />
                <h3 style={{ margin: '0 0 8px 0', fontSize: '18px', fontWeight: '700' }}>Verification Queue Clear</h3>
                <p style={{ margin: '0', fontSize: '14px', color: '#64748b', maxWidth: '360px' }}>
                  All Relationship Manager queries are verified, clean, and complying with banking regulations.
                </p>
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
                {escalations.map((item) => (
                  <div key={item.id} className="compliance-queue-card">
                    
                    {/* Item header with reason */}
                    <div className="compliance-queue-header">
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <AlertTriangle style={{ width: '16px', height: '16px', color: '#f59e0b' }} />
                        <span style={{ fontSize: '12px', fontFamily: 'Fira Code, monospace', color: '#cbd5e1' }}>Escalation ID: {item.id.slice(0, 8)}</span>
                      </div>
                      <span className="badge-count" style={{ animation: 'none' }}>
                        {item.reason}
                      </span>
                    </div>

                    {/* Details body */}
                    <div className="compliance-queue-body">
                      
                      {/* Left: Input details */}
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                        <div>
                          <h4 className="section-label">RM Inquiry</h4>
                          <div style={{ padding: '12px', backgroundColor: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: '8px', fontSize: '14px', fontWeight: '500' }}>
                            "{item.transcript}"
                          </div>
                        </div>
                        
                        <div>
                          <h4 className="section-label">Guardrail Violations</h4>
                          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                            {item.guardrail_flags.keyword_blocked && (
                              <span className="status-pill escalated">Keyword Blocked</span>
                            )}
                            {item.guardrail_flags.pii_detected && (
                              <span className="status-pill escalated">PII Detected</span>
                            )}
                            {item.guardrail_flags.fact_mismatch && (
                              <span className="status-pill escalated">
                                Fact Mismatch: {item.guardrail_flags.fact_mismatch_detail || 'Unverified numbers'}
                              </span>
                            )}
                            {item.guardrail_flags.policy_violation && (
                              <span className="status-pill escalated">Investment Advice Warning</span>
                            )}
                          </div>
                        </div>
                      </div>

                      {/* Right: AI draft response and modification */}
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                        <h4 className="section-label">Verify or Edit AI Answer</h4>
                        <textarea
                          value={complianceEdits[item.id] || ''}
                          onChange={(e) => setComplianceEdits({ ...complianceEdits, [item.id]: e.target.value })}
                          className="text-area-input"
                          style={{ height: '140px', fontFamily: 'Fira Code, monospace' }}
                        />
                      </div>

                    </div>

                    {/* Actions footer */}
                    <div className="compliance-queue-footer">
                      <span style={{ fontSize: '13px', color: '#64748b', fontWeight: '500' }}>
                        RM: <span style={{ fontFamily: 'Fira Code, monospace' }}>{item.rm_id}</span> | Action required
                      </span>
                      
                      <div className="btn-group">
                        <button
                          onClick={() => handleResolve(item.id, 'rejected')}
                          disabled={resolvingId !== null}
                          className="btn-secondary btn-reject"
                        >
                          <XCircle style={{ width: '16px', height: '16px' }} />
                          Reject
                        </button>
                        
                        <button
                          onClick={() => handleResolve(item.id, 'edited')}
                          disabled={resolvingId !== null}
                          className="btn-primary btn-approve-edit"
                        >
                          <Edit2 style={{ width: '16px', height: '16px', color: '#facc15' }} />
                          Approve with Edits
                        </button>

                        <button
                          onClick={() => handleResolve(item.id, 'approved')}
                          disabled={resolvingId !== null}
                          className="btn-primary btn-approve"
                        >
                          <Check style={{ width: '16px', height: '16px' }} />
                          Approve As-Is
                        </button>
                      </div>
                    </div>

                  </div>
                ))}
              </div>
            )}

          </div>
        )}

      </main>
      
      {/* ── FOOTER ──────────────────────────────────────────────────────── */}
      <footer className="app-footer">
        <p>© 2026 SahayakAI. Trusted Banking Relationship Officer Platform. Built for Security & Regulatory Compliance.</p>
      </footer>
    </div>
  );
}
