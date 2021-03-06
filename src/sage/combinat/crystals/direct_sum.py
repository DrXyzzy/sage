"""
Direct Sum of Crystals
"""
#*****************************************************************************
#       Copyright (C) 2010 Anne Schilling <anne at math.ucdavis.edu>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#
#    This code is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#    General Public License for more details.
#
#  The full text of the GPL is available at:
#
#                  http://www.gnu.org/licenses/
#****************************************************************************

from sage.structure.parent import Parent
from sage.categories.category import Category
from sage.sets.disjoint_union_enumerated_sets import DisjointUnionEnumeratedSets
from sage.structure.element_wrapper import ElementWrapper

class DirectSumOfCrystals(DisjointUnionEnumeratedSets):
    r"""
    Direct sum of crystals.

    Given a list of crystals `B_0, \ldots, B_k` of the same Cartan type,
    one can form the direct sum `B_0 \oplus \cdots \oplus B_k`.

    INPUT:

     - ``crystals``  -- a list of crystals of the same Cartan type
     - ``keepkey``   -- a boolean

    The option ``keepkey`` is by default set to ``False``, assuming
    that the crystals are all distinct. In this case the elements of
    the direct sum are just represented by the elements in the
    crystals `B_i`.  If the crystals are not all distinct, one should
    set the ``keepkey`` option to ``True``.  In this case, the
    elements of the direct sum are represented as tuples `(i, b)`
    where `b \in B_i`.

    EXAMPLES::

        sage: C = crystals.Letters(['A',2])
        sage: C1 = crystals.Tableaux(['A',2],shape=[1,1])
        sage: B = crystals.DirectSum([C,C1])
        sage: B.list()
        [1, 2, 3, [[1], [2]], [[1], [3]], [[2], [3]]]
        sage: [b.f(1) for b in B]
        [2, None, None, None, [[2], [3]], None]
        sage: B.module_generators
        [1, [[1], [2]]]

    ::

        sage: B = crystals.DirectSum([C,C], keepkey=True)
        sage: B.list()
        [(0, 1), (0, 2), (0, 3), (1, 1), (1, 2), (1, 3)]
        sage: B.module_generators
        [(0, 1), (1, 1)]
        sage: b = B( tuple([0,C(1)]) )
        sage: b
        (0, 1)
        sage: b.weight()
        (1, 0, 0)

    The following is required, because
    :class:`~sage.combinat.crystals.direct_sum.DirectSumOfCrystals`
    takes the same arguments as :class:`DisjointUnionEnumeratedSets`
    (which see for details).

    TESTS::

        sage: C = crystals.Letters(['A',2])
        sage: B = crystals.DirectSum([C,C], keepkey=True)
        sage: B
        Direct sum of the crystals Family (The crystal of letters for type ['A', 2], The crystal of letters for type ['A', 2])

        sage: TestSuite(C).run()
    """
    __classcall_private__ = staticmethod(DisjointUnionEnumeratedSets.__classcall_private__)


    def __init__(self, crystals, **options):
        """
        TESTS::

            sage: C = crystals.Letters(['A',2])
            sage: B = crystals.DirectSum([C,C], keepkey=True)
            sage: B
            Direct sum of the crystals Family (The crystal of letters for type ['A', 2], The crystal of letters for type ['A', 2])
            sage: B.cartan_type()
            ['A', 2]

            sage: from sage.combinat.crystals.direct_sum import DirectSumOfCrystals
            sage: isinstance(B, DirectSumOfCrystals)
            True
        """
        if 'keepkey' in options:
            keepkey = options['keepkey']
        else:
            keepkey = False
#        facade = options['facade']
        if keepkey:
            facade = False
        else:
            facade = True
        category = Category.meet([Category.join(crystal.categories()) for crystal in crystals])
        Parent.__init__(self, category = category)
        DisjointUnionEnumeratedSets.__init__(self, crystals, keepkey = keepkey, facade = facade)
        self.rename("Direct sum of the crystals %s"%(crystals,))
        self._keepkey = keepkey
        self.crystals = crystals
        if len(crystals) == 0:
            raise ValueError("The direct sum is empty")
        else:
            assert(crystal.cartan_type() == crystals[0].cartan_type() for crystal in crystals)
            self._cartan_type = crystals[0].cartan_type()
        if keepkey:
            self.module_generators = [ self(tuple([i,b])) for i in range(len(crystals))
                                       for b in crystals[i].module_generators ]
        else:
            self.module_generators = sum( (list(B.module_generators) for B in crystals), [])


    class Element(ElementWrapper):
        r"""
        A class for elements of direct sums of crystals
        """

        def e(self, i):
            r"""
            Returns the action of `e_i` on self.

            EXAMPLES::

                sage: C = crystals.Letters(['A',2])
                sage: B = crystals.DirectSum([C,C], keepkey=True)
                sage: [[b, b.e(2)] for b in B]
                [[(0, 1), None], [(0, 2), None], [(0, 3), (0, 2)], [(1, 1), None], [(1, 2), None], [(1, 3), (1, 2)]]
            """
            v = self.value
            vn = v[1].e(i)
            if vn is None:
                return None
            else:
                return self.parent()(tuple([v[0],vn]))

        def f(self, i):
            r"""
            Returns the action of `f_i` on self.

            EXAMPLES::

                sage: C = crystals.Letters(['A',2])
                sage: B = crystals.DirectSum([C,C], keepkey=True)
                sage: [[b,b.f(1)] for b in B]
                [[(0, 1), (0, 2)], [(0, 2), None], [(0, 3), None], [(1, 1), (1, 2)], [(1, 2), None], [(1, 3), None]]
            """
            v = self.value
            vn = v[1].f(i)
            if vn is None:
                return None
            else:
                return self.parent()(tuple([v[0],vn]))

        def weight(self):
            r"""
            Returns the weight of self.

            EXAMPLES::

                sage: C = crystals.Letters(['A',2])
                sage: B = crystals.DirectSum([C,C], keepkey=True)
                sage: b = B( tuple([0,C(2)]) )
                sage: b
                (0, 2)
                sage: b.weight()
                (0, 1, 0)
            """
            return self.value[1].weight()

        def phi(self, i):
            r"""
            EXAMPLES::

                sage: C = crystals.Letters(['A',2])
                sage: B = crystals.DirectSum([C,C], keepkey=True)
                sage: b = B( tuple([0,C(2)]) )
                sage: b.phi(2)
                1
            """
            return self.value[1].phi(i)

        def epsilon(self, i):
            r"""
            EXAMPLES::

                sage: C = crystals.Letters(['A',2])
                sage: B = crystals.DirectSum([C,C], keepkey=True)
                sage: b = B( tuple([0,C(2)]) )
                sage: b.epsilon(2)
                0
            """
            return self.value[1].epsilon(i)

