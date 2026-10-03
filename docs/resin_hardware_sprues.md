# Resin hardware sprues

This corrects the scope of the earlier resin export. The requested sprues contain screws, bolts, nuts, washers and tube spacers from the metal hardware BOM. They do not contain the turbine's plastic housings, gears or fans.

Output: experiments/print_petg_12/output/stl/resin_hardware_sprues. The older plastic-body sprues are retained as an explicitly named earlier variation.

## Coverage

H01-H16 reproduce all 274 applicable hardware pieces: 105 screws/bolts, 124 nuts, 12 washers and 33 tube spacers. H00 adds four short screws and four nuts as thread-fit samples. The original 11 x608 bearings, 9 x604 bearings and 468 mm M8 main rod remain purchased parts; no segmented shaft or printed bearing redesign is implied.

Each individual item has an adjacent embossed size label on the sacrificial frame. The labels use DejaVu Sans Bold at 12-point equivalent CAD height (4.233 mm) and project 0.8 mm above the tag. File suffixes count complete sheet copies, with per-sheet item quantities in the manifest.

## Thread and fastener geometry

Right-hand helical threads are modeled as solids, with coarse pitches M2.5=0.45, M3=0.50, M4=0.70 and M8=1.25 mm. The profile is a truncated 60-degree approximation, not an ISO tolerance-class certification. Male radial offset is -0.025 mm; female cutting-tool offset is +0.075 mm, providing 0.10 mm radial prototype clearance.

Threads are generated directly as closed meshes from a periodic radial profile: 48 angular samples (64 for M8) and 24 axial steps per pitch. Manifold performs the unions and subtractions. This replaces the OCCT sweep approach, which silently lost some threads and produced unreliable overlap results. The 75 mm thread is continuous, without segment joins. Fastener and washer meshes are simplified by at most 0.002 mm; tube sheets retain their original tessellation. Exported meshes are then independently reloaded and checked in FreeCAD.

Head and nut dimensions follow the existing assembly envelopes. Screws have recessed hex drives. The M4 x10 button profile stays within the original 7.6 mm diameter / 2.2 mm head-height envelope. The M8 acorn prototype has an 8.5 mm blind thread depth and a closed dome. Spacer bores, outside diameters and lengths match the hardware list; washer geometry is explicit.

## Use and verification

These are resin fit-test copies. They are not equivalent to loaded metal screws, steel bearing axles or steel spacer stacks. The original metal hardware remains the operating configuration. H00 must be printed and checked after the intended curing workflow before committing to the complete hardware set.

Sprue necks attach to head faces, nut end faces, washer faces or tube end faces. Additional print supports and layer inspection are required. The sprue frame alone is not a validated support layout.

The generator checks valid Manifold solids, closed single-component STL meshes, M5s bed envelopes and exact BOM quantities. Four screw/nut pairs are checked for zero nominal overlap at 0, 90 and 180 degrees with pitch-matched axial travel. The CAD viewer document contains mesh objects; regenerate dimensions through mesh_build.py. The packager verifies file hashes, label counts/sizes, complete hardware quantities and ZIP byte contents.

Run python3 experiments/resin_hardware_sprues/launch.py in WSL. The generator uses the WSL virtual environment ~/.cache/angularmomflyer/meshchecks with the dependencies in requirements.txt. FreeCAD closes after preview generation. The --render-only option reuses exported geometry. Primary thread and printer references are linked in the output README.
