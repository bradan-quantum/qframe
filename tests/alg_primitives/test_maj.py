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

from qframe.alg_primitives.maj import majority_gate, recip_majority_gate


@pytest.fixture
def n_float():
    return 2

@pytest.fixture
def target():
    return 11


def phase_oracle_init(p):
    qrisp.z(qrisp.h(p))

def apply_oracle_function(a:qrisp.QuantumFloat, b:qrisp.QuantumFloat, c:qrisp.QuantumFloat, target):
    majority_gate(a, b, c)
    for i in range(target.bit_length()):
        if (target & 1<<i): qrisp.x(c[i])

def apply_recip_oracle_function(a:qrisp.QuantumFloat, b:qrisp.QuantumFloat, c:qrisp.QuantumFloat, anc:qrisp.Qubit):
    phase_oracle_init(anc)
    recip_majority_gate(a, b, c, anc)


class Test_Maj:
    def test_maj_single_bit(self):
        # Initialize variables
        a = qrisp.QuantumFloat(1, name='a')
        b = qrisp.QuantumFloat(1, name='b')
        c = qrisp.QuantumFloat(1, name='c')
        anc = qrisp.QuantumVariable(1, name='anc')

        # Prepare the quantum state in an equal-weighted superposition (Walsh-Hadamard transform)
        h(a)
        h(b)
        h(c)

        qrisp.barrier(a[0] + b[0] + c[0] + anc[0])

        # Single partial oracle iteration
        with qrisp.conjugate(apply_oracle_function)(a, b, c, 0):
            qrisp.barrier(a[0] + b[0] + c[0] + anc[0])
            qrisp.s(c)
            qrisp.barrier(a[0] + b[0] + c[0] + anc[0])
        qrisp.barrier(a[0] + b[0] + c[0] + anc[0])
        h(a)
        h(b)
        h(c)
        qrisp.barrier(a[0] + b[0] + c[0] + anc[0])
        with qrisp.conjugate(apply_recip_oracle_function)(a, b, c, anc[0]):
            qrisp.barrier(a[0] + b[0] + c[0] + anc[0])
            qrisp.s(c)
            qrisp.barrier(a[0] + b[0] + c[0] + anc[0])
        h(c)
        h(b)
        h(a)

        # Show the circuit
        print(c.qs)
        # Show result
        print(qrisp.multi_measurement([a, b, c]))

