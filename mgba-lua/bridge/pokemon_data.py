"""
Static lookup tables for Pokemon FireRed / Gen III.
Species indexed by National Dex (Gen 3 internal index), moves by Gen 3 move index.
"""

SPECIES_NAMES = {
    0: "---",
    1: "Bulbasaur", 2: "Ivysaur", 3: "Venusaur", 4: "Charmander", 5: "Charmeleon",
    6: "Charizard", 7: "Squirtle", 8: "Wartortle", 9: "Blastoise", 10: "Caterpie",
    11: "Metapod", 12: "Butterfree", 13: "Weedle", 14: "Kakuna", 15: "Beedrill",
    16: "Pidgey", 17: "Pidgeotto", 18: "Pidgeot", 19: "Rattata", 20: "Raticate",
    21: "Spearow", 22: "Fearow", 23: "Ekans", 24: "Arbok", 25: "Pikachu",
    26: "Raichu", 27: "Sandshrew", 28: "Sandslash", 29: "Nidoran-F", 30: "Nidorina",
    31: "Nidoqueen", 32: "Nidoran-M", 33: "Nidorino", 34: "Nidoking", 35: "Clefairy",
    36: "Clefable", 37: "Vulpix", 38: "Ninetales", 39: "Jigglypuff", 40: "Wigglytuff",
    41: "Zubat", 42: "Golbat", 43: "Oddish", 44: "Gloom", 45: "Vileplume",
    46: "Paras", 47: "Parasect", 48: "Venonat", 49: "Venomoth", 50: "Diglett",
    51: "Dugtrio", 52: "Meowth", 53: "Persian", 54: "Psyduck", 55: "Golduck",
    56: "Mankey", 57: "Primeape", 58: "Growlithe", 59: "Arcanine", 60: "Poliwag",
    61: "Poliwhirl", 62: "Poliwrath", 63: "Abra", 64: "Kadabra", 65: "Alakazam",
    66: "Machop", 67: "Machoke", 68: "Machamp", 69: "Bellsprout", 70: "Weepinbell",
    71: "Victreebel", 72: "Tentacool", 73: "Tentacruel", 74: "Geodude", 75: "Graveler",
    76: "Golem", 77: "Ponyta", 78: "Rapidash", 79: "Slowpoke", 80: "Slowbro",
    81: "Magnemite", 82: "Magneton", 83: "Farfetch'd", 84: "Doduo", 85: "Dodrio",
    86: "Seel", 87: "Dewgong", 88: "Grimer", 89: "Muk", 90: "Shellder",
    91: "Cloyster", 92: "Gastly", 93: "Haunter", 94: "Gengar", 95: "Onix",
    96: "Drowzee", 97: "Hypno", 98: "Krabby", 99: "Kingler", 100: "Voltorb",
    101: "Electrode", 102: "Exeggcute", 103: "Exeggutor", 104: "Cubone", 105: "Marowak",
    106: "Hitmonlee", 107: "Hitmonchan", 108: "Lickitung", 109: "Koffing", 110: "Weezing",
    111: "Rhyhorn", 112: "Rhydon", 113: "Chansey", 114: "Tangela", 115: "Kangaskhan",
    116: "Horsea", 117: "Seadra", 118: "Goldeen", 119: "Seaking", 120: "Staryu",
    121: "Starmie", 122: "Mr. Mime", 123: "Scyther", 124: "Jynx", 125: "Electabuzz",
    126: "Magmar", 127: "Pinsir", 128: "Tauros", 129: "Magikarp", 130: "Gyarados",
    131: "Lapras", 132: "Ditto", 133: "Eevee", 134: "Vaporeon", 135: "Jolteon",
    136: "Flareon", 137: "Porygon", 138: "Omanyte", 139: "Omastar", 140: "Kabuto",
    141: "Kabutops", 142: "Aerodactyl", 143: "Snorlax", 144: "Articuno", 145: "Zapdos",
    146: "Moltres", 147: "Dratini", 148: "Dragonair", 149: "Dragonite", 150: "Mewtwo",
    151: "Mew", 152: "Chikorita", 153: "Bayleef", 154: "Meganium", 155: "Cyndaquil",
    156: "Quilava", 157: "Typhlosion", 158: "Totodile", 159: "Croconaw", 160: "Feraligatr",
    161: "Sentret", 162: "Furret", 163: "Hoothoot", 164: "Noctowl", 165: "Ledyba",
    166: "Ledian", 167: "Spinarak", 168: "Ariados", 169: "Crobat", 170: "Chinchou",
    171: "Lanturn", 172: "Pichu", 173: "Cleffa", 174: "Igglybuff", 175: "Togepi",
    176: "Togetic", 177: "Natu", 178: "Xatu", 179: "Mareep", 180: "Flaaffy",
    181: "Ampharos", 182: "Bellossom", 183: "Marill", 184: "Azumarill", 185: "Sudowoodo",
    186: "Politoed", 187: "Hoppip", 188: "Skiploom", 189: "Jumpluff", 190: "Aipom",
    191: "Sunkern", 192: "Sunflora", 193: "Yanma", 194: "Wooper", 195: "Quagsire",
    196: "Espeon", 197: "Umbreon", 198: "Murkrow", 199: "Slowking", 200: "Misdreavus",
    201: "Unown", 202: "Wobbuffet", 203: "Girafarig", 204: "Pineco", 205: "Forretress",
    206: "Dunsparce", 207: "Gligar", 208: "Steelix", 209: "Snubbull", 210: "Granbull",
    211: "Qwilfish", 212: "Scizor", 213: "Shuckle", 214: "Heracross", 215: "Sneasel",
    216: "Teddiursa", 217: "Ursaring", 218: "Slugma", 219: "Magcargo", 220: "Swinub",
    221: "Piloswine", 222: "Corsola", 223: "Remoraid", 224: "Octillery", 225: "Delibird",
    226: "Mantine", 227: "Skarmory", 228: "Houndour", 229: "Houndoom", 230: "Kingdra",
    231: "Phanpy", 232: "Donphan", 233: "Porygon2", 234: "Stantler", 235: "Smeargle",
    236: "Tyrogue", 237: "Hitmontop", 238: "Smoochum", 239: "Elekid", 240: "Magby",
    241: "Miltank", 242: "Blissey", 243: "Raikou", 244: "Entei", 245: "Suicune",
    246: "Larvitar", 247: "Pupitar", 248: "Tyranitar", 249: "Lugia", 250: "Ho-Oh",
    251: "Celebi", 252: "Treecko", 253: "Grovyle", 254: "Sceptile", 255: "Torchic",
    256: "Combusken", 257: "Blaziken", 258: "Mudkip", 259: "Marshtomp", 260: "Swampert",
    261: "Poochyena", 262: "Mightyena", 263: "Zigzagoon", 264: "Linoone", 265: "Wurmple",
    266: "Silcoon", 267: "Beautifly", 268: "Cascoon", 269: "Dustox", 270: "Lotad",
    271: "Lombre", 272: "Ludicolo", 273: "Seedot", 274: "Nuzleaf", 275: "Shiftry",
    276: "Taillow", 277: "Swellow", 278: "Wingull", 279: "Pelipper", 280: "Ralts",
    281: "Kirlia", 282: "Gardevoir", 283: "Surskit", 284: "Masquerain", 285: "Shroomish",
    286: "Breloom", 287: "Slakoth", 288: "Vigoroth", 289: "Slaking", 290: "Nincada",
    291: "Ninjask", 292: "Shedinja", 293: "Whismur", 294: "Loudred", 295: "Exploud",
    296: "Makuhita", 297: "Hariyama", 298: "Azurill", 299: "Nosepass", 300: "Skitty",
    301: "Delcatty", 302: "Sableye", 303: "Mawile", 304: "Aron", 305: "Lairon",
    306: "Aggron", 307: "Meditite", 308: "Medicham", 309: "Electrike", 310: "Manectric",
    311: "Plusle", 312: "Minun", 313: "Volbeat", 314: "Illumise", 315: "Roselia",
    316: "Gulpin", 317: "Swalot", 318: "Carvanha", 319: "Sharpedo", 320: "Wailmer",
    321: "Wailord", 322: "Numel", 323: "Camerupt", 324: "Torkoal", 325: "Spoink",
    326: "Grumpig", 327: "Spinda", 328: "Trapinch", 329: "Vibrava", 330: "Flygon",
    331: "Cacnea", 332: "Cacturne", 333: "Swablu", 334: "Altaria", 335: "Zangoose",
    336: "Seviper", 337: "Lunatone", 338: "Solrock", 339: "Barboach", 340: "Whiscash",
    341: "Corphish", 342: "Crawdaunt", 343: "Baltoy", 344: "Claydol", 345: "Lileep",
    346: "Cradily", 347: "Anorith", 348: "Armaldo", 349: "Feebas", 350: "Milotic",
    351: "Castform", 352: "Kecleon", 353: "Shuppet", 354: "Banette", 355: "Duskull",
    356: "Dusclops", 357: "Tropius", 358: "Chimecho", 359: "Absol", 360: "Wynaut",
    361: "Snorunt", 362: "Glalie", 363: "Spheal", 364: "Sealeo", 365: "Walrein",
    366: "Clamperl", 367: "Huntail", 368: "Gorebyss", 369: "Relicanth", 370: "Luvdisc",
    371: "Bagon", 372: "Shelgon", 373: "Salamence", 374: "Beldum", 375: "Metang",
    376: "Metagross", 377: "Regirock", 378: "Regice", 379: "Registeel", 380: "Latias",
    381: "Latios", 382: "Kyogre", 383: "Groudon", 384: "Rayquaza", 385: "Jirachi",
    386: "Deoxys",
}

