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


@qrisp.gate_wrap(name='Maj')
def majority_gate(a, b, c):
    qrisp.cx(c, a)
    qrisp.cx(c, b)
    for k in range(len(c)):
        qrisp.mcx([a[k], b[k]], c[k])

@qrisp.gate_wrap(name='rMaj')
def recip_majority_gate(a:qrisp.Qubit, b:qrisp.Qubit, c:qrisp.Qubit, phase_oracle:qrisp.Qubit):
    qrisp.cx(a, c)
    qrisp.cx(b, c)
    with qrisp.control(c):
        qrisp.mcx([a, b], phase_oracle)
        h(a)
        h(b)
        qrisp.mcx([a, b], phase_oracle)
        qrisp.swap(a, b)
