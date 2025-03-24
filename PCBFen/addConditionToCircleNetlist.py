import re
import random

# 给简单环电路添加条件分支
def add_condition_to_circle_netlist(file_path, circuit, output_file_path, inputNetlistName):
    print("**********add condition to circle netlist*********")
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
    power_voltage = circuit.power_sources.get(voltage_names[0], 0)
    print(f"power_voltage={power_voltage}")

    # 遍历电路元件，找到电源元件的 node_pos 引脚名称
    power_source_node_pos = None
    for component, info in circuit.components.items():
        if component.lower().startswith('v'):
            power_source_node_pos = info['node_pos']
            break

    conditions = []
    # 根据电压值生成两个数值，用于if判断
    value1 = random.uniform(0.1,power_voltage) # 比电源值小的一个值
    value2 = random.uniform(power_voltage,power_voltage+10) # 比电源值大的一个值

    # 遍历这两个值，对应的添加语句到网表
    for value in [value1,value2]:
        ifFlag = False
        elseFlag = False
        if power_voltage > value:
            ifFlag = True
        else:
            elseFlag = True

        # 对于该开关来说，此时为通路
        ifContent = f"*添加通路可做的一些命令"
        # 此时为断路
        elseContent = f"*添加断路可做的一些命令"

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
            component_name = component
            original_value = info['value']
            numeric_value = extract_numeric_value(original_value) # 获取到电气值的数字部分

            if numeric_value:
                # 生成随机数替代原始数字
                # new_numeric_value = str(random.uniform(1, 10))
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

        # 将所有变异插入到条件模板中
        if ifFlag and not elseFlag:
            # 生成两个条件语句
            condition = f"if V({power_source_node_pos}) > {value}V {{\n{func_statements}\n}} else {{\n{alter_commands_string}\n}}"
        else:
            condition = f"if V({power_source_node_pos}) > {value}V {{\n{alter_commands_string}\n}} else {{\n{func_statements}\n}}"

        # 标志位归到初始状态，不影响下次遍历
        #ifFlag = False
        #elseFlag = False
        # 添加指令到指令语句
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
    with open(output_file_path + "\\" + "CircleNetlistAddCondition" + inputNetlistName + ".cir",
              'w', encoding='utf-8') as file:
        file.write(new_netlist_content)