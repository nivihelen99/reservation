#ifndef BTREE_NODE_H
#define BTREE_NODE_H

#include <vector>
#include <algorithm> // For std::find, std::distance, std::copy, std::move
#include <iostream>  // For BTreeNode::traverse

// Forward declaration for BTree to use as a friend class
template <typename T>
class BTree;

/**
 * @file btree_node.h
 * @brief Contains the definition of the BTreeNode class, representing a node in a B-Tree.
 */

/**
 * @brief Represents a node in a B-Tree.
 *
 * Each node maintains a list of keys, a list of child pointers (if not a leaf),
 * its current number of keys, its minimum degree `t`, and a flag indicating if it's a leaf.
 *
 * @tparam T The type of keys stored in the B-Tree. Keys must be comparable (support <, >, ==).
 */
template <typename T>
class BTreeNode {
public:
    // Match initialization order in constructor for BTreeNode(int, bool)
    int t;          ///< Minimum degree of the B-Tree. Defines the range for number of keys: t-1 to 2t-1.
    bool is_leaf;   ///< True if this node is a leaf, false otherwise.
    int n;          ///< Current number of keys stored in the node.
    std::vector<T> keys; ///< Stores the keys in the node. Max keys: 2t-1.
    std::vector<BTreeNode<T>*> children; ///< Pointers to child nodes. Max children: 2t.

    /**
     * @brief Constructor for BTreeNode.
     * @param _t Minimum degree of the B-Tree.
     * @param _is_leaf True if the node is a leaf, false otherwise.
     */
    BTreeNode(int _t, bool _is_leaf);

    /**
     * @brief Destructor for BTreeNode.
     * Recursively deletes all child nodes if this is an internal node.
     */
    ~BTreeNode();

    /**
     * @brief Inserts a new key into the subtree rooted with this node.
     * This function assumes that the node is NOT full when it is called.
     * @param k The key to be inserted.
     */
    void insert_non_full(T k);

    /**
     * @brief Splits the child `y` of this node.
     * `y` must be a full child of this node and must be at index `i` in the `children` array.
     * After the split, the middle key of `y` moves up to this node, and `y` is split into two nodes.
     * @param i The index of child `y` in the `children` array of this node.
     * @param y Pointer to the child node to be split (children[i]).
     */
    void split_child(int i, BTreeNode<T>* y);

    /**
     * @brief Traverses all nodes in the subtree rooted with this node (in-order).
     * This is primarily used for debugging and displaying the tree's contents.
     */
    void traverse() const;

    /**
     * @brief Searches for a key `k` in the subtree rooted with this node.
     * @param k The key to search for.
     * @return BTreeNode<T>* A pointer to this node if `k` is found in this node's keys.
     *         If `k` is not in this node's keys, it recursively calls search on the appropriate child.
     *         Returns `nullptr` if `k` is not found in the subtree and this is a leaf node.
     */
    BTreeNode<T>* search(T k);

    // Grant BTree class access to private/protected members of BTreeNode
    friend class BTree<T>;

private:
    // Note on memory management:
    // The current implementation uses raw pointers for children and std::vector for keys.
    // For non-primitive types or very performance-sensitive applications,
    // consider std::unique_ptr for children or custom memory allocators.
    // The destructor handles recursive deletion of child nodes.
};


// --- Template Method Implementations for BTreeNode ---
// These are defined here (or could be in btree.h or a .tpp file included here)
// because they are templated and need to be available where BTreeNode is used.

template <typename T>
BTreeNode<T>::BTreeNode(int _t, bool _is_leaf) : t(_t), is_leaf(_is_leaf), n(0) {
    keys.resize(2 * t - 1);
    if (!is_leaf) { // Only allocate for children if it's not a leaf initially.
                    // Max children is 2*t.
        children.resize(2 * t, nullptr); // Initialize with nullptr
    }
    // For leaves, children vector can remain empty or sized 0, as it won't be used.
    // However, to be safe and consistent with split_child logic which might temporarily
    // assign children to a node that becomes non-leaf, it's safer to always allocate it.
    // Let's stick to the original:
    children.resize(2 * t, nullptr);
}

template <typename T>
BTreeNode<T>::~BTreeNode() {
    if (!is_leaf) {
        for (int i = 0; i <= n; ++i) { // Iterate through all potential child pointers
            if (children[i] != nullptr) {
                delete children[i];
                children[i] = nullptr;
            }
        }
    }
}


template <typename T>
void BTreeNode<T>::traverse() const {
    int i;
    for (i = 0; i < n; i++) {
        if (!is_leaf) {
            if(children[i]) children[i]->traverse();
        }
        std::cout << " " << keys[i];
    }
    if (!is_leaf) {
         if(children[i]) children[i]->traverse(); // Traverse the subtree rooted with the last child
    }
}


template <typename T>
BTreeNode<T>* BTreeNode<T>::search(T k) {
    int i = 0;
    while (i < n && k > keys[i]) {
        i++;
    }

    if (i < n && keys[i] == k) {
        return this;
    }

    if (is_leaf) {
        return nullptr;
    }
    // Ensure child pointer is valid before dereferencing
    if (children[i] == nullptr && i <=n ) {
        // This case should ideally not happen in a correctly formed B-Tree if searching for a key
        // that should exist or if the tree structure is maintained.
        // However, if it implies key is not in a path that exists, it means key not found.
        return nullptr;
    }
    return children[i]->search(k);
}

// Implementations for insert_non_full and split_child are in btree.h
// as they are often called by BTree methods and might be more tightly coupled
// with the BTree class logic, or to avoid circular dependency issues if BTree methods
// also needed to call them.

#endif // BTREE_NODE_H
