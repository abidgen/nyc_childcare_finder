# NYC Childcare Finder

## Summary
A Web App to assist working parents living in New York City identify childcare facilities per their preferences. 

## Problem Statement
As there are more than 3000 childcare facilities in New York City, It can be proven very difficult for a parent to compare and evaluate the safety conditions of all the facilities to identify the best options. 

Additionally, parents want these facilities to be at a convenient location, where they would not have to make a significant detour during their daily commute. 

Using the Web app, users can quickly identify all the childcare facilities located along the route of their daily commute. These facilities can be filtered based on user preferences. Moreover, they can observe the ranking of these facilities based on customized safety score metrics. They also have the option to compare two different facilities side by side to identify the best possible options.    

## Project
### Data
Initial data were collected from [NYC Open Data](https://opendata.cityofnewyork.us/ ) web portal. This specific dataset is titled ["DOHMH Childcare Center Inspections"](https://data.cityofnewyork.us/Health/DOHMH-Childcare-Center-Inspections/dsg6-ifza ), contains information regarding all childcare facilities located in New York City. In addition, this dataset contains a list of all inspections conducted by the New York City Department of Health and Mental Hygiene (NYC DOHMH) and any associated violations at active, city-regulated, center-based child care programs and summer camps over the past three years. The violations are pre-adjudicated.

### Data processing
*	All data were aggregated to get results for each specific facility.
*	Google Geocoding API was used to identify GPS coordinates of all facilities. 
*	A scoring algorithm was applied to determine the safety score for all facilities
*	All data were combined in one file for the app.

### Web App working model
*	Identify the route from the user's home address to the work address using [Google Geocoding API](https://developers.google.com/maps/documentation/geocoding/overview ) and [Google Directions API](https://developers.google.com/maps/documentation/directions/overview ).
* Use [shapely](https://shapely.readthedocs.io/en/stable/manual.html ) to determine the search area along the route or user location
* Identify facilities that fall inside the search area.
* Filter selected facilities based on user preferences.
* Plot route, search area and filtered facilities on google maps using [gmaps](https://jupyter-gmaps.readthedocs.io/en/latest/ ). 
* Provide a list of filtered facilities in descending order based on safety score. 
* The Web App was developed using [Streamlit](https://docs.streamlit.io/) framework.

```mermaid
flowchart TD
    A[Identify Route] --> B[Determine Search Area]
    B --> C[Identify Facilities within Search Aear]
    C --> D[Filter Facilities]
    D --> E:::result[Plot on Map] & F:::result[List of Facilities]
    F --> G[Campare Two facilities]
    G --> H:::result[Detaled info of facilities] & I:::result[Inspection results]
    
    classDef result fill:#b3e59d;
```


## Deliverables
* Source Code: [GitHub](https://github.com/abidgen/nyc_childcare_finder )
* Web App: [NYC Childcare Finder](https://abidgen-nyc-childcare-finder-childcare-app-99xm7h.streamlitapp.com/ )
