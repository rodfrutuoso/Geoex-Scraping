## Badges

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)
[![Python](https://img.shields.io/badge/Python-3.12%2B-blue)](https://www.python.org/)
[![Cloudscraper](https://img.shields.io/badge/Cloudscraper-v1.2.71-orange)](https://github.com/codemanki/cloudscraper)
[![Google Sheets API](https://img.shields.io/badge/Google%20Sheets%20API-v4-yellowgreen)](https://developers.google.com/sheets/api)
[![PySide6](https://img.shields.io/badge/PySide6-v6.5.0-red)](https://pypi.org/project/PySide6/)

# Geoex-Scraping

A data scraping from the Geoex system


## Installation

[Download](https://github.com/Max-GF/Geoex-Scraping/archive/refs/heads/main.zip) the zip file from the repository, or clone the project

```bash
  git clone https://github.com/Max-GF/Geoex-Scraping.git
```

Install dependencies

```bash
  pip install -r requirements.txt
```

## Environment Variables

To run this project, you will need to add the following environment variables to your .env file. Check the [.env.example](.env.example) file for reference.

`APP_NAME`
`MAXIMIZE_ICON_PATH`
`MINIMIZE_ICON_PATH`
`CLOSE_ICON_PATH`
`PRIVACY_POLICIES_ICON_PATH`
`HELP_ICON_PATH`
`HOME_LOGO_PATH`
`TITLE_ICON_PATH`
`EXPAND_SIDEBAR_ICON_PATH`
`RESIZE_BUTTON_ICON_PATH`
`HOME_BUTTON_ICON_PATH`
`GEOEX_PAGE_BUTTON_ICON_PATH`
`WORKING_GIF_PATH`

You also need to create a Google Cloud project and enable the Google Sheets API. Then, create a service account and download the JSON key file. Rename it to `credentials.json` and place it in the [assets](./assets) directory of the project.
Go to https://developers.google.com/workspace/guides/create-project for more information.


## Usage

To run the project, use the following command:

```bash
  python .\src\main.py
  python.exe -m src.modules.scrappers.geoex_scrapper
```

This will open the GUI application. You can then enter your credentials and start scraping data from the Geoex system. The scraped data will be exported to a Google Sheets document.

If you want to export the app as a .exe file, you can use the `pyinstaller` command. Make sure to have `pyinstaller` installed in your environment.

```bash
  pyinstaller main.spec
```

## Features
- Scrape data from the Geoex system
- Export data to Google Sheets
- User-friendly GUI
- Settings to export app as a .exe file


## Feedback

If you have any feedback, please reach out to me at maxdultra@gmail.com

## Authors

- [@Max-GF](https://github.com/Max-GF)

