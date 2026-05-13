/* main.cpp
 * CS112 Pre-Lab 00 — The CS112 Oracle
 * Calvin University
 *
 * NOTE TO STUDENTS: You do NOT need to edit this file.
 * Your only job is to complete fortune.cpp.
 */

#include <iostream>
#include <string>
#include "fortune.h"
using namespace std;

int main() {
    string name;
    int stressLevel;
    int birthMonth;

    cout << "=============================================" << endl;
    cout << "        Welcome to the CS112 Oracle!" << endl;
    cout << "   (where segfaults are just... destiny)" << endl;
    cout << "=============================================" << endl;
    cout << endl;

    cout << "What is your name? ";
    cin >> name;

    cout << "On a scale of 1-5, how nervous are you about CS112? ";
    cin >> stressLevel;

    cout << "What month were you born in (1-12)? ";
    cin >> birthMonth;

    cout << endl;
    cout << "  ...consulting the ancient data structures..." << endl;
    cout << endl;

    string fortune = getFortune(stressLevel, birthMonth);

    cout << "=============================================" << endl;
    cout << "  The Oracle speaks, " << name << "!" << endl;
    cout << "=============================================" << endl;
    cout << endl;
    cout << fortune << endl;
    cout << endl;
    cout << "=============================================" << endl;
    cout << endl;

    return 0;
}
