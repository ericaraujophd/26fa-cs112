# makefile, CS112 operator overloading cheatsheet
# Calvin University · Fall 2026
#
# Usage:
#   make        : build ./tester (one TEST_CASE per section of the page)
#   make test   : build and run it
#   make clean  : delete everything that was compiled

CXX      = g++
CXXFLAGS = -Wall -std=c++17 -g

SOURCES = Fraction.cpp Bag.cpp
CHECKS  = tests.cpp

CLASS_OBJ = $(SOURCES:.cpp=.o)
CHECK_OBJ = $(CHECKS:.cpp=.o)

all: tester

tester: catchmain.o $(CHECK_OBJ) $(CLASS_OBJ)
	$(CXX) $(CXXFLAGS) -o tester catchmain.o $(CHECK_OBJ) $(CLASS_OBJ)

%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c $<

Fraction.o:  Fraction.cpp Fraction.h
Bag.o:       Bag.cpp Bag.h
tests.o:     tests.cpp Fraction.h Bag.h catch.hpp
catchmain.o: catchmain.cpp catch.hpp

test: tester
	./tester

clean:
	rm -f *.o tester

.PHONY: all test clean
