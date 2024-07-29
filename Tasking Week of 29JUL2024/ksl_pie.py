# ## Imports
# 
# In this section, we import the necessary libraries and modules required for scraping ksl.com. These imports include standard libraries for handling dates and times, data manipulation, regular expressions, numerical operations, JSON handling, and making HTTP requests.

# %%
# !pip install requests
# !pip install beautifulsoup4
# !pip install pandas
# !pip install numpy
# !pip install json

# %%
import time
from datetime import datetime, timedelta
import pandas as pd
import json
import requests


# Setting pandas display options for better readability during debugging
pd.set_option('display.max_columns', None)  # Display all columns in DataFrames
pd.set_option('display.max_rows', None)     # Display all rows in DataFrames
pd.options.mode.chained_assignment = None   # Disable warning for chained assignments

# %% [markdown]
# ## All KSL Functions

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
    """
    Check if the IP is blocked by making a request to the KSL Cars API and analyzing the response.

    Args:
        session (requests.Session): The session with the proxy set.
        timeout (int, optional): The timeout for the request in seconds. Default is 5 seconds.

    Returns:
        tuple: A tuple containing a boolean indicating if blocked (True) or not (False), and a dictionary with error details if blocked.
    """
    print('Function: check_blocked')


    checkpoint_data = {
        "ErrorName": "Blocked",
        "ErrorTime": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "ErrorDescription": "Error loading search page",
    }

    try:
        response = session.get('https://cars.ksl.com/nextjs-api/ip', timeout=timeout)
        response.raise_for_status()  # Raises an HTTPError for bad responses
    except requests.Timeout:
        print(f'Timeout error: The request took longer than {timeout} seconds.')
        checkpoint_data["ErrorDescription"] = "Timeout error while loading search page"
        return True, checkpoint_data
    except requests.RequestException as e:
        print(f'Error fetching IP: {e}')
        return True, checkpoint_data

    try:
        data = json.loads(response.text)['data']['ipAddress']
        print(f'Successful response from KSL Cars API. IP Address: {data}')
    except (json.JSONDecodeError, KeyError) as e:
        print(f'Error parsing response JSON: {e}')
        return True, checkpoint_data

    return False, {}

###
### Sites method for Checking If IP is Blocked
### Could Be used to chech if blocked
###
# 'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"

# fetch("https://be.durationmedia.net/scriptloaded?siteId=11162", {
#   "headers": {
#     "accept": "*/*",
#     "accept-language": "en-US,en;q=0.9",
#     "cache-control": "no-cache",
#     "pragma": "no-cache",
#     "sec-ch-ua": "\"Not/A)Brand\";v=\"8\", \"Chromium\";v=\"126\", \"Google Chrome\";v=\"126\"",
#     "sec-ch-ua-mobile": "?0",
#     "sec-ch-ua-platform": "\"Windows\"",
#     "sec-fetch-dest": "empty",
#     "sec-fetch-mode": "cors",
#     "sec-fetch-site": "cross-site"
#   },
#   "referrer": "https://cars.ksl.com/",
#   "referrerPolicy": "strict-origin-when-cross-origin",
#   "body": null,
#   "method": "GET",
#   "mode": "cors",
#   "credentials": "omit"
# });

# %% [markdown]
# ### KSL Searching Functions

