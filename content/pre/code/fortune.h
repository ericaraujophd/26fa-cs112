/* fortune.h
 * CS112 Pre-Lab 00 — The CS112 Oracle
 * Calvin University
 */

#ifndef FORTUNE_H
#define FORTUNE_H

#include <string>

/* getFortune()
 * Parameters:
 *   stressLevel — an integer from 1 (very calm) to 5 (full panic mode)
 *   birthMonth  — an integer from 1 (January) to 12 (December)
 * Returns:
 *   A fortune string selected from an array of 10 possibilities.
 */
std::string getFortune(int stressLevel, int birthMonth);

#endif
