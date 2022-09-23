import os

from src.utils import read_data, write_data
from typing import List, Dict
import re
from tqdm import tqdm
from collections import Counter

def have_constant(target_template: List) -> bool:
    for val in target_template:
        if val.strip() == "1":
        # if val.strip() == "pi" or val.strip() == "PI":
            return True
    return False

def have_pi(target_template: List) -> bool:
    for val in target_template:
        if val.strip() == "PI":
        # if val.strip() == "pi" or val.strip() == "PI":
            return True
    return False

def have_square(target_template: List) -> bool:
    for val in target_template:
        if val.strip() == "^":
            return True
    return False


def count_variable(target_template: List) -> int:
    num_vars = set()
    for val in target_template:
        if val.strip().startswith("temp_"):
            num_vars.add(val.strip())
    return len(num_vars)

def have_multiple_m0(target_template: List):
    target_string = ' '.join(target_template)
    target_string = target_string.replace("()", "").replace("( )", "")
    target_string = re.sub(r"\(.*\)", "temp_m", target_string)
    target_template = target_string.split()
    high_priority_symbol_pos = []
    for idx, val in enumerate(target_template):
        if val in {"*", "/"}:
            high_priority_symbol_pos.append(idx)
    for prev, next in zip(high_priority_symbol_pos[:-1], high_priority_symbol_pos[1:]):
        if next - prev != 2:
            return True
    return False

def check_in_labels(current_tuple, labels):
    if current_tuple in labels:
        return current_tuple
    if current_tuple[-1] in {'+', '*'} and [current_tuple[1], current_tuple[0], current_tuple[-1]] in labels:
        return [current_tuple[1], current_tuple[0], current_tuple[-1]]
    return None

