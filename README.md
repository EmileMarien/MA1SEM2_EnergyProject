# MA1SEM2_EnergyProject
Optimization model of a home PV-system to select the optimal components. 

Part of the course "Integrated Project & Design" at the KU Leuven, Belgium.


TODO
- have contract class with costs
    either fill these in manually or scan the internet or a document
- financialmodel class in which you can either give components or electricity flow already (later also solar panel inputs etc.)
- gridcost class that calculates the cost of the grid from the given components or electricity flow 
    -> adapt to using contract
    -> Initialise it first
    -> Add calculate function that gives the cost


- optimizer that, given list of contracts and energy consumption or components, knows what is the optimal contract and displays it on graphs
- Add possibility to simulate what impact would be of solar panels, batteries, your cost. Also of gas boiler and heat pump



given the PDF of an electricity contract below, write code that reads this and returns a fully filled in electricitClass object (with all the attributes having data from the pdf contract). Is this possible?

It should read the belpex data from the internet to ensure it always has the right info -> append automatically to the list

Show graph with electricity consumption and price for the different contracts

