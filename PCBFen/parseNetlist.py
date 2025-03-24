import re

from Circuit import Circuit

# 对电路进行解析，将元器件存储到数组中。其中也记录一些有用的信息用于后续需要写文件用
def parse_netlist(file_path):
    print("********parse file******************")
    circuit = Circuit()
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            # 去掉分号及其之后的内容
            line = line.split(';', 1)[0].strip()

            if not line or line.startswith('*'): # 去掉空格和注释
                continue
            if line.startswith('.title'):
                circuit.title = line # 记录网表文件的表头
                continue
            if line.startswith('.include'):
                circuit.includes.append(line) # 记录网表文件引用的库
                continue
            if line.startswith('.options'):
                circuit.options.append(line)
                continue
            if line.startswith('.tran') or line.startswith('.TRAN') or line.startswith('.dc'):
                circuit.simulation = line # 记录网表文件用的仿真语句
                continue
            if line.startswith('.end'): # 网表文件最后的.end 则不进行任何处理
                continue

            tokens = line.split()
            component_name = tokens[0]
            #print(f"component_name={component_name}")
            ## 存储电路中的开关模型
            if tokens[0].startswith('.'):
                print(f"component_name={component_name}")
                if tokens[1].upper().startswith('SW'): # 处理开关
                    model_name = tokens[1]
                    print(f'model_name={model_name}')
                    model_params_str = ' '.join(tokens[2:])
                    print(f"model_params_str={model_params_str}")

                    def extract_model_parameters(model_string):
                        # 定义匹配参数的正则表达式
                        pattern = re.compile(r'\b(\w+)=(\S+)\b')

                        # 使用正则表达式匹配模型字符串中的参数
                        matches = re.findall(pattern, model_string)

                        # 将匹配结果转换为字典
                        parameters_dict = dict(matches)

                        return parameters_dict

                    model_params_dict = extract_model_parameters(model_params_str)
                    print("Model 1 Parameters:", model_params_dict)

                    circuit.add_model(model_name, model_params_dict)
                    # print("OK")
                continue
            ## 处理电路图中的元器件
            if tokens[0].startswith('V'): # 处理电源
                #print('component_name=', component_name)
                node_pos = tokens[1]
                #print('node_pos', node_pos)
                node_neg = tokens[2]
                value = tokens[3] + ' ' + tokens[4]
                # 记录电源信息
                circuit.add_power_source(tokens[0],value)
            # 开关是以Switch开头的，之后根据开关的名字命名
            elif tokens[0].upper().startswith('SW'):
                # print(" ")
                #print('component_name=', component_name)
                node_pos = tokens[1]
                #print('node_pos', node_pos)
                node_neg = tokens[2]
                value = tokens[5]
                circuit.add_switch_state_node(tokens[0], tokens[3], tokens[4])
            # 处理以Q开头的三极管，由于三极管的引脚多于2个，因此只保留连接其他元器件的两个引脚
            elif tokens[0].upper().startswith("Q") or tokens[0].upper().startswith("XQ"):
                circuit.QComponents[tokens[0]] = {} # 记住引脚位置的顺序，为了后续写文件
                index_of_zero = tokens[1:4].index('0')
                if index_of_zero not in [0,1,2]:
                    print("三极管引脚，未有引脚接地，可能会导致错误")
                if index_of_zero == 0:
                    node_pos = tokens[2]
                    node_neg = tokens[3]
                    circuit.QComponents[tokens[0]]['node_zero'] = tokens[1]
                    circuit.QComponents[tokens[0]]['node_pos'] = tokens[2]
                    circuit.QComponents[tokens[0]]['node_neg'] = tokens[3]
                if index_of_zero == 1:
                    node_pos = tokens[1]
                    node_neg = tokens[3]
                    circuit.QComponents[tokens[0]]['node_pos'] = tokens[1]
                    circuit.QComponents[tokens[0]]['node_zero'] = tokens[2]
                    circuit.QComponents[tokens[0]]['node_neg'] = tokens[3]
                if index_of_zero == 2:
                    node_pos = tokens[1]
                    node_neg = tokens[2]
                    circuit.QComponents[tokens[0]]['node_pos'] = tokens[1]
                    circuit.QComponents[tokens[0]]['node_neg'] = tokens[2]
                    circuit.QComponents[tokens[0]]['node_zero'] = tokens[3]

                value = tokens[4]
                #print(f"tokens[1:4]={tokens[1:4].index('0')}")
                #print('Q')
            else:
                print('component_name=',component_name)
                node_pos = tokens[1]
                print('node_pos',node_pos)
                node_neg = tokens[2]
                value = tokens[3]
            circuit.add_component(component_name, node_pos, node_neg, value)
            circuit.add_topology(component_name)
    return circuit