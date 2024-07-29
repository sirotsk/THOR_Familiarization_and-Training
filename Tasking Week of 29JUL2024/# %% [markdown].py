# %% [markdown]
# <style>
#     .main-header {
#         font-family: Courier, monospace;
#         font-size: 96px; /* Increased font size */
#         text-align: center;
#         color: #00FF00;
#     }
#     .sub-header {
#         font-family: Courier, monospace;
#         font-size: 72px; /* Increased font size */
#         text-align: center;
#         color: #00FF00;
#     }
#     .cursor {
#         font-family: Courier, monospace;
#         font-size: 72px; /* Increased font size to match sub-header */
#         text-align: center;
#         color: #00FF00;
#         display: inline;
#         animation: blink 1s steps(2, start) infinite;
#     }
#     @keyframes blink {
#         to {
#             visibility: hidden;
#         }
#     }
# </style>
# 
# <div class="main-header">
#     THOR - Site Script
# </div>
# <div class="sub-header">
#     autotrader.com<span class="cursor">_</span>
# </div>
# 

# %% [markdown]
# ## Imports

# %%
import time
from datetime import datetime, timedelta
import pandas as pd
import json
import requests

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.options.mode.chained_assignment = None

# %% [markdown]
# ## All Autotrader Functions

# %% [markdown]
# ### Check if IP is blocked

# %%
def check_proxy(session, ip, timeout=5):
    """
    Check if the proxy is working by comparing the reported IP with the expected IP.

    Args:
        session (requests.Session): The session with the proxy set.
        ip (str): The expected IP address of the proxy.
        timeout (int, optional): The timeout for the request in seconds. Default is 5 seconds.

    Returns:
        bool: True if the proxy IP matches the reported IP, False otherwise.
    """
    print('Function: check_proxy')


    try:
        response = session.get('https://icanhazip.com', timeout=timeout)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        reported_ip = response.text.strip()
        print(f'Successful response from icanhazip.com. Reported IP: {reported_ip}')
    except requests.Timeout:
        print(f'Timeout error: The request took longer than {timeout} seconds.')
        reported_ip = ''
    except requests.RequestException as e:
        print(f'Error setting proxy or fetching IP: {e}')
        reported_ip = ''

    print(f'Proxy IP: {ip} - Reported IP: {reported_ip}')
    return ip.strip() == reported_ip


def check_blocked(session, timeout=5):
    """
    Check if a session request to Autotrader is blocked.

    This function attempts to retrieve data from a specified Autotrader URL. 
    Iby calling this api r.

    Args:
        session (requests.Session): The session object to use for the request.
        timeout (int, optional): The timeout duration for the request in seconds. Defaults to 5.

    Returns:
        tuple: A tuple containing a boolean indicating if the request was blocked, 
               and a dictionary with error details if the request was blocked or failed.
    """
    print('Function: check_blocked')


    checkpoint_data = {
        "ErrorName": "Blocked",
        "ErrorTime": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "ErrorDescription": "Error loading search page",
    }

    try:
        response = session.get('https://www.autotrader.com/rest/lsc/modelinfo/457775', timeout=timeout)
        response.raise_for_status()  # Raises an HTTPError for bad responses
    except requests.Timeout:
        print(f'Timeout error: The request took longer than {timeout} seconds.')
        checkpoint_data["ErrorDescription"] = "Timeout error while loading search page"
        return True, checkpoint_data
    except requests.RequestException as e:
        print(f'Error fetching Test Data: {e}')
        return True, checkpoint_data

    try:
        data = json.loads(response.text)['title']
        print(f'Successful response from Autotrader. Test Data: {data}') #Should be "2024 Tesla Cybertruck"
    except (json.JSONDecodeError, KeyError) as e:
        print(f'Error parsing response JSON: {e}')
        return True, checkpoint_data

    return False, {}

# %% [markdown]
# ### Autotrader Searching Functions

