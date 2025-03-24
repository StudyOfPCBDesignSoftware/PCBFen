import re

class Circuit:
    def __init__(self):
        self.components = {}  # 存储元件连接信息的字典
        self.model = {} # 存储电路图中的模型，目前只是存储开关的模型
        self.topology = []  # 存储电路拓扑结构的列表
        self.power_sources = {}  # 存储电源信息的字典
        self.switch_state = {} # 记录开关状态节点信息的字典cont+，cont-
        self.nodes_connected_info = {} # 记录每个引脚相连的元器件，以及是元器件的哪个引脚
        self.title = [] # 记录网表文件的title
        self.includes = [] # 记录网表文件引用的库
        self.options = [] # 记录网表文件用的.options 命令
        self.simulation = [] # 记录仿真类型
        self.QComponents = {} # 由于三极管三引脚，有一个引脚要接地，但是self.components只存储双引角。因此在更新文件的时候，需要记录引脚情况

    def add_component(self, component_name, node_pos, node_neg, value):
        # 添加元件连接信息到字典
        self.components[component_name] = {'node_pos': node_pos, 'node_neg': node_neg, 'value': value}

    def add_topology(self, component_name):
        # 添加电路拓扑结构到列表
        self.topology.append(component_name)

    def add_power_source(self, source_name, voltage):
        # 添加电源信息到字典
        # 只提取电压值的数字部分
        voltage_value = re.search(r'\d+(\.\d+)?', voltage).group()
        self.power_sources[source_name] = float(voltage_value)

    def add_model(self, model_name, model_params):
        # 添加开关模型信息到字典
        self.model[model_name] = model_params

    def add_switch_state_node(self, swtich_name, switch_cont_pos, switch_cont_neg):
        # 添加开关状态节点信息
        state_nodes = {}
        state_nodes['cont_pos'] = switch_cont_pos
        state_nodes['cont_neg'] = switch_cont_neg
        self.switch_state[swtich_name] = state_nodes

    def print_circuit(self):
        # 打印元件连接信息和电路拓扑结构
        print("Components:")
        for component, info in self.components.items():
            print(f"{component}: {info}")
        print("\nTopology:")
        print(self.topology)
        print("\nModels")
        for model, info in self.model.items():
            print(f"{model}:{info}")

    def remove_component(self, component_name):
        # 从components中删除指定元器件
        if component_name in self.components:
            del self.components[component_name]

    def update_topology(self):
        # 更新电路拓扑结构
        self.topology = []
        for component in self.components:
            self.add_topology(component)

    def update_connections(self):
        # 更新连接关系
        connections = {}
        for comp in self.components:
            connections[comp] = []
            for other_comp in self.components:
                if comp != other_comp:
                    if self.components[comp]['node_pos'] == self.components[other_comp]['node_neg'] or \
                            self.components[comp]['node_neg'] == self.components[other_comp]['node_pos']:
                        connections[comp].append(other_comp)
        return connections

    def update_netlist(self, write_file_path):
        # 更新网表文件
        with open(write_file_path, 'w', encoding='utf-8') as file:
            # if self.title:
            #     file.write(self.title+'\n')
            file.write(".title KiCad schematic\n")
            # for include in self.includes:
            #     file.write(include)
            include_statements = "\n".join(self.includes)
            file.write(include_statements+"\n")
            option_statements = "\n".join(self.options)
            file.write(option_statements+"\n")
            for component, info in self.components.items():
                if component.upper().startswith('SW'):
                    file.write(f".model {info['value']} SW(ron={self.model.get(info['value'], {}).get('ron')} "
                               f"roff={self.model.get(info['value'], {}).get('roff')} "
                               f"vh={self.model.get(info['value'], {}).get('vh')} "
                               f"vt={self.model.get(info['value'], {}).get('vt')})\n")
                    file.write(f"{component} {info['node_pos']} {info['node_neg']} {self.switch_state[component]['cont_pos']} "
                               f"{self.switch_state[component]['cont_neg']} {info['value']}\n")
                elif component.upper().startswith("Q") or component.upper().startswith("XQ"):
                    for key, value in self.QComponents[component].items():
                        if key == 'node_pos':
                            self.QComponents[component]['node_pos'] = info['node_pos']
                        if key == 'node_neg':
                            self.QComponents[component]['node_neg'] = info['node_neg']

                    values = list(self.QComponents[component].values())
                    #print(values[0])
                    #print(f"typeddddd={type(self.QComponents[component].values())}")
                    file.write(f"{component} {values[0]} {values[1]} {values[2]} {info['value']}\n")
                else:
                    file.write(f"{component} {info['node_pos']} {info['node_neg']} {info['value']}\n")
            # file.write(".tran 0.1ms 20ms ; 时间域分析\n")
            file.write(self.simulation+'\n')

            # 为了等价变异，设置的监测点：存储电源V1的电流
            file.write(".save I(V1)\n")

            file.write(".end")