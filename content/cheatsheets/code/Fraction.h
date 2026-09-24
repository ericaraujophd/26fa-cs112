/* Fraction.h, CS112 operator overloading cheatsheet
 * Calvin University · Fall 2026
 *
 * A fraction with an integer numerator and denominator, kept in
 * lowest terms with a positive denominator. Every operator on
 * the cheatsheet page is declared here and defined in Fraction.cpp.
 *
 * Read the page and this file side by side. The page explains each
 * operator; this file is the exact signature to copy.
 */

#ifndef FRACTION_H
#define FRACTION_H

#include <iostream>
using namespace std;

class Fraction {
public:
    Fraction();                               // 0/1
    Fraction(int numerator, int denominator); // throws invalid_argument

    int getNumerator() const;
    int getDenominator() const;

    // arithmetic: a new Fraction, neither operand changes
    Fraction operator+(const Fraction& rhs) const;
    Fraction operator-(const Fraction& rhs) const;
    Fraction operator*(const Fraction& rhs) const;
    Fraction operator/(const Fraction& rhs) const;  // throws

    // compound assignment: this object changes, then hands
    // itself back
    Fraction& operator+=(const Fraction& rhs);

    // unary minus: -f
    Fraction operator-() const;

    // comparison
    bool operator==(const Fraction& rhs) const;
    bool operator!=(const Fraction& rhs) const;
    bool operator< (const Fraction& rhs) const;
    bool operator> (const Fraction& rhs) const;
    bool operator<=(const Fraction& rhs) const;
    bool operator>=(const Fraction& rhs) const;

    // increment: ++f adds one and hands back this object,
    //            f++ adds one and hands back a copy of the
    //            OLD value
    Fraction  operator++(int);   // postfix, the int is a dummy
    Fraction& operator++();      // prefix

    // conversion: (double)f, explicit so it never happens
    // by accident
    explicit operator double() const;

private:
    int myNumerator;
    int myDenominator;

    void reduce();               // lowest terms, positive denom.
};

// stream operators are free functions: the left operand is
// the stream
ostream& operator<<(ostream& out, const Fraction& f);
istream& operator>>(istream& in, Fraction& f);   // reads "3/4"

// mixed arithmetic where the Fraction is on the RIGHT: 2 + f
Fraction operator+(int lhs, const Fraction& rhs);

#endif
