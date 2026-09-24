/* Bag.cpp, CS112 operator overloading cheatsheet
 * Calvin University · Fall 2026
 */

#include "Bag.h"
#include <stdexcept>
using namespace std;

Bag::Bag(unsigned size) {
    mySize  = size;
    myItems = new int[size];
    for (unsigned i = 0; i < size; i++) {
        myItems[i] = 0;
    }
}

Bag::Bag(const Bag& original) {
    mySize  = original.mySize;
    myItems = new int[original.mySize];  // OUR array, not theirs
    for (unsigned i = 0; i < mySize; i++) {
        myItems[i] = original.myItems[i];
    }
}

Bag::~Bag() {
    delete[] myItems;
}

Bag& Bag::operator=(const Bag& rhs) {
    if (this != &rhs) {                  // 1. guard: b = b;
        delete[] myItems;                // 2. let go of the old array
        mySize  = rhs.mySize;
        myItems = new int[rhs.mySize];   // 3. get a new one and fill it
        for (unsigned i = 0; i < mySize; i++) {
            myItems[i] = rhs.myItems[i];
        }
    }
    return *this;                        // 4. so a = b = c works
}

unsigned Bag::getSize() const {
    return mySize;
}

int& Bag::operator[](unsigned i) {
    if (i >= mySize) {
        throw range_error("no item at that index");
    }
    return myItems[i];                   // a reference: bag[i] = 7
}

const int& Bag::operator[](unsigned i) const {
    if (i >= mySize) {
        throw range_error("no item at that index");
    }
    return myItems[i];                   // read only
}

unsigned Bag::operator()(int value) const {
    unsigned count = 0;
    for (unsigned i = 0; i < mySize; i++) {
        if (myItems[i] == value) {
            count++;
        }
    }
    return count;
}

ostream& operator<<(ostream& out, const Bag& bag) {
    out << "[";
    for (unsigned i = 0; i < bag.getSize(); i++) {
        if (i > 0) {
            out << ", ";
        }
        out << bag[i];                   // the const operator[]
    }
    out << "]";
    return out;
}
