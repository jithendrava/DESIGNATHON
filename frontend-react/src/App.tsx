import { useMemo, useState } from 'react'
import { NavLink, Route, Routes, useNavigate } from 'react-router-dom'
import {
  Activity, AlertTriangle, ArrowUpRight, CalendarClock, ClipboardCheck,
  LayoutDashboard, ListChecks, LogOut, Search, Stethoscope, UserRound,
} from 'lucide-react'
import { Bar, BarChart, CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'

const patientsSeed = [
  { id: 'UCI-1001', name: 'John Carter', department: 'Cardiology', risk: 84, status: 'Pending', driver: 'Prior inpatient admissions', age: 72 },
  { id: 'UCI-1002', name: 'Maria Garcia', department: 'Internal Medicine', risk: 69, status: 'In review', driver: 'Extended hospital stay', age: 68 },
  { id: 'UCI-1003', name: 'David Wilson', department: 'Neurology', risk: 76, status: 'Pending', driver: 'Age 80+', age: 81 },
  { id: 'UCI-1004', name: 'Aisha Khan', department: 'Internal Medicine', risk: 43, status: 'Approved', driver: 'Medication count', age: 55 },
  { id: 'UCI-1005', name: 'Robert Brown', department: 'Cardiology', risk: 81, status: 'Pending', driver: 'Emergency visits', age: 76 },
  { id: 'UCI-1006', name: 'Emma Davis', department: 'Orthopedics', risk: 28, status: 'Approved', driver: 'Low-risk profile', age: 63 },
]

function riskClass(risk: number) {
  return risk >= 70 ? 'high' : risk >= 40 ? 'medium' : 'low'
}

function Shell() {
  const [search, setSearch] = useState('')
  const navigate = useNavigate()

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <button className="brand" onClick={() => navigate('/')}>
          <div className="brand-mark"><Activity size={20} /></div>
          <div><strong>ReadmissionAI</strong><span>Care Coordination</span></div>
        </button>

        <nav>
          <NavLink to="/" end><LayoutDashboard size={18} />Overview</NavLink>
          <NavLink to="/worklist"><ListChecks size={18} />Care Worklist</NavLink>
          <NavLink to="/review"><ClipboardCheck size={18} />Clinician Review</NavLink>
          <NavLink to="/dashboard"><Activity size={18} />Trends</NavLink>
        </nav>

        <div className="sidebar-bottom">
          <div className="model-status"><span className="status-dot" />Model active</div>
          <button className="profile"><div className="avatar">DR</div><div><strong>Dr. Roberts</strong><span>Clinician</span></div><LogOut size={16} /></button>
        </div>
      </aside>

      <main>
        <header className="topbar">
          <div className="search"><Search size={17} /><input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search patients or encounters" /></div>
          <button className="notification"><AlertTriangle size={18} /><span>3</span></button>
        </header>
        <Routes>
          <Route path="/" element={<Overview search={search} />} />
          <Route path="/worklist" element={<Worklist />} />
          <Route path="/review" element={<ClinicianReview />} />
          <Route path="/dashboard" element={<Trends />} />
        </Routes>
      </main>
    </div>
  )
}

function Overview({ search }: { search: string }) {
  const visible = useMemo(() => patientsSeed.filter(p => `${p.name} ${p.id} ${p.department}`.toLowerCase().includes(search.toLowerCase())).sort((a,b) => b.risk-a.risk), [search])
  return (
    <div className="page">
      <div className="page-heading"><div><span className="eyebrow">CLINICAL OVERVIEW</span><h1>Patient risk overview</h1><p>AI-supported prioritization requiring clinician review</p></div><button className="primary"><ArrowUpRight size={17} />Run risk assessment</button></div>
      <section className="metrics">
        <Metric label="High-risk patients" value="3" detail="Requires action" tone="red" />
        <Metric label="Moderate risk" value="2" detail="Monitor closely" tone="amber" />
        <Metric label="Pending review" value="3" detail="Clinician action" tone="blue" />
        <Metric label="Today's discharges" value="6" detail="2 from yesterday" tone="green" />
      </section>
      <section className="grid-two">
        <div className="panel"><div className="panel-heading"><div><span>PRIORITY QUEUE</span><h2>Patients nearing discharge</h2></div><button className="text-button">View worklist</button></div>
          <div className="table">
            <div className="table-head"><span>Patient</span><span>Department</span><span>Risk</span><span>Primary driver</span></div>
            {visible.map(p => <div className="table-row" key={p.id}><div className="patient"><div className="patient-avatar">{p.name.split(' ').map(x=>x[0]).join('')}</div><div><strong>{p.name}</strong><small>{p.id}</small></div></div><span>{p.department}</span><Risk risk={p.risk} /><span className="muted">{p.driver}</span></div>)}
          </div>
        </div>
        <div className="panel"><div className="panel-heading"><div><span>RISK DISTRIBUTION</span><h2>Current census</h2></div></div>
          <div className="donut-wrap"><div className="donut"><div><strong>6</strong><span>patients</span></div></div><div className="legend"><div><i className="red" />High <strong>3</strong></div><div><i className="amber" />Moderate <strong>2</strong></div><div><i className="green" />Low <strong>1</strong></div></div></div>
        </div>
      </section>
    </div>
  )
}

