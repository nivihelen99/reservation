#include "../include/btree.h" // Adjust path as necessary
#include <iostream>
#include <vector>
#include <algorithm> // For std::is_sorted
#include <set>       // For checking uniqueness and content

// Basic assertion function for testing
void assert_true(bool condition, const std::string& message) {
    if (!condition) {
        std::cerr << "Assertion Failed: " << message << std::endl;
    } else {
        std::cout << "Assertion Passed: " << message << std::endl;
    }
}

// Helper function to collect all keys from the tree via traversal
// This is a bit of a hack for testing; proper B-tree iteration would be better.
template <typename T>
void collect_keys_recursive(BTreeNode<T>* node, std::vector<T>& keys_collected) {
    if (node == nullptr) {
        return;
    }
    int i;
    for (i = 0; i < node->n; i++) {
        if (!node->is_leaf) {
            collect_keys_recursive(node->children[i], keys_collected);
        }
        keys_collected.push_back(node->keys[i]);
    }
    if (!node->is_leaf) {
        collect_keys_recursive(node->children[i], keys_collected);
    }
}

template <typename T>
std::vector<T> get_all_keys(BTree<T>& tree) {
    std::vector<T> keys_collected;
    if (tree.root != nullptr) {
        collect_keys_recursive(tree.root, keys_collected);
    }
    return keys_collected;
}

