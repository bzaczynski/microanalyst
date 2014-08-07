Case Study
==========

Overview
--------

Let us identify genes which consistently reduce the lifespan of sampled cells. In the first example we will take a closer look at strictly repeatable patterns, but later that constraint will be relaxed with the use of Hamming distance metric.

Basic Example
-------------

First, the experiment needs to be loaded from a JSON file with microanalyst. We will also need NumPy later on, thus the additional import statement.

::

 import microanalyst.model
 import numpy as np

 model = microanalyst.model.from_file(r'C:\data\experiment.json')

Clustering
^^^^^^^^^^

In order to facilitate pattern recognition well values must be translated to a simpler form. This can be achieved twofold, either via ``quantize.py`` script described in previous chapters or by directly manipulating the model, which is more flexible.

The most suitable representation of data samples in this case would be with sequences of binary digits. Designating "ones" for starved wells instead of "zeros" allows for capturing gene's values with a meaningful decimal number directly expressing the mortality of that gene. Due to positional nature of the binary system the earlier the moment of starvation the greater that number will be, which can serve as a simple metric. This is briefly demonstrated by the following table.

 +-----------+--------------------------+--------------------------+
 | iteration |            1st           |            2nd           |
 +-----------+--------+--------+--------+--------+--------+--------+
 | days      |   14   |   28   |   42   |   14   |   28   |   42   |
 +===========+========+========+========+========+========+========+
 | values    | 0.6915 | 0.0605 | 0.0603 | 0.6979 | 0.6187 | 0.0653 |
 +-----------+--------+--------+--------+--------+--------+--------+
 | binary    |    0   |    1   |    1   |    0   |    0   |    1   |
 +-----------+--------+--------+--------+--------+--------+--------+
 | decimal   |             3            |              1           |
 +-----------+--------------------------+--------------------------+

Binarization is straightforward given a known threshold (e.g. values below or equal to 0.2)::

 starved = model.array4d <= 0.2
 model.array4d[starved]  = 1
 model.array4d[~starved] = 0

However, this does not account for missing data samples (indicated with ``None``), which would be incorrectly regarded as zeros, nor for control wells. To reject them we need to isolate those elements with a mask before doing any value assignment and then mark invalid data samples with a special value after the binarization. The final code for value clustering could be encapsulated in a function similar to this one (note array type casting at the end to allow bitwise operations later):

.. code-block:: python

 def cluster(model):
     """Assign values: { starved=1, missing/control=2, other=0 }."""

     starved = model.array4d <= 0.2
     special = model.control_mask.values | np.equal(model.array4d, None)

     model.array4d[starved] = 1
     model.array4d[~starved] = 0
     model.array4d[special] = 2

     model.array4d = model.array4d.astype(np.int8, copy=False)

After calling ``cluster(model)`` the only values left should be 0, 1 and 2::

 >>> set(model.values().ravel())
 set([0, 1, 2])


Conversion
^^^^^^^^^^

One way of converting a sequence of binary digits, e.g. a tuple or a list of integers, to a decimal number is with bit shifting (from right to left):

.. code-block:: python

 def decimal(binary_digits):
     """Convert a sequence of binary digits to decimal number."""

     number = 0
     for i, digit in enumerate(reversed(binary_digits)):
         number |= digit << i

     return number

Example::

 >>> decimal([1, 0, 1, 1])
 11

Smoothing
^^^^^^^^^

Naturally cells which once died can no longer become alive. For this reason it is expected to observe continuous sequences of zeros followed by continuous sequences of ones but never the other way around. If for some reason that rule does not hold all initial "ones" must be discarded as false positives. Consider this:

 +--------+---+---+---+---+---+---+---+---+---------+
 |        |  binary                       | decimal |
 +--------+---+---+---+---+---+---+---+---+---------+
 | input  | 1 | 0 | 1 | 1 | 0 | 1 | 1 | 1 | 183     |
 +--------+---+---+---+---+---+---+---+---+---------+
 | output | 0 | 0 | 0 | 0 | 0 | 1 | 1 | 1 | 7       |
 +--------+---+---+---+---+---+---+---+---+---------+

