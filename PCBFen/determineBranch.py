import re

# 判断switch分支的
def DetermineBranch(circuit):
    print("********determine branch***********")
    # 构建连接关系,根据引脚连接关系，判断每个元器件与之相连的元器件
    # 首先统计所有的节点
    all_nodes = set()
    for component in circuit.components.values():
        all_nodes.add(component['node_pos'])
        all_nodes.add(component['node_neg'])
    unique_nodes = list(all_nodes)
    print("Unique Nodes:", unique_nodes)

    # 统计每个节点相连的元器件，以及这个节点是元器件的第几节点
    node_connected_info = {}
    for node in unique_nodes:
        node_connected_info[node] = {}
        for component_name, component in circuit.components.items():
            if component['node_pos'] == node:
                node_connected_info[node][component_name] = "P"
            elif component['node_neg'] == node:
                node_connected_info[node][component_name] = "N"

    # 打印结果
    print(node_connected_info)
    for node, info in node_connected_info.items():
        print(f"Node: {node}")
        print(f"info: {info}")

    circuit.nodes_connected_info = node_connected_info

    # Find switch names dynamically
    switch_names = [component for component in circuit.components if component.lower().startswith('sw')]
    print(f"switch_names={switch_names}")

    watchFlag = 0 # 监视电路图类型，1 = 条件分支电路；0 = 正常一个环的电路
    if len(switch_names) != 0: # 生成的条件分支电路是通过开关实现的，因此判断电路中是否有开关来判断是不是分支电路
        watchFlag = 1
        # 根据统计的节点连接的元器件以及元器件是哪个节点相连的，判断出元器件相连的分支
        ## 因为条件分支是从电源开始的，就会导致有的顶点是三个元器件相连，我们就可以通过这个判断条件分支是从哪个开始的


    print(f"watchFlag={watchFlag}")
    # Store connected components in a dictionary
    connected_components_dict = {}

    Branch = []

    if watchFlag == 1: # watchFlag = 1 判断是条件分支电路
        StartComponents = []  # 条件分支开始的节点
        endComponents = []  # 条件分支结束的节点
        # for key,values in Components.items():
        for key, values in node_connected_info.items():
            if len(values) == 3:
                if values.get('V1') == 'P':
                    for value in values.keys():
                        if not value.upper().startswith("V"):
                            StartComponents.append(value)
                if values.get('V1') == 'N':
                    print("N")
                    for value in values.keys():
                        if not value.upper().startswith("V"):
                            endComponents.append(value)
        print(StartComponents)
        print(endComponents)
        ## 通过条件分支开始的节点，通过node_connected_info来获取每条分支相连元器件的情况
        for startcom in StartComponents:
            print("*********************")
            stack = []  # 定义一个栈，来存储与上一个元器件相连的元器件
            stack.append(startcom)
            Connections = []  # 存储相连的元器件
            Connections.append(startcom)
            visited = set()  # 定义一个如何元器件已经连连接上时，就不在重复判断是不是相连
            while stack:
                comp = stack.pop()
                if comp not in visited:
                    visited.add(comp)
                    # print(f"visited={visited}")
                    for values in node_connected_info.values():
                        if len(values) != 3:
                            if comp in values.keys():
                                for value in values.keys():
                                    # print(f"value={value}")
                                    if value != comp:
                                        if value not in visited:
                                            stack.append(value)
                                            # print(f"middle len(stack)={len(stack)}")
                                            Connections.append(value)
                                            visited.add(comp)
                                            # print(f"visited={visited}")
            Branch.append(Connections)

        print(f"Branch={Branch}")
        # 寻找与每个开关在同一分支的元器件
        for switch_name in switch_names:
            # 判断通路和断路
            # 获取电源的电压值
            source_voltage = float(circuit.power_sources.get('V1', 0))
            # print(f'source_voltage={source_voltage}')

            # 获取开关使用的模型的Vt阈值
            switch_model_vt = float(re.search(r'\d+(\.\d+)?', circuit.model[circuit.components[switch_name]['value']]['vt']).group())

            switch_branch = []
            for branch in Branch:
                if switch_name in branch:
                    switch_branch = branch

            # 比较电源电压值和开关模型Vt阈值
            if source_voltage >= switch_model_vt:
                # 当前分支为通路
                print("Closed:",switch_name)
                connected_components_dict['ClosedCircuit'] = switch_branch
                #print(f"电源电压值({source_voltage}V) 大于等于 开关({switch_name}) 使用模型的Vt阈值({switch_model_vt}V)，当前分支为通路。\n")
            else:
                # 当前分支为断路
                print("Open:",switch_name)
                connected_components_dict['OpenCircuit'] = switch_branch
                #print(f"电源电压值({source_voltage}V) 小于 开关({switch_name}) 使用模型的Vt阈值({switch_model_vt}V)，当前分支为断路。\n")

        # Print the results
        for BranchType, connected_components in connected_components_dict.items():
            print(f"与{BranchType}在同一分支的元器件: {connected_components}")

    if watchFlag == 0: # 电路图单纯一个环
        print("********单纯一个环***********")
        StartComponents = []  # 条件分支开始的节点
        endComponents = []  # 条件分支结束的节点
        # for key,values in Components.items():
        for key, values in node_connected_info.items():
            if values.get('V1') == 'P':
                for value in values.keys():
                    if not value.upper().startswith("V"):
                        StartComponents.append(value)
            if values.get('V1') == 'N':
                print("N")
                for value in values.keys():
                    if not value.upper().startswith("V"):
                        endComponents.append(value)
        print(StartComponents)
        print(endComponents)
        ## 通过条件分支开始的节点，通过node_connected_info来获取每条分支相连元器件的情况

        for startcom in StartComponents:
            print("*********************")
            stack = []  # 定义一个栈，来存储与上一个元器件相连的元器件
            stack.append(startcom)
            Connections = []  # 存储相连的元器件
            Connections.append(startcom)
            visited = set()  # 定义一个如何元器件已经连连接上时，就不在重复判断是不是相连
            while stack:
                comp = stack.pop()
                if comp not in visited:
                    visited.add(comp)
                    # print(f"visited={visited}")
                    for values in node_connected_info.values():
                        if 'V1' not in values:
                            if comp in values.keys():
                                for value in values.keys():
                                    # print(f"value={value}")
                                    if value != comp:
                                        if value not in visited:
                                            stack.append(value)
                                            # print(f"middle len(stack)={len(stack)}")
                                            Connections.append(value)
                                            visited.add(comp)
                                            # print(f"visited={visited}")
            # Branch.append(Connections)
        # 单纯一个环的电路，都叫ClosedCircuit
        connected_components_dict['ClosedCircuit'] = Connections

    return connected_components_dict, watchFlag