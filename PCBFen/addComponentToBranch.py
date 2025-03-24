import random

from determineBranch import DetermineBranch

def add_component_to_branch(circuit, BranchOfCircuit, branch_type, out_file_path, inputNetlistName):
    print("***********add compoent to branch*************")
    # 获取断路中的元器件列表
    components_in_branch = BranchOfCircuit.get(branch_type, [])
    if not components_in_branch:
        print(f"在{branch_type}分支没有找到元器件，无法添加。")
        return

    # 随机选择一个已存在的元器件
    random_integer = random.randint(0, len(components_in_branch)-1)
    existing_component = components_in_branch[random_integer]

    # 生成新元器件的名称，可以根据需求进行修改
    # 提取电阻名字后的数字
    resistor_numbers = [int(name[1:]) for name in circuit.components.keys() if name.startswith('R')]

    # 找到最大的一个数字,+1之后作为新电阻的序号
    max_resistor_number = max(resistor_numbers)+1

    print(f"The maximum resistor number is: {max_resistor_number}")
    new_component_name = f"R{max_resistor_number}"
    print(f"new_component_name={new_component_name}")

    # 获取新元器件的连接引脚
    ## 根据定位到的元器件，在其后面加入新的元器件，根据定位元器件的引脚，确定新元器件的引脚
    ## 将新元器件添加到定位元器件之后，则定位元器件的neg引脚就是新元器件的neg引脚，需要重新定义一个新的pos引脚作为定位引脚的neg引脚
    N = 1 ## 如果未来需要添加多个元器件则修改N，这是为了给引脚添加顺序
    new_node_pos = 'NewPin' + str(N)
    new_node_neg = circuit.components[existing_component]['node_neg']
    ## 定位引脚修改neg引脚，保持与新加元器件的连接
    circuit.components[existing_component]['node_neg'] = new_node_pos

    # 随机生成一个新元器件的值
    new_value = f"{random.randint(1, 10)}k"

    # 添加新元器件到电路中
    circuit.add_component(new_component_name, new_node_pos, new_node_neg, new_value)

    # 更新电路拓扑结构
    # circuit.update_topology()

    # 更新连接关系
    connections = circuit.update_connections()

    # 更新网表文件
    circuit.update_netlist(out_file_path+ "\\" + "NetlistAddComponent" +inputNetlistName + ".cir")

    # 重新判断通路和断路
    BranchOfCircuit = DetermineBranch(circuit)

    print(f"已向{branch_type}分支添加新元器件: {new_component_name}")
    print(f"更新后的连接关系: {connections}")