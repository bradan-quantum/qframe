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

import qrisp
from qrisp import h

@qrisp.gate_wrap(name='rCarry')
def recip_carry_gate(a:qrisp.Qubit, b:qrisp.Qubit, c:qrisp.Qubit, phase_oracle:qrisp.Qubit):
    qrisp.cx(a, c)
    qrisp.cx(b, c)
    with qrisp.control(c):
        qrisp.mcx([a, b], phase_oracle)
        h(a)
        h(b)
        qrisp.mcx([a, b], phase_oracle)
        qrisp.swap(a, b)

@qrisp.gate_wrap(name='rCarry_inv')
def recip_carry_gate_inverse(a:qrisp.Qubit, b:qrisp.Qubit, c:qrisp.Qubit, phase_oracle:qrisp.Qubit):
    with qrisp.invert():
        recip_carry_gate(a, b, c, phase_oracle)

@qrisp.gate_wrap(name='rSum')
def recip_sum_gate(a:qrisp.Qubit, b:qrisp.Qubit, c:qrisp.Qubit):
    qrisp.cx(b, a)
    qrisp.cx(b, c)

@qrisp.gate_wrap(name='rAdd')
def recip_adder_gate(x:qrisp.QuantumFloat, y:qrisp.QuantumFloat, c:qrisp.Qubit, phase_oracle:qrisp.Qubit):
    if (len(x) != len(y)):
        raise Exception('Addition operands must have the same bit length')
    n_float = len(x)
    # Add reciprocal carry gates
    for k in range(n_float - 1):
        recip_carry_gate(x[k], y[k], c, phase_oracle)
    # Add sum gate for highest order bit
    recip_sum_gate(x[n_float - 1], y[n_float - 1], c)
    # Add descending carry inverse / sum gates
    for k in reversed(range(n_float - 1)):
        recip_carry_gate_inverse(x[k], y[k], c, phase_oracle)
        recip_sum_gate(x[k], y[k], c)
