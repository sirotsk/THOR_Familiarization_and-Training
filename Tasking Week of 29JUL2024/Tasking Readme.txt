 .----------------.  .----------------.  .----------------.          .----------------.  .----------------.  .----------------.  .----------------. 
| .--------------. || .--------------. || .--------------. |        | .--------------. || .--------------. || .--------------. || .--------------. |
| |  _________   | || |  ____  ____  | || |  _________   | |        | |  _________   | || |      __      | || |    _______   | || |  ___  ____   | |
| | |  _   _  |  | || | |_   ||   _| | || | |_   ___  |  | |        | | |  _   _  |  | || |     /  \     | || |   /  ___  |  | || | |_  ||_  _|  | |
| | |_/ | | \_|  | || |   | |__| |   | || |   | |_  \_|  | |        | | |_/ | | \_|  | || |    / /\ \    | || |  |  (__ \_|  | || |   | |_/ /    | |
| |     | |      | || |   |  __  |   | || |   |  _|  _   | |        | |     | |      | || |   / ____ \   | || |   '.___`-.   | || |   |  __'.    | |
| |    _| |_     | || |  _| |  | |_  | || |  _| |___/ |  | |        | |    _| |_     | || | _/ /    \ \_ | || |  |`\____) |  | || |  _| |  \ \_  | |
| |   |_____|    | || | |____||____| | || | |_________|  | |        | |   |_____|    | || ||____|  |____|| || |  |_______.'  | || | |____||____| | |
| |              | || |              | || |              | |        | |              | || |              | || |              | || |              | |
| '--------------' || '--------------' || '--------------' |        | '--------------' || '--------------' || '--------------' || '--------------' |
 '----------------'  '----------------'  '----------------'            '----------------'  '----------------'  '----------------'  '----------------' 

* For this task, you will build off of what you have learned from the previous weeks, and build a more intricate app that will take in user input and conduct searches 
using the provided input on all 3 websites we have gone over.

Below is the link to the confluence page for documentation / walkthrough.
https://asgard-analytics.atlassian.net/wiki/spaces/THOR/pages/90210465/Craigslist+Scraping

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
More details are included in the tasking notebook to help you get started, but a general outline and some quick 'how-tos' are below.
	1. Understand that you can import python scripts into other python scripts / notebooks just like you do python libraries (i.e. pandas), and run functions from those 
	scripts in the same way.
	///////////////////////////////////////////////////////////
		import my_module

		# Using the functions from the imported module
		greeting = my_module.greet("Alice")
		print(greeting)  # Output: Hello, Alice!

		result = my_module.add(5, 3)
		print(result)  # Output: 8
	///////////////////////////////////////////////////////////

	2. Create some functions that will send seacrh tersm / payload to each of the websites to run a search. 

	3. Create a function that will take in some search terms and send a custom payload to each of the sites using the input search terms.
		here, you will have to make some coade that will formatt the input terms differently for each of the websites payload to properly conduct the search.

	4. Ensure that the data being pulled from each site search is formatted the same.
		Here, you can use the formatting functions found in each notebook/py file to make sure the data pulled from each site is formatted into the standardised format. 
		After each sites df is properly formatted, you will then join all 3 dfs (the dfs from each website) into one master df.
		Once you have your master df of all of the search results, you will export this df into a csv. 
		(o) if you can, write some code that will remove duplicates from the master df, you can do this by removing dupes from each individual one, or from the master df.

	5. Bring it all together.
		Using your scripts you created above, you will now make an app (just like last week) that will take in some user input, formats the input for each payload, sends a 
		unique payload (using the formatted user input) to each sites scarping function, and then formats and joins the resulting result dfs into one master df, and exports them into a csv.
	

 .----------------.  .----------------.  .----------------.        .----------------.  .----------------.  .----------------.  .----------------. 
| .--------------. || .--------------. || .--------------. |      | .--------------. || .--------------. || .--------------. || .--------------. |
| |  ________    | || | _____  _____ | || |  _________   | |      | |     ____     | || | _____  _____ | || |  _________   | || |    _______   | |
| | |_   ___ `.  | || ||_   _||_   _|| || | |_   ___  |  | |      | |   .'    `.   | || ||_   _||_   _|| || | |  _   _  |  | || |   /  ___  |  | |
| |   | |   `. \ | || |  | |    | |  | || |   | |_  \_|  | |      | |  /  .--.  \  | || |  | |    | |  | || | |_/ | | \_|  | || |  |  (__ \_|  | |
| |   | |    | | | || |  | '    ' |  | || |   |  _|  _   | |      | |  | |    | |  | || |  | '    ' |  | || |     | |      | || |   '.___`-.   | |
| |  _| |___.' / | || |   \ `--' /   | || |  _| |___/ |  | |      | |  \  `--'  /  | || |   \ `--' /   | || |    _| |_     | || |  |`\____) |  | |
| | |________.'  | || |    `.__.'    | || | |_________|  | |      | |   `.____.'   | || |    `.__.'    | || |   |_____|    | || |  |_______.'  | |
| |              | || |              | || |              | |      | |              | || |              | || |              | || |              | |
| '--------------' || '--------------' || '--------------' |      | '--------------' || '--------------' || '--------------' || '--------------' |
 '----------------'  '----------------'  '----------------'        '----------------'  '----------------'  '----------------'  '----------------' 

1). WORKING code that conducts a search from your app to all 3 websites.
2). Your first priority should be making functions that can send a search terms to another function that formats those terms into unique payloads for 
	each site, and then runs searches on all 3 sites. 

========================================================================================================================================================================================================
NOTES:	

===========================================================================================================================================================================================================