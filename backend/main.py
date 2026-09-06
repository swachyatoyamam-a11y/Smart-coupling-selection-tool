"""Smart Coupling Selection & Recommendation Tool API.

Coupling data in this file is transcribed directly from the Regal Rexnord
Thomas Flexible Disc Couplings METRIC catalog (Catalog 2000M), covering the
XTSR52 (non-adapter spacer) and XTSR71 (adapter spacer) series across their
full published size range (494-5258). No values are estimated or invented:
where the manual does not publish a figure (e.g. parallel misalignment or
temperature ratings for these series), the field is left null and the API
reports "Not specified in supplied manual" rather than guessing.

Source pages: XTSR52 pp. 11-13, XTSR71 pp. 14-16 of Catalog 2000M.
"""
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Literal, Optional
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import Float, Integer, String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

DB_PATH = Path(__file__).parent / "database" / "couplings.db"
engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
HP_TO_KW = 0.745699872
SERVICE_FACTOR = 1.5


class Base(DeclarativeBase):
    pass


class Coupling(Base):
    __tablename__ = "couplings"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    series: Mapped[str] = mapped_column(String)
    size: Mapped[int] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(String, unique=True)
    disc_pack_style: Mapped[str] = mapped_column(String)
    standard_balance: Mapped[str] = mapped_column(String)
    angular_misalignment: Mapped[str] = mapped_column(String)
    angular_misalignment_deg: Mapped[float] = mapped_column(Float)
    parallel_misalignment: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    axial_capacity_mm: Mapped[float] = mapped_column(Float)
    max_continuous_torque_nm: Mapped[float] = mapped_column(Float)
    peak_overload_torque_nm: Mapped[float] = mapped_column(Float)
    std_hub_max_bore_mm: Mapped[float] = mapped_column(Float)
    xl_hub_max_bore_mm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    xxl_hub_max_bore_mm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    min_dbse_mm: Mapped[float] = mapped_column(Float)
    max_dbse_mm: Mapped[float] = mapped_column(Float)
    max_speed_as_mfd_rpm: Mapped[float] = mapped_column(Float)
    max_speed_balanced_rpm: Mapped[float] = mapped_column(Float)
    weight_kg: Mapped[float] = mapped_column(Float)
    disc_pack_material: Mapped[str] = mapped_column(String)
    major_component_material: Mapped[str] = mapped_column(String)
    bolt_material: Mapped[str] = mapped_column(String)
    coating: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    temperature_rating: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    api_compliance: Mapped[str] = mapped_column(String)
    typical_applications: Mapped[str] = mapped_column(String)
    source_reference: Mapped[str] = mapped_column(String)

    @property
    def max_bore_available_mm(self) -> float:
        return max(b for b in (self.std_hub_max_bore_mm, self.xl_hub_max_bore_mm, self.xxl_hub_max_bore_mm) if b)


def angular_label(series: str, size: int) -> tuple[str, float]:
    """Angular misalignment per disc pack, per Catalog 2000M 'General' box for XTSR52/XTSR71."""
    if size in (494, 644):
        return "2/3° per disc pack", 2 / 3
    if size in (726, 826, 996):
        return "1/2° per disc pack", 0.5
    return "1/3° per disc pack", 1 / 3


