import sys
import ast
import gc


def levenshtein(a, b):
    dp = [0] * (len(a) + 1)
    for i in range(len(a) + 1):
        dp[i] = i
    for i in range(1, len(b) + 1):
        cur_dp = [0] * (len(a) + 1)
        cur_dp[0] = i
        for j in range(1, len(a) + 1):
            if b[i - 1] == a[j - 1]:
                cur_dp[j] = dp[j - 1]
            else:
                cur_dp[j] = dp[j - 1] + 1
            cur_dp[j] = min(cur_dp[j], dp[j] + 1, cur_dp[j - 1] + 1)
        del dp
        gc.collect()
        dp = cur_dp
        if i % 50 == 0:
            print(i)
    tmp = dp[len(a)]
    del dp
    gc.collect()
    return tmp


def files_handler(file_name):
    with open(file_name, "r", encoding='utf-8') as f:
        res_str = ""
        for line in f.readlines():
            res_str += line + '\n'
    return res_str


def del_docs(tree, tree_str):
    for node in ast.walk(tree):
        try:
            to_del = ast.get_docstring(node, clean=True)
            if to_del is not None:
                to_del = str(to_del)
                to_del = to_del.expandtabs(0)
                to_del = to_del.replace(" ", "")
                to_del = to_del.replace('\n', "")
                tree_str = tree_str.replace(to_del, "")
            del to_del
        except TypeError:
            pass
    gc.collect()
    return tree_str


with open(str(sys.argv[1]), "r") as inline, open(str(sys.argv[2]), "w") as outline:
    for line in inline.readlines():
        line = line.split()
        first_file, second_file = line[0], line[1]
        try:
            tree_one, tree_two = ast.parse(files_handler(first_file)), \
                                 ast.parse(files_handler(second_file))
        except Exception:
            outline.write("Один из файлов не является корректным файлом Python" + '\n')
        else:
            first_tree, second_tree = str(ast.dump(tree_one)), \
                                      str(ast.dump(tree_two))
            first_tree = first_tree.expandtabs(0)
            first_tree = first_tree.replace(" ", "")
            first_tree = first_tree.replace("\\n", "")
            second_tree = second_tree.expandtabs(0)
            second_tree = second_tree.replace(" ", "")
            second_tree = second_tree.replace("\\n", "")
            first_tree = del_docs(tree_one, first_tree)
            second_tree = del_docs(tree_two, second_tree)
            first_tree = first_tree.lower()
            second_tree = second_tree.lower()
            difference = levenshtein(first_tree, second_tree)
            max_len = max(len(first_tree), len(second_tree))
            del first_tree, second_file
            gc.collect()
            outline.write(str(round((max_len - difference) / max_len, 3)) + '\n')
