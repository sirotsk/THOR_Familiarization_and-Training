# # Imports

# %%
# !pip install ipywidgets

# %%
import time
from datetime import datetime, timedelta
import pandas as pd
import json
import requests
import uuid

# import import_ipynb
# import thor_filters

# Setting pandas display options for better readability during debugging
pd.set_option('display.max_columns', None)  # Display all columns in DataFrames
pd.set_option('display.max_rows', None)     # Display all rows in DataFrames
pd.options.mode.chained_assignment = None   # Disable warning for chained assignments

# %%


# %% [markdown]
# ## All Craigslist Functions

# %% [markdown]
# ### Check If Account Is blocked or Suspended

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
    print('Function: check_blocked')


    checkpoint_data = {
        "ErrorName": "Blocked",
        "ErrorTime": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "ErrorDescription": "Error loading search page",
    }

    url = "https://sapi.craigslist.org/web/v8/postings/search"
    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
        "Cookie": "cl_b=4|5411c775aa66ff242fc29367d82280f3412d3b62|17197899267o-9M; cl_tocmode=",
        "DNT": "1",
        "Host": "sapi.craigslist.org",
        "If-Modified-Since": "Tue, 02 Jul 2024 14:59:49 GMT",
        "Origin": "https://wichita.craigslist.org",
        "Referer": "https://wichita.craigslist.org/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "sec-ch-ua": '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"'
    }
    params = {
        # "subarea": "-",
        "cc": "US",
        "batchSize": "1",
        "area_id": "99",
        "lang": "en",
        # "minDate": "$minDate",
        "searchPath": "cta",
        "startIndex": "0",
        # "sort": "date",
        # "bundleDuplicates": "1",
        # "query": "diesel"
        # "search_distance": "1000",
    }

    try:
        response = session.get(url, headers=headers, params=params, timeout=timeout)
        json_data = response.json()
        response.raise_for_status()  # Raises an HTTPError for bad responses
    except requests.Timeout:
        print(f'Timeout error: The request took longer than {timeout} seconds.')
        checkpoint_data["ErrorDescription"] = "Timeout error while loading search page"
        return True, checkpoint_data
    except requests.RequestException as e:
        json_data = {}
        print(f'Error fetching IP: {e}')
        return True, checkpoint_data

    try:
        print(f"Successful response from Craigslist Api: {len(json_data['data']['items'])}")
    except (json.JSONDecodeError, KeyError) as e:
        print(f'Error parsing response JSON: {e}')
        return True, checkpoint_data

    return False, {}

# %% [markdown]
# ### Craigslist Searching Functions

# %%
def remove_duplicates(dict_list, key='id'):
    seen_ids = set()
    unique_dicts = []
    for dictionary in dict_list:
        dict_id = dictionary.get(key)
        if dict_id not in seen_ids:
            unique_dicts.append(dictionary)
            seen_ids.add(dict_id)
    return unique_dicts


