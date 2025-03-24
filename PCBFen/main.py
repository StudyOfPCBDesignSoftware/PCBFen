import re
import random
import os
import shutil
import time

from parseNetlist import parse_netlist
from determineBranch import DetermineBranch
from removeComponentFromBranch import remove_component_from_branch
from addComponentToBranch import add_component_to_branch
from splitResistorInBranch import split_resistor_in_branch
from splitCapacitorBranch import split_capacitor_in_branch
from splitInductorBranch import split_inductor_in_branch
from addConditionToConditionNetlist import add_condition_to_condition_netlist
from addConditionToCircleNetlist import add_condition_to_circle_netlist


# 主函数
def main(input_file_path,ouput_file_path,inputNetlistname):
    # 解析并存储电路图
    circuit1 = parse_netlist(input_file_path)
    circuit2 = parse_netlist(input_file_path)
    circuit3 = parse_netlist(input_file_path)
    circuit4 = parse_netlist(input_file_path)
    circuit5 = parse_netlist(input_file_path)
    circuit6 = parse_netlist(input_file_path)

    # 打印电路信息
    #circuit1.print_circuit()
    #circuit2.print_circuit()
    #circuit3.print_circuit()
    #circuit4.print_circuit()

    # 具有条件分支的电路，判断通路和断路的标志
    BranchOfCircuit,watchDog = DetermineBranch(circuit1)
    print("==========---------------============")
    print(BranchOfCircuit)
    print(f"watchDog={watchDog}")

    # watchDog == 1，带有分支的电路（也就是带开关，有通路和断路得开关）

    if watchDog == 1:
        # 在断路删除一个元器件，保证电路仍然连接
        remove_component_from_branch(circuit1, BranchOfCircuit, 'OpenCircuit', ouput_file_path, inputNetlistname)

        # 在断路增加一个元器件，保证电路连接性
        add_component_to_branch(circuit2, BranchOfCircuit, 'OpenCircuit', ouput_file_path, inputNetlistname)
        # 在网表文件中添加IF else条件分支块
        add_condition_to_condition_netlist(input_file_path, circuit4, ouput_file_path, inputNetlistname)

    # 在通路中选择一个电阻，在这个电阻的位置，将这个电阻变成两个电阻，两个电阻的电阻值正好等于原来一个电阻的电阻值，修改完毕后，保持电路分支的连接
    split_resistor_in_branch(circuit3, BranchOfCircuit, 'ClosedCircuit', ouput_file_path, inputNetlistname)
    split_capacitor_in_branch(circuit5, BranchOfCircuit, 'ClosedCircuit', ouput_file_path, inputNetlistname)
    split_inductor_in_branch(circuit6, BranchOfCircuit, 'ClosedCircuit', ouput_file_path, inputNetlistname)

    # watchDog == 0，单纯一个环的电路
    if watchDog == 0:
        ## 在网表文件中添加IF else条件分支块
        add_condition_to_circle_netlist(input_file_path, circuit4, ouput_file_path, inputNetlistname)

# 获取到文件加下所有文件和子文件夹的名称
def get_all_files_in_folder(folder_path):
    all_files = []

    # 遍历folder_path下的每一个文件和文件夹
    for entry in os.listdir(folder_path):
        full_path = os.path.join(folder_path, entry)

        # 如果是文件，添加到结果列表中
        if os.path.isfile(full_path):
            all_files.append(full_path)
        # 如果是文件夹，递归调用函数
        elif os.path.isdir(full_path):
            all_files.extend(get_all_files_in_folder(full_path))

    return all_files

# 给种子文件添加监测点
def addWatchPointToBaseNetlist(inputfile,output_file_path):
    with open(inputfile, 'r', encoding='utf-8') as file:
        netlist_content = file.read()

    end_position = netlist_content.find('.end')
    print(f"end_position={end_position}")

    new_netlist_content = (
        f"{netlist_content[:end_position]}\n.save I(V1)\n{netlist_content[end_position:]}"
    )
    print(output_file_path + "\\" + inputfile[last_backslash_pos + 1:])

    with open(output_file_path + "\\" + inputfile[last_backslash_pos + 1:],
              'w', encoding='utf-8') as file:
        file.write(new_netlist_content)


if __name__ == '__main__':

    start_time = time.time()
    # 读取网表文件并解析
    # file_path = "E:\\PythonProjects\\SchematicNetlistEMI\\Netlists\\SchematicNetlistTest.cir"
    # file_path = "E:\\PythonProjects\\SchematicNetlistEMI\\Netlists\\test4_5.cir"
    # file_path = "E:\\PythonProjects\\SchematicNetlistEMI\\Netlists\\"
    file_path = ".\\Netlists\\" # 网表所在文件
    #output_path = file_path+'Results'
    output_path = ".\\Results" # 存放网表变异结果所在文件

    if not os.path.exists(output_path):
        print("路径不存在")
        os.mkdir(output_path)
        numbers = 0
    else:
        print("路径存在\n")
        files_in_current_directory = os.listdir(output_path)

        if files_in_current_directory: # 如果Results存在，但是里面存在其它网表的EMI变异文件夹
            print(f"files in current directory {type(files_in_current_directory)}")
            last_file_name = files_in_current_directory[-1]
            print(f"且当前的最后一个文件夹为={last_file_name}")
            numbers = int(last_file_name)+1
        else: # 只是Results文件夹存在，但是里面是空的
            numbers = 0

    all_files = get_all_files_in_folder(file_path) #获取到所有网表文件
    #print(all_files)

    for inputfilepath in all_files:
        print("inputfile=",inputfilepath)
        last_backslash_pos = inputfilepath.rfind('\\')
        inputNetlistName = inputfilepath[last_backslash_pos+1:-4]
        print(inputfilepath[last_backslash_pos+1:-4])

        # 创建每个网表单独的文件夹，用来存放变异结果
        output_file_path = output_path+"\\"+str(numbers)+"_"+inputNetlistName
        #output_file_path = output_path + "\\" + inputfile[last_backslash_pos + 1:-4]
        print(output_file_path)
        if not os.path.exists(output_file_path):
            os.mkdir(output_file_path)


        
        # 对网表文件进行等价变异
        main(inputfilepath,output_file_path,inputNetlistName)

        #shutil.move(file_path+inputfile,output_file_path)
        ## 变异的时候，目前是直接将源网表文件粘贴过去，如果想要进行bug检测的时候，也需要添加监测点（即：查看某点的电流或电压）
        # 未添加监测点：：将原文件复制到变异后的文件所在文件夹下
        #shutil.copy2(inputfile, output_file_path)
        # 给base种子网表，添加监测点.save I(V1)(监测V1的电流)
        addWatchPointToBaseNetlist(inputfilepath,output_file_path)

        numbers += 1
    end_time = time.time()
    run_time = end_time -start_time
    print("run_time=",run_time)