A smoothing function::

 def smooth(number):
     """Discard bits before the last continuous block of ones."""

     result = 0
     i = 0

     while number & 1:
         result |= 1 << i
         i += 1
         number >>= 1

     return result

Example::

 >>> x = decimal([1, 0, 1, 1, 0, 1, 1, 1])
 >>> y = smooth(x)
 >>> print 'before: %d = %s, after: %d = %s' % (x, bin(x)[2:], y, bin(y)[2:])
 before: 183 = 10110111, after: 7 = 111

Filtering
^^^^^^^^^

Now that we have all the building blocks in place we can proceed to filtering genes by eliminating those which are of no interest. Specifically we want to skip genes containing control wells or with missing data samples or those which caused no cell starvation whatsoever. This can be done by examining values of a particular well measured at different points in time.

If you recall gene's ``values()`` method returns a complete picture of a particular microplate well (associated with a gene). The result is a 2-D array of samples measured within iterations (rows) and spreadsheets (columns)::

 >>> gene.values()
 array([[ 0.722     ,  0.6814    ,  0.70859998],
        [ 0.7245    ,  0.71319997,  0.73180002],
        [ 0.73210001,  0.7324    ,  0.77560002]])

Since our model was clustered the domain of ``values()`` becomes {0, 1, 2}::

 >>> gene.values()
 array([[0, 0, 0, 0],
        [0, 1, 1, 1],
        [2, 2, 2, 2]], dtype=int8)

Those clustered values can be used to evaluate genes::

 for gene in model.genes_used():

      values = gene.values()

      # missing/control wells are marked with "2"
      if 2 in set(values.ravel()): continue

      # lack of starvation adds up to zero
      if values.sum() == 0: continue

The next step is compressing a series of binary digits from each iteration into a smoothed decimal number using helper functions defined earlier::

 values = [smooth(decimal(x)) for x in values]

At this point smoothing might have introduced useless "zeros" again if the original binary sequence comprised of false positives followed by zeros. To mitigate this we need to rewrite our filter so that lack of starvation is detected afterwards. Additionally we add a condition for ignoring patterns which do not repeat exactly across iterations. Note that ``values`` becomes a list rather than numpy.ndarray due to the use of list comprehension::

 for gene in model.genes_used():

      values = gene.values()

      # missing/control wells are marked with "2"
      if 2 in set(values.ravel()): continue

      # express patterns with numbers
      values = [smooth(decimal(x)) for x in values]

      # lack of starvation adds up to zero
      if sum(values) == 0: continue

      # different patterns in iterations
      if len(set(values)) > 1: continue

Collecting
^^^^^^^^^^

If a gene makes its way through all the checks then it can be regarded as a legitimate candidate for further evaluation. We may save its name and starvation pattern in a dictionary. As intended the list of values contains identical patterns so we are free to pick any index, e.g. ``values[0]``::

 patterns = {}
 for gene in model.genes_used():
     (...)
     patterns[gene] = values[0]

Then to obtain protein names ranked by their mortality level (best come first)::

 >>> for i, gene in enumerate(reversed(sorted(patterns, key=patterns.get))):
 >>>     print '%d. %s' % (i + 1, gene)
 1. LYE328J
 2. LTE008P
 3. LBY102P
 4. LOE101P
 5. LQE368J
 6. LUY021P
 7. LWE127P
 8. LTY014J
 (...)

Remember to take advantage of ``xlsv.py`` and ``xlsh.py`` scripts for visualizing experiment data, which can substantially simplify and augment the process of protein analysis.

