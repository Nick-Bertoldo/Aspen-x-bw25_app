# Integrating Aspen Plus Simulations with Brightway 2.5 for Sustainable Process Design

![image](https://github.com/user-attachments/assets/2d536f74-7efa-4597-974e-9781b63c8143)


This project was presented at the 2024 Life Cycle Innovation Conference (LCIC) in Berlin, Germany (https://fslci.org/lcic/lcic2024/lcic2024-abstracts/integrating-aspen-plus-simulations-with-brightway-2-5-for-sustainable-process-design-a-case-study-on-hydrogen-production-from-mixed-plastic-waste/).

## 📝 Description
The process industry faces significant challenges in achieving sustainable development, often constrained by narrow profit margins and a conservative approach to innovation. The implementation of novel solutions to reduce environmental impact is not readily embraced in this industry. Additionally, the quantification of environmental impacts at the early stages of process design is hindered by a lack of primary data and comprehensive life cycle assessment (LCA) databases tailored to the specificities of the process industry. This research addresses this gap by introducing a novel framework that enables the quantification of environmental impacts during the initial design phase of a process.
In this study, we present a novel approach that seamlessly integrates simulation results from Aspen Plus, a widely-used process simulator, with the open-source life cycle assessment framework, Brightway 2.5. The process simulation results obtained from Aspen, namely material and energy flows, are seamlessly linked to Brightway 2.5, allowing for direct computation of environmental impacts.
The integration is facilitated through a user-friendly graphical user interface (GUI) developed using the Dash library from Plotly in Python. Such an interface serves as an intuitive bridge between Aspen Plus and Brightway 2.5, enabling researchers and practitioners to effortlessly navigate through simulation inputs, view results, and perform life cycle assessments.
The presented framework stands as a scalable and adaptable solution, aiming to foster sustainable practices by integrating seamlessly into the existing workflow, providing a valuable tool for decision-makers in the pursuit of environmentally conscious process design.

## 📋 Prerequisites

Before you begin, ensure you have met the following requirements:

- Aspen plus software;
- ecoinvent licence;
- brightway 2.5: To install bw you can follow the instructions present in this repository:  https://github.com/brightway-lca/brightway25
- A brightway project with ecoinvent (https://docs.brightway.dev/en/latest/content/cheatsheet/importing.html). 

## 🔧 Installation

### Clone the Repository

```bash
git clone https://github.com/Nick-Bertoldo/Aspen-x-bw25_app.git
cd [repository-name]
```



## ✨ Known issues and potential improvements



## 📞 Contact
If you have any questions or need help, do not hesitate to contact me:
Nicolas Bertoldo - nicolas.bertoldo@polimi.it
Project Link: https://github.com/Nick-Bertoldo/Aspen-x-bw25_app

