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

* For this task, you will familiarize yourself with this example of THOR web scraping code. The notebook in this folder is the webscraping code for ksl.com. 
Read through the notebook, and familiarize yourself with the code and how it works. 

* After going through the notebook, your next task will be to change the SearchTerms (found the TESTING section, under the 'current_task'). Change the payload in the SearchTerms, to 
	match either your dream car, or your current vehicle. 
	- In order to get the proper terms to load into the SearchTerms, you will have to go to the ksl.com website, conduct a search through the website matching the criteria for the vehicle. 
		After conducting the search, follow the directions on this confluence page 
		https://asgard-analytics.atlassian.net/wiki/spaces/~63cc1c60e28ec74364cd3ecd/pages/80773232/KSL+Tasking to inspect the page and find the API call. 
		You will take the terms from the payload and put those into the SearchTerms. 
	- Then you will run this code to conduct a search for your vehicle. 
	
* Once you have gotten the search to work, your next task will be to explore the ksl website, and find any other APIs you find interesting or helpful. This is pretty much a sandbox task from here out. Just explore the website, find any API calls you can, and mess around with them in the notebook. If you want to make these API calls through python, you can right-click on the API call in your inspect element and 'copy as fetch', then you can paste this into ChatGPT and tell it to convert it into a python request.

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

1). WORKING code that conducts a searchg for your vehicle. Really we just need to see it return a DF of results.

2). Any API calls you find and make, the code to run them in the notebook. Document any findings you make on the confluence page. For now, create your own confluenece page and kep
	all of your documentation / progress there.

========================================================================================================================================================================================================
NOTES:	This tasking is very similiar to lasts weeks, except this week we are going over a different website.


===========================================================================================================================================================================================================