# %%
def GetSearchListings(session, search_terms, timeout=(5, 5), sleep_time=5, max_pages=1):
    """
    Fetches search listings from AutoTrader based on specified search criteria.

    Parameters:
    - session: A requests.Session object for making HTTP requests.
    - search_terms: A dictionary containing search parameters including:
        - 'Max Year': Maximum year of the vehicles.
        - 'Max Miles': Maximum mileage of the vehicles.
        - 'Model': Model code of the vehicles.
        - 'Min Year': Minimum year of the vehicles.
        - 'Fuel Type': Fuel type of the vehicles.
        - 'Make': Make code of the vehicles.
    - timeout: A tuple specifying the connect and read timeout durations in seconds (default is (5, 5)).
    - sleep_time: Time to wait between requests in seconds (default is 5).
    - max_pages: Maximum number of pages to fetch (default is 1).

    Returns:
    - A tuple containing:
        - search_results: A DataFrame with the search results.
        - errors: A list of errors encountered during the search.
    """
    print("Function: GetSearchListings")


    url = "https://www.autotrader.com/rest/lsc/listing"

    headers = {
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "content-type": "application/json",
        "newrelic": "eyJ2IjpbMCwxXSwiZCI6eyJ0eSI6IkJyb3dzZXIiLCJhYyI6IjE1NDM2NzAiLCJhcCI6IjkxMDMyNjU3OSIsImlkIjoiNjljYTZmNzQ1NWJiZDFhZSIsInRyIjoiNTVjZTdiMWE0YWYzMGFmOTM0NzczMTJmMGI4YTc5ODIiLCJ0aSI6MTcxOTYzMDk5MjQ3MCwidGsiOiIxMTkwODkzIn19",
        "priority": "u=1, i",
        "sec-ch-ua": "\"Not/A)Brand\";v=\"8\", \"Chromium\";v=\"126\", \"Google Chrome\";v=\"126\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "traceparent": "00-55ce7b1a4af30af93477312f0b8a7982-69ca6f7455bbd1ae-01",
        "tracestate": "1190893@nr=0-1-1543670-910326579-69ca6f7455bbd1ae----1719630992470",
        # "referrer": "https://www.autotrader.com/cars-for-sale/awd-4wd/diesel/ford?endYear=2003&isNewSearch=true&maxMileage=150000&modelCodeList=EXCURSION%2CF250%2CF350&sortBy=datelistedDESC&startYear=1994&searchRadius=0",
        "referrerPolicy": "unsafe-url",
        "body": None,
        "method": "GET",
        "mode": "cors",
        "credentials": "include"
    }

    num_records = 100
    first_record = 0
    page_num = 1
    new_search = True
    results_returned = 0
    total_returned = 0
    results_count = 1000
    search_results = pd.DataFrame()
    errors = []
    while total_returned < results_count and page_num <= max_pages:

        search_keys = {
            "endYear": 'Max Year',
            "mileage": 'Max Miles',
            "modelCode": 'Model',
            "startYear": 'Min Year',
            "trimCode": 'Trim',
            "driveGroup": 'Drive',
            "fuelTypeGroup": 'Fuel Type',
            "makeCode": 'Make'
        }

        params = {
            key: search_terms[value]
            for key, value in search_keys.items()
            if value in search_terms
        }

        # Add the remaining fixed parameters
        params.update({
            "firstRecord": first_record,
            "newSearch": new_search,
            "sortBy": "datelistedDESC",
            "searchRadius": "0",
            "zip": "63025",
            "state": "MO",
            "city": "Eureka",
            "dma": "[object Object]",
            "listingType": "USED",
            "channel": "ATC",
            "relevanceConfig": "relevance-v3",
            "pixallId": "fS84p6V6wpKLFEWKTMNdzW8G",
            "stats": "year,derivedprice",
            "numRecords": num_records
        })
        print(params)
        # params = {
        #     "endYear": "2003",
        #     "firstRecord": first_record,
        #     "mileage": "150000",
        #     "modelCode": "EXCURSION,F250,F350",
        #     "newSearch": new_search,
        #     "sortBy": "datelistedDESC",
        #     "startYear": "1994",
        #     "searchRadius": "0",
        #     "driveGroup": "AWD4WD",
        #     "fuelTypeGroup": "DSL",
        #     "makeCode": "FORD",
        #     "zip": "63025",
        #     "state": "MO",
        #     "city": "Eureka",
        #     "dma": "[object Object]",
        #     "listingType": "USED",
        #     "channel": "ATC",
        #     "relevanceConfig": "relevance-v3",
        #     "pixallId": "fS84p6V6wpKLFEWKTMNdzW8G",
        #     "stats": "year,derivedprice",
        #     "numRecords": num_records
        # }
        
        try:
            # Perform the GET request
            response = session.get(url, params=params, headers=headers, cookies=None, timeout=timeout)
            response.raise_for_status()  # Raises an HTTPError for bad responses
            print(f'Successful response for page {page_num}')
        except requests.Timeout:
            error_info = {
                "ErrorName": "Timeout",
                "ErrorTime": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "ErrorDescription": f'Timeout error on page {page_num}'
            }
            print(error_info["ErrorDescription"])
            errors.append(error_info)
            break  # Exit loop on timeout
        except requests.RequestException as e:
            error_info = {
                "ErrorName": "RequestException",
                "ErrorTime": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "ErrorDescription": f'Error on page {page_num}: {e}'
            }
            print(error_info["ErrorDescription"])
            errors.append(error_info)
            break  # Exit loop on request exception

        try:
            json_data = response.json()
            json_items = json_data['listings']
            results_returned = len(json_items)
            total_returned += results_returned
            results_count = json_data['totalResultCount']
            print(f'Page {page_num} Returned: {results_returned} Total: {total_returned} results so far out of {results_count} total.')
        except (json.JSONDecodeError, KeyError) as e:
            error_info = {
                "ErrorName": "JSONDecodeError" if isinstance(e, json.JSONDecodeError) else "KeyError",
                "ErrorTime": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "ErrorDescription": f'Error parsing response JSON on page {page_num}: {e}'
            }
            print(error_info["ErrorDescription"])
            errors.append(error_info)
            break  # Exit loop on JSON error

        if not results_returned:
            print('No results returned')
            break # Exit loop on no results
        elif total_returned < results_count:
            page_num += 1
            first_record += results_returned
            params['newSearch'] = False
            params['firstRecord'] = first_record
            time.sleep(sleep_time) # Sleep only if there are more results

        search_results = pd.concat([search_results, pd.json_normalize(json_items)])

        print(search_results.shape)
        if not search_results.empty and 'id' in search_results.columns:
            search_results.reset_index(drop=True, inplace=True)
            search_results = search_results.drop_duplicates(subset='id')
            print(search_results.shape)

            search_url = ""#search_terms['Search Url'] #'"' + '", "'.join(body['options']['body']) + '"'
            search_results['thor_timestamp'] = int(time.time())
            search_results['thor_website'] = "autotrader.com"
            search_results['thor_search_url'] = search_url
            search_results['thor_full_listing_url'] = 'https://www.autotrader.com/cars-for-sale/vehicle/' + search_results['id'].astype(str)
            search_results['thor_listing_url'] = 'https://www.autotrader.com/cars-for-sale/vehicle/' + search_results['id'].astype(str)

    return search_results, errors


def GetListingDetails(session, listing_ids, timeout=(5, 5), sleep_time=5):
    """
    Fetches detailed information for specific listings from AutoTrader based on listing IDs.

    Parameters:
    - session: A requests.Session object for making HTTP requests.
    - listing_ids: A list of listing IDs for which details are to be fetched.
    - timeout: A tuple specifying the connect and read timeout durations in seconds (default is (5, 5)).
    - sleep_time: Time to wait between requests in seconds (default is 5).

    Returns:
    - A tuple containing:
        - listing_details: A DataFrame with detailed information of the listings.
        - errors: A list of errors encountered during the process.
    """
    print('Function: GetListingDetails')


    params = {}
    headers = {
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "content-type": "application/json",
        "newrelic": "eyJ2IjpbMCwxXSwiZCI6eyJ0eSI6IkJyb3dzZXIiLCJhYyI6IjE1NDM2NzAiLCJhcCI6IjkxMDMwODc3MCIsImlkIjoiOGFkYmRhYmUxZjA3ZWUzNCIsInRyIjoiZWZiNDUyNTNkZTI4MDg2M2FmZGNmZDEzYjhjYTgyMDMiLCJ0aSI6MTcxOTY4MTU3MzEwNCwidGsiOiIxMTkwODkzIn19",
        "priority": "u=1, i",
        "sec-ch-ua": "\"Not/A)Brand\";v=\"8\", \"Chromium\";v=\"126\", \"Google Chrome\";v=\"126\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "traceparent": "00-efb45253de280863afdcfd13b8ca8203-8adbdabe1f07ee34-01",
        "tracestate": "1190893@nr=0-1-1543670-910308770-8adbdabe1f07ee34----1719681573104"
    }

    errors = []
    listing_details = pd.DataFrame()
    json_items = []

    for index, id in enumerate(listing_ids):
        url = f"https://www.autotrader.com/rest/lsc/listing/id/{id}"
        try:
            response = session.get(url, params=params, headers=headers, cookies=None, timeout=timeout)
            response.raise_for_status()  # Raises an HTTPError for bad responses
            print(f'Successful response for page')
        except requests.Timeout:
            error_info = {
                "ErrorName": "Timeout",
                "ErrorTime": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "ErrorDescription": f'Timeout error on page'
            }
            print(error_info["ErrorDescription"])
            errors.append(error_info)
            return listing_details, errors
        except requests.RequestException as e:
            error_info = {
                "ErrorName": "RequestException",
                "ErrorTime": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "ErrorDescription": f'Error on page: {e}'
            }
            print(error_info["ErrorDescription"])
            errors.append(error_info)
            return listing_details, errors

        try:
            json_data = response.json()
            json_items = json_data['listings']
            results_returned = len(json_items)
            # results_count = json_data['totalResultCount']
            print(f'Returned: {results_returned} out of {len(listing_ids)} total.')
        except (json.JSONDecodeError, KeyError) as e:
            error_info = {
                "ErrorName": "JSONDecodeError" if isinstance(e, json.JSONDecodeError) else "KeyError",
                "ErrorTime": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "ErrorDescription": f'Error parsing response JSON: {e}'
            }
            print(error_info["ErrorDescription"])
            errors.append(error_info)
            return listing_details, errors

        if results_returned:
            listing_details = pd.concat([listing_details, pd.json_normalize(json_items)])
            listing_details.reset_index(drop=True, inplace=True)
            listing_details = listing_details.drop_duplicates(subset='id')
            print(listing_details.shape)
            
            print('Adding standard fields to the DataFrame.')
            listing_details['thor_timestamp'] = int(time.time())
            listing_details['thor_website'] = "autotrader.com"
            
        
        if not index == len(listing_ids) - 1:
            time.sleep(sleep_time)
 
    return listing_details, errors

