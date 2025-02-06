import app

def main():
    print("\n🌡️  ICE FORMATION CALCULATOR  🌡️\n")
    lat = input("Enter latitude (default 47.83): ") or "47.83"
    lon = input("Enter longitude (default -59.21): ") or "-59.21"

    print("\nFetching weather and tide data...\n")
    past_weather = app.fetch_past_weather(lat, lon)
    current_weather = app.fetch_current_weather(lat, lon)
    tide_data = app.fetch_tide_data(lat, lon)

    weather_data = past_weather + current_weather
    total_ice_inches, report_data = app.calculate_ice_formation(weather_data, tide_data, lat, lon)

    print("\n" + "=" * 60)
    print(f"🌍 Location: Latitude {lat}, Longitude {lon}")
    print("=" * 60)
    print(f"{'Date':<12}{'Min (°C)':<10}{'Max (°C)':<10}{'Wind (km/h)':<12}{'Snow (cm)':<10}{'Tide (m)':<10}{'Ice Growth (in)':<15}")
    print("-" * 80)
    for entry in report_data:
        print(f"{entry[0]:<12}{entry[1]:<10}{entry[2]:<10}{entry[3]:<12}{entry[4]:<10}{entry[5]:<10.2f}{entry[6]:<15}")
    print(f"\n✅ Total Ice Formation Over 7 Days: {total_ice_inches} inches")
    print("=" * 60)

if __name__ == "__main__":
    main()
