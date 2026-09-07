"""Smart Coupling Selection & Recommendation Tool API - Phase 2.

Selection is grounded entirely in the Regal Rexnord Thomas Flexible Disc Coupling catalogs
(see catalog_data.py for the transcribed source tables and their provenance). This module
contains ONLY the selection engine and API surface; no catalog values are hardcoded here.

Core rules (approved Phase 2 spec):
  1. kW power -> required torque is checked against the METRIC (2000M) catalog's
     Max. Continuous Torque (N*m).
  2. HP power -> required torque is checked against the IMPERIAL (Catalog 2000) catalog's
     Max. Continuous Torque (lb*in). Torque is computed natively per unit (9550*kW/RPM or
     63025*HP/RPM), never by converting HP to kW first.
  3. Required torque = transmitted torque * a FIXED 1.5 service factor.
  4. The candidate with the SMALLEST catalog torque rating >= required torque wins (not the
     lightest, not the first found) - "next higher torque" rule.
  5. Driver shaft, driven shaft and DBSE units are independently mm/in.
  6. Power unit and dimensional units are completely independent of each other.
  7. coupling_type ("spacer" | "closed_coupled") is a hard filter applied BEFORE any
     engineering check - never a tie-break or a post-hoc classification.
  8. For "spacer", XTSR52, XTSR71 and the legacy SERIES71 are all considered. XTSR71 and
     SERIES71 are distinct catalog products (different size numbering, never merged); if
     both have a size that qualifies at the same minimum sufficient torque, both are
     returned as valid recommendations rather than one being silently dropped.
  9. DBSE must fall inside the catalog's continuous Min C-Max C range where published.
     SERIES71 does not publish a Max C - Std C is used as a conservative reference ceiling
     and is flagged as such, never presented as an official catalog maximum.
  10. Misalignment limits are read directly from catalog data; only angular is published for
      the products in scope, so parallel is reported "not specified" rather than guessed.
  11. No catalog in this project publishes a sub-zero / heat-treated-alloy-steel rating for
      any product in scope. A requirement of temperature < -45C is therefore a hard
      constraint that NO candidate can satisfy, and must return NO_VALID_RECOMMENDATION with
      that explanation - never an assumed Series 71 / XTSR71 exception.
  12. Nothing is invented: every displayed figure traces to a catalog field, or is reported
      as "Not specified in supplied manual".
"""
import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Literal, Optional
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, model_validator
from sqlalchemy import JSON, Boolean, Float, Integer, String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

import catalog_data

# Production (Render) sets DATABASE_URL to the Supabase Postgres connection string.
# Local development leaves it unset and falls back to the bundled SQLite database, so
# nothing about local dev changes. Supabase/most providers hand out a bare
# "postgresql://" (or legacy "postgres://") URL; SQLAlchemy needs the driver named
# explicitly, so it's rewritten to use the psycopg 3 dialect actually installed below.
_database_url = os.environ.get("DATABASE_URL")
if _database_url:
    if _database_url.startswith("postgres://"):
        _database_url = _database_url.replace("postgres://", "postgresql+psycopg://", 1)
    elif _database_url.startswith("postgresql://"):
        _database_url = _database_url.replace("postgresql://", "postgresql+psycopg://", 1)
    engine = create_engine(_database_url)
else:
    DB_PATH = Path(__file__).parent / "database" / "couplings.db"
    engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

IN_TO_MM = 25.4
SERVICE_FACTOR = 1.5
NOT_SPECIFIED = "Not specified in supplied manual"
LOW_TEMP_THRESHOLD_C = -45


class Base(DeclarativeBase):
    pass


