import random

def split_capacitor_in_branch(circuit, BranchOfCircuit, branch_type, out_file_path, inputNetlistName):
    print("**************split resistor in branch*********")
    # 获取通路中的电阻列表
    components_in_branch = BranchOfCircuit.get(branch_type, [])
    print(components_in_branch)
    if not components_in_branch:
        print(f"在{branch_type}分支没有找到电阻，无法拆分。")
        return

    # 判断通路中是否有电阻
    def has_capacitor(components):
        for component in components:
            # 如果元件以 'R' 开头，则认为是电阻
            if component.startswith('C'):
                return True
        return False

    hasCapacitors = has_capacitor(components_in_branch)
    if hasCapacitors:
        # 随机选择一个已存在的电容
        # 从列表中筛选出电容元件
        capacitors = [component for component in components_in_branch if component.startswith('C')]
        random_integer = random.randint(0, len(capacitors)-1)
        existing_capacitor = capacitors[random_integer]

        # 生成两个新电容的名称
        new_capacitor_name_1 = f"C{max([int(name[1:]) for name in circuit.components.keys() if name.startswith('C')]) + 1}"
        new_capacitor_name_2 = f"C{max([int(name[1:]) for name in circuit.components.keys() if name.startswith('C')]) + 2}"

        # 获取原电容的连接引脚
        existing_node_pos = circuit.components[existing_capacitor]['node_pos']
        existing_node_neg = circuit.components[existing_capacitor]['node_neg']

        # 获取原电阻的电阻值
        existing_capacitor_value = circuit.components[existing_capacitor]['value']
        print(f"exiting_capacitor_value={existing_capacitor_value}")

        # 计算新电阻的电阻值
        if existing_capacitor_value.lower().endswith("nf"):
            new_capacitor_value = f"{float(existing_capacitor_value[:-2]) / 2}nF"
        else:
            new_capacitor_value = f"{float(existing_capacitor_value) / 2}"

        # 添加一个新引脚
        newPINName = f"NewPin{random.randint(1, 100)}"
        # 添加两个新电阻到电路中
        circuit.add_component(new_capacitor_name_1, existing_node_pos, existing_node_neg, new_capacitor_value)
        circuit.add_component(new_capacitor_name_2, existing_node_pos, existing_node_neg, new_capacitor_value)

        # 删除原电阻
        circuit.remove_component(existing_capacitor)

        # 更新电路拓扑结构
        circuit.update_topology()

        # 更新连接关系
        connections = circuit.update_connections()

        # 更新网表文件
        circuit.update_netlist(out_file_path+ "\\" + "CapacitorSplit" + inputNetlistName + ".cir")

        # 重新判断通路和断路
        # BranchOfCircuit = DetermineBranch(circuit)

        print(f"已在{branch_type}分支拆分电阻: {existing_capacitor}")
        print(f"添加的新电阻: {new_capacitor_name_1}, {new_capacitor_name_2}")
        print(f"更新后的连接关系: {connections}")
    else:
        # 通路分支中没有电阻
        ## 后续看看是否需要保持变异文件的个数一致，如果需要则复制现有网表文件，变成新的变异文件即可
        return