A distribution of genes causing death after a certain number of days can be calculated using a counter. The percentages are non-cumulative and are only relative to a small subset of genes which have a pattern repeating exactly across all subsequent iterations.::

 >>> from collections import Counter
 >>>
 >>> day_offsets = [14, 28, 42]
 >>>
 >>> counter = Counter(patterns.values())
 >>> for pattern in reversed(sorted(counter.keys(), key=counter.get)):
 >>>
 >>>      percentage = counter.get(pattern) / float(len(patterns)) * 100.0
 >>>      days = day_offsets[len(day_offsets) - len(bin(pattern)[2:])]
 >>>
 >>>      print '%d%% caused death after %d days' % (percentage, days)
 55% caused death after 42 days
 33% caused death after 14 days
 10% caused death after 28 days

Complete code
^^^^^^^^^^^^^

Basic Example::

 #!/usr/bin/env python

 # The MIT License (MIT)
 #
 # Copyright (c) 2014 Bartosz Zaczynski
 #
 # Permission is hereby granted, free of charge, to any person obtaining a copy
 # of this software and associated documentation files (the "Software"), to deal
 # in the Software without restriction, including without limitation the rights
 # to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 # copies of the Software, and to permit persons to whom the Software is
 # furnished to do so, subject to the following conditions:
 #
 # The above copyright notice and this permission notice shall be included in
 # all copies or substantial portions of the Software.
 #
 # THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 # IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 # FITNESS FOR A PARTICULAR PURPOSE ANfD NONINFRINGEMENT. IN NO EVENT SHALL THE
 # AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 # LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 # OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 # THE SOFTWARE.

 from collections import Counter

 import microanalyst.model
 import numpy as np


 def cluster(model):
     """Assign values: { starved=1, missing/control=2, other=0 }."""

     starved = model.array4d <= 0.2
     special = model.control_mask.values | np.equal(model.array4d, None)

     model.array4d[starved] = 1
     model.array4d[~starved] = 0
     model.array4d[special] = 2

     model.array4d = model.array4d.astype(np.int8, copy=False)


 def decimal(binary_digits):
     """Convert a sequence of binary digits to decimal number."""

     number = 0
     for i, digit in enumerate(reversed(binary_digits)):
         number |= digit << i

     return number


 def smooth(number):
     """Discard bits before the last continuous block of ones."""

     result = 0
     i = 0

     while number & 1:
         result |= 1 << i
         i += 1
         number >>= 1

     return result


 def show_ranked(patterns):
     """List protein names ranked by their mortality level."""
     for i, gene in enumerate(reversed(sorted(patterns, key=patterns.get))):
         print '%d. %s' % (i + 1, gene)


 def show_distribution(patterns, day_offsets):
     """Show distribution of genes' mortality level."""

     counter = Counter(patterns.values())
     for pattern in reversed(sorted(counter.keys(), key=counter.get)):

         percentage = counter.get(pattern) / float(len(patterns)) * 100.0
         days = day_offsets[len(day_offsets) - len(bin(pattern)[2:])]

         print '%d%% caused death after %d days' % (percentage, days)


 def main(filename):

     model = microanalyst.model.from_file(filename)

     cluster(model)

     patterns = {}
     for gene in model.genes_used():

         values = gene.values()

         # missing/control wells are marked with "2"
         if 2 in set(values.ravel()): continue

         # express patterns with numbers
         values = [smooth(decimal(x)) for x in values]

         # lack of starvation adds up to zero
         if sum(values) == 0: continue

         # different patterns in iterations
         if len(set(values)) > 1: continue

         patterns[gene] = values[0]

     day_offsets = [14*(i+1) for i in xrange(model.array4d.shape[1])]

     show_ranked(patterns)
     show_distribution(patterns, day_offsets)


 if __name__ == '__main__':
     main(r'C:\data\experiment.json')


Advanced Example
----------------

In this advanced example we will remove the constraint on strictly repeating patterns and replace it with a more sophisticated metric comprised of:

