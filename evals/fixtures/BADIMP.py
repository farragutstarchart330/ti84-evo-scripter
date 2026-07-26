# Fixture: passes on desktop CPython, must FAIL in the sandbox.
# Proves that verification inherits the calculator's module restrictions
# instead of just being "python ran it and nothing crashed".
import statistics

print("Mean: {:.2f}".format(statistics.mean([1, 2, 3])))