# %%
def GetSearchListings(session, search_terms, timeout=(5, 5), sleep_time=3, max_pages=10):
    """
    Fetches car listings based on the given search terms from the specified API endpoint.

    Args:
        session: The requests session to be used for making HTTP requests.
        search_terms (dict): Dictionary containing search parameters such as Make, Model, Min Year, Max Year, Max Miles, and Fuel Type.
        timeout (tuple): Timeout settings for the HTTP requests (connect timeout, read timeout).
        sleep_time (int): Time in seconds to sleep between requests to avoid rate limiting.
        max_pages (int): Maximum number of pages to fetch.

    Returns:
        search_results (pd.DataFrame): DataFrame containing the search results.
        errors (list): List of dictionaries containing error information.
    """
    print('Function: GetSearchListings')


    url = "https://cars.ksl.com/nextjs-api/proxy?"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "content-type": "application/json",
        "priority": "u=1, i",
        "sec-ch-ua": "\"Not/A)Brand\";v=\"8\", \"Chromium\";v=\"126\", \"Google Chrome\";v=\"126\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "x-ddm-event-accept-language": "en-US",
        "x-ddm-event-ip-address": "undefined",
        "x-ddm-event-user-agent": "[object Object]"
    }

    body = {
        "endpoint": "/classifieds/cars/search/searchByUrlParams",
        "options": {
            "method": "POST",
            "headers": {
                "Content-Type": "application/json",
                "User-Agent": "cars-node",
                "X-App-Source": "frontline",
                "X-DDM-EVENT-USER-AGENT": {
                    "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
                    "browser": {
                        "name": "Chrome",
                        "version": "126.0.0.0",
                        "major": "126"
                    },
                    "engine": {
                        "name": "Blink",
                        "version": "126.0.0.0"
                    },
                    "os": {
                        "name": "Windows",
                        "version": "10"
                    },
                    "device": {},
                    "cpu": {
                        "architecture": "amd64"
                    }
                },
                "X-DDM-EVENT-ACCEPT-LANGUAGE": "en-US",
                "X-MEMBER-ID": None,
                "cookie": ""
            },
            "body": []
        }
    }

    page_num = 1
    results_returned = 0
    total_returned = 0
    results_count = 1000
    search_results = pd.DataFrame()
    errors = []

    while total_returned < results_count and page_num <= max_pages:

        #Pagination and Search Terms
        body['options']['body'] = [
            "perPage", "96",
            "page", str(page_num),
            "make", search_terms['Make'],
            "model", search_terms['Model'],
            "yearTo", search_terms['Max Year'],
            "yearFrom", search_terms['Min Year'],
            "mileageTo", search_terms['Max Miles'],
            "fuel", search_terms['Fuel Type'],
            "includeFacetCounts", "0",
            "es_query_group", None
        ]
        
        # Check if 'Trim' exists in search_terms and is not None
        if 'Trim' in search_terms and search_terms['Trim']:
            # Find the index where 'model' is located
            model_index = body['options']['body'].index("model")
            # Insert 'trim' and its value right after 'model' and its value
            body['options']['body'][model_index + 2:model_index + 2] = ["trim", search_terms['Trim']]

        try:
            response = session.post(url, headers=headers, json=body, timeout=timeout)
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
            json_data = json.loads(response.text)
            json_items = json_data['data']['items']
            results_returned = len(json_items)
            total_returned += results_returned
            results_count = json_data['data']['count']
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

        search_results = pd.concat([search_results, pd.json_normalize(json_items)])

        if not results_returned:
            print('No results returned')
            break # Exit loop on no results
        elif total_returned < results_count:
            page_num += 1
            body['options']['body'][3] = str(page_num)
            time.sleep(sleep_time) # Sleep only if there are more results

    print(search_results.shape)
    if not search_results.empty and 'id' in search_results.columns:
        search_results.reset_index(drop=True, inplace=True)
        search_results = search_results.drop_duplicates(subset='id')
        print(search_results.shape)

        search_url = search_terms['Search Url'] #'"' + '", "'.join(body['options']['body']) + '"'
        search_results['thor_timestamp'] = int(time.time())
        search_results['thor_website'] = "ksl.com"
        search_results['thor_search_url'] = search_url
        search_results['thor_full_listing_url'] = 'https://cars.ksl.com/listing/' + search_results['id'].astype(str)
        search_results['thor_listing_url'] = 'https://cars.ksl.com/listing/' + search_results['id'].astype(str)
        
    return search_results, errors