# %% [markdown]
# ## Standard Formatting

# %%


def FormatAggregator(ids, results, details, custom, source_key):
    """
    Aggregates and formats data from multiple DataFrames based on provided IDs and source key mapping.

    Parameters:
    ids (list): List of IDs to iterate over and extract data for.
    results (pd.DataFrame): DataFrame containing results data (not directly used in the function but assumed to be part of locals()).
    details (pd.DataFrame): DataFrame containing details data (not directly used in the function but assumed to be part of locals()).
    custom (pd.DataFrame): Default DataFrame to use if no specific DataFrame is mentioned in source_key.
    source_key (dict): Dictionary mapping target DataFrame columns to source DataFrame columns. The key is the target column name, and the value is a dictionary with the source DataFrame name as key and source column name as value. If value is an empty dictionary, the target column will be filled with None.

    Returns:
    pd.DataFrame: A DataFrame with the aggregated and formatted data.
    
    Example:
    source_key = {
        'column1': {'results': 'source_column1'},
        'column2': {'details': 'source_column2'},
        'column3': {},  # This will be filled with None
        'column4': 'custom',  # This will default to the custom DataFrame
    }

    Notes:
    - The function assumes that the DataFrames (results, details) are present in the local scope.
    - If a source column specified in source_key is not present in the corresponding DataFrame, the resulting column will be filled with None.
    - The function concatenates the formatted data into a single DataFrame.
    """
    print('Function: FormatAggregator')


    # Create an empty DataFrame with columns from the keys of source_key
    formatted_df = pd.DataFrame(columns=source_key.keys())
    formatted_data = []
    
    # Iterate over each id
    for id_ in ids:
        row = {}
        # Iterate over each key in source_key
        for key, value in source_key.items():
            if not value:  # If value is an empty dictionary
                row[key] = value
                continue
            
            if isinstance(value, dict):
                # Extract the DataFrame and column name
                df_name, column_name = list(value.items())[0]
                df = locals().get(df_name)  # Get the DataFrame by its name
                
                if df is None or column_name not in df.columns:
                    row[key] = None
                else:
                    # Extract the value from the DataFrame using the id
                    match = df.loc[df['id'] == id_, column_name]
                    row[key] = match.values[0] if not match.empty else None
            else:
                if key == 'id': # If id, use the current id
                    row[key] = id_
                else:
                    # If the value is not a dictionary, use the provided value directly
                    row[key] = value
        
        # Append the row to the formatted DataFrame
        formatted_data.append(row)
    
    formatted_df = pd.concat([formatted_df, pd.DataFrame(formatted_data)])
    
    return formatted_df



def Format_Output(current_task, current_user, search_results, listing_details, ids):
    """
    Formats and aggregates output data for vehicle listings based on various input parameters.

    Parameters:
    - current_task (dict): Information about the current task, including task name and host.
    - current_user (dict): Information about the current user, including account details.
    - search_results (DataFrame): DataFrame containing search results with details such as URL, creation time, fuel type, etc.
    - listing_details (DataFrame): DataFrame containing detailed information about listings, including photos, descriptions, and location.
    - ids (list): List of IDs corresponding to the vehicle listings.

    Returns:
    - tuple: A tuple containing the following elements:
        - search_results (DataFrame): The original search results DataFrame.
        - listing_details (DataFrame): The original listing details DataFrame.
        - Listings (DataFrame): Aggregated and formatted listings DataFrame.
        - task_telemetry (DataFrame): DataFrame containing task telemetry information.
        - user_telemetry (DataFrame): DataFrame containing user telemetry information.

    Notes:
    - The function uses a source key dictionary to map specific fields to their corresponding sources (custom, results, or details).
    - It ensures required columns are present in the listing details before processing.
    - Custom data is created by extracting and transforming specific fields such as images, title, and location.
    - The final Listings DataFrame is generated using the FormatAggregator function.
    - Task telemetry and user telemetry data are also created and returned as part of the output.
    """
    print('Function: Format_Output')

    
    source_key = {
        'title': {'results': 'title'},
        'id': 'id',
        'link': {'results': 'thor_listing_url'},
        'creation_time': {'custom': 'creation_time'},
        'vehicle_condition': {'results': 'listingType'},
        'vehicle_color': {'results': 'color.exteriorColorSimple'},
        'fuel_type': {'results': 'fuelType.name'},
        'paid_off': {'results': 'financingTypePSX'},
        'make': {'results': 'makeCode'},
        'model': {'results': 'modelCode'},
        'year': {'results': 'year'},
        'number_owners': '',
        'seller_type': {'results': 'owner.privateSeller'},
        'vehicle_trim': {'results': 'trim.name'},
        'vin': {'results': 'vin'},
        'listing_photos': {'custom': 'images'},
        'seller_name': {'results': 'owner.name'},
        'location': {'custom': 'location'},
        'location_city': {'results': 'owner.location.address.city'},
        'location_state': {'results': 'owner.location.address.state'},
        'location_country': '',
        'description': {'details': 'fullDescription'},
        'price': {'results': 'pricingDetail.salePrice'},
        'strikethrough_price': '',
        'odometer_unit': {'results': 'mileage.label'},
        'odometer_value': {'results': 'mileage.value'},
        'thor_timestamp': {'results': 'thor_timestamp'},
        'thor_website': "autotrader.com",
        'thor_mmr': False,
        'thor_task': f"{current_task}",
        'thor_user': f"{current_user}",
        'Task': current_task['TaskName'],
        'Host': current_task["Host"],
        'Account': current_user["AccountInfo"]["AccountID"]
    }


    results_required_columns = ['id', 'owner.location.address.city', 'owner.location.address.state', 'pricingHistory']
    if all(col in search_results.columns for col in results_required_columns):
        if not search_results.empty:
            custom_data = search_results[results_required_columns].copy()

            custom_data['location'] = custom_data['owner.location.address.city'] + ", " + custom_data['owner.location.address.state']

            # custom_data['strikethrough_price'] = custom_data['pricingHistory'].apply(lambda prices_data: \
            #     max(
            #         [entry for entry in prices_data if entry['dateUpdated'] != 'Price Today'],
            #         default=[{'price': None}],  # Default value for empty lists or None
            #         key=lambda entry: pd.to_datetime(entry['dateUpdated'], format='%d.%m.%Y', errors='coerce')
            #     )['price'] if prices_data else None
            # )

        else:
            custom_data = pd.DataFrame(columns=results_required_columns)
    else:
        custom_data = pd.DataFrame(columns=results_required_columns)
   
   
    details_required_columns = ['id', 'lastModified', 'images.sources']
    if all(col in listing_details.columns for col in details_required_columns):
        if not listing_details.empty:
            custom_data = pd.merge(listing_details[details_required_columns], custom_data, on='id', how='left')

            custom_data['creation_time'] = custom_data['lastModified'].apply(lambda x: int(datetime.fromisoformat(x).timestamp()))

            custom_data['images'] = custom_data['images.sources'].apply(
                lambda photo_list: [photo['src'] for photo in photo_list] if isinstance(photo_list, list) else None
            )
        else:
            custom_data = pd.DataFrame(columns=details_required_columns)
    else:
        custom_data = pd.DataFrame(columns=details_required_columns)

    Listings = FormatAggregator(ids, search_results, listing_details, custom_data, source_key)

    # Create task_telemetry/Will Be phased out
    task_telemetry = Listings
    
    #Create user_telemetry
    user_telemetry_data = {
        "TaskName": current_task["TaskName"],
        "Host": current_task["Host"],
        "AccountID": current_user["AccountInfo"]["AccountID"]
    }

    user_telemetry = pd.DataFrame([user_telemetry_data])

    return search_results, listing_details, Listings, task_telemetry, user_telemetry