def DecodeCraigslistData(json_data):
    maxPostedDate = json_data['data']['decode']['maxPostedDate']
    minDate = json_data['data']['decode']['minDate']
    minPostedDate = json_data['data']['decode']['minPostedDate']
    minPostingId = json_data['data']['decode']['minPostingId']
    locationDescriptions = json_data['data']['decode']['locationDescriptions']
    locations = json_data['data']['decode']['locations']
    areas = json_data['data']['areas']
    categories = {
        '145': "cto",
        '146': "ctd"
    }
    category_descriptions = {
        '145': "cars & trucks - by owner",
        '146': "cars & trucks - by dealer"
    }
    items = json_data['data']['items']


    decoded_items = []
    for item in items:
        
        #Get the Posting ID
        PostingId = item[0] + minPostingId

        #get posted date
        PostedDate_from_min = item[1] + minPostedDate

        #decode location string
        location_string = item[4]
        location_id_string, location_lat, location_long = location_string.split('~')

        #parse and lookup location
        location = locations[int(location_id_string.split(":")[0])]

        #lookup Area name
        area_name = areas[str(location[0])]['name']

        #lookup location description
        location_description = locationDescriptions[int(location_id_string.split(":")[1])]

        #get catagory code
        catagory_code = item[2]

        #get price
        price_int = item[3]

        #get optional data
        listing_url_part = ''
        listing_miles = None
        listing_price = None
        listing_images = []
        for item_list in item:
            if isinstance(item_list, list) and len(item_list) > 0 and item_list[0] == 6:
                listing_url_part = item_list[1]

            if isinstance(item_list, list) and len(item_list) > 0 and item_list[0] == 10:
                listing_price = item_list[1]

            if isinstance(item_list, list) and len(item_list) > 0 and item_list[0] == 4:
                listing_images = item_list[1:]
                listing_images = ['https://images.craigslist.org/' + item.split(":", 1)[1] + '_1200x900.jpg' for item in listing_images]

            if isinstance(item_list, list) and len(item_list) > 0 and item_list[0] == 9:
                listing_miles = item_list[1]
                

        #Get title
        if isinstance(item[-1], str):
            listing_title = item[-1]
        else:
            listing_title = ''

        #Build Link
        if len(location) == 3:
            # get location sub area
            location_sub_area = location[2]

            listing_link = 'https://' + location[1] + '.craigslist.org/'  + location_sub_area + '/' + categories[str(catagory_code)] + '/d/' + listing_url_part + '/' + str(PostingId) + '.html'
        elif len(location) == 2:
            location_sub_area = None
            listing_link = 'https://' + location[1] + '.craigslist.org/' + categories[str(catagory_code)] + '/d/' + listing_url_part + '/' + str(PostingId) + '.html'
        else:
            listing_link = ''

        #Add data to dataframe
        decoded_data = {
            'id': PostingId,
            'PostingId': PostingId,
            'Title': listing_title,
            'PostingName': listing_url_part,
            'PostedDate': PostedDate_from_min,
            'AreaName':area_name,
            'SubAreaName': location_sub_area,           
            'locationDescription' :location_description,
            'LocationLat': location_lat,
            'LocationLong': location_long,
            'CategoryId': catagory_code,
            'CategoryCode': categories[str(catagory_code)],
            'CategoryDescription': category_descriptions[str(catagory_code)],
            'Miles': listing_miles,
            'Price': price_int,
            'PriceFormatted': listing_price,
            'Images': listing_images,
            'Link': listing_link
        }

        decoded_items.append(decoded_data)
    return decoded_items



def GetSearchListings(session, search_terms, timeout=(5, 5), sleep_time=3, max_pages=10):
    print('Function: GetSearchListings')
    errors = []

    search_postal_codes = [
        '67207',
        '20009',
        '93728'
    ]

    url = "https://sapi.craigslist.org/web/v8/postings/search/full"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Cookie": "cl_b=4|5411c775aa66ff242fc29367d82280f3412d3b62|17197899267o-9M; cl_tocmode=",
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "cache-control": "no-cache",
        "pragma": "no-cache",
        "sec-ch-ua": "\"Not/A)Brand\";v=\"8\", \"Chromium\";v=\"126\", \"Google Chrome\";v=\"126\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "referer": "https://wichita.craigslist.org/"
    }

    search_results_json = []
    page_num = 1 
    for postal_code in search_postal_codes:

        params = {
            "batch": "99-0-360-1-0",
            "bundleDuplicates": "1",
            "cc": "US",
            "lang": "en",
            "postal": postal_code,
            "query": search_terms['Search Text'],
            "searchPath": "cta",
            "search_distance": "1000",
            "sort": "date"
        }

        try:
            response = session.get(url, headers=headers, params=params, timeout=timeout)
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
            results_data = DecodeCraigslistData(json_data)
            print(f'Page Returned Data: {len(results_data)}')
        except (json.JSONDecodeError, KeyError) as e:
            error_info = {
                "ErrorName": "JSONDecodeError" if isinstance(e, json.JSONDecodeError) else "KeyError",
                "ErrorTime": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "ErrorDescription": f'Error parsing response JSON on page {page_num}: {e}'
            }
            print(error_info["ErrorDescription"])
            errors.append(error_info)
            break  # Exit loop on JSON error

        #append list together
        search_results_json = [*search_results_json, *results_data]

        if not len(results_data):
            print('No results returned')
            break # Exit loop on no results
        elif page_num < len(search_postal_codes):
            page_num += 1
            time.sleep(sleep_time) # Sleep only if there are more results
            

    #remove any duplicates
    print('remove_duplicates', len(search_results_json))
    search_results_json = remove_duplicates(search_results_json)
    print('remaining values', len(search_results_json))
    
    return search_results_json, errors



