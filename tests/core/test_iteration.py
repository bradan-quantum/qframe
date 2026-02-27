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


class Test_Iteration:
    def test_iteration(self):
        v1 = QFrameUInt(4, name='v1')
        v2 = QFrameUInt(4, name='v2')

        # Define the algorithm
        v1 += v2
        v1 += 3

        # Get the QFrameSession object
        qfs = v1.qfs

        seed_args = {v1: 3, v2: 7}
        target = qfs.calculate(seed_args, raw_result=True)
        print(f'\n\ncalculate(v1: {seed_args[v1]}, v2: {seed_args[v2]}) = {qfs.calculate(seed_args)}')

        # Prepare the quantum state
        h(v1.qv)
        h(v2.qv)

        qfs.partial_oracle_iteration(target)

        print(v1.qv.qs)
        print(qrisp.multi_measurement([v1.qv, v2.qv]))