# %% [markdown]
# ## Run Task

# %%
def Task_Run(driver, current_profile, current_task, current_user, results_check_callback, user_timer):
    """
    Executes a task using the given parameters and handles session management, proxy settings, 
    and result processing.

    Args:
        driver (object): The driver used for performing tasks.
        current_profile (dict): The current profile details.
        current_task (dict): The current task details including search terms.
        current_user (dict): Information about the current user including proxy details.
        results_check_callback (function): Callback function to check and compare results.
        user_timer (object): Timer object to track user account activity.

    Yields:
        tuple: A tuple containing the following elements:
            - search_results (DataFrame): DataFrame containing search results.
            - listing_details (DataFrame): DataFrame containing details of listings.
            - Listings (list): List of processed listings.
            - task_telemetry (dict): Dictionary containing task telemetry data.
            - user_telemetry (dict): Dictionary containing user telemetry data.
            - errors (dict): Dictionary containing error information if any issues are encountered.

    The function performs the following steps:
    1. Tracks how long the user account has been active using `user_timer.status()`.
    2. Creates a session object with updated headers.
    3. Configures the session to use a proxy if specified in `current_user`.
    4. Checks if the session is blocked using `check_blocked` function.
    5. If blocked, formats and yields the final results with errors.
    6. Retrieves search listings using `GetSearchListings`.
    7. Compares the search results with existing data using `results_check_callback`.
    8. Retrieves details for new listings if any.
    9. Formats and yields the final results including search results, listing details, 
       listings, task telemetry, user telemetry, and errors.
    """
    print('Main Funtion: Task_Run')


    #How to track how long the user account has been active
    user_status = user_timer.status()
    
    # Create a session object
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    })

    if current_user['ProxyInfo']['ProxyIp'] != '':
        proxy = {
            'http': current_user['ProxyInfo']['ProxyIp'] + ':' + current_user['ProxyInfo']['ProxyPort'],
            'https':current_user['ProxyInfo']['ProxyIp'] + ':' + current_user['ProxyInfo']['ProxyPort']
        }

        # Configure the session to use the proxy
        session.proxies.update(proxy)
        proxy_set = check_proxy(session, current_user['ProxyInfo']['ProxyIp']) 
        
        print('Proxy Set: ', proxy_set)
    else:
        proxy_set = True


    #Check if Blocked
    is_blocked, blocked_errors = check_blocked(session)
    print(f"is blocked: {is_blocked}")
    if is_blocked or proxy_set == False:
        errors = {"Disable": True, "error_data": [blocked_errors]}   
        print(errors)

        final_results, final_details, Listings, task_telemetry, user_telemetry = Format_Output(current_task, current_user, pd.DataFrame(), pd.DataFrame(), [])
        yield final_results, final_details, Listings, task_telemetry, user_telemetry, errors
        return


    search_results, errors = GetSearchListings(session, current_task['SearchTerms'], sleep_time=3, max_pages=3)
    print(errors)

    # Check For New Listings
    print(f"****************COMPARE DB****************** {len(search_results)} Results")
    compare_columns = {
        'id': 'id',
    }
    new_results = results_check_callback(search_results, 'autotrader.com', compare_columns)
    print(f"****************COMPARE DB Complete****************** {len(new_results)} New")

    #get list of new IDs and ensure no blanks or duplicates
    new_ids = new_results['id'].to_list()
    new_ids = [*{item for item in new_ids if item}]

    #Get listing Details
    if len(new_results) > 0:
        listing_details, errors = GetListingDetails(session, new_ids, sleep_time=2)
    else:
        listing_details = pd.DataFrame()
        
    #Format standard Output
    search_results, listing_details, Listings, task_telemetry, user_telemetry = Format_Output(current_task, current_user,  search_results, listing_details, new_ids)

    print(f"{len(search_results)} search_results")
    print(f"{len(listing_details)} listing_details")
    print(f"{len(Listings)} Listings")
    print(f"{len(task_telemetry)} task_telemetry")
    print(f"{len(user_telemetry)} user_telemetry")
    print(f"{errors} errors")
    errors = {}
    
    yield search_results, listing_details, Listings, task_telemetry, user_telemetry, errors

# %% [markdown]
# ## Testing

# %%
# def results_check(data, website, columns_map):
#     new_rows = data[:5]   #pd.DataFrame(columns=data.columns)
#     return new_rows

# class ProcessTimer:
#     def __init__(self):
#         self.start_time = time.time()
#         print(f"Process started at {self._format_time(self.start_time)}")

#     def finish(self):
#         self.end_time = time.time()
#         active_time = self.end_time - self.start_time
#         result = {
#             'start_time': self._format_time(self.start_time),
#             'end_time': self._format_time(self.end_time),
#             'active_time': str(timedelta(seconds=active_time))
#         }
#         return result

#     def status(self):
#         current_time = time.time()
#         active_time = current_time - self.start_time
#         return str(timedelta(seconds=active_time))

