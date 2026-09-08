from targets.binary_tree import BinarySearchTree, TreeNode


def test_tree_node_defaults():
    node = TreeNode(7)
    assert node.value == 7
    assert node.left is None
    assert node.right is None


def test_insert_root():
    bst = BinarySearchTree()
    bst.insert(10)
    assert bst.root is not None
    assert bst.root.value == 10


def test_insert_left_child():
    bst = BinarySearchTree()
    bst.insert(10)
    bst.insert(5)
    assert bst.root.left.value == 5


def test_insert_right_child():
    bst = BinarySearchTree()
    bst.insert(10)
    bst.insert(15)
    assert bst.root.right.value == 15


def test_insert_deep_left():
    bst = BinarySearchTree()
    bst.insert(10)
    bst.insert(5)
    bst.insert(3)
    assert bst.root.left.left.value == 3


def test_insert_deep_right():
    bst = BinarySearchTree()
    bst.insert(10)
    bst.insert(15)
    bst.insert(20)
    assert bst.root.right.right.value == 20


def test_inorder_empty():
    bst = BinarySearchTree()
    assert bst.inorder() == []


def test_inorder_single():
    bst = BinarySearchTree()
    bst.insert(5)
    assert bst.inorder() == [5]


def test_inorder_sorted():
    bst = BinarySearchTree()
    for v in [5, 3, 7, 1, 4]:
        bst.insert(v)
    assert bst.inorder() == [1, 3, 4, 5, 7]


def test_search_found_root():
    bst = BinarySearchTree()
    bst.insert(10)
    assert bst.search(10) is True


def test_search_found_left():
    bst = BinarySearchTree()
    bst.insert(10)
    bst.insert(5)
    assert bst.search(5) is True


def test_search_found_right():
    bst = BinarySearchTree()
    bst.insert(10)
    bst.insert(15)
    assert bst.search(15) is True


def test_search_not_found_empty():
    bst = BinarySearchTree()
    assert bst.search(42) is False


def test_search_not_found_nonempty():
    bst = BinarySearchTree()
    bst.insert(10)
    assert bst.search(99) is False
