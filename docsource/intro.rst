********************************************************************************
Introduction
********************************************************************************

.. figure:: /_images/AGS_intro.png
    :figclass: figure
    :class: figure-img img-fluid

    A Fink truss is a statically determined structure that cannot be calculated
    directly with traditional graphic statics.

.. warning::

    Under construction...


*From the abstract of AGS*

Algebraic Graph Statics is a general, non-procedural, algebraic approach to graphical
analysis of structures.

Using graph theoretical properties of reciprocal graphs, the geometrical relation
between the form and force diagrams used in graphic statics is written algebraically.
These formulations have been found to be equivalent to the equilibrium equations
used in matrix analysis of planar, self-stressed structural systems.
The significance and uses of this general approach are demonstrated through several
examples and it is shown that it provides a robust back-end for a real-time,
interactive and flexible computational implementation of traditional graphic statics.

*From the outline of AGS*

In Section 2, we bring together concepts and techniques from graph theory and matrix
analysis of structures and present them in a unified framework for algebraic graphical
analysis built around the reciprocal relation between the form and force diagrams of
graphicstatics.

In Section 3, we discuss a general scheme for a computational implementation of
the presented approach that can be used as back-end of a real-time, interactive 
graphic statics application. 
Different steps of the implementation are illustrated using a Fink truss, which
is a statically determinate structure that cannot be calculated directly with traditional
graphic statics, because it contains crossing edges. 
Relevant algorithms are provided as code snippets.

In Section 4, the use of this framework for non-procedural graphic statics is
demonstrated through four examples: a three-hinged trussed frame, an externally
statically indeterminate three-bar truss, a geometrically constrained thrust line,
defining its funicular loading, and a pre-stressed net.
Finally, we briefly discuss the relevance of the presented approach for three-dimensional
equilibrium methods, such as Thrust Network Analysis.

*From the conclusions of AGS*

In Section 2.2, we discussed the interpretation of the form and force diagrams of
graphic statics as reciprocal graphs. 
We described how an algebraic formulation of the reciprocal relation between these
two graphs results in the equilibrium equations of an unloaded network that is
equivalent to the structural system represented by the form graph (Section 2.3).

We furthermore showed how the possible states of equilibrium of this structural system
can be controlled using the force densities of the system's free or independent
edges, which can be identified by rank analysis using singular value decomposition and
Gauss–Jordan elimination of the equilibrium matrix of the unloaded network (Section2.6).

In Section 3.2, we discussed how the topology of the force graph can be derived
from a planar straight-line drawing of the form graph using a wall following maze
solving algorithm.
We furthermore described an algorithm for generating planar straight-line drawings
of (planar) form graphs based on the repetitive application of a force-driven layout
method in combination with a crossing-edges check.

A computational setup allowing the presented approach to be used as back-end for
a graphic statics application in an interactive CAD environment was described in 
Section3.

Through a series of examples (Section 4), we showed how an implementation of the
computational setup can be used to investigate the equilibrium of different types
of structural systems, including a fink truss, a three-hinged arch, an indeterminate
structure, funicular systems and self-stressed networks.

Finally, the relation to advanced form-finding and analysis techniques for three-dimensional
equilibrium structures were briefly discussed.