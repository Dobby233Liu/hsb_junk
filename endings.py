import math
import os
import hacktools
import hacktools.nitro as nitro
from tqdm import tqdm


regions = ["JP", "EU"]


characters_int_order = [
    {"JP": "Mio", "EU": "Alyssa"},
    {"JP": "Kanami", "EU": "Gabrielle"},
    {"JP": "Mahiru", "EU": "Kelly"},
    {"JP": "Riko", "EU": "Madison"},
]
characters = [
    {"JP": "Mahiru", "EU": "Kelly"},
    {"JP": "Kanami", "EU": "Alyssa"},
    {"JP": "Mio", "EU": "Madison"},
    {"JP": "Riko", "EU": "Gabrielle"},
]
# oops
character_names_broken_compat = False
character_names_broken = [
    "Kelly",
    "Madison",
    "Gabrielle",
    "Alyssa",
]


ending_types = ["Bad", "Normal", "Good"]


orig_fn_format = "en{i:02}"
fn_format = "PrincessOnIce {region} Ending {character} {type}.png"


wikitables_outer = \
"""<div style="text-align: center">
{0}
</div>"""
wikitable_skeleton = \
"""{{| class="wikitable" style="display: inline-table"
|+ {character[EU]}/{character[JP]}
! Europe/US !! Japan
{rows}
|}}"""
wikitable_row = \
"""|-
| {files}"""
wikitable_col = "[[File:{filename}|256px|{type} Ending]]"
wikitable_col_sep = " || "


def gen_fns(region):
    i = 1
    for character in characters_int_order:
        for ending_type in ending_types:
            yield orig_fn_format.format(i=i), fn_format.format(
                region=region,
                character=character[region],
                type=ending_type
            )
            i = i + 1


def gen_wikitables():
    wikitables = []

    for char_i, character in enumerate(characters):
        rows = []
        for ending_type in ending_types:
            files = []
            for region in regions:
                character_name_broken = character[region]
                if character_names_broken_compat and region == "EU":
                    character_name_broken = character_names_broken[char_i]
                files.append(wikitable_col.format(
                    filename=fn_format.format(
                        region=region,
                        character=character_name_broken,
                        type=ending_type
                    ),
                    type=ending_type
                ))

            rows.append(wikitable_row.format(
                files=wikitable_col_sep.join(files)
            ))

        wikitables.append(wikitable_skeleton.format(
            character=character,
            rows="\n".join(rows)
        ))
    
    return wikitables_outer.format("\n".join(wikitables))


import os
os.chdir("C:\\Users\\Dobby\\Downloads\\deltawarriors_lightnerinicepalace\\endings")


image_dirs = {
    "JP": "../poi_jp/bg",
    "EU": "../poi_eu/bg"
}


def proc_images():
    # the original code drew the palette aside the image??
    def drawNCGR(outfile, nscr, ncgr, palettes, width, height, usetransp=True):
        try:
            from PIL import Image
        except ImportError:
            hacktools.common.logError("PIL not found")
            return
        if width == 0xffff or height == 0xffff:
            root = int(math.sqrt(len(ncgr.tiles)))
            if math.pow(root, 2) == len(ncgr.tiles):
                width = height = root * ncgr.tilesize
                hacktools.common.logWarning("Assuming square size", width, "for", outfile)
            else:
                hacktools.common.logError("Wrong width/height", width, height, "for", outfile)
                return
        img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        pixels = img.load()
        x = 0
        for i in range(height // ncgr.tilesize):
            for j in range(width // ncgr.tilesize):
                if nscr is not None:
                    map = nscr.maps[x]
                    if map.pal in palettes.keys():
                        pali = 0
                        palette = palettes[map.pal]
                    else:
                        pali = map.pal * 16
                        palette = palettes[0]
                    pixels = hacktools.nitro.tileToPixels(pixels, width, ncgr, map.tile, map.xflip, map.yflip, i, j, palette, pali, usetransp)
                else:
                    pixels = hacktools.nitro.tileToPixels(pixels, width, ncgr, x, False, False, i, j, palettes[0], 0, usetransp)
                x += 1
        img.save(outfile, "PNG")

    for region, in_dir in image_dirs.items():
        for orig_fn, out_fn in (pbar := tqdm(gen_fns(region), desc=region, unit="image")):
            pbar.set_description(f"{region} {out_fn}")
            orig_path = os.path.join(in_dir, orig_fn)
            palettes, image, map, _, width, height = nitro.readNitroGraphic(f"{orig_path}.NCLR", f"{orig_path}.NCGR", f"{orig_path}.NSCR", "")
            assert image
            drawNCGR(out_fn, map, image, palettes, width, height)


def proc_wikitable():
    with open(f"table.mediawiki", "w") as tables_out:
        tables_out.write(gen_wikitables())


proc_images()
proc_wikitable()