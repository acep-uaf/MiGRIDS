# MicroGRIDS Tool 
Welcome to the **MicroGRIDS** tool! MicroGRIDS stands for Micro Grid Renewable Integration Dispatch and Sizing. This tool is designed to help optimize the size and dispatch of grid components in a microgrid. While a grid connect feature is expected to be added in the future, islanded operation is the focus. Note that this is a basic implementation and more features and functionality (such as a GUI) are coming!

This tool runs time-step energy balance simulations for different grid components and controls. An advantage of this tool is that it allows you to see the effect of different dispatch schemes and settings. In smaller microgrid environments, dispatch decisions are being made on the order of seconds. Thus, in order to fully capture their effect, the simulation should be run at a short enough time step. The end result is a more realistic representation of what can be achieved by integrating different components and control strategies in a grid.

## Getting Started
### Requirements
* Python 3.6+
* netCDF4 package

### Installation

### Running MicroGRIDS
See the [project flow and directory structure wiki page](https://github.com/acep-uaf/GBSTools/wiki/Project-flow-and-directory-structure) and the [project tutorials wiki page](https://github.com/acep-uaf/GBSTools/wiki/Project-tutorials) to get started using the MicroGRIDS tool. 
