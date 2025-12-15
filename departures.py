import requests
from datetime import datetime, timezone
import json
import html

# Variables to be set by the user
API_KEY = ""

# Set output paths explicitly
OUTPUT_HTML_PATH = "dashboard.html"
OUTPUT_JSON_PATH = "departures.json"

# hardcoded stops
# 1 = Train, 2 = Metro, 4 = Light Rail, 5 = Bus, 7 = Coach, 9 = Ferry, 11 = School Bus
stops_to_show = [
    {
        "station_name": "Parramatta",
        "stop_id": "10101229",
        "modes": [
            {
                "mode_name": "train",
                "mode_number": 1,
            },
            {
                "mode_name": "bus",
                "mode_number": 5,
                "routes_to_exclude": ["520", "521", "523", "524", "546", "549", "552", "600", "601", "603", "604", "606", "609", "625", "660", "661", "662", "663", "700", "705", "706", "707", "708", "711", "802", "804", "806", "810X", "811X", "824", "906", "907", "909", "920"]
            }
        ]
    },
    {
        "station_name": "Parramatta Square",
        "stop_id": "10101710",
        "modes": [
            {
                "mode_name": "light_rail",
                "mode_number": 4,
            }
        ]
    },
    {
        "station_name": "Parramatta Wharf",
        "stop_id": "10102032",
        "modes": [
            {
                "mode_name": "ferry",
                "mode_number": 9,
            }
        ]
    }
]
#######################################################################################################################################

def get_accent_colour(line, mode_of_transport_name):
    """
    Simplified accent colours:
      - buses: blue
      - trains & metros: orange
      - light rail: red
      - ferries: green
    Any other mode falls back to black.
    """
    mode_map = {
        "train": "#F6891F",      # orange
        "metro": "#168388",      # orange (same as train)
        "light_rail": "#BB2043", # red
        "bus": "#009ED7",        # blue
        "ferry": "#648C3C",      # green
    }

    # Return mapped colour for mode, fallback to black
    return mode_map.get(mode_of_transport_name, "#000000")

def hex_to_rgba(hex_str, alpha=1.0):
    """Convert #RRGGBB or #RRGGBBAA to rgba(...) string for inline CSS."""
    if not hex_str:
        return hex_str or ""
    h = hex_str.lstrip('#')
    try:
        if len(h) == 8:  # RRGGBBAA
            r = int(h[0:2], 16)
            g = int(h[2:4], 16)
            b = int(h[4:6], 16)
            a = int(h[6:8], 16) / 255.0
            return f"rgba({r},{g},{b},{a * alpha})"
        elif len(h) == 6:  # RRGGBB
            r = int(h[0:2], 16)
            g = int(h[2:4], 16)
            b = int(h[4:6], 16)
            return f"rgba({r},{g},{b},{alpha})"
    except Exception:
        pass
    return hex_str

def generate_html_output(every_departure, output_path):
    """
    Generate a static HTML file with the departures table.
    Styling matches index.html. Platform info is not shown.
    """
    rows_html = []
    for dep in every_departure:
        line = html.escape(dep.get('line_disassembledName_route') or '')
        accent = dep.get('accent_colour') or '#000000'
        bg_second = hex_to_rgba(accent, 0.1)
        destination = html.escape(dep.get('destination_without_via') or 'Unknown Destination')
        via = html.escape(dep.get('destination_via_only') or '')
        minutes = dep.get('minutes_to_departure')
        is_rt = dep.get('isRealtimeControlled', True)

        # time cell
        if minutes == 0:
            time_text = 'Now'
        elif minutes is None:
            time_text = ''
        elif minutes > 60:
            hours = minutes // 60
            mins = minutes % 60
            time_text = f"{hours} hr<br>{mins} min"
        else:
            time_text = f"{minutes} min"

        time_style = "" if is_rt else "color: rgb(0,0,0);"

        row = f"""
            <tr>
                <td class="category" style="background-color:{accent};">{line}</td>
                <td class="content expand" style="background-color:{bg_second};">
                    <span class="destination">{destination}</span>"""
        if via:
            row += f""" <span class="regular" style="font-size:0.9em"> via {via}</span>"""
        row += f"""
                </td>
                <td class="time" style="background-color:{bg_second}; {time_style}">{time_text}</td>
            </tr>
        """
        rows_html.append(row)

    full_table_html = "\n".join(rows_html)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="refresh" content="60">