#     def _format_time(self, timestamp):
#         return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

    
    
# # App Settings
# app_settings = {
#     'UserProfilesPath': r'\User Profiles',
#     'PluginsPath': r'\Plugins',
#     'WebRtcName': 'WebRTC',
#     'DefaultBrowserArgs': [
#          '--disable-gpu',
#          '--disable-software-rasterizer'
#     ]
# }

# current_user = {
#     "Host": "Bot-Host-0",
#     "ProfileName": "autotrader",
#     "CheckedOut": True,
#     "ProxyInfo": {
#         "ProxyIp": "",
#         "ProxyPort": "",
#         "ProxyUsername": "",
#         "ProxyPassword": "",
#         "Description": "",
#     },
#     "BrowserInfo": {
#         "BrowserType": "Chrome",
#         "UserFolderName": "autotraderTest",
#         "Args": ['--disable-notifications'],
#         "Extensions": [],
#         "Cookies": [],
#         "UserAgent": "",
#         "WindowMaximized": False,
#         "WindowWidth": 0,
#         "WindowHight": 0,
#         "ClearCookies": False,
#         "Incognito": False,
#         "Description": ""
#     },
#     "AccountInfo": {
#         "AccountID": "autotraderTest",
#         "AccountSite": "autotrader.com",
#         "ProfileURL": "",
#         "UserName": "",
#         "AltUserName": "",
#         "Password": "",
#         "MFAKey": "",
#         "OtherData": {},
#         "Description": ""
#     },
#     "Usage": {
#         "LastActive": "0001-01-01T00:00:00",
#         "ActiveTime": "00:00:00",
#         "MaxActiveTime": "00:20:00",
#         "MinCoolDownTime": "01:00:00"
#     }
# }


# current_task = {
#   "Description": "Ford F-250/350/Excursion (1994 - 2003) (150,000 Miles)",
#   "Host": "Bot-Host-12",
#   "ProfileName": "autotrader",
#   "Schedule": {
#     "DailyEndTime": "21:59:59",
#     "DailyStartTime": "05:02:46",
#     "HitTimes": [],
#     "Interval": "00:05:00",
#     "IsActive": True
#   },
#   "ScriptName": "Task_Run_19:04:41",
#   "SearchTerms": {
#     "Drive": "",
#     "Fuel Type": "DSL",
#     "Location": "eureka-mo-63025",
#     "Make": "FORD",
#     "Max Miles": "",
#     "Max Year": "2003",
#     "Min Year": "",
#     "Model": "EXCURSION,F250,F350",
#     "Trim": ""
#   },
#   "TaskName": "AT Ford F250-350-Excursion",
#   "Website": "autotrader.com"
# }

# current_profile = {
#     "Hosts": ["Bot-Host-0"],
#     "ProfileName": 'autotrader',
#     "Website": 'autotrader.com',
#     "Script": "autotrader_scripts",
#     "Description": "Master Profile For Autotrader"
# }  


# ddd = ProcessTimer()
# for final_results, final_details, Listings, task_telemetry, user_telemetry, errors in Task_Run(None, current_profile, current_task, current_user, results_check, ddd):
#     # print('final_results')
#     # display(final_results)
#     # print('final_details')
#     # display(final_details)
#     # print('Listings')
#     # display(Listings)
#     # print('task_telemetry')
#     # display(task_telemetry)
#     # print('user_telemetry')
#     # display(user_telemetry)
#     print('errors')
#     print(errors)

# display(Listings)

# %%
# import requests

# url = "https://www.autotrader.com/rest/lsc/listing/spotlight/results"

# params = {
#     "modelCode": "M3",
#     "makeCode": "BMW",
#     "searchRadius": "50",
#     "zip": "20120",
#     "location": "[object Object]",
#     "newSearch": "true",
#     "marketExtension": "[object Object]",
#     "sortBy": "relevance",
#     "numRecords": "25",
#     "firstRecord": "0",
#     "listingTier": "Featured",
#     "numSpotlights": "1"
# }

# headers = {
#     "accept": "*/*",
#     "accept-language": "en-US,en;q=0.9",
#     "content-type": "application/json",
#     "newrelic": "eyJ2IjpbMCwxXSwiZCI6eyJ0eSI6IkJyb3dzZXIiLCJhYyI6IjE1NDM2NzAiLCJhcCI6IjkxMDMwODc3MCIsImlkIjoiMWUxYmJhYjg3ZDE2NDBlNyIsInRyIjoiZWZjYjkwYjJmOTdhOTc4MDEzYTU3ZjNhZDY0ODNiMzIiLCJ0aSI6MTcyMDQ4NTE5MDM1MSwidGsiOiIxMTkwODkzIn19",
#     "priority": "u=1, i",
#     "sec-ch-ua": "\"Not/A)Brand\";v=\"8\", \"Chromium\";v=\"126\", \"Google Chrome\";v=\"126\"",
#     "sec-ch-ua-mobile": "?0",
#     "sec-ch-ua-platform": "\"Windows\"",
#     "sec-fetch-dest": "empty",
#     "sec-fetch-mode": "cors",
#     "sec-fetch-site": "same-origin",
#     "traceparent": "00-efcb90b2f97a978013a57f3ad6483b32-1e1bbab87d1640e7-01",
#     "tracestate": "1190893@nr=0-1-1543670-910308770-1e1bbab87d1640e7----1720485190351",
#     "x-fwd-svc": "atc",
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
# }

# response = requests.get(url, headers=headers, params=params)

# print(response.text)


# %% [markdown]
# ## Notes

# %%
# Notes in order to get the API calls to show in the network tab you will need to click on a listing first then go back the the search page
# https://www.autotrader.com/cars-for-sale/awd-4wd/diesel/ford?endYear=2003&isNewSearch=true&maxMileage=150000&modelCodeList=EXCURSION%2CF250%2CF350&sortBy=datelistedDESC&startYear=1994&searchRadius=0

# %%
# ##Get Search Listings


