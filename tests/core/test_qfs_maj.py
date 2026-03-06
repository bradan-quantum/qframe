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


class Test_QFS_Majority:
    def test_qfs_majority(self):
        width = 4
        v1 = QFrameUInt(width, name='v1')
        v2 = QFrameUInt(width, name='v2')
        v3 = QFrameUInt(width, name='v3')
        v4 = QFrameUInt(width, name='v4')

        # Define algorithm using QFrame
        v1 += qframe.maj(v2, v3, v4)

        # Get the QFrameSession object
        qfs = v1.qfs

        # qfs.apply_oracle_gate()
        # print(v1.qv.qs)

        seed_args = {v1: 0, v2: 6, v3: 7, v4: 8}
        target = qfs.calculate(seed_args, raw_result=True)
        print(f'calculate(v1: 0, v2: 6, v3: 7, v4: 8) = {qfs.calculate(seed_args)}')

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
        result_dict = qrisp.multi_measurement([v1.qv, v2.qv, v3.qv, v4.qv])
        print(result_dict)

        for result_tuple in result_dict:
            (v1_res, v2_res, v3_res, v4_res) = result_tuple
            assert target == qfs.calculate({v1: v1_res, v2: v2_res, v3: v3_res, v4: v4_res}, raw_result=True)
