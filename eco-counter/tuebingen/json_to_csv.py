#!/usr/bin/env python3
"""
Convert JSON traffic data files to CSV format.
Input: JSON files with timestamp and traffic.counts structure
Output: CSV files with timestamp,counts columns
"""

import json
import csv
import argparse
from pathlib import Path


def json_to_csv(input_file, output_file=None, overwrite=False):
    """
    Convert a JSON file to CSV format.
    
    Args:
        input_file: Path to input JSON file
        output_file: Path to output CSV file (optional)
        overwrite: If True, overwrite existing output file
    """
    input_path = Path(input_file)
    
    # Generate output filename if not provided
    if output_file is None:
        output_file = input_path.parent / f"{input_path.stem}.csv"
    else:
        output_file = Path(output_file)
    
    # Check if output file exists
    if output_file.exists() and not overwrite:
        print(f"Error: Output file {output_file} already exists. Use --overwrite to replace it.")
        return
    
    # Read JSON data
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Input file {input_path} not found.")
        return
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {input_path}: {e}")
        return
    
    # Write CSV data
    try:
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write header
            writer.writerow(['timestamp', 'counts'])
            
            # Write data rows
            for entry in data:
                timestamp = entry.get('timestamp', '')
                counts = entry.get('traffic', {}).get('counts', '')
                writer.writerow([timestamp, counts])
        
        print(f"Successfully converted {input_path} to {output_file}")
        print(f"Total records: {len(data)}")
    
    except Exception as e:
        print(f"Error writing to {output_file}: {e}")


def main():
    parser = argparse.ArgumentParser(
        description='Convert JSON traffic data files to CSV format'
    )
    parser.add_argument(
        '--input', '-i',
        required=True,
        help='Input JSON file path'
    )
    parser.add_argument(
        '--output', '-o',
        help='Output CSV file path (default: <input_name>_bike.csv)'
    )
    parser.add_argument(
        '--overwrite',
        action='store_true',
        help='Overwrite existing output file'
    )
    
    args = parser.parse_args()
    
    json_to_csv(args.input, args.output, args.overwrite)


if __name__ == '__main__':
    main()