def GetListingDetails(session, listing_ids, timeout=(5, 5), sleep_time=3):

    errors = []
    # listing_details = pd.DataFrame()
    listing_details_json = []
    page_num = 1
    for listing_info in listing_ids:

        if not listing_info['SubAreaName']:
            listing_info['SubAreaName'] = '-'
            
        url = f"https://rapi.craigslist.org/web/v8/postings/{listing_info['AreaName']}/{listing_info['SubAreaName']}/{listing_info['CategoryCode']}/{listing_info['id']}"
        params = {
            "categoryAbbr": listing_info['CategoryCode'],
            "cc": "US",
            "hostname": listing_info['AreaName'],
            "lang": "en",
            "subareaAbbr": listing_info['SubAreaName']
        }


        headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive",
            "Cookie": "cl_b=4|5411c775aa66ff242fc29367d82280f3412d3b62|17197899267o-9M; cl_tocmode=",
            "DNT": "1",
            "Host": "sapi.craigslist.org",
            "If-Modified-Since": "Tue, 02 Jul 2024 14:59:49 GMT",
            "Origin": "https://wichita.craigslist.org",
            "Referer": "https://wichita.craigslist.org/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            "sec-ch-ua": '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"'
        }

        try:
            response = session.get(url, headers=headers, params=params, timeout=timeout)
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
            break
        except requests.RequestException as e:
            error_info = {
                "ErrorName": "RequestException",
                "ErrorTime": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "ErrorDescription": f'Error on page: {e}'
            }
            print(error_info["ErrorDescription"])
            errors.append(error_info)
            break

        try:
            json_data = response.json()
            json_items = json_data['data']['items']
            results_returned = len(json_items)
            print(f'Returned: {results_returned} results. {page_num} out of {len(listing_ids)} total.')
        except (json.JSONDecodeError, KeyError) as e:
            error_info = {
                "ErrorName": "JSONDecodeError" if isinstance(e, json.JSONDecodeError) else "KeyError",
                "ErrorTime": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "ErrorDescription": f'Error parsing response JSON: {e}'
            }
            print(error_info["ErrorDescription"])
            errors.append(error_info)
            break


        #append list together
        listing_details_json = [*listing_details_json, *json_items]

        if page_num < len(listing_ids):
            page_num += 1
            time.sleep(sleep_time)

    #remove any duplicates
    print('remove_duplicates', len(listing_details_json))
    listing_details_json = remove_duplicates(listing_details_json, key='postingId')
    print('remaining values', len(listing_details_json))

    return listing_details_json, errors   
    

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
        'title': {'details': 'title'},
        'id': 'id',
        'link': {'details': 'url'},
        'creation_time': {'details': 'postedDate'},
        'vehicle_condition': {'details': 'condition'},
        'vehicle_color': {'details': 'auto_paint'},
        'fuel_type': {'details': 'auto_fuel_type'},
        'paid_off': {'details': 'auto_title_status'},
        'make': {'details': 'auto_make_model'},
        'model': {'details': 'auto_make_model'},
        'year': {'details': 'auto_year'},
        'number_owners': '',
        'seller_type': {'details': 'categoryAbbr'},
        'vehicle_trim': '',
        'vin': {'details': 'auto_vin'},
        'listing_photos': {'details': 'images'},
        'seller_name': {'results': 'locationDescription'},
        'location': {'details': 'location.description'},
        'location_city': {'details': 'location.area'},
        'location_state': '',
        'location_country': '',
        'description': {'details': 'body'},
        'price': {'details': 'price'},
        'strikethrough_price': '',
        'odometer_unit': '',
        'odometer_value': {'details': 'auto_miles'},
        'thor_timestamp': {'results': 'thor_timestamp'},
        'thor_website': "autotrader.com",
        'thor_mmr': False,
        'thor_task': f"{current_task}",
        'thor_user': f"{current_user}",
        'Task': current_task['TaskName'],
        'Host': current_task["Host"],
        'Account': current_user["AccountInfo"]["AccountID"]
    }


    if not search_results.empty:
        #Custome Data from search_results here
        custom_data = pd.DataFrame(columns=['id'])
    else:
        custom_data = pd.DataFrame(columns=['id'])


    if not listing_details.empty:
        custom_data = pd.merge(listing_details, custom_data, on='id', how='left')

        # Check if 'attributes' column exists and expand the attributes
        if 'attributes' in listing_details.columns:
            try:
                listing_details = listing_details.join(
                    listing_details['attributes'].apply(
                        lambda row: pd.Series(
                            {
                                attr['postingAttributeKey']: attr['value']
                                for attr in row
                            }
                        ) if isinstance(row, list) else pd.Series()
                    )
                ).drop(columns=['attributes'])
            except Exception as e:
                print(f"Error processing 'attributes' column: {e}")

        # Check if 'autoVinData' column exists and expand autoVinData
        if 'autoVinData' in listing_details.columns:
            try:
                listing_details = listing_details.join(
                    listing_details['autoVinData'].apply(
                        lambda row: pd.Series(
                            {
                                f"{main_category[0]}.{attribute[0]}": attribute[1]
                                for main_category in row
                                for attribute in main_category[1]
                            }
                        ) if isinstance(row, list) else pd.Series()
                    )
                ).drop(columns=['autoVinData'])
            except Exception as e:
                print(f"Error processing 'autoVinData' column: {e}")

        # Check if 'images' column exists and expand images
        if 'images' in listing_details.columns:
            try:
                listing_details['images'] = listing_details['images'].apply(
                    lambda listing_images: [
                        f"https://images.craigslist.org/{item.split(':', 1)[1]}_1200x900.jpg" 
                        for item in listing_images
                    ] if isinstance(listing_images, list) else []
                )
            except Exception as e:
                print(f"Error processing 'images' column: {e}")
    else:
        print('no details')


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
        p_ip = current_user['ProxyInfo']['ProxyIp']
        p_port = current_user['ProxyInfo']['ProxyPort']
        p_user = current_user['ProxyInfo']['ProxyUsername']
        p_password = current_user['ProxyInfo']['ProxyPassword']
        if p_user is not None and p_user != '':
            proxy = {
            'http': f"http://{p_user}:{p_password}@{p_ip}:{p_port}",
            'https': f"http://{p_user}:{p_password}@{p_ip}:{p_port}"
            }   
        else: 
            proxy = {
                'http': f"http://{p_ip}:{p_port}",
                'https': f"http://{p_ip}:{p_port}",
            }


        # Configure the session to use the proxy
        session.proxies.update(proxy)
        proxy_set = check_proxy(session, p_ip) 
        
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


    search_results_json, errors = GetSearchListings(session, current_task['SearchTerms'], sleep_time=2)
    print('JSON', len(search_results_json))
    print(errors)

    #format data
    search_results = pd.DataFrame()
    thor_search_results = []
    if len(search_results_json):

        ##Create Gen 4 DataFrame
        search_results = pd.DataFrame(search_results_json)
        search_results.reset_index(drop=True, inplace=True)
        search_results = search_results.drop_duplicates(subset='id')
        print(search_results.shape)
        search_results['thor_timestamp'] = int(time.time())
        search_results['thor_website'] = "craigslist.com"
        search_results['thor_search_url'] = current_task['SearchTerms']['Search Text']
        search_results['thor_full_listing_url'] = search_results['Link']
        search_results['thor_listing_url'] = search_results['Link']

        #Create Gen 5 Json
        for dictionary in search_results_json:
            dictionary['thor_id'] = str(uuid.uuid4())
            dictionary['thor_website'] = 'craigslist.com'
            dictionary['thor_scraped'] = int(time.time())
            dictionary['thor_host'] = current_task['Host']
            dictionary['thor_task'] = current_task['TaskName']
            dictionary['thor_user'] = current_user['AccountInfo']['AccountID']
            dictionary['thor_content'] = json.dumps(dictionary)
            thor_search_results.append(dictionary)


    # Check For New Listings
    print(f"****************COMPARE DB****************** {len(search_results)} Results")
    compare_columns = {
        'id': 'id',
    }
    new_results = results_check_callback(search_results, 'craigslist.com', compare_columns)
    print(f"****************COMPARE DB Complete****************** {len(new_results)} New")

    #get list of new IDs and ensure no blanks or duplicates
    new_ids = new_results['id'].to_list()
    new_ids = [*{item for item in new_ids if item}]
    new_data = new_results[['SubAreaName', 'AreaName', 'CategoryCode', 'id']].to_dict(orient='records')
    print(new_data)

    
    #Get listing Details
    if len(new_results) > 0:
        listing_details_json, errors = GetListingDetails(session, new_data, sleep_time=.8)
    else:
        listing_details_json = []

    print(listing_details_json)

    thor_listing_details = []
    if len(listing_details_json):
        #Create Gen 4 DataFrame
        listing_details =  pd.json_normalize(listing_details_json)
        listing_details['id'] = listing_details['postingId']
        listing_details.reset_index(drop=True, inplace=True)
        listing_details = listing_details.drop_duplicates(subset='id')
        print(listing_details.shape)
        
        print('Adding standard fields to the DataFrame.')
        listing_details['thor_timestamp'] = int(time.time())
        listing_details['thor_website'] = "craigslist.com"

        #Create Gen 5 Json
        for dictionary in listing_details_json:
            dictionary['thor_id'] = str(uuid.uuid4())
            dictionary['thor_website'] = 'craigslist.com'
            dictionary['thor_scraped'] = int(time.time())
            dictionary['thor_host'] = current_task['Host']
            dictionary['thor_task'] = current_task['TaskName']
            dictionary['thor_user'] = current_user['AccountInfo']['AccountID']
            dictionary['thor_content'] = json.dumps(dictionary)
            dictionary['id'] = dictionary['postingId']            
            thor_listing_details.append(dictionary)



        
    #Format standard Output
    search_results, listing_details, Listings, task_telemetry, user_telemetry = Format_Output(current_task, current_user,  search_results, listing_details, new_ids)

    #filter to only Trucks and Vics we want
    # try:
    #     filters = thor_filters.listing_filters
    #     Listings = thor_filters.apply_filters(Listings, filters)
    # except:
    #     print('error Filtering')
    #     Listings = pd.DataFrame()


    print(f"{len(search_results)} search_results")
    print(f"{len(listing_details)} listing_details")
    print(f"{len(Listings)} Listings")
    print(f"{len(task_telemetry)} task_telemetry")
    print(f"{len(user_telemetry)} user_telemetry")
    print(f"{errors} errors")
    errors = {}
    
    yield search_results, listing_details, Listings, task_telemetry, user_telemetry, errors, thor_search_results, thor_listing_details