function Worklist() {
  const [filter, setFilter] = useState('All')
  const items = filter === 'All' ? patientsSeed : patientsSeed.filter(p => filter === 'High' ? p.risk >= 70 : filter === 'Moderate' ? p.risk >= 40 && p.risk < 70 : p.risk < 40)
  return <div className="page"><div className="page-heading"><div><span className="eyebrow">CARE COORDINATION</span><h1>Prioritized worklist</h1><p>Actionable follow-up queue sorted by risk</p></div></div>
    <div className="filters">{['All','High','Moderate','Low'].map(x => <button className={filter===x?'active':''} onClick={()=>setFilter(x)} key={x}>{x} risk</button>)}</div>
    <div className="worklist">{items.sort((a,b)=>b.risk-a.risk).map(p => <article className="work-card" key={p.id}><div className="patient"><div className="patient-avatar">{p.name.split(' ').map(x=>x[0]).join('')}</div><div><strong>{p.name}</strong><small>{p.id} · {p.department}</small></div></div><Risk risk={p.risk}/><div className="intervention"><span>SUGGESTED ACTION</span><strong>{p.risk >= 70 ? 'Medication reconciliation + 48-hour call' : p.risk >= 40 ? 'Schedule 7-day follow-up' : 'Standard discharge education'}</strong></div><select defaultValue="Not started"><option>Not started</option><option>Scheduled</option><option>In progress</option><option>Completed</option></select></article>)}</div>
  </div>
}