<title>Departures (static)</title>
<style>
    /* Always light mode styling with reduced row heights (approx. half) */
    body {{ font-family: 'Segoe UI', sans-serif; background-color: white; color: #000; font-size: 14px; }}
    /* vertical spacing set to ~half (5 -> 2), padding halved (8 -> 4) */
    table {{ width: 100%; border-spacing: 3px 2px; border-collapse: separate; padding: 5px; overflow: hidden; border-radius: 8px; background-color: transparent; }}
    td {{ padding: 4px; background-color: transparent; }}
    tr {{ overflow: hidden; border-radius: 8px; }}
    /* category cell: increased by 1px (global) + 3px extra => 15px */
    .category {{ font-size: 15px; font-weight: bold; color: white; text-align: center; width: 50px; height: 25px; line-height: 25px; border-radius: 8px; }}
    /* keep content readable while allowing shorter rows (original 13px -> now 14px) */
    .content {{ font-size: 14px; font-weight: normal; }}
    .expand {{ width: auto; text-align: left; border-top-left-radius: 8px; border-bottom-left-radius: 8px; }}
    .time {{ font-size: 14px; width: 60px; text-align: left; border-top-right-radius: 8px; border-bottom-right-radius: 8px; }}
    .destination {{ font-weight: bold; }}
    .regular {{ font-weight: normal; }}
    .red-text {{ color: red; }}
    tr:hover {{ background-color: rgba(0, 0, 0, 0.03); transition: background-color 0.2s ease-in-out; }}
    .tooltip {{ position: absolute; background-color: white; color: black; padding: 10px; border-radius: 5px; box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.2); display: none; z-index: 1000; max-width: 90%; font-size: 15px; }}
</style>
</head>
<body>
    <table id="departures-table">
{full_table_html}
    </table>

    <script>
    // Fallback JS reload every 60 seconds (supports browsers that ignore meta refresh)
    setTimeout(function() {{
        location.reload(true);
    }}, 60000);
    </script>
</body>
</html>"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"Static HTML file generated: {output_path}")

def get_departures_from_api_response(stop_name, stop_id, modes_of_transport, routes_to_exclude):
    """
    Global args:
        API_KEY (str): API key for the Transport for NSW API.
    
    Args:
        stop_name (str): used to remove 'via' from the destination name if it is the same as the stop name.
        stop_id (str): The ID of the stop to get departures from.
        modes_of_transport (list): List of transport modes to include (e.g., ["train", "bus", "ferry"]).
        routes_to_exclude (list): List of routes to exclude from the results. Just really used for busses.
        
    Returns:
        list: List of departures with relevant details.
    
    Get departures for a specific transport type.
    """
    # Get the current date and time at the time of the API call
    current_date = datetime.now().strftime("%Y%m%d")
    current_time = datetime.now().strftime("%H%M")

    # Base endpoint URL without query parameters
    endpoint = "https://api.transport.nsw.gov.au/v1/tp/departure_mon"

    # Set up headers
    headers = {
        "Authorization": f"apikey {API_KEY}",
        "Content-Type": "application/json"
    }

    # Query parameters
    params = {
        "outputFormat": "rapidJSON",
        "coordOutputFormat": "EPSG:4326",
        "mode": "direct",
        "type_dm": "stop",
        "name_dm": stop_id,
        "departureMonitorMacro": "true",
        "TfNSWDM": "true",
        "version": "10.2.1.42",
        "itdDate": current_date,
        "itdTime": current_time,
        "excludedMeans": "checkbox",
        "includeNonPassengerTrips": "false",
    }

    # Will be used later to map the type of transport to a more readable format for the JSON output and defining the accent colours
    type_lookup_table = {
        1: "train",
        2: "metro",
        4: "light_rail",
        5: "bus",
        7: "coach",
        9: "ferry",
        11: "school_bus"
    }
    
    # The API specifies which modes to EXCLUDE, not include, so assume we wan't to exclude all then remove the ones from exluded_modes we want to keep.
    
    # Start by assuming we'll exclude all modes of transport
    excluded_modes = [
        "exclMOT_1",  # Exclude trains
        "exclMOT_2",  # Exclude metro
        "exclMOT_4",  # Exclude light rail
        "exclMOT_5",  # Exclude bus
        "exclMOT_7",  # Exclude coach
        "exclMOT_9",  # Exclude ferry
        "exclMOT_11"  # Exclude school bus
    ]

    # Actually don't exclude modes we want to keep
    mode_name = modes_of_transport["mode_name"]
    if mode_name == "train":
        excluded_modes.remove("exclMOT_1")  # Keep trains
    elif mode_name == "metro":
        excluded_modes.remove("exclMOT_2")  # Keep metros
    elif mode_name == "light_rail":
        excluded_modes.remove("exclMOT_4")  # Keep light rails
    elif mode_name == "bus":
        excluded_modes.remove("exclMOT_5")  # Keep buses
    elif mode_name == "coach":
        excluded_modes.remove("exclMOT_7")  # Keep coaches
    elif mode_name == "ferry":
        excluded_modes.remove("exclMOT_9")  # Keep ferries
    elif mode_name == "school_bus":
        excluded_modes.remove("exclMOT_11")  # Keep school buses

    # Add exclusion parameters
    for mode in excluded_modes:
        params[mode] = "true"

    try:
        response = requests.get(endpoint, headers=headers, params=params, timeout=10)
    except requests.RequestException as e:
        print(f"HTTP request failed for {stop_name} ({stop_id}): {e}")
        return []
    departures = []
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        print(response.text)
        return departures  # Early return if the response is not successful

    json_data = response.json()
    if "stopEvents" not in json_data:
        print(f"'stopEvents' not found in response for {stop_name} (stop ID {stop_id}) for {mode_name}")
        return departures  # Early return if no stop events are found

    departures = extract_and_flatten_json_api_response(json_data, stop_name, routes_to_exclude)
    return departures

def extract_and_flatten_json_api_response(full_json, stop_name, routes_to_exclude):
    
    transport_modes = {
        1: "train",
        2: "metro",
        4: "light_rail",
        5: "bus",
        7: "coach",
        9: "ferry",
        11: "school_bus",
    }

    extracted_and_flattened_json = []

    for stop_event in full_json['stopEvents']:
        
        # If this is a route to exclude, then skip
        line_disassembledName_route = stop_event.get('transportation', {}).get('disassembledName')
        
        if line_disassembledName_route in routes_to_exclude:
            continue
        
        # Vehicle
        trip_id = stop_event.get('transportation', {}).get('id')
        realtime_trip_id = stop_event.get('properties', {}).get('RealtimeTripId')
        mode_of_transport_number = stop_event.get('transportation', {}).get('product', {}).get('class')
        derived_mode_of_transport_name = transport_modes.get(stop_event.get('transportation', {}).get('product', {}).get('class'), 'unknown')
        occupancy = stop_event.get('location', {}).get('properties', {}).get('occupancy')
        isRealtimeControlled = stop_event.get('isRealtimeControlled')

        # Route, Destination, and via
        destination_name = stop_event.get('transportation', {}).get('destination', {}).get('name')
        destination_without_via = stop_event.get('transportation', {}).get('destination', {}).get('name').split(' via ')[0]
        destination_without_via = destination_without_via.replace('Stn', 'Station')
        destination_via_only = stop_event.get('transportation', {}).get('destination', {}).get('name').split(' via ')[1] if ' via ' in stop_event.get('transportation', {}).get('destination', {}).get('name') else None
        destination_via_only = None if destination_via_only == stop_name else destination_via_only
        line_number_route = stop_event.get('transportation', {}).get('number')

        # Origin location
        stopEvent_location_name = stop_event.get('location', {}).get('name')
        stopEvents_stop_disassembledName = stop_event.get('location', {}).get('parent', {}).get('disassembledName')
        parent_location_properties_stopId = stop_event.get('location', {}).get('parent', {}).get('properties', {}).get('stopId')
        stopEvents_properties_stopId = stop_event.get('location', {}).get('properties', {}).get('stopId')
        # Platforms intentionally hidden
        derived_platform = ""
        stopEvents_disassembledName = stop_event.get('location', {}).get('parent', {}).get('disassembledName')

        # Timing
        minutes_to_departure = int((datetime.strptime(stop_event.get('departureTimeEstimated') or stop_event.get('departureTimePlanned'), "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc) - datetime.now(timezone.utc)).total_seconds() / 60)
        departureTimePlanned = stop_event.get('departureTimePlanned')
        departureTimeBaseTimetable = stop_event.get('departureTimeBaseTimetable')
        departureTimeEstimated = stop_event.get('departureTimeEstimated')
        departure_time = stop_event.get('departureTimeEstimated') or stop_event.get('departureTimePlanned')
        
        # Alerts
        alert_priority = stop_event.get('infos', [{}])[0].get('priority')
        alert_id = stop_event.get('infos', [{}])[0].get('id')
        alert_type = stop_event.get('infos', [{}])[0].get('type')
        alert_subtitle = stop_event.get('infos', [{}])[0].get('subtitle')
        alert_infoType = stop_event.get('infos', [{}])[0].get('properties', {}).get('infoType')


        # Get accent colour
        accent_colour = get_accent_colour(line_disassembledName_route, derived_mode_of_transport_name)

        # APPENDING
        extracted_and_flattened_json.append({
            'realtime_trip_id': realtime_trip_id,
            'accent_colour': accent_colour,
            'line_disassembledName_route': line_disassembledName_route,
            'destination_without_via': destination_without_via,
            'destination_via_only': destination_via_only,
            'line_disassembledName_route': line_disassembledName_route,
            'dervied_platform': derived_platform,
            'minutes_to_departure': minutes_to_departure,
            'derived_mode_of_transport_name': derived_mode_of_transport_name,
            'isRealtimeControlled': isRealtimeControlled
    })

    return extracted_and_flattened_json

def print_in_terminal(every_departure):
    # Define color codes for terminal printing
    colors = {
        "train": "\033[33m",  # Yellow for trains
        "light_rail": "\033[31m",  # Red for light rails
        "ferry": "\033[32m",  # Green for ferries
        "bus": "\033[34m",  # Blue for buses
        "school bus": "\033[34m",  # Blue for school buses
        "metro": "\033[36m",  # Cyan for metros
        "coach": "\033[35m",  # Magenta for coaches
        "reset": "\033[0m"  # Reset to default; stop printing in color
    }

    # Printing for terminal using color codes
    print(f"Found {len(every_departure)} departures")
    print_iterator = 1
    for departure in every_departure:
        type_of_transport = departure["derived_mode_of_transport_name"]
        line_colour = colors.get(type_of_transport, colors["reset"])
        
        # Adjust column widths for consistent spacing
        print(
            f"{print_iterator:<3} "
            f"{line_colour}Departure from {departure['line_disassembledName_route']:<25} "
            f"{departure['dervied_platform']:<30} "
            f"{departure['destination_without_via']:<25} "
            f"{departure['destination_via_only'] or '':<20} "
            f"{departure['minutes_to_departure']:>4} min "
            f"Line: {departure['line_disassembledName_route']:<4}{colors['reset']}"
        )
        
        print_iterator += 1

def write_departures_to_json(departures, filename=OUTPUT_JSON_PATH):
    """Write the departures list to a JSON file."""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(departures, f, ensure_ascii=False, indent=4)
    print(f"Departures written to {filename}")

def main():
    every_departure = []

    # Get the departures for each station in the stops_to_show stops
    for station in stops_to_show:
        for mode in station["modes"]:
            routes_to_exclude = mode.get("routes_to_exclude", [])  # Get routes_to_exclude if it exists, otherwise use an empty list
            departures = get_departures_from_api_response(
                station["station_name"],
                station["stop_id"],
                mode,
                routes_to_exclude
            )
            every_departure.extend(departures)

    # Sort the list of departures by minutes until departure
    every_departure.sort(key=lambda x: x["minutes_to_departure"])

    # Exclude departures that are less than 0 minutes until departure
    every_departure = [departure for departure in every_departure if departure["minutes_to_departure"] >= 0]

    # Exclude departures that are more than 120 minutes away
    every_departure = [departure for departure in every_departure if departure["minutes_to_departure"] <= 120]

    # Print the departures in the terminal
    print_in_terminal(every_departure)

    # Write departures to JSON file
    write_departures_to_json(every_departure, OUTPUT_JSON_PATH)

# Can run this script continously with error handling
# while True:
#     max_error = 3
#     try:
#         main()
#         print("Waiting 1 minute before refreshing...\n")
#         time.sleep(60)
#     except exception as e:
#         print(f"An error occurred: {e}")
#         max_error -= 1
#         if max_error <= 0:
#             print("Maximum retry attempts reached. Exiting script.")
            
#             break
#         print("Error: Waiting 1 minute before retrying...\n")
#         time.sleep(60)

# Or just run once, on a cron schedule for only a specific time period
if __name__ == "__main__":
    main()