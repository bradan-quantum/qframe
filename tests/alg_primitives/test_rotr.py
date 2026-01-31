# ********************************************************************************
# * Copyright (c) 2026 Bradan Quantum GmbH
# *
# * This program and the accompanying materials are made available under the
# * terms of the Eclipse Public License 2.0 which is available at
# * http://www.eclipse.org/legal/epl-2.0.
# *
# * This Source Code may also be made available under the following Secondary
# * Licenses when the conditions for such availability set forth in the Eclipse
# * Public License, v. 2.0 are satisfied: GNU General Public License, version 2
# * with the GNU Classpath Exception which is
# * available at https://www.gnu.org/software/classpath/license.html.
# *
# * SPDX-License-Identifier: EPL-2.0 OR GPL-2.0 WITH Classpath-exception-2.0
# ********************************************************************************

import pytest

import qrisp
from qrisp import h

from qframe.alg_primitives.rotr import Rotr


@pytest.fixture
def rotr_instance():
    pass


class Test_Rotr:
    def test_rotr_inv_func(self):
        r = Rotr(8, [0, 1, 3])
        for x in range(2**8):
            assert x == r.inv_rotr_function( r.rotr_function(x) )
        r = Rotr(8, [2, 5, 7])
        for x in range(2**8):
            assert x == r.inv_rotr_function( r.rotr_function(x) )
        r = Rotr(8, [2, 5], shr_list=[7])
        for x in range(2**8):
            assert x == r.inv_rotr_function( r.rotr_function(x) )

    def oracle_function(self, r: Rotr, x: qrisp.QuantumVariable, anc: qrisp.QuantumVariable, target):
        r.rotr_gate(x, anc)
        for i in range(target.bit_length()):
            if (target & 1<<i): qrisp.x(x[i])

    def recip_oracle_function(self, r: Rotr, x: qrisp.QuantumVariable, anc: qrisp.QuantumVariable):
        r.recip_rotr_gate(x, anc)

    def test_rotr_gate(self):
        # r = Rotr(8, [2, 5, 7])
        r = Rotr(8, [2, 5], shr_list=[7])
        seed = 0b10011011
        target = r.rotr_function(seed)
        print(f'seed = 0b{seed:08b}')
        print(f'target = 0b{target:08b}')

        # Brute force the solution
        brute_soln = list()
        for j in range(2**8):
            if r.rotr_function(j) == target:
                brute_soln.append(j)
        print('Brute force solution:')
        print(brute_soln)

        # Initialize variables
        x   = qrisp.QuantumFloat(8, name='x')
        anc = qrisp.QuantumFloat(8, name='anc')

        # Prepare the quantum state in an equal-weighted superposition (Walsh-Hadamard transform)
        h(x)

        qrisp.barrier(list(x) + list(anc))

        # Single partial oracle iteration
        with qrisp.conjugate(self.oracle_function)(r, x, anc, target):
            qrisp.barrier(list(x) + list(anc))
            qrisp.s(x)
            qrisp.barrier(list(x) + list(anc))
        qrisp.barrier(list(x) + list(anc))
        h(x)
        qrisp.barrier(list(x) + list(anc))
        with qrisp.conjugate(self.recip_oracle_function)(r, x, anc):
            qrisp.barrier(list(x) + list(anc))
            qrisp.s(x)
            qrisp.barrier(list(x) + list(anc))
        qrisp.barrier(list(x) + list(anc))
        h(x)

        # Show the circuit
        print(x.qs)

        # Show result
        results = x.get_measurement()
        print(results)

        # for meas in results.keys():
        #     print(f'meas = 0b{meas:08b}, rotr_function(meas) = 0b{r.rotr_function(meas):08b}')
        #     assert meas == seed

    @pytest.mark.skip
    def test_rotr_gate_variants(self):
        r = Rotr(8, [2, 5, 7])
        seed = 0b10011011

        # Variant 1
        x   = qrisp.QuantumFloat(8, name='x')
        anc = qrisp.QuantumFloat(8, name='anc')

        x[:] = seed

        r.rotr_gate(x, anc, clean_up=False)
        print(qrisp.multi_measurement([x, anc]))

        with qrisp.invert():
            r.rotr_gate(x, anc, clean_up=False)

        r.recip_rotr_gate(x, anc, clean_up=False)
        print(qrisp.multi_measurement([x, anc]))

        # Variant 2
        # x1   = qrisp.QuantumFloat(8, name='x')
        # anc1 = qrisp.QuantumFloat(8, name='anc')

        # r.rotr_gate(x1, anc1, clean_up=False, no_swap=True)
        # print(x.qs)
