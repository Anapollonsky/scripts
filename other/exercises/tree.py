
from copy import deepcopy
from collections import deque

class tree(object):
    """ Simple tree implementation, where a tree is a list of lists (of lists), leaves are
    lists with a single entry, and any subsequent entries represent children."""
    def __init__(self, rootval, children=[]):
        if isinstance(rootval, list):
            self.value = rootval[0]
            self.children = []
            for k in rootval[1:]:
                if k:
                    self.add_child(tree(k))
        else:
            self.value = rootval
            self.children = children

    def __repr__(self):
        return str(self.to_list())

    def get_val(self):
        return self.value

    def add_child(self, node):
        self.children.append(node)

    def get_child(self, num):
        return self.children[num]

    def get_children(self):
        return self.children

    def get_depths(self, start_depth=0):
        data = [start_depth]
        for child in self.get_children():
            for child_datum in child.get_depths(start_depth + 1):
                data.append(child_datum)
        return data

    def to_list(self):
        temp = list(self.children)
        temp.insert(0, self.value)
        return temp


class binary_tree(tree):

    def __init__(self, rootval, children=[]):
        if isinstance(rootval, list):
            self.value = rootval[0]
            self.children = [binary_tree(x) if x else x for x in rootval[1:]
            ] + [None for x in range(2-len(rootval[1:]))]
        else:
            self.value = rootval
            self.children = children + [None for x in range(2-len(children))]


    def get_left(self):
        return self.children[0]

    def get_right(self):
        return self.children[1]

    def set_left(self, node):
        self.children[0] = node

    def set_right(self, node):
        self.children[1] = node

    def get_tree_height(self):
        left_height = self.left().get_tree_height() if self.left() else 0
        right_height = self.right().get_tree_height() if self.right() else 0
        return 1 + max(left_height, right_height)

    ## 9.1: Check if balanced
    def is_balanced(self):
        """ Return height of tree, or None if not balanced"""
        left_height = self.get_left().is_balanced() if self.get_left() else 0
        right_height = self.get_right().is_balanced() if self.get_right() else 0
        if left_height == None or right_height == None or abs(right_height -
                                                      left_height) > 1:
            return None
        else:
            return 1 + max(left_height, right_height)

    ## 9.2: k-balanced nodes
    # def kbalanced(self)

    ## 9.3 symmetric tree
    def is_symmetric(self):
        """Return true if symmetric tree, else false"""
        def symmetric_helper(left_node, right_node):
            if bool(left_node) != bool(right_node): # If one exists and other doesn't, False
                return False
            if not (left_node or right_node): # If neither exists, True
                return True
            if not left_node.get_val() == right_node.get_val(): # If both exist but have different values, False
                return False
            # Otherwise, both exist, have same values, compare children...
            return (symmetric_helper(left_node.get_left(), right_node.get_right())
                    and symmetric_helper(left_node.get_right(), right_node.get_left()))
        return symmetric_helper(self.get_left(), self.get_right())

    ## 9.7 reconstruct from inorder and preorder or postorder
    def reconstruct_inorder_preorder(inorder, preorder):
        """Reconstruct tree from inorder and preorder lists"""
        if len(inorder) == 0:
            return None
        rootindex = inorder.index(preorder[0])
        root = binary_tree(preorder[0],
                           [binary_tree.reconstruct_inorder_preorder(inorder[:rootindex], preorder[1:1+rootindex]),
                            binary_tree.reconstruct_inorder_preorder(inorder[rootindex+1:], preorder[rootindex+1:])])
        return root

    ## 9.8 reconstruct tree from preorder transversal with null for empty nodes
    def null_reconstruct_preorder(preorder):
        if len(preorder) == 1:
            return None
        tcount, ncount = 0, 0
        left = []
        for i, k in enumerate(preorder[1:]):
            if not k == None:
                tcount += 1
            else:
                ncount += 1
            left.append(k)
            if ncount == tcount * 2 - (tcount - 1):
                right = preorder[i+2:]
                break
        root = binary_tree(preorder[0])
        if root:
            root.set_left(binary_tree.null_reconstruct_preorder(left))
            root.set_right(binary_tree.null_reconstruct_preorder(right))
        return root

    ## 9.9 Form linked list from leaf nodes of tree
    def linked_list_from_leaves(node):
        linked_list = []
        if node.get_left():
            linked_list += binary_tree.linked_list_from_leaves(node.get_left())
        if node.get_right():
            linked_list += binary_tree.linked_list_from_leaves(node.get_right())
        if not (node.get_left() or node.get_right()):
            linked_list.append(node.get_val())
        return linked_list

    # ## 9.10 Print exterior of binary tree in anti-clockwise: nodes on
    # ## path to leftmost leaf, then leaves left-right, then nodes of rightmost
    # ## to root

    # # Assuming that going left/right until first leaf matches definition; unclear
    # def binary_tree_exterior(node):
    #     def print_left_anticlockwise(node):
    #         the_list = [node.get_val()]
    #         if node.get_left():
    #             the_list += print_left_anticlockwise(node.get_left)
    #         elif node.get_right():
    #             the_list += print_left_anticlockwise(node.get_right)
    #         return the_list

    #     def print_left_anticlockwise(node):
    #         the_list = [node.get_val()]
    #         if node.get_left():
    #             the_list += print_left_anticlockwise(node.get_left)
    #         elif node.get_right():
    #             the_list += print_left_anticlockwise(node.get_right)
    #         return the_list

    ## 9.11 Lowest common ancestor
    # Assumes values are unique
    def lowest_common_ancestor(root, vals):

        # Breadth-first search
        def lca_helper(root, queue):
            if root.get_left():
                queue.append(root.get_left())
                ancestry[root.get_left().get_val()] = root
            if root.get_right():
                queue.append(root.get_right())
                ancestry[root.get_right().get_val()] = root

        # Keep track of history for path recreation
        queue = deque()
        ancestry = {root.get_val(): None}
        lca_helper(root, queue)
        while queue and not all([x in ancestry for x in vals]):
            # print(visited_queue, vals)
            curnode = queue.popleft()
            lca_helper(curnode, queue)

        # Generate paths out of node path history
        paths = {}
        for k in vals:
            paths[k] = []
            ancestry_pather = k
            while ancestry_pather:
                paths[k].append(ancestry_pather)
                if ancestry[ancestry_pather]:
                    ancestry_pather = ancestry[ancestry_pather].get_val()
                else:
                    ancestry_pather = None
        # Go through paths, looking for earliest common member
        for path in paths:
            for path_member in paths[path]:
                if all([path_member in paths[x] for x in paths]):
                    return path_member
        # Doesn't exist
        return None

