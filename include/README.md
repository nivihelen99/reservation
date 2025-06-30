# C++ B-Tree Implementation

This directory contains a C++ implementation of a B-Tree data structure.

## Files

-   `btree_node.h`: Defines the `BTreeNode` class, which represents a single node within the B-Tree. It includes storage for keys, child pointers, the node's minimum degree `t`, current key count `n`, and a flag `is_leaf`. Template method declarations are present here.
-   `btree.h`: Defines the `BTree` class, which manages the overall B-Tree structure (like the root pointer and minimum degree `t`). It provides the main public interface for operations like `insert`, `search`, and `traverse`. This file also contains the template method implementations for both `BTree` and `BTreeNode` classes.

## B-Tree Properties

A B-Tree is a self-balancing tree data structure that maintains sorted data and allows searches, sequential access, insertions, and deletions in logarithmic time. This implementation focuses on insertion and search.

Key properties based on the minimum degree `t` (where `t >= 2`):
1.  Every node except the root must have at least `t-1` keys. The root may have between 1 and `2t-1` keys (unless it's a leaf, then 0 keys is possible for an empty tree).
2.  Every node can contain a maximum of `2t-1` keys.
3.  Every internal node (non-leaf node) except the root must have at least `t` children.
4.  Every internal node can have a maximum of `2t` children.
5.  All leaves appear on the same level.

This implementation allows duplicate keys.

## Core Operations Implemented

-   **`BTree(int t)`**: Constructor to create a B-Tree with a minimum degree `t`.
-   **`void insert(T key)`**: Inserts a key into the B-Tree. Handles node splitting, including root splits, to maintain B-Tree properties.
-   **`bool search(T key)`**: Searches for a key in the B-Tree. Returns `true` if found, `false` otherwise.
-   **`void traverse()`**: Performs an in-order traversal of the B-Tree and prints the keys. Useful for debugging and verifying tree contents.

Deletion is a standard B-Tree operation but is not implemented in this version due to its increased complexity.

## How to Use

1.  Include `btree.h` in your C++ source file:
    ```cpp
    #include "path/to/include/btree.h"
    ```
2.  Create a B-Tree object, specifying the minimum degree `t`. The type `T` of the keys must support comparison operators (`<`, `>`, `==`).
    ```cpp
    BTree<int> myBTree(3); // Creates a B-Tree for integers with minimum degree 3
    ```
3.  Use the public methods:
    ```cpp
    myBTree.insert(10);
    myBTree.insert(20);
    myBTree.insert(5);

    if (myBTree.search(10)) {
        // Key 10 found
    }

    myBTree.traverse(); // Prints keys in sorted order
    ```

## Compilation

The B-Tree is implemented using C++ templates. Ensure your compiler supports C++11 or later for features like `nullptr` and `std::vector` initializations used.

Example compilation for a test file (e.g., `main.cpp` that uses `btree.h`):
```bash
g++ -std=c++11 -I./include main.cpp -o my_program
```
(Adjust `-I./include` if `btree.h` is in a different relative path).

The provided `tests/test_btree.cpp` serves as a more comprehensive example and can be compiled similarly:
```bash
g++ -std=c++11 -I./include tests/test_btree.cpp -o bin/test_btree
./bin/test_btree
```

## Further Development

-   Implement the `remove(T key)` operation.
-   Add iterators for more convenient traversal and access.
-   Support for custom comparators.
-   More rigorous testing, especially for complex scenarios and larger datasets.
-   Performance benchmarking.
-   Consider `std::unique_ptr` for child node management to simplify memory handling and prevent leaks if exceptions occur during construction/manipulation.
```
