"""Production-oriented API for Smart Coupling Selection & Recommendation Tool."""
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Literal
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import Float, Integer, String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

DB_PATH = Path(__file__).parent / "database" / "couplings.db"
engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
class Base(DeclarativeBase): pass
class Coupling(Base):
    __tablename__="couplings"
    id:Mapped[int]=mapped_column(Integer,primary_key=True); name:Mapped[str]=mapped_column(String,unique=True); type:Mapped[str]=mapped_column(String)
    description:Mapped[str]=mapped_column(String); working_principle:Mapped[str]=mapped_column(String); torque_min:Mapped[float]=mapped_column(Float); torque_max:Mapped[float]=mapped_column(Float); speed_min:Mapped[float]=mapped_column(Float); speed_max:Mapped[float]=mapped_column(Float)
    misalignment:Mapped[str]=mapped_column(String); shock_load:Mapped[str]=mapped_column(String); environment:Mapped[str]=mapped_column(String); maintenance:Mapped[str]=mapped_column(String); cost:Mapped[str]=mapped_column(String); applications:Mapped[str]=mapped_column(String); advantages:Mapped[str]=mapped_column(String); limitations:Mapped[str]=mapped_column(String); life:Mapped[str]=mapped_column(String); efficiency:Mapped[float]=mapped_column(Float)
SEED=[
 ("Jaw Coupling","Jaw",10,1800,100,8000,"Medium","Medium","Indoor, outdoor","Low","Low","Pumps, fans, gearboxes","Elastomer spider transmits torque while damping vibration.","Damps vibration; easy insert replacement","Limited high-torque capacity","5–8 years",98),
 ("Gear Coupling","Gear",500,25000,100,6000,"Medium","Heavy","Indoor, dusty","High","High","Mills, turbines, heavy conveyors","Crowned gear teeth transmit high torque across flexible hubs.","Very high torque; compact design","Requires lubrication and alignment checks","10–15 years",99),
 ("Grid Coupling","Grid",200,4500,100,5000,"Medium","Heavy","Indoor, dusty","Medium","Medium","Crushers, conveyors, pumps","A resilient steel grid connects slotted hubs and cushions shock.","Excellent shock absorption; high torque capacity","Periodic lubrication needed","8–12 years",98),
 ("Disc Coupling","Disc",50,8000,500,15000,"High","Light","Indoor, chemical","Low","High","Compressors, pumps, test rigs","Flexible metallic discs transfer torque without backlash.","Backlash-free; no lubrication","Limited damping of shock loads","10–15 years",99),
 ("Tyre Coupling","Tyre",30,6000,100,4500,"High","Medium","Indoor, outdoor","Low","Medium","Conveyors, fans, mixers","A rubber tyre element flexes between flanged hubs.","High damping; simple replacement","Tyre may degrade in harsh chemicals","5–7 years",97),
 ("Fluid Coupling","Fluid",100,15000,500,3600,"Low","Heavy","Indoor, dusty","Medium","High","Conveyors, crushers, mills","Hydrodynamic oil flow transfers torque without mechanical contact.","Soft start; overload protection","Power loss and heat generation","8–12 years",94),
 ("Chain Coupling","Chain",40,4000,100,3000,"Low","Medium","Indoor, dusty","High","Low","Conveyors, agitators","Duplex roller chain meshes with two sprocket hubs.","Economical; easy installation","Lubrication required; can be noisy","4–7 years",96),
 ("Pin Bush Coupling","Pin",100,8000,100,4000,"Medium","Heavy","Indoor, outdoor","Medium","Medium","Crushers, pumps, mixers","Flexible bushes on drive pins cushion between flanges.","Shock cushioning; reliable","Bush replacement needed","6–10 years",97),
 ("Rigid Coupling","Rigid",20,10000,100,10000,"None","Medium","Indoor","Low","Low","Line shafts, precision-aligned drives","Machined hubs clamp both perfectly aligned shafts.","High efficiency; lowest cost","No misalignment or damping capability","15+ years",99),
 ("Elastomer Coupling","Elastomer",15,3500,100,7000,"Medium","Medium","Indoor, wet","Low","Medium","Pumps, HVAC, compressors","An engineered elastomer element isolates torsional vibration.","Excellent vibration damping; maintenance free","Temperature and chemical sensitivity","5–8 years",97)]
def get_db():
    db=SessionLocal()
    try: yield db
    finally: db.close()
