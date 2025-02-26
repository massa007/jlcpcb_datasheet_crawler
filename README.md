# jlcpcb_datasheet_crawler

Download Datasheets for all Parts in your BOM file from JLCPCB named "bom.xls" which is located in the same folder like the script.
BOM File should have a column named "JLCPCB Part #" which is used to ectract the needed part numbers.

Additionally you need to download geckodriver (Mozilla driver for running Selenium module) and place it in /usr/local/bin or somewhere else as long as you correct the path in the script.

Also you need to install following dependencies:

```pip3 install pandas openpyxl requests beautifulsoup4 selenium xlrd``` 