# %% [markdown]
# # Test Code

# %%
# def results_check(data, website, columns_map):
#     new_rows = data[:100]#pd.DataFrame(columns=data.columns)
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
#   "AccountInfo": {
#     "AccountID": "craigslist_test_1",
#     "AccountSite": "craigslist.com",
#     "AltUserName": "",
#     "Description": "",
#     "MFAKey": "",
#     "OtherData": {},
#     "Password": "",
#     "ProfileURL": "",
#     "UserName": ""
#   },
#   "ActiveTime": "00:00:00",
#   "BrowserInfo": {
#     "Args": [
#       "--disable-notifications"
#     ],
#     "BrowserType": "None",
#     "ClearCookies": False,
#     "Cookies": [],
#     "Description": "",
#     "Extensions": [],
#     "Incognito": False,
#     "UserAgent": "",
#     "UserFolderName": "",
#     "WindowHight": 0,
#     "WindowMaximized": False,
#     "WindowWidth": 0
#   },
#   "CheckedOut": False,
#   "Disabled": False,
#   "Errors": [],
#   "Host": "Bot-Host-10",
#   "LastActive": "2024-07-04 17:00:04",
#   "MaxActiveTime": "00:01:00",
#   "MinCoolDownTime": "00:10:00",
#   "ProxyInfo": {
#     "Description": "",
#     "ProxyIp": "",
#     "ProxyLoginUrl": "",
#     "ProxyPassword": "",
#     "ProxyPort": "",
#     "ProxyUsername": ""
#   },
#   "Website": "craigslist.com",
#   "user_id": ""
# }


