/* Fraction.cpp, CS112 operator overloading cheatsheet
 * Calvin University · Fall 2026
 */

#include "Fraction.h"
#include <stdexcept>
#include <cstdlib>          // abs
using namespace std;

// ── Constructors ────────────────────────────────────────────────────────────

Fraction::Fraction() {
    myNumerator   = 0;
    myDenominator = 1;
}

Fraction::Fraction(int numerator, int denominator) {
    if (denominator == 0) {
        throw invalid_argument("a fraction cannot have denominator 0");
    }
    myNumerator   = numerator;
    myDenominator = denominator;
    reduce();
}

// ── Getters ─────────────────────────────────────────────────────────────────

int Fraction::getNumerator() const {
    return myNumerator;
}

int Fraction::getDenominator() const {
    return myDenominator;
}

// ── Private helper ──────────────────────────────────────────────────────────

void Fraction::reduce() {
    // Euclid's algorithm for the greatest common divisor
    int a = abs(myNumerator);
    int b = abs(myDenominator);
    while (b != 0) {
        int remainder = a % b;
        a = b;
        b = remainder;
    }
    if (a > 1) {
        myNumerator   /= a;
        myDenominator /= a;
    }
    if (myDenominator < 0) {        // sign lives in the numerator
        myNumerator   = -myNumerator;
        myDenominator = -myDenominator;
    }
}

// ── Arithmetic ──────────────────────────────────────────────────────────────

Fraction Fraction::operator+(const Fraction& rhs) const {
    int numerator   = myNumerator * rhs.myDenominator
                    + rhs.myNumerator * myDenominator;
    int denominator = myDenominator * rhs.myDenominator;
    return Fraction(numerator, denominator);  // constructor reduces
}

Fraction Fraction::operator-(const Fraction& rhs) const {
    return *this + (-rhs);          // reuse + and unary -
}

Fraction Fraction::operator*(const Fraction& rhs) const {
    return Fraction(myNumerator * rhs.myNumerator,
                    myDenominator * rhs.myDenominator);
}

Fraction Fraction::operator/(const Fraction& rhs) const {
    if (rhs.myNumerator == 0) {
        throw invalid_argument("cannot divide by zero");
    }
    return Fraction(myNumerator * rhs.myDenominator,
                    myDenominator * rhs.myNumerator);
}

Fraction& Fraction::operator+=(const Fraction& rhs) {
    *this = *this + rhs;         // reuse +, then hand this object back
    return *this;
}

Fraction Fraction::operator-() const {
    return Fraction(-myNumerator, myDenominator);
}

// The Fraction is on the right, so this cannot be a method
Fraction operator+(int lhs, const Fraction& rhs) {
    return Fraction(lhs, 1) + rhs;
}

// ── Comparison ──────────────────────────────────────────────────────────────

bool Fraction::operator==(const Fraction& rhs) const {
    // both are in lowest terms, so equal fractions have equal parts
    return myNumerator == rhs.myNumerator
        && myDenominator == rhs.myDenominator;
}

bool Fraction::operator!=(const Fraction& rhs) const {
    return !(*this == rhs);
}

bool Fraction::operator<(const Fraction& rhs) const {
    // denominators are positive, so cross-multiplying keeps
    // the direction
    return myNumerator * rhs.myDenominator
         < rhs.myNumerator * myDenominator;
}

bool Fraction::operator>(const Fraction& rhs) const {
    return rhs < *this;
}

bool Fraction::operator<=(const Fraction& rhs) const {
    return !(rhs < *this);
}

bool Fraction::operator>=(const Fraction& rhs) const {
    return !(*this < rhs);
}

// ── Increment ───────────────────────────────────────────────────────────────

Fraction& Fraction::operator++() {         // ++f
    myNumerator += myDenominator;          // add 1 = d/d
    return *this;
}

Fraction Fraction::operator++(int) {       // f++
    Fraction old = *this;                  // remember the old value
    ++(*this);                             // reuse the prefix version
    return old;                            // hand back the OLD value
}

// ── Conversion ──────────────────────────────────────────────────────────────

Fraction::operator double() const {
    return (double) myNumerator / myDenominator;
}

// ── Streams ─────────────────────────────────────────────────────────────────

ostream& operator<<(ostream& out, const Fraction& f) {
    out << f.getNumerator() << "/" << f.getDenominator();
    return out;                  // hand the stream back to chain
}

istream& operator>>(istream& in, Fraction& f) {
    int  numerator, denominator;
    char slash;
    in >> numerator >> slash >> denominator;
    if (in) {                    // only change f if the read worked
        f = Fraction(numerator, denominator);
    }
    return in;
}
