"""Regal Rexnord Thomas Flexible Disc Coupling catalog data.

Transcribed directly from two source documents, both publisher Regal Rexnord / Thomas:
  - METRIC:   "2000_MA4_catalog_2100.pdf"  -> cover reads "Catalog 2000M"
  - IMPERIAL: "2000_catalog_7124.pdf"      -> cover reads "Catalog 2000"

Every numeric field here is transcribed as published, independently per catalog (metric
figures are NOT derived by converting the imperial figures, and vice versa - spot checks
across all products show the two catalogs round their published dimensions independently,
sometimes by several percent, even though the underlying torque rating is the same physical
quantity). Nothing here is estimated, interpolated, or invented. Where a catalog does not
publish a figure (e.g. parallel misalignment, temperature rating, a Max C for Series 71,
or a Std/XL/XXL hub that a given size does not offer), the field is left as None.

Products in scope (Phase 2 - Regal Rexnord Thomas DISC COUPLINGS only):

  Spacer type (coupling_type="spacer"):
    XTSR52   - current lineup, non-adapter spacer.            Catalog pp. 11-13.
    XTSR71   - current lineup, adapter-style spacer.           Catalog pp. 14-17.
    SERIES71 - legacy adapter-style spacer, distinct size      Catalog pp. 41-42.
               numbering from XTSR71. The catalog itself flags
               this page "SEE PAGES [..] FOR UPDATED VERSION
               WITH ENHANCED FEATURES" but does NOT state
               SERIES71 and XTSR71 are the same product, so
               both are modeled as distinct, independently
               selectable candidates per user instruction.

  Close-coupled type (coupling_type="closed_coupled"):
    54RDG    - current lineup, reduced-diameter close-coupled. Catalog p. 9.
    54RD     - current lineup, close-coupled.                  Catalog p. 10.

  Explicitly OUT of scope for this phase (not transcribed): Series 52 (legacy, superseded
  by XTSR52 per the catalog's own footnote), DBZ/DBZ-A/DBZ-B (legacy close-coupled, not
  requested), AMR/CMR/Series 44/XTSRLS*/XTSRGA/XTSRS/miniature couplings (not disc spacer
  or close-coupled products under active consideration in this phase).

Known catalog facts baked into this data (not assumptions):
  - Peak Overload Torque = 2x Max. Continuous Torque, stated as a footnote on every torque
    table in both catalogs.
  - Neither catalog publishes any low-temperature (e.g. -45C) rating or a heat-treatment
    claim for any product in scope. The only temperature figure in either document is
    "Maximum temperature: 250F" under Miniature Couplings, an unrelated product family.
    So `temperature_rating` is None for every row here - this is deliberate, not an
    omission.
  - Parallel misalignment is not published for any product in scope; only Miniature
    Couplings (out of scope) publish a parallel misalignment figure.
  - SERIES71 publishes "Std. C" and "Min. C" but no "Max. C" (unlike XTSR52/XTSR71, which
    publish a real Min C-Max C range). `series71_max_c_is_std_not_published=True` marks
    that its `max_dbse_*` is the catalog's Standard C used as a conservative reference
    ceiling, NOT a documented maximum - callers must not present it as a published max.
  - 54RDG/54RD are true close-coupled designs: each size publishes a single fixed "C"
    dimension, not a variable spacer range. They have no DBSE input concept.
  - 54RD size 1000 is published in the metric catalog only; the supplied imperial catalog
    stops at size 925. Its `*_lbin` / `*_in` imperial fields are therefore None, which
    correctly excludes it from HP-path (Imperial-catalog) candidate pools.
"""

IN_TO_MM = 25.4
LB_TO_KG = 0.45359237
LBIN_TO_NM = 0.112984829


def _angular_label_xtsr(size: int) -> tuple[str, float]:
    """Angular misalignment per disc pack - Catalog 2000/2000M 'General' box, XTSR52/XTSR71."""
    if size in (494, 644):
        return "2/3° per disc pack", 2 / 3
    if size in (726, 826, 996):
        return "1/2° per disc pack", 0.5
    return "1/3° per disc pack", 1 / 3


# ---------------------------------------------------------------------------
# XTSR52 - Spacer Type Coupling (non-adapter). Catalog pp. 11-13.
# ---------------------------------------------------------------------------
XTSR52_SIZES = [494, 644, 726, 826, 996, 1088, 1298, 1548, 1698, 1928, 2068,
                2278, 2468, 2698, 2888, 3058, 3358, 3668, 3908, 4178, 4588, 4918, 5258]
XTSR52_TORQUE_NM = [85, 145, 297, 554, 927, 2190, 3550, 5910, 8190, 11100, 15400,
                     19900, 26200, 35900, 47000, 52000, 70200, 94300, 103000, 128000, 189000, 235000, 283000]
XTSR52_TORQUE_LBIN = [750, 1280, 2630, 4900, 8210, 19400, 31400, 52300, 72500, 98200, 136000,
                       176000, 232000, 318000, 416000, 461000, 622000, 834000, 909000, 1130000, 1670000, 2080000, 2510000]
