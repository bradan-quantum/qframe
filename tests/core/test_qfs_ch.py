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
import qframe


class Test_QFS_Choose:
    def test_qfs_choose(self):
        v1 = QFrameUInt(4, name='v1')
        v2 = QFrameUInt(4, name='v2')
        v3 = QFrameUInt(4, name='v3')
        v4 = QFrameUInt(4, name='v4')

        v2 += v1
        v2 += qframe.ch(v1, v3, v4)

        # Get the QFrameSession object
        qfs = v1.qfs

        # qfs.apply_oracle_gate()
        # print(v1.qv.qs)

        # seed_args = {v1: 0, v2: 6, v3: 7, v4: 8}
        seed_args = {v1: 5, v2: 11, v3: 5, v4: 12}
        target = qfs.calculate(seed_args, raw_result=True)
        # print(f'calculate(v1: 0, v2: 6, v3: 7, v4: 8) = {qfs.calculate(seed_args)}')
        print(f'calculate(v1: 5, v2: 11, v3: 5, v4: 12) = {qfs.calculate(seed_args)}')

        # Prepare the quantum state in an equal-weighted superposition (Walsh-Hadamard transform)
        h(v1.qv)
        h(v2.qv)
        h(v3.qv)
        h(v4.qv)

        qrisp.barrier(v1.qv[:] + v2.qv[:] + v3.qv[:] + v4.qv[:])

        # Single partial oracle iteration
        with qrisp.conjugate(qfs.apply_oracle_gate)(target_dict=target):
            qrisp.barrier(v1.qv[:] + v2.qv[:] + v3.qv[:] + v4.qv[:])
            qrisp.s(v1.qv)
            qrisp.s(v2.qv)
            qrisp.s(v3.qv)
            qrisp.s(v4.qv)
            qrisp.barrier(v1.qv[:] + v2.qv[:] + v3.qv[:] + v4.qv[:])
        qrisp.barrier(v1.qv[:] + v2.qv[:] + v3.qv[:] + v4.qv[:])
        h(v1.qv)
        h(v2.qv)
        h(v3.qv)
        h(v4.qv)
        qrisp.barrier(v1.qv[:] + v2.qv[:] + v3.qv[:] + v4.qv[:])
        with qrisp.conjugate(qfs.apply_recip_oracle_gate)():
            qrisp.barrier(v1.qv[:] + v2.qv[:] + v3.qv[:] + v4.qv[:])
            qrisp.s(v1.qv)
            qrisp.s(v2.qv)
            qrisp.s(v3.qv)
            qrisp.s(v4.qv)
            qrisp.barrier(v1.qv[:] + v2.qv[:] + v3.qv[:] + v4.qv[:])
        h(v4.qv)
        h(v3.qv)
        h(v2.qv)
        h(v1.qv)

        # Show the circuit
        print(v1.qv.qs)
        # Show result
        print(qrisp.multi_measurement([v1.qv, v2.qv, v3.qv, v4.qv]))
