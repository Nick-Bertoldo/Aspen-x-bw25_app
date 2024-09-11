# Integrating Aspen Plus Simulations with Brightway 2.5 for Sustainable Process Design

This project was presented at the 2024 Life Cycle Innovation Conference (LCIC) in Berlin, Germany.

## Brief description:  
The process industry faces significant challenges in achieving sustainable development, often constrained by narrow profit margins and a conservative approach to innovation. The implementation of novel solutions to reduce environmental impact is not readily embraced in this industry. Additionally, the quantification of environmental impacts at the early stages of process design is hindered by a lack of primary data and comprehensive life cycle assessment (LCA) databases tailored to the specificities of the process industry. This research addresses this gap by introducing a novel framework that enables the quantification of environmental impacts during the initial design phase of a process.
In this study, we present a novel approach that seamlessly integrates simulation results from Aspen Plus, a widely-used process simulator, with the open-source life cycle assessment framework, Brightway 2.5. The process simulation results obtained from Aspen, namely material and energy flows, are seamlessly linked to Brightway 2.5, allowing for direct computation of environmental impacts.
The integration is facilitated through a user-friendly graphical user interface (GUI) developed using the Dash library from Plotly in Python. Such an interface serves as an intuitive bridge between Aspen Plus and Brightway 2.5, enabling researchers and practitioners to effortlessly navigate through simulation inputs, view results, and perform life cycle assessments.
The presented framework stands as a scalable and adaptable solution, aiming to foster sustainable practices by integrating seamlessly into the existing workflow, providing a valuable tool for decision-makers in the pursuit of environmentally conscious process design.

## Installation
For the app to work properly, you need to have installed in you computer brightway 2.5 and since the app is based on ecoinvent database, you need to have a valid ecoinvent licence.
To install bw you can follow the instructions present in this repository:  
https://github.com/brightway-lca/brightway25

