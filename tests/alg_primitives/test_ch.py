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

from qframe.alg_primitives.ch import choose_gate, recip_choose_gate, recip_choose_first_order_gate
import qframe


@pytest.fixture
def n_float():
    return 2

@pytest.fixture
def target():
    return 3


def phase_oracle_init(p):
    qrisp.z(qrisp.h(p))

def oracle_function(a:qrisp.QuantumFloat, b:qrisp.QuantumFloat, c:qrisp.QuantumFloat, target):
    choose_gate(a, b, c)
    for i in range(target.bit_length()):
        if (target & 1<<i): qrisp.x(c[i])

def recip_oracle_function(a:qrisp.QuantumFloat, b:qrisp.QuantumFloat, c:qrisp.QuantumFloat, anc:qrisp.Qubit):
    phase_oracle_init(anc)
    recip_choose_gate(a, b, c, anc)

def recip_oracle_function_optimized(a:qrisp.QuantumFloat, b:qrisp.QuantumFloat, c:qrisp.QuantumFloat):
    recip_choose_first_order_gate(a, b, c)


class Test_Ch:
    def test_ch_single_bit(self):
        # Initialize variables
        a = qrisp.QuantumFloat(1, name='a')
        b = qrisp.QuantumFloat(1, name='b')
        c = qrisp.QuantumFloat(1, name='c')
        anc = qrisp.QuantumVariable(1, name='anc')

        # Prepare the quantum state in an equal-weighted superposition (Walsh-Hadamard transform)
        h(a)
        h(b)
        h(c)

        qrisp.barrier(a[0] + b[0] + c[0])

        # Single partial oracle iteration
        with qrisp.conjugate(oracle_function)(a, b, c, 0):
            qrisp.barrier(a[0] + b[0] + c[0])
            qrisp.s(c)
            qrisp.barrier(a[0] + b[0] + c[0])
        qrisp.barrier(a[0] + b[0] + c[0])
        h(a)
        h(b)
        h(c)
        qrisp.barrier(a[0] + b[0] + c[0])
        # with qrisp.conjugate(recip_oracle_function)(a, b, c, anc[0]):
        with qrisp.conjugate(recip_oracle_function_optimized)(a, b, c):
            qrisp.barrier(a[0] + b[0] + c[0])
            qrisp.s(c)
            qrisp.barrier(a[0] + b[0] + c[0])
        qrisp.barrier(list(a) + list(b) + list(c))
        h(c)
        h(b)
        h(a)

        # Show the circuit
        print(c.qs)

        # Show result
        result_dict = qrisp.multi_measurement([a, b, c])
        print(result_dict)

        for result_tuple in result_dict:
            (a_res, b_res, c_res) = result_tuple
            assert qframe.choose_function(a_res, b_res, c_res) == 0


    def test_ch_multi_bit(self, n_float, target):
        # Initialize variables
        a = qrisp.QuantumFloat(n_float, name='a')
        b = qrisp.QuantumFloat(n_float, name='b')
        c = qrisp.QuantumFloat(n_float, name='c')
        anc = qrisp.QuantumVariable(1, name='anc')

        # Prepare the quantum state in an equal-weighted superposition (Walsh-Hadamard transform)
        h(a)
        h(b)
        h(c)

        qrisp.barrier(list(a) + list(b) + list(c))

        # Single partial oracle iteration
        with qrisp.conjugate(oracle_function)(a, b, c, target):
            qrisp.barrier(list(a) + list(b) + list(c))
            qrisp.s(c)
            qrisp.barrier(list(a) + list(b) + list(c))
        qrisp.barrier(list(a) + list(b) + list(c))
        h(a)
        h(b)
        h(c)
        qrisp.barrier(list(a) + list(b) + list(c))
        # with qrisp.conjugate(recip_oracle_function)(a, b, c, anc[0]):
        with qrisp.conjugate(recip_oracle_function_optimized)(a, b, c):
            qrisp.barrier(list(a) + list(b) + list(c))
            qrisp.s(c)
            qrisp.barrier(list(a) + list(b) + list(c))
        qrisp.barrier(list(a) + list(b) + list(c))
        h(c)
        h(b)
        h(a)

        # Show the circuit
        print(c.qs)

        # Show result
        result_dict = qrisp.multi_measurement([a, b, c])
        print(result_dict)

        for result_tuple in result_dict:
            (a_res, b_res, c_res) = result_tuple
            assert qframe.choose_function(a_res, b_res, c_res, width=n_float) == target

    @pytest.mark.skip
    def test_ch_full_reciprocal_gate(self):
        pass
        # ToDo: The existing tests do NOT really test the full reciprocal gate, because they only
        # depend on the first order effects of the gate, not the full gate circuit.
