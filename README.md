# Computational Design and Fabrication 1 (CDF1)

## Welcome

Welcome to **Computational Design and Fabrication**, a platform dedicated to beginner-friendly creative coding tutorials and exercises for computational design and fabrication in architecture.


## Session Blocks 
## General Computational Geometry

Title | Description | Slides | Session material | Assignment 
----- | ----------- | ------ | ---------------- | ----------
**01 Python Basics** | Quick start on Python | [Python Basics](https://docs.google.com/presentation/d/1itrUdpCxscddm8ilBpDHMNRPB9uUaK41vLhZXXznRcU/edit?usp=sharing) | [Session 01](https://github.com/computationaldesignandfabrication/cdf1-session-01) |[Assignment 01](https://github.com/computationaldesignandfabrication/cdf1-assignment-01)
**02 Basic Geometry 2D** | 2D primitive geometry  | [Geometry 2D](https://docs.google.com/presentation/d/1t5Old_fkJYUoT19DOXw5mV__aK2kXLFIzcbFNjCk49I/edit?usp=sharing) | [Session 02](https://github.com/computationaldesignandfabrication/cdf1-session-02) | [Assignment 02](https://github.com/computationaldesignandfabrication/cdf1-assignment-02)
**03 Basic Geometry 3D** | 3D primitive geometry  | [Geometry 3D](https://docs.google.com/presentation/d/1BRTuzIq9qnQWI6xbl-DzDe6EcIYqgHcdwXjCbWrDimM/edit?usp=sharing) | [Session 03](https://github.com/computationaldesignandfabrication/cdf1-session-03) | [Assignment 03](https://github.com/computationaldesignandfabrication/cdf1-assignment-03)
**04 Advanced Geometry** | Meshes and mesh operations | [Meshes](https://docs.google.com/presentation/d/157haw_1_zLma1QmPeS_Vz5kyLTYuytL1gbhSn71Se1M/edit?usp=sharing) |  [Session 04](https://github.com/computationaldesignandfabrication/cdf1-session-04) | [Assignment 04](https://github.com/computationaldesignandfabrication/cdf1-assignment-04)


## Session Blocks 
## Associated With the Design Tool

Title | Description | Slides | Session material | Assignment 
----- | ----------- | ------ | ---------------- | ----------
**05 Earth 3D Printing Demo** | Earth 3D Printing Demo | [Earth 3D Printing Demo](LINK) | No assignment
**06 Surface Form Finding** | Geometric form finding for compression-only structures | [Form Finding](LINK) | 
**07 Volume Form Finding** | Geometric form finding for compression-only structures | [Form Finding](LINK) | 
**08 Shape Segmentation** | Segmentation and connection detailing | [Form Finding](LINK) | 
**09 Slicing and Print Path Generation** | Slicing and Print Path generation | [Slicing and Print Path Generation](LINK) | 


## Requirements

* Windows 10 Professional
* Rhino 7 / Grasshopper
* [Anaconda Python](https://www.anaconda.com/distribution/?gclid=CjwKCAjwo9rtBRAdEiwA_WXcFoyH8v3m-gVC55J6YzR0HpgB8R-PwM-FClIIR1bIPYZXsBtbPRfJ8xoC6HsQAvD_BwE)
* [Visual Studio Code](https://code.visualstudio.com/)
* [Github Desktop](https://desktop.github.com/)

## Dependencies

* [COMPAS](https://compas-dev.github.io/)

* [matplotlib](https://matplotlib.org/)
* [COMPAS Viewer](https://compas.dev/compas_viewer/latest/index.html)


## Getting started

### Setting up the Anaconda environment

Execute the commands below in Anaconda Prompt:
	
#### Installation

    (base) conda config --add channels conda-forge
    (base) conda create -n cdf compas
    (base) conda activate cdf
    
#### Verify Installation

    (cdf) pip show compas

####
    Name: COMPAS
    Version: 2.0.2
    Summary: The COMPAS framework
    ...

#### Installation of dependencies
    conda install matplotlib
    pip install compas_viewer
    
#### Installation for Rhino

    (cdf) python -m compas_rhino.install -v 7.0


### Cloning the CDF Repository

* Firstly, create a **workspace** directory in your File Explorer:

    C:\Users\your_username\workspace

* Secondly, open Github Desktop and clone the [CDF repository](https://github.com/computational_design_and_fabrication/computational_design_and_fabrication) into your **workspace** folder.

**Done! Now you can go to VS Code, Rhino, or Grasshopper to run the example files of CDF.**

First time using VS Code and on Windows? Make sure select the correct terminal profile: Ctrl+Shift+P, Terminal: Select Default Profile and select Command Prompt.