TYPE_NAMES = [
    "Normal", "Fighting", "Flying", "Poison", "Ground", "Rock",
    "Bug", "Ghost", "Steel", "???",
    "Fire", "Water", "Grass", "Electric", "Psychic", "Ice",
    "Dragon", "Dark",
]

MOVE_DATA = {
    0: ("---", "Normal"),
    1: ("Pound", "Normal"), 2: ("Karate Chop", "Fighting"), 3: ("Double Slap", "Normal"),
    4: ("Comet Punch", "Normal"), 5: ("Mega Punch", "Normal"), 6: ("Pay Day", "Normal"),
    7: ("Fire Punch", "Fire"), 8: ("Ice Punch", "Ice"), 9: ("Thunder Punch", "Electric"),
    10: ("Scratch", "Normal"), 11: ("Vice Grip", "Normal"), 12: ("Guillotine", "Normal"),
    13: ("Razor Wind", "Normal"), 14: ("Swords Dance", "Normal"), 15: ("Cut", "Normal"),
    16: ("Gust", "Flying"), 17: ("Wing Attack", "Flying"), 18: ("Whirlwind", "Normal"),
    19: ("Fly", "Flying"), 20: ("Bind", "Normal"), 21: ("Slam", "Normal"),
    22: ("Vine Whip", "Grass"), 23: ("Stomp", "Normal"), 24: ("Double Kick", "Fighting"),
    25: ("Mega Kick", "Normal"), 26: ("Jump Kick", "Fighting"), 27: ("Rolling Kick", "Fighting"),
    28: ("Sand Attack", "Ground"), 29: ("Headbutt", "Normal"), 30: ("Horn Attack", "Normal"),
    31: ("Fury Attack", "Normal"), 32: ("Horn Drill", "Normal"), 33: ("Tackle", "Normal"),
    34: ("Body Slam", "Normal"), 35: ("Wrap", "Normal"), 36: ("Take Down", "Normal"),
    37: ("Thrash", "Normal"), 38: ("Double-Edge", "Normal"), 39: ("Tail Whip", "Normal"),
    40: ("Poison Sting", "Poison"), 41: ("Twineedle", "Bug"), 42: ("Pin Missile", "Bug"),
    43: ("Leer", "Normal"), 44: ("Bite", "Dark"), 45: ("Growl", "Normal"),
    46: ("Roar", "Normal"), 47: ("Sing", "Normal"), 48: ("Supersonic", "Normal"),
    49: ("Sonic Boom", "Normal"), 50: ("Disable", "Normal"), 51: ("Acid", "Poison"),
    52: ("Ember", "Fire"), 53: ("Flamethrower", "Fire"), 54: ("Mist", "Ice"),
    55: ("Water Gun", "Water"), 56: ("Hydro Pump", "Water"), 57: ("Surf", "Water"),
    58: ("Ice Beam", "Ice"), 59: ("Blizzard", "Ice"), 60: ("Psybeam", "Psychic"),
    61: ("Bubble Beam", "Water"), 62: ("Aurora Beam", "Ice"), 63: ("Hyper Beam", "Normal"),
    64: ("Peck", "Flying"), 65: ("Drill Peck", "Flying"), 66: ("Submission", "Fighting"),
    67: ("Low Kick", "Fighting"), 68: ("Counter", "Fighting"), 69: ("Seismic Toss", "Fighting"),
    70: ("Strength", "Normal"), 71: ("Absorb", "Grass"), 72: ("Mega Drain", "Grass"),
    73: ("Leech Seed", "Grass"), 74: ("Growth", "Normal"), 75: ("Razor Leaf", "Grass"),
    76: ("Solar Beam", "Grass"), 77: ("Poison Powder", "Poison"), 78: ("Stun Spore", "Grass"),
    79: ("Sleep Powder", "Grass"), 80: ("Petal Dance", "Grass"), 81: ("String Shot", "Bug"),
    82: ("Dragon Rage", "Dragon"), 83: ("Fire Spin", "Fire"), 84: ("Thunder Shock", "Electric"),
    85: ("Thunderbolt", "Electric"), 86: ("Thunder Wave", "Electric"), 87: ("Thunder", "Electric"),
    88: ("Rock Throw", "Rock"), 89: ("Earthquake", "Ground"), 90: ("Fissure", "Ground"),
    91: ("Dig", "Ground"), 92: ("Toxic", "Poison"), 93: ("Confusion", "Psychic"),
    94: ("Psychic", "Psychic"), 95: ("Hypnosis", "Psychic"), 96: ("Meditate", "Psychic"),
    97: ("Agility", "Psychic"), 98: ("Quick Attack", "Normal"), 99: ("Rage", "Normal"),
    100: ("Teleport", "Psychic"), 101: ("Night Shade", "Ghost"), 102: ("Mimic", "Normal"),
    103: ("Screech", "Normal"), 104: ("Double Team", "Normal"), 105: ("Recover", "Normal"),
    106: ("Harden", "Normal"), 107: ("Minimize", "Normal"), 108: ("Smokescreen", "Normal"),
    109: ("Confuse Ray", "Ghost"), 110: ("Withdraw", "Water"), 111: ("Defense Curl", "Normal"),
    112: ("Barrier", "Psychic"), 113: ("Light Screen", "Psychic"), 114: ("Haze", "Ice"),
    115: ("Reflect", "Psychic"), 116: ("Focus Energy", "Normal"), 117: ("Bide", "Normal"),
    118: ("Metronome", "Normal"), 119: ("Mirror Move", "Flying"), 120: ("Self-Destruct", "Normal"),
    121: ("Egg Bomb", "Normal"), 122: ("Lick", "Ghost"), 123: ("Smog", "Poison"),
    124: ("Sludge", "Poison"), 125: ("Bone Club", "Ground"), 126: ("Fire Blast", "Fire"),
    127: ("Waterfall", "Water"), 128: ("Clamp", "Water"), 129: ("Swift", "Normal"),
    130: ("Skull Bash", "Normal"), 131: ("Spike Cannon", "Normal"), 132: ("Constrict", "Normal"),
    133: ("Amnesia", "Psychic"), 134: ("Kinesis", "Psychic"), 135: ("Soft-Boiled", "Normal"),
    136: ("High Jump Kick", "Fighting"), 137: ("Glare", "Normal"), 138: ("Dream Eater", "Psychic"),
    139: ("Poison Gas", "Poison"), 140: ("Barrage", "Normal"), 141: ("Leech Life", "Bug"),
    142: ("Lovely Kiss", "Normal"), 143: ("Sky Attack", "Flying"), 144: ("Transform", "Normal"),
    145: ("Bubble", "Water"), 146: ("Dizzy Punch", "Normal"), 147: ("Spore", "Grass"),
    148: ("Flash", "Normal"), 149: ("Psywave", "Psychic"), 150: ("Splash", "Normal"),
    151: ("Acid Armor", "Poison"), 152: ("Crabhammer", "Water"), 153: ("Explosion", "Normal"),
    154: ("Fury Swipes", "Normal"), 155: ("Bonemerang", "Ground"), 156: ("Rest", "Psychic"),
    157: ("Rock Slide", "Rock"), 158: ("Hyper Fang", "Normal"), 159: ("Sharpen", "Normal"),
    160: ("Conversion", "Normal"), 161: ("Tri Attack", "Normal"), 162: ("Super Fang", "Normal"),
    163: ("Slash", "Normal"), 164: ("Substitute", "Normal"), 165: ("Struggle", "Normal"),
    166: ("Sketch", "Normal"), 167: ("Triple Kick", "Fighting"), 168: ("Thief", "Dark"),
    169: ("Spider Web", "Bug"), 170: ("Mind Reader", "Normal"), 171: ("Nightmare", "Ghost"),
    172: ("Flame Wheel", "Fire"), 173: ("Snore", "Normal"), 174: ("Curse", "???"),
    175: ("Flail", "Normal"), 176: ("Conversion 2", "Normal"), 177: ("Aeroblast", "Flying"),
    178: ("Cotton Spore", "Grass"), 179: ("Reversal", "Fighting"), 180: ("Spite", "Ghost"),
    181: ("Powder Snow", "Ice"), 182: ("Protect", "Normal"), 183: ("Mach Punch", "Fighting"),
    184: ("Scary Face", "Normal"), 185: ("Faint Attack", "Dark"), 186: ("Sweet Kiss", "Normal"),
    187: ("Belly Drum", "Normal"), 188: ("Sludge Bomb", "Poison"), 189: ("Mud-Slap", "Ground"),
    190: ("Octazooka", "Water"), 191: ("Spikes", "Ground"), 192: ("Zap Cannon", "Electric"),
    193: ("Foresight", "Normal"), 194: ("Destiny Bond", "Ghost"), 195: ("Perish Song", "Normal"),
    196: ("Icy Wind", "Ice"), 197: ("Detect", "Fighting"), 198: ("Bone Rush", "Ground"),
    199: ("Lock-On", "Normal"), 200: ("Outrage", "Dragon"), 201: ("Sandstorm", "Rock"),
    202: ("Giga Drain", "Grass"), 203: ("Endure", "Normal"), 204: ("Charm", "Normal"),
    205: ("Rollout", "Rock"), 206: ("False Swipe", "Normal"), 207: ("Swagger", "Normal"),
    208: ("Milk Drink", "Normal"), 209: ("Spark", "Electric"), 210: ("Fury Cutter", "Bug"),
    211: ("Steel Wing", "Steel"), 212: ("Mean Look", "Normal"), 213: ("Attract", "Normal"),
    214: ("Sleep Talk", "Normal"), 215: ("Heal Bell", "Normal"), 216: ("Return", "Normal"),
    217: ("Present", "Normal"), 218: ("Frustration", "Normal"), 219: ("Safeguard", "Normal"),
    220: ("Pain Split", "Normal"), 221: ("Sacred Fire", "Fire"), 222: ("Magnitude", "Ground"),
    223: ("Dynamic Punch", "Fighting"), 224: ("Megahorn", "Bug"), 225: ("Dragon Breath", "Dragon"),
    226: ("Baton Pass", "Normal"), 227: ("Encore", "Normal"), 228: ("Pursuit", "Dark"),
    229: ("Rapid Spin", "Normal"), 230: ("Sweet Scent", "Normal"), 231: ("Iron Tail", "Steel"),
    232: ("Metal Claw", "Steel"), 233: ("Vital Throw", "Fighting"), 234: ("Morning Sun", "Normal"),
    235: ("Synthesis", "Grass"), 236: ("Moonlight", "Normal"), 237: ("Hidden Power", "Normal"),
    238: ("Cross Chop", "Fighting"), 239: ("Twister", "Dragon"), 240: ("Rain Dance", "Water"),
    241: ("Sunny Day", "Fire"), 242: ("Crunch", "Dark"), 243: ("Mirror Coat", "Psychic"),
    244: ("Psych Up", "Normal"), 245: ("Extreme Speed", "Normal"), 246: ("Ancient Power", "Rock"),
    247: ("Shadow Ball", "Ghost"), 248: ("Future Sight", "Psychic"), 249: ("Rock Smash", "Fighting"),
    250: ("Whirlpool", "Water"), 251: ("Beat Up", "Dark"), 252: ("Fake Out", "Normal"),
    253: ("Uproar", "Normal"), 254: ("Stockpile", "Normal"), 255: ("Spit Up", "Normal"),
    256: ("Swallow", "Normal"), 257: ("Heat Wave", "Fire"), 258: ("Hail", "Ice"),
    259: ("Torment", "Dark"), 260: ("Flatter", "Dark"), 261: ("Will-O-Wisp", "Fire"),
    262: ("Memento", "Dark"), 263: ("Facade", "Normal"), 264: ("Focus Punch", "Fighting"),
    265: ("Smelling Salts", "Normal"), 266: ("Follow Me", "Normal"), 267: ("Nature Power", "Normal"),
    268: ("Charge", "Electric"), 269: ("Taunt", "Dark"), 270: ("Helping Hand", "Normal"),
    271: ("Trick", "Psychic"), 272: ("Role Play", "Psychic"), 273: ("Wish", "Normal"),
    274: ("Assist", "Normal"), 275: ("Ingrain", "Grass"), 276: ("Superpower", "Fighting"),
    277: ("Magic Coat", "Psychic"), 278: ("Recycle", "Normal"), 279: ("Revenge", "Fighting"),
    280: ("Brick Break", "Fighting"), 281: ("Yawn", "Normal"), 282: ("Knock Off", "Dark"),
    283: ("Endeavor", "Normal"), 284: ("Eruption", "Fire"), 285: ("Skill Swap", "Psychic"),
    286: ("Imprison", "Psychic"), 287: ("Refresh", "Normal"), 288: ("Grudge", "Ghost"),
    289: ("Snatch", "Dark"), 290: ("Secret Power", "Normal"), 291: ("Dive", "Water"),
    292: ("Arm Thrust", "Fighting"), 293: ("Camouflage", "Normal"), 294: ("Tail Glow", "Bug"),
    295: ("Luster Purge", "Psychic"), 296: ("Mist Ball", "Psychic"), 297: ("Feather Dance", "Flying"),
    298: ("Teeter Dance", "Normal"), 299: ("Blaze Kick", "Fire"), 300: ("Mud Sport", "Ground"),
    301: ("Ice Ball", "Ice"), 302: ("Needle Arm", "Grass"), 303: ("Slack Off", "Normal"),
    304: ("Hyper Voice", "Normal"), 305: ("Poison Fang", "Poison"), 306: ("Crush Claw", "Normal"),
    307: ("Blast Burn", "Fire"), 308: ("Hydro Cannon", "Water"), 309: ("Meteor Mash", "Steel"),
    310: ("Astonish", "Ghost"), 311: ("Weather Ball", "Normal"), 312: ("Aromatherapy", "Grass"),
    313: ("Fake Tears", "Dark"), 314: ("Air Cutter", "Flying"), 315: ("Overheat", "Fire"),
    316: ("Odor Sleuth", "Normal"), 317: ("Rock Tomb", "Rock"), 318: ("Silver Wind", "Bug"),
    319: ("Metal Sound", "Steel"), 320: ("Grass Whistle", "Grass"), 321: ("Tickle", "Normal"),
    322: ("Cosmic Power", "Psychic"), 323: ("Water Spout", "Water"), 324: ("Signal Beam", "Bug"),
    325: ("Shadow Punch", "Ghost"), 326: ("Extrasensory", "Psychic"), 327: ("Sky Uppercut", "Fighting"),
    328: ("Sand Tomb", "Ground"), 329: ("Sheer Cold", "Ice"), 330: ("Muddy Water", "Water"),
    331: ("Bullet Seed", "Grass"), 332: ("Aerial Ace", "Flying"), 333: ("Icicle Spear", "Ice"),
    334: ("Iron Defense", "Steel"), 335: ("Block", "Normal"), 336: ("Howl", "Normal"),
    337: ("Dragon Claw", "Dragon"), 338: ("Frenzy Plant", "Grass"), 339: ("Bulk Up", "Fighting"),
    340: ("Bounce", "Flying"), 341: ("Mud Shot", "Ground"), 342: ("Poison Tail", "Poison"),
    343: ("Covet", "Normal"), 344: ("Volt Tackle", "Electric"), 345: ("Magical Leaf", "Grass"),
    346: ("Water Sport", "Water"), 347: ("Calm Mind", "Psychic"), 348: ("Leaf Blade", "Grass"),
    349: ("Dragon Dance", "Dragon"), 350: ("Rock Blast", "Rock"), 351: ("Shock Wave", "Electric"),
    352: ("Water Pulse", "Water"), 353: ("Doom Desire", "Steel"), 354: ("Psycho Boost", "Psychic"),
}