def GetListingDetails(session, listing_ids, timeout=(5, 5)):
    """
    Fetches details for a list of car listings from the KSL Cars API.

    Args:
        session (requests.Session): The session object used to perform HTTP requests.
        listing_ids (list): A list of listing IDs for which details are to be fetched.
        timeout (tuple): A tuple specifying the connection and read timeout for the request.

    Returns:
        tuple: A tuple containing:
            - pd.DataFrame: A DataFrame with the details of the listings.
            - list: A list of errors encountered during the process.

    Raises:
        requests.Timeout: If the request times out.
        requests.RequestException: For any other request-related errors.
        json.JSONDecodeError: If there is an error in decoding the JSON response.
        KeyError: If the expected keys are not found in the response JSON.
    
    Notes:
        The function sends a POST request to the KSL Cars API with the listing IDs in the request body.
        It processes the response JSON to extract the listing details and normalize them into a DataFrame.
        Any errors encountered during the request or JSON parsing are captured and returned in the errors list.
        Additional standard fields are added to the resulting DataFrame.
    """
    print('Function: GetListingDetails')

    
    errors = []
    listing_details = pd.DataFrame()
    json_items = []

    url = "https://cars.ksl.com/nextjs-api/cars-api"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "content-type": "text/plain;charset=UTF-8",
        "priority": "u=1, i",
        "sec-ch-ua": "\"Not/A)Brand\";v=\"8\", \"Chromium\";v=\"126\", \"Google Chrome\";v=\"126\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "cookie": ("ddmDeviceId=4cayt4aocxik; __zlcmid=1JlmPjqmqsSCgGn; PHPSESSID=c6umt3leifcbc9uqmdo3dkstnh; kslPhotoViewerNewOldRollout=82; "
                "kslInactiveSpecsRollout=34; kslUseNewFeaturedAdLayoutRollout=38; kslRentalRulesFlagRollout=99; "
                "kslGeneralSelfServeTextVariantsRollout=71; kslGenElasticSearchRollout=16; kslGeneralShowImmediateRollout=22; "
                "kslCarsBigQueryRollout=90; kslElasticSearch2Rollout=65; session_type=mongo; "
                "mf_378954bf-e4e1-4ec3-b201-d1be116e57c4=||1719184063920||0||||0|0|58.90044; pxcts=6666a42d-31b5-11ef-a29f-5649a26cf9fd; "
                "_pxvid=661ec623-31b5-11ef-a0e0-7a1142995b80; OTGPPConsent=DBABBg~BAAAAACA.QA; __ssid=3645285dec96aec382dbfc49a9b9a4f; "
                "visitor_id911272=543911626; visitor_id911272-hash=ebcabbd596efb8e26587bc22e053b175b2641f9c5ad68c39d059fde66c78bb9404d33d010c9cfc6c50d723c929cec0fafc06fd3f; "
                "__stripe_mid=efef22a5-5d7e-4993-9af5-b5846b1554d63de97b; OptanonAlertBoxClosed=2024-06-23T23:07:59.336Z; "
                "ddmSessionId=a3qt6rmjb5kn; _pxhd=BFxro8Fys/KtNLq7EdOXCOOF9kJpb/OPegfL3iguuaNt9KQaprTOIpvUsC9xS8Pp/r5kpw0q1D8lpvOrMTqF1Q==:z9G/vdL7G0jMjYNERvO4GNwWf9/i0QiZumG4--3PktD9MMLCJwFX9gfd-TDfg7bBmH0-PZmxkUSFmF0lV0hIe6ng9LNjvwTFM6JbPNFCBYs=; "
                "__stripe_sid=8184e90b-67ac-471e-815b-ca34a768fd1cb474d8; OptanonConsent=isGpcEnabled=0&datestamp=Sun+Jun+23+2024+22%3A52%3A14+GMT-0400+(Eastern+Daylight+Time)&version=202405.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=88fdf437-02c0-4110-8341-7927659c312a&interactionCount=1&isAnonUser=1&landingPath=NotLandingPage&GPPCookiesCount=1&groups=C0001%3A1%2CC0003%3A1%2CC0002%3A1%2CSSPD_BG%3A1%2CC0004%3A1&intType=3&geolocation=US%3BMO&AwaitingReconsent=false; "
                "_px2=eyJ1IjoiYzJjZTkxNDAtMzFkNC0xMWVmLTljNzktYTE2ZjUxZmUxM2RlIiwidiI6IjY2MWVjNjIzLTMxYjUtMTFlZi1hMGUwLTdhMTE0Mjk5NWI4MCIsInQiOjE3MTkxOTc4MzU0MzksImgiOiI4NjhjZTMyYTNhZTIyZTBiNzNiNjNhYTkzMDEyYjg0ZDdlZTljNzllYTFjYjEzOTg5YzEyNzdhMDhiN2MxNWVjIn0=; "
                "_ga=GA1.1.715650853.1719197760; _gcl_au=1.1.189562850.1719197761; _ga_JW89DL7T5D=GS1.1.1719197759.1.1.1719197760.59.0.0"),
        "Referer": "https://cars.ksl.com/listing/9362104",
        "Referrer-Policy": "strict-origin-when-cross-origin"
    }

    body = {
        "endpoint": "/search",
        "request": {
            "method": "POST",
            "body": {
                "data": {
                    "type": "search",
                    "attributes": {
                        "query": {
                            "id": listing_ids
                        },
                        "nav": {
                            "page": 1,
                            "perPage": len(listing_ids)
                        }
                    }
                }
            }
        }
    }

    try:
        response = session.post(url, headers=headers, json=body)
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
        json_data = json.loads(response.text)
        json_items = json_data['data']
        results_returned = len(json_items)
        results_count = json_data['data']
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

    if len(json_items) and 'attributes' in json_items[0].keys():
        flattened_data = [{**item['attributes']} for item in json_items]
        listing_details = pd.json_normalize(flattened_data)
        listing_details.reset_index(drop=True, inplace=True)
        listing_details = listing_details.drop_duplicates(subset='id')
        print(listing_details.shape)
        
        print('Adding standard fields to the DataFrame.')
        listing_details['thor_timestamp'] = int(time.time())
        listing_details['thor_website'] = "ksl.com"

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
        'title': {'custom': 'title'},
        'id': 'id',
        'link': {'results': 'thor_listing_url'},
        'creation_time': {'results': 'createTime'},
        'vehicle_condition': {'details': 'exteriorCondition'},
        'vehicle_color': {'details': 'exteriorColor'},
        'fuel_type': {'results': 'fuel'},
        'paid_off': {'results': 'titleType'},
        'make': {'results': 'make'},
        'model': {'results': 'model'},
        'year': {'results': 'makeYear'},
        'number_owners': '',
        'seller_type': {'results': 'sellerType'},
        'vehicle_trim': {'results': 'trim'},
        'vin': {'results': 'vin'},
        'listing_photos': {'custom': 'images'},
        'seller_name': {'results': 'firstName'},
        'location': {'custom': 'location'},
        'location_city': {'results': 'city'},
        'location_state': {'results': 'state'},
        'location_country': '',
        'description': {'details': 'description'},
        'price': {'results': 'price'},
        'strikethrough_price': {'results': 'previousLowPrice'},
        'odometer_unit': '',
        'odometer_value': {'results': 'mileage'},
        'thor_timestamp': {'results': 'thor_timestamp'},
        'thor_website': "ksl.com",
        'thor_mmr': False,
        'thor_task': f"{current_task}",
        'thor_user': f"{current_user}",
        'Task': current_task['TaskName'],
        'Host': current_task["Host"],
        'Account': current_user["AccountInfo"]["AccountID"]
    }

    # Ensure 'id' and 'photo' are in the columns before proceeding
    required_columns = ['id', 'photo', 'makeYear', 'make', 'model', 'trim', 'city', 'state']
    if all(col in listing_details.columns for col in required_columns):
        if not listing_details.empty:
            custom_data = listing_details[['id', 'photo']].copy()
            custom_data['images'] = custom_data['photo'].apply(
                lambda photo_list: [photo['id'] for photo in photo_list] if isinstance(photo_list, list) else None
            )
            custom_data['title'] = (listing_details['makeYear'].astype(str) + ' ' + listing_details['make'] + ' ' + listing_details['model'] + ' ' + listing_details['trim']).str.strip()
            custom_data['location'] = listing_details['city'] + ", " + listing_details['state']
        else:
            custom_data = pd.DataFrame(columns=['id', 'photo', 'images', 'title'])
    else:
        custom_data = pd.DataFrame(columns=['id', 'photo', 'images', 'title'])

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
# 

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


    search_results, errors = GetSearchListings(session, current_task['SearchTerms'], sleep_time=3)
    print(errors)

    # Check For New Listings
    print(f"****************COMPARE DB****************** {len(search_results)} Results")
    compare_columns = {
        'id': 'id',
    }
    new_results = results_check_callback(search_results, 'ksl.com', compare_columns)
    print(f"****************COMPARE DB Complete****************** {len(new_results)} New")

    #get list of new IDs and ensure no blanks or duplicates
    new_ids = new_results['id'].to_list()
    new_ids = [*{item for item in new_ids if item}]

    #Get listing Details
    if len(new_results) > 0:
        listing_details, errors = GetListingDetails(session, new_ids)
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
# ## Test Code

