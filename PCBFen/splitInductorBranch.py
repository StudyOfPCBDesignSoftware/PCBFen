import random

def split_inductor_in_branch(circuit, BranchOfCircuit, branch_type, out_file_path, inputNetlistName):
    print("**************split resistor in branch*********")
    # 获取通路中的元器件列表
    components_in_branch = BranchOfCircuit.get(branch_type, [])
    print(components_in_branch)
    if not components_in_branch:
        print(f"在{branch_type}分支没有找到元器件，无法拆分。")
        return

    # 判断通路中是否有电阻
    def has_inductor(components):
        for component in components:
            # 如果元件以 'L' 开头，则认为是电感
            if component.startswith('L'):
                return True
        return False

    hasInductors = has_inductor(components_in_branch)
    if hasInductors:
        # 随机选择一个已存在的电阻
        # 从列表中筛选出电阻元件
        inductors = [component for component in components_in_branch if component.startswith('L')]
        random_integer = random.randint(0, len(inductors)-1)
        existing_inductor = inductors[random_integer]

        # 生成两个新电阻的名称
        new_inductor_name_1 = f"L{max([int(name[1:]) for name in circuit.components.keys() if name.startswith('L')]) + 1}"
        new_inductor_name_2 = f"L{max([int(name[1:]) for name in circuit.components.keys() if name.startswith('L')]) + 2}"

        # 获取原电阻的连接引脚
        existing_node_pos = circuit.components[existing_inductor]['node_pos']
        existing_node_neg = circuit.components[existing_inductor]['node_neg']

        # 获取原电阻的电阻值
        existing_inductor_value = circuit.components[existing_inductor]['value']
        print(f"exiting_registor_value={existing_inductor_value}")

        # 计算新电阻的电阻值
        if existing_inductor_value.lower().endswith('uh'):
            new_inductor_value = f"{float(existing_inductor_value[:-2]) / 2}uH"
        elif existing_inductor_value.lower().endswith('mh'):
            new_inductor_value = f"{float(existing_inductor_value[:-2]) / 2}mH"
        else:
            new_inductor_value = f"{float(existing_inductor_value) / 2}"

        # 添加一个新引脚
        newPINName = f"NewPin{random.randint(1, 100)}"
        # 添加两个新电阻到电路中
        circuit.add_component(new_inductor_name_1, existing_node_pos, newPINName, new_inductor_value)
        circuit.add_component(new_inductor_name_2, newPINName, existing_node_neg, new_inductor_value)

        # 删除原电阻
        circuit.remove_component(existing_inductor)

        # 更新电路拓扑结构
        circuit.update_topology()

        # 更新连接关系
        connections = circuit.update_connections()

        # 更新网表文件
        circuit.update_netlist(out_file_path+ "\\" + "InductorSplit" + inputNetlistName + ".cir")

        # 重新判断通路和断路
        # BranchOfCircuit = DetermineBranch(circuit)

        print(f"已在{branch_type}分支拆分电阻: {existing_inductor}")
        print(f"添加的新电阻: {new_inductor_name_1}, {new_inductor_name_2}")
        print(f"更新后的连接关系: {connections}")
    else:
        # 通路分支中没有电阻
        ## 后续看看是否需要保持变异文件的个数一致，如果需要则复制现有网表文件，变成新的变异文件即可
        return