# (size, max_cont_torque_Nm, std_bore_mm, min_C_mm, max_C_mm, max_rpm_as_mfd, max_rpm_balanced, axial_mm, weight_kg)
# Source: Catalog 2000M p.12 "XTSR52 Spacer Type Coupling - General Coupling Data"
XTSR52_DATA = [
    (494, 85, 27, 82, 163, 13800, 23000, 1.2, 0.88),
    (644, 145, 38, 82, 239, 12500, 21500, 1.7, 1.35),
    (726, 297, 45, 82, 373, 12000, 20000, 1.3, 1.77),
    (826, 554, 50, 88, 374, 10900, 18500, 1.5, 3.34),
    (996, 927, 60, 98, 781, 9800, 15000, 1.8, 4.78),
    (1088, 2190, 65, 103, 783, 9000, 14000, 1.3, 8.34),
    (1298, 3550, 80, 116, 788, 8000, 12000, 1.6, 13.6),
    (1548, 5910, 95, 128, 792, 7100, 10000, 1.8, 20.8),
    (1698, 8190, 105, 152, 794, 6600, 9100, 2.0, 29.0),
    (1928, 11100, 120, 160, 796, 6100, 8500, 2.3, 38.2),
    (2068, 15400, 130, 176, 799, 5800, 7800, 2.5, 49.9),
    (2278, 19900, 140, 213, 800, 5500, 7100, 2.7, 69.7),
    (2468, 26200, 150, 222, 803, 5200, 6500, 3.0, 87.3),
    (2698, 35900, 165, 238, 1114, 4800, 6000, 3.2, 111),
    (2888, 47000, 175, 270, 1117, 4600, 5700, 3.5, 150),
    (3058, 52000, 185, 270, 1117, 4400, 5400, 3.7, 172),
    (3358, 70200, 215, 302, 1121, 4200, 4700, 4.0, 232),
    (3668, 94300, 225, 321, 1128, 3900, 4400, 4.4, 329),
    (3908, 103000, 240, 321, 1128, 3800, 4100, 4.7, 381),
    (4178, 128000, 255, 343, 1132, 3600, 3900, 5.0, 468),
    (4588, 189000, 280, 498, 1037, 3400, 3600, 5.5, 661),
    (4918, 235000, 300, 518, 1041, 3200, 3300, 5.9, 817),
    (5258, 283000, 320, 540, 1046, 3100, 3100, 6.3, 991),
]

# (size, max_cont_torque_Nm, std_bore, xl_bore, xxl_bore, min_C_mm, max_C_mm, max_rpm_as_mfd, max_rpm_balanced, axial_mm, weight_kg)
# Source: Catalog 2000M p.15 "XTSR71 Spacer Type Coupling with Adapters - General Coupling Data"
XTSR71_DATA = [
    (494, 85, 28, 38, 42, 65, 162, 13800, 23000, 1.2, 1.6),
    (644, 145, 38, None, 52, 68, 266, 12500, 21500, 1.7, 2.5),
    (726, 297, 42, 52, 61, 65, 398, 12000, 20000, 1.3, 3.1),
    (826, 554, 52, 61, 76, 77, 404, 10900, 18500, 1.5, 5.0),
    (996, 927, 61, 76, 90, 92, 819, 9800, 15000, 1.8, 8.4),
    (1088, 2190, 76, 90, 105, 96, 821, 9000, 14000, 1.3, 12.5),
    (1298, 3550, 90, 105, 125, 115, 834, 8000, 12000, 1.6, 20.6),
    (1548, 5910, 105, 125, 135, 135, 846, 7100, 10000, 1.8, 34.6),
    (1698, 8190, 125, 135, 150, 151, 856, 6600, 9100, 2.0, 47.0),
    (1928, 11100, 135, 150, 155, 161, 861, 6100, 8500, 2.3, 62.7),
    (2068, 15400, 150, 155, 166, 187, 877, 5800, 7800, 2.5, 84.9),
    (2278, 19900, 155, 166, 200, 196, 881, 5500, 7100, 2.7, 110),
    (2468, 26200, 166, 200, 220, 209, 889, 5200, 6500, 3.0, 143),
    (2698, 35900, 200, 220, 235, 236, 1211, 4800, 6000, 3.2, 184),
    (2888, 47000, 220, 235, 260, 255, 1221, 4600, 5700, 3.5, 257),
    (3058, 52000, 235, 260, 285, 257, 1222, 4400, 5400, 3.7, 274),
    (3358, 70200, 260, 285, 310, 287, 1239, 4200, 4700, 4.0, 366),
    (3668, 94300, 285, 310, 330, 310, 1254, 3900, 4400, 4.4, 521),
    (3908, 103000, 310, 330, 360, 311, 1255, 3800, 4100, 4.7, 536),
    (4178, 128000, 330, 360, 400, 340, 1272, 3600, 3900, 5.0, 648),
    (4588, 189000, 360, 400, 430, 386, 1197, 3400, 3600, 5.5, 993),
    (4918, 235000, 400, 430, None, 408, 1209, 3200, 3300, 5.9, 1200),
    (5258, 283000, 430, None, None, 438, 1227, 3100, 3100, 6.3, 1420),
]