# %%
# def results_check(data, website, columns_map):
#     new_rows = data#[:1]#pd.DataFrame(columns=data.columns)
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
#     'UserProfilesPath': r'User Profiles',
#     'PluginsPath': r'Plugins',
#     'WebRtcName': 'WebRTC',
#     'DefaultBrowserArgs': [
#          '--disable-gpu',
#          '--disable-software-rasterizer'
#     ]
# }


# current_user = {
#     "Host": "Bot-Host-0",
#     "ProfileName": "ksl",
#     "CheckedOut": True,
#     "ProxyInfo": {
#         "ProxyIp": "",
#         "ProxyPort": "",
#         "ProxyUsername": "",
#         "ProxyPassword": "",
#         "Description": "",
#     },
#     "BrowserInfo": {
#         "BrowserType": "None",
#         "UserFolderName": "kslTest",
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
#         "AccountID": "kslTest",
#         "AccountSite": "ksl.com",
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


# current_task =  {
#     'Host': 'Bot-Host-0',
#     'Website': 'ksl.com',
#     'ScriptName': 'Task_Run',
#     'ProfileName': 'ksl',
#     'TaskName': 'GMC Sierra 3500HD Crew',
#     'Description': 'GMC Sierra (2004 - 2007) (130,000 Miles)',
#     'Schedule': {
#         'DailyEndTime': '23:59:59',
#         'Interval': '00:50:00',
#         'DailyStartTime': '00:48:00',
#         'HitTimes': [],
#         'IsActive': True
#     },
#     'SearchTerms': {
#         'Max Miles': '140000',
#         'Min Year': '1989',
#         'Max Year': '2009',
#         'Model': 'F-250;F-250 Super Duty;F-350;F-350 Super Duty;Excursion;Silverado 2500;Silverado 2500HD;Silverado 3500;Silverado 3500 CC Classic;Silverado 3500HD;Silverado 3500HD CC;D Series;D/W Series;Ram 2500;Ram 3500;Ram Pickup 2500;Ram Pickup 3500;Sierra 2500 Classic;Sierra 3500 CC Classic;Sierra 3500HD CC',
#         'Fuel Type': 'Diesel;Bio-Diesel',
#         'Make': 'Ford;Chevrolet;Dodge;GMC',
#         # 'Trim': 'Trackhawk',
#         'Search Url': "https://cars.ksl.com/search/make/Ford;Chevrolet;Dodge;GMC/model/F-250;F-250+Super+Duty;F-350;F-350+Super+Duty;Excursion;Silverado+2500;Silverado+2500HD;Silverado+3500;Silverado+3500+CC+Classic;Silverado+3500HD;Silverado+3500HD+CC;D+Series;D%7CW+Series;Ram+2500;Ram+3500;Ram+Pickup+2500;Ram+Pickup+3500;Sierra+2500+Classic;Sierra+3500+CC+Classic;Sierra+3500HD+CC/yearFrom/1989/yearTo/2009/mileageTo/140000/fuel/Diesel;Bio-Diesel/sort/0"
#     }
# }

