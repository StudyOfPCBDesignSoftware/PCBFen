import re
import random

# 给分支电路添加条件分支
def add_condition_to_condition_netlist(file_path, circuit, out_file_path, inputNetlistName):
    print("********add condition to condition netlist*************")
    """
    添加条件和操作到网表文件

    Parameters:
    - file_path: 网表文件路径
    - circuit: Circuit 类的实例，包含电路信息

    Returns:
    - None
    """
    # 获取电源节点名称
    # 获取所有以 "V" 开头的元素的名字
    voltage_names = [key for key in circuit.components.keys() if key.startswith('V')]
    # 获取到电源的电压值
    power_voltage = circuit.power_sources.get(voltage_names[0], 0)
    print(f"power_voltage={power_voltage}")

    # 遍历电路元件，找到电源元件的 node_pos 引脚名称
    power_source_node_pos = None
    for component, info in circuit.components.items():
        if component.lower().startswith('v'):
            power_source_node_pos = info['node_pos']
            break

    # 获取到开关模型的电压阈值
    thresholds = {name: float(re.search(r'\d+(\.\d+)?', model_params['vt']).group()) for
                     name, model_params in circuit.model.items() if name.lower().startswith('sw')}

    print("%%%$%$%%$%$%$%$%$%$%$%%$%%$%")
    print(thresholds)

    conditions = []
    # 根据电压和开关电压阈值
    for key,value in thresholds.items():
        print(f"{key}:{value}")
        ifFlag = False
        elseFlag = False
        if power_voltage > value:
            ifFlag = True
        else:
            elseFlag = True

        # 对于该开关来说，此时为通路
        ifContent = f"*Commands that can be used to add closed path"
        # 此时为断路
        elseContent = f"*Commands that can be used to add closed path"

        # ***********断路分支一些操作************
        ##### 改变元器件参数值 ######
        alter_commands = []

        # 有的元器件的电气值是有单位的，要去掉单位
        def extract_numeric_value(value_string):
            # 使用正则表达式提取数字部分
            match = re.search(r'(\d+(\.\d+)?)', value_string)
            if match:
                numeric_value = match.group(1)
                return numeric_value
            return None

        # 修改元器件的电气值
        for component, info in circuit.components.items():
            #if not component.upper().startswith('SW'): # 不是开关的剩下所有元器件
            if component.upper().startswith('D') or component.upper().startswith('L') or component.upper().startswith('C'):
                component_name = component
                original_value = info['value']
                numeric_value = extract_numeric_value(original_value) # 获取到电气值的数字部分

                if numeric_value:
                    # 生成随机数替代原始数字
                    # new_numeric_value = str(random.uniform(1, 10))l
                    new_numeric_value = str(random.randint(1, 10))
                    # 替换原始数字部分
                    new_value = f"{component_name} {new_numeric_value}"
                    alter_command = f"alter {new_value}"
                    alter_commands.append(alter_command)
        # 打印生成的命令字符串
        for command in alter_commands:
            print(command)

        # 使用join方法将alter_commands中的字符串按行连接
        alter_commands_string = "\n".join(alter_commands)

        ##### 添加一些计算 #######
        # Custom function definition
        custom_function_definition = ".func my_function(x) sin(2*pi*x)"

        # Usage of custom function with a component's value
        # 过滤掉不以数字开头的元器件的电气值，并只获取数字部分
        numeric_values = [re.sub(r'[^0-9.]', '', component['value']) for component in circuit.components.values() if
                          re.match(r'^\d', component['value'])]

        # 随机选择一个元器件，并获取到他的value值
        component_value = random.choice(numeric_values)
        usage_of_custom_function = f"let result = my_function({component_value})"
        print_result = "print result"

        # 将自定义函数定义和使用插入到条件模板中
        functions = [
            custom_function_definition,
            f"{usage_of_custom_function}\n{print_result}"
        ]

        # 根据conditions的长度生成相应数量的条件语句
        func_statements = "\n".join(functions)

        ####### 修改元器件使用的模型参数 #######
        print(circuit.model)
        alter_model_parameters = []
        for model_name, parameters in circuit.model.items():
            alter_command = f"alterparam {model_name} "
            random_parameters = {param: f'{random.randint(1, 100)}' for param in parameters}
            parameters_str = ' '.join([f"{param}={value}" for param, value in random_parameters.items()])
            full_command = alter_command + parameters_str
            alter_model_parameters.append(full_command)
            print(full_command)

            # 根据conditions的长度生成相应数量的条件语句
            modelPara_statements = "\n".join(alter_model_parameters)

        # 将所有变异插入到条件模板中
        if ifFlag:
            # 生成两个条件语句
            condition = f"if V({power_source_node_pos}) > {value}V {{\n{ifContent}\n}} else {{\n{alter_commands_string}\n{func_statements}\n{modelPara_statements}\n}}"
        else:
            condition = f"if V({power_source_node_pos}) > {value}V {{\n{alter_commands_string}\n{func_statements}\n{modelPara_statements}\n}} else {{\n{ifContent}\n}}"
        # 标志位归到初始状态
        conditions.append(condition)

    # 根据conditions的长度生成相应数量的条件语句
    condition_statements = "\n".join(conditions)

    # 合成新控制块
    new_control_block = f".control\nrun\n{condition_statements}\nrun\n.endc"

    with open(file_path, 'r', encoding='utf-8') as file:
        netlist_content = file.read()

    print(f'type={netlist_content}')

    # 找到.end行的位置
    end_position = netlist_content.find('.end')
    print(f"end_position={end_position}")

    tran_position = netlist_content.find('.tran')
    print(f"tran={tran_position}")

    dc_position = netlist_content.find('.dc')
    print(f"dc_position={dc_position}")

    if end_position != -1:
        insertPosition = end_position
    elif tran_position != -1:
        insertPosition = tran_position
    else:
        insertPosition = dc_position

    print(f"insertPosition={insertPosition}")

    # 在.end行之前插入新的.control块
    new_netlist_content = (
        f"{netlist_content[:insertPosition]}\n{new_control_block}\n.save I(V1)\n{netlist_content[insertPosition:]}"
    )

    # 将修改后的内容写回到文件中
    with open(out_file_path + "\\" + "ConditionNetlistAddCondition" + inputNetlistName + ".cir",
              'w', encoding='utf-8') as file:
        file.write(new_netlist_content)