# fetch("https://www.autotrader.com/rest/lsc/listing?endYear=2003&newSearch=true&mileage=150000&modelCode=EXCURSION%2CF250%2CF350&sortBy=datelistedDESC&startYear=1994&searchRadius=0&driveGroup=AWD4WD&fuelTypeGroup=DSL&makeCode=FORD&zip=63025&state=MO&city=Eureka&dma=%5Bobject+Object%5D&listingType=USED&channel=ATC&relevanceConfig=relevance-v3&pixallId=fS84p6V6wpKLFEWKTMNdzW8G&stats=year%2Cderivedprice", {
#   "headers": {
#     "accept": "*/*",
#     "accept-language": "en-US,en;q=0.9",
#     "content-type": "application/json",
#     "newrelic": "eyJ2IjpbMCwxXSwiZCI6eyJ0eSI6IkJyb3dzZXIiLCJhYyI6IjE1NDM2NzAiLCJhcCI6IjkxMDMyNjU3OSIsImlkIjoiNjljYTZmNzQ1NWJiZDFhZSIsInRyIjoiNTVjZTdiMWE0YWYzMGFmOTM0NzczMTJmMGI4YTc5ODIiLCJ0aSI6MTcxOTYzMDk5MjQ3MCwidGsiOiIxMTkwODkzIn19",
#     "priority": "u=1, i",
#     "sec-ch-ua": "\"Not/A)Brand\";v=\"8\", \"Chromium\";v=\"126\", \"Google Chrome\";v=\"126\"",
#     "sec-ch-ua-mobile": "?0",
#     "sec-ch-ua-platform": "\"Windows\"",
#     "sec-fetch-dest": "empty",
#     "sec-fetch-mode": "cors",
#     "sec-fetch-site": "same-origin",
#     "traceparent": "00-55ce7b1a4af30af93477312f0b8a7982-69ca6f7455bbd1ae-01",
#     "tracestate": "1190893@nr=0-1-1543670-910326579-69ca6f7455bbd1ae----1719630992470"
#   },
#   "referrer": "https://www.autotrader.com/cars-for-sale/awd-4wd/diesel/ford?endYear=2003&isNewSearch=true&maxMileage=150000&modelCodeList=EXCURSION%2CF250%2CF350&sortBy=datelistedDESC&startYear=1994&searchRadius=0",
#   "referrerPolicy": "unsafe-url",
#   "body": null,
#   "method": "GET",
#   "mode": "cors",
#   "credentials": "include"
# });

# ## Get Adds
# fetch("https://www.autotrader.com/rest/lsc/alpha/base?endYear=2003&newSearch=true&mileage=150000&modelCode=EXCURSION%2CF250%2CF350&sortBy=datelistedDESC&startYear=1994&searchRadius=0&driveGroup=AWD4WD&fuelTypeGroup=DSL&makeCode=FORD&zip=63025&state=MO&city=Eureka&dma=%5Bobject+Object%5D&listingType=USED&channel=ATC&relevanceConfig=relevance-v3&pixallId=fS84p6V6wpKLFEWKTMNdzW8G&stats=year%2Cderivedprice", {
#   "headers": {
#     "accept": "*/*",
#     "accept-language": "en-US,en;q=0.9",
#     "content-type": "application/json",
#     "newrelic": "eyJ2IjpbMCwxXSwiZCI6eyJ0eSI6IkJyb3dzZXIiLCJhYyI6IjE1NDM2NzAiLCJhcCI6IjkxMDMyNjU3OSIsImlkIjoiN2E0N2IxMzA5MmRiNjgwZSIsInRyIjoiNDYwMWMyMjA1YmVlZTM0NjUyMmQ0NTJmNWJjMThlNWYiLCJ0aSI6MTcxOTYzMDk5MjQ2MywidGsiOiIxMTkwODkzIn19",
#     "priority": "u=1, i",
#     "sec-ch-ua": "\"Not/A)Brand\";v=\"8\", \"Chromium\";v=\"126\", \"Google Chrome\";v=\"126\"",
#     "sec-ch-ua-mobile": "?0",
#     "sec-ch-ua-platform": "\"Windows\"",
#     "sec-fetch-dest": "empty",
#     "sec-fetch-mode": "cors",
#     "sec-fetch-site": "same-origin",
#     "traceparent": "00-4601c2205beee346522d452f5bc18e5f-7a47b13092db680e-01",
#     "tracestate": "1190893@nr=0-1-1543670-910326579-7a47b13092db680e----1719630992463"
#   },
#   "referrer": "https://www.autotrader.com/cars-for-sale/awd-4wd/diesel/ford?endYear=2003&isNewSearch=true&maxMileage=150000&modelCodeList=EXCURSION%2CF250%2CF350&sortBy=datelistedDESC&startYear=1994&searchRadius=0",
#   "referrerPolicy": "unsafe-url",
#   "body": null,
#   "method": "GET",
#   "mode": "cors",
#   "credentials": "include"
# });

# %%
# https://www.autotrader.com/cars-for-sale/awd-4wd/diesel/dodge?endYear=2009&isNewSearch=true&maxMileage=140000&modelCodeList=DODDW%2CRAM25002WD%2CRAM3502WD&sortBy=datelistedDESC&startYear=1989&searchRadius=0

# endYear: 2009
# newSearch: true
# mileage: 140000
# modelCode: DODDW,RAM25002WD,RAM3502WD
# sortBy: datelistedDESC
# startYear: 1989
# searchRadius: 0
# driveGroup: AWD4WD
# fuelTypeGroup: DSL
# makeCode: DODGE
# zip: 63025
# state: MO
# city: Eureka
# dma: [object Object]
# listingType: USED
# channel: ATC
# relevanceConfig: relevance-v3
# pixallId: 600ujHskdLT2xf2tvTutP39v
# stats: year,derivedprice


# {
#   "Description": "Dodge Ram 2500/3500/D Series (1989 - 2009) (140,000 Miles)",
#   "Host": "Bot-Host-12",
#   "ProfileName": "autotrader",
#   "Schedule": {
#     "DailyEndTime": "23:59:59",
#     "DailyStartTime": "05:06:40",
#     "HitTimes": [],
#     "Interval": "00:10:00",
#     "IsActive": true
#   },
#   "ScriptName": "Task_Run_23:04:30",
#   "SearchTerms": {
#     "Fuel Type": "DSL",
#     "Location": "eureka-mo-63025",
#     "Make": "DODGE",
#     "Max Miles": "140000",
#     "Max Year": "2009",
#     "Min Year": "1989",
#     "Model": "DODDW,RAM25002WD,RAM3502WD",
#     "Trim": "",
#     "Drive": "AWD4WD"
#   },
#   "TaskName": "AT Dodge Ram 2500-3500-D Series",
#   "Website": "autotrader.com"
# }

# %%
# https://www.autotrader.com/cars-for-sale/gasoline/dodge/viper?endYear=2003&mileage=200001&newSearch=true&searchRadius=0&sortBy=datelistedDESC&startYear=2017

# endYear: 2003
# mileage: 200001
# newSearch: true
# searchRadius: 0
# sortBy: datelistedDESC
# startYear: 2017
# fuelTypeGroup: GSL
# makeCode: DODGE
# modelCode: VIPER
# zip: 63025
# state: MO
# city: Eureka
# dma: %5Bobject+Object%5D
# location: %5Bobject+Object%5D
# listingType: USED
# channel: ATC
# relevanceConfig: relevance-v3
# pixallId: 600ujHskdLT2xf2tvTutP39v
# stats: year%2Cderivedprice


