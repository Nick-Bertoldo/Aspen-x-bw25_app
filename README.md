# Aspen-x-bw: Integrating Aspen Plus Simulations with Brightway 2.5 for Sustainable Process Design

![image](https://github.com/user-attachments/assets/2d536f74-7efa-4597-974e-9781b63c8143)


This project was presented at [the 2024 Life Cycle Innovation Conference](https://fslci.org/lcic/lcic2024/lcic2024-abstracts/integrating-aspen-plus-simulations-with-brightway-2-5-for-sustainable-process-design-a-case-study-on-hydrogen-production-from-mixed-plastic-waste/) (LCIC) in Berlin, Germany.

## 📝 About
The tool integrates Aspen Plus process simulation results with Brightway 2.5 life cycle assessment framework, enabling the quantification of environmental impacts during the early stages of process design.

## 🚀 Key Features
- Material and energy flows from Aspen Plus simulations are directly imported.
- Linking process flows to ecoinvent activities.
- Computing LCA results with the open-source framework brightway 2.5.
- User-Friendly GUI built with Plotly's Dash library in Python for easy navigation and visualization.

## 💡 Uses:
Early-Stage Impact Assessment: Enables environmental impact quantification during initial design phases.

## 📋 Prerequisites
Before you begin, ensure you have met the following requirements:

- Aspen plus software;
- ecoinvent licence;
- brightway 2.5: To install bw you can follow the instructions present in this repository:  https://github.com/brightway-lca/brightway25
- [A brightway project with ecoinvent](https://docs.brightway.dev/en/latest/content/cheatsheet/importing.html).
- [Plotly Dash](https://dash.plotly.com/)

## 🔧 Installation

### Clone the Repository

```console
git clone https://github.com/Nick-Bertoldo/Aspen-x-bw25_app.git
cd Aspen-x-bw25_app
```

### App setup:
- Loading Brightway project with ecoinvent:

```python
bd.projects.set_current("<name of your project with ecoinvent>") # insert the name of your project
ei_db = bd.Database("<ecoinvent database name>") 
bio_db = bd.Database("<biosphere database name>")
# impact assessment method used for the computation of LCA impacts
EF_select = [met for met in bd.methods if met[0] == 'EF v3.1']
```

## ✨ Potential improvements
- Adding a complete unit conversion from Aspen to bw.
- Dealing with co-product.
- Improve the integration with Aspen, including a python interface directly in the app. (e.g. [AspenPythonInterface](https://github.com/YouMayCallMeJesus/AspenPlus-Python-Interface))


## 📞 Contact
If you have any questions or need help, do not hesitate to contact me:

[Nicolas Bertoldo](nicolas.bertoldo@polimi.it)