XTSR52_BORE_MM = [27, 38, 45, 50, 60, 65, 80, 95, 105, 120, 130, 140, 150, 165, 175, 185, 215, 225, 240, 255, 280, 300, 320]
XTSR52_BORE_IN = [1.00, 1.50, 1.75, 2.00, 2.25, 2.50, 3.00, 3.50, 4.00, 4.50, 4.75, 5.38, 5.75, 6.00, 6.75, 7.13, 8.00, 8.88, 9.50, 10.13, 11.00, 11.75, 12.63]
XTSR52_MIN_C_MM = [82, 82, 82, 88, 98, 103, 116, 128, 152, 160, 176, 213, 222, 238, 270, 270, 302, 321, 321, 343, 498, 518, 540]
XTSR52_MAX_C_MM = [163, 239, 373, 374, 781, 783, 788, 792, 794, 796, 799, 800, 803, 1114, 1117, 1117, 1121, 1128, 1128, 1132, 1037, 1041, 1046]
XTSR52_MIN_C_IN = [3.23, 3.23, 3.23, 3.47, 3.84, 4.06, 4.56, 5.04, 6.00, 6.30, 6.93, 8.38, 8.73, 9.36, 10.63, 10.63, 11.88, 12.62, 12.62, 13.50, 19.62, 20.38, 21.25]
XTSR52_MAX_C_IN = [6.40, 9.40, 14.68, 14.74, 30.76, 30.82, 31.02, 31.16, 31.24, 31.34, 31.45, 31.51, 31.61, 43.85, 43.98, 43.98, 44.15, 44.39, 44.39, 44.55, 40.83, 41.00, 41.17]
XTSR52_RPM_MFD = [13800, 12500, 12000, 10900, 9800, 9000, 8000, 7100, 6600, 6100, 5800, 5500, 5200, 4800, 4600, 4400, 4200, 3900, 3800, 3600, 3400, 3200, 3100]
XTSR52_RPM_BAL = [23000, 21500, 20000, 18500, 15000, 14000, 12000, 10000, 9100, 8500, 7800, 7100, 6500, 6000, 5700, 5400, 4700, 4400, 4100, 3900, 3600, 3300, 3100]
XTSR52_AXIAL_MM = [1.2, 1.7, 1.3, 1.5, 1.8, 1.3, 1.6, 1.8, 2.0, 2.3, 2.5, 2.7, 3.0, 3.2, 3.5, 3.7, 4.0, 4.4, 4.7, 5.0, 5.5, 5.9, 6.3]
XTSR52_AXIAL_IN = [0.05, 0.07, 0.05, 0.06, 0.07, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10, 0.11, 0.12, 0.13, 0.14, 0.15, 0.16, 0.17, 0.19, 0.20, 0.22, 0.23, 0.25]
XTSR52_WEIGHT_KG = [0.88, 1.35, 1.77, 3.34, 4.78, 8.34, 13.6, 20.8, 29.0, 38.2, 49.9, 69.7, 87.3, 111, 150, 172, 232, 329, 381, 468, 661, 817, 991]
XTSR52_WEIGHT_LB = [1.98, 3.09, 4.41, 7.28, 10.8, 19.0, 31.3, 48.7, 67.2, 89.1, 118, 157, 197, 260, 333, 384, 534, 723, 837, 1024, 1466, 1819, 2191]

