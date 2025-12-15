# TfNSW Departure Monitor

A real-time departure monitor for Transport for NSW (TfNSW) services including trains, buses, light rail, and ferries.

## How It Works

The system consists of three main components:

1. **departures.py** - Python script that fetches departure data from the TfNSW API
2. **departures.json** - JSON file containing the departure information
3. **index.html** - Web page that displays the departures

## Setup

1. Make sure you have Python installed with the `requests` library:
   ```powershell
   pip install requests
   ```

2. Your API key is already configured in `departures.py`

## Usage

### Step 1: Fetch Departure Data

Run the Python script to fetch current departure information from the TfNSW API:

```powershell
python departures.py
```

This will:
- Query the TfNSW API for departures from configured stops (Parramatta Station, Parramatta Square, Parramatta Wharf)
- Filter and sort the departures
- Save the results to `departures.json`

### Step 2: View Departures

Open `index.html` in a web browser to view the departures. The page will:
- Read data from `departures.json`
- Display departures in a clean, color-coded table
- Auto-refresh every 60 seconds

## Customizing Stations/Stops

Edit the `stops_to_show` list in `departures.py` to add or remove stations:

```python
stops_to_show = [
    {
        "station_name": "Parramatta",
        "stop_id": "10101229",
        "modes": [
            {
                "mode_name": "train",
                "mode_number": 1,
            },
            # Add more modes here
        ]
    },
    # Add more stations here
]
```

## Automation

To keep the departures updated, you can:

1. **Run manually** when you want to check departures
2. **Run on a schedule** using Windows Task Scheduler or a cron job
3. **Run continuously** by uncommenting the loop at the end of `departures.py`

## Color Coding

- **Orange** (#F6891F) - Trains
- **Blue** (#009ED7) - Buses  
- **Red** (#BB2043) - Light Rail
- **Green** (#648C3C) - Ferries

## Files

- `departures.py` - Main Python script
- `departures.json` - Generated departure data (updated each time you run the script)
- `index.html` - Web interface for viewing departures
- `index.html.backup` - Backup of original HTML file
