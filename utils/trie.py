class TrieNode:
    def __init__(self, parent=None, char=None):
        self.children = {}
        self.end_of_word = False
        self.parent = parent
        self.char = char

    def get_char_in_context(self):
        if self.parent is None:
            return self.char
        else:
            return self.char if self.char is not None else '' + self.parent.get_char_in_context() if self.parent.get_char_in_context() is not None else ''


class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode(parent=node, char=char)
            node = node.children[char]
        node.end_of_word = True

    def find_multi_child_nodes(self, node=None):
        if node is None:
            node = self.root
        multi_child_nodes = []
        for child_node in node.children.values():
            if len(child_node.children) > 1:
                multi_child_nodes.append(child_node)
            multi_child_nodes += self.find_multi_child_nodes(child_node)
        return multi_child_nodes