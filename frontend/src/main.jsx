// @ts-nocheck - migration-friendly React entrypoint; shared domain types are in types.ts.
import React, { createContext, useContext, useEffect, useMemo, useState } from 'react';
import { motion } from 'framer-motion';
import { createRoot } from 'react-dom/client';
import { BrowserRouter, NavLink, Route, Routes, useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { AlertTriangle, ArrowRight, Award, BarChart3, Check, Clock3, Cog, Disc3, Download, Gauge, Heart, Link2, Menu, Moon, Printer, Search, ShieldCheck, Sparkles, Sun, X, Zap } from 'lucide-react';
import { BarChart, Bar, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { toast, Toaster } from 'sonner';
import { api } from './services/api';
import './styles.css';

const AppContext = createContext();
const useApp = () => useContext(AppContext);
const iconMap = { XTSR52: Disc3, XTSR71: Disc3, SERIES71: Disc3, '54RDG': Link2, '54RD': Link2 };
const NOT_SPECIFIED = 'Not specified in supplied manual';
const COUPLING_TYPE_LABEL = { spacer: 'Spacer Coupling', closed_coupled: 'Closed-Coupled' };

function Shell({children}) { const [open,setOpen]=useState(false); const {dark,setDark}=useApp(); const nav=[['/','Home'],['/select','Select Coupling'],['/library','Coupling Library'],['/compare','Compare'],['/about','About'],['/contact','Contact']]; return <><header className="sticky top-0 z-40 border-b border-slate-100 bg-white/90 backdrop-blur dark:border-slate-800 dark:bg-slate-950/90"><div className="mx-auto flex h-18 max-w-7xl items-center justify-between px-5"><NavLink to="/" className="flex items-center gap-3 font-semibold text-ink dark:text-white"><span className="grid h-9 w-9 place-items-center rounded-lg bg-navy text-white"><Cog size={21}/></span><span>Couple<span className="text-teal">Smart</span></span></NavLink><nav className="hidden gap-6 lg:flex">{nav.map(([to,label])=><NavLink key={to} to={to} end={to==='/' } className={({isActive})=>`text-sm font-medium transition ${isActive?'text-navy dark:text-teal':'text-slate-600 hover:text-navy dark:text-slate-300'}`}>{label}</NavLink>)}</nav><div className="flex items-center gap-3"><button aria-label="toggle theme" onClick={()=>setDark(!dark)} className="icon-btn">{dark?<Sun size={18}/>:<Moon size={18}/>}</button><NavLink to="/select" className="hidden rounded-lg bg-navy px-4 py-2 text-sm font-semibold text-white hover:bg-ink sm:block">Get Started</NavLink><button className="icon-btn lg:hidden" onClick={()=>setOpen(!open)}>{open?<X/>:<Menu/>}</button></div></div>{open&&<nav className="border-t bg-white p-4 dark:bg-slate-950 lg:hidden">{nav.map(([to,label])=><NavLink onClick={()=>setOpen(false)} key={to} to={to} className="block rounded-lg px-3 py-2 font-medium hover:bg-slate-100 dark:hover:bg-slate-800">{label}</NavLink>)}</nav>}</header><main>{children}</main><footer className="mt-20 bg-ink py-10 text-slate-300"><div className="mx-auto flex max-w-7xl flex-col justify-between gap-5 px-5 sm:flex-row"><div><div className="font-semibold text-white">Couple<span className="text-teal">Smart</span></div><p className="mt-2 text-sm">Engineering decisions, made reliable.</p></div><p className="text-sm">© 2026 Smart Coupling Selection Tool</p></div></footer></> }

function Home(){const nav=useNavigate(); const features=[[Award,'Manual-Grounded Data','Every rating is transcribed from the Thomas metric and imperial catalogs — nothing is estimated.'],[Clock3,'Reduced Downtime','Match capability to actual operating conditions.'],[Sparkles,'Engineering Intelligence','Transparent, step-by-step selection reasoning.'],[ShieldCheck,'Higher Reliability','Built for confident, documented decisions.'],[BarChart3,'Easy Comparison','Compare published specifications before committing.'],[Zap,'Fast Decision Making','Turn catalog research into a guided workflow.']]; return <><section className="industrial-grid overflow-hidden bg-slate-50"><div className="mx-auto grid max-w-7xl gap-12 px-5 py-20 lg:grid-cols-2 lg:py-28"><motion.div initial={{opacity:0,x:-20}} animate={{opacity:1,x:0}} className="max-w-2xl"><span className="eyebrow">ENGINEERING DECISION SUPPORT</span><h1 className="mt-5 text-4xl font-bold leading-tight text-ink dark:text-white sm:text-6xl">Smart Coupling Selection & <span className="text-navy dark:text-teal">Recommendation Tool</span></h1><p className="mt-6 max-w-xl text-lg leading-8 text-slate-600 dark:text-slate-300">Select the right Thomas flexible disc coupling in seconds, checked directly against published metric and imperial catalog ratings.</p><div className="mt-8 flex flex-wrap gap-3"><button onClick={()=>nav('/select')} className="btn-primary">Get Started <ArrowRight size={17}/></button><button onClick={()=>nav('/library')} className="btn-secondary">Explore Library</button></div><div className="mt-10 flex gap-8 text-sm"><span><strong className="block text-2xl text-ink dark:text-white">5</strong>Catalog product families</span><span><strong className="block text-2xl text-ink dark:text-white">2</strong>Spacer & close-coupled</span></div></motion.div><motion.div initial={{opacity:0,scale:.92}} animate={{opacity:1,scale:1}} transition={{delay:.15}} className="relative mx-auto flex w-full max-w-md items-center justify-center"><div className="absolute h-72 w-72 rounded-full border-[24px] border-navy/10"></div><div className="relative grid h-72 w-72 place-items-center rounded-full border-[22px] border-navy bg-white shadow-soft dark:bg-slate-900"><Cog className="text-teal" size={110}/><span className="absolute rounded-full bg-teal px-3 py-1 text-xs font-bold text-white">SYSTEM READY</span></div><div className="absolute right-0 top-8 rounded-xl bg-white p-4 shadow-soft dark:bg-slate-900"><Gauge className="text-teal"/><p className="mt-1 text-xs font-semibold">Torque matched</p></div></motion.div></div></section><section className="mx-auto max-w-7xl px-5 py-20"><div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">{features.map(([Icon,title,text],i)=><motion.article initial={{opacity:0,y:12}} whileInView={{opacity:1,y:0}} viewport={{once:true}} transition={{delay:i*.06}} key={title} className="card"><span className="mb-5 inline-grid h-11 w-11 place-items-center rounded-lg bg-teal/10 text-teal"><Icon size={22}/></span><h2 className="font-semibold text-ink dark:text-white">{title}</h2><p className="mt-2 text-sm leading-6 text-slate-500">{text}</p></motion.article>)}</div></section><section id="how" className="bg-slate-50 py-20 dark:bg-slate-900/30"><div className="mx-auto max-w-5xl px-5 text-center"><span className="eyebrow">HOW IT WORKS</span><h2 className="mt-3 text-3xl font-bold text-ink dark:text-white">From machine data to a clear decision</h2><div className="mt-12 grid gap-6 md:grid-cols-4">{['Choose coupling type, shafts, power and speed','Torque is computed and service-factored','Catalog checked for torque, bore, DBSE, speed','Smallest sufficient torque rating recommended'].map((t,i)=><div key={t} className="relative"><span className="mx-auto grid h-12 w-12 place-items-center rounded-full bg-navy font-bold text-white">0{i+1}</span><p className="mt-4 font-medium">{t}</p>{i<3&&<ArrowRight className="absolute -right-5 top-3 hidden text-teal md:block"/>}</div>)}</div></div></section><section className="mx-auto max-w-7xl px-5 py-20"><div className="grid gap-5 md:grid-cols-3">{[['“It gives our applications team a common, defensible starting point.”','Reliability Engineer','Process Manufacturing'],['“The comparison view made a difficult replacement decision much faster.”','Maintenance Manager','Bulk Materials'],['“A polished tool that translates catalog data into an actionable recommendation.”','Project Engineer','Industrial OEM']].map(([quote,role,company])=><article className="card" key={role}><p className="text-teal">★★★★★</p><p className="mt-4 leading-7 text-slate-600 dark:text-slate-300">{quote}</p><p className="mt-5 font-semibold">{role}</p><p className="text-sm text-slate-500">{company}</p></article>)}</div></section></>}

const optNum = validator => z.preprocess(v => (v===''||v===undefined||v===null?undefined:v), validator.optional());
const optStr = () => z.preprocess(v => (v===''?undefined:v), z.string().optional());
const schema = z.object({
  coupling_type: z.enum(['spacer','closed_coupled']),
  driver_shaft: z.coerce.number().positive('Enter the driver shaft diameter'),
  driver_shaft_unit: z.enum(['mm','in']),
  driven_shaft: z.coerce.number().positive('Enter the driven shaft diameter'),
  driven_shaft_unit: z.enum(['mm','in']),
  dbse: optNum(z.coerce.number().positive('Enter the required DBSE')),
  dbse_unit: optStr(),
  power: z.coerce.number().positive('Enter a valid power'),
  power_unit: z.enum(['kW','HP']),
  speed: z.coerce.number().positive('Enter a valid speed'),
  temperature_c: optNum(z.coerce.number()),
  hours_per_day: optNum(z.coerce.number().positive()),
  service_life_years: optNum(z.coerce.number().positive()),
  required_angular_misalignment_deg: optNum(z.coerce.number().nonnegative()),
  required_parallel_misalignment_mm: optNum(z.coerce.number().nonnegative()),
  shock_load: optStr(), environment: optStr(), budget: optStr(),
  precision: z.boolean().optional(), vibration_damping: z.boolean().optional(), soft_start: z.boolean().optional(),
}).refine(d => d.coupling_type !== 'spacer' || (d.dbse != null && d.dbse_unit), { message: 'DBSE is required for a spacer coupling', path: ['dbse'] });

const Input=React.forwardRef(({label,error,...props},ref)=><label className="block text-sm font-medium text-slate-700 dark:text-slate-200">{label}<input ref={ref} {...props} className="field"/>{error&&<span className="mt-1 block text-xs text-rose-600">{error}</span>}</label>);
const Select=React.forwardRef(({label,children,...props},ref)=><label className="block text-sm font-medium text-slate-700 dark:text-slate-200">{label}<select ref={ref} {...props} className="field">{children}</select></label>);
function DimensionField({label,error,valueProps,unitProps}){return <div><label className="block text-sm font-medium text-slate-700 dark:text-slate-200">{label}</label><div className="mt-2 flex gap-2"><input type="number" step="0.1" className="field mt-0 flex-1" {...valueProps}/><select className="field mt-0 w-24" {...unitProps}><option value="mm">mm</option><option value="in">in</option></select></div>{error&&<span className="mt-1 block text-xs text-rose-600">{error}</span>}</div>}

function SelectPage(){
  const nav=useNavigate(); const {setResult}=useApp();
  const {register,handleSubmit,watch,formState:{errors,isSubmitting}}=useForm({resolver:zodResolver(schema),defaultValues:{
    coupling_type:'spacer', driver_shaft:60,driver_shaft_unit:'mm', driven_shaft:60,driven_shaft_unit:'mm', dbse:150,dbse_unit:'mm',
    power:75,power_unit:'kW',speed:1480,
    temperature_c:'',hours_per_day:'',service_life_years:'',required_angular_misalignment_deg:'',required_parallel_misalignment_mm:'',
    shock_load:'',environment:'',budget:'',precision:false,vibration_damping:false,soft_start:false,
  }});
  const couplingType=watch('coupling_type'), power=watch('power'),speed=watch('speed'),powerUnit=watch('power_unit');
  const preview = power&&speed ? (powerUnit==='HP' ? 63025*power/speed : 9550*power/speed) : null;
  const previewUnit = powerUnit==='HP' ? 'lb·in' : 'N·m';
  const submit=async data=>{
    try{
      const payload={...data};
      if(payload.coupling_type!=='spacer'){delete payload.dbse; delete payload.dbse_unit;}
      const res=await api.recommend(payload); setResult(res); localStorage.setItem('recent',JSON.stringify(res)); nav('/result');
    }catch{toast.error('Recommendation service is unavailable. Please try again.')}
  };
  return <section className="mx-auto max-w-5xl px-5 py-14">
    <div className="mb-9"><span className="eyebrow">CONFIGURE YOUR DRIVE</span><h1 className="mt-3 text-3xl font-bold text-ink dark:text-white">Select a coupling</h1><p className="mt-2 text-slate-500">Tell us about your coupling type, shafts, power train and operating conditions.</p></div>
    <form onSubmit={handleSubmit(submit)} className="space-y-7">
      <FormSection title="Coupling type">
        <div className="grid gap-4 sm:grid-cols-2">
          {[['spacer','Spacer Coupling','A center spacer/adapter separates the shaft ends. Considers XTSR52, XTSR71 and legacy Series 71.'],
            ['closed_coupled','Closed-Coupled','Hubs connect with minimal shaft-to-shaft spacing, no adjustable span. Considers Series 54RDG and 54RD.']]
            .map(([val,title,desc])=>
            <label key={val} className={`cursor-pointer rounded-xl border p-4 transition ${couplingType===val?'border-navy bg-navy/5 dark:border-teal dark:bg-teal/10':'border-slate-200 dark:border-slate-700'}`}>
              <input type="radio" value={val} className="sr-only" {...register('coupling_type')}/>
              <p className="font-semibold text-ink dark:text-white">{title}</p>
              <p className="mt-1 text-sm text-slate-500">{desc}</p>
            </label>)}
        </div>
      </FormSection>
      <FormSection title="Shaft & power train">
        <div className="grid gap-5 md:grid-cols-3">
          <DimensionField label="Driver shaft diameter" error={errors.driver_shaft?.message} valueProps={register('driver_shaft')} unitProps={register('driver_shaft_unit')}/>
          <DimensionField label="Driven shaft diameter" error={errors.driven_shaft?.message} valueProps={register('driven_shaft')} unitProps={register('driven_shaft_unit')}/>
          {couplingType==='spacer' && <DimensionField label="Required DBSE" error={errors.dbse?.message} valueProps={register('dbse')} unitProps={register('dbse_unit')}/>}
          <Input label="Motor power" type="number" step="0.1" error={errors.power?.message} {...register('power')}/>
          <Select label="Power unit" {...register('power_unit')}><option value="kW">kW</option><option value="HP">HP</option></Select>
          <Input label="Motor speed (RPM)" type="number" error={errors.speed?.message} {...register('speed')}/>
        </div>
        {couplingType!=='spacer' && <p className="mt-4 text-sm text-slate-500">DBSE does not apply to a closed-coupled selection — Series 54RDG/54RD publish a single fixed dimension per size, not an adjustable span.</p>}
        {preview!=null && <p className="mt-5 self-end rounded-lg bg-teal/10 px-4 py-3 text-sm text-teal">Transmitted torque preview: <strong>{preview.toFixed(1)} {previewUnit}</strong> ({powerUnit==='HP'?'63025 × Power[HP] ÷ Speed[RPM]':'9550 × Power[kW] ÷ Speed[RPM]'}) — a 1.5× service factor is applied by the recommendation engine, and the {powerUnit==='HP'?'Imperial':'Metric'} catalog supplies the torque rating.</p>}
      </FormSection>
      <FormSection title="Operating conditions (optional)">
        <p className="mb-5 text-sm text-slate-500">These are not published per-size in the Thomas catalogs for these products, so they are reported back for context but never used to reject a candidate — except temperature below -45°C, which no catalog in this project supports for any product in scope.</p>
        <div className="grid gap-5 md:grid-cols-3">
          <Input label="Operating temperature (°C)" type="number" {...register('temperature_c')}/>
          <Input label="Operating hours / day" type="number" {...register('hours_per_day')}/>
          <Input label="Required service life (years)" type="number" {...register('service_life_years')}/>
          <Input label="Required angular misalignment (°)" type="number" step="0.01" {...register('required_angular_misalignment_deg')}/>
          <Input label="Required parallel misalignment (mm)" type="number" step="0.01" {...register('required_parallel_misalignment_mm')}/>
          <Select label="Shock load" {...register('shock_load')}><option value="">Not specified</option>{['Light','Medium','Heavy'].map(x=><option key={x}>{x}</option>)}</Select>
          <Select label="Environment" {...register('environment')}><option value="">Not specified</option>{['Indoor','Outdoor','Dusty','Wet','Chemical'].map(x=><option key={x}>{x}</option>)}</Select>
          <Select label="Budget" {...register('budget')}><option value="">Not specified</option>{['Low','Medium','High'].map(x=><option key={x}>{x}</option>)}</Select>
        </div>
        <div className="mt-6 flex flex-wrap gap-5">{[['precision','High precision'],['vibration_damping','Vibration damping required'],['soft_start','Soft starting required']].map(([v,l])=><label key={v} className="flex cursor-pointer items-center gap-2 text-sm"><input type="checkbox" className="accent-teal" {...register(v)}/>{l}</label>)}</div>
      </FormSection>
      <div className="flex justify-end"><button disabled={isSubmitting} className="btn-primary">{isSubmitting?'Evaluating…':'Recommend Coupling'} <ArrowRight size={17}/></button></div>
    </form>
  </section>;
}
function FormSection({title,children}){return <section className="card"><h2 className="mb-6 border-b border-slate-100 pb-4 text-lg font-semibold text-ink dark:border-slate-800 dark:text-white">{title}</h2>{children}</section>}

function Row({k,v}){return <div className="flex justify-between gap-4 border-b border-slate-100 pb-2 dark:border-slate-800"><dt className="text-slate-500">{k}</dt><dd className="font-medium text-right">{v}</dd></div>}
function Steps({steps}){return <ol className="mt-4 space-y-4">{steps.map((s,i)=><li key={s.label} className="flex gap-4"><span className="grid h-7 w-7 shrink-0 place-items-center rounded-full bg-navy/10 text-xs font-bold text-navy dark:bg-teal/10 dark:text-teal">{i+1}</span><div><p className="text-sm font-semibold text-ink dark:text-white">{s.label}</p><p className="mt-0.5 text-sm text-slate-500">{s.detail}</p></div></li>)}</ol>}

function Infeasible({result,nav}){const d=result.diagnostics; return <section className="mx-auto max-w-4xl px-5 py-14"><span className="eyebrow">NO MATCH FOUND</span><h1 className="mt-3 text-3xl font-bold text-ink dark:text-white">No coupling satisfies every requirement</h1><div className="mt-8 grid gap-6 md:grid-cols-2"><article className="card"><p className="text-sm text-slate-500">Transmitted torque</p><p className="mt-1 text-3xl font-bold text-ink dark:text-white">{result.transmitted_torque.value.toLocaleString()} {result.transmitted_torque.unit}</p><p className="mt-3 text-sm text-slate-500">Required (× {result.service_factor} service factor)</p><p className="mt-1 text-2xl font-bold text-navy dark:text-teal">{result.required_torque.value.toLocaleString()} {result.required_torque.unit}</p></article>{d&&<article className="card"><p className="text-sm text-slate-500">Constraint pass rate across {d.total} {COUPLING_TYPE_LABEL[result.coupling_type]} catalog entries</p><dl className="mt-4 space-y-3 text-sm"><Row k="Torque capacity" v={`${d.torque_pass} / ${d.total}`}/><Row k="Shaft bore" v={`${d.bore_pass} / ${d.total}`}/><Row k="DBSE range" v={`${d.dbse_pass} / ${d.total}`}/><Row k="Max speed" v={`${d.speed_pass} / ${d.total}`}/><Row k="Temperature" v={`${d.temperature_pass} / ${d.total}`}/></dl></article>}</div><article className="card mt-6"><h2 className="font-semibold text-ink dark:text-white">Why nothing qualified</h2><ul className="mt-4 space-y-3">{result.reasoning.map(x=><li key={x} className="flex gap-3 text-sm text-slate-600 dark:text-slate-300"><AlertTriangle className="shrink-0 text-rose-500" size={18}/>{x}</li>)}</ul></article><button onClick={()=>nav('/select')} className="btn-primary mt-8">Adjust requirements <ArrowRight size={17}/></button></section>}

function RecommendationCard({c,result}){
  const Icon=iconMap[c.product]||Cog; const isSpacer=c.coupling_type==='spacer';
  const metric=result.torque_catalog.includes('Metric'); const dimUnit=metric?'mm':'in'; const torqueUnit=result.required_torque.unit;
  const torqueNative=metric?c.max_continuous_torque_nm:c.max_continuous_torque_lbin;
  const peakNative=metric?c.peak_overload_torque_nm:c.peak_overload_torque_lbin;
  const minDbse=metric?c.min_dbse_mm:c.min_dbse_in, maxDbse=metric?c.max_dbse_mm:c.max_dbse_in;
  const boreKey=metric?'max_bore_mm':'max_bore_in';
  const weight=metric?c.weight_kg:c.weight_lb, weightUnit=metric?'kg':'lb';
  const sourceRef=metric?c.source_reference_metric:c.source_reference_imperial;
  return <article className="card">
    <div className="flex items-center gap-4">
      <span className="grid h-16 w-16 shrink-0 place-items-center rounded-xl bg-navy/10 text-navy dark:bg-teal/10 dark:text-teal"><Icon size={30}/></span>
      <div><p className="text-xs font-semibold text-teal">{c.product} · {result.torque_catalog}</p><h3 className="text-xl font-bold text-ink dark:text-white">{c.name}</h3><p className="text-sm text-slate-500">{c.disc_pack_style}, {c.standard_balance} balance</p></div>
    </div>
    <dl className="mt-5 space-y-2 text-sm">
      <Row k="Continuous torque rating" v={torqueNative!=null?`${torqueNative.toLocaleString()} ${torqueUnit}`:NOT_SPECIFIED}/>
      <Row k="Peak overload torque" v={peakNative!=null?`${peakNative.toLocaleString()} ${torqueUnit}`:NOT_SPECIFIED}/>
      <Row k="Hub configuration" v={c.hub_configuration}/>
      <Row k="Driver-side hub/bore" v={c.driver_bore_configuration?`${c.driver_bore_configuration.label} — ${c.driver_bore_configuration[boreKey]} ${dimUnit} max`:'—'}/>
      <Row k="Driven-side hub/bore" v={c.driven_bore_configuration?`${c.driven_bore_configuration.label} — ${c.driven_bore_configuration[boreKey]} ${dimUnit} max`:'—'}/>
      {c.bore_options?.length>1 && <Row k="All documented hub options" v={c.bore_options.map(o=>`${o.label}: ${o[boreKey]??'—'} ${dimUnit}`).join(', ')}/>}
      {isSpacer ? <Row k="DBSE range" v={minDbse!=null?`${minDbse}–${maxDbse} ${dimUnit}${!c.dbse_max_documented?' (Std. length used as reference — no Max. C published)':''}`:NOT_SPECIFIED}/>
                : <Row k="DBSE / spacer span" v="Not applicable — close-coupled design"/>}
      <Row k="Speed limit (as mfd.)" v={c.max_speed_as_mfd_rpm?`${c.max_speed_as_mfd_rpm.toLocaleString()} RPM`:NOT_SPECIFIED}/>
      <Row k="Angular misalignment" v={c.angular_misalignment_label}/>
      <Row k="Parallel misalignment" v={c.parallel_misalignment}/>
      <Row k="Temperature rating" v={c.temperature_rating}/>
      <Row k="Weight" v={weight!=null?`${weight} ${weightUnit}`:NOT_SPECIFIED}/>
    </dl>
    <div className="mt-5"><p className="text-sm font-semibold text-ink dark:text-white">Why it qualifies</p><ul className="mt-2 space-y-2">{c.qualifies_because.map(x=><li key={x} className="flex gap-2 text-sm text-slate-600 dark:text-slate-300"><Check size={16} className="mt-0.5 shrink-0 text-teal"/>{x}</li>)}</ul></div>
    {c.optional_condition_notes?.length>0 && <div className="mt-4"><p className="text-sm font-semibold text-ink dark:text-white">Operating-condition notes</p><ul className="mt-2 space-y-1">{c.optional_condition_notes.map(x=><li key={x} className="text-xs text-slate-500">{x}</li>)}</ul></div>}
    <div className="mt-4 border-t border-slate-100 pt-3 text-xs text-slate-400 dark:border-slate-800">
      <p>Materials: {c.disc_pack_material}; {c.major_component_material}; {c.bolt_material}. Coating: {c.coating}.</p>
      <p className="mt-1">Compliance: {c.api_compliance}</p>
      <p className="mt-1">Source: {sourceRef}</p>
    </div>
  </article>;
}

function Result(){
  const {result}=useApp(); const nav=useNavigate();
  if(!result) return <section className="mx-auto max-w-xl px-5 py-24 text-center"><h1 className="text-2xl font-bold">No selection yet</h1><button onClick={()=>nav('/select')} className="btn-primary mt-5">Start a selection</button></section>;
  if(!result.feasible) return <Infeasible result={result} nav={nav}/>;
  const report=()=>window.print();
  const winners=result.valid_recommendations;
  const metric=result.torque_catalog.includes('Metric');
  const chart=[...winners,...result.alternatives].map(c=>({name:c.name, weight: metric?c.weight_kg:c.weight_lb}));
  const rejected=(result.product_summary||[]).filter(p=>p.status==='rejected');
  return <section className="mx-auto max-w-6xl px-5 py-14">
    <div className="no-print mb-7 flex flex-wrap items-center justify-between gap-4">
      <div><span className="eyebrow">RECOMMENDATION READY</span><h1 className="mt-2 text-3xl font-bold text-ink dark:text-white">Your coupling selection{winners.length>1?'s':''}</h1></div>
      <div className="flex gap-3"><button onClick={report} className="btn-secondary"><Printer size={17}/> Print Report</button><button onClick={report} className="btn-primary"><Download size={17}/> Download PDF</button></div>
    </div>
    <div className="card mb-6 grid gap-4 sm:grid-cols-5">
      <div><p className="text-xs text-slate-500">Coupling type</p><p className="font-semibold text-ink dark:text-white">{COUPLING_TYPE_LABEL[result.coupling_type]}</p></div>
      <div><p className="text-xs text-slate-500">Torque catalog</p><p className="font-semibold text-ink dark:text-white">{result.torque_catalog}</p></div>
      <div><p className="text-xs text-slate-500">Transmitted torque</p><p className="font-semibold text-ink dark:text-white">{result.transmitted_torque.value.toLocaleString()} {result.transmitted_torque.unit}</p></div>
      <div><p className="text-xs text-slate-500">Service factor</p><p className="font-semibold text-ink dark:text-white">× {result.service_factor}</p></div>
      <div><p className="text-xs text-slate-500">Required torque</p><p className="font-semibold text-navy dark:text-teal">{result.required_torque.value.toLocaleString()} {result.required_torque.unit}</p></div>
    </div>
    {winners.length>1 && <div className="card mb-6 border-teal/30 bg-teal/5"><p className="text-sm text-ink dark:text-white"><strong>{winners.length} equally valid options</strong> share the minimum sufficient torque rating of {winners[0].max_continuous_torque_nm && metric ? winners[0].max_continuous_torque_nm.toLocaleString() : winners[0].max_continuous_torque_lbin?.toLocaleString()} {result.required_torque.unit} across distinct catalog products — both are shown rather than arbitrarily picking one.</p></div>}
    <div className={`grid gap-6 ${winners.length>1?'md:grid-cols-2':''}`}>{winners.map(c=><RecommendationCard key={c.id} c={c} result={result}/>)}</div>
    {rejected.length>0 && <section className="card mt-6"><h2 className="font-semibold text-ink dark:text-white">Other product families considered</h2><ul className="mt-4 space-y-2">{rejected.map(p=><li key={p.product} className="flex gap-3 text-sm text-slate-600 dark:text-slate-300"><AlertTriangle size={16} className="mt-0.5 shrink-0 text-amber-500"/>{p.reason}</li>)}</ul></section>}
    <section className="card mt-6"><h2 className="font-semibold text-ink dark:text-white">Weight comparison</h2><div className="mt-3 h-52"><ResponsiveContainer width="100%" height="100%"><BarChart data={chart}><XAxis dataKey="name" fontSize={11}/><YAxis fontSize={12} unit={metric?' kg':' lb'}/><Tooltip/><Bar dataKey="weight" fill="#2AA198" radius={[5,5,0,0]}/></BarChart></ResponsiveContainer></div></section>
    <section className="card mt-6"><h2 className="font-semibold text-ink dark:text-white">Selection trace</h2><Steps steps={result.selection_steps}/></section>
    {result.alternatives.length>0 && <section className="mt-8"><h2 className="text-xl font-bold text-ink dark:text-white">Alternatives to consider</h2><div className="mt-4 grid gap-4 md:grid-cols-3">{result.alternatives.map(a=><article className="card" key={a.id}><p className="font-semibold">{a.name}</p><p className="mt-2 text-sm text-slate-500">{a.disc_pack_style}</p><p className="mt-4 text-sm font-medium text-teal">{(metric?a.max_continuous_torque_nm:a.max_continuous_torque_lbin)?.toLocaleString()} {result.required_torque.unit} rated</p></article>)}</div></section>}
  </section>;
}

function useCouplings(){const [data,setData]=useState(null),[error,setError]=useState(false); useEffect(()=>{let live=true; api.couplings().then(d=>live&&setData(d)).catch(()=>live&&setError(true)); return()=>{live=false}},[]); return {data,error}}
function StateBanner({error}){return error?<div className="card flex items-center gap-3 border-rose-200 bg-rose-50 text-rose-700 dark:border-rose-900 dark:bg-rose-950 dark:text-rose-300"><AlertTriangle size={20}/> Could not reach the coupling API. Start the backend and reload — this page does not fall back to placeholder data.</div>:<div className="card text-center text-slate-500">Loading catalog data…</div>}
function maxBore(c,key){const vals=(c.bore_options||[]).map(o=>o[key]).filter(v=>v!=null); return vals.length?Math.max(...vals):null}

function Library(){
  const {data,error}=useCouplings();
  const [query,setQuery]=useState(''),[typeFilter,setTypeFilter]=useState('All'),[productFilter,setProductFilter]=useState('All');
  const [favorites,setFavorites]=useState(()=>JSON.parse(localStorage.getItem('favorites')||'[]'));
  const toggle=id=>{const n=favorites.includes(id)?favorites.filter(x=>x!==id):[...favorites,id];setFavorites(n);localStorage.setItem('favorites',JSON.stringify(n));};
  const products=useMemo(()=>['All',...Array.from(new Set((data||[]).map(c=>c.product)))],[data]);
  const show=useMemo(()=>(data||[]).filter(c=>(typeFilter==='All'||c.coupling_type===typeFilter)&&(productFilter==='All'||c.product===productFilter)&&(c.name.toLowerCase().includes(query.toLowerCase())||c.size.toLowerCase().includes(query.toLowerCase()))),[data,typeFilter,productFilter,query]);
  return <section className="mx-auto max-w-7xl px-5 py-14">
    <span className="eyebrow">ENGINEERING CATALOG</span><h1 className="mt-3 text-3xl font-bold text-ink dark:text-white">Coupling library</h1>
    <p className="mt-2 text-slate-500">Regal Rexnord Thomas Flexible Disc Couplings — metric &amp; imperial catalogs, spacer &amp; close-coupled products.</p>
    <div className="mt-7 flex flex-col gap-3 sm:flex-row">
      <label className="relative flex-1"><Search className="absolute left-3 top-3 text-slate-400" size={18}/><input className="field pl-10" placeholder="Search by name or size…" value={query} onChange={e=>setQuery(e.target.value)}/></label>
      <select className="field sm:w-52" value={typeFilter} onChange={e=>setTypeFilter(e.target.value)}><option value="All">All coupling types</option><option value="spacer">Spacer</option><option value="closed_coupled">Closed-coupled</option></select>
      <select className="field sm:w-52" value={productFilter} onChange={e=>setProductFilter(e.target.value)}>{products.map(p=><option key={p} value={p}>{p==='All'?'All products':p}</option>)}</select>
    </div>
    {!data?<div className="mt-7"><StateBanner error={error}/></div>:<div className="mt-7 grid gap-5 md:grid-cols-2 xl:grid-cols-3">{show.map(c=>{
      const Icon=iconMap[c.product]||Cog; const maxBoreMm=maxBore(c,'max_bore_mm'), maxBoreIn=maxBore(c,'max_bore_in');
      return <article className="card group" key={c.id}>
        <div className="flex justify-between"><span className="grid h-14 w-14 place-items-center rounded-xl bg-navy/10 text-navy dark:text-teal"><Icon size={30}/></span><button aria-label="favorite" onClick={()=>toggle(c.id)}><Heart size={20} className={favorites.includes(c.id)?'fill-rose-500 text-rose-500':'text-slate-400'}/></button></div>
        <h2 className="mt-5 text-lg font-semibold text-ink dark:text-white">{c.name}</h2>
        <p className="mt-2 text-sm leading-6 text-slate-500">{COUPLING_TYPE_LABEL[c.coupling_type]} · {c.disc_pack_style}, {c.standard_balance} balance.</p>
        <div className="mt-5 grid grid-cols-2 gap-3 border-t border-slate-100 pt-4 text-xs dark:border-slate-800">
          <span><b className="block text-ink dark:text-white">{c.max_continuous_torque_nm?.toLocaleString()??'—'} N·m</b>{c.max_continuous_torque_lbin?.toLocaleString()??'—'} lb·in continuous</span>
          <span><b className="block text-ink dark:text-white">{maxBoreMm??'—'} mm</b>{maxBoreIn??'—'} in max bore</span>
          <span><b className="block text-ink dark:text-white">{c.coupling_type==='spacer'?(c.min_dbse_mm!=null?`${c.min_dbse_mm}–${c.max_dbse_mm} mm`:'—'):'Fixed'}</b>DBSE</span>
          <span><b className="block text-ink dark:text-white">{c.weight_kg??'—'} kg</b>{c.weight_lb??'—'} lb</span>
        </div>
      </article>})}</div>}
  </section>;
}

function Compare(){
  const {data,error}=useCouplings(); const [a,setA]=useState(''),[b,setB]=useState('');
  useEffect(()=>{if(data&&data.length>1&&!a&&!b){setA(data[0].id);setB(data[1].id)}},[data]);
  if(!data)return <section className="mx-auto max-w-5xl px-5 py-14"><span className="eyebrow">SIDE-BY-SIDE ANALYSIS</span><h1 className="mt-3 text-3xl font-bold text-ink dark:text-white">Compare couplings</h1><div className="mt-8"><StateBanner error={error}/></div></section>;
  const x=data.find(c=>c.id===+a)||data[0],y=data.find(c=>c.id===+b)||data[1];
  const dbse=c=>c.coupling_type==='spacer'?(c.min_dbse_mm!=null?`${c.min_dbse_mm}–${c.max_dbse_mm} mm / ${c.min_dbse_in}–${c.max_dbse_in} in${!c.dbse_max_documented?' (Std. length ref.)':''}`:NOT_SPECIFIED):'Not applicable (close-coupled)';
  const rows=[
    ['Coupling type',COUPLING_TYPE_LABEL[x.coupling_type],COUPLING_TYPE_LABEL[y.coupling_type]],
    ['Product',x.product,y.product],
    ['Disc pack style',x.disc_pack_style,y.disc_pack_style],
    ['Standard balance',x.standard_balance,y.standard_balance],
    ['Angular misalignment',x.angular_misalignment_label,y.angular_misalignment_label],
    ['Parallel misalignment',x.parallel_misalignment,y.parallel_misalignment],
    ['Axial capacity',`${x.axial_capacity_mm??'—'} mm / ${x.axial_capacity_in??'—'} in`,`${y.axial_capacity_mm??'—'} mm / ${y.axial_capacity_in??'—'} in`],
    ['Max continuous torque',`${x.max_continuous_torque_nm?.toLocaleString()??'—'} N·m / ${x.max_continuous_torque_lbin?.toLocaleString()??'—'} lb·in`,`${y.max_continuous_torque_nm?.toLocaleString()??'—'} N·m / ${y.max_continuous_torque_lbin?.toLocaleString()??'—'} lb·in`],
    ['Peak overload torque',`${x.peak_overload_torque_nm?.toLocaleString()??'—'} N·m / ${x.peak_overload_torque_lbin?.toLocaleString()??'—'} lb·in`,`${y.peak_overload_torque_nm?.toLocaleString()??'—'} N·m / ${y.peak_overload_torque_lbin?.toLocaleString()??'—'} lb·in`],
    ['Max bore available',`${maxBore(x,'max_bore_mm')??'—'} mm / ${maxBore(x,'max_bore_in')??'—'} in`,`${maxBore(y,'max_bore_mm')??'—'} mm / ${maxBore(y,'max_bore_in')??'—'} in`],
    ['DBSE range',dbse(x),dbse(y)],
    ['Max speed (as mfd.)',`${x.max_speed_as_mfd_rpm?.toLocaleString()??'—'} RPM`,`${y.max_speed_as_mfd_rpm?.toLocaleString()??'—'} RPM`],
    ['Max speed (balanced)',`${x.max_speed_balanced_rpm?.toLocaleString()??'—'} RPM`,`${y.max_speed_balanced_rpm?.toLocaleString()??'—'} RPM`],
    ['Weight',`${x.weight_kg??'—'} kg / ${x.weight_lb??'—'} lb`,`${y.weight_kg??'—'} kg / ${y.weight_lb??'—'} lb`],
    ['Disc pack material',x.disc_pack_material,y.disc_pack_material],
    ['Major component material',x.major_component_material,y.major_component_material],
    ['Bolt material',x.bolt_material,y.bolt_material],
    ['Coating',x.coating,y.coating],
    ['Temperature rating',x.temperature_rating,y.temperature_rating],
    ['API / ATEX compliance',x.api_compliance,y.api_compliance],
    ['Typical applications',x.typical_applications,y.typical_applications],
  ];
  return <section className="mx-auto max-w-5xl px-5 py-14"><span className="eyebrow">SIDE-BY-SIDE ANALYSIS</span><h1 className="mt-3 text-3xl font-bold text-ink dark:text-white">Compare couplings</h1>
    <div className="mt-8 grid gap-4 sm:grid-cols-2">{[[a,setA],[b,setB]].map(([val,set],i)=><Select key={i} label={i?'Coupling B':'Coupling A'} value={val} onChange={e=>set(e.target.value)}>{data.map(c=><option value={c.id} key={c.id}>{c.name}</option>)}</Select>)}</div>
    <div className="mt-8 overflow-x-auto rounded-xl border border-slate-200 dark:border-slate-800"><table className="w-full text-left text-sm"><thead className="bg-ink text-white"><tr><th className="p-4">Criteria</th><th className="p-4">{x.name}</th><th className="p-4">{y.name}</th></tr></thead><tbody>{rows.map(r=><tr key={r[0]} className="border-t border-slate-100 even:bg-slate-50 dark:border-slate-800 dark:even:bg-slate-900"><td className="p-4 font-semibold">{r[0]}</td><td className="p-4 text-slate-600 dark:text-slate-300">{r[1]}</td><td className="p-4 text-slate-600 dark:text-slate-300">{r[2]}</td></tr>)}</tbody></table></div>
  </section>;
}

function About(){return <section className="mx-auto max-w-5xl px-5 py-14"><span className="eyebrow">ABOUT THE PLATFORM</span><h1 className="mt-3 text-4xl font-bold text-ink dark:text-white">Engineering knowledge, made accessible.</h1><div className="mt-10 space-y-6">{[['Problem statement','Industrial coupling selection still relies heavily on manual catalogs, past experience and trial-and-error. That leaves teams vulnerable to avoidable failures, downtime and maintenance cost.'],['Our objectives','Reduce manual effort, improve selection accuracy, reduce unplanned downtime and support more reliable machine performance with clear engineering rationale, grounded entirely in published Thomas catalog data — both metric and imperial editions.'],['Future scope','The platform is designed to evolve with additional coupling series and manufacturers without rewriting the selection engine, plus machine-learning models, IoT operating data, digital-twin simulation and CAD integration.']].map(([h,p])=><article className="card" key={h}><h2 className="text-xl font-semibold text-ink dark:text-white">{h}</h2><p className="mt-3 leading-7 text-slate-600 dark:text-slate-300">{p}</p></article>)}</div></section>}
function Contact(){const {register,handleSubmit,reset}=useForm(); const submit=()=>{toast.success('Thanks — your message has been received.');reset()}; return <section className="mx-auto max-w-2xl px-5 py-14"><span className="eyebrow">CONTACT</span><h1 className="mt-3 text-3xl font-bold text-ink dark:text-white">Talk to the engineering team</h1><form onSubmit={handleSubmit(submit)} className="card mt-8 space-y-5"><Input label="Name" required {...register('name')}/><Input label="Company" required {...register('company')}/><Input label="Email" type="email" required {...register('email')}/><label className="block text-sm font-medium">Message<textarea className="field min-h-32" required {...register('message')}/></label><button className="btn-primary">Send Message <ArrowRight size={17}/></button></form></section>}
function NotFound(){return <section className="mx-auto max-w-xl px-5 py-24 text-center"><p className="text-7xl font-bold text-teal">404</p><h1 className="mt-5 text-2xl font-bold">This shaft isn’t connected.</h1><NavLink className="btn-primary mt-6 inline-flex" to="/">Back home</NavLink></section>}

function App(){const [dark,setDark]=useState(()=>localStorage.theme==='dark');const [result,setResult]=useState(()=>JSON.parse(localStorage.getItem('recent')||'null'));useEffect(()=>{document.documentElement.classList.toggle('dark',dark);localStorage.theme=dark?'dark':'light'},[dark]);return <AppContext.Provider value={{dark,setDark,result,setResult}}><BrowserRouter><Shell><Routes><Route path="/" element={<Home/>}/><Route path="/select" element={<SelectPage/>}/><Route path="/result" element={<Result/>}/><Route path="/library" element={<Library/>}/><Route path="/compare" element={<Compare/>}/><Route path="/about" element={<About/>}/><Route path="/contact" element={<Contact/>}/><Route path="*" element={<NotFound/>}/></Routes></Shell><Toaster richColors position="top-right"/></BrowserRouter></AppContext.Provider>};
createRoot(document.getElementById('root')).render(<App/>);
