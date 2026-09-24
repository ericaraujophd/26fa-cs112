/* tests.cpp, CS112 operator overloading cheatsheet
 * Calvin University · Fall 2026
 *
 * One TEST_CASE per section of the cheatsheet page. If an example on
 * the page is ever wrong, one of these fails first.
 *
 * Notice how many of these are one line: REQUIRE(a + b == c) needs
 * operator+ AND operator== to exist. Write == early and everything
 * else becomes easy to test.
 */

#include "catch.hpp"
#include "Fraction.h"
#include "Bag.h"
#include <sstream>
#include <stdexcept>
using namespace std;

// ── Fraction ─────────────────────────────────────────────────────────

TEST_CASE("Fraction: constructors reduce and normalise", "[fraction]") {
    REQUIRE(Fraction().getNumerator() == 0);
    REQUIRE(Fraction().getDenominator() == 1);
    REQUIRE(Fraction(2, 4) == Fraction(1, 2));
    REQUIRE(Fraction(6, -8) == Fraction(-3, 4));
    REQUIRE(Fraction(6, -8).getDenominator() == 4);
    REQUIRE_THROWS_AS(Fraction(1, 0), invalid_argument);
}

TEST_CASE("Fraction: << and >>", "[fraction]") {
    ostringstream out;
    out << Fraction(1, 2) << " and " << Fraction(-3, 4);
    REQUIRE(out.str() == "1/2 and -3/4");     // chaining works

    istringstream in("3/9");
    Fraction f;
    in >> f;
    REQUIRE(f == Fraction(1, 3));
}

TEST_CASE("Fraction: arithmetic leaves operands alone", "[fraction]") {
    const Fraction a(1, 2);                   // const on purpose
    const Fraction b(3, 4);
    REQUIRE(a + b == Fraction(5, 4));
    REQUIRE(a - b == Fraction(-1, 4));
    REQUIRE(a * b == Fraction(3, 8));
    REQUIRE(a / b == Fraction(2, 3));
    REQUIRE(a == Fraction(1, 2));             // a did not change
    REQUIRE_THROWS_AS(a / Fraction(), invalid_argument);
}

TEST_CASE("Fraction: 2 + f, the free function", "[fraction]") {
    REQUIRE(2 + Fraction(1, 2) == Fraction(5, 2));
}

TEST_CASE("Fraction: += changes and chains", "[fraction]") {
    Fraction c(1, 4);
    c += Fraction(1, 2);
    REQUIRE(c == Fraction(3, 4));
    (c += Fraction(1, 4)) += Fraction(1, 1);  // the returned reference
    REQUIRE(c == Fraction(2, 1));
}

TEST_CASE("Fraction: unary minus", "[fraction]") {
    REQUIRE(-Fraction(1, 2) == Fraction(-1, 2));
    REQUIRE(-Fraction(-1, 2) == Fraction(1, 2));
}

TEST_CASE("Fraction: all six comparisons", "[fraction]") {
    Fraction a(1, 2), b(3, 4);
    REQUIRE(a != b);
    REQUIRE(a < b);
    REQUIRE(b > a);
    REQUIRE(a <= a);
    REQUIRE(a >= a);
    REQUIRE_FALSE(b <= a);
    REQUIRE(Fraction(-1, 2) < Fraction(1, 3));   // negatives too
}

TEST_CASE("Fraction: ++ prefix and postfix", "[fraction]") {
    Fraction d(1, 3);
    REQUIRE(++d == Fraction(4, 3));           // changed, then seen
    REQUIRE(d++ == Fraction(4, 3));           // seen, then changed
    REQUIRE(d == Fraction(7, 3));
}

TEST_CASE("Fraction: explicit conversion to double", "[fraction]") {
    REQUIRE((double) Fraction(1, 2) == 0.5);
    REQUIRE((double) Fraction(-3, 4) == -0.75);
}

// ── Bag ──────────────────────────────────────────────────────────────

TEST_CASE("Bag: [] in both flavours", "[bag]") {
    Bag bag(3);
    bag[0] = 7;                               // the non-const one
    bag[1] = 7;
    bag[2] = 2;
    const Bag& view = bag;                    // now only the const one
    REQUIRE(view[0] == 7);
    REQUIRE(view[2] == 2);
    REQUIRE_THROWS_AS(bag[3], range_error);
    REQUIRE_THROWS_AS(view[3], range_error);
}

TEST_CASE("Bag: () counts", "[bag]") {
    Bag bag(3);
    bag[0] = 7;
    bag[1] = 7;
    bag[2] = 2;
    REQUIRE(bag(7) == 2);
    REQUIRE(bag(2) == 1);
    REQUIRE(bag(9) == 0);
}

TEST_CASE("Bag: copy constructor is a deep copy", "[bag]") {
    Bag a(2);
    a[0] = 1;
    Bag b = a;                                // copy constructor
    b[0] = 99;
    REQUIRE(a[0] == 1);                       // a has its own array
}

TEST_CASE("Bag: operator= is deep and self-safe", "[bag]") {
    Bag a(2), b(5);
    a[0] = 1;
    a[1] = 2;
    b = a;
    REQUIRE(b.getSize() == 2);
    REQUIRE(b[1] == 2);
    b[1] = 42;
    REQUIRE(a[1] == 2);                       // a untouched

    b = b;                                    // the guard
    REQUIRE(b[1] == 42);

    Bag c(1);
    c = b = a;                                // chains, because *this
    REQUIRE(c[1] == 2);
}

TEST_CASE("Bag: << goes through the const []", "[bag]") {
    Bag bag(3);
    bag[0] = 7;
    bag[1] = 7;
    bag[2] = 2;
    ostringstream out;
    out << bag;
    REQUIRE(out.str() == "[7, 7, 2]");
}
