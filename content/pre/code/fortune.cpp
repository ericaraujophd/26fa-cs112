/* fortune.cpp
 * CS112 Pre-Lab 00 — The CS112 Oracle
 * Calvin University
 * Author: YOUR NAME HERE
 */

#include "fortune.h"
#include <string>
using namespace std;

/* getFortune()
 * Selects one of 10 fortune strings based on stressLevel and birthMonth.
 *
 * How the selection works:
 *   index = (stressLevel + birthMonth) % NUM_FORTUNES
 *
 * Because stressLevel ranges from 1-5 and birthMonth from 1-12,
 * different students will get different fortunes — the Oracle is personal!
 *
 * YOUR TASK: Replace each placeholder string ("Fortune N: ...") with a
 * funny, CS-themed fortune of your own. Keep it clean and school-appropriate.
 * Each fortune should be a complete sentence ending in a period or
 * exclamation point.
 *
 * Example of a good fortune:
 *   "Your code will work on the first try. You will not trust it. Good instinct."
 */
string getFortune(int stressLevel, int birthMonth) {
    const int NUM_FORTUNES = 10;

    string fortunes[NUM_FORTUNES] = {
        // TODO: Replace each line below with your own funny CS-themed fortune.
        // You must keep exactly 10 strings. Each should end with . or !
        "Fortune 0: Replace this with something funny.",   // index 0
        "Fortune 1: Replace this with something funny.",   // index 1
        "Fortune 2: Replace this with something funny.",   // index 2
        "Fortune 3: Replace this with something funny.",   // index 3
        "Fortune 4: Replace this with something funny.",   // index 4
        "Fortune 5: Replace this with something funny.",   // index 5
        "Fortune 6: Replace this with something funny.",   // index 6
        "Fortune 7: Replace this with something funny.",   // index 7
        "Fortune 8: Replace this with something funny.",   // index 8
        "Fortune 9: Replace this with something funny."    // index 9
    };

    int index = (stressLevel + birthMonth) % NUM_FORTUNES;
    return fortunes[index];
}