MOVE_NAMES = {k: v[0] for k, v in MOVE_DATA.items()}
MOVE_TYPES = {k: v[1] for k, v in MOVE_DATA.items()}

NATURE_NAMES = [
    "Hardy", "Lonely", "Brave", "Adamant", "Naughty",
    "Bold", "Docile", "Relaxed", "Impish", "Lax",
    "Timid", "Hasty", "Serious", "Jolly", "Naive",
    "Modest", "Mild", "Quiet", "Bashful", "Rash",
    "Calm", "Gentle", "Sassy", "Careful", "Quirky",
]

# FireRed map (bank, number) -> name for key locations
MAP_NAMES = {
    (3, 0): "Pallet Town",
    (3, 1): "Viridian City",
    (3, 2): "Pewter City",
    (3, 3): "Cerulean City",
    (3, 4): "Lavender Town",
    (3, 5): "Vermilion City",
    (3, 6): "Celadon City",
    (3, 7): "Fuchsia City",
    (3, 8): "Cinnabar Island",
    (3, 9): "Indigo Plateau",
    (3, 10): "Saffron City",
    (3, 11): "One Island",
    (3, 12): "Two Island",
    (3, 13): "Three Island",
    (3, 14): "Four Island",
    (3, 15): "Five Island",
    (3, 16): "Seven Island",
    (3, 17): "Six Island",
    (3, 18): "Route 1",
    (3, 19): "Route 2",
    (3, 20): "Route 3",
    (3, 21): "Route 4",
    (3, 22): "Route 5",
    (3, 23): "Route 6",
    (3, 24): "Route 7",
    (3, 25): "Route 8",
    (3, 26): "Route 9",
    (3, 27): "Route 10",
    (3, 28): "Route 11",
    (3, 29): "Route 12",
    (3, 30): "Route 13",
    (3, 31): "Route 14",
    (3, 32): "Route 15",
    (3, 33): "Route 16",
    (3, 34): "Route 17",
    (3, 35): "Route 18",
    (3, 36): "Route 19",
    (3, 37): "Route 20",
    (3, 38): "Route 21",
    (3, 39): "Route 22",
    (3, 40): "Route 23",
    (3, 41): "Route 24",
    (3, 42): "Route 25",
    (4, 0): "Player's House 1F",
    (4, 1): "Player's House 2F",
    (4, 2): "Rival's House",
    (4, 3): "Oak's Lab",
    (4, 4): "Viridian Pokemon Center",
    (4, 5): "Viridian Mart",
    (4, 6): "Viridian School",
    (4, 7): "Viridian House",
    (4, 8): "Viridian Gym",
    (4, 9): "Viridian NPC House",
    (4, 10): "Pewter Museum 1F",
    (4, 11): "Pewter Museum 2F",
    (4, 12): "Pewter Gym",
    (4, 13): "Pewter House",
    (4, 14): "Pewter Pokemon Center",
    (4, 15): "Pewter Mart",
    (4, 16): "Cerulean House",
    (4, 17): "Cerulean Bike Shop",
    (4, 18): "Cerulean Pokemon Center",
    (4, 19): "Cerulean Gym",
    (4, 20): "Cerulean Mart",
    (4, 36): "Vermilion Pokemon Center",
    (4, 37): "Vermilion Mart",
    (4, 38): "Vermilion Gym",
    (4, 39): "Vermilion Fan Club",
    (4, 43): "Celadon Dept Store 1F",
    (4, 48): "Celadon Pokemon Center",
    (4, 49): "Celadon Gym",
    (4, 53): "Saffron Gym",
    (4, 54): "Saffron Pokemon Center",
    (4, 55): "Saffron Mart",
    (4, 58): "Fuchsia Pokemon Center",
    (4, 59): "Fuchsia Mart",
    (4, 60): "Fuchsia Gym",
    (4, 62): "Cinnabar Pokemon Center",
    (4, 63): "Cinnabar Gym",
    (4, 64): "Cinnabar Lab",
    (5, 0): "Indigo Plateau Pokemon Center",
    (5, 1): "Indigo Plateau Lobby",
    (5, 2): "Lorelei's Room",
    (5, 3): "Bruno's Room",
    (5, 4): "Agatha's Room",
    (5, 5): "Lance's Room",
    (5, 6): "Champion's Room",
    (5, 7): "Hall of Fame",
    (8, 0): "Viridian Forest",
    (8, 1): "Mt. Moon 1F",
    (8, 2): "Mt. Moon B1F",
    (8, 3): "Mt. Moon B2F",
    (8, 4): "S.S. Anne Exterior",
    (8, 11): "Victory Road 1F",
    (8, 12): "Victory Road 2F",
    (8, 13): "Victory Road 3F",
    (8, 14): "Pokemon Tower 1F",
    (8, 15): "Pokemon Tower 2F",
    (8, 16): "Pokemon Tower 3F",
    (8, 17): "Pokemon Tower 4F",
    (8, 18): "Pokemon Tower 5F",
    (8, 19): "Pokemon Tower 6F",
    (8, 20): "Pokemon Tower 7F",
    (8, 21): "Silph Co. 1F",
    (8, 31): "Silph Co. 11F",
    (8, 32): "Rock Tunnel 1F",
    (8, 33): "Rock Tunnel B1F",
    (8, 34): "Safari Zone Center",
    (8, 35): "Safari Zone East",
    (8, 36): "Safari Zone North",
    (8, 37): "Safari Zone West",
    (9, 0): "Route 1 Gate",
    (9, 1): "Route 2 Gate",
    (9, 3): "Route 3 Gate",
    (9, 5): "Route 5 Gate",
    (9, 7): "Route 6 Gate",
    (9, 9): "Route 7 Gate",
    (9, 11): "Route 8 Gate",
    (9, 14): "Underground Path (5-6)",
    (9, 15): "Underground Path (7-8)",
    (10, 0): "Digletts Cave North",
    (10, 1): "Digletts Cave South",
    (10, 3): "Cerulean Cave 1F",
    (10, 4): "Cerulean Cave 2F",
    (10, 5): "Cerulean Cave B1F",
    (10, 6): "Seafoam Islands 1F",
    (10, 11): "Pokemon Mansion 1F",
    (10, 14): "Power Plant",
}

