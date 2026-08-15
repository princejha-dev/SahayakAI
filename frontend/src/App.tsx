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
  const audioRef = useRef<HTMLAudioElement | null>(null);

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
      
      rec.onstart = () => {
        setIsRecording(true);
        // Stop any currently playing audio so it doesn't feed back into the mic
        if (audioRef.current) {
          audioRef.current.pause();
        }
      };
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
      const baseUrl = API_URL.endsWith('/') ? API_URL.slice(0, -1) : API_URL;
      intervalId = setInterval(async () => {
        try {
          const res = await fetch(`${baseUrl}/escalations?_t=${Date.now()}`);
          if (res.ok) {
            const queue: EscalationItem[] = await res.json();
            const isPending = queue.some(item => item.query_id === queryResult.query_id);
            if (!isPending) {
              const auditRes = await fetch(`${baseUrl}/audit/${queryResult.query_id}?_t=${Date.now()}`);
              if (auditRes.ok) {
                const logs = await auditRes.json();
                const resolutionLog = logs.find((l: any) => l.step === 'resolution');
                if (resolutionLog) {
                  const detail = typeof resolutionLog.detail === 'string' 
                    ? JSON.parse(resolutionLog.detail) 
                    : resolutionLog.detail;
                  setQueryResult(prev => prev ? {
                    ...prev,
                    status: 'resolved',
                    final_answer: detail.reviewer_response || 'Approved as-is'
                  } : null);
                  setPollingActive(false);
                  
                  // Speak resolved answer
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
      // Normalize URL to handle trailing slashes safely and add cache buster
      const baseUrl = API_URL.endsWith('/') ? API_URL.slice(0, -1) : API_URL;
      const res = await fetch(`${baseUrl}/escalations?_t=${Date.now()}`);
      if (res.ok) {
        const data = await res.json();
        const flattened = data.map((item: any) => ({
          id: item.id,
          query_id: item.query_id,
          reason: item.reason,
          status: item.status,
          rm_id: item.rm_id,
          transcript: item.transcript,
          draft_answer: item.draft_answer,
          guardrail_flags: typeof item.guardrail_flags === 'string' 
            ? JSON.parse(item.guardrail_flags) 
            : item.guardrail_flags
        }));
        setEscalations(flattened);
        
        setComplianceEdits(prev => {
          const edits = { ...prev };
          flattened.forEach((e: EscalationItem) => {
            if (edits[e.id] === undefined) {
              edits[e.id] = e.draft_answer;
            }
          });
          return edits;
        });
      }
    } catch (err) {
      console.error('Failed to fetch escalations:', err);
    }
  };

  // Load escalations on mount and periodically to keep the header badge updated
  useEffect(() => {
    fetchEscalations();
    const interval = setInterval(fetchEscalations, 10000); // refresh badge every 10s
    return () => clearInterval(interval);
  }, []);

  // Force reload escalations when switching view to Compliance
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
      try {
        recognitionRef.current.start();
      } catch (e) {
        console.error('Failed to start speech recognition:', e);
      }
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
          fetchEscalations(); // Immediately update the Compliance tab badge count
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
        audioRef.current = audio;
        
        // Auto-restart listening after the response ends, IF user is in Voice mode
        audio.onended = () => {
          if (!textMode && speechSupported) {
            try {
              recognitionRef.current.start();
            } catch (e) {
              console.log('Auto-listening restart skipped (already active/unsupported):', e);
            }
          }
        };

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
      const baseUrl = API_URL.endsWith('/') ? API_URL.slice(0, -1) : API_URL;
      const res = await fetch(`${baseUrl}/escalations/${id}/resolve`, {
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

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 font-sans flex flex-col">
      {/* ── HEADER ──────────────────────────────────────────────────────── */}
      <header className="bg-slate-900 text-white shadow-lg px-6 py-4 flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <Shield className="w-8 h-8 text-yellow-500" />
          <div>
            <h1 className="text-xl font-bold tracking-wide">SahayakAI</h1>
            <p className="text-xs text-slate-400">Voice Banking Copilot & Compliance Layer</p>
          </div>
        </div>

        {/* View Switcher Tabs */}
        <div className="flex bg-slate-800 p-1 rounded-lg border border-slate-700 w-full md:w-auto justify-center">
          <button 
            onClick={() => setActiveView('rm')}
            className={`flex items-center justify-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-all w-1/2 md:w-auto ${
              activeView === 'rm' 
                ? 'bg-slate-700 text-white shadow' 
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <User className="w-4 h-4" />
            RM Workspace
          </button>
          <button 
            onClick={() => setActiveView('compliance')}
            className={`flex items-center justify-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-all w-1/2 md:w-auto ${
              activeView === 'compliance' 
                ? 'bg-slate-700 text-white shadow' 
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Shield className="w-4 h-4" />
            Compliance Queue
            {escalations.length > 0 && (
              <span className="bg-yellow-600 text-white text-xs px-2 py-0.5 rounded-full font-bold ml-1 animate-pulse">
                {escalations.length}
              </span>
            )}
          </button>
        </div>

        <div className="text-sm text-slate-400">
          RM ID: <span className="text-slate-200 font-mono">{rmId}</span>
        </div>
      </header>

      {/* ── WORKSPACE CONTENT ───────────────────────────────────────────── */}
      <main className="flex-grow p-4 md:p-8 max-w-7xl w-full mx-auto grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        {/* ==================== RELATIONSHIP MANAGER VIEW ==================== */}
        {activeView === 'rm' && (
          <>
            {/* Left Panel: Query Input */}
            <div className="lg:col-span-5 bg-white p-6 rounded-2xl shadow-sm border border-slate-200 flex flex-col justify-between min-h-[420px] transition-all duration-300">
              <div>
                <h2 className="text-lg font-bold mb-2 flex items-center gap-2 text-slate-900">
                  <User className="text-slate-500 w-5 h-5" />
                  Ask Copilot
                </h2>
                <p className="text-sm text-slate-500 mb-6">
                  Speak or type queries about banking products, rates, or policies.
                </p>

                {/* Speech Toggle Button & Area */}
                {speechSupported && (
                  <div className="flex items-center justify-between mb-4 bg-slate-50 p-3 rounded-lg border border-slate-200">
                    <span className="text-sm font-medium text-slate-700">Voice Assistant Mode</span>
                    <button 
                      onClick={() => {
                        setTextMode(!textMode);
                        if (isRecording) recognitionRef.current.stop();
                      }}
                      className={`text-xs px-3 py-1 rounded font-bold border transition-all duration-200 ${
                        !textMode 
                          ? 'bg-slate-900 text-white border-slate-900' 
                          : 'bg-white text-slate-700 border-slate-300 hover:bg-slate-50'
                      }`}
                    >
                      {!textMode ? 'Voice Mode Active' : 'Enable Voice'}
                    </button>
                  </div>
                )}

                {/* Input Fields */}
                {textMode ? (
                  <div className="flex flex-col gap-2">
                    <textarea 
                      value={transcript}
                      onChange={(e) => setTranscript(e.target.value)}
                      placeholder="Type your question here (e.g. What is the interest rate on a 1-year fixed deposit?)..."
                      className="w-full h-32 p-3 bg-slate-50 rounded-lg border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-slate-900 transition-shadow"
                    />
                    <button
                      onClick={() => handleQuerySubmit(transcript)}
                      disabled={isProcessing || !transcript.trim()}
                      className="mt-2 flex items-center justify-center gap-2 bg-slate-900 hover:bg-slate-800 text-white font-bold py-2.5 px-4 rounded-lg transition disabled:opacity-50 cursor-pointer"
                    >
                      {isProcessing ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
                      Submit Query
                    </button>
                  </div>
                ) : (
                  <div className="flex flex-col items-center justify-center py-6">
                    <button 
                      onClick={toggleRecording}
                      className={`w-24 h-24 rounded-full flex items-center justify-center transition-all duration-300 cursor-pointer ${
                        isRecording 
                          ? 'bg-red-500 hover:bg-red-600 text-white animate-pulse shadow-lg shadow-red-500/50' 
                          : 'bg-slate-100 hover:bg-slate-200 border border-slate-300 text-slate-700'
                      }`}
                    >
                      {isRecording ? <MicOff className="w-10 h-10 animate-bounce" /> : <Mic className="w-10 h-10" />}
                    </button>
                    <p className="text-xs text-slate-500 mt-4">
                      {isRecording ? 'Listening... speak now.' : 'Click to start recording voice input'}
                    </p>
                    {transcript && (
                      <div className="mt-4 p-3 bg-slate-50 rounded-lg border border-slate-200 text-sm text-slate-700 text-center italic w-full">
                        "{transcript}"
                      </div>
                    )}
                  </div>
                )}
              </div>

              {/* Status Banner */}
              {isProcessing && (
                <div className="flex items-center justify-center gap-3 bg-slate-50 p-3 rounded-lg border border-slate-200 mt-4">
                  <RefreshCw className="w-5 h-5 text-slate-600 animate-spin" />
                  <span className="text-sm font-medium text-slate-700">Running guardrail check pipeline...</span>
                </div>
              )}
            </div>

            {/* Right Panel: AI Results & Pipeline Output */}
            <div className="lg:col-span-7 flex flex-col gap-6 w-full">
              
              {!queryResult && !isProcessing && (
                <div className="bg-white p-8 rounded-2xl shadow-sm border border-slate-200 flex flex-col items-center justify-center text-center min-h-[420px]">
                  <Sparkles className="w-12 h-12 text-slate-300 mb-4" />
                  <h3 className="text-lg font-bold text-slate-800">No Query Processed</h3>
                  <p className="text-sm text-slate-500 max-w-sm mt-2">
                    Ask a question to see real-time guardrail checks, RAG content citations, and the Compliance Officer queue behavior.
                  </p>
                </div>
              )}

              {queryResult && (
                <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 flex flex-col gap-6">
                  {/* Pipeline Header Status Card */}
                  <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-slate-100 pb-4">
                    <div className="flex items-center gap-3">
                      {queryResult.status === 'safe' && (
                        <div className="flex items-center gap-2 bg-emerald-50 text-emerald-800 px-3 py-1.5 rounded-full text-xs font-bold border border-emerald-200">
                          <CheckCircle className="w-4 h-4" />
                          Safe Response Approved
                        </div>
                      )}
                      {queryResult.status === 'escalated' && (
                        <div className="flex items-center gap-2 bg-amber-50 text-amber-800 px-3 py-1.5 rounded-full text-xs font-bold border border-amber-200 animate-pulse">
                          <AlertTriangle className="w-4 h-4" />
                          Escalated to Compliance Queue
                        </div>
                      )}
                      {queryResult.status === 'resolved' && (
                        <div className="flex items-center gap-2 bg-blue-50 text-blue-800 px-3 py-1.5 rounded-full text-xs font-bold border border-blue-200 font-medium">
                          <Check className="w-4 h-4" />
                          Resolved by Compliance
                        </div>
                      )}
                    </div>

                    <div className="flex items-center gap-2">
                      <span className="text-xs text-slate-500 font-bold uppercase">Confidence:</span>
                      <span className={`text-sm px-2.5 py-1 rounded-md font-mono font-bold ${
                        queryResult.confidence >= 0.6 
                          ? 'bg-emerald-100 text-emerald-800' 
                          : queryResult.confidence >= 0.45 
                          ? 'bg-amber-100 text-amber-800' 
                          : 'bg-red-100 text-red-800'
                      }`}>
                        {queryResult.confidence.toFixed(2)}
                      </span>
                    </div>
                  </div>

                  {/* Main Content Area */}
                  <div>
                    <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">Final Answer</h3>
                    {queryResult.status === 'safe' || queryResult.status === 'resolved' ? (
                      <div className="bg-slate-50 p-4 rounded-xl border border-slate-200 text-slate-900 leading-relaxed font-medium">
                        {queryResult.final_answer}
                      </div>
                    ) : (
                      <div className="bg-amber-50/50 border border-amber-200 rounded-xl p-5 text-slate-800 flex flex-col gap-3">
                        <p className="font-semibold text-amber-900 flex items-center gap-2">
                          <AlertTriangle className="w-5 h-5 text-amber-600" />
                          HUMAN REVIEW REQUIRED
                        </p>
                        <p className="text-sm text-amber-800">
                          This query triggered our compliance filters. The Relationship Manager is not authorized to deliver this answer directly to the customer.
                        </p>
                        <div className="text-xs font-bold bg-amber-100 text-amber-800 p-2.5 rounded border border-amber-200 font-mono">
                          REASON: {queryResult.escalation_reason}
                        </div>
                        <div className="flex items-center gap-2 text-xs text-slate-500 mt-2">
                          <RefreshCw className="w-4 h-4 animate-spin text-slate-600" />
                          Waiting for Compliance resolution... (Auto-polling)
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Citations */}
                  {queryResult.citations.length > 0 && (
                    <div>
                      <h4 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">Citations</h4>
                      <div className="flex flex-wrap gap-2">
                        {queryResult.citations.map((cite, index) => (
                          <span key={index} className="flex items-center gap-1.5 bg-slate-100 text-slate-800 text-xs px-2.5 py-1 rounded-md border border-slate-200 font-medium">
                            <FileText className="w-3.5 h-3.5 text-slate-500" />
                            {cite}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* TTS Speaker Output */}
                  {(queryResult.status === 'safe' || queryResult.status === 'resolved') && (
                    <div className="flex items-center justify-between border-t border-slate-100 pt-4 mt-2">
                      <span className="text-xs text-slate-500 flex items-center gap-1.5 font-medium">
                        <Volume2 className="w-4 h-4 text-slate-600" />
                        Audio auto-play enabled
                      </span>
                      <button 
                        onClick={() => playAudioResponse(queryResult.final_answer)}
                        className="flex items-center gap-1.5 text-xs text-slate-700 hover:text-slate-900 font-bold border border-slate-300 hover:border-slate-400 bg-white hover:bg-slate-50 px-3 py-1.5 rounded transition cursor-pointer"
                      >
                        <Play className="w-3.5 h-3.5 fill-slate-700" />
                        Replay Audio
                      </button>
                    </div>
                  )}

                  {/* Guardrail Flag Audit */}
                  <div className="border-t border-slate-100 pt-4">
                    <h4 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-3">Guardrail Logs</h4>
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
                      
                      <div className={`p-2.5 rounded-lg border flex flex-col justify-between ${
                        queryResult.guardrail_flags.keyword_blocked 
                          ? 'bg-red-50 border-red-200 text-red-800' 
                          : 'bg-slate-50 border-slate-200 text-slate-700'
                      }`}>
                        <span className="font-bold">1. Keyword Block</span>
                        <span className="mt-1 font-mono text-[10px]">
                          {queryResult.guardrail_flags.keyword_blocked ? 'TRIGGERED' : 'PASS'}
                        </span>
                      </div>

                      <div className={`p-2.5 rounded-lg border flex flex-col justify-between ${
                        queryResult.guardrail_flags.pii_detected 
                          ? 'bg-yellow-50 border-yellow-200 text-yellow-800' 
                          : 'bg-slate-50 border-slate-200 text-slate-700'
                      }`}>
                        <span className="font-bold">2. PII Redaction</span>
                        <span className="mt-1 font-mono text-[10px]">
                          {queryResult.guardrail_flags.pii_detected ? 'REDACTED' : 'PASS'}
                        </span>
                      </div>

                      <div className={`p-2.5 rounded-lg border flex flex-col justify-between ${
                        queryResult.guardrail_flags.fact_mismatch 
                          ? 'bg-red-50 border-red-200 text-red-800' 
                          : 'bg-slate-50 border-slate-200 text-slate-700'
                      }`}>
                        <span className="font-bold">3. Fact Check</span>
                        <span className="mt-1 font-mono text-[10px]">
                          {queryResult.guardrail_flags.fact_mismatch ? 'MISMATCH' : 'PASS'}
                        </span>
                      </div>

                      <div className={`p-2.5 rounded-lg border flex flex-col justify-between ${
                        queryResult.guardrail_flags.policy_violation 
                          ? 'bg-red-50 border-red-200 text-red-800' 
                          : 'bg-slate-50 border-slate-200 text-slate-700'
                      }`}>
                        <span className="font-bold">4. Policy Advice</span>
                        <span className="mt-1 font-mono text-[10px]">
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
          <div className="lg:col-span-12 flex flex-col gap-6 w-full">
            
            {/* Header section with count */}
            <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
              <div>
                <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
                  <Shield className="w-5 h-5 text-slate-500" />
                  Compliance Verification Queue
                </h2>
                <p className="text-sm text-slate-500 mt-1">
                  Review and resolve inquiries from RMs that triggered advice policies, fact mismatch rules, or keyword blocks.
                </p>
              </div>
              <button 
                onClick={fetchEscalations}
                className="flex items-center gap-2 text-xs font-bold text-slate-700 hover:text-slate-900 bg-slate-100 hover:bg-slate-200 py-2 px-4 rounded-lg border border-slate-300 transition-all cursor-pointer w-full sm:w-auto justify-center"
              >
                <RefreshCw className="w-3.5 h-3.5 text-slate-600" />
                Refresh Queue
              </button>
            </div>

            {/* Queue List */}
            {escalations.length === 0 ? (
              <div className="bg-white p-12 rounded-2xl shadow-sm border border-slate-200 flex flex-col items-center justify-center text-center">
                <CheckCircle className="w-12 h-12 text-emerald-500 mb-4" />
                <h3 className="text-lg font-bold text-slate-800">Verification Queue Clear</h3>
                <p className="text-sm text-slate-500 max-w-sm mt-2">
                  All Relationship Manager queries are verified, clean, and complying with banking regulations.
                </p>
              </div>
            ) : (
              <div className="flex flex-col gap-6">
                {escalations.map((item) => (
                  <div key={item.id} className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden flex flex-col">
                    
                    {/* Item header with reason */}
                    <div className="bg-slate-900 text-white px-6 py-3.5 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2">
                      <div className="flex items-center gap-2">
                        <AlertTriangle className="w-4 h-4 text-yellow-500" />
                        <span className="text-xs font-mono text-slate-400">Escalation ID: {item.id.slice(0, 8)}</span>
                      </div>
                      <span className="bg-yellow-600 text-white text-[10px] uppercase font-bold px-2 py-0.5 rounded-full font-mono">
                        {item.reason}
                      </span>
                    </div>

                    {/* Details body */}
                    <div className="p-6 grid grid-cols-1 md:grid-cols-2 gap-6 border-b border-slate-100">
                      
                      {/* Left: Input details */}
                      <div className="flex flex-col gap-4">
                        <div>
                          <h4 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-1">RM Inquiry</h4>
                          <div className="bg-slate-50 p-3 rounded-lg border border-slate-200 text-sm font-medium text-slate-900">
                            "{item.transcript}"
                          </div>
                        </div>
                        
                        <div>
                          <h4 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">Guardrail Violations</h4>
                          <div className="flex flex-wrap gap-2 text-xs">
                            {item.guardrail_flags.keyword_blocked && (
                              <span className="bg-red-50 text-red-800 px-2 py-1 rounded border border-red-200 font-medium">
                                Keyword Blocked
                              </span>
                            )}
                            {item.guardrail_flags.pii_detected && (
                              <span className="bg-yellow-50 text-yellow-800 px-2 py-1 rounded border border-yellow-200 font-medium">
                                PII Detected
                              </span>
                            )}
                            {item.guardrail_flags.fact_mismatch && (
                              <span className="bg-red-50 text-red-800 px-2 py-1 rounded border border-red-200 font-medium">
                                Fact Mismatch: {item.guardrail_flags.fact_mismatch_detail || 'Unverified numbers'}
                              </span>
                            )}
                            {item.guardrail_flags.policy_violation && (
                              <span className="bg-red-50 text-red-800 px-2 py-1 rounded border border-red-200 font-medium">
                                Investment Advice Warning
                              </span>
                            )}
                          </div>
                        </div>
                      </div>

                      {/* Right: AI draft response and modification */}
                      <div className="flex flex-col gap-3">
                        <h4 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-1">Verify or Edit AI Answer</h4>
                        <textarea
                          value={complianceEdits[item.id] || ''}
                          onChange={(e) => setComplianceEdits({ ...complianceEdits, [item.id]: e.target.value })}
                          className="w-full h-32 p-3 bg-slate-50 rounded-lg border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-slate-900 font-mono text-slate-800"
                        />
                      </div>

                    </div>

                    {/* Actions footer */}
                    <div className="bg-slate-50 px-6 py-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                      <span className="text-xs text-slate-500 font-medium">
                        RM: <span className="font-mono">{item.rm_id}</span> | Action required
                      </span>
                      
                      <div className="flex flex-wrap gap-2 w-full sm:w-auto">
                        <button
                          onClick={() => handleResolve(item.id, 'rejected')}
                          disabled={resolvingId !== null}
                          className="flex items-center justify-center gap-1.5 bg-white hover:bg-red-50 text-red-700 hover:text-red-800 text-xs font-bold border border-red-300 px-4 py-2 rounded-lg transition disabled:opacity-50 cursor-pointer w-full sm:w-auto"
                        >
                          <XCircle className="w-4 h-4" />
                          Reject
                        </button>
                        
                        <button
                          onClick={() => handleResolve(item.id, 'edited')}
                          disabled={resolvingId !== null}
                          className="flex items-center justify-center gap-1.5 bg-slate-900 hover:bg-slate-850 text-white text-xs font-bold px-4 py-2 rounded-lg transition disabled:opacity-50 cursor-pointer w-full sm:w-auto"
                        >
                          <Edit2 className="w-4 h-4 text-yellow-500" />
                          Approve with Edits
                        </button>

                        <button
                          onClick={() => handleResolve(item.id, 'approved')}
                          disabled={resolvingId !== null}
                          className="flex items-center justify-center gap-1.5 bg-emerald-700 hover:bg-emerald-800 text-white text-xs font-bold px-4 py-2 rounded-lg transition disabled:opacity-50 cursor-pointer w-full sm:w-auto"
                        >
                          <Check className="w-4 h-4" />
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
      <footer className="bg-slate-900 text-slate-500 py-6 border-t border-slate-800 px-6 text-center text-xs">
        <p>© 2026 SahayakAI. Trusted Banking Relationship Officer Platform. Built for Security & Regulatory Compliance.</p>
      </footer>
    </div>
  );
}
