# Ted Henderson, Capitol Bells, Inc. 2/22/2017

Step 1: Download federal agency directory as a .csv file at https://docs.google.com/spreadsheets/d/1F2WjJfYeZJWmL6FvO-IHGSN95S77YLdZ3ByKTihfnAo/edit#gid=878701128

Step 2: Upload the .csv file to http://www.convertcsv.com/csv-to-json.htm then redownload it as a .json formatted file.

Step 3: Open your python shell, run "from directory_massager import main", then
run "main()" to output 1 version of the directory extended with geocoordinate
locations, and one version also ordered by hierarchy from the White House down,
with duplicate emails and geocoordinates removed by seniority.
 