* the moment of starvation
* repeatability of patterns
* similarity of patterns.

Mortality
^^^^^^^^^

Mortality level will be calculated as before, i.e. by comparing numbers which reflect gene's binary patterns. A greater number indicates stronger effect on survival of the cells. Since the numbers from subsequent iterations might be different at this time the actual mortality is the sum of respective decimal numbers::

 mortality = sum(values)

Repeatability
^^^^^^^^^^^^^

A repeatable pattern is the one which contains at least one starvation and appears unchanged most frequently. Note there be might cases where a pattern is comprised of zeros in one iteration but not in the others. Therefore, we want to count occurrences of non-zero patterns only and determine the most frequent one as long as it occurs more than once. By definition a pattern which has a count of one is not repeatable.

Example:

 +-----------+----------------------------+---------------+
 | pattern   | occurrences                | repeatability |
 +===+===+===+============================+===============+
 | 0 | 0 | 1 | { "1": 1 }                 | 0             |
 +---+---+---+----------------------------+---------------+
 | 1 | 0 | 3 | { "1": 1, "3": 1 }         | 0             |
 +---+---+---+----------------------------+---------------+
 | 1 | 7 | 3 | { "1": 1, "3": 1, "7": 1 } | 0             |
 +---+---+---+----------------------------+---------------+
 | 0 | 3 | 3 | { "3": 2 }                 | 2             |
 +---+---+---+----------------------------+---------------+
 | 1 | 3 | 3 | { "1": 1, "3": 2 }         | 2             |
 +---+---+---+----------------------------+---------------+
 | 1 | 1 | 1 | { "1": 3 }                 | 3             |
 +---+---+---+----------------------------+---------------+

The code::

    from collections import Counter

    counter = Counter([x for x in values if x != 0])
    max_count = max(counter.values())

    repeatability = max_count if max_count > 1 else 0

Similarity
^^^^^^^^^^

Similarity is the measure of differences between the patterns observed in consecutive iterations. An essential part of this measure will be the Hamming distance which counts the number of positions at which two equally long binary strings manifest different digits::

 def hamming_distance(a, b):
     """Calculate the Hamming distance between two numbers."""

     result, c = 0, a ^ b
     while c:
         result += 1
         c &= c - 1

     return result

This needs to be extrapolated over all combinations of unordered pairs of patterns::

 import itertools

 def hamming_pairs(values):
     """Return the sum of Hamming distances between all pair combinations."""

     distance = 0
     for pair in itertools.combinations(values, 2):
         distance += hamming_distance(*pair)

     return distance

Unlike the factors defined earlier Hamming distance is inversely proportional to the measured quality, i.e. a short distance is considered to be better than a long one. In order to make it compatible with the remaining components of the metric it needs to be reversed. The actual distance must be subtracted from the maximum theoretical one.

.. math::
  H_{max} = k \cdot C^2_n = k \cdot {n \choose 2} = k \cdot \frac{n!}{2! \cdot (n - 2)!} = \frac{k \cdot n \cdot (n - 1)}{2}

  k - \text{number of spreadsheets per iteration}

  n - \text{number of iterations}

However, this formula as well as the Hamming distance itself cannot be applied directly on an unprocessed sequence of patterns. Just like with repeatability we need to exclude zeros from the computation to avoid comparing meaningless patterns such as (0, 0) and reject non-repeating patterns. Therefore::

    nonzero = [x for x in values if x != 0]

    n = len(nonzero)
    k = model.array4d.shape[1]

    hmax = k * n * (n - 1) / 2
    h = hamming_pairs(nonzero)

    similarity = hmax - h if n > 1 else 0

Final Metric
^^^^^^^^^^^^

