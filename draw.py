from importlib.metadata import version
from numpy import random
from datetime import datetime
from markdown_pdf import MarkdownPdf, Section
import json
import argparse
import os
import sys
import hashlib


def calculate_totals(desired_dances: dict):
    totals = {
        "Solo Dance": {"National": 0, "Adults": 0},
        "Couples Dance": {"National": 0, "Adults": 0},
    }

    totals["Solo Dance"]["National"] = sum(
        desired_dances["Solo Dance"]["National"].values()
    )
    totals["Solo Dance"]["Adults"] = sum(
        desired_dances["Solo Dance"]["Adults"].values()
    )
    totals["Couples Dance"]["National"] = sum(
        desired_dances["Couples Dance"]["National"].values()
    )
    totals["Couples Dance"]["Adults"] = sum(
        desired_dances["Couples Dance"]["Adults"].values()
    )

    return totals


def choose_dances(
    dance_list: list, number_of_dances: int, generator: random.Generator
) -> list:
    chosen_dances = []
    numbered_dances = []

    x = 1
    for dance in dance_list:
        numbered_dances.append(f"{x:02d}||{dance}")
        x += 1

    selection = generator.choice(
        numbered_dances, size=number_of_dances, replace=False, shuffle=False
    )
    selection.sort()

    for dance in selection:
        chosen_dances.append(str(dance))

    chosen_dances = [x.split("||")[1] for x in chosen_dances]

    return chosen_dances


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "DANCES",
        help="JSON file containing all dances for current season. See repo for examples.",
    )
    parser.add_argument(
        "COMPETITION",
        help="JSON file containing the number of dances to be drawn in each category.",
    )
    parser.add_argument(
        "OUTPUT_FOLDER",
        help="Folder to output generated draw to. File is named automatically after the random seed used.",
    )
    parser.add_argument(
        "COMPETITION_NAME",
        help='Name for the competition. Any strings containing spaces must be wrapped in " marks.',
    )
    parser.add_argument(
        "--force-seed", "-f", help="Manually provide a seed to replicate a given draw."
    )
    args = parser.parse_args()

    current_dances_filepath = os.path.normpath(args.DANCES)
    competition_filepath = os.path.normpath(args.COMPETITION)
    out_folder = os.path.normpath(args.OUTPUT_FOLDER)

    if args.force_seed is not None:
        forced_seed = int(args.force_seed)
    else:
        forced_seed = None

    now = datetime.now()

    if forced_seed is None:
        seed_randomiser = random.default_rng()
        random_int = seed_randomiser.integers(0, 100)
        seed = (int(now.strftime("%d%m%Y%H%M%S")) / 20) * random_int
    else:
        seed = forced_seed
    seed = int(seed)

    generator = random.Generator(random.PCG64(seed=seed))

    with open(current_dances_filepath, "r") as f:
        all_dances: dict = json.load(f)
    with open(competition_filepath, "r") as f:
        competition: dict = json.load(f)

    totals = calculate_totals(competition)
    dance_choices = competition

    top_level_keys = ["Solo Dance", "Couples Dance"]
    second_level_keys = ["National", "Adults"]

    keys_to_pop = []

    for l1k in top_level_keys:
        for l2k in second_level_keys:
            if totals[l1k][l2k] != 0:
                for level in competition[l1k][l2k].keys():
                    if dance_choices[l1k][l2k][level] != 0:
                        dance_choices[l1k][l2k][level] = choose_dances(
                            all_dances[l1k][l2k][level],
                            competition[l1k][l2k][level],
                            generator,
                        )
                    else:
                        keys_to_pop.append([l1k, l2k, level])

            else:
                keys_to_pop.append([l1k, l2k])
        if dance_choices[l1k] == {}:
            keys_to_pop.append(l1k)

    for entry in keys_to_pop:
        if len(entry) == 1:
            try:
                dance_choices.pop(entry[0])
            except KeyError:
                pass
        elif len(entry) == 2:
            try:
                dance_choices[entry[0]].pop(entry[1])
            except KeyError:
                pass
        elif len(entry) == 3:
            try:
                dance_choices[entry[0]][entry[1]].pop(entry[2])
            except KeyError:
                pass

    master_string = []
    for discipline, age in dance_choices.items():
        master_string.append(f"## {discipline}\n\n")
        for age_designation, category in age.items():
            master_string.append(f"### {age_designation}\n\n")
            for category_name, drawn_dances in category.items():
                master_string.append(f"#### {category_name}\n\n")
                for dance in drawn_dances:
                    master_string.append(f"1. {dance}\n")
                master_string.append("\n")
    master_string = "".join(master_string)

    with open("style.css", "r") as f:
        css = f.read()

    with open("draw.py", "r") as f:
        self_hash_string = f.read()

    if forced_seed is None:
        seed_state = "Random"
    else:
        seed_state = "Forced"

    technical_information = f"""# Technical Details

This draw was performed using draw.py, a Python program based on the following modules:

| Module | Version |
|---|---|
| `Numpy` | `{version("numpy")}` |
| `MarkdownPDF` | `{version("markdown_pdf")}` |

This program was run in the following environment:
- Python version: `{sys.version}`
- Python System platform: `{sys.platform}`
- Python OS Name: `{os.name}`
- Draw time: `{now}`
- Randomiser: `np.random.PCG64`
- Randomiser seed: `{seed}`
- Seed state (random/forced): `{seed_state}`
- Program hash: `{hashlib.sha256(self_hash_string.encode("utf-8")).hexdigest()}`

The code for this program can be found at [github.com/rghskate/bis-dance-draw](https://github.com/rghskate/bis-dance-draw)
    """

    pdf = MarkdownPdf(toc_level=1)
    pdf.add_section(
        Section(
            f"![BIS_Logo](bis_logo.png)\n# Drawn dances for {args.COMPETITION_NAME.title()}\n{master_string}",
            toc=True,
        ),
        user_css=css,
    )
    pdf.add_section(Section(technical_information, toc=True), user_css=css)

    pdf.meta["title"] = f"BIS Pattern Dance draws for {args.COMPETITION_NAME}"
    pdf.meta["author"] = f"British Ice Skating"
    pdf.meta["producer"] = f"British Ice Skating"
    pdf.save(
        os.path.join(
            out_folder,
            f"dance_draw_{args.COMPETITION_NAME.replace(' ', '_')}_seed_{seed}.pdf",
        )
    )


if __name__ == "__main__":
    main()