# {
#   "Description": "Dodge Viper (2003 - 2017) (200,000 Miles)",
#   "Host": "Bot-Host-12",
#   "ProfileName": "autotrader",
#   "Schedule": {
#     "DailyEndTime": "23:59:59",
#     "DailyStartTime": "05:08:20",
#     "HitTimes": [],
#     "Interval": "00:10:00",
#     "IsActive": true
#   },
#   "ScriptName": "Task_Run_23:04:30",
#   "SearchTerms": {
#     "Fuel Type": "GSL",
#     "Location": "eureka-mo-63025",
#     "Make": "DODGE",
#     "Max Miles": "200001",
#     "Max Year": "2003",
#     "Min Year": "2017",
#     "Model": "VIPER",
#     "Trim": "",
#     "Drive": ""
#   },
#   "TaskName": "AT Dodge Viper",
#   "Website": "autotrader.com"
# }

# %%
# https://www.autotrader.com/cars-for-sale/awd-4wd/diesel/ford?endYear=2003&isNewSearch=true&maxMileage=150000&modelCodeList=EXCURSION%2CF250%2CF350&sortBy=datelistedDESC&startYear=1994&searchRadius=0

# endYear: 2003
# newSearch: true
# mileage: 150000
# modelCode: EXCURSION%2CF250%2CF350
# sortBy: datelistedDESC
# startYear: 1994
# searchRadius: 0
# driveGroup: AWD4WD
# fuelTypeGroup: DSL
# makeCode: FORD
# zip: 63025
# state: MO
# city: Eureka
# dma: %5Bobject+Object%5D
# listingType: USED
# channel: ATC
# relevanceConfig: relevance-v3
# pixallId: 600ujHskdLT2xf2tvTutP39v
# stats: year%2Cderivedprice


# {
#   "Description": "Ford F-250/350/Excursion (1994 - 2003) (150,000 Miles)",
#   "Host": "Bot-Host-12",
#   "ProfileName": "autotrader",
#   "Schedule": {
#     "DailyEndTime": "23:59:59",
#     "DailyStartTime": "05:10:00",
#     "HitTimes": [],
#     "Interval": "00:10:00",
#     "IsActive": true
#   },
#   "ScriptName": "Task_Run_23:04:30",
#   "SearchTerms": {
#     "Fuel Type": "DSL",
#     "Location": "eureka-mo-63025",
#     "Make": "FORD",
#     "Max Miles": "150000",
#     "Max Year": "2003",
#     "Min Year": "1994",
#     "Model": "EXCURSION,F250,F350",
#     "Trim": "",
#     "Drive": "AWD4WD"
#   },
#   "TaskName": "AT Ford F250-350-Excursion",
#   "Website": "autotrader.com"
# }

# %%
# https://www.autotrader.com/cars-for-sale/awd-4wd/diesel/gmc?endYear=2007&isNewSearch=true&maxMileage=130000&modelCodeList=GMCC25PU%2CGMC3500PU&sortBy=datelistedDESC&startYear=2004&searchRadius=0

# endYear: 2007
# newSearch: true
# mileage: 130000
# modelCode: GMCC25PU%2CGMC3500PU
# sortBy: datelistedDESC
# startYear: 2004
# searchRadius: 0
# driveGroup: AWD4WD
# fuelTypeGroup: DSL
# makeCode: GMC
# zip: 63025
# state: MO
# city: Eureka
# dma: %5Bobject+Object%5D
# listingType: USED
# channel: ATC
# relevanceConfig: relevance-v3
# pixallId: 600ujHskdLT2xf2tvTutP39v
# stats: year%2Cderivedprice


# {
#   "Description": "GMC Sierra 2500/3500 (Diesel) (2004 - 2007) (130,000 Miles)",
#   "Host": "Bot-Host-12",
#   "ProfileName": "autotrader",
#   "Schedule": {
#     "DailyEndTime": "23:59:59",
#     "DailyStartTime": "05:11:40",
#     "HitTimes": [],
#     "Interval": "00:10:00",
#     "IsActive": true
#   },
#   "ScriptName": "Task_Run_23:04:30",
#   "SearchTerms": {
#     "Fuel Type": "DSL",
#     "Location": "eureka-mo-63025",
#     "Make": "GMC",
#     "Max Miles": "130000",
#     "Max Year": "2007",
#     "Min Year": "2004",
#     "Model": "GMCC25PU,GMC3500PU",
#     "Trim": "",
#     "Drive": "AWD4WD"
#   },
#   "TaskName": "AT GMC Sierra 2500-3500",
#   "Website": "autotrader.com"
# }

# %%
# https://www.autotrader.com/cars-for-sale/gasoline/jeep?endYear=2020&isNewSearch=true&maxMileage=200001&modelCodeList=grand-cherokee/trackhawk&sortBy=datelistedDESC&startYear=2021&searchRadius=0

# endYear: 2021
# mileage: 200001
# newSearch: true
# searchRadius: 0
# sortBy: datelistedDESC
# startYear: 2020
# fuelTypeGroup: GSL
# makeCode: JEEP
# modelCode: JEEPGRAND
# trimCode: JEEPGRAND|Trackhawk
# city: Eureka
# state: MO
# zip: 63025
# location: [object Object]
# dma: [object Object]
# listingType: USED
# channel: ATC
# relevanceConfig: relevance-v3
# pixallId: 600ujHskdLT2xf2tvTutP39v
# stats: year,derivedprice


# {
#   "Description": "Jeep Trackhawk (2020 - 2021) (Any Miles)",
#   "Host": "Bot-Host-12",
#   "ProfileName": "autotrader",
#   "Schedule": {
#     "DailyEndTime": "23:59:59",
#     "DailyStartTime": "05:13:20",
#     "HitTimes": [],
#     "Interval": "00:10:00",
#     "IsActive": true
#   },
#   "ScriptName": "Task_Run_23:04:30",
#   "SearchTerms": {
#     "Fuel Type": "GSL",
#     "Location": "eureka-mo-63025",
#     "Make": "JEEP",
#     "Max Miles": "",
#     "Max Year": "2020",
#     "Min Year": "2021",
#     "Model": "JEEPGRAND",
#     "Trim": "JEEPGRAND|Trackhawk",
#     "Drive": ""
#   },
#   "TaskName": "AT Jeep Trackhawk",
#   "Website": "autotrader.com"
# }

# %%
# https://www.autotrader.com/cars-for-sale/awd-4wd/diesel/chevrolet?endYear=2007&isNewSearch=true&maxMileage=130000&modelCodeList=CH3500PU%2CCHEVC25&sortBy=datelistedDESC&startYear=2004&searchRadius=0

# endYear: 2007
# newSearch: true
# mileage: 130000
# modelCode: CH3500PU%2CCHEVC25
# sortBy: datelistedDESC
# startYear: 2004
# searchRadius: 0
# driveGroup: AWD4WD
# fuelTypeGroup: DSL
# makeCode: CHEV
# zip: 63025
# state: MO
# city: Eureka
# dma: %5Bobject+Object%5D
# listingType: USED
# channel: ATC
# relevanceConfig: relevance-v3
# pixallId: 600ujHskdLT2xf2tvTutP39v
# stats: year%2Cderivedprice