# Gen 3 proprietary charset -> ASCII (partial, covers common English text)
GEN3_CHARSET = {
    0xBB: "A", 0xBC: "B", 0xBD: "C", 0xBE: "D", 0xBF: "E",
    0xC0: "F", 0xC1: "G", 0xC2: "H", 0xC3: "I", 0xC4: "J",
    0xC5: "K", 0xC6: "L", 0xC7: "M", 0xC8: "N", 0xC9: "O",
    0xCA: "P", 0xCB: "Q", 0xCC: "R", 0xCD: "S", 0xCE: "T",
    0xCF: "U", 0xD0: "V", 0xD1: "W", 0xD2: "X", 0xD3: "Y",
    0xD4: "Z", 0xD5: "a", 0xD6: "b", 0xD7: "c", 0xD8: "d",
    0xD9: "e", 0xDA: "f", 0xDB: "g", 0xDC: "h", 0xDD: "i",
    0xDE: "j", 0xDF: "k", 0xE0: "l", 0xE1: "m", 0xE2: "n",
    0xE3: "o", 0xE4: "p", 0xE5: "q", 0xE6: "r", 0xE7: "s",
    0xE8: "t", 0xE9: "u", 0xEA: "v", 0xEB: "w", 0xEC: "x",
    0xED: "y", 0xEE: "z", 0x00: " ", 0xAB: "!", 0xAC: "?",
    0xAD: ".", 0xB8: ",", 0xBA: "-", 0xB4: "'", 0xB1: '"',
    0xA1: "0", 0xA2: "1", 0xA3: "2", 0xA4: "3", 0xA5: "4",
    0xA6: "5", 0xA7: "6", 0xA8: "7", 0xA9: "8", 0xAA: "9",
    0xFF: "",  # terminator
}

