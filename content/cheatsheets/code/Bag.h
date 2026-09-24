/* Bag.h, CS112 operator overloading cheatsheet
 * Calvin University · Fall 2026
 *
 * A fixed-size bag of ints on the heap. It exists to show the operators
 * a class needs once it owns memory: =, [] in two flavours, and ().
 */

#ifndef BAG_H
#define BAG_H

#include <iostream>
using namespace std;

class Bag {
public:
    Bag(unsigned size);                  // size zeros
    Bag(const Bag& original);            // deep copy
    ~Bag();
    Bag& operator=(const Bag& rhs);      // deep copy, self-safe

    unsigned getSize() const;

    // subscript, one for reading a const Bag, one for changing
    int&       operator[](unsigned i);          // throws
    const int& operator[](unsigned i) const;    // throws

    // call operator: bag(k) counts how many items equal k
    unsigned operator()(int value) const;

private:
    int*     myItems;
    unsigned mySize;
};

ostream& operator<<(ostream& out, const Bag& bag);

#endif
