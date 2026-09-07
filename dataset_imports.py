CYCLE = 5

centroidal_datasets = [
    {"a": 0.001, "file": "DATA/Centroidal/OrientationO/PC216M3Db_Centroidal_a0_OrientationO_1.csv",             "load": 38, "mass": 18.72, "orientation": "O", "title": "Centroidal, a=0.001"},
    {"a": 0.125, "file": "DATA/Centroidal/OrientationO/PC216C3D_Centroidal_1.5mm_75mm_a0.125_OrientationO.csv", "load": 36, "mass": 19.68, "orientation": "O", "title": "Centroidal, a=0.125"},
    {"a": 0.25,  "file": "DATA/Centroidal/OrientationO/PC216C3D_Centroidal_1.5mm_75mm_a0.25_O.csv",              "load": 36, "mass": 18.47, "orientation": "O", "title": "Centroidal, a=0.25"},
    {"a": 0.5,   "file": "DATA/Centroidal/OrientationO/PC216C3D_Centroidal_1.5mm_75mm_a0.5_OrientationO.csv",    "load": 36, "mass": 17.91, "orientation": "O", "title": "Centroidal, a=0.5"},
    {"a": 0.75,  "file": "DATA/Centroidal/OrientationO/PC216C3D_Centroidal_1.5mm_75mm_a0.75_O.csv",              "load": 36, "mass": 18.42, "orientation": "O", "title": "Centroidal, a=0.75"},
    {"a": 1.00,  "file": "DATA/Centroidal/OrientationO/PC216C3D_Centroidal_1.5mm_75mm_a1.00_OrientationO.csv",   "load": 36, "mass": 18.19, "orientation": "O", "title": "Centroidal, a=1.0"},
]

delaunay_datasets = [
    {"a": 0.001, "file": "DATA/Delaunay/OrientationO/PC216M3Db_Delaunay_a0_OrientationO_1.csv",                 "load": 36, "mass": 33.34, "orientation": "O", "title": "Delaunay, a=0.001"},
    {"a": 0.125, "file": "DATA/Delaunay/OrientationO/PC216D3D_Delaunay_1.5mm_75mm_a0.125_OrientationO.csv",     "load": 36, "mass": 34.11, "orientation": "O", "title": "Delaunay, a=0.125"},
    {"a": 0.25,  "file": "DATA/Delaunay/OrientationO/PC216D3D_Delaunay_1.5mm_75mm_a0.25_OrientationO.csv",      "load": 36, "mass": 32.71, "orientation": "O", "title": "Delaunay, a=0.25"},
    {"a": 0.5,   "file": "DATA/Delaunay/OrientationO/PC216D3D_Delaunay_1.5mm_75mm_a0.5_orientationO.csv",       "load": 36, "mass": 30.85, "orientation": "O", "title": "Delaunay, a=0.5"},
    {"a": 0.75,  "file": "DATA/Delaunay/OrientationO/PC216D3Dcl_Delaunay_1.5mm_75mm_a0.75_OrientationO.csv",    "load": 36, "mass": 31.59, "orientation": "O", "title": "Delaunay, a=0.75"},
    {"a": 1.00,  "file": "DATA/Delaunay/OrientationO/PC216D3D_Delaunay_1.5mm_75mm_a1.00_OrientationO.csv",      "load": 36, "mass": 31.92, "orientation": "O", "title": "Delaunay, a=1.0"},

    # Mass reused from the OrientationO sample at the same a-value (orientation doesn't affect mass).
    {"a": 0.001, "file": "DATA/Delaunay/Orientation1/PC216M3Db_Delaunay_1.5mm_75mm_a0.001_Orientation1.csv",    "load": 36, "mass": 33.34, "orientation": "1", "title": "Delaunay, a=0.001, Orientation 1"},
    {"a": 0.25,  "file": "DATA/Delaunay/OrientationN/PC216D3D_Delaunay_1.5mm_75mm_a0.25_OrientationN.csv",      "load": 36, "mass": 32.71, "orientation": "N", "title": "Delaunay, a=0.25, Orientation N"},
]

