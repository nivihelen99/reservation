#ifndef BTREE_H
#define BTREE_H

#include "btree_node.h" // Also brings in BTreeNode method implementations if they are there
#include <iostream>     // For BTree::traverse and BTreeNode::traverse

/**
 * @file btree.h
 * @brief Contains the definition of the BTree class and implementations of BTreeNode's core logic.
 */

/**
 * @brief Represents a B-Tree data structure.
 *
 * The B-Tree allows for efficient insertion, deletion (not implemented here), and search operations.
 * It is a self-balancing tree data structure that maintains sorted data and allows searches,
 * sequential access, insertions, and deletions in logarithmic time. B-Trees are optimized
 * for systems that read and write large blocks of data.
 *
 * @tparam T The type of keys stored in the B-Tree. Keys must be comparable.
 */
template <typename T>
class BTree {
public:
    BTreeNode<T>* root; ///< Pointer to the root node of the B-Tree.
    int t;              ///< Minimum degree of the B-Tree. Determines the node size.

    /**
     * @brief Constructor for BTree.
     * Initializes an empty B-Tree with a given minimum degree.
     * @param _t The minimum degree `t`. `t` must be >= 2.
     *           Each node (except root) must have at least `t-1` keys.
     *           Each node can have at most `2t-1` keys.
     *           Each internal node (except root) must have at least `t` children.
     *           Each internal node can have at most `2t` children.
     */
    BTree(int _t);

    /**
     * @brief Destructor for BTree.
     * Deletes the root node, which in turn recursively deletes all nodes in the tree.
     */
    ~BTree();

    /**
     * @brief Traverses the B-Tree and prints keys in ascending order.
     * This is primarily for debugging and inspecting the tree's contents.
     */
    void traverse() const;

    /**
     * @brief Searches for a key `k` in the B-Tree.
     * @param k The key to search for.
     * @return bool True if the key is found in the tree, false otherwise.
     */
    bool search(T k) const;

    /**
     * @brief Inserts a new key `k` into the B-Tree.
     * If the key already exists, this implementation will add it again (allows duplicates).
     * To prevent duplicates, a search should be performed before insertion,
     * or the insertion logic modified.
     * @param k The key to be inserted.
     */
    void insert(T k);

    // Note: Deletion is a common B-Tree operation but is not implemented here
    // due to its complexity.
};

// --- BTree Method Implementations ---

template <typename T>
BTree<T>::BTree(int _t) : root(nullptr), t(_t) {
    if (_t < 2) {
        // Throw an exception or handle error: minimum degree must be at least 2
        // For simplicity, we can assume t >= 2 from user.
        // Or, set a default or clamp:
        // if (this->t < 2) this->t = 2;
        // For now, let's rely on the user providing a valid t.
    }
}

template <typename T>
BTree<T>::~BTree() {
    delete root; // This will trigger BTreeNode's destructor, cascading deletions.
    root = nullptr;
}

template <typename T>
void BTree<T>::traverse() const {
    if (root != nullptr) {
        root->traverse();
    }
    std::cout << std::endl; // Add a newline after traversal for cleaner output
}

template <typename T>
bool BTree<T>::search(T k) const {
    return (root == nullptr) ? false : (root->search(k) != nullptr);
}

template <typename T>
void BTree<T>::insert(T k) {
    // If tree is empty
    if (root == nullptr) {
        root = new BTreeNode<T>(t, true);
        root->keys[0] = k;
        root->n = 1;
    } else { // If tree is not empty
        // If root is full, then tree grows in height
        if (root->n == 2 * t - 1) {
            BTreeNode<T>* s = new BTreeNode<T>(t, false); // New root will be internal node
            s->children[0] = root; // Old root becomes child of new root

            s->split_child(0, root); // Split the old root

            // New root has two children now. Decide which of the
            // two children is going to have the new key.
            int i = 0;
            if (s->keys[0] < k) {
                i++;
            }
            s->children[i]->insert_non_full(k);

            root = s; // Change root
        } else { // If root is not full, call insert_non_full for root
            root->insert_non_full(k);
        }
    }
}


// --- BTreeNode Method Implementations (continued from btree_node.h or placed here for compilation) ---
// These are methods of BTreeNode, but are often closely tied to BTree operations
// or are placed here to ensure template instantiations are found by the compiler.

/**
 * @brief Inserts a new key `k` into this node, which is assumed to be non-full.
 * If this is a leaf node, `k` is inserted directly into the `keys` array.
 * If this is an internal node, `k` is inserted into the appropriate child's subtree.
 * If a child to descend into is full, it is split first.
 * @param k The key to insert.
 */
template <typename T>
void BTreeNode<T>::insert_non_full(T k) {
    int i = n - 1; // Start from the rightmost key

    if (is_leaf) {
        // Find location for k and shift greater keys to the right
        while (i >= 0 && keys[i] > k) {
            keys[i + 1] = keys[i];
            i--;
        }
        keys[i + 1] = k; // Insert k
        n = n + 1;       // Increment count of keys
    } else { // This node is not a leaf
        // Find the child which is going to have the new key
        while (i >= 0 && keys[i] > k) {
            i--;
        }
        // i is now the index of the key just before the child to descend,
        // so child is children[i+1]

        // Check if the found child is full
        if (children[i + 1]->n == 2 * t - 1) {
            split_child(i + 1, children[i + 1]); // Split the child

            // After split, the middle key of children[i+1] goes up to this node (keys[i+1])
            // and children[i+1] is split into two.
            // Decide which of the two children will get the new key.
            if (keys[i + 1] < k) {
                i++; // The new key goes into the new right child created by the split
            }
        }
        children[i + 1]->insert_non_full(k);
    }
}

/**
 * @brief Splits the child `y` (which is `children[i]`) of this node.
 * `y` must be full when this function is called.
 * The middle key of `y` is moved to this node.
 * `y` is split into two nodes, and these two nodes become children of this node.
 * @param i Index of `y` in `children` array. `y` is `children[i]`.
 * @param y Pointer to the child node to be split (`children[i]`).
 */
template <typename T>
void BTreeNode<T>::split_child(int i, BTreeNode<T>* y) {
    // Create a new node z which will store (t-1) keys of y
    BTreeNode<T>* z = new BTreeNode<T>(y->t, y->is_leaf);
    z->n = t - 1;

    // Copy the last (t-1) keys of y to z
    for (int j = 0; j < t - 1; j++) {
        z->keys[j] = y->keys[j + t];
    }

    // Copy the last t children of y to z (if y is not a leaf)
    if (!y->is_leaf) {
        for (int j = 0; j < t; j++) {
            z->children[j] = y->children[j + t];
            y->children[j + t] = nullptr; // Null out moved children pointers in y
        }
    }

    // Reduce the number of keys in y
    y->n = t - 1;

    // Since this node is going to have a new child (z),
    // create space for the new child pointer in this node's children array.
    // Shift children to the right starting from children[i+1].
    for (int j = n; j >= i + 1; j--) {
        children[j + 1] = children[j];
    }

    // Link the new child z to this node
    children[i + 1] = z;

    // A key from y will move to this node.
    // Find location for this new key (y->keys[t-1]) and move all greater keys
    // in this node one space ahead.
    for (int j = n - 1; j >= i; j--) {
        keys[j + 1] = keys[j];
    }

    // Copy the middle key of y to this node
    keys[i] = y->keys[t - 1];
    // y->keys[t-1] can be optionally cleared/invalidated in y if T is complex.

    // Increment count of keys in this node
    n = n + 1;
}

#endif // BTREE_H
