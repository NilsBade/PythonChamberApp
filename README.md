# PythonChamberApp
> Python based app that automates measurement processes for the E3 institute at TUHH.

The app connects to the measurement chamber and a vector network analyzer (VNA) that are located in the same network as the app's host via http protocol.
Given the IP addresses and API-commands of the chamber and the VNA, the app takes inputs about the desired near-field-scan (mesh, boundaries, ..) through an UI
and controls both devices/measurement equipment in an alternating fashion to achieve an automated measurement process for a defined volume.

![](figures/header.svg)

## File structure
The app is structured in a modular fashion to achieve extendability and maintainability.
This section gives you an overview of the modules that are defined, what their purposes are and where each file is located.
> [!NOTE]
> The file structure is work in progress and  must be maintained manually!

```
PythonChamberApp/
│
│
├── docs/
│   ├── user_interface.md
│   ├── connection_handler.md
│   ├── process_controller.md
│   ├── figure_generator.md
│   ├── chamber_net_interface.md
│   └── vna_net_interface.md
│
├── PythonChamberApp/
│   ├── __init__.py	[?]
│   ├── runner.py	[?]
│   ├── user_interface/
│   │   ├── __init__.py
│   │   ├── hello.py
│   │   └── helpers.py
│   │
│   ├── connection_handler/
│   │   ├── __init__.py
│   │   ├── helpers.py
│   │   └── world.py
│   │
│   ├── process_controller/
│   │	├── __init__.py
│   │   ├── helpers.py
│   │   └── world.py
│   │
│   ├── figure_generator/
│   │	├── __init__.py
│   │   ├── helpers.py
│   │   └── world.py
│   │
│   ├── chamber_net_interface/
│   │	├── __init__.py
│   │   ├── helpers.py
│   │   └── world.py
│   │
│   └── vna_net_interface/
│    	├── __init__.py
│       ├── helpers.py
│       └── world.py
│
├── data/
│   ├── figures?
│   └── logos?
│
├── tests/
│   ├── hello
│   │   ├── helpers_tests.py
│   │   └── hello_tests.py
│   │
│   └── world/
│       ├── helpers_tests.py
│       └── world_tests.py
│
├── figures/
│   └── ...
│
├── .gitignore
├── LICENSE
└── README.md
```

![](figures/SoftwareStructure.svg)

## Installation
To run the PythonChamberApp the following steps are necessary:

0. Clone this repository in a desired directory
1. Install Python 3.11.9 if not already available
2. Create a virtual environment and set Python 3.11.9 as active interpreter inside the cloned directory
3. Install necessary modules for UI and network communication from terminal.
    **PyQT6**
    ```
    python -m pip install PyQt6
    ```
    **requests**
    ```
    python -m pip install requests
    ```
4. Run PythonChamberApp from python console [?] ``ToDo``
    
<!-- 
OS X & Linux:

```sh
npm install my-crazy-module --save
```

Windows:

```sh
edit autoexec.bat
``` 
-->

## Usage example

``ToDo``
A few motivating and useful examples of how your product can be used. Spice this up with code blocks and potentially more screenshots.

_For more examples and usage, please refer to the [Wiki][wiki]._

## Development setup

``ToDo``
Describe how to install all development dependencies and how to run an automated test-suite of some kind. Potentially do this for multiple platforms.

```sh
make install
npm test
```

## Release History

* 0.0.2
    * ADD: Filestructure!
    * FIX: nothing so far
    * CHANGE: adaptations to readme file with personal data
    * started file structure based on recommendations on [RealPython](https://realpython.com/python-application-layouts/#application-with-internal-packages)
* 0.0.1
    * Initialization with templates for .gitignore file and readme

## Meta

Nils Bade – n.bade@tuhh.de

Distributed under the GPL-3.0 license. See ``LICENSE`` for more information.

[https://github.com/NilsBade](https://github.com/NilsBade)

## Contributing

1. Only desired in cooperation with E3 institute of TUHH

<!-- Markdown link & img dfn's -->
[travis-image]: https://img.shields.io/travis/dbader/node-datadog-metrics/master.svg?style=flat-square
[travis-url]: https://travis-ci.org/dbader/node-datadog-metrics
[wiki]: https://github.com/yourname/yourproject/wiki