# {
#   "Description": "Chevrolet Silverado 2500/3500 (2004 - 2007) (130,000 Miles)",
#   "Host": "Bot-Host-12",
#   "ProfileName": "autotrader",
#   "Schedule": {
#     "DailyEndTime": "23:59:59",
#     "DailyStartTime": "05:05:00",
#     "HitTimes": [],
#     "Interval": "00:10:00",
#     "IsActive": true
#   },
#   "ScriptName": "Task_Run_23:04:30",
#   "SearchTerms": {
#     "Fuel Type": "DSL",
#     "Location": "eureka-mo-63025",
#     "Make": "CHEV",
#     "Max Miles": "130000",
#     "Max Year": "2007",
#     "Min Year": "2004",
#     "Model": "CH3500PU,CHEVC25",
#     "Trim": "",
#     "Drive": "AWD4WD"
#   },
#   "TaskName": "AT Chevrolet Silverado 2500-3500",
#   "Website": "autotrader.com"
# }

# %%
# https://www.autotrader.com/cars-for-sale/awd-4wd/diesel/ram/eureka-mo?endYear=2018&mileage=140000&modelCode=RM2500&modelCode=RM3500&newSearch=true&searchRadius=0&sortBy=datelistedDESC&startYear=2009

# endYear: 2018
# mileage: 140000
# modelCode: RM2500%2CRM3500
# newSearch: true
# searchRadius: 0
# sortBy: datelistedDESC
# startYear: 2009
# driveGroup: AWD4WD
# fuelTypeGroup: DSL
# makeCode: RAM
# city: Eureka
# state: MO
# zip: 63025
# location: %5Bobject+Object%5D
# dma: %5Bobject+Object%5D
# listingType: USED
# channel: ATC
# relevanceConfig: relevance-v3
# pixallId: 600ujHskdLT2xf2tvTutP39v
# stats: year%2Cderivedprice


# {
#   "Description": "Ram 2500/3500 (2009 - 2018) (140,000 Miles)",
#   "Host": "Bot-Host-12",
#   "ProfileName": "autotrader",
#   "Schedule": {
#     "DailyEndTime": "23:59:59",
#     "DailyStartTime": "05:06:40",
#     "HitTimes": [],
#     "Interval": "00:10:00",
#     "IsActive": true
#   },
#   "ScriptName": "Task_Run_23:04:30",
#   "SearchTerms": {
#     "Fuel Type": "DSL",
#     "Location": "eureka-mo-63025",
#     "Make": "RAM",
#     "Max Miles": "",
#     "Max Year": "2018",
#     "Min Year": "2009",
#     "Model": "RM2500,RM3500",
#     "Trim": "",
#     "Drive": "AWD4WD"
#   },
#   "TaskName": "AT Ram 2500-3500",
#   "Website": "autotrader.com"
# }

# %%
# https://www.autotrader.com/cars-for-sale/all-cars/ford/f150/eureka-mo?endYear=2024&newSearch=true&searchRadius=0&startYear=2021&trimCode=F150PICKUP%7CRaptor&trimCode=F150PICKUP%7CRaptor%20R

# endYear: 2024
# newSearch: true
# searchRadius: 0
# startYear: 2021
# trimCode: F150PICKUP|Raptor,F150PICKUP|Raptor R
# allListingType: all-cars
# makeCode: FORD
# modelCode: F150PICKUP
# city: Eureka
# state: MO
# zip: 63025
# location: [object Object]
# dma: [object Object]
# channel: ATC
# relevanceConfig: relevance-v3
# pixallId: 600ujHskdLT2xf2tvTutP39v
# stats: year,derivedprice


# {
#   "Description": "Ford F-150 Raptor (2021 - 2024) (Any Miles)",
#   "Host": "Bot-Host-12",
#   "ProfileName": "autotrader",
#   "Schedule": {
#     "DailyEndTime": "23:59:59",
#     "DailyStartTime": "05:10:00",
#     "HitTimes": [],
#     "Interval": "00:10:00",
#     "IsActive": true
#   },
#   "ScriptName": "Task_Run_23:04:30",
#   "SearchTerms": {
#     "Fuel Type": "",
#     "Location": "eureka-mo-63025",
#     "Make": "FORD",
#     "Max Miles": "",
#     "Max Year": "2024",
#     "Min Year": "2021",
#     "Model": "F150PICKUP",
#     "Trim": "F150PICKUP|Raptor,F150PICKUP|Raptor R",
#     "Drive": ""
#   },
#   "TaskName": "AT Ford F-150 Raptor",
#   "Website": "autotrader.com"
# }

# %%
# https://www.autotrader.com/cars-for-sale/all-cars/ford/f150/eureka-mo?endYear=2004&newSearch=true&searchRadius=0&startYear=1999&trimCode=F150PICKUP%7CLightning&trimCode=F150PICKUP%7CLightning%20Lariat&trimCode=F150PICKUP%7CLightning%20Platinum&trimCode=F150PICKUP%7CLightning%20Pro&trimCode=F150PICKUP%7CLightning%20XLT

# endYear: 2004
# newSearch: true
# searchRadius: 0
# startYear: 1999
# trimCode: F150PICKUP|Lightning,F150PICKUP|Lightning Lariat,F150PICKUP|Lightning Platinum,F150PICKUP|Lightning Pro,F150PICKUP|Lightning XLT
# allListingType: all-cars
# makeCode: FORD
# modelCode: F150PICKUP
# city: Eureka
# state: MO
# zip: 63025
# location: [object Object]
# dma: [object Object]
# channel: ATC
# relevanceConfig: relevance-v3
# pixallId: 600ujHskdLT2xf2tvTutP39v
# stats: year,derivedprice


# {
#   "Description": "Ford F-150 Lightning (1999 - 2004) (Any Miles)",
#   "Host": "Bot-Host-12",
#   "ProfileName": "autotrader",
#   "Schedule": {
#     "DailyEndTime": "23:59:59",
#     "DailyStartTime": "05:10:00",
#     "HitTimes": [],
#     "Interval": "00:10:00",
#     "IsActive": true
#   },
#   "ScriptName": "Task_Run_23:04:30",
#   "SearchTerms": {
#     "Fuel Type": "",
#     "Location": "eureka-mo-63025",
#     "Make": "FORD",
#     "Max Miles": "",
#     "Max Year": "2004",
#     "Min Year": "1999",
#     "Model": "F150PICKUP",
#     "Trim": "F150PICKUP|Lightning,F150PICKUP|Lightning Lariat,F150PICKUP|Lightning Platinum,F150PICKUP|Lightning Pro,F150PICKUP|Lightning XLT",
#     "Drive": ""
#   },
#   "TaskName": "AT Ford F-150 Lightning",
#   "Website": "autotrader.com"
# }