# current_profile = {
#     "Hosts": ["Bot-Host-0"],
#     "ProfileName": 'ksl',
#     "Website": 'facekslbook.com',
#     "Script": "ksl_scripts",
#     "Description": "Master Profile For KSL"
# }  
    
    
# ddd = ProcessTimer()
# for final_results, final_details, Listings, task_telemetry, user_telemetry, errors in Task_Run(None, current_profile, current_task, current_user, results_check, ddd):
#     print('final_results')
#     display(final_results)
#     print('final_details')
#     display(final_details)
#     print('Listings')
#     display(Listings)
#     print('task_telemetry')
#     display(task_telemetry)
#     print('user_telemetry')
#     display(user_telemetry)
#     print('errors')
#     print(errors)

# %% [markdown]
# ## Notes

# %%
# # Create a session object
# session = requests.Session()
# session.headers.update({
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
# })

# if current_user['ProxyInfo']['ProxyIp'] != '':
#     proxy = {
#         'http': current_user['ProxyInfo']['ProxyIp'] + ':' + current_user['ProxyInfo']['ProxyPort'],
#         'https':current_user['ProxyInfo']['ProxyIp'] + ':' + current_user['ProxyInfo']['ProxyPort']
#     }

#     # Configure the session to use the proxy
#     session.proxies.update(proxy)
#     proxy_set = check_proxy(session, current_user['ProxyInfo']['ProxyIp']) 
    
