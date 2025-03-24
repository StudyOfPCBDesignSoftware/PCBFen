# Program Description

## Main Function
**main.py** : The main control file.

## Netlist Parsing

**Circuit.py** : Defines the class used to store the netlist file, i.e., the circuit diagram.

**parseNetlist.py** : Parses the netlist file and stores the circuit structure using the Circuit class. Once stored, a series of operations can be performed on the netlist file.

**determineBranch.py** :After parsing the netlist, this script determines whether the circuit has closed or open branches and stores the branch information. This branch information is used to determine which mutation strategy to apply. If the circuit has conditional branches, it is named ConditionNetlist; otherwise, it is named CircleNetlist.

## Mutation Strategies

### circuit topology mutation

**addComponentToBranch.py** : Adds a component to a branch

**removeComponentFromBranch.py** :  Randomly removes a component from a branch.

**splitXXXXXInBranch.py** :Splits a XXXX (e.g., resistor) in a closed branch (closedCircuit).

### control condition mutation

**addConditionToConditionNetlist.py** : Adds a control module to the netlist with conditional branches.

**addConditionToCircleNetlist.py** : Adds a control module to the netlist without conditional branches.