ITEM_NAMES = {
    0: "None",
    1: "Master Ball", 2: "Ultra Ball", 3: "Great Ball", 4: "Poke Ball",
    5: "Safari Ball", 6: "Net Ball", 7: "Dive Ball", 8: "Nest Ball",
    9: "Repeat Ball", 10: "Timer Ball", 11: "Luxury Ball", 12: "Premier Ball",
    13: "Potion", 14: "Antidote", 15: "Burn Heal", 16: "Ice Heal",
    17: "Awakening", 18: "Parlyz Heal", 19: "Full Restore", 20: "Max Potion",
    21: "Hyper Potion", 22: "Super Potion", 23: "Full Heal", 24: "Revive",
    25: "Max Revive", 26: "Fresh Water", 27: "Soda Pop", 28: "Lemonade",
    29: "Moomoo Milk", 30: "Energy Powder", 31: "Energy Root", 32: "Heal Powder",
    33: "Revival Herb", 34: "Ether", 35: "Max Ether", 36: "Elixir",
    37: "Max Elixir", 38: "Lava Cookie", 39: "Blue Flute", 40: "Yellow Flute",
    41: "Red Flute", 42: "Black Flute", 43: "White Flute", 44: "Berry Juice",
    45: "Sacred Ash", 46: "Shoal Salt", 47: "Shoal Shell", 48: "Red Shard",
    49: "Blue Shard", 50: "Yellow Shard", 51: "Green Shard",
    63: "HP Up", 64: "Protein", 65: "Iron", 66: "Carbos",
    67: "Calcium", 68: "Rare Candy", 69: "PP Up", 70: "Zinc",
    71: "PP Max", 73: "Guard Spec.", 74: "Dire Hit", 75: "X Attack",
    76: "X Defend", 77: "X Speed", 78: "X Accuracy", 79: "X Special",
    80: "Poke Doll", 81: "Repel", 82: "Super Repel", 83: "Max Repel",
    84: "Escape Rope", 85: "Sun Stone", 86: "Moon Stone", 87: "Fire Stone",
    88: "Thunder Stone", 89: "Water Stone", 90: "Leaf Stone",
    179: "Bright Powder", 180: "White Herb", 181: "Macho Brace",
    182: "Exp. Share", 183: "Quick Claw", 187: "King's Rock",
    191: "Leftovers", 197: "Focus Band", 199: "Scope Lens",
    213: "Shell Bell", 216: "Choice Band",
}


