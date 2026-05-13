# makefile — CS112 Pre-Lab 00: The CS112 Oracle
# Calvin University
#
# Usage:
#   make          — compile everything and produce the 'lab00' executable
#   make clean    — delete all compiled files (object files and executable)
#
# How it works:
#   1. Each .cpp file is compiled separately into an object file (.o)
#   2. The object files are linked together into the final executable
#
# Variables:
#   CXX      — the C++ compiler to use
#   CXXFLAGS — compiler options:
#              -Wall    : turn on all warnings (your friend, not your enemy)
#              -std=c++17 : use the C++17 standard

CXX      = g++
CXXFLAGS = -Wall -std=c++17

# ---------------------------------------------------------
# Rule: build the final executable 'lab00'
#
# Depends on: main.o and fortune.o (both must be up to date)
# Command: link the two object files into one executable
# ---------------------------------------------------------
lab00: main.o fortune.o
	$(CXX) $(CXXFLAGS) -o lab00 main.o fortune.o

# ---------------------------------------------------------
# Rule: compile main.cpp into main.o
#
# Depends on: main.cpp and fortune.h
# The -c flag means "compile only, do not link"
# ---------------------------------------------------------
main.o: main.cpp fortune.h
	$(CXX) $(CXXFLAGS) -c main.cpp

# ---------------------------------------------------------
# Rule: compile fortune.cpp into fortune.o
#
# Depends on: fortune.cpp and fortune.h
# ---------------------------------------------------------
fortune.o: fortune.cpp fortune.h
	$(CXX) $(CXXFLAGS) -c fortune.cpp

# ---------------------------------------------------------
# Rule: clean up all compiled output
#
# 'make clean' removes object files and the executable so
# you can do a completely fresh build.
# ---------------------------------------------------------
clean:
	rm -f *.o lab00
