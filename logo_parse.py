from pathlib import Path
import shutil


SRC = Path('/Users/jus/PycharmProjects/StockReader/Logo-3K+')
DEST = Path('/Users/jus/PycharmProjects/StockReader/logos')

# Folder names from Logo-2K+ that correspond to S&P 100 companies
SP100_FOLDERS = [
    # Electronic
    'AMD',
    'Apple',
    'Cisco Systems',
    'Honeywell',
    'IBM',
    'Intel',
    'Microsoft',
    'Texas Instruments',  # found under Medical/

    # Transportation
    'Tesla',

    # Accessories
    'Nike',

    # Food
    'coca cola',
    'Costco Wholesale',
    'McDonald\'s',
    'pepsi',
    'Starbucks',

    # Institution
    'Amazon at Lab126',
    'Chevron',
    'Exxon',
    'General Electric',
    'Google',
    'J.P. Morgan',
    'John Deere',
    'Marathon Petroleum',
    'Marriott International',
    'Target',
    'Walmart',

    # Cosmetic
    'Johnson & Johnson',

    # Medical
    'Colgate',

    # Leisure
    'Disney'
]

for category in SRC.iterdir():
    if category.is_dir():
        for company in category.iterdir():
            if company.is_dir() and company.name in SP100_FOLDERS:
                print(f"Moving directory: {company.name} -> ")
                shutil.move(str(company), str(DEST / company.name))