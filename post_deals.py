name: Auto Post Travel Deals

on:
  schedule:
    - cron: '0 8,13,18 * * *'
  workflow_dispatch:

jobs:
  post-deals:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Repo
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install Dependencies
        run: pip install requests

      - name: Run Deal Poster
        env:
          TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
          TELEGRAM_CHANNEL_ID: ${{ secrets.TELEGRAM_CHANNEL_ID }}
          TRAVELPAYOUTS_TOKEN: ${{ secrets.TRAVELPAYOUTS_TOKEN }}
          AFFILIATE_MARKER: ${{ secrets.AFFILIATE_MARKER }}
        run: python post_deals.py