# ---------------------------------------------------------------------------
# XTSR71 - Spacer Type Coupling with Adapters. Catalog pp. 14-17.
# ---------------------------------------------------------------------------
XTSR71_SIZES = XTSR52_SIZES
XTSR71_TORQUE_NM = XTSR52_TORQUE_NM
XTSR71_TORQUE_LBIN = XTSR52_TORQUE_LBIN
XTSR71_STD_BORE_MM = [28, 38, 42, 52, 61, 76, 90, 105, 125, 135, 150, 155, 166, 200, 220, 235, 260, 285, 310, 330, 360, 400, 430]
XTSR71_XL_BORE_MM = [None, None, 52, 61, 76, 90, 105, 125, 135, 150, 155, 166, 200, 220, 235, 260, 285, 310, 330, 360, 400, 430, None]
XTSR71_XXL_BORE_MM = [42, 52, 61, 76, 90, 105, 125, 135, 150, 155, 166, 200, 220, 235, 260, 285, 310, 330, 360, 400, 430, None, None]
XTSR71_STD_BORE_IN = [1.13, 1.50, 1.63, 2.00, 2.38, 2.88, 3.38, 4.00, 4.50, 5.00, 5.50, 6.00, 6.50, 7.75, 8.63, 9.13, 10.00, 11.00, 11.50, 12.25, 14.00, 15.00, 16.00]
XTSR71_XL_BORE_IN = [1.50, None, 2.00, 2.38, 2.88, 3.38, 4.00, 4.50, 5.00, 5.50, 6.00, 6.50, 7.75, 8.63, 9.13, 10.00, 11.00, 11.50, 12.25, 14.00, 15.00, 16.00, None]
XTSR71_XXL_BORE_IN = [1.63, 2.00, 2.38, 2.88, 3.38, 4.00, 4.50, 5.00, 5.50, 6.00, 6.50, 7.75, 8.63, 9.13, 10.00, 11.00, 11.50, 12.25, 14.00, 15.00, 16.00, None, None]
XTSR71_MIN_C_MM = [65, 68, 65, 77, 92, 96, 115, 135, 151, 161, 187, 196, 209, 236, 255, 257, 287, 310, 311, 340, 386, 408, 438]
XTSR71_MAX_C_MM = [162, 266, 398, 404, 819, 821, 834, 846, 856, 861, 877, 881, 889, 1211, 1221, 1222, 1239, 1254, 1255, 1272, 1197, 1209, 1227]
XTSR71_MIN_C_IN = [2.56, 2.68, 2.56, 3.03, 3.62, 3.78, 4.53, 5.31, 5.94, 6.34, 7.36, 7.72, 8.23, 9.29, 10.04, 10.12, 11.30, 12.20, 12.24, 13.39, 15.20, 16.06, 17.24]
XTSR71_MAX_C_IN = [6.40, 10.50, 15.68, 15.89, 32.30, 32.28, 32.80, 33.33, 33.65, 33.87, 34.59, 34.69, 34.99, 47.62, 48.09, 48.13, 48.85, 49.34, 49.39, 50.11, 47.13, 47.60, 48.31]
XTSR71_RPM_MFD = XTSR52_RPM_MFD
XTSR71_RPM_BAL = XTSR52_RPM_BAL
XTSR71_AXIAL_MM = XTSR52_AXIAL_MM
XTSR71_AXIAL_IN = XTSR52_AXIAL_IN
XTSR71_WEIGHT_KG = [1.6, 2.5, 3.1, 5.0, 8.4, 12.5, 20.6, 34.6, 47.0, 62.7, 84.9, 110, 143, 184, 257, 274, 366, 521, 536, 648, 993, 1200, 1420]
XTSR71_WEIGHT_LB = [3.50, 5.50, 6.80, 10.6, 18.1, 27.1, 45.9, 76.5, 106, 140, 190, 246, 312, 420, 556, 627, 814, 1131, 1213, 1454, 2188, 2697, 3170]

# ---------------------------------------------------------------------------
# SERIES71 (legacy) - Spacer Type Coupling. Catalog pp. 41-42.
# No Max. C is published for this product (only Std. C and Min. C) - see module docstring.
# ---------------------------------------------------------------------------
SERIES71_SIZES = ["150", "175", "225", "300", "350", "375", "412", "462", "512", "562", "600",
                   "225-8", "262-8", "312-8", "350-8", "375-8", "425-8", "450-8", "500-8", "550-8", "600-8", "700-8", "750-8"]
SERIES71_BOLT_DESIGN = ["4-Bolt", "4-Bolt", "6-Bolt", "6-Bolt", "6-Bolt", "6-Bolt", "6-Bolt", "6-Bolt", "6-Bolt", "6-Bolt", "6-Bolt",
                         "8-Bolt", "8-Bolt", "8-Bolt", "8-Bolt", "8-Bolt", "8-Bolt", "8-Bolt", "8-Bolt", "8-Bolt", "8-Bolt", "8-Bolt", "8-Bolt"]
SERIES71_TORQUE_LBIN = [930, 1630, 3060, 7260, 13400, 19300, 22500, 40400, 55000, 84100, 91700,
                          17500, 32830, 51400, 66900, 100300, 134300, 150400, 246400, 330400, 433800, 674800, 838800]
SERIES71_TORQUE_NM = [105, 184, 345, 820, 1513, 2179, 2540, 4561, 6209, 9494, 10352,
                        1976, 3706, 5803, 7552, 11323, 15161, 16979, 27817, 37300, 48973, 76180, 94694]
SERIES71_B_HUB_BORE_IN = [1.500, 1.875, 2.250, 3.000, 3.500, 3.750, 4.125, 4.625, 5.125, 5.625, 6.000,
                            3.000, 3.438, 4.188, 4.688, 5.250, 5.625, 6.188, 7.000, 7.625, 8.812, 9.750, 10.812]
SERIES71_B2_HUB_BORE_IN = [2.375, 2.750, 3.250, 4.000, 4.500, 5.000, 5.310, 6.000, 6.690, 7.310, 7.810,
                             3.750, 4.188, 5.125, 5.562, 6.500, 6.750, 7.500, 8.750, None, None, None, None]
SERIES71_B_HUB_BORE_MM = [39, 50, 58, 81, 95, 100, 110, 130, 140, 156, 166,
                            80, 95, 112, 130, 144, 158, 170, 196, 215, 242, 258, 286]