function ClinicianReview() {
  const [patientId, setPatientId] = useState(patientsSeed[0].id)
  const patient = patientsSeed.find(p => p.id === patientId)!
  const [decision, setDecision] = useState('Approve plan')
  const [language, setLanguage] = useState('English')
  const [draft, setDraft] = useState('')
  const [draftProvider, setDraftProvider] = useState('')
  const [generating, setGenerating] = useState(false)

  async function generateDraft(task: 'discharge_summary' | 'clinician_note' | 'reminder') {
    setGenerating(true)
    try {
      const apiUrl = import.meta.env.VITE_API_URL || '/api'
      const response = await fetch(`${apiUrl}/genai/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          task,
          name: patient.name,
          language,
          risk: patient.risk,
          drivers: [patient.driver, 'Extended length of stay', 'Medication count'],
          interventions: patient.risk >= 70
            ? ['Priority 48-hour follow-up call', 'Medication reconciliation', 'Care manager review']
            : ['Schedule 7-day follow-up', 'Medication review'],
        }),
      })
      const result = await response.json()
      setDraft(result.text || '')
      setDraftProvider(result.provider || 'gen-ai')
    } catch {
      setDraft('Draft unavailable. Please retry or use standard discharge guidance.')
      setDraftProvider('offline-safe-fallback')
    } finally {
      setGenerating(false)
    }
  }

  return <div className="page"><div className="page-heading"><div><span className="eyebrow">CLINICAL DECISION SUPPORT</span><h1>Clinician review</h1><p>Required approval before intervention plans are released</p></div></div>
    <div className="review-layout"><section className="panel review-patient"><div className="review-head"><div className="patient"><div className="patient-avatar large">JC</div><div><strong>{patient.name}</strong><small>{patient.id} · {patient.department}</small></div></div><Risk risk={patient.risk}/></div>
      <label className="field-label">Select patient<select value={patientId} onChange={(e)=>setPatientId(e.target.value)}>{patientsSeed.map(p=> <option value={p.id} key={p.id}>{p.name}</option>)}</select></label>
      <h3>Top risk drivers</h3><div className="drivers"><div><span>01</span><strong>{patient.driver}</strong><em>High contribution</em></div><div><span>02</span><strong>Extended length of stay</strong><em>Moderate contribution</em></div><div><span>03</span><strong>Medication count</strong><em>Moderate contribution</em></div></div>
      <h3>Gen AI discharge draft</h3>
      <div className="genai-actions">
        <select value={language} onChange={(e) => setLanguage(e.target.value)}><option>English</option><option>Hindi</option></select>
        <button className="secondary-button" onClick={() => generateDraft('discharge_summary')} disabled={generating}>{generating ? 'Generating...' : 'Generate summary'}</button>
        <button className="secondary-button" onClick={() => generateDraft('reminder')} disabled={generating}>Generate reminder</button>
      </div>
      {draft && <div className="genai-draft"><div className="draft-meta"><span>AI DRAFT</span><em>{draftProvider}</em></div><p>{draft}</p><small>Requires clinician review before use.</small></div>}
    </section><aside className="panel review-plan"><h2>Recommended plan</h2><label><input type="checkbox" defaultChecked /> Priority 48-hour follow-up call</label><label><input type="checkbox" defaultChecked /> Medication reconciliation</label><label><input type="checkbox" defaultChecked /> Care manager review</label><label><input type="checkbox" /> Community support coordination</label><h3>Clinical decision</h3>{['Approve plan','Modify plan','Defer to later'].map(x => <label className="radio" key={x}><input type="radio" checked={decision===x} onChange={()=>setDecision(x)} />{x}</label>)}<textarea placeholder="Clinical note or rationale" /><button className="primary full" onClick={() => generateDraft('clinician_note')}>Draft clinician note with Gen AI</button><button className="primary full">Submit review</button></aside></div>
  </div>
}

function Trends() {
  const trend = [{month:'Jan',rate:14.2},{month:'Feb',rate:13.8},{month:'Mar',rate:13.1},{month:'Apr',rate:12.6},{month:'May',rate:11.9},{month:'Jun',rate:11.4}]
  const departments = [{name:'Cardiology',rate:14.8},{name:'Internal Medicine',rate:13.2},{name:'Neurology',rate:11.7},{name:'Orthopedics',rate:9.4},{name:'Pulmonology',rate:16.1}]
  return <div className="page"><div className="page-heading"><div><span className="eyebrow">QUALITY & OUTCOMES</span><h1>Readmission trends</h1><p>Monthly and department-level performance</p></div></div><section className="metrics"><Metric label="30-day readmission rate" value="11.4%" detail="-0.5 pts" tone="green"/><Metric label="Test ROC-AUC" value="0.666" detail="UCI dataset" tone="blue"/><Metric label="Bed-days avoided" value="24" detail="Estimated" tone="amber"/></section>
    <section className="grid-two"><div className="panel"><div className="panel-heading"><div><span>MONTHLY TREND</span><h2>Readmission rate</h2></div></div><ResponsiveContainer width="100%" height={260}><LineChart data={trend}><CartesianGrid stroke="#1e3852"/><XAxis dataKey="month" stroke="#91a5bc"/><YAxis stroke="#91a5bc"/><Tooltip/><Line type="monotone" dataKey="rate" stroke="#5b8def" strokeWidth={3}/></LineChart></ResponsiveContainer></div>
    <div className="panel"><div className="panel-heading"><div><span>BY DEPARTMENT</span><h2>Demo department rates</h2></div></div><ResponsiveContainer width="100%" height={260}><BarChart data={departments}><CartesianGrid stroke="#1e3852"/><XAxis dataKey="name" stroke="#91a5bc"/><YAxis stroke="#91a5bc"/><Tooltip/><Bar dataKey="rate" fill="#4c82d8" radius={[6,6,0,0]}/></BarChart></ResponsiveContainer></div></section>
  </div>
}

function Metric({label,value,detail,tone}:{label:string,value:string,detail:string,tone:string}){return <article className="metric-card"><div className={`metric-icon ${tone}`}><Activity size={19}/></div><div><span>{label}</span><strong>{value}</strong><small>{detail}</small></div></article>}
function Risk({risk}:{risk:number}){return <div className={`risk ${riskClass(risk)}`}><strong>{risk}%</strong><span>{risk>=70?'High':risk>=40?'Moderate':'Low'}</span></div>}

export default Shell
