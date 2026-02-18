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

from qframe.core.qframe_uint import QFrameUInt


class Test_QFS_Adder:
    def test_qfs_adder(self):
        v1 = QFrameUInt(4, name='v1')
        v2 = QFrameUInt(4, name='v2')

        v1 += v2

        # # Initialize variables
        # v1.qv[:] = 3
        # v2.qv[:] = 7

        # qfs = v1.qfs
        # qfs.apply_oracle_gate(target_dict={v1: 10})
        # qfs.apply_recip_oracle_gate()

        # print(v1.qv.qs)
        # print(f'calculate(v1: 3, v2: 7) = {qfs.calculate({v1: 3, v2: 7})}')
        # # print(v1.qv)


        # Get the QFrameSession object
        qfs = v1.qfs

        # Prepare the quantum state in an equal-weighted superposition (Walsh-Hadamard transform)
        h(v1.qv)
        h(v2.qv)

        qrisp.barrier(v1.qv[:] + v2.qv[:])

        # Single partial oracle iteration
        with qrisp.conjugate(qfs.apply_oracle_gate)(target_dict={v1: 10}):
            qrisp.barrier(v1.qv[:] + v2.qv[:])
            qrisp.s(v1.qv)
            qrisp.barrier(v1.qv[:] + v2.qv[:])
        qrisp.barrier(v1.qv[:] + v2.qv[:])
        h(v1.qv)
        h(v2.qv)
        qrisp.barrier(v1.qv[:] + v2.qv[:])
        with qrisp.conjugate(qfs.apply_recip_oracle_gate)():
            qrisp.barrier(v1.qv[:] + v2.qv[:])
            qrisp.s(v1.qv)
            qrisp.barrier(v1.qv[:] + v2.qv[:])
        h(v2.qv)
        h(v1.qv)

        # Show the circuit
        print(v1.qv.qs)
        # Show result
        print(qrisp.multi_measurement([v1.qv, v2.qv]))
