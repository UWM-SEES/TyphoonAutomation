# TyphoonAutomator
**An automation tool for [Typhoon HIL](https://www.typhoon-hil.com/) simulations**

Created by the [Center for Sustainable Electric Energy Systems](https://github.com/uwm-sees) at the [University of Wisconsin - Milwaukee](https://uwm.edu/).

This project is a work in progress and is still in its early phases.  See the **Contributing** section below!

## Purpose
Intended uses of this tool include:
- Real-time Controller Hardware in the Loop (CHIL) testing
- Generating data for Machine Learning and Artificial Intelligece (ML/AI)
- Online training of Reinforcement Learning (RL) and similar learning methods
- Development of Digital Twins (DT)

## Goals
The goal of this project is to create a tool which can automate the interaction with Typhoon HIL simuluations.  Its primary features should include:
- Reading and writing SCADA values and model variables while the simulation is running
- Recording high resolution sensor and probe data to files
- Repeating a large number of simulations with random variations to each run

## Summary
Users should have the ability to write a script which will automate the interaction with an HIL simulation.  Model values can be read and written in near real-time while the simulation is running.  Each run of the simulation may be randomized, e.g. a fault could be induced randomly with a normal distribution around a pre-scheduled simulation time.  Sensor and probe data from each run of the simuation can be captured and stored.  The real-time capability of Typhoon hardware will allow a large volume of rich simulation and test data to be rapidly generated.

Users will need a Typhoon license suitable for running their models on the intended simulation platform.

## Contributing
Use of this tool should be as simple as providing a Typhoon schematic and an automation script to the tool.  This feature, like many other features, is not yet complete.  **Contributions to this project are welcome and encouraged!**  Feel free to post questions or comments on the Issues page or to fork the repository and improve the project.

Active work should merged into the `dev` branch, preferably through a pull request with appropriate reviewers.  Adding unit testing, CI/CD, and **documentation** would be fantastic.  The `main` branch should be reserved for release-ready code.