# current_task =  {
#     'SearchTerms': {
#         'Search Text': 'tesla model y'
#     },
#     'Host': 'Bot-Host-0',
#     'Website': 'craigslist.com',
#     'ScriptName': 'Task_Run',
#     'ProfileName': 'craigslist',
#     'TaskName': 'All Diesel Vehicles',
#     'Description': 'All Diesel Vehicles',
#     'Schedule': {
#         'DailyEndTime': '23:59:59',
#         'Interval': '00:50:00',
#         'DailyStartTime': '00:48:00',
#         'HitTimes': [],
#         'IsActive': True
#         }
#     }

# current_profile = {
#     "Hosts": ["Bot-Host-0"],
#     "ProfileName": 'craigslist',
#     "Website": 'craigslist.com',
#     "Script": "craigslist_scripts",
#     "Description": "Master Profile For Craigslist"
# }  
    
    
# # ddd = ProcessTimer()
# # for final_results, final_details, Listings, task_telemetry, user_telemetry, errors, search_results_json, thor_listing_details in Task_Run(None, current_profile, current_task, current_user, results_check, ddd):
# #     # print('final_results')
# #     # display(final_results)
# #     # print('final_details')
# #     # display(final_details)
# #     print('Listings')
# #     display(Listings)
# #     # print('task_telemetry')
# #     # display(task_telemetry)
# #     # print('user_telemetry')
# #     # display(user_telemetry)
# #     # print('errors')
# #     search_results_json
# #     print(errors)

