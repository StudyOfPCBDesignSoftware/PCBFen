import random

def split_resistor_in_branch(circuit, BranchOfCircuit, branch_type, out_file_path, inputNetlistName):
    print("**************split resistor in branch*********")
    # 获取通路中的电阻列表
    components_in_branch = BranchOfCircuit.get(branch_type, [])
    print(components_in_branch)
    if not components_in_branch:
        print(f"在{branch_type}分支没有找到电阻，无法拆分。")
        return

    # 判断通路中是否有电阻
    def has_resistor(components):
        for component in components:
            # 如果元件以 'R' 开头，则认为是电阻
            if component.startswith('R'):
                return True
        return False

    hasResistors = has_resistor(components_in_branch)
    if hasResistors:
        # 随机选择一个已存在的电阻
        # 从列表中筛选出电阻元件
        resistors = [component for component in components_in_branch if component.startswith('R')]
        random_integer = random.randint(0, len(resistors)-1)
        existing_resistor = resistors[random_integer]

        # 生成两个新电阻的名称
        new_resistor_name_1 = f"R{max([int(name[1:]) for name in circuit.components.keys() if name.startswith('R')]) + 1}"
        new_resistor_name_2 = f"R{max([int(name[1:]) for name in circuit.components.keys() if name.startswith('R')]) + 2}"

        # 获取原电阻的连接引脚
        existing_node_pos = circuit.components[existing_resistor]['node_pos']
        existing_node_neg = circuit.components[existing_resistor]['node_neg']

        # 获取原电阻的电阻值
        existing_resistor_value = circuit.components[existing_resistor]['value']
        print(f"exiting_registor_value={existing_resistor_value}")

        # 计算新电阻的电阻值
        if existing_resistor_value.lower().endswith('k'):
            new_resistor_value = f"{float(existing_resistor_value[:-1]) / 2}k"
        else:
            new_resistor_value = f"{float(existing_resistor_value) / 2}"

        # 添加一个新引脚
        newPINName = f"NewPin{random.randint(1, 100)}"
        # 添加两个新电阻到电路中
        circuit.add_component(new_resistor_name_1, existing_node_pos, newPINName, new_resistor_value)
        circuit.add_component(new_resistor_name_2, newPINName, existing_node_neg, new_resistor_value)

        # 删除原电阻
        circuit.remove_component(existing_resistor)

        # 更新电路拓扑结构
        circuit.update_topology()

        # 更新连接关系
        connections = circuit.update_connections()

        # 更新网表文件
        circuit.update_netlist(out_file_path+ "\\" + "ResistorSplit" + inputNetlistName + ".cir")

        # 重新判断通路和断路
        # BranchOfCircuit = DetermineBranch(circuit)

        print(f"已在{branch_type}分支拆分电阻: {existing_resistor}")
        print(f"添加的新电阻: {new_resistor_name_1}, {new_resistor_name_2}")
        print(f"更新后的连接关系: {connections}")
    else:
        # 通路分支中没有电阻
        ## 后续看看是否需要保持变异文件的个数一致，如果需要则复制现有网表文件，变成新的变异文件即可
        return