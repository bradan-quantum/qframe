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

from qframe.alg_primitives.adder import recip_adder_gate


@pytest.fixture
def n_float():
    return 4

@pytest.fixture
def target():
    return 11


def phase_oracle_init(p):
    qrisp.z(qrisp.h(p))

def apply_oracle_function(x:qrisp.QuantumFloat, y:qrisp.QuantumFloat, target):
    y += x
    for i in range(target.bit_length()):
        if (target & 1<<i): qrisp.x(y[i])

def apply_recip_oracle_function(x:qrisp.QuantumFloat, y:qrisp.QuantumFloat, c:qrisp.Qubit, anc:qrisp.Qubit):
    # Initialize reciprocal carry bit
    h(c)
    phase_oracle_init(anc)
    recip_adder_gate(x, y, c, anc)


class Test_Adder:
    def test_adder(self, n_float, target):
        # Initialize variables
        x = qrisp.QuantumFloat(n_float, name='x')
        y = qrisp.QuantumFloat(n_float, name='y')
        carry = qrisp.QuantumVariable(1, name='c')
        anc   = qrisp.QuantumVariable(1, name='anc')

        # Prepare the quantum state in an equal-weighted superposition (Walsh-Hadamard transform)
        h(x)
        h(y)

        qrisp.barrier(x[:] + y[:] + carry[0] + anc[0])

        # Single partial oracle iteration
        with qrisp.conjugate(apply_oracle_function)(x, y, target):
            qrisp.barrier(x[:] + y[:] + carry[0] + anc[0])
            qrisp.s(y)
            qrisp.barrier(x[:] + y[:] + carry[0] + anc[0])
        qrisp.barrier(x[:] + y[:] + carry[0] + anc[0])
        h(x)
        h(y)
        qrisp.barrier(x[:] + y[:] + carry[0] + anc[0])
        with qrisp.conjugate(apply_recip_oracle_function)(x, y, carry[0], anc[0]):
            qrisp.barrier(x[:] + y[:] + carry[0] + anc[0])
            qrisp.s(y)
            qrisp.barrier(x[:] + y[:] + carry[0] + anc[0])
        h(y)
        h(x)

        # Show the circuit
        print(y.qs)
        # Show result
        print(qrisp.multi_measurement([x, y]))

