# Leak Survey Updater


## Features

Leak Survey Updater

The ArcGIS for Gas Leak Survey solutions use a series of Python scripts to calculate and share data. These tools leverage core ArcGIS Platform technology to calculate leak survey grid information, update the work order and leak survey grid feature classes, and calculate the compliance overview data.  

This GitHub repository houses the data aggregation toolset needed for the [Leak Survey Manager](http://solutions.arcgis.com/utilities/gas/help/leak-survey-manager/) and [Leak Survey Compliance Dashboard](http://solutions.arcgis.com/utilities/gas/help/leak-survey-dashboard/) solutions.

Toolset features:

1. Calculate leak survey grid days until due, footage of mains, number of services, and date completed fields.
2. Create and update workorder from assigned leak survey grids.
3. Calculate leak survey compliance overviews

Toolset tools:

1. Sample schema and data
3. A python scripts that can run standalone as a Windows task scheduler, or any scheduler that can run a python script
4. A configuration file (text) that allows you to specify the location of your gas network, leak survey grid, and overview areas data


## Instructions

### General Help
[New to Github? Get started here.](http://htmlpreview.github.com/?https://github.com/Esri/esri.github.com/blob/master/help/esri-getting-to-know-github.html)

## Requirements

* Notepad or a Python Editor
* ArcGIS Desktop 10.2
* ArcGIS for Server 10.2
 
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
