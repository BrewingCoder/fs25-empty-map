"""
gen_configs.py - map.xml, farmlands.xml, modDesc.xml, empty default vehicles/placeables/items, and a generated
icon. See docs/10_moddesc.md + docs/20_mapxml.md. Nothing copied from another map; $data sub-config refs are the
base-game engine defaults (environment/weed/fieldGround/aiSystem/npcs), which carry no map data.
"""
import os
from PIL import Image

MAP_XML = '''<?xml version="1.0" encoding="utf-8" standalone="no" ?>
<map width="8192" height="8192" imageFilename="maps/overview.png" mapFieldColor="0.1500 0.1195 0.0953" mapGrassFieldColor="0.1470 0.1441 0.0823">
    <filename>maps/empty16x.i3d</filename>
    <sounds filename="$data/maps/mapUS/sounds/sounds.xml" />
    <environment filename="$data/maps/mapUS/config/environment.xml" />
    <weed filename="$data/maps/mapUS/config/weed.xml" />
    <fieldGround filename="$data/maps/mapUS/config/fieldGround.xml" />
    <farmlands filename="maps/farmlands.xml" />
    <aiSystem filename="$data/maps/mapUS/config/aiSystem.xml" />
    <npcs filename="$data/maps/maps_npcs.xml" />
    <missions vehicleFilename="$dataS/missionVehicles.xml" />
</map>
'''

FARMLANDS_XML = '''<?xml version="1.0" encoding="utf-8" standalone="no" ?>
<map>
    <farmlands infoLayer="farmlands" pricePerHa="60000">
        <farmland id="1" priceScale="1" defaultFarmProperty="true" />
        <farmland id="2" priceScale="1" npcName="FORESTER" />
    </farmlands>
</map>
'''

MODDESC = '''<?xml version="1.0" encoding="utf-8" standalone="no" ?>
<modDesc descVersion="{descVersion}">
    <author>fs25-empty-map</author>
    <version>1.0.0.0</version>
    <title><en>Empty 16x</en></title>
    <description><en>A completely empty flat 16x map, generated 100% from scratch.</en></description>
    <iconFilename>icon.dds</iconFilename>
    <maps>
        <map id="Empty16x" className="Mission00" filename="$dataS/scripts/mission00.lua" configFilename="maps/map.xml" defaultVehiclesXMLFilename="maps/vehicles.xml" defaultPlaceablesXMLFilename="maps/placeables.xml" defaultItemsXMLFilename="maps/items.xml" defaultHandToolsXMLFilename="$data/maps/mapUS/config/handTools.xml">
            <title><en>Empty 16x</en></title>
            <iconFilename>icon.dds</iconFilename>
        </map>
    </maps>
</modDesc>
'''


def _w(path, text):
    open(path, "w", encoding="utf-8").write(text)


def build(mod_dir, maps_dir, desc_version="100"):
    _w(os.path.join(maps_dir, "map.xml"), MAP_XML)
    # map overview image: the game does NOT render the map top-down at runtime - it DISPLAYS this static image and
    # overlays fields/graph/icons on top (external tools like AutoDrive Editor read this same file to show the map).
    # It must match the map layout: 8192x8192 (1 px per metre) for a 16x map. Empty grass map = solid grass green.
    Image.new("RGB", (8192, 8192), (72, 88, 48)).save(os.path.join(maps_dir, "overview.png"))
    _w(os.path.join(maps_dir, "farmlands.xml"), FARMLANDS_XML)
    # empty default start config (modDesc references these; empty = new farm starts with nothing)
    for name, root in (("vehicles", "vehicles"), ("placeables", "placeables"), ("items", "items")):
        _w(os.path.join(maps_dir, name + ".xml"),
           f'<?xml version="1.0" encoding="utf-8" standalone="no" ?>\n<{root}></{root}>\n')
    _w(os.path.join(mod_dir, "modDesc.xml"), MODDESC.format(descVersion=desc_version))
    # generated icon (solid green) - the mod-list preview. PIL writes uncompressed DDS.
    ok = "ok"
    try:
        Image.new("RGBA", (256, 256), (54, 110, 40, 255)).save(os.path.join(mod_dir, "icon.dds"))
    except Exception as e:
        ok = f"icon.dds FAILED ({e}) - non-blocking cosmetic"
    print(f"gen_configs: map.xml, farmlands.xml, modDesc.xml (descVersion={desc_version}), "
          f"empty vehicles/placeables/items, icon.dds [{ok}]")
