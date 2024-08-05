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

- Build app that will create Filters and save them to a json file  
- Add example code to current webscraping notebooks
- 

Below is the link to the confluence page for documentation / walkthrough.
https://asgard-analytics.atlassian.net/wiki/spaces/THOR/pages/116195331/Thor+Filters

Tasking / Due outs
	1. 	Using the tkinter library (or customtkinter), build a python app that will create new filters based on user selected options in the app, 
		and update / save the 	filters to a json file. 
			- Make an option to choose what json file to write to / name of the new file. Maybe make a 'default' file that is the current thor_filters, 
				and then have new created filters fgo to a new json file. The idea is to have different jsons of filters we can load into a function
				later.
	2. Add the thor_filters code to the current scraping scripts.
			- Following the instructions in https://asgard-analytics.atlassian.net/wiki/spaces/THOR/pages/116195331/Thor+Filters#Adding-to-your-Scraping-Script
			'Adding to your Scraping Script' section, modify the scraping scripts for each website to apply/use the thor_filters. 
	3. Modify you web scraping app to now use the modified scraping code that applies the thor_filters. Make sure to modify your current scraping scripts 
		in the app to account for the thor_filters.
			- Add to your current app an option to choose what json file of thor_filters to load / run with the webscraping search. 
		
	

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

1). WORKING code that conducts a search from your app to all 3 websites with thor_filters applied.
2). A python app that can create new filters based on the format in the thor_filters notebook and save them to a json file. 
3). A python app that combines webscraping of all the websites with the thor_filters applied.

========================================================================================================================================================================================================
NOTES:	

===========================================================================================================================================================================================================