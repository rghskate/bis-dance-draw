from importlib.metadata import version
from numpy import random
from datetime import datetime
from markdown_pdf import MarkdownPdf, Section
import json
import argparse
import os
import sys

def recursive_sum(node:dict|int):
    if isinstance(node, int):
        return node
    elif isinstance(node, dict):
        return sum(recursive_sum(child) for child in node.values())
    return 0

def sum_child_values(data:dict, level=None):
    """
    Recursively computes the sum of all integer values starting at a given level in a nested dictionary.
    
    Args:
        data (dict): The nested dictionary.
        level (str): The key at which to start the sum. If None, starts at the root of the dictionary.

    Returns:
        int: The sum of all integer values in the child nodes.
    """
    if level is None:
        return recursive_sum(data)
    
    if level in data:
        return recursive_sum(data[level])
    else:
        for value in data.values():
            if isinstance(value, dict):
                result = sum_child_values(value, level)
                if result is not None:
                    return result
    return None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('DANCES',help='JSON file containing all dances for current season. See repo for examples.')
    parser.add_argument('COMPETITION',help='JSON file containing the number of dances to be drawn in each category.')
    parser.add_argument('OUTPUT_FOLDER',help='Folder to output generated draw to. File is named automatically after the random seed used.')
    parser.add_argument('COMPETITION_NAME',help='Name for the competition. Any strings containing spaces must be wrapped in " marks.')
    parser.add_argument('--force-seed','-f',help='Manually provide a seed to replicate a given draw.')
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
        random_int = seed_randomiser.integers(0,100)
        seed = (int(now.strftime("%d%m%Y%H%M%S"))/20)*random_int
    else:
        seed = forced_seed
    seed=int(seed)

    generator = random.Generator(random.PCG64(seed=seed))

    with open(current_dances_filepath, 'r') as f:
        all_dances:dict = json.load(f)
    with open(competition_filepath, 'r') as f:
        competition:dict = json.load(f)

    master_string = []
    loop_string = []

    for cat_type, supercategory in competition.items():
        if sum_child_values(supercategory) != 0:
            loop_string.append(f'## {cat_type}\n\n')
            for supercategory_name, category in supercategory.items():
                if sum_child_values(category) != 0:
                    loop_string.append(f'### {supercategory_name}\n\n')
                    for category_name, no_of_dances in category.items():
                            if no_of_dances != 0:
                                available_dances = all_dances.get(cat_type).get(supercategory_name).get(category_name)
                                drawn_dances = [f'1. {dance_name}' for dance_name in generator.choice(available_dances, no_of_dances, replace=False)]
                                drawn_dance_list = '\n'.join(drawn_dances)
                                loop_string.append(f'#### {category_name}\n{drawn_dance_list}\n')
            master_string.extend(loop_string)
        
    css = '''@font-face {
    font-family: Barlow;
    src: url('Barlow/Barlow-Regular.ttf');
    }
    body {font-family: Barlow,Arial}
    th {text-align: left; font-style: bold}
    img[alt=BIS_Logo]{width: 200px}
    '''

    technical_information = f'''# Technical Details

This draw was performed using draw.py, a Python program based on the following modules:

| Module | Version |
|---|---|
| `Numpy` | `{version("numpy")}` |
| `MarkdownPDF` | `{version("markdown_pdf")}` |
| `Pip` | `{version("pip")}` |

This program was run in the following environment:
- Python version: `{sys.version}`
- Python System platform: `{sys.platform}`
- Python OS Name: `{os.name}`
- Draw time: `{now}`
- Randomiser: `np.random.PCG64`
- Randomiser seed: `{seed}`

The code for this program can be found at [github.com/rghs/bis-dance-draw](https://github.com/rghs/bis-dance-draw)
    '''

    pdf = MarkdownPdf(toc_level=1)
    pdf.add_section(Section(f'![BIS_Logo](bis_logo.png)\n# Drawn dances for {args.COMPETITION_NAME.title()}\n{"".join(master_string)}',toc=True),
                            user_css=css)
    pdf.add_section(Section(technical_information,toc=True), user_css=css)

    pdf.meta['title'] = f'BIS Pattern Dance draws for {args.COMPETITION_NAME}'
    pdf.meta['author'] = f'British Ice Skating'
    pdf.meta['producer'] = f'British Ice Skating'
    pdf.save(os.path.join(out_folder,f'dance_draw_{args.COMPETITION_NAME.replace(' ', '_')}_seed_{seed}.pdf'))

if __name__ == '__main__':
    main()