All components can be encapsulated in a class utilizing delegation for the computation of specific metrics::

 from collection import namedtuple

 class Metric(object):

    def __init__(self, model, values):

        n, k = model.array4d.shape[:2]

        Component = namedtuple('Component', 'value, max')

        self.components = [
            Component(mortality(values), n*(2**k-1)),
            Component(repeatability(values), n),
            Component(similarity(model, values), k*n*(n-1)/2)
        ]

        self.percents = [x.value / float(x.max) * 100.0 for x in self.components]
        self.total = sum([x.value for x in self.components])

    def __str__(self):
        return '(m=%d%%, r=%d%%, s=%d%%)' % tuple(self.percents)

Example::

 >>> Metric(model, [3, 3, 1])
 (m=15%, r=66%, s=83%)

* Mortality is measured at 15% because the sum of all patterns amounts to 7, whereas the maximum is 3 x 15 for this particular model (there were four spreadsheets per iteration).
* Repeatability scores 66% because a pattern appears twice during three iterations.
* Similarity:

 .. math::

    S = \frac{H_{max} - \left(h(3, 3) + h(3, 1) + h(3, 1)\right)}{H_{max}} = \frac{12 - \left(0 + 1 + 1\right)}{12} = \frac{10}{12} \approx 85\%

    \text{where}

    H_{max} = \frac{k \cdot n \cdot (n - 1)}{2} = \frac{4 \cdot 3 \cdot 2}{2} = 12

Of course the components of this metric are correlated. For instance a pattern repeating exactly, i.e. having r=100%, implies similarity of s=100% and vice versa. However, some correlations do not work both ways such as mortality and repeatability (m=100% then r=100%, but not the other way around).

Scores
^^^^^^

Genes can be ranked by their total score::

 >>> it = sorted(metrics.iteritems(), key=lambda x: x[1].total)
 >>> for i, (gene, metric) in enumerate(reversed(it)):
 >>>     print '%d. %s = %s' % (i + 1, gene, metric)
 1. LVE011P = (m=100%, r=100%, s=100%)
 2. LVE013P = (m=100%, r=100%, s=100%)
 3. LUE026J = (m=82%, r=66%, s=83%)
 4. LYE299J = (m=64%, r=66%, s=83%)
 5. LUY031P = (m=68%, r=66%, s=50%)
 6. LZE276J = (m=46%, r=100%, s=100%)
 7. LZE179J = (m=66%, r=66%, s=33%)
 8. LTE162J = (m=46%, r=100%, s=100%)
 9. LPE088J = (m=46%, r=100%, s=100%)
 (...)

If some quality needs to be emphasized use a weighted average. For example to favour repeatable patterns (``average`` is defined in the next section)::

 >>> weights = [1, 2, 1]
 >>> it = sorted(metrics.iteritems(), key=lambda x: x[1].average(weights))
 >>> for i, (gene, metric) in enumerate(reversed(it)):
 >>>     print '%d. %s = %s' % (i + 1, gene, metric)
 1. LVE011P = (m=100%, r=100%, s=100%)
 2. LVE013P = (m=100%, r=100%, s=100%)
 3. LZE276J = (m=46%, r=100%, s=100%)
 4. LUY021P = (m=46%, r=100%, s=100%)
 5. LTE162J = (m=46%, r=100%, s=100%)
 6. LPE088J = (m=46%, r=100%, s=100%)
 7. LBE223J = (m=46%, r=100%, s=100%)
 8. LRE123J = (m=46%, r=100%, s=100%)
 9. LNY032P = (m=46%, r=100%, s=100%)
 (...)

Complete code
^^^^^^^^^^^^^

