"""
gen_data.py - generate every map-local binary the i3d references, from scratch via tools/binfmt.py.
Flat DEM + uniform grass weight + blank densities + blank infolayers. See docs 40/41/50/51. Nothing copied.
Resolutions/headers are the verified 16x-map values (docs/31_terrain_node.md).
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
import binfmt

# --- the 100ha owned wheat field, dead centre ----------------------------------------------------------------
FIELD_HALF = 500          # 100 ha = 1000 x 1000 m field, centred on the origin
WHEAT = 7 | (7 << 5)      # fruits packed value: typeIdx 7 (wheat) | state 7 (harvest-ready) = 231
GROUND_SOWN = 7           # terrainDetail groundType 7 = sown (the tilled/sown dirt under the crop)


def _sq(res, half_m, inset_m=0):
    """Centred-square pixel slice at a .gdm/.grle resolution (8192 m map). inset_m shrinks it (the workable area)."""
    ppm = res / 8192.0; c = res // 2; h = int((half_m - inset_m) * ppm)
    return slice(c - h, c + h)


def build(data_dir):
    os.makedirs(data_dir, exist_ok=True)
    P = lambda f: os.path.join(data_dir, f)

    # DEM: 4097^2 16-bit, FLAT at an even medium-low height. value 8000 -> 8000/65535*255 ~= 31 m. undulation=0 =
    # truly flat: safe now that the terrain builds with the full layer/foliage structure (the occluder crash was
    # the missing OccluderLods + layer block, never flatness - see the corpus).
    binfmt.flat_dem(P("map_dem.png"), 4097, 8000, undulation=0)

    # grass01 layer weight = 255 everywhere (grass covers the map); every OTHER of the 86 standard layers
    # shares one blank (0) weight so it's hidden. (8192^2, 8-bit)
    binfmt.uniform_weight(P("grass_weight.png"), 8192, 255)
    binfmt.uniform_weight(P("blank_weight.png"), 8192, 0)

    # densities (16384^2). ground + fruits carry the 100ha field (workable area = 1 m inset from the polygon); the
    # rest of the map is blank. Everything else stays blank.
    N = 16384; wa = _sq(N, FIELD_HALF, inset_m=1)
    ground = np.zeros((N, N), np.uint16); ground[wa, wa] = GROUND_SOWN
    binfmt.paint_gdm(P("densityMap_ground.gdm"), N, ground, 11, 1, 0)
    # height is 2-range, split 0-5 / 6-11 (terrainDetailHeight compressionChannels=6) -> range_splits=(6,)
    binfmt.blank_gdm(P("densityMap_height.gdm"), 16384, num_channels=12, num_ranges=2, num_type_index_channels=0,
                     range_splits=(6,))
    # FoliageSystem densities (blank = nothing planted). Channels/ranges match the base-game mapUS FMLs.
    binfmt.blank_gdm(P("densityMap_groundFoliage.gdm"), 16384, num_channels=4, num_ranges=1, num_type_index_channels=0)
    fruits = np.zeros((N, N), np.uint16); fruits[wa, wa] = WHEAT     # wheat, harvest-ready, across the workable area
    binfmt.paint_gdm(P("densityMap_fruits.gdm"), N, fruits, 10, 2, 5, range_splits=(5,))
    binfmt.blank_gdm(P("densityMap_weed.gdm"), 16384, num_channels=4, num_ranges=1, num_type_index_channels=0)
    binfmt.blank_gdm(P("densityMap_stones.gdm"), 16384, num_channels=3, num_ranges=1, num_type_index_channels=0)

    # farmland: the 100ha field = farmland 1 (owned via defaultFarmProperty); the rest of the map = farmland 2
    # (buyable). A farmland's definition needs pixels or it's skipped ("Farmland-Id not defined") -> no owned land.
    farm = np.full((4096, 4096), 2, np.uint8); ff = _sq(4096, FIELD_HALF); farm[ff, ff] = 1
    binfmt.paint_grle(P("infoLayer_farmland.grle"), farm)
    binfmt.blank_grle(P("infoLayer_fieldType.grle"), 4096)   # blank = no fields
    # collision/mask infolayers - resolutions MUST match the base game (verified against Kansas). tipCollision at
    # 2048 caused "DensityMapHeightUpdater collision map with invalid size (8388608 vs 536870912)" - it must be
    # 16384 (16384^2 x2 = 536870912). Each layer has its own resolution.
    for f, res in (("infoLayer_indoorMask.grle", 16384), ("infoLayer_navigationCollision.grle", 8192),
                   ("infoLayer_tipCollision.grle", 16384), ("infoLayer_tipCollisionGenerated.grle", 16384),
                   ("infoLayer_placementCollision.grle", 4096), ("infoLayer_placementCollisionGenerated.grle", 4096)):
        binfmt.blank_grle(P(f), res)

    print(f"gen_data: flat DEM + grass weight + 2 blank densities + 8 blank infolayers -> {data_dir}")