XTSR52_APPS = "Pumps and compressors (centrifugal, rotary, lobe and axial), speed increasers, fans, dynamometers."
XTSR71_APPS = "Pumps and compressors with popular shaft separation standards, blowers, fans, speed increasers."
XTSR52_API = "API 610, ISO 14691 compliant when specified; ATEX II 2GD c T6 certified."
XTSR71_API = "API 610 / ISO 14691 compliant as standard; API 671 (ISO 10441) compliant when specified; ATEX II 2GD c T6 certified."


def build_seed():
    rows = []
    for size, torque, bore, cmin, cmax, rpm_mfd, rpm_bal, axial, weight in XTSR52_DATA:
        label, deg = angular_label("XTSR52", size)
        rows.append(dict(
            series="XTSR52", size=size, name=f"XTSR52-{size}",
            disc_pack_style="Unitized XTSR", standard_balance="AGMA Class 9",
            angular_misalignment=label, angular_misalignment_deg=deg,
            parallel_misalignment=None, axial_capacity_mm=axial,
            max_continuous_torque_nm=torque, peak_overload_torque_nm=torque * 2,
            std_hub_max_bore_mm=bore, xl_hub_max_bore_mm=None, xxl_hub_max_bore_mm=None,
            min_dbse_mm=cmin, max_dbse_mm=cmax,
            max_speed_as_mfd_rpm=rpm_mfd, max_speed_balanced_rpm=rpm_bal, weight_kg=weight,
            disc_pack_material="Stainless steel", major_component_material="Carbon steel",
            bolt_material="Alloy steel", coating="Manganese phosphate (other coatings available on request)",
            temperature_rating=None, api_compliance=XTSR52_API, typical_applications=XTSR52_APPS,
            source_reference="Regal Rexnord Thomas Flexible Disc Couplings, Catalog 2000M, XTSR52 Spacer Type Coupling, pp. 11-13",
        ))
    for size, torque, bore, xl, xxl, cmin, cmax, rpm_mfd, rpm_bal, axial, weight in XTSR71_DATA:
        label, deg = angular_label("XTSR71", size)
        rows.append(dict(
            series="XTSR71", size=size, name=f"XTSR71-{size}",
            disc_pack_style="Unitized XTSR", standard_balance="AGMA Class 9",
            angular_misalignment=label, angular_misalignment_deg=deg,
            parallel_misalignment=None, axial_capacity_mm=axial,
            max_continuous_torque_nm=torque, peak_overload_torque_nm=torque * 2,
            std_hub_max_bore_mm=bore, xl_hub_max_bore_mm=xl, xxl_hub_max_bore_mm=xxl,
            min_dbse_mm=cmin, max_dbse_mm=cmax,
            max_speed_as_mfd_rpm=rpm_mfd, max_speed_balanced_rpm=rpm_bal, weight_kg=weight,
            disc_pack_material="Stainless steel", major_component_material="Carbon steel",
            bolt_material="Alloy steel", coating=None,
            temperature_rating=None, api_compliance=XTSR71_API, typical_applications=XTSR71_APPS,
            source_reference="Regal Rexnord Thomas Flexible Disc Couplings, Catalog 2000M, XTSR71 Spacer Type Coupling with Adapters, pp. 14-16",
        ))
    return rows


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def out(c: Coupling) -> dict:
    d = {k: getattr(c, k) for k in Coupling.__table__.columns.keys()}
    d["parallel_misalignment"] = c.parallel_misalignment or "Not specified in supplied manual"
    d["temperature_rating"] = c.temperature_rating or "Not specified in supplied manual"
    d["max_bore_available_mm"] = c.max_bore_available_mm
    return d