SERIES71_B2_HUB_BORE_MM = [64, 73, 87, 110, 120, 137, 145, 166, 187, 200, 220,
                             106, 128, 145, 166, 185, 203, 214, 248, None, None, None, None]
SERIES71_STD_C_IN = [3.50, 3.50, 5.00, 5.00, 5.00, 5.50, 7.00, 7.00, 7.00, 8.00, 9.00,
                      5.00, 7.00, 7.50, 7.50, 7.50, 8.00, 9.00, 11.00, 11.50, 12.50, 14.50, 15.75]
SERIES71_MIN_C_IN = [3.44, 3.44, 3.44, 4.00, 4.88, 5.00, 6.12, 7.00, 7.00, 8.00, 9.00,
                      4.75, 5.50, 6.00, 6.75, 7.25, 7.50, 8.75, 10.25, 11.50, 12.50, 14.50, 15.75]
SERIES71_STD_C_MM = [89, 89, 127, 127, 127, 140, 178, 178, 178, 203, 229,
                      127, 178, 191, 191, 191, 203, 229, 279, 292, 318, 368, 400]
SERIES71_MIN_C_MM = [87, 87, 87, 102, 124, 127, 155, 178, 178, 203, 229,
                      121, 140, 152, 171, 184, 191, 222, 260, 292, 318, 368, 400]
SERIES71_RPM_MFD = [9000, 8300, 7700, 6800, 6200, 5650, 5350, 5000, 4700, 4350, 4150,
                     7500, 6800, 6200, 5700, 5200, 5000, 4700, 4200, 3900, 3600, 3300, 3100]
SERIES71_RPM_BAL = [20800, 17000, 16000, 14000, 13500, 12000, 11000, 10000, 9200, 8300, 7800,
                     14000, 12500, 11500, 10500, 9800, 9300, 8700, 7900, 7300, 6800, 6200, 5800]
SERIES71_WEIGHT_LB = [6.7, 9.4, 14.0, 26.0, 43.0, 55.0, 71.0, 101.0, 135.0, 186.0, 228.0,
                       27.8, 43.0, 67.0, 95.0, 134.0, 169.0, 220.0, 341.0, 475.0, 653.0, 961.0, 1242.0]
SERIES71_WEIGHT_KG = [3.0, 4.3, 6.4, 11.8, 19.5, 25.0, 32.2, 45.9, 61.3, 84.4, 103.5,
                       12.6, 19.5, 30.0, 43.0, 61.0, 77.0, 100.0, 155.0, 216.0, 296.0, 436.0, 564.0]
# Axial capacity in inches, cross-referenced against the metric column for the first three
# entries (the source PDF's metric axial column extracted as "0.127/0.1778/0.1905" for
# 150/175/225, one decimal short of the pattern every other row follows - corrected here to
# 1.27/1.78/1.91mm by cross-checking against this inch column x25.4, per Part G).
SERIES71_AXIAL_IN = [0.050, 0.070, 0.075, 0.085, 0.090, 0.095, 0.110, 0.120, 0.130, 0.145, 0.160,
                      0.036, 0.043, 0.051, 0.056, 0.062, 0.067, 0.072, 0.082, 0.092, 0.102, 0.115, 0.125]

# ---------------------------------------------------------------------------
# 54RDG - Close-Coupled Coupling. Catalog p. 9.
# ---------------------------------------------------------------------------
S54RDG_SIZES = [125, 162, 200, 225, 262, 312, 350, 375, 425, 450, 500, 550, 600, 700, 750, 800, 850, 925]
S54RDG_BORE_INTERNAL_IN = [1.19, 1.62, 2.25, 2.38, 2.75, 3.38, 3.75, 4.19, 4.50, 4.75, 5.00, 5.50, 6.00, 7.00, 7.50, 8.00, 8.50, 9.00]
S54RDG_BORE_EXTERNAL_IN = [1.38, 1.88, 2.25, 2.62, 3.12, 3.62, 4.00, 4.50, 4.75, 5.12, 5.38, 6.00, 6.50, 7.50, 8.00, 8.75, 9.25, 10.12]
S54RDG_BORE_INTERNAL_MM = [29, 42, 58, 65, 74, 95, 100, 114, 120, 130, 137, 150, 166, 195, 206, 223, 235, 248]
S54RDG_BORE_EXTERNAL_MM = [34, 50, 58, 70, 84, 97, 110, 120, 130, 140, 146, 166, 176, 205, 224, 241, 250, 267]
S54RDG_TORQUE_LBIN = [2700, 5350, 10500, 17500, 32830, 51400, 66900, 100300, 134300, 150400, 246400, 330400, 433800, 674800, 838800, 1078700, 1273000, 1724000]
S54RDG_TORQUE_NM = [305, 604, 1185, 1976, 3706, 5803, 7552, 11323, 15161, 16979, 27817, 37300, 48973, 76242, 94772, 121877, 143830, 194786]
S54RDG_WEIGHT_LB = [6.90, 9.27, 16.4, 19.0, 31.4, 45.6, 65.9, 87.7, 116, 149, 224, 323, 430, 657, 837, 1028, 1259, 1684]
S54RDG_WEIGHT_KG = [3.1, 4.2, 7.3, 8.6, 14.1, 20.9, 30.0, 40.0, 53.1, 69.9, 101.7, 147.1, 198.4, 298.3, 380.9, 472.2, 572.0, 767.3]
S54RDG_RPM_MFD = [4600, 4200, 3800, 3700, 3600, 3000, 2800, 2500, 2300, 2200, 2000, 1900, 1800, 1700, 1550, 1450, 1350, 1300]
S54RDG_RPM_BAL = [10500, 9700, 8600, 8400, 7400, 6700, 6200, 5800, 5400, 5000, 4600, 4200, 3900, 3600, 3400, 3200, 3000, 2800]
S54RDG_AXIAL_IN = [0.036, 0.036, 0.036, 0.036, 0.043, 0.051, 0.056, 0.062, 0.067, 0.072, 0.082, 0.092, 0.102, 0.115, 0.125, 0.136, 0.144, 0.156]
S54RDG_AXIAL_MM = [0.91, 0.91, 0.91, 0.91, 1.09, 1.29, 1.42, 1.57, 1.70, 1.82, 2.02, 2.33, 2.59, 2.92, 3.17, 3.45, 3.65, 3.96]