testtree = binary_tree([3, [1, [2, [3, [4]]]], [3, [2], [3]]])
balanced_tree = binary_tree([3, [2, [1], [3]], [2, [3], [3]]])
symmetric_tree = binary_tree([3, [2, [3], [2]], [2, [2], [3]]])
# print(testtree.get_depths())
# print(testtree.is_balanced())
# print(balanced_tree.is_balanced())
# print(testtree.is_symmetric())
# print(symmetric_tree.is_symmetric())

chartree = binary_tree(['H', ['B', ['F', None, None], ['E', ['A', None, None], None]], ['C', None, ['D', None, ['G', ['I', None, None], None]]]])
chartree_inorder = ['F', 'B', 'A', 'E', 'H', 'C', 'D', 'I', 'G']
chartree_preorder = ['H', 'B', 'F', 'E', 'A', 'C', 'D', 'G', 'I']
# nc = binary_tree.reconstruct_inorder_preorder(chartree_inorder, chartree_preorder)
# print(chartree.to_list())
# print(nc)

# chartree_preorder_marked = ['H', 'B', 'F', None, None, 'E', 'A',
#                             None, None, None, 'C', None, 'D',
#                             None, 'G', 'I', None, None, None]
# print(chartree)
# print(binary_tree.null_reconstruct_preorder(chartree_preorder_marked))

# print (binary_tree.linked_list_from_leaves(chartree))
print(binary_tree.lowest_common_ancestor(chartree, ['B', 'D']))
print(binary_tree.lowest_common_ancestor(chartree, ['I', 'D', 'G']))