def seed():
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        if db.scalar(select(Coupling.id).limit(1)) is None:
            for row in build_seed():
                db.add(Coupling(**row))
            db.commit()


@asynccontextmanager
async def lifespan(_: FastAPI):
    seed()
    yield


app = FastAPI(title="Smart Coupling API", version="3.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"], allow_methods=["*"], allow_headers=["*"])


class TorqueInput(BaseModel):
    power: float = Field(gt=0)
    power_unit: Literal["kW", "HP"]
    speed: float = Field(gt=0)


def transmitted_torque_nm(power: float, power_unit: str, speed: float) -> float:
    kw = power if power_unit == "kW" else power * HP_TO_KW
    return 9550 * kw / speed


class Request(BaseModel):
    driver_shaft_mm: float = Field(gt=0)
    driven_shaft_mm: float = Field(gt=0)
    dbse_mm: float = Field(gt=0)
    power: float = Field(gt=0)
    power_unit: Literal["kW", "HP"]
    speed: float = Field(gt=0)
    # Operating conditions are all optional and never used to reject a candidate.
    temperature_c: Optional[float] = None
    hours_per_day: Optional[float] = Field(default=None, gt=0)
    service_life_years: Optional[float] = Field(default=None, gt=0)
    required_angular_misalignment_deg: Optional[float] = Field(default=None, ge=0)
    required_parallel_misalignment_mm: Optional[float] = Field(default=None, ge=0)
    shock_load: Optional[Literal["Light", "Medium", "Heavy"]] = None
    environment: Optional[str] = None
    budget: Optional[Literal["Low", "Medium", "High"]] = None
    precision: bool = False
    vibration_damping: bool = False
    soft_start: bool = False


class CompareInput(BaseModel):
    coupling_ids: list[int] = Field(min_length=2, max_length=2)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/couplings")
def couplings(db: Session = Depends(get_db)):
    return [out(c) for c in db.scalars(select(Coupling).order_by(Coupling.series, Coupling.size))]


@app.get("/couplings/{coupling_id}")
def coupling(coupling_id: int, db: Session = Depends(get_db)):
    c = db.get(Coupling, coupling_id)
    if not c:
        raise HTTPException(404, "Coupling not found")
    return out(c)


@app.post("/calculate-torque")
def torque(data: TorqueInput):
    t = transmitted_torque_nm(data.power, data.power_unit, data.speed)
    kw = data.power if data.power_unit == "kW" else data.power * HP_TO_KW
    return {"torque_nm": round(t, 2), "kw": round(kw, 3), "formula": "9550 × Power (kW) ÷ Speed (RPM)"}


@app.post("/compare")
def compare(data: CompareInput, db: Session = Depends(get_db)):
    items = [db.get(Coupling, i) for i in data.coupling_ids]
    if not all(items):
        raise HTTPException(404, "One or more couplings were not found")
    return [out(c) for c in items]


def check(c: Coupling, req: Request, required_torque: float):
    return {
        "torque": required_torque <= c.max_continuous_torque_nm,
        "driver_bore": req.driver_shaft_mm <= c.max_bore_available_mm,
        "driven_bore": req.driven_shaft_mm <= c.max_bore_available_mm,
        "dbse": c.min_dbse_mm <= req.dbse_mm <= c.max_dbse_mm,
        "speed": req.speed <= c.max_speed_as_mfd_rpm,
    }