# %%


# %% [markdown]
# # Notes

# %%
# base_urls = [
#     "https://wichita.craigslist.org/search/sss?bundleDuplicates=1&postal=67207&auto_fuel_type={Fuel Type}&bundleDuplicates=1&max_auto_miles={Max Miles}&max_auto_year={Max Year}&min_auto_year={Min Year}&purveyor=owner&query={Make}+{Model}&searchNearby=2&sort=date&search_distance=1000&sort=date#search=1~gallery~0~0",
#     "https://washingtondc.craigslist.org/search/sss?bundleDuplicates=1&postal=20009&auto_fuel_type={Fuel Type}&bundleDuplicates=1&max_auto_miles={Max Miles}&max_auto_year={Max Year}&min_auto_year={Min Year}&purveyor=owner&query={Make}+{Model}&searchNearby=2&sort=date%20F250&search_distance=1000&sort=date#search=1~gallery~0~0",
#     "https://fresno.craigslist.org/search/sss?bundleDuplicates=1&postal=93728&auto_fuel_type={Fuel Type}&bundleDuplicates=1&max_auto_miles={Max Miles}&max_auto_year={Max Year}&min_auto_year={Min Year}&purveyor=owner&query={Make}+{Model}&searchNearby=2&sort=date%20F250&search_distance=1000&sort=date#search=1~gallery~0~0"
# ]



# %% [markdown]
# # Example code for different types of "apps"

# %%
# ##### Example script that runs the regular code, but takes a new dict / json as input REPLACING the default 



# def run_webscrape(script_task):       
#     ddd = ProcessTimer()
#     for final_results, final_details, Listings, task_telemetry, user_telemetry, errors, search_results_json, thor_listing_details in Task_Run(None, current_profile, script_task, current_user, results_check, ddd):
#         # print('final_results')
#         # display(final_results)
#         # print('final_details')
#         # display(final_details)
#         print('Listings')
#         display(Listings)
#         # print('task_telemetry')
#         # display(task_telemetry)
#         # print('user_telemetry')
#         # display(user_telemetry)
#         # print('errors')
#         search_results_json
#         print(errors)


# %%
# ### example using IPYWIDGETS to create a dropdown and button to run the function with the new search terms


# import ipywidgets as widgets
# from IPython.display import display

# # Function to be executed when the button is pressed
# def my_function(var1, var2):
#     print(f'Function called with var1={var1} and var2={var2}')

# # Create dropdown widgets
# # you can change these to be the different options for the search parameters.
# dropdown_var1 = widgets.Dropdown(
#     options=['Telsa', 'Ford Mustang', 'Delorean'],
#     value='Delorean',
#     description='Vehicle Make:',
# )
# # you can change these to be the different options for the search parameters.
# dropdown_var2 = widgets.Dropdown(
#     options=['Option A', 'Option B', 'Option C'],
#     value='Option A',
#     description='Variable 2:',
# )

# # Create a button widget
# button = widgets.Button(
#     description='Run Function',
#     button_style='success', # 'success', 'info', 'warning', 'danger' or ''
#     tooltip='Click me',
#     icon='check' # (FontAwesome names without the `fa-` prefix)
# )

