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

def _bit(b, j):
    return ((0b1 << j) & b) >> j

def choose_function(a: int, b: int, c: int, width=1) -> int:
    if (a.bit_length() > width) or (b.bit_length() > width) or (c.bit_length() > width):
        raise Exception(f'Arguments a, b, c greater than specified bit width {width}')
    result = 0
    for i in range(width):
        ai = _bit(a, i)
        bi = _bit(b, i)
        ci = _bit(c, i)
        result |= ( (ai * bi) ^ ((1-ai) * ci) ) << i
    return result

@qrisp.gate_wrap(name='Ch')
def choose_gate(a, b, c):
    qrisp.cx(c, b)
    for k in range(len(c)):
        qrisp.mcx([a[k], b[k]], c[k])

def _recip_choose_single_bit_gate(a:qrisp.Qubit, b:qrisp.Qubit, c:qrisp.Qubit, phase_oracle:qrisp.Qubit):
    """
    Applies the single-qubit variant of the reciprocal choose() gate
    """
    qrisp.cx(b, c)
    with qrisp.control(c):
        qrisp.mcx([a, b], phase_oracle)
        h(a)
        h(b)
        qrisp.mcx([a, b], phase_oracle)
        qrisp.swap(a, b)


@qrisp.gate_wrap(name='rCh')
def recip_choose_gate(a, b, c, phase_oracle:qrisp.Qubit):
    """
    Applies the multi-qubit (and single-bit) variant of the reciprocal choose() gate
    """
    if isinstance(c, qrisp.Qubit):
        _recip_choose_single_bit_gate(a, b, c, phase_oracle)
    elif isinstance(c, qrisp.QuantumVariable):
        for k in range(len(c)):
            _recip_choose_single_bit_gate(a[k], b[k], c[k], phase_oracle)
    else:
        raise Exception('Arguments a, b, c should either be all Qubit or all QuantumVariable types')

@qrisp.gate_wrap(name='rCh_1')
def recip_choose_first_order_gate(a, b, c):
    """
    Applies the circuit for the **first order** reciprocal choose() gate

    An optimization of the reciprocal choose gate, got by dropping the second half of the circuit. This optimization should only be enabled in the appropriate context: in some cases, after applying this gate, only the 'c' qubit (which references the output of the Ch() function) is used before uncomputing (by applying the inverse reciprocal choose gate). In this case, the second half of the reciprocal choose circuit is superfluous, because it change qubits 'a' and 'b' only and this change gets immediately reversed by the uncompute.
    """
    qrisp.cx(b, c)
