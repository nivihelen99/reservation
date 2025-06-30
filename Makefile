# Simple Makefile for B-Tree tests

# Compiler and flags
CXX = g++
CXXFLAGS = -std=c++11 -Wall -Wextra -g # -Wall and -Wextra for more warnings, -g for debug symbols
INCLUDES = -I./include

# Directories
SRC_DIR = tests
OBJ_DIR = bin
BIN_DIR = bin

# Source files and executable name
TEST_SOURCES = $(SRC_DIR)/test_btree.cpp
TEST_EXECUTABLE = $(BIN_DIR)/test_btree

# Default target
all: $(TEST_EXECUTABLE)

# Rule to link the test executable
$(TEST_EXECUTABLE): $(OBJ_DIR)/test_btree.o
	@mkdir -p $(@D) # Ensure bin directory exists
	$(CXX) $(CXXFLAGS) $^ -o $@

# Rule to compile test_btree.cpp into an object file
$(OBJ_DIR)/test_btree.o: $(TEST_SOURCES) $(wildcard $(INCLUDES_DIR)/*.h) $(wildcard ./include/*.h)
	@mkdir -p $(@D) # Ensure bin directory exists (for .o files)
	$(CXX) $(CXXFLAGS) $(INCLUDES) -c $< -o $@

# Target to run tests
run_tests: $(TEST_EXECUTABLE)
	./$(TEST_EXECUTABLE)

# Clean target
clean:
	rm -rf $(OBJ_DIR)/*
	rm -f $(TEST_EXECUTABLE)

# Phony targets
.PHONY: all clean run_tests
