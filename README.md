# BIS Dance Draw Randomiser

A simple program to perform electronic draws for pattern dances at Ice Dance and Solo Dance events.

## Installation

Currently, no installer is provided for this program. The simplest way to install the program is to clone the repo and install the dependencies using the `uv` package manager. The below commands on a system with git and uv installed will get you up and running:

```bash
git clone https://github.com/rghskate/bis-dance-draw/
cd bis-dance-draw
uv run draw.py --help
```

## Using the program

The program requires two inputs formatted as `JSON` files: these files are a list of pattern dances for each discipline for the season, and a list for each competition of how many dances in each discipline and level are required. Examples of both are included later in the README.

The program will produce a markdown document with the desired selection of dances and convert this document into a PDF for distribution.

### Reproducing draws

The validity of a pattern dance draw can be verified by any third party wishing to do so simply by cloning the repository and input files and running the program with the `--force-seed` flag. Seeds for all pattern dance draws can be found in the produced PDF.

An example of the command is as follows:

```bash
python draw.py dance_lists/2526_dances.json competitions/2526/2509idqual_idadults.json . "Example competition" --force-seed 3732986713469
```

This command will recreate the `Example competition.pdf` in the current directory.

## Example input documents
### Pattern Dance list

```json
{
    "Solo Dance": {
        "National": {
            "Beginner": [
                "Novice Foxtrot",
                "Rhythm Blues"
            ],
            "Juvenile": [
                "Golden Skater's Waltz",
                "Tango Fiesta"
            ],
            "Basic Novice": [
                "Willow Waltz",
                "Tango Canasta"
            ],
            "Intermediate Novice": [
                "European Waltz",
                "Tango"
            ],
            "Advanced Novice": [
                "Starlight Waltz",
                "Quickstep Plus"
            ]
        },
        "Adults": {
            "Pre-Bronze": [
                "Novice Foxtrot",
                "Rhythm Blues"
            ],
            "Bronze": [
                "Willow Waltz",
                "Tango Canasta"
            ],
            "Silver": [
                "European Waltz",
                "Tango"
            ],
            "Gold": [
                "Starlight Waltz",
                "Quickstep Plus"
            ],
            "Masters": [
                "Starlight Waltz",
                "Quickstep Plus"
            ]
        }
    },
    "Couples Dance": {
        "National": {
            "Beginner": [
                "Novice Foxtrot",
                "Rhythm Blues"
            ],
            "Juvenile": [
                "Riverside Rhumba",
                "Tango Fiesta"
            ],
            "Basic Novice": [
                "Willow Waltz",
                "Tango Canasta",
                "Rhythm Blues"
            ],
            "Intermediate Novice": [
                "Rocker Foxtrot",
                "European Waltz",
                "Tango"
            ],
            "Advanced Novice": [
                "Starlight Waltz",
                "Quickstep Plus"
            ]
        },
        "Adults": {
            "Pre-Bronze": [
                "Novice Foxtrot",
                "Rhythm Blues"
            ],
            "Bronze": [
                "Willow Waltz",
                "Tango Fiesta"
            ],
            "Silver": [
                "American Waltz",
                "Tango"
            ],
            "Gold": [
                "Westminster Waltz",
                "Silver Samba"
            ],
            "Masters": [
                "Ravensburger Waltz",
                "Cha Cha Congelado"
            ]
        }
    }
}
```

### Dance quotas

```json
{
    "Solo Dance": {
        "National": {
            "Beginner": 1,
            "Juvenile": 1,
            "Basic Novice": 1,
            "Intermediate Novice": 1,
            "Advanced Novice": 1
        },
        "Adults": {
            "Pre-Bronze": 2,
            "Bronze": 2,
            "Silver": 2,
            "Gold": 2,
            "Masters": 0
        }
    },
    "Couples Dance": {
        "National": {
            "Beginner": 0,
            "Juvenile": 0,
            "Basic Novice": 0,
            "Intermediate Novice": 1,
            "Advanced Novice": 0
        },
        "Adults": {
            "Pre-Bronze": 2,
            "Bronze": 0,
            "Silver": 0,
            "Gold": 0,
            "Masters": 0
        }
    }
}
```

### Example

The included example file (`Example competition.pdf`), produced with the command seen earlier in the README (without the `--force-seed` flag), uses the JSON documents shown above.

## Program hash

The program calculates a SHA256 hash of the bytes of `draw.py` when it is run. The current version of the program, when unmodified, should produce the following checksum: `2c8b529d307a5006865534896c72335931873c1fde618866e2a4324844d021f4`.
