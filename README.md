# Depop Scraper

A Python script to export all ACTIVE Depop listings (title description price images links) to a CSV file, perfect for bulk importing into eBay or other reselling platforms.

## Installation Steps:

### 1. Install Required Python Packages

```
pip install selenium pandas
```

### 2. Download Chromedriver
Can get it here: https://chromedriver.chromium.org/downloads

### 3. Download or copy `depop_scraper_full.py` to a folder on your computer.
Make sure you edit the script with your own depop username:

```
USERNAME = "your-depop-username"
```

### 4. Run the Script
Open Command Prompt/Terminal and navigate to your script's folder:

```
cd path/to/your/folder
python depop_scraper_full.py
```

### 5. Find Your Scraped Listings
When finished, you'll see `depop_scraped.csv` in your folder.
- Open it in Excel, Google Sheets, or any spreadsheet program to review.

Follow eBay's bulk listing tool instructions for uploading your file.

## Sample Output

Your CSV file will contain columns like:

| title | desc | price | PictureURL | image_count | listing_url |
|-------|------|-------|------------|-------------|-------------|
| Vintage Band Tee | Green shirt, size L | 20 | https://media-photos.depop.com/.../image.jpg | 2 | https://www.depop.com/products/... |

## Troubleshooting

- **If you get "chromedriver not found":** Add the path to your chromedriver in the script:

```
driver_path = "C:/path/to/chromedriver.exe" # Update this path
driver = webdriver.Chrome(executable_path=driver_path, options=chrome_options)
```

- **If listings don't appear in the CSV:** Make sure you can see your products while signed out of Depop (they must be public and unsold).

- **Browser errors in output:** Safe to ignore messages about WebGL, GCM, or SharedImage—these don't affect scraping.

## Requirements

- Python 3.8 or higher
- Google Chrome browser
- Chromedriver (matching your Chrome version)
- Python packages: `selenium`, `pandas`