int main() {
    // Test 1: Basic insertion and search (degree t=3)
    std::cout << "--- Test 1: Basic Insertion and Search (t=3) ---" << std::endl;
    BTree<int> t(3); // A B-Tree with minimum degree 3
    t.insert(10);
    t.insert(20);
    t.insert(5);
    t.insert(6);
    t.insert(12);
    t.insert(30);
    t.insert(7);
    t.insert(17);

    std::cout << "Traversal of the constructed tree: ";
    t.traverse(); // Expected: 5 6 7 10 12 17 20 30

    assert_true(t.search(10), "Search for 10");
    assert_true(t.search(20), "Search for 20");
    assert_true(t.search(5), "Search for 5");
    assert_true(t.search(6), "Search for 6");
    assert_true(t.search(12), "Search for 12");
    assert_true(t.search(30), "Search for 30");
    assert_true(t.search(7), "Search for 7");
    assert_true(t.search(17), "Search for 17");
    assert_true(!t.search(15), "Search for 15 (non-existent)");
    assert_true(!t.search(100), "Search for 100 (non-existent)");
    assert_true(!t.search(1), "Search for 1 (non-existent)");

    std::vector<int> expected_keys1 = {5, 6, 7, 10, 12, 17, 20, 30};
    std::vector<int> actual_keys1 = get_all_keys(t);
    assert_true(actual_keys1 == expected_keys1, "Verify all keys and their order after Test 1");

    // Test 2: Insertion causing root split (degree t=2)
    // With t=2, a node can have max 2*2-1 = 3 keys.
    // A node splits when it has 3 keys and one more is inserted.
    std::cout << "\n--- Test 2: Root Split (t=2) ---" << std::endl;
    BTree<int> t2(2);
    t2.insert(1);
    t2.insert(2);
    t2.insert(3); // Root is now full: [1, 2, 3]
    std::cout << "Traversal before root split: ";
    t2.traverse(); // Expected: 1 2 3

    t2.insert(4); // This should cause a root split.
                  // Root becomes [2], left child [1], right child [3, 4]
                  // Or root becomes [3], left child [1,2], right child [4]
                  // Or root becomes [x]... let's trace:
                  // 1. Insert 1: root=[1], n=1
                  // 2. Insert 2: root=[1,2], n=2
                  // 3. Insert 3: root=[1,2,3], n=3 (full for t=2)
                  // 4. Insert 4: root is full.
                  //    New root 's' created. Old root becomes child of 's'.
                  //    s->children[0] = old_root ([1,2,3])
                  //    s->split_child(0, old_root)
                  //        y = old_root ([1,2,3]), t=2
                  //        z = new BTreeNode(2, true), z->n = t-1 = 1
                  //        z->keys[0] = y->keys[t] = y->keys[2] = 3
                  //        y->n = t-1 = 1 (y now contains [1])
                  //        s->children[1] = z
                  //        s->keys[0] = y->keys[t-1] = y->keys[1] = 2
                  //        s->n = 1.  Root 's' is now [2]
                  //        Left child (old_root 'y') is [1]
                  //        Right child ('z') is [3]
                  //    New root 's' is [2]. children are [1] and [3]
                  //    Now decide where 4 goes. s->keys[0]=2 < 4, so i=1.
                  //    s->children[1]->insert_non_full(4). Child is [3].
                  //        Node [3], i=0 (keys[0]=3 < 4). keys[1]=4. n=2. Node is [3,4]
                  // Final structure: Root: [2], Left child: [1], Right child: [3, 4]
    std::cout << "Traversal after root split (inserting 4): ";
    t2.traverse(); // Expected: 1 2 3 4

    assert_true(t2.search(1), "Search for 1 (t2)");
    assert_true(t2.search(2), "Search for 2 (t2)");
    assert_true(t2.search(3), "Search for 3 (t2)");
    assert_true(t2.search(4), "Search for 4 (t2)");
    assert_true(!t2.search(5), "Search for 5 (non-existent in t2)");

    std::vector<int> expected_keys2 = {1, 2, 3, 4};
    std::vector<int> actual_keys2 = get_all_keys(t2);
    assert_true(actual_keys2 == expected_keys2, "Verify all keys and their order after Test 2");


    // Test 3: More insertions, causing internal node splits (degree t=2)
    std::cout << "\n--- Test 3: Internal Splits (t=2) ---" << std::endl;
    BTree<int> t3(2);
    int keys_to_insert[] = {10, 20, 5, 30, 15, 25, 3, 7, 12, 18, 22, 28, 1, 35, 40};
    std::set<int> inserted_set; // To verify against
    for (int key : keys_to_insert) {
        t3.insert(key);
        inserted_set.insert(key);
        std::cout << "Inserted " << key << ". Traversal: ";
        t3.traverse();
    }

    std::cout << "Final traversal of t3: ";
    t3.traverse();

    std::vector<int> actual_keys3 = get_all_keys(t3);
    std::vector<int> expected_keys3(inserted_set.begin(), inserted_set.end());
    assert_true(actual_keys3 == expected_keys3, "Verify all keys and their order after Test 3");

    for (int key : inserted_set) {
        assert_true(t3.search(key), "Search for existing key " + std::to_string(key) + " (t3)");
    }
    assert_true(!t3.search(0), "Search for 0 (non-existent in t3)");
    assert_true(!t3.search(50), "Search for 50 (non-existent in t3)");


    // Test 4: Empty tree
    std::cout << "\n--- Test 4: Empty Tree (t=3) ---" << std::endl;
    BTree<int> t4(3);
    std::cout << "Traversal of empty tree: ";
    t4.traverse(); // Expected: (empty line)
    assert_true(!t4.search(10), "Search for 10 in empty tree");
    std::vector<int> actual_keys4 = get_all_keys(t4);
    assert_true(actual_keys4.empty(), "Verify empty tree has no keys");

    // Test 5: Single element tree
    std::cout << "\n--- Test 5: Single Element Tree (t=3) ---" << std::endl;
    BTree<int> t5(3);
    t5.insert(100);
    std::cout << "Traversal of single element tree: ";
    t5.traverse(); // Expected: 100
    assert_true(t5.search(100), "Search for 100 in single element tree");
    assert_true(!t5.search(10), "Search for 10 in single element tree (non-existent)");
    std::vector<int> expected_keys5 = {100};
    std::vector<int> actual_keys5 = get_all_keys(t5);
    assert_true(actual_keys5 == expected_keys5, "Verify single element tree keys");

    // Test 6: Inserting duplicate keys (B-Tree typically doesn't store duplicates,
    // current implementation will just not change the tree if key exists)
    // Let's verify search still works and tree remains valid.
    std::cout << "\n--- Test 6: Duplicate Key Insertion (t=3) ---" << std::endl;
    BTree<int> t6(3);
    t6.insert(10);
    t6.insert(20);
    t6.insert(10); // Insert duplicate
    std::cout << "Traversal after inserting 10, 20, 10: ";
    t6.traverse(); // Expected: 10 20 (or how search handles it - current search stops at first match)
                   // Our BTree search will find the existing 10, so it won't re-insert.
                   // The structure doesn't explicitly prevent insertion of duplicates if they were
                   // to be stored, but the search logic in insert_non_full would typically place
                   // a new key relative to existing ones. The current `search` only finds if one exists.
                   // The `insert` logic as is doesn't add duplicates if a key already exists
                   // because `BTreeNode::search` is not used by insert to check for existence first.
                   // Let's check the content.
    std::vector<int> expected_keys6 = {10, 20};
    std::vector<int> actual_keys6 = get_all_keys(t6);
     // The current implementation might create duplicates if not careful or allow them.
     // Let's re-verify insert_non_full: it places keys in sorted order. If k == keys[i],
     // it will still shift and insert. So duplicates ARE possible.
     // BTreeNode::search finds the first one.
     // Let's re-evaluate expected for duplicates.
     // If 10, 20, then 10 is inserted:
     // Leaf: [10, 20], insert 10. i starts at 1 (20). keys[1]=20 > 10. keys[2]=20. i=0. keys[0]=10.
     // keys[0] is not > 10. So loop stops. keys[i+1] = k -> keys[0+1] = 10.
     // So it becomes [10, 10, 20].
    t6.insert(5);
    std::cout << "Traversal after inserting 5: ";
    t6.traverse(); // Expected: 5 10 10 20

    std::vector<int> keys_for_t6 = {10, 20, 10, 5};
    std::sort(keys_for_t6.begin(), keys_for_t6.end()); // {5, 10, 10, 20}

    actual_keys6 = get_all_keys(t6);
    assert_true(actual_keys6 == keys_for_t6, "Verify keys with duplicates in Test 6");
    assert_true(t6.search(10), "Search for 10 (duplicate present) in t6");
    assert_true(t6.search(5), "Search for 5 in t6");
    assert_true(t6.search(20), "Search for 20 in t6");


    std::cout << "\nAll tests complete. Review output for any failures." << std::endl;

    return 0;
}

/*
To compile and run this test (assuming GCC/G++ and files in correct paths):
mkdir -p bin
g++ -std=c++11 -I../include tests/test_btree.cpp -o bin/test_btree
./bin/test_btree
*/