Advanced Example::

 #!/usr/bin/env python

 # The MIT License (MIT)
 #
 # Copyright (c) 2014 Bartosz Zaczynski
 #
 # Permission is hereby granted, free of charge, to any person obtaining a copy
 # of this software and associated documentation files (the "Software"), to deal
 # in the Software without restriction, including without limitation the rights
 # to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 # copies of the Software, and to permit persons to whom the Software is
 # furnished to do so, subject to the following conditions:
 #
 # The above copyright notice and this permission notice shall be included in
 # all copies or substantial portions of the Software.
 #
 # THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 # IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 # FITNESS FOR A PARTICULAR PURPOSE ANfD NONINFRINGEMENT. IN NO EVENT SHALL THE
 # AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 # LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 # OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 # THE SOFTWARE.

 from collections import Counter, namedtuple

 import microanalyst.model
 import numpy as np
 import itertools


 def cluster(model):
     """Assign values: { starved=1, missing/control=2, other=0 }."""

     starved = model.array4d <= 0.2
     special = model.control_mask.values | np.equal(model.array4d, None)

     model.array4d[starved] = 1
     model.array4d[~starved] = 0
     model.array4d[special] = 2

     model.array4d = model.array4d.astype(np.int8, copy=False)


 def decimal(binary_digits):
     """Convert a sequence of binary digits to decimal number."""

     number = 0
     for i, digit in enumerate(reversed(binary_digits)):
         number |= digit << i

     return number


 def smooth(number):
     """Discard bits before the last continuous block of ones."""

     result = 0
     i = 0

     while number & 1:
         result |= 1 << i
         i += 1
         number >>= 1

     return result


 def hamming_distance(a, b):
     """Calculate the Hamming distance between two numbers."""

     result, c = 0, a ^ b
     while c:
         result += 1
         c &= c - 1

     return result


 def hamming_pairs(values):
     """Return the sum of Hamming distances between all pair combinations."""

     distance = 0
     for pair in itertools.combinations(values, 2):
         distance += hamming_distance(*pair)

     return distance


 def mortality(values):
     return sum(values)


 def repeatability(values):
     counter = Counter([x for x in values if x != 0])
     max_count = max(counter.values())
     return max_count if max_count > 1 else 0


 def similarity(model, values):

     nonzero = [x for x in values if x != 0]

     n = len(nonzero)
     k = model.array4d.shape[1]

     hmax = k * n * (n - 1) / 2
     h = hamming_pairs(nonzero)

     return hmax - h if n > 1 else 0


 class Metric(object):

     def __init__(self, model, values):

         n, k = model.array4d.shape[:2]

         Component = namedtuple('Component', 'value, max')

         self.components = [
             Component(mortality(values), n*(2**k-1)),
             Component(repeatability(values), n),
             Component(similarity(model, values), k*n*(n-1)/2)
         ]

         self.percents = [x.value / float(x.max) * 100.0 for x in self.components]
         self.total = sum([x.value for x in self.components])

     def __str__(self):
         return '(m=%d%%, r=%d%%, s=%d%%)' % tuple(self.percents)

     def average(self, weights=None):

         if not weights:
             weights = [1] * 3

         return sum([weights[i] * self.percents[i] for i in xrange(3)]) / float(sum(weights))


 def show_ranked_total(metrics):
     _show_ranked(metrics, lambda x: x[1].total)


 def show_ranked_average(metrics, weights=None):
     _show_ranked(metrics, lambda x: x[1].average(weights))


 def _show_ranked(metrics, key_func):
     it = sorted(metrics.iteritems(), key=key_func)
     for i, (gene, metric) in enumerate(reversed(it)):
         print '%d. %s = %s' % (i + 1, gene, metric)


 def main(filename):

     model = microanalyst.model.from_file(filename)

     cluster(model)

     metrics = {}
     for gene in model.genes_used():

         values = gene.values()

         # missing/control wells are marked with "2"
         if 2 in set(values.ravel()): continue

         # express patterns with numbers
         values = [smooth(decimal(x)) for x in values]

         # lack of starvation adds up to zero
         if sum(values) == 0: continue

         metrics[gene] = Metric(model, values)

     #show_ranked_total(metrics)
     show_ranked_average(metrics, [1, 2, 1])


 if __name__ == '__main__':
     main(r'C:\data\experiment.json')