class Coupling(Base):
    __tablename__ = "couplings"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product: Mapped[str] = mapped_column(String)
    coupling_type: Mapped[str] = mapped_column(String)
    size: Mapped[str] = mapped_column(String)
    name: Mapped[str] = mapped_column(String, unique=True)
    disc_pack_style: Mapped[str] = mapped_column(String)
    standard_balance: Mapped[str] = mapped_column(String)
    angular_misalignment_label: Mapped[str] = mapped_column(String)
    angular_misalignment_deg: Mapped[float] = mapped_column(Float)
    parallel_misalignment: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    bore_options: Mapped[list] = mapped_column(JSON)
    min_dbse_mm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    max_dbse_mm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    min_dbse_in: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    max_dbse_in: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    dbse_max_documented: Mapped[bool] = mapped_column(Boolean, default=False)
    dbse_is_variable: Mapped[bool] = mapped_column(Boolean, default=True)
    fixed_c_mm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    fixed_c_in: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    max_continuous_torque_nm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    max_continuous_torque_lbin: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    peak_overload_torque_nm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    peak_overload_torque_lbin: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    max_speed_as_mfd_rpm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    max_speed_balanced_rpm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    axial_capacity_mm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    axial_capacity_in: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    weight_kg: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    weight_lb: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    disc_pack_material: Mapped[str] = mapped_column(String)
    major_component_material: Mapped[str] = mapped_column(String)
    bolt_material: Mapped[str] = mapped_column(String)
    coating: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    temperature_rating: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    api_compliance: Mapped[str] = mapped_column(String)
    typical_applications: Mapped[str] = mapped_column(String)
    source_reference_metric: Mapped[str] = mapped_column(String)
    source_reference_imperial: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    imperial_not_published: Mapped[bool] = mapped_column(Boolean, default=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def seed():
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        if db.scalar(select(Coupling.id).limit(1)) is None:
            for row in catalog_data.build_rows():
                db.add(Coupling(**row))
            db.commit()


@asynccontextmanager
async def lifespan(_: FastAPI):
    seed()
    yield


app = FastAPI(title="Smart Coupling API", version="4.0.0", lifespan=lifespan)

# Local dev origin is always allowed so the deployed backend can still be exercised from
# a local frontend during testing. Production (Render) additionally allows FRONTEND_URL,
# the deployed Vercel domain, set via environment variable rather than hardcoded.
_allowed_origins = ["http://localhost:5173"]
_frontend_url = os.environ.get("FRONTEND_URL")
if _frontend_url and _frontend_url not in _allowed_origins:
    _allowed_origins.append(_frontend_url)
app.add_middleware(CORSMiddleware, allow_origins=_allowed_origins, allow_methods=["*"], allow_headers=["*"])


# ---------------------------------------------------------------------------
# Unit helpers
# ---------------------------------------------------------------------------
def convert_length(value: float, from_unit: str, to_unit: str) -> float:
    if from_unit == to_unit:
        return value
    return value * IN_TO_MM if from_unit == "in" else value / IN_TO_MM


def native_unit_for(power_unit: str) -> str:
    """The dimensional unit system whose catalog is authoritative for the chosen power unit."""
    return "mm" if power_unit == "kW" else "in"


def transmitted_torque(power: float, power_unit: str, speed: float) -> tuple[float, str]:
    if power_unit == "kW":
        return 9550 * power / speed, "N·m"
    return 63025 * power / speed, "lb·in"


def out_coupling(c: Coupling) -> dict:
    return {
        "id": c.id, "product": c.product, "coupling_type": c.coupling_type, "size": c.size, "name": c.name,
        "disc_pack_style": c.disc_pack_style, "standard_balance": c.standard_balance,
        "angular_misalignment_label": c.angular_misalignment_label, "angular_misalignment_deg": c.angular_misalignment_deg,
        "parallel_misalignment": c.parallel_misalignment or NOT_SPECIFIED,
        "bore_options": c.bore_options,
        "min_dbse_mm": c.min_dbse_mm, "max_dbse_mm": c.max_dbse_mm,
        "min_dbse_in": c.min_dbse_in, "max_dbse_in": c.max_dbse_in,
        "dbse_max_documented": c.dbse_max_documented, "dbse_is_variable": c.dbse_is_variable,
        "max_continuous_torque_nm": c.max_continuous_torque_nm, "max_continuous_torque_lbin": c.max_continuous_torque_lbin,
        "peak_overload_torque_nm": c.peak_overload_torque_nm, "peak_overload_torque_lbin": c.peak_overload_torque_lbin,
        "max_speed_as_mfd_rpm": c.max_speed_as_mfd_rpm, "max_speed_balanced_rpm": c.max_speed_balanced_rpm,
        "axial_capacity_mm": c.axial_capacity_mm, "axial_capacity_in": c.axial_capacity_in,
        "weight_kg": c.weight_kg, "weight_lb": c.weight_lb,
        "disc_pack_material": c.disc_pack_material, "major_component_material": c.major_component_material,
        "bolt_material": c.bolt_material, "coating": c.coating or NOT_SPECIFIED,
        "temperature_rating": c.temperature_rating or NOT_SPECIFIED,
        "api_compliance": c.api_compliance, "typical_applications": c.typical_applications,
        "source_reference_metric": c.source_reference_metric,
        "source_reference_imperial": c.source_reference_imperial or NOT_SPECIFIED,
        "imperial_not_published": c.imperial_not_published,
    }


class TorqueInput(BaseModel):
    power: float = Field(gt=0)
    power_unit: Literal["kW", "HP"]
    speed: float = Field(gt=0)


@app.post("/calculate-torque")
def torque(data: TorqueInput):
    value, unit = transmitted_torque(data.power, data.power_unit, data.speed)
    return {"torque": round(value, 2), "unit": unit,
            "formula": "9550 × Power(kW) ÷ Speed(RPM)" if data.power_unit == "kW" else "63025 × Power(HP) ÷ Speed(RPM)"}


class Request(BaseModel):
    coupling_type: Literal["spacer", "closed_coupled"]
    driver_shaft: float = Field(gt=0)
    driver_shaft_unit: Literal["mm", "in"]
    driven_shaft: float = Field(gt=0)
    driven_shaft_unit: Literal["mm", "in"]
    dbse: Optional[float] = Field(default=None, gt=0)
    dbse_unit: Optional[Literal["mm", "in"]] = None
    power: float = Field(gt=0)
    power_unit: Literal["kW", "HP"]
    speed: float = Field(gt=0)
    # Operating conditions are optional. Only the sub -45C temperature case is a hard
    # constraint (Part I); everything else here is reported for context only, per what the
    # supplied catalogs do and do not publish for the products in scope.
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

    @model_validator(mode="after")
    def _dbse_required_for_spacer(self):
        if self.coupling_type == "spacer":
            if self.dbse is None or self.dbse_unit is None:
                raise ValueError("dbse and dbse_unit are required when coupling_type is 'spacer'")
        return self


class CompareInput(BaseModel):
    coupling_ids: list[int] = Field(min_length=2, max_length=2)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/couplings")
def couplings(db: Session = Depends(get_db)):
    return [out_coupling(c) for c in db.scalars(select(Coupling).order_by(Coupling.coupling_type, Coupling.product, Coupling.id))]


@app.get("/couplings/{coupling_id}")
def coupling(coupling_id: int, db: Session = Depends(get_db)):
    c = db.get(Coupling, coupling_id)
    if not c:
        raise HTTPException(404, "Coupling not found")
    return out_coupling(c)


@app.post("/compare")
def compare(data: CompareInput, db: Session = Depends(get_db)):
    items = [db.get(Coupling, i) for i in data.coupling_ids]
    if not all(items):
        raise HTTPException(404, "One or more couplings were not found")
    return [out_coupling(c) for c in items]


# ---------------------------------------------------------------------------
# Selection engine
# ---------------------------------------------------------------------------
def best_bore_mm_or_in(c: Coupling, native_unit: str) -> Optional[float]:
    key = "max_bore_mm" if native_unit == "mm" else "max_bore_in"
    values = [o.get(key) for o in c.bore_options if o.get(key) is not None]
    return max(values) if values else None


def hub_satisfies(c: Coupling, native_unit: str, required: float) -> bool:
    """Hub-level check: does ANY documented hub configuration for this coupling SIZE
    accommodate `required`? This is the "exhaust every hub configuration before rejecting
    the size" rule - a size is only bore-rejected when every one of its catalog-documented
    hub options (Std/XL/XXL for XTSR71, B & B1/B2 for Series 71, Internal/External for
    close-coupled, or the single Max Bore for XTSR52) fails independently."""
    key = "max_bore_mm" if native_unit == "mm" else "max_bore_in"
    return any(o.get(key) is not None and o[key] >= required for o in c.bore_options)


def smallest_sufficient_bore_option(c: Coupling, native_unit: str, required: float) -> Optional[dict]:
    """The smallest hub configuration (by published bore) that accommodates `required`,
    checked independently per shaft side - driver and driven each pick their own smallest
    sufficient hub, exactly as the catalog's own worked examples do (e.g. a 1088 XTSR71
    ordered with a Std hub on one side and an XXL hub on the other)."""
    key = "max_bore_mm" if native_unit == "mm" else "max_bore_in"
    fitting = [o for o in c.bore_options if o.get(key) is not None and o[key] >= required]
    if not fitting:
        return None
    return min(fitting, key=lambda o: o[key])


def overall_hub_label(c: Coupling, native_unit: str, driver_hub: Optional[dict], driven_hub: Optional[dict]) -> str:
    """Single headline hub-configuration name for a winning candidate, per the catalog's own
    naming convention (e.g. 'coupling is a 1088 XTSR71 XXL' when only one side needed the
    largest tier) - named after whichever side's hub has the larger published bore. Falls
    back to the lone hub's name for single-hub-option products like XTSR52."""
    if len(c.bore_options) <= 1:
        return c.bore_options[0]["label"] if c.bore_options else NOT_SPECIFIED
    if driver_hub is None or driven_hub is None:
        return NOT_SPECIFIED
    if driver_hub["label"] == driven_hub["label"]:
        return driver_hub["label"]
    key = "max_bore_mm" if native_unit == "mm" else "max_bore_in"
    larger = driver_hub if driver_hub[key] >= driven_hub[key] else driven_hub
    return f"{larger['label']} (driver: {driver_hub['label']}, driven: {driven_hub['label']})"


def torque_rating(c: Coupling, native_unit: str) -> Optional[float]:
    return c.max_continuous_torque_nm if native_unit == "mm" else c.max_continuous_torque_lbin


def check_candidate(c: Coupling, req: Request, required_torque: float, native_unit: str,
                     driver_native: float, driven_native: float, dbse_native: Optional[float]) -> dict:
    rating = torque_rating(c, native_unit)
    result = {
        "torque": rating is not None and rating >= required_torque,
        # Hub-level check: a size is only bore-rejected once EVERY documented hub
        # configuration for it fails - never just its smallest/default hub. Driver and
        # driven are each checked against the full set of hub options independently, since
        # the catalog allows ordering a different hub tier per side (see overall_hub_label).
        "driver_bore": hub_satisfies(c, native_unit, driver_native),
        "driven_bore": hub_satisfies(c, native_unit, driven_native),
        "speed": c.max_speed_as_mfd_rpm is not None and req.speed <= c.max_speed_as_mfd_rpm,
        "temperature": True,
    }
    if c.coupling_type == "spacer":
        min_dbse = c.min_dbse_mm if native_unit == "mm" else c.min_dbse_in
        max_dbse = c.max_dbse_mm if native_unit == "mm" else c.max_dbse_in
        result["dbse"] = (min_dbse is not None and max_dbse is not None and dbse_native is not None
                           and min_dbse <= dbse_native <= max_dbse)
    else:
        result["dbse"] = True  # closed-coupled: no user-adjustable DBSE in this catalog data
    if req.temperature_c is not None and req.temperature_c < LOW_TEMP_THRESHOLD_C:
        result["temperature"] = False  # no catalog in this project supports sub -45C service for any product in scope
    return result


def qualification_notes(c: Coupling, req: Request, required_torque: float, native_unit: str, torque_unit_label: str,
                         driver_native: float, driven_native: float, dbse_native: Optional[float]) -> list[str]:
    rating = torque_rating(c, native_unit)
    dim_unit = native_unit
    driver_hub = smallest_sufficient_bore_option(c, native_unit, driver_native)
    driven_hub = smallest_sufficient_bore_option(c, native_unit, driven_native)
    key = "max_bore_mm" if native_unit == "mm" else "max_bore_in"
    notes = [f"{c.name} rated {rating:,.0f} {torque_unit_label} continuous ≥ {required_torque:,.1f} {torque_unit_label} required."]
    if len(c.bore_options) > 1:
        tried = ", ".join(f"{o['label']} ({o.get(key):.2f} {dim_unit})" if o.get(key) is not None else f"{o['label']} (not published)" for o in c.bore_options)
        notes.append(f"Hub configurations evaluated for size {c.size} before considering a larger coupling size: {tried}.")
    notes.append(f"Driver ({driver_native:.2f} {dim_unit}) fits the {driver_hub['label']} configuration "
                 f"({driver_hub[key]:.2f} {dim_unit} max) and driven ({driven_native:.2f} {dim_unit}) fits the "
                 f"{driven_hub['label']} configuration ({driven_hub[key]:.2f} {dim_unit} max) for this coupling size.")
    if c.coupling_type == "spacer" and dbse_native is not None:
        min_dbse = c.min_dbse_mm if native_unit == "mm" else c.min_dbse_in
        max_dbse = c.max_dbse_mm if native_unit == "mm" else c.max_dbse_in
        ceiling_note = "" if c.dbse_max_documented else " (Std. C used as a reference ceiling - the catalog does not publish a Max. C for this product)"
        notes.append(f"Requested DBSE {dbse_native:.2f} {dim_unit} falls within the published range "
                      f"{min_dbse:.2f}–{max_dbse:.2f} {dim_unit}{ceiling_note}.")
    if c.max_speed_as_mfd_rpm is not None:
        notes.append(f"Operating speed {req.speed:.0f} RPM ≤ Max. Speed (As Manufactured) {c.max_speed_as_mfd_rpm:,.0f} RPM.")
    return notes


def rejection_reason(c: Coupling, checks: dict, native_unit: str, torque_unit_label: str, required_torque: float) -> str:
    rating = torque_rating(c, native_unit)
    if not checks["torque"]:
        if rating is None:
            return f"{c.name}: continuous torque rating is not published in the {'Imperial' if native_unit == 'in' else 'Metric'} catalog for this size."
        return f"{c.name}: rated {rating:,.0f} {torque_unit_label} continuous < {required_torque:,.1f} {torque_unit_label} required."
    if not checks["driver_bore"] or not checks["driven_bore"]:
        key = "max_bore_mm" if native_unit == "mm" else "max_bore_in"
        tried = ", ".join(f"{o['label']} ({o.get(key):.2f} {native_unit})" if o.get(key) is not None else f"{o['label']} (not published)" for o in c.bore_options)
        side = "driver and driven shafts" if (not checks["driver_bore"] and not checks["driven_bore"]) else ("driver shaft" if not checks["driver_bore"] else "driven shaft")
        return f"{c.name}: every documented hub configuration for this size was checked ({tried}) and none accommodates the requested {side}."
    if not checks["dbse"]:
        min_dbse = c.min_dbse_mm if native_unit == "mm" else c.min_dbse_in
        max_dbse = c.max_dbse_mm if native_unit == "mm" else c.max_dbse_in
        if min_dbse is None:
            return f"{c.name}: no DBSE range published for this size."
        return f"{c.name}: requested DBSE is outside the published range {min_dbse:.2f}–{max_dbse:.2f} {native_unit}."
    if not checks["speed"]:
        return f"{c.name}: requested speed exceeds the published Max. Speed (As Manufactured)."
    if not checks["temperature"]:
        return (f"{c.name}: a temperature below {LOW_TEMP_THRESHOLD_C}°C was requested, but no coupling in the supplied "
                f"Regal Rexnord Thomas catalogs (metric or imperial) publishes a low-temperature or heat-treated-alloy-steel "
                f"rating for any product in scope - this is not supported, not assumed.")
    return f"{c.name}: does not satisfy all mandatory constraints."


@app.post("/recommend")
def recommend(req: Request, db: Session = Depends(get_db)):
    native_unit = native_unit_for(req.power_unit)
    torque_unit_label = "N·m" if native_unit == "mm" else "lb·in"
    transmitted, _ = transmitted_torque(req.power, req.power_unit, req.speed)
    required_torque = transmitted * SERVICE_FACTOR

    driver_native = convert_length(req.driver_shaft, req.driver_shaft_unit, native_unit)
    driven_native = convert_length(req.driven_shaft, req.driven_shaft_unit, native_unit)
    dbse_native = convert_length(req.dbse, req.dbse_unit, native_unit) if req.dbse is not None else None

    pool = list(db.scalars(select(Coupling).where(Coupling.coupling_type == req.coupling_type).order_by(Coupling.product, Coupling.id)))
    evaluated = [(c, check_candidate(c, req, required_torque, native_unit, driver_native, driven_native, dbse_native)) for c in pool]
    candidates = [c for c, r in evaluated if all(r.values())]

    steps = [
        {"label": "Power → Speed → Transmitted Torque",
         "detail": f"{req.power} {req.power_unit} at {req.speed} RPM → {transmitted:,.1f} {torque_unit_label} "
                   f"({'9550 × Power[kW] ÷ Speed[RPM]' if req.power_unit == 'kW' else '63025 × Power[HP] ÷ Speed[RPM]'})"},
        {"label": "Service Factor", "detail": f"Fixed service factor of {SERVICE_FACTOR} applied to transmitted torque (not user-adjustable)."},
        {"label": "Required Torque", "detail": f"{transmitted:,.1f} × {SERVICE_FACTOR} = {required_torque:,.1f} {torque_unit_label} required coupling rating."},
        {"label": "Torque Catalog", "detail": f"{'Catalog 2000M (Metric)' if native_unit == 'mm' else 'Catalog 2000 (Imperial)'} "
                                               f"Maximum Continuous Torque is authoritative for a {req.power_unit} power input."},
        {"label": "Coupling Type Filter", "detail": f"Restricted to catalog products documented as \"{req.coupling_type.replace('_', '-')}\" "
                                                      f"before any engineering check was applied ({len(pool)} candidate sizes considered)."},
    ]

    diag = {
        "torque_pass": sum(1 for _, r in evaluated if r["torque"]),
        "bore_pass": sum(1 for _, r in evaluated if r["driver_bore"] and r["driven_bore"]),
        "dbse_pass": sum(1 for _, r in evaluated if r["dbse"]),
        "speed_pass": sum(1 for _, r in evaluated if r["speed"]),
        "temperature_pass": sum(1 for _, r in evaluated if r["temperature"]),
        "total": len(evaluated),
    }

    # Per-product summary: which product families in this pool had at least one qualifying size.
    products_in_pool = sorted({c.product for c in pool})
    product_summary = []
    for prod in products_in_pool:
        prod_rows = [(c, r) for c, r in evaluated if c.product == prod]
        prod_candidates = [c for c, r in prod_rows if all(r.values())]
        if prod_candidates:
            best = min(prod_candidates, key=lambda c: torque_rating(c, native_unit))
            product_summary.append({"product": prod, "status": "valid", "best_size": best.name, "reason": None})
        else:
            # Report why the largest (best-attempt) candidate for this product failed.
            closest = min(prod_rows, key=lambda cr: (torque_rating(cr[0], native_unit) is None, -(torque_rating(cr[0], native_unit) or 0)))
            product_summary.append({"product": prod, "status": "rejected",
                                     "best_size": None,
                                     "reason": rejection_reason(closest[0], closest[1], native_unit, torque_unit_label, required_torque)})

    if not candidates:
        notes = []
        if diag["temperature_pass"] == 0:
            notes.append(f"A temperature below {LOW_TEMP_THRESHOLD_C}°C was requested. No coupling in the supplied Regal Rexnord "
                          f"Thomas catalogs (metric or imperial) publishes a low-temperature or heat-treated-alloy-steel rating for any "
                          f"{req.coupling_type.replace('_', '-')} product in scope, so this cannot be satisfied.")
        if diag["torque_pass"] == 0:
            notes.append(f"Required torque {required_torque:,.0f} {torque_unit_label} exceeds every {req.coupling_type.replace('_', '-')} "
                         f"coupling currently loaded for the {'Metric' if native_unit == 'mm' else 'Imperial'} catalog.")
        if diag["bore_pass"] == 0:
            notes.append("The requested driver/driven shaft diameter exceeds the largest published bore for every candidate in this pool.")
        if diag["dbse_pass"] == 0 and req.coupling_type == "spacer":
            notes.append("The requested DBSE falls outside every published Min C–Max C (or Std. C reference) range in this pool.")
        if diag["speed_pass"] == 0:
            notes.append("The requested speed exceeds the published Max. Speed (As Manufactured) for every candidate in this pool.")
        return {
            "feasible": False, "coupling_type": req.coupling_type,
            "torque_catalog": "Catalog 2000M (Metric)" if native_unit == "mm" else "Catalog 2000 (Imperial)",
            "transmitted_torque": {"value": round(transmitted, 1), "unit": torque_unit_label},
            "required_torque": {"value": round(required_torque, 1), "unit": torque_unit_label},
            "service_factor": SERVICE_FACTOR,
            "selection_steps": steps, "diagnostics": diag, "product_summary": product_summary,
            "reasoning": notes or ["No coupling in the currently loaded catalog data satisfies all constraints simultaneously."],
            "valid_recommendations": [], "alternatives": [],
        }

    min_torque = min(torque_rating(c, native_unit) for c in candidates)
    winners = sorted([c for c in candidates if torque_rating(c, native_unit) == min_torque],
                      key=lambda c: (c.weight_kg if c.weight_kg is not None else float("inf")))
    remaining = sorted([c for c in candidates if c not in winners], key=lambda c: torque_rating(c, native_unit))[:4]

    steps.append({"label": "Next-Higher-Torque Selection",
                  "detail": f"Smallest catalog rating ≥ {required_torque:,.1f} {torque_unit_label} is {min_torque:,.0f} {torque_unit_label}, "
                            f"met by {', '.join(c.name for c in winners)}."})
    if len(winners) > 1:
        steps.append({"label": "Cross-Product Tie", "detail": f"{len(winners)} distinct catalog products ({', '.join(sorted({c.product for c in winners}))}) "
                                                                 f"qualify at the identical minimum sufficient torque rating - all are returned rather than "
                                                                 f"arbitrarily eliminating one."})

    valid_recommendations = []
    for c in winners:
        checks = check_candidate(c, req, required_torque, native_unit, driver_native, driven_native, dbse_native)
        notes = qualification_notes(c, req, required_torque, native_unit, torque_unit_label, driver_native, driven_native, dbse_native)
        if len(c.bore_options) > 1:
            steps.append({"label": f"Hub Configuration Check - {c.name}",
                          "detail": f"{c.name} was NOT rejected for a larger coupling size merely because its smallest hub "
                                    f"might not fit - all {len(c.bore_options)} documented hub configurations "
                                    f"({', '.join(o['label'] for o in c.bore_options)}) were checked before concluding this size works."})
        driver_hub = smallest_sufficient_bore_option(c, native_unit, driver_native)
        driven_hub = smallest_sufficient_bore_option(c, native_unit, driven_native)
        entry = out_coupling(c)
        entry["qualifies_because"] = notes
        entry["hub_configuration"] = overall_hub_label(c, native_unit, driver_hub, driven_hub)
        entry["driver_bore_configuration"] = driver_hub
        entry["driven_bore_configuration"] = driven_hub
        optional_notes = []
        if req.temperature_c is not None:
            optional_notes.append(f"Temperature requirement ({req.temperature_c}°C) → {NOT_SPECIFIED} for {c.product}; "
                                   f"no product in scope publishes a temperature rating applicable here.")
        if req.required_angular_misalignment_deg is not None:
            satisfied = req.required_angular_misalignment_deg <= c.angular_misalignment_deg
            optional_notes.append(f"Angular misalignment requirement: {req.required_angular_misalignment_deg}° vs. allowable "
                                   f"{c.angular_misalignment_label} → {'meets' if satisfied else 'EXCEEDS'} the manual-rated capacity.")
        if req.required_parallel_misalignment_mm is not None:
            optional_notes.append(f"Parallel misalignment requirement: {req.required_parallel_misalignment_mm} mm vs. allowable: "
                                   f"{NOT_SPECIFIED} for {c.product} (only angular misalignment per disc pack is published).")
        for label, val in (("Shock load", req.shock_load), ("Environment", req.environment), ("Budget", req.budget)):
            if val:
                optional_notes.append(f"{label} ({val}) noted, but not used to filter or score candidates - not a catalog-published rating for this attribute.")
        entry["optional_condition_notes"] = optional_notes
        entry["misalignment_comparison"] = {
            "angular": {
                "required_deg": req.required_angular_misalignment_deg,
                "allowable_label": c.angular_misalignment_label, "allowable_deg": c.angular_misalignment_deg,
                "satisfied": (req.required_angular_misalignment_deg <= c.angular_misalignment_deg) if req.required_angular_misalignment_deg is not None else None,
            },
            "parallel": {"required_mm": req.required_parallel_misalignment_mm, "allowable": NOT_SPECIFIED, "satisfied": None},
            "axial": {"allowable_mm": c.axial_capacity_mm, "allowable_in": c.axial_capacity_in},
        }
        valid_recommendations.append(entry)

    steps.append({"label": "Final Recommendation(s)", "detail": ", ".join(c.name for c in winners) + " selected."})

    return {
        "feasible": True, "coupling_type": req.coupling_type,
        "torque_catalog": "Catalog 2000M (Metric)" if native_unit == "mm" else "Catalog 2000 (Imperial)",
        "transmitted_torque": {"value": round(transmitted, 1), "unit": torque_unit_label},
        "required_torque": {"value": round(required_torque, 1), "unit": torque_unit_label},
        "service_factor": SERVICE_FACTOR,
        "valid_recommendations": valid_recommendations,
        "alternatives": [out_coupling(c) for c in remaining],
        "product_summary": product_summary,
        "selection_steps": steps,
        "reasoning": [f"{len(winners)} candidate(s) share the minimum sufficient torque rating of {min_torque:,.0f} {torque_unit_label}."] +
                     (["Distinct catalog products at that rating are all shown per instruction - none eliminated by weight."] if len(winners) > 1 else []),
    }