def decode_status(status_int):
    """Decode the Gen 3 status condition bitfield into a human-readable string."""
    if status_int == 0:
        return "OK"
    parts = []
    sleep_turns = status_int & 0x07
    if sleep_turns:
        parts.append(f"SLP({sleep_turns})")
    if status_int & 0x08:
        parts.append("PSN")
    if status_int & 0x10:
        parts.append("BRN")
    if status_int & 0x20:
        parts.append("FRZ")
    if status_int & 0x40:
        parts.append("PAR")
    if status_int & 0x80:
        parts.append("TOX")
    return "/".join(parts) if parts else "OK"


def species_name(species_id):
    return SPECIES_NAMES.get(species_id, f"???({species_id})")


def move_name(move_id):
    return MOVE_NAMES.get(move_id, f"???({move_id})")


def move_type(move_id):
    return MOVE_TYPES.get(move_id, "Normal")


def item_name(item_id):
    return ITEM_NAMES.get(item_id, f"Item#{item_id}")


def map_name(bank, number):
    return MAP_NAMES.get((bank, number), f"Unknown({bank},{number})")


def enrich_pokemon(pkmn):
    """Add human-readable names to a raw pokemon dict from state.json."""
    enriched = dict(pkmn)
    enriched["species_name"] = species_name(pkmn.get("species_id", 0))
    enriched["status_text"] = decode_status(pkmn.get("status", 0))
    enriched["held_item_name"] = item_name(pkmn.get("held_item_id", 0))
    raw_moves = pkmn.get("moves", [])
    raw_pp = pkmn.get("pp", [])
    enriched["move_details"] = []
    for i, mid in enumerate(raw_moves):
        if mid == 0:
            continue
        pp = raw_pp[i] if i < len(raw_pp) else 0
        enriched["move_details"].append({
            "slot": i + 1,
            "name": move_name(mid),
            "type": move_type(mid),
            "pp": pp,
        })
    return enriched


def enrich_state(state):
    """Add all human-readable names to a raw state dict from state.json."""
    enriched = dict(state)
    enriched["map_name"] = map_name(
        state.get("map_bank", 0), state.get("map_number", 0)
    )
    enriched["party"] = [enrich_pokemon(p) for p in state.get("party", [])]
    enriched["enemy"] = [enrich_pokemon(e) for e in state.get("enemy", [])]
    return enriched