# Masses sourced from script-cycle-G.py (masses array aligned to a_values [0.001, 0.125, 0.25, 0.5, 0.75, 1])
gabriel_datasets = [
    {"a": 0.001, "file": "DATA/Gabriel/OrientationO/PC216M3Db_Gabriel_a0_OrientationO_1.csv",              "load": 36, "mass": 19.08, "orientation": "O", "title": "Gabriel, a=0.001"},
    {"a": 0.125, "file": "DATA/Gabriel/OrientationO/PC216G3D_Gabriel_1.5mm_75mm_a0.125_OrientationO.csv",  "load": 36, "mass": 18.59, "orientation": "O", "title": "Gabriel, a=0.125"},
    {"a": 0.25,  "file": "DATA/Gabriel/OrientationO/PC216G3D_Gabriel_1.5mm_75mm_a0.25_OrientationO.csv",   "load": 36, "mass": 17.95, "orientation": "O", "title": "Gabriel, a=0.25"},
    {"a": 0.5,   "file": "DATA/Gabriel/OrientationO/PC216G3D_Gabriel_1.5mm_75mm_a0.5_orientationO.csv",    "load": 36, "mass": 19.73, "orientation": "O", "title": "Gabriel, a=0.5"},
    {"a": 0.75,  "file": "DATA/Gabriel/OrientationO/PC216G3Dcl_Gabriel_1.5mm_75mm_a0.75_OrientationO.csv", "load": 36, "mass": 18.95, "orientation": "O", "title": "Gabriel, a=0.75"},
    {"a": 1.00,  "file": "DATA/Gabriel/OrientationO/PC216G3D_Gabriel_1.5mm_75mm_a1.00_OrientationO.csv",   "load": 36, "mass": 15.50, "orientation": "O", "title": "Gabriel, a=1.0"},
]

# Voronoi combines both orientations found on disk. Orientation O masses/loads come from
# script-cycle-V.py; Orientation 1 loads come from script-cycle.py. script-cycle.py has no
# distinct Orientation 1 masses (it reused the OrientationO values for matching a), so we do
# the same here -- swap these in if real Orientation 1 masses become available.
voronoi_datasets = [
    {"a": 0.001, "file": "DATA/Voronoi/OrientationO/PC216M3Db_Voronoi_a0_OrientationO_1.csv",              "load": 38, "mass": 12.05, "orientation": "O", "title": "Voronoi, a=0.001, Orientation O"},
    {"a": 0.125, "file": "DATA/Voronoi/OrientationO/PC216V3D_Voronoi_1.5mm_75mm_a0.125_OrientationO.csv",  "load": 36, "mass": 15.93, "orientation": "O", "title": "Voronoi, a=0.125, Orientation O"},
    {"a": 0.25,  "file": "DATA/Voronoi/OrientationO/PC216V3D_Voronoi_1.5mm_75mm_a0.25_OrientationO.csv",   "load": 36, "mass": 17.26, "orientation": "O", "title": "Voronoi, a=0.25, Orientation O"},
    {"a": 0.5,   "file": "DATA/Voronoi/OrientationO/PC216V3D_Voronoi_1.5mm_75mm_a0.5_OrientationO.csv",    "load": 36, "mass": 17.58, "orientation": "O", "title": "Voronoi, a=0.5, Orientation O"},
    {"a": 0.75,  "file": "DATA/Voronoi/OrientationO/PC216V3D_Voronoi_1.5mm_75mm_a0.75_OrientationO.csv",   "load": 44, "mass": 17.85, "orientation": "O", "title": "Voronoi, a=0.75, Orientation O"},
    {"a": 1.00,  "file": "DATA/Voronoi/OrientationO/PC216V3D_Voronoi_1.5mm_75mm_a1_OrientationO.csv",      "load": 36, "mass": 18.25, "orientation": "O", "title": "Voronoi, a=1.0, Orientation O"},

    {"a": 0.25,  "file": "DATA/Voronoi/Orientation1/PC216V3D_Voronoi_1.5mm_75mm_a0.25_Orientation1.csv",   "load": 36, "mass": 17.26, "orientation": "1", "title": "Voronoi, a=0.25, Orientation 1"},
    {"a": 0.5,   "file": "DATA/Voronoi/Orientation1/PC216V3D_Voronoi_1.5mm_75mm_a0.5_Orientation1.csv",    "load": 36, "mass": 17.58, "orientation": "1", "title": "Voronoi, a=0.5, Orientation 1"},
    {"a": 0.75,  "file": "DATA/Voronoi/Orientation1/PC216V3D_Voronoi_1.5mm_75mm_a0.75_Orientation1.csv",   "load": 76, "mass": 17.85, "orientation": "1", "title": "Voronoi, a=0.75, Orientation 1"},
    {"a": 1.00,  "file": "DATA/Voronoi/Orientation1/PC216V3D_Voronoi_1.5mm_75mm_a1_Orientation1.csv",      "load": 47, "mass": 18.25, "orientation": "1", "title": "Voronoi, a=1.0, Orientation 1"},

    # Mass reused from the O/1 orientation sample at a=0.25 (orientation doesn't affect mass).
    {"a": 0.25,  "file": "DATA/Voronoi/OrientationN/PC216V3D_Voronoi_1.5mm_75mm_a0.25_OrientationN.csv",   "load": 36, "mass": 17.26, "orientation": "N", "title": "Voronoi, a=0.25, Orientation N"},
]

TESSELATION_DATASETS = {
    "C": centroidal_datasets,
    "D": delaunay_datasets,
    "G": gabriel_datasets,
    "V": voronoi_datasets,
}

TESSELATION_NAMES = {
    "C": "Centroidal",
    "D": "Delaunay",
    "G": "Gabriel",
    "V": "Voronoi",
}
