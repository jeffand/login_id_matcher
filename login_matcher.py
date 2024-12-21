#!/usr/bin/env python3

import csv

def generate_login_permutations(first_name, last_name):
    """Generate various possible login ID permutations from a first and last name."""
    # Convert names to lowercase and remove spaces
    first = first_name.lower().strip()
    last = last_name.lower().strip()
    
    permutations = [
        first + last,                    # johnsmith
        first + "." + last,              # john.smith
        first[0] + last,                 # jsmith
        first + last[0],                 # johns
        first[:3] + last[:3],            # johsmi
        last + first,                    # smithjohn
        last + "." + first,              # smith.john
        last + first[0],                 # smithj
        first + str(len(last)),          # john5
        first[0] + "." + last,           # j.smith
        first[:3] + "." + last[:3],      # joh.smi
        first + "_" + last,              # john_smith
        last + "_" + first,              # smith_john
        first[0] + "_" + last,           # j_smith
        first[:2] + last[:3],            # josmi
        first[:4] + last[:2],            # johnsm
        first + last[:4],                # johnsmit
        last[:4] + first[:4],            # smitjohn
        first[0] + last[:4],             # jsmit
        first[:4] + last[0],             # johns
        first[0] + first[-1] + last[0] + last[-1],  # jhsh
        first[:2] + last[:2]             # josm
    ]
    
    # Remove duplicates while preserving order
    return list(dict.fromkeys(permutations))

def find_matching_logins(names_list, existing_logins):
    """
    Find matching login IDs for a list of names.
    
    Args:
        names_list: List of tuples containing (first_name, last_name)
        existing_logins: Dictionary mapping login IDs to their additional fields
    
    Returns:
        Dictionary with two keys:
        - 'matches': Dictionary mapping (first_name, last_name) to list of matching login data
        - 'non_matches': List of login data that didn't match any names
    """
    matches = {}
    existing_login_ids = set(existing_logins.keys())
    matched_logins = set()
    
    for first_name, last_name in names_list:
        possible_logins = generate_login_permutations(first_name, last_name)
        found_matches = [
            login for login in possible_logins 
            if login in existing_login_ids
        ]
        if found_matches:
            matches[(first_name, last_name)] = [
                existing_logins[login] for login in found_matches
            ]
            matched_logins.update(found_matches)
    
    # Find non-matching logins
    non_matches = {
        login: data 
        for login, data in existing_logins.items() 
        if login not in matched_logins
    }
    
    return {'matches': matches, 'non_matches': non_matches}

def read_names_from_csv(csv_file):
    """Read names from a CSV file containing first and last names."""
    names = []
    with open(csv_file, 'r') as f:
        reader = csv.reader(f)
        next(reader, None)  # Skip header row if it exists
        for row in reader:
            if len(row) >= 2:
                first_name = row[0].strip()
                last_name = row[1].strip()
                names.append((first_name, last_name))
    return names

def read_logins_from_csv(csv_file):
    """Read login IDs and additional fields from a CSV file.
    
    Expected CSV format:
    Login ID, Field1, Field2, ...
    login1, value1, value2, ...
    
    To add additional fields:
    1. Ensure your CSV file has headers for all fields
    2. Each row should contain the login ID in the first column, followed by additional fields
    3. All fields from the row will be stored in a dictionary with the header as the key
    """
    logins = {}  # Changed to dictionary to store additional fields
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # First column name is used as login ID field
            login_id_field = reader.fieldnames[0]
            if row[login_id_field]:  # Check if login ID exists
                login = row[login_id_field].strip()
                if login:  # Store all fields for this login
                    logins[login] = row
    return logins

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Match login IDs with names')
    parser.add_argument('names_file', help='CSV file containing first and last names')
    parser.add_argument('logins_file', help='CSV file containing existing login IDs')
    parser.add_argument('--show-non-matches', action='store_true', 
                      help='Display login IDs that did not match any names')
    parser.add_argument('--show-all-fields', action='store_true',
                      help='Display all fields from the login IDs file, not just the ID')
    
    args = parser.parse_args()
    
    names = read_names_from_csv(args.names_file)
    existing_logins = read_logins_from_csv(args.logins_file)
    results = find_matching_logins(names, existing_logins)
    
    # Print matching logins
    for matches in results['matches'].values():
        for login_data in matches:
            if args.show_all_fields:
                print(','.join(login_data.values()))
            else:
                print(login_data[next(iter(login_data.keys()))])  # Print just the login ID
    
    # Print non-matching logins if requested
    if args.show_non_matches:
        if results['matches']:  # If we printed matches, add a separator
            print("---")
        for login_data in results['non_matches'].values():
            if args.show_all_fields:
                print(','.join(login_data.values()))
            else:
                print(login_data[next(iter(login_data.keys()))])  # Print just the login ID

if __name__ == '__main__':
    main()