def out(c:Coupling): return {k:getattr(c,k) for k in Coupling.__table__.columns.keys()} | {"disadvantages":c.limitations}
def seed():
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        if db.scalar(select(Coupling.id).limit(1)) is None:
            for row in SEED:
                n,t,tmin,tmax,smin,smax,mis,shock,env,maint,cost,apps,principle,adv,lim,life,eff=row
                db.add(Coupling(name=n,type=t,description=f"{t} coupling for industrial power transmission.",working_principle=principle,torque_min=tmin,torque_max=tmax,speed_min=smin,speed_max=smax,misalignment=mis,shock_load=shock,environment=env,maintenance=maint,cost=cost,applications=apps,advantages=adv,limitations=lim,life=life,efficiency=eff))
            db.commit()
@asynccontextmanager
async def lifespan(_:FastAPI): seed(); yield
app=FastAPI(title="Smart Coupling API",version="2.0.0",lifespan=lifespan)
app.add_middleware(CORSMiddleware,allow_origins=["http://localhost:5173"],allow_methods=["*"],allow_headers=["*"])
class TorqueInput(BaseModel): power:float=Field(gt=0); speed:float=Field(gt=0)
class Request(BaseModel):
    machine_name:str=Field(min_length=2); application:str; power:float=Field(gt=0); speed:float=Field(gt=0); torque:float=Field(ge=0); temperature:float; hours:float=Field(gt=0); misalignment:Literal['Low','Medium','High']; shock_load:Literal['Light','Medium','Heavy']; environment:str; service_life:float=Field(gt=0); budget:Literal['Low','Medium','High']; precision:bool=False; vibration_damping:bool=False; soft_start:bool=False
class CompareInput(BaseModel): coupling_ids:list[int]=Field(min_length=2,max_length=2)
@app.get('/health')
def health(): return {"status":"ok"}
@app.get('/couplings')
def couplings(db:Session=Depends(get_db)): return [out(c) for c in db.scalars(select(Coupling).order_by(Coupling.name))]
@app.get('/couplings/{coupling_id}')
def coupling(coupling_id:int,db:Session=Depends(get_db)):
    c=db.get(Coupling,coupling_id)
    if not c: raise HTTPException(404,"Coupling not found")
    return out(c)
@app.post('/calculate-torque')
def torque(data:TorqueInput): return {"torque":round(9550*data.power/data.speed,2),"formula":"9550 × Power (kW) / RPM"}
def score(c:Coupling,d:Request):
    s=0; why=[]
    if c.torque_min<=d.torque<=c.torque_max: s+=27; why.append("Torque is inside the rated capacity range")
    elif d.torque<c.torque_min: s+=9
    if c.speed_min<=d.speed<=c.speed_max: s+=16; why.append("Speed is within the recommended operating range")
    levels={'None':0,'Low':1,'Medium':2,'High':3}; s+=12 if levels.get(c.misalignment,0)>=levels[d.misalignment] else 1
    if c.shock_load==d.shock_load:s+=12;why.append(f"Designed for {d.shock_load.lower()} shock duty")
    if d.application.lower() in c.applications.lower():s+=12;why.append(f"Proven for {d.application.lower()} applications")
    if d.environment.lower() in c.environment.lower():s+=7
    if -20<=d.temperature<=90:s+=4
    if c.cost==d.budget:s+=4
    if d.soft_start and c.type=='Fluid':s+=18;why.append("Fluid coupling fulfils soft-start requirement")
    if d.precision and c.type=='Disc':s+=16;why.append("Disc pack supports precision, backlash-free operation")
    if d.vibration_damping and c.type in ('Jaw','Tyre','Elastomer'):s+=12;why.append("Flexible element provides vibration damping")
    return min(98,max(15,s)),why
@app.post('/recommend')
def recommend(data:Request,db:Session=Depends(get_db)):
    ranked=sorted(((score(c,data),c) for c in db.scalars(select(Coupling))),key=lambda x:x[0][0],reverse=True)
    (fit,reasons),winner=ranked[0]
    reasons=(reasons+[f"{winner.maintenance} maintenance profile supports the stated duty cycle"])[:4]
    return {"recommendation":out(winner),"suitability_score":fit,"confidence_score":min(96,fit-2),"reasoning":reasons,"alternatives":[out(c)|{"score":v[0]} for v,c in ranked[1:4]]}
@app.post('/compare')
def compare(data:CompareInput,db:Session=Depends(get_db)):
    items=[db.get(Coupling,i) for i in data.coupling_ids]
    if not all(items):raise HTTPException(404,"One or more couplings were not found")
    return [out(c) for c in items]