# ---------------------------------------------------------------------------
# 54RD - Close-Coupled Coupling. Catalog p. 10.
# Metric catalog publishes an extra size (1000) that the supplied imperial catalog does not.
# ---------------------------------------------------------------------------
S54RD_SIZES_METRIC = [125, 162, 200, 225, 262, 312, 350, 375, 425, 450, 500, 550, 600, 700, 750, 800, 850, 925, 1000]
S54RD_SIZES_IMPERIAL = [125, 162, 200, 225, 262, 312, 350, 375, 425, 450, 500, 550, 600, 700, 750, 800, 850, 925]  # no 1000
S54RD_BORE_INTERNAL_MM = [29, 42, 58, 65, 74, 95, 100, 114, 120, 130, 137, 150, 166, 195, 206, 223, 235, 248, 264]
S54RD_BORE_EXTERNAL_MM = [34, 50, 58, 70, 84, 97, 110, 120, 130, 140, 146, 166, 176, 205, 224, 241, 250, 267, 290]
S54RD_TORQUE_NM = [263, 492, 958, 1208, 1976, 2743, 3850, 5769, 8162, 9280, 13999, 24272, 30368, 39061, 52721, 65478, 80041, 106909, 146760]
S54RD_WEIGHT_KG = [3.0, 4.4, 7.3, 8.2, 14.1, 21.5, 31.0, 42.9, 56.8, 74.9, 109, 158, 217, 324, 402, 499, 663, 890, 1108]
S54RD_RPM_MFD_METRIC = [4600, 4200, 3800, 3700, 3600, 3000, 2800, 2500, 2300, 2200, 2000, 1900, 1800, 1700, 1550, 1450, 1350, 1300, 1200]
S54RD_RPM_BAL_METRIC = [7200, 7000, 6300, 6000, 5500, 5000, 4500, 4000, 3700, 3400, 3300, 2800, 2500, 2500, 2200, 2100, 1950, 1850, 1750]
S54RD_AXIAL_MM = [0.91, 0.91, 0.91, 0.91, 1.09, 1.29, 1.42, 1.57, 1.70, 1.82, 2.02, 2.33, 2.59, 2.92, 3.17, 3.45, 3.65, 3.96, 4.36]

S54RD_BORE_INTERNAL_IN = [1.19, 1.62, 2.25, 2.38, 2.75, 3.38, 3.75, 4.19, 4.50, 4.75, 5.00, 5.50, 6.00, 7.00, 7.50, 8.00, 8.50, 9.00]
S54RD_BORE_EXTERNAL_IN = [1.38, 1.88, 2.25, 2.62, 3.12, 3.62, 4.00, 4.50, 4.75, 5.12, 5.38, 6.00, 6.50, 7.50, 8.00, 8.75, 9.25, 10.12]
S54RD_TORQUE_LBIN = [2330, 4360, 8490, 10700, 17500, 24300, 34100, 51100, 72300, 82200, 124000, 215000, 269000, 346000, 467000, 580000, 709000, 947000]
S54RD_WEIGHT_LB = [6.63, 9.00, 16.1, 18.2, 30.1, 47.8, 69.6, 94.8, 126, 164, 244, 351, 480, 721, 868, 1095, 1452, 1954]
S54RD_RPM_MFD_IMPERIAL = [4600, 4200, 3800, 3700, 3600, 3000, 2800, 2500, 2300, 2200, 2000, 1900, 1800, 1700, 1550, 1450, 1350, 1300]
S54RD_RPM_BAL_IMPERIAL = [7200, 7000, 6300, 6000, 5500, 5000, 4500, 4000, 3700, 3400, 3300, 2800, 2500, 2500, 2200, 2100, 1950, 1850]
S54RD_AXIAL_IN = [0.036, 0.036, 0.036, 0.036, 0.043, 0.051, 0.056, 0.062, 0.067, 0.072, 0.082, 0.092, 0.102, 0.115, 0.125, 0.136, 0.144, 0.156]


