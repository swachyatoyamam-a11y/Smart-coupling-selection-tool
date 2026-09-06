export interface Coupling { id:number; series:'XTSR52'|'XTSR71'; size:number; name:string; disc_pack_style:string; standard_balance:string; angular_misalignment:string; angular_misalignment_deg:number; parallel_misalignment:string; axial_capacity_mm:number; max_continuous_torque_nm:number; peak_overload_torque_nm:number; std_hub_max_bore_mm:number; xl_hub_max_bore_mm:number|null; xxl_hub_max_bore_mm:number|null; max_bore_available_mm:number; min_dbse_mm:number; max_dbse_mm:number; max_speed_as_mfd_rpm:number; max_speed_balanced_rpm:number; weight_kg:number; disc_pack_material:string; major_component_material:string; bolt_material:string; coating:string|null; temperature_rating:string; api_compliance:string; typical_applications:string; source_reference:string; }
export interface SelectionStep { label:string; detail:string; }
export interface MisalignmentCheck { required_deg?:number|null; required_mm?:number|null; allowable:string; allowable_deg?:number; satisfied:boolean|null; }
export interface Diagnostics { torque_pass:number; bore_pass:number; dbse_pass:number; speed_pass:number; total:number; }
export interface RecommendResponse {
  feasible:boolean; transmitted_torque_nm:number; required_torque_nm:number; service_factor:number;
  recommendation:Coupling|null; selection_steps:SelectionStep[]; reasoning:string[];
  diagnostics?:Diagnostics;
  misalignment_comparison?:{ angular:MisalignmentCheck; parallel:MisalignmentCheck; axial:{allowable_mm:number} };
  alternatives:Coupling[];
}
export interface SelectionRequest {
  driver_shaft_mm:number; driven_shaft_mm:number; dbse_mm:number; power:number; power_unit:'kW'|'HP'; speed:number;
  temperature_c?:number; hours_per_day?:number; service_life_years?:number;
  required_angular_misalignment_deg?:number; required_parallel_misalignment_mm?:number;
  shock_load?:'Light'|'Medium'|'Heavy'; environment?:string; budget?:'Low'|'Medium'|'High';
  precision?:boolean; vibration_damping?:boolean; soft_start?:boolean;
}