def get_labels(target_norm_post_template: List, target_template: List, remove_duplicate: bool = False):
    assert target_norm_post_template[:2] == ["X", "="] or target_norm_post_template[:2] == ["x", "="]
    # if len(target_norm_post_template) == 3:
    #     assert target_norm_post_template[2].startswith("temp_")
    #     target_norm_post_template.append("1")
    #     target_norm_post_template.append("*")
    stack = []
    pointer = 2
    labels = []
    both_m = False
    eq_2_m = {}
    contain_constant = False
    got_duplicate = False
    while pointer != len(target_norm_post_template):
        stack.append(target_norm_post_template[pointer])
        if stack[-1] in {'+', '-', '*', '/', '^'}:
            if len(stack[-3:]) == 3:
                if stack[-3].startswith("m_") and stack[-2].startswith("m_"):
                    both_m = True
                if remove_duplicate:
                    checker = check_in_labels([stack[-3], stack[-2], stack[-1]], labels)
                    if checker:
                        got_duplicate= True
                        m_string = eq_2_m[' '.join(checker)]
                    else:
                        labels.append([stack[-3], stack[-2], stack[-1]])
                        m_string = f"m_{len(labels)}"
                        eq_2_m[' '.join([stack[-3], stack[-2], stack[-1]])] = m_string
                else:
                    labels.append([stack[-3], stack[-2], stack[-1]])
                    m_string = f"m_{len(labels)}"
                stack.pop()
                stack.pop()
                stack.pop()
                stack.append(m_string)
        pointer += 1
    for i, (left, right, op) in enumerate(labels):
        # left = left[-1:] if left.startswith("temp_") else left
        # right = right[-1:] if right.startswith("temp_") else right
        if left.startswith("m_") or right.startswith("m_"):
            if left.startswith("m_") and right.startswith("m_"):
                left_is_smaller = (ord(left[-1:]) - ord(right[-1:])) <= 0
                modified_op = op + "_rev" if op in {'-', '/', '^'} and (not left_is_smaller) else op
                labels[i] = [left, right, modified_op] if left_is_smaller else [right, left, modified_op]
            elif right.startswith("m_"):
                modified_op = op + "_rev" if op in {'-', '/', '^'} else op
                labels[i] = [right, left, modified_op]
                if not left.startswith("temp_"):
                    labels[i] = [right, str(float(left)), modified_op]
                    const_list.add(str(float(left)))
                    const2num[str(float(left))] +=1
                    contain_constant = True
            else:
                if not right.startswith("temp_"):
                    labels[i] = [left, str(float(right)), op]
                    const_list.add(str(float(right)))
                    const2num[str(float(right))] += 1
                    contain_constant = True
        else:
            if left.startswith("temp_") or right.startswith("temp_"):
                if left.startswith("temp_") and right.startswith("temp_"):
                    left_is_smaller = (ord(left[-1:]) - ord(right[-1:])) <= 0
                    modified_op = op + "_rev" if op in {'-', '/', '^'} and (not left_is_smaller) else op
                    labels[i] = [left, right, modified_op] if left_is_smaller else [right, left, modified_op]
                elif right.startswith("temp_"):
                    modified_op = op + "_rev" if op in {'-', '/', '^'} else op
                    labels[i] = [right, str(float(left)), modified_op]
                    const_list.add(str(float(left)))
                    const2num[str(float(left))] += 1
                    contain_constant = True
                else:
                    # pass
                    labels[i] = [left, str(float(right)), op]
                    const_list.add( str(float(right)))
                    const2num[ str(float(right))] += 1
                    contain_constant = True
                    # assert right in {"1", "PI", "12"}
            else:
                labels[i] = [str(float(left)), str(float(right)), op]
                const_list.add(str(float(left)))
                const_list.add(str(float(right)))
                const2num[str(float(left))] += 1
                const2num[str(float(right))] += 1
                contain_constant = True
                # print("be "labels[i]) ## both are constant
                pass
                # raise NotImplementedError(f"all constant for label: {labels[i]}")

    for i, (left, right, op) in enumerate(labels):
        left = left[-1:] if left.startswith("temp_") else left
        right = right[-1:] if right.startswith("temp_") else right
        # if (left == "PI" or right == "PI"):# and op not in {'*', '/'}:
        #     print(labels[i])
        labels[i] = [left, right, op]

    temp_var_list = [v for v in target_template if v.startswith("temp_")]
    gap = 0
    if len(temp_var_list) !=0:
        max_temp_org = max(temp_var_list)
        max_temp_update = max([v for v in target_norm_post_template if v.startswith("temp_")])
        gap = ord(max_temp_org[-1]) - ord(max_temp_update[-1])
        if gap > 0:
            for i, (left, right, op) in enumerate(labels):
                left = chr(ord(left) + gap) if len(left) == 1 and ord(left) >= ord('a') and ord(left) <= ord('z') else left
                right = chr(ord(right) + gap) if len(right) == 1 and ord(right) >= ord('a') and ord(right) <= ord('z') else right
                labels[i] = [left, right, op]
    return labels, both_m, gap, contain_constant, got_duplicate

def check_intermediate_m_in_order(labels: List[List[str]]):
    current_m_idx = 0
    for idx, (left_var, right_var, op) in enumerate(labels):
        if left_var.startswith("m_"):
            # try:
            assert int(left_var[2:]) - current_m_idx == 1
            # except:
            #     print("not incremental")
            current_m_idx += 1
    return True


def process_obj(obj: Dict, remove_duplicate: bool = False):
    target_template = [val.strip() for val in obj["template_equ"].split()]

    labels, have_both_m, gap, contain_constant, got_duplicate = get_labels(obj["norm_post_equ"].split(), obj["template_equ"].split(), remove_duplicate)
    type_str = "legal"

    # if count_variable(target_template) > 7: ## only 2 in test
    #     type_str = "variable more than 7"
    #     return type_str, labels, gap


    # if have_constant(target_template):
    #     type_str = "have constant"
    #     return type_str, labels
    #
    # if have_pi(target_template):
    #     type_str = "have pi"
    #     print(obj["equation"], obj["target_template"])
    #     return type_str, labels

    if have_square(target_template): ## only 1 in test
        type_str = "have square"
        return type_str, labels, gap, None, False

    # if have_both_m:
    #     type_str = "have both m0, m1"
    #     return type_str, labels, gap


    # have_same_variable = []
    # for idx, curr_labels in enumerate(labels):
    #     if curr_labels[0] == curr_labels[1]:
    #         have_same_variable.append(idx)
    # if len(have_same_variable) > 0:
    #     if len(have_same_variable) == 1 and have_same_variable[0] == 0:
    #         return "legal", labels, gap
    #     else:
    #         return "have same variable at multiple layer", labels, gap

    # if have_multiple_m0(target_template):
    #     type_str = "have mutiple m0"
    #     return type_str, labels, gap





    return type_str, labels, gap, contain_constant, got_duplicate

