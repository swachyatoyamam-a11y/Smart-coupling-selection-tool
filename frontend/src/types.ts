export type CouplingTypeKey = 'spacer' | 'closed_coupled';
export type Product = 'XTSR52' | 'XTSR71' | 'SERIES71' | '54RDG' | '54RD';
export interface BoreOption { label: string; max_bore_mm: number | null; max_bore_in: number | null; }
export interface Coupling {
  id: number; product: Product; coupling_type: CouplingTypeKey; size: string; name: string;
  disc_pack_style: string; standard_balance: string;
  angular_misalignment_label: string; angular_misalignment_deg: number; parallel_misalignment: string;
  bore_options: BoreOption[];
  min_dbse_mm: number | null; max_dbse_mm: number | null; min_dbse_in: number | null; max_dbse_in: number | null;
  dbse_max_documented: boolean; dbse_is_variable: boolean;
  max_continuous_torque_nm: number | null; max_continuous_torque_lbin: number | null;
  peak_overload_torque_nm: number | null; peak_overload_torque_lbin: number | null;
  max_speed_as_mfd_rpm: number | null; max_speed_balanced_rpm: number | null;
  axial_capacity_mm: number | null; axial_capacity_in: number | null;
  weight_kg: number | null; weight_lb: number | null;
  disc_pack_material: string; major_component_material: string; bolt_material: string;
  coating: string; temperature_rating: string; api_compliance: string; typical_applications: string;
  source_reference_metric: string; source_reference_imperial: string; imperial_not_published: boolean;
}
export interface RecommendedCoupling extends Coupling {
  qualifies_because: string[];
  hub_configuration: string;
  driver_bore_configuration: BoreOption | null;
  driven_bore_configuration: BoreOption | null;
  optional_condition_notes: string[];
  misalignment_comparison: {
    angular: { required_deg: number | null; allowable_label: string; allowable_deg: number; satisfied: boolean | null };
    parallel: { required_mm: number | null; allowable: string; satisfied: null };
    axial: { allowable_mm: number | null; allowable_in: number | null };
  };
}
export interface SelectionStep { label: string; detail: string; }
export interface Diagnostics { torque_pass: number; bore_pass: number; dbse_pass: number; speed_pass: number; temperature_pass: number; total: number; }
export interface ProductSummaryEntry { product: Product; status: 'valid' | 'rejected'; best_size: string | null; reason: string | null; }
export interface TorqueValue { value: number; unit: 'N·m' | 'lb·in'; }
export interface RecommendResponse {
  feasible: boolean; coupling_type: CouplingTypeKey; torque_catalog: string;
  transmitted_torque: TorqueValue; required_torque: TorqueValue; service_factor: number;
  valid_recommendations: RecommendedCoupling[]; alternatives: Coupling[];
  product_summary: ProductSummaryEntry[]; selection_steps: SelectionStep[]; reasoning: string[];
  diagnostics?: Diagnostics;
}
export interface SelectionRequest {
  coupling_type: CouplingTypeKey;
  driver_shaft: number; driver_shaft_unit: 'mm' | 'in';
  driven_shaft: number; driven_shaft_unit: 'mm' | 'in';
  dbse?: number; dbse_unit?: 'mm' | 'in';
  power: number; power_unit: 'kW' | 'HP'; speed: number;
  temperature_c?: number; hours_per_day?: number; service_life_years?: number;
  required_angular_misalignment_deg?: number; required_parallel_misalignment_mm?: number;
  shock_load?: 'Light' | 'Medium' | 'Heavy'; environment?: string; budget?: 'Low' | 'Medium' | 'High';
  precision?: boolean; vibration_damping?: boolean; soft_start?: boolean;
}