@app.post("/recommend")
def recommend(req: Request, db: Session = Depends(get_db)):
    all_couplings = list(db.scalars(select(Coupling).order_by(Coupling.series, Coupling.size)))
    required_torque = transmitted_torque_nm(req.power, req.power_unit, req.speed) * SERVICE_FACTOR
    transmitted = required_torque / SERVICE_FACTOR

    evaluated = [(c, check(c, req, required_torque)) for c in all_couplings]
    candidates = [c for c, r in evaluated if all(r.values())]

    steps = [
        {"label": "Power → Speed → Transmitted Torque",
         "detail": f"{req.power} {req.power_unit} at {req.speed} RPM → {transmitted:.1f} N·m (Torque = 9550 × Power[kW] ÷ Speed[RPM])"},
        {"label": "Service Factor", "detail": f"Fixed service factor of {SERVICE_FACTOR} applied to transmitted torque."},
        {"label": "Required Torque", "detail": f"{transmitted:.1f} N·m × {SERVICE_FACTOR} = {required_torque:.1f} N·m required coupling rating."},
    ]

    if not candidates:
        diag = {
            "torque_pass": sum(1 for _, r in evaluated if r["torque"]),
            "bore_pass": sum(1 for _, r in evaluated if r["driver_bore"] and r["driven_bore"]),
            "dbse_pass": sum(1 for _, r in evaluated if r["dbse"]),
            "speed_pass": sum(1 for _, r in evaluated if r["speed"]),
            "total": len(evaluated),
        }
        largest_bore = max(c.max_bore_available_mm for c in all_couplings)
        largest_torque = max(c.max_continuous_torque_nm for c in all_couplings)
        max_dbse = max(c.max_dbse_mm for c in all_couplings)
        min_dbse_overall = min(c.min_dbse_mm for c in all_couplings)
        notes = []
        if diag["torque_pass"] == 0:
            notes.append(f"Required torque {required_torque:.0f} N·m exceeds the largest coupling in this library ({largest_torque:.0f} N·m, XTSR52/71-5258).")
        if diag["bore_pass"] == 0:
            notes.append(f"A shaft of {max(req.driver_shaft_mm, req.driven_shaft_mm)} mm exceeds the largest available bore in this library ({largest_bore} mm, XTSR71-5258 XXL hub).")
        if diag["dbse_pass"] == 0:
            notes.append(f"DBSE {req.dbse_mm} mm is outside every published Min C/Max C range in this library ({min_dbse_overall}-{max_dbse} mm).")
        if diag["speed_pass"] == 0:
            notes.append(f"Speed {req.speed} RPM exceeds the Max RPM (As Manufactured) rating of every coupling in this library.")
        return {
            "feasible": False,
            "transmitted_torque_nm": round(transmitted, 1),
            "required_torque_nm": round(required_torque, 1),
            "service_factor": SERVICE_FACTOR,
            "selection_steps": steps,
            "diagnostics": diag,
            "reasoning": notes or ["No coupling in the currently loaded manual data (XTSR52/XTSR71 series) satisfies all constraints simultaneously."],
            "recommendation": None,
            "alternatives": [],
        }

    candidates.sort(key=lambda c: c.weight_kg)
    winner = candidates[0]
    alternatives = candidates[1:4]

    steps += [
        {"label": "Torque Capacity Check", "detail": f"{winner.name}: rated {winner.max_continuous_torque_nm:.0f} N·m continuous ≥ {required_torque:.1f} N·m required → PASS"},
        {"label": "Shaft / Bore Check", "detail": f"Driver {req.driver_shaft_mm} mm and driven {req.driven_shaft_mm} mm ≤ max available bore {winner.max_bore_available_mm:.0f} mm → PASS"},
        {"label": "DBSE Check", "detail": f"DBSE {req.dbse_mm} mm within published range {winner.min_dbse_mm:.0f}-{winner.max_dbse_mm:.0f} mm → PASS"},
        {"label": "Speed Check", "detail": f"{req.speed} RPM ≤ Max RPM As Manufactured {winner.max_speed_as_mfd_rpm:.0f} → PASS"},
    ]

    reasoning = [
        f"{winner.name} torque capacity ({winner.max_continuous_torque_nm:.0f} N·m) meets the {SERVICE_FACTOR}× service-factor-adjusted requirement of {required_torque:.1f} N·m.",
        f"Both driver ({req.driver_shaft_mm} mm) and driven ({req.driven_shaft_mm} mm) shafts fit within the {winner.max_bore_available_mm:.0f} mm maximum bore published for this size.",
        f"Requested DBSE of {req.dbse_mm} mm falls within the manual's published Min C / Max C range ({winner.min_dbse_mm:.0f}-{winner.max_dbse_mm:.0f} mm) for {winner.name}.",
        f"Selected as the lightest ({winner.weight_kg} kg) of {len(candidates)} coupling(s) in the library that satisfy every hard constraint.",
    ]

    optional_notes = []
    if req.temperature_c is not None:
        optional_notes.append(f"Temperature requirement ({req.temperature_c}°C) → Not specified in supplied manual for the {winner.series} series; no coupling series in the currently loaded catalog data publishes a temperature rating applicable here.")
    if req.required_angular_misalignment_deg is not None:
        satisfied = req.required_angular_misalignment_deg <= winner.angular_misalignment_deg
        optional_notes.append(f"Angular misalignment requirement: {req.required_angular_misalignment_deg}° vs. allowable {winner.angular_misalignment} → {'meets' if satisfied else 'EXCEEDS'} the manual-rated capacity.")
    if req.required_parallel_misalignment_mm is not None:
        optional_notes.append(f"Parallel misalignment requirement: {req.required_parallel_misalignment_mm} mm vs. allowable: Not specified in supplied manual for {winner.series} (only angular misalignment per disc pack is published for this series).")
    for label, val in (("Shock load", req.shock_load), ("Environment", req.environment), ("Budget", req.budget)):
        if val:
            optional_notes.append(f"{label} ({val}) noted, but the supplied manual does not publish a per-coupling rating for this attribute in the XTSR52/XTSR71 series, so it was not used to filter or score candidates.")
    for label, flag in (("High precision", req.precision), ("Vibration damping", req.vibration_damping), ("Soft starting", req.soft_start)):
        if flag:
            optional_notes.append(f"{label} was requested, but the supplied manual does not differentiate XTSR52/XTSR71 sizes on this attribute, so it did not affect the selection.")

    steps.append({"label": "Optional Operating-Condition Checks", "detail": "; ".join(optional_notes) if optional_notes else "None provided — recommendation based on mechanical/dimensional requirements only."})
    steps.append({"label": "Final Recommendation", "detail": f"{winner.name} selected."})

    misalignment_comparison = {
        "angular": {
            "required_deg": req.required_angular_misalignment_deg,
            "allowable": winner.angular_misalignment,
            "allowable_deg": winner.angular_misalignment_deg,
            "satisfied": (req.required_angular_misalignment_deg <= winner.angular_misalignment_deg) if req.required_angular_misalignment_deg is not None else None,
        },
        "parallel": {
            "required_mm": req.required_parallel_misalignment_mm,
            "allowable": "Not specified in supplied manual",
            "satisfied": None,
        },
        "axial": {"allowable_mm": winner.axial_capacity_mm},
    }

    return {
        "feasible": True,
        "transmitted_torque_nm": round(transmitted, 1),
        "required_torque_nm": round(required_torque, 1),
        "service_factor": SERVICE_FACTOR,
        "recommendation": out(winner),
        "selection_steps": steps,
        "reasoning": reasoning + optional_notes,
        "misalignment_comparison": misalignment_comparison,
        "alternatives": [out(c) for c in alternatives],
    }