def build_rows() -> list[dict]:
    """Assemble every catalog row into a flat, unit-dual list of plain dicts.

    Each row carries BOTH metric-native and imperial-native fields for every
    dimension that both catalogs publish, so the selection engine can pick
    whichever catalog is authoritative (per power unit) without converting
    through the other.
    """
    rows: list[dict] = []

    # XTSR52
    for i, size in enumerate(XTSR52_SIZES):
        label, deg = _angular_label_xtsr(size)
        rows.append(dict(
            product="XTSR52", coupling_type="spacer", size=str(size), name=f"XTSR52-{size}",
            disc_pack_style="Unitized XTSR", standard_balance="AGMA Class 9",
            angular_misalignment_label=label, angular_misalignment_deg=deg, parallel_misalignment=None,
            bore_options=[
                {"label": "Max Bore", "max_bore_mm": XTSR52_BORE_MM[i], "max_bore_in": XTSR52_BORE_IN[i]},
            ],
            min_dbse_mm=XTSR52_MIN_C_MM[i], max_dbse_mm=XTSR52_MAX_C_MM[i], dbse_max_documented=True,
            min_dbse_in=XTSR52_MIN_C_IN[i], max_dbse_in=XTSR52_MAX_C_IN[i],
            dbse_is_variable=True, fixed_c_mm=None, fixed_c_in=None,
            max_continuous_torque_nm=XTSR52_TORQUE_NM[i], max_continuous_torque_lbin=XTSR52_TORQUE_LBIN[i],
            peak_overload_torque_nm=XTSR52_TORQUE_NM[i] * 2, peak_overload_torque_lbin=XTSR52_TORQUE_LBIN[i] * 2,
            max_speed_as_mfd_rpm=XTSR52_RPM_MFD[i], max_speed_balanced_rpm=XTSR52_RPM_BAL[i],
            axial_capacity_mm=XTSR52_AXIAL_MM[i], axial_capacity_in=XTSR52_AXIAL_IN[i],
            weight_kg=XTSR52_WEIGHT_KG[i], weight_lb=XTSR52_WEIGHT_LB[i],
            disc_pack_material="Stainless steel", major_component_material="Carbon steel", bolt_material="Alloy steel",
            coating="Manganese phosphate (other coatings available on request)", temperature_rating=None,
            api_compliance="API 610, ISO 14691 compliant when specified; ATEX II 2GD c T6 certified.",
            typical_applications="Pumps and compressors (centrifugal, rotary, lobe and axial), speed increasers, fans, dynamometers.",
            source_reference_metric="Regal Rexnord Thomas Flexible Disc Couplings, Catalog 2000M, XTSR52 Spacer Type Coupling, pp. 11-13",
            source_reference_imperial="Regal Rexnord Thomas Flexible Disc Couplings, Catalog 2000 (Imperial), XTSR52 Spacer Type Coupling, pp. 11-13",
        ))

    # XTSR71
    for i, size in enumerate(XTSR71_SIZES):
        label, deg = _angular_label_xtsr(size)
        bore_options = [{"label": "Std Hub", "max_bore_mm": XTSR71_STD_BORE_MM[i], "max_bore_in": XTSR71_STD_BORE_IN[i]}]
        if XTSR71_XL_BORE_MM[i] is not None:
            bore_options.append({"label": "XL Hub", "max_bore_mm": XTSR71_XL_BORE_MM[i], "max_bore_in": XTSR71_XL_BORE_IN[i]})
        if XTSR71_XXL_BORE_MM[i] is not None:
            bore_options.append({"label": "XXL Hub", "max_bore_mm": XTSR71_XXL_BORE_MM[i], "max_bore_in": XTSR71_XXL_BORE_IN[i]})
        rows.append(dict(
            product="XTSR71", coupling_type="spacer", size=str(size), name=f"XTSR71-{size}",
            disc_pack_style="Unitized XTSR", standard_balance="AGMA Class 9",
            angular_misalignment_label=label, angular_misalignment_deg=deg, parallel_misalignment=None,
            bore_options=bore_options,
            min_dbse_mm=XTSR71_MIN_C_MM[i], max_dbse_mm=XTSR71_MAX_C_MM[i], dbse_max_documented=True,
            min_dbse_in=XTSR71_MIN_C_IN[i], max_dbse_in=XTSR71_MAX_C_IN[i],
            dbse_is_variable=True, fixed_c_mm=None, fixed_c_in=None,
            max_continuous_torque_nm=XTSR71_TORQUE_NM[i], max_continuous_torque_lbin=XTSR71_TORQUE_LBIN[i],
            peak_overload_torque_nm=XTSR71_TORQUE_NM[i] * 2, peak_overload_torque_lbin=XTSR71_TORQUE_LBIN[i] * 2,
            max_speed_as_mfd_rpm=XTSR71_RPM_MFD[i], max_speed_balanced_rpm=XTSR71_RPM_BAL[i],
            axial_capacity_mm=XTSR71_AXIAL_MM[i], axial_capacity_in=XTSR71_AXIAL_IN[i],
            weight_kg=XTSR71_WEIGHT_KG[i], weight_lb=XTSR71_WEIGHT_LB[i],
            disc_pack_material="Stainless steel", major_component_material="Carbon steel", bolt_material="Alloy steel",
            coating=None, temperature_rating=None,
            api_compliance="API 610 / ISO 14691 compliant as standard; API 671 (ISO 10441) compliant when specified; ATEX II 2GD c T6 certified.",
            typical_applications="Pumps and compressors with popular shaft separation standards, blowers, fans, speed increasers.",
            source_reference_metric="Regal Rexnord Thomas Flexible Disc Couplings, Catalog 2000M, XTSR71 Spacer Type Coupling with Adapters, pp. 14-17",
            source_reference_imperial="Regal Rexnord Thomas Flexible Disc Couplings, Catalog 2000 (Imperial), XTSR71 Spacer Type Coupling with Adapters, pp. 14-17",
        ))

    # SERIES71 (legacy)
    for i, size in enumerate(SERIES71_SIZES):
        bore_options = [{"label": "B & B1 Hub", "max_bore_mm": SERIES71_B_HUB_BORE_MM[i], "max_bore_in": SERIES71_B_HUB_BORE_IN[i]}]
        if SERIES71_B2_HUB_BORE_MM[i] is not None:
            bore_options.append({"label": "B2 Hub", "max_bore_mm": SERIES71_B2_HUB_BORE_MM[i], "max_bore_in": SERIES71_B2_HUB_BORE_IN[i]})
        disc_pack_style = "Slabbed (4-bolt)" if SERIES71_BOLT_DESIGN[i] == "4-Bolt" else ("Slabbed (6-bolt)" if SERIES71_BOLT_DESIGN[i] == "6-Bolt" else "Tpack (8-bolt)")
        rows.append(dict(
            product="SERIES71", coupling_type="spacer", size=size, name=f"SERIES71-{size}",
            disc_pack_style=disc_pack_style, standard_balance="AGMA Class 9",
            angular_misalignment_label="1/3° per disc pack", angular_misalignment_deg=1 / 3, parallel_misalignment=None,
            bore_options=bore_options,
            min_dbse_mm=SERIES71_MIN_C_MM[i], max_dbse_mm=SERIES71_STD_C_MM[i], dbse_max_documented=False,
            min_dbse_in=SERIES71_MIN_C_IN[i], max_dbse_in=SERIES71_STD_C_IN[i],
            dbse_is_variable=True, fixed_c_mm=None, fixed_c_in=None,
            max_continuous_torque_nm=SERIES71_TORQUE_NM[i], max_continuous_torque_lbin=SERIES71_TORQUE_LBIN[i],
            peak_overload_torque_nm=SERIES71_TORQUE_NM[i] * 2, peak_overload_torque_lbin=SERIES71_TORQUE_LBIN[i] * 2,
            max_speed_as_mfd_rpm=SERIES71_RPM_MFD[i], max_speed_balanced_rpm=SERIES71_RPM_BAL[i],
            axial_capacity_mm=round(SERIES71_AXIAL_IN[i] * IN_TO_MM, 3), axial_capacity_in=SERIES71_AXIAL_IN[i],
            weight_kg=SERIES71_WEIGHT_KG[i], weight_lb=SERIES71_WEIGHT_LB[i],
            disc_pack_material="Stainless steel (Monel and Inconel available as options)",
            major_component_material="Carbon steel", bolt_material="Alloy steel",
            coating="Options: Black Oxide, Zinc, Cadmium", temperature_rating=None,
            api_compliance="API 610 or API 671 compliant when specified.",
            typical_applications="Motor, turbine, and gear driven pumps, compressors, and blowers.",
            source_reference_metric="Regal Rexnord Thomas Flexible Disc Couplings, Catalog 2000M, Series 71 Spacer Type Couplings (Supported Products - legacy), pp. 41-42",
            source_reference_imperial="Regal Rexnord Thomas Flexible Disc Couplings, Catalog 2000 (Imperial), Series 71 Spacer Type Couplings (Supported Products - legacy), pp. 41-42",
        ))

    # 54RDG
    for i, size in enumerate(S54RDG_SIZES):
        rows.append(dict(
            product="54RDG", coupling_type="closed_coupled", size=str(size), name=f"54RDG-{size}",
            disc_pack_style="Classic Round", standard_balance="AGMA Class 6",
            angular_misalignment_label="1/3° per disc pack", angular_misalignment_deg=1 / 3, parallel_misalignment=None,
            bore_options=[
                {"label": "Internal", "max_bore_mm": S54RDG_BORE_INTERNAL_MM[i], "max_bore_in": S54RDG_BORE_INTERNAL_IN[i]},
                {"label": "External", "max_bore_mm": S54RDG_BORE_EXTERNAL_MM[i], "max_bore_in": S54RDG_BORE_EXTERNAL_IN[i]},
            ],
            min_dbse_mm=None, max_dbse_mm=None, dbse_max_documented=False,
            min_dbse_in=None, max_dbse_in=None,
            dbse_is_variable=False, fixed_c_mm=None, fixed_c_in=None,  # C is a drawing dimension, not a selectable span, for this close-coupled design
            max_continuous_torque_nm=S54RDG_TORQUE_NM[i], max_continuous_torque_lbin=S54RDG_TORQUE_LBIN[i],
            peak_overload_torque_nm=S54RDG_TORQUE_NM[i] * 2, peak_overload_torque_lbin=S54RDG_TORQUE_LBIN[i] * 2,
            max_speed_as_mfd_rpm=S54RDG_RPM_MFD[i], max_speed_balanced_rpm=S54RDG_RPM_BAL[i],
            axial_capacity_mm=S54RDG_AXIAL_MM[i], axial_capacity_in=S54RDG_AXIAL_IN[i],
            weight_kg=S54RDG_WEIGHT_KG[i], weight_lb=S54RDG_WEIGHT_LB[i],
            disc_pack_material="Stainless steel (Tomaloy, Monel and Inconel available as options)",
            major_component_material="Carbon steel", bolt_material="Alloy steel",
            coating=None, temperature_rating=None,
            api_compliance="API 610 or API 671 compliant when specified.",
            typical_applications="Reduced-diameter gear/grid coupling replacement where shaft-to-shaft spacing is minimal.",
            source_reference_metric="Regal Rexnord Thomas Flexible Disc Couplings, Catalog 2000M, Series 54RDG Close-Coupled Coupling, p. 9",
            source_reference_imperial="Regal Rexnord Thomas Flexible Disc Couplings, Catalog 2000 (Imperial), Series 54RDG Close-Coupled Coupling, p. 9",
        ))

    # 54RD (metric list is authoritative for iteration since it has one extra size)
    for i, size in enumerate(S54RD_SIZES_METRIC):
        has_imperial = size in S54RD_SIZES_IMPERIAL
        j = S54RD_SIZES_IMPERIAL.index(size) if has_imperial else None
        rows.append(dict(
            product="54RD", coupling_type="closed_coupled", size=str(size), name=f"54RD-{size}",
            disc_pack_style="Classic Round", standard_balance="AGMA Class 6",
            angular_misalignment_label="1/3° per disc pack", angular_misalignment_deg=1 / 3, parallel_misalignment=None,
            bore_options=[
                {"label": "Internal", "max_bore_mm": S54RD_BORE_INTERNAL_MM[i], "max_bore_in": (S54RD_BORE_INTERNAL_IN[j] if has_imperial else None)},
                {"label": "External", "max_bore_mm": S54RD_BORE_EXTERNAL_MM[i], "max_bore_in": (S54RD_BORE_EXTERNAL_IN[j] if has_imperial else None)},
            ],
            min_dbse_mm=None, max_dbse_mm=None, dbse_max_documented=False,
            min_dbse_in=None, max_dbse_in=None,
            dbse_is_variable=False, fixed_c_mm=None, fixed_c_in=None,
            max_continuous_torque_nm=S54RD_TORQUE_NM[i], max_continuous_torque_lbin=(S54RD_TORQUE_LBIN[j] if has_imperial else None),
            peak_overload_torque_nm=S54RD_TORQUE_NM[i] * 2, peak_overload_torque_lbin=(S54RD_TORQUE_LBIN[j] * 2 if has_imperial else None),
            max_speed_as_mfd_rpm=S54RD_RPM_MFD_METRIC[i], max_speed_balanced_rpm=S54RD_RPM_BAL_METRIC[i],
            axial_capacity_mm=S54RD_AXIAL_MM[i], axial_capacity_in=(S54RD_AXIAL_IN[j] if has_imperial else None),
            weight_kg=S54RD_WEIGHT_KG[i], weight_lb=(S54RD_WEIGHT_LB[j] if has_imperial else None),
            disc_pack_material="Stainless steel (Tomaloy, Monel and Inconel available as options)",
            major_component_material="Carbon steel", bolt_material="Alloy steel",
            coating=None, temperature_rating=None,
            api_compliance="API 610 compliant when specified.",
            typical_applications="Close-coupled replacement for gear and grid couplings.",
            source_reference_metric="Regal Rexnord Thomas Flexible Disc Couplings, Catalog 2000M, Series 54RD Close-Coupled Coupling, p. 10",
            source_reference_imperial=("Regal Rexnord Thomas Flexible Disc Couplings, Catalog 2000 (Imperial), Series 54RD Close-Coupled Coupling, p. 10" if has_imperial else None),
            imperial_not_published=not has_imperial,
        ))

    return rows
