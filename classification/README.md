# deiden
A simple de-identification framework based around the `Classifier`
class in `classifier.py`.
These classifiers take in a column from a table and then output a
rating from 0 to 1 that rate the "probability" of the column containing
PII (the probability isn't an actual probability and is more aptly called
a heuristic).
The simplest way to measure this is to take a per-row sample and try to
classify it as a certain kind of PII, then taking the percentage of rows
that were successfully classified.

