********************************************************************************
Algebraic Graph Statics
********************************************************************************

.. warning::

    Under construction...


.. code-block:: latex

    @article{VanMele2014,
        author  = "Van Mele, T. and Block, P.",
        title   = "Algebraic Graph Statics",
        journal = "Computer-Aided Design",
        year    = "2014",
        volume  = "53",
        number  = "",
        pages   = "104-116",
        month   = "",
        doi     = "10.1016/j.cad.2014.04.004",
        note    = "",
    }


**Abstract**

This paper presents a general, non-procedural, algebraic approach to graphical
analysis of structures.
Using graph theoretical properties of reciprocal graphs, the geometrical relation
between the form and force diagrams used in graphic statics is written algebraically.
These formulations have been found to be equivalent to the equilibrium equations
used in matrix analysis of planar, self-stressed structural systems.
The significance and uses of this general approach are demonstrated through several
examples and it is shown that it provides a robust back-end for a real-time, interactive
and flexible computational implementation of traditional graphic statics.


**Contributions**

The paper brings together concepts and techniques from graph theory and matrix 
analysis of structures and present them in a unified framework for algebraic graphical
analysis built around the reciprocal relation between the form and force diagrams
of graphic statics.

A general scheme is discussed for a computational implementation of the presented
approach that can be used as back-end of a real-time, interactive graphic statics
application.
Different steps of the implementation are illustrated using a Fink truss, which
is a statically determinate structure that cannot be calculated directly with 
traditional graphic statics, because it contains crossing edges.
Relevant algorithms are provided as code snippets.

The use of this framework for non-procedural graphic statics is demonstrated through
four examples: a three-hinged trussed frame, an externally statically indeterminate
three-bar truss, a geometrically constrained thrust line, defining its funicular
loading, and a pre-stressed net.
Finally, we briefly discuss the relevance of the presented approach for three-dimensional
equilibrium methods, such as Thrust Network Analysis.
