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
from qframe.core.qframe_variable import QFrameVariable
from qframe.core.operation_wrapper import OperationWrapper
from qframe.core.qframe_session import QFrameSession

class QFrameUInt(QFrameVariable):
    def __init__(self, size, qfs=None, name=None):
        super().__init__(size, qfs, name)
        self.qv = qrisp.QuantumFloat(size, name=name)

    def __iadd__(self, other):
        from qframe.alg_primitives.adder import recip_adder_gate
        if isinstance(other, QFrameUInt):
            if self.qfs != other.qfs:
                self.qfs.merge(other.qfs)
            opw = OperationWrapper()
            def _gate_apply_impl(qfs: QFrameSession):
                self.qv += other.qv
            def _calculate_impl(arg_dict:dict):
                arg_dict[self] += arg_dict[other]
            opw.set_gate_apply_impl(_gate_apply_impl)
            opw.set_recip_gate_apply_impl(lambda qfs: recip_adder_gate(other.qv, self.qv, qfs.recip_carry_anc, qfs.phase_anc))
            opw.set_calculate_impl(_calculate_impl)
            self.qfs.append_operation_wrapper(opw)
        return self
