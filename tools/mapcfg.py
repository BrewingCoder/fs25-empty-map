"""
Map-size configuration. EVERYTHING scales from MAP_M (map size in metres). Ratios verified from the working 16x
build (see the corpus). A 16x FS25 map = 8192 m; a 4x map = 4096 m (unitsPerPixel stays 2).

Only resolutions scale. Terrain attributes (patchSize 65, heightScale 255, the occluder set, the standard layer
block, the foliage system) and absolute-metre things (the 100ha field, the sun, spawn) are size-INDEPENDENT.
"""


class Cfg:
    UNITS_PER_PIXEL = 2

    def __init__(self, map_m, name, tag):
        self.map_m = map_m                                   # 8192 (16x) / 4096 (4x); map.xml width/height
        self.name = name                                     # "Empty16x" - map id
        self.mod = f"FS25_{name}"                            # FS25_Empty16x - mod folder
        self.i3d = f"{name.lower()}.i3d"                     # empty16x.i3d
        self.title = f"Empty {tag}"                          # "Empty 16x"
        self.dem_res = map_m // self.UNITS_PER_PIXEL + 1     # 4097 for 8192 (patch edges share -> +1)
        self.weight_res = map_m                              # 8192 (1 px/m)
        self.density_res = map_m * 2                         # 16384 (2 px/m); .gdm mapSizeLog = log2-5
        self.overview_res = map_m                            # 8192 (1 px/m)
        self.disp_size = self.density_res                    # DisplacementLayer size = density res
        d = self.density_res                                 # infolayer .grle resolutions (verified vs Kansas)
        self.il_res = {"indoorMask": d, "tipCollision": d, "tipCollisionGenerated": d,
                       "navigationCollision": d // 2,
                       "placementCollision": d // 4, "placementCollisionGenerated": d // 4,
                       "farmland": d // 4, "fieldType": d // 4}


CFG16 = Cfg(8192, "Empty16x", "16x")
CFG4 = Cfg(4096, "Empty4x", "4x")
