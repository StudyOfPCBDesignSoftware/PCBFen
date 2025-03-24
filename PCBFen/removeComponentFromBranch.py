import random

from determineBranch import DetermineBranch

# 删除断路中的元器件：随机选择一个断路中的元器件（除了开关），将其删除
def remove_component_from_branch(circuit, BranchOfCircuit, branch_type, out_file_path, inputNetlistName):
    print("********remove component from branch*************")
    # 获取要删除的元器件列表
    components_to_remove = BranchOfCircuit.get(branch_type, [])
    if not components_to_remove:
        print(f"没有在{branch_type}分支找到要删除的元器件。")
        return
    print(f"components_to_remove={components_to_remove}")
    # 随机选择一个要删除的元器件
    random_integer = random.randint(1, len(components_to_remove)-1)
    # random_integer = 0
    component_to_remove = components_to_remove[random_integer]
    while component_to_remove.upper().startswith('SW'):
        random_integer = random.randint(1, len(components_to_remove) - 1)
        component_to_remove = components_to_remove[random_integer]

    print(f'component_to_remove={component_to_remove}')

    # 记录被删除元器件的引脚连接关系
    node_pos_to_remove = circuit.components[component_to_remove]['node_pos']
    node_neg_to_remove = circuit.components[component_to_remove]['node_neg']

    # 从电路中删除元器件
    circuit.remove_component(component_to_remove)

    # 更新电路拓扑结构
    # circuit.update_topology()

    # 更新连接关系
    connections = circuit.update_connections()

    # print("connections=",connections)

    # 更新与被删除元器件连接的元器件的引脚信息
    ## 获取元器件在分支中的位置
    position = components_to_remove.index(component_to_remove)
    print(f"position={position}")
    ## 判断元器件的前面是否有元器件
    if 0 <= position-1 < len(components_to_remove):
        # 如果被删除的元器件存在上一个元器件，这个元器件的node_neg换成删掉元器件引脚的node_neg
        print(f"被删除的元器件上面有元器件")
        for comp_con_pin in circuit.nodes_connected_info.values():
            if components_to_remove[position-1] in comp_con_pin:
                if component_to_remove in comp_con_pin:
                    print("+++++++++++++++++++++++++++")
                    if comp_con_pin[component_to_remove] == 'N':
                        print( comp_con_pin[components_to_remove[position-1]])
                        if comp_con_pin[components_to_remove[position-1]] == 'N':
                            print("N-N")
                            circuit.components[components_to_remove[position - 1]]['node_neg'] = node_pos_to_remove
                        else:
                            print("P-N")
                            circuit.components[components_to_remove[position - 1]]['node_pos'] = node_pos_to_remove
                    else:
                        if comp_con_pin[components_to_remove[position-1]] == 'N':
                            print("N-P")
                            circuit.components[components_to_remove[position - 1]]['node_neg'] = node_neg_to_remove
                        else:
                            print("P-P")
                            circuit.components[components_to_remove[position - 1]]['node_pos'] = node_neg_to_remove
    else:
        # 如果被删除的元器件不存在上一个元器件，则将下一个元器件的node_pos换成删掉元器件引脚的node_pos
        print(f"被删除的元器件前面没有元器件")
        for comp_con_pin in circuit.nodes_connected_info.values():
            if components_to_remove[position + 1] in comp_con_pin:
                if component_to_remove in comp_con_pin:
                    print("+++++++++++++++++++++++++++")
                    if comp_con_pin[component_to_remove] == 'N':
                        print(comp_con_pin[components_to_remove[position + 1]])
                        if comp_con_pin[components_to_remove[position + 1]] == 'N':
                            print("N-N")
                            circuit.components[components_to_remove[position + 1]]['node_neg'] = node_pos_to_remove
                        else:
                            print("P-N")
                            circuit.components[components_to_remove[position + 1]]['node_pos'] = node_pos_to_remove
                    else:
                        if comp_con_pin[components_to_remove[position + 1]] == 'N':
                            print("N-P")
                            circuit.components[components_to_remove[position + 1]]['node_neg'] = node_neg_to_remove
                        else:
                            print("P-P")
                            circuit.components[components_to_remove[position + 1]]['node_pos'] = node_neg_to_remove

    # 更新网表文件
    circuit.update_netlist(out_file_path+"\\"+"NetlistRemoveComponent" + inputNetlistName + ".cir")

    # 重新判断通路和断路
    BranchOfCircuit = DetermineBranch(circuit)

    print(f"已从{branch_type}分支删除元器件: {component_to_remove}")
    print(f"更新后的连接关系: {connections}")