#     print('Proxy Set: ', proxy_set)
# else:
#     proxy_set = True




# url = "https://cars.ksl.com/nextjs-api/proxy?"

# headers = {
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
#     "accept": "*/*",
#     "accept-language": "en-US,en;q=0.9",
#     "content-type": "application/json",
#     "priority": "u=1, i",
#     "sec-ch-ua": "\"Not/A)Brand\";v=\"8\", \"Chromium\";v=\"126\", \"Google Chrome\";v=\"126\"",
#     "sec-ch-ua-mobile": "?0",
#     "sec-ch-ua-platform": "\"Windows\"",
#     "sec-fetch-dest": "empty",
#     "sec-fetch-mode": "cors",
#     "sec-fetch-site": "same-origin",
#     "x-ddm-event-accept-language": "en-US",
#     "x-ddm-event-ip-address": "undefined",
#     "x-ddm-event-user-agent": "[object Object]"
# }

# body = {
#     "endpoint": "/classifieds/cars/search/searchByUrlParams",
#     "options": {
#         "method": "POST",
#         "headers": {
#             "Content-Type": "application/json",
#             "User-Agent": "cars-node",
#             "X-App-Source": "frontline",
#             "X-DDM-EVENT-USER-AGENT": {
#                 "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
#                 "browser": {
#                     "name": "Chrome",
#                     "version": "126.0.0.0",
#                     "major": "126"
#                 },
#                 "engine": {
#                     "name": "Blink",
#                     "version": "126.0.0.0"
#                 },
#                 "os": {
#                     "name": "Windows",
#                     "version": "10"
#                 },
#                 "device": {},
#                 "cpu": {
#                     "architecture": "amd64"
#                 }
#             },
#             "X-DDM-EVENT-ACCEPT-LANGUAGE": "en-US",
#             "X-MEMBER-ID": None,
#             "cookie": ""
#         },
#         "body": []
#     }
# }



# #Pagination and Search Terms
# body['options']['body'] = [
#     "perPage", "96",
#     "page", str(page_num),
#     "make", search_terms['Make'],
#     "model", search_terms['Model'],
#     "trim", search_terms['Trim'],
#     "yearTo", search_terms['Max Year'],
#     "yearFrom", search_terms['Min Year'],
#     "mileageTo", search_terms['Max Miles'],
#     "fuel", search_terms['Fuel Type'],
#     "includeFacetCounts", "0",
#     "es_query_group", None
# ]

# try:
#     response = session.post(url, headers=headers, json=body, timeout=timeout)
#     response.raise_for_status()  # Raises an HTTPError for bad responses
#     print(f'Successful response for page {page_num}')
# except requests.Timeout:
#     error_info = {
#         "ErrorName": "Timeout",
#         "ErrorTime": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
#         "ErrorDescription": f'Timeout error on page {page_num}'
#     }
#     print(error_info["ErrorDescription"])
#     errors.append(error_info)
#     break  # Exit loop on timeout
# except requests.RequestException as e:
#     error_info = {
#         "ErrorName": "RequestException",
#         "ErrorTime": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
#         "ErrorDescription": f'Error on page {page_num}: {e}'
#     }
#     print(error_info["ErrorDescription"])
#     errors.append(error_info)
#     break  # Exit loop on request exception

# try:
#     json_data = json.loads(response.text)
#     json_items = json_data['data']['items']


