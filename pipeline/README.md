# Pipeline

A `Pipeline` is a simple functional class that uses `Pipe`s to chain together
pairs of classifiers and filters to run a cohesive pipeline over a dataset.
For example, a `Pipeline` could be created to be used for HIPAA classification.
All that would need to be done would be pairing the required classifiers for HIPAA
and pairing them with their correct filters, such as dropping a column or paring
an address down to a ZIP code.

