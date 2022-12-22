import argparse

from fetch import get_data, get_station_data, get_stations


def main():
    parser = argparse.ArgumentParser(description='Fetch weather data')

    parser.add_argument('--station_id', help='Station ID', required=False)
    parser.add_argument('--start_date', help='Start date')
    parser.add_argument('--end_date', help='End date')
    parser.add_argument('--elements', help='Elements', required=False)

    ## Examples
    # python cli.py --start_date 2018-01-01 --end_date 2018-01-02 --elements TMAX,TMIN

    args = parser.parse_args()
    print(args.start_date)
    print(args.end_date)
    print(args.elements)

    stations = get_stations() if not args.station_id else [args.station_id]
    # e.g., {'mindate': '1983-03-04', 'maxdate': '2022-12-13', 'name': 'Abu Dhabi, AE', 'datacoverage': 0.84, 'id': 'CITY:AE000001'}
    # The data coverage is the percentage of the time period for which data is available for this station.

    for station in stations:
        print(station)
        print(get_station_data(station["id"], args.start_date, args.end_date))


if __name__ == '__main__':
    main()