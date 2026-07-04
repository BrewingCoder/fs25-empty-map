"""
build.py - assemble the empty flat 16x map: run every generator into out/FS25_Empty16x/, verify the i3d's local
file refs all exist, then report. Symlink to the FS25 mods folder separately.
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gen_i3d, gen_data, gen_configs

OUT  = os.path.abspath(os.path.join(HERE, "..", "out", "FS25_Empty16x"))
MAPS = os.path.join(OUT, "maps")
DATA = os.path.join(MAPS, "data")


def main():
    os.makedirs(DATA, exist_ok=True)
    local = gen_i3d.build(os.path.join(MAPS, "empty16x.i3d"))   # returns the map-local files it references
    gen_data.build(DATA)
    gen_configs.build(OUT, MAPS)
    # verify every map-local file the i3d references now exists on disk
    missing = [f for f in local if not os.path.exists(os.path.join(MAPS, f.replace("/", os.sep)))]
    print(f"\nbuild -> {OUT}")
    print("local files referenced by i3d:", len(local), "| MISSING:", missing or "none")


if __name__ == "__main__":
    main()
