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
from qframe.core.qframe_session import QFrameSession
from qframe.core.qframe_variable import QFrameVariable

class OperationWrapper:
    def __init__(self, conjugate_me=False):
        self.conjugate_me = conjugate_me
        self._gate_apply_impl = None
        self._gate_result_qfv: QFrameVariable = None
        self._recip_gate_apply_impl = None
        self._recip_gate_result_qfv: QFrameVariable = None
        self._calculate_impl = None

    def merge_qfs(self, other_qfs=None):
        # Override this method when necessary
        pass

    # Gate methods/properties
    def gate_apply(self, qfs: QFrameSession) -> None:
        self._gate_result_qfv = self._gate_apply_impl(qfs)

    def set_gate_apply_impl(self, gate_apply_impl) -> None:
        self._gate_apply_impl = gate_apply_impl

    @property
    def gate_result_qfv(self):
        return self._gate_result_qfv

    # Reciprocal gate methods/properties
    def recip_gate_apply(self, qfs: QFrameSession) -> None:
        self._recip_gate_result_qfv = self._recip_gate_apply_impl(qfs)

    def set_recip_gate_apply_impl(self, recip_gate_apply_impl) -> None:
        self._recip_gate_apply_impl = recip_gate_apply_impl

    @property
    def recip_gate_result_qfv(self):
        return self._recip_gate_result_qfv

    # Classical function methods/properties
    def calculate(self, arg_dict: dict):
        """Returns the result of the classical calculation"""
        return self._calculate_impl(arg_dict)

    def set_calculate_impl(self, calculate_impl):
        self._calculate_impl = calculate_impl
