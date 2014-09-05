# Spatial Data Warehouse


## Features

Spatialize System Data

The spatial data warehouse tools are used to add and update existing system data to your ArcGIS Organization. Feature services are created with this data from a CSV file.

This GitHub repository houses the toolset used to stage and update the following ArcGIS for Utilities solutions:
1. [Customer Complaints](http://solutions.arcgis.com/utilities/water/help/customer-complaints/)  
2. [Water SCADA Processor](http://solutions.arcgis.com/utilities/water/help/water-scada-processor/)
	*Note: The Water SCADA Processor uses these tools to stage the services and maps only. 

Toolset features:

1. Map (fields) and adjust (project) your system data to the provided schemas
2. Truncate current views from the staged ArcGIS online feature service
3. Update the current views feature services using your system data
3. Add a dated feature service of your system data (from CSV to Feature Service)

Toolset tools:

1. Schema and sample data
2. A Python script to create the necessary feature services, maps, and apps in your ArcGIS Organization
3. A Python script that can run standalone as a Windows task scheduler, or any scheduler that can run a Python script
4. A configuration file (text) that allows you to specify the location of your system data, the sample schema, and username and password information 


## Instructions

### General Help
[New to Github? Get started here.](http://htmlpreview.github.com/?https://github.com/Esri/esri.github.com/blob/master/help/esri-getting-to-know-github.html)

## Requirements

* Notepad or a Python Editor
* ArcGIS Desktop 10.2
 
## Resources


## Issues

Find a bug or want to request a new feature?  Please let us know by submitting an issue.


## Contributing

Esri welcomes contributions from anyone and everyone.
Please see our [guidelines for contributing](https://github.com/esri/contributing).

## Licensing

Copyright 2014 Esri

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

A copy of the license is available in the repository's
[LICENSE.txt](https://raw.github.com/Esri/telco-service-qualification/master/LICENSE.txt) file.

[](Esri Tags: Utilities AGOL Python ArcGIS-Online)
[](Esri Language: Python)
