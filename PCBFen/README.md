# 程序说明

## 主函数
**main.py** : 主控函数。

## 网表解析

**Circuit.py** : 存储网表文件，也就是存储电路图的类。

现在Circuit.py中update_netlist中，添加了.save I(V1)命令，以后可能根据需要在修改该函数
但是addConditionToXXX两个文件没有使用undate_netlist进行，因此.save I(V1)命令

**parseNetlist.py** : 解析网表文件，并将网表（电路图）结构用Circuit类存储，存储后即可对网表文件进行一系列操作。

**determineBranch.py** : 解析好的网表文件首先判断是不是具有通路和断路分支。然后存储分支情况。后续根据是否是具有 
条件分支来判断采取何种变异方式。有条件分支的会被命名为ConditionNetlist，没有的则会命名为CircleNetlist。

## 变异策略
变异策略会根据网表是否具有条件分支，采取不同的变异策略。

### 改变电路拓扑结构

#### 具有条件分支（conditionNetlist）

**addComponentToBranch.py** : 在断路（openCircuit）增加一个元器件（目前是添加一个电阻）

**removeComponentFromBranch.py** : 在断路（openCircuit）随机删除一个元器件

**splitResistorInBranch.py** : 在通路(closedCircuit)中拆分一个电阻

#### 没有条件分支（circleNetlist）

**splitResistorInBranch.py** : 环路元器件也被存储到closedCircuit，因此也用相同函数就可以实现拆分电阻

### 改变网表文件

#### 具有条件分支（conditionNetlist）

**addConditionToConditionNetlist.py** : 在条件分支电路网表中添加If-else模块

#### 没有条件分支（circleNetlist）

**addConditionToCircleNetlist.py** : 在环电路网表中添加If-else模块

## bug检测

### EMIBugDetect.py
1.首先原种子文件以及等价变异种子文件在两种模式下进行仿真，判断是否一致
其中，包括判断是否有文件没有正确仿真。
所有等价变异的网表文件是否都成功仿真，如果有没成功仿真的则是bug candidate。

2.所有仿真成功的等价变异网表，判断仿真结果是否一致