def main():
    remove_duplicate = True
    for in_file in ["mawps_train.json", "mawps_valid.json", "mawps_test.json"]:
        print(f"working on... {in_file}")
        in_file = f"../data/mawps-single/{in_file}"
        if remove_duplicate:
            out_file = in_file.split(".json")[0] + "_nodup.json"
        else:
            out_file = in_file.split(".json")[0] + "_all.json"
        data = read_data(in_file)
        count = Counter()
        inst_num_with_gap = 0
        num_cannot_compute_labels = 0
        num_inst_have_constants = 0
        duplicate_num = 0
        for obj in tqdm(data, desc="processing data", total=len(data)):
            type_str, labels, gap, contain_constant, got_duplicate = process_obj(obj, remove_duplicate=remove_duplicate)
            if len(labels) == 0:
                print(obj)
                num_cannot_compute_labels+=1
            obj["have_constant"] = contain_constant
            if contain_constant:
                # print(obj)
                num_inst_have_constants+=1
                # assert len(obj["norm_post_equ"]) == 3
                # print("something", obj["num_list"], obj["norm_mid_equ"])
            if gap > 0:
                inst_num_with_gap += 1
            duplicate_num += int(got_duplicate)
            count[type_str] += 1
            obj["type_str"] = type_str
            obj["equation_layer"] = labels
            obj["answer"] = obj["lSolutions"][0]
            obj.pop("lSolutions")
            obj["text"] = obj["mask_text"]
            obj.pop("mask_text")
            # if type_str == "legal":
            #     check_intermediate_m_in_order(labels)
        # write_data(file=out_file, data = data)

        print(inst_num_with_gap)
        print(f"number of duplication: {duplicate_num}")
        for key in count:
            print(f"{key}, valid number: {count[key]}, total: {len(data)}, %: {count[key] * 1.0 / len(data) * 100:.2f}")
        print(f"number cannot compute: {num_cannot_compute_labels}, num insts have constant: {num_inst_have_constants}")
        print(const_list)
        const_list.clear()
        print(sorted(const2num.items(), key=lambda kv: (kv[1], kv[0]), reverse=True))
        const2num.clear()

def get_five_fold(train_file, dev_file, test_file, output_folder):
    import random
    random.seed(42)
    train_data = read_data(train_file)
    dev_data = read_data(dev_file)
    test_data = read_data(test_file)
    all_data = train_data + dev_data + test_data
    random.shuffle(all_data)
    num_fold = 5
    fold_size = len(all_data) // num_fold
    os.makedirs(f"../data/{output_folder}", exist_ok=True)
    for i in range(num_fold):
        if i == num_fold - 1:
            test_data = all_data[i * fold_size:]
            train_data = all_data[:i * fold_size]
        else:
            test_data = all_data[i * fold_size:(i + 1) * fold_size]
            train_data = all_data[:i * fold_size] + all_data[(i + 1) * fold_size:]
        size = len(train_data) + len(test_data)
        print(f"total size : {size}, train: {len(train_data)}, test: {len(test_data)}")
        write_data(file=f"../data/{output_folder}/train_{i}.json", data=train_data)
        write_data(file=f"../data/{output_folder}/test_{i}.json", data=test_data)



if __name__ == '__main__':
    const_list = set()
    const2num = Counter()
    # text = "a () * c"
    # print(re.sub(r"\(.*\)", "temp_m", text))
    main()
    # print(const_list)

    # get_five_fold(train_file="../data/mawps-single/mawps_train_nodup.json",
    #               dev_file="../data/mawps-single/mawps_valid_nodup.json",
    #               test_file="../data/mawps-single/mawps_test_nodup.json",
    #               output_folder="mawps-single-five-fold")

    # print(breakit('(((a+b)+a)+c)'))