# # Function to be called when the button is clicked. This should run your code, that then runns 
# def run_webscrape(script_task):
#     var1 = dropdown_var1.value
#     var2 = dropdown_var2.value

#     search_terms =  {
#     'SearchTerms': {
#         'Search Text': f'{var1}'
#     },
#     'Host': 'Bot-Host-0',
#     'Website': 'craigslist.com',
#     'ScriptName': 'Task_Run',
#     'ProfileName': 'craigslist',
#     'TaskName': 'All Diesel Vehicles',
#     'Description': 'All Diesel Vehicles',
#     'Schedule': {
#         'DailyEndTime': '23:59:59',
#         'Interval': '00:50:00',
#         'DailyStartTime': '00:48:00',
#         'HitTimes': [],
#         'IsActive': True
#         }
#     }
#     run_webscrape(search_terms)

# # Assign the function to the button click event
# button.on_click(run_webscrape)

# # Display the widgets
# display(dropdown_var1, dropdown_var2, button)


# %%
# ### Example using TKINTER to create a UI with dropdowns and button to run the function with the new search terms


# import tkinter as tk
# from tkinter import ttk

# # Function to be executed when the button is pressed
# def my_function(var1, var2):
#     print(f'Function called with var1={var1} and var2={var2}')

# # Create the main window
# root = tk.Tk()
# root.title("Simple Tkinter UI")

# # Create a frame for the dropdown menus and button
# frame = ttk.Frame(root, padding="10")
# frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

# # Variable for dropdown_var1
# var1 = tk.StringVar()
# dropdown_var1 = ttk.Combobox(frame, textvariable=var1)
# dropdown_var1['values'] = ('Option 1', 'Option 2', 'Option 3')
# dropdown_var1.grid(row=0, column=1, padx=5, pady=5)
# dropdown_var1.current(0)

# # Label for dropdown_var1
# label_var1 = ttk.Label(frame, text="Variable 1:")
# label_var1.grid(row=0, column=0, padx=5, pady=5)

# # Variable for dropdown_var2
# var2 = tk.StringVar()
# dropdown_var2 = ttk.Combobox(frame, textvariable=var2)
# dropdown_var2['values'] = ('Option A', 'Option B', 'Option C')
# dropdown_var2.grid(row=1, column=1, padx=5, pady=5)
# dropdown_var2.current(0)

# # Label for dropdown_var2
# label_var2 = ttk.Label(frame, text="Variable 2:")
# label_var2.grid(row=1, column=0, padx=5, pady=5)

# # Function to be called when the button is clicked
# def on_button_clicked():
#     selected_var1 = var1.get()
#     selected_var2 = var2.get()
#     my_function(selected_var1, selected_var2)

# # Create the button widget
# button = ttk.Button(frame, text="Run Function", command=on_button_clicked)
# button.grid(row=2, column=0, columnspan=2, pady=10)

# # Run the application
# root.mainloop()


# %%
# #### Example where you just change the dict that is sent with the payload


# def run_webscrape(script_task):       
#     ddd = ProcessTimer()
#     for final_results, final_details, Listings, task_telemetry, user_telemetry, errors, search_results_json, thor_listing_details in Task_Run(None, current_profile, script_task, current_user, results_check, ddd):
#         # print('final_results')
#         # display(final_results)
#         # print('final_details')
#         # display(final_details)
#         print('Listings')
#         display(Listings)
#         # print('task_telemetry')
#         # display(task_telemetry)
#         # print('user_telemetry')
#         # display(user_telemetry)
#         # print('errors')
#         search_results_json
#         print(errors)


# new_payload_dict = {
#     'SearchTerms': {
#         ##### I change this one
#         'Search Text': 'delorean'
#     },
#     'Host': 'Bot-Host-0',
#     'Website': 'craigslist.com',
#     'ScriptName': 'Task_Run',
#     'ProfileName': 'craigslist',
#     'TaskName': 'All Diesel Vehicles',
#     'Description': 'All Diesel Vehicles',
#     'Schedule': {
#         'DailyEndTime': '23:59:59',
#         'Interval': '00:50:00',
#         'DailyStartTime': '00:48:00',
#         'HitTimes': [],
#         'IsActive': True
#         }
#     } 


# run_webscrape(new_payload_dict)

# %%



