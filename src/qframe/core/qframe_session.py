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
import qframe

class QFrameSession:
    def __init__(self):
        self.opw_list = []
        self.qfv_list = []
        self._phase_anc = qrisp.QuantumVariable(1, name='_phase_anc')
        self._recip_carry_anc = qrisp.QuantumVariable(1, name='_recip_carry_anc')
        self._register_anc: qrisp.QuantumVariable = None

    def register_qfv(self, qfv, size):
        self.qfv_list.append(qfv)
        # Allocate a matching ancillary, in case it's needed (e.g. for reciprocal bit shift)
        if self._register_anc is not None:
            if size > self._register_anc.size:
                self._register_anc.extend(size - self._register_anc.size)
        else:
            self._register_anc = qrisp.QuantumVariable(size, name='_register_anc')

    def append_operation_wrapper(self, opw):
        self.opw_list.append(opw)

    def merge(self, qfs_other):
        if self == qfs_other:
            return

        self.opw_list.extend(qfs_other.opw_list)
        self.qfv_list.extend(qfs_other.qfv_list)
        for v in qfs_other.qfv_list:
            v.qfs = self

        # Keep the largest _register_anc variable (if any)
        if qfs_other._register_anc is not None:
            if self._register_anc is None:
                self._register_anc = qfs_other._register_anc
            elif qfs_other._register_anc.size > self._register_anc.size:
                self._register_anc = qfs_other._register_anc
                qfs_other._register_anc.delete(verify=True)

    def calculate(self, arg_dict: dict, raw_result=False):
        working_arg_dict = arg_dict.copy()
        for opw in self.opw_list:
            opw.calculate(working_arg_dict)
        if raw_result:
            return working_arg_dict
        else:
            result_dict = {}
            for qfv in working_arg_dict.keys():
                result_dict[qfv.name] = working_arg_dict[qfv]
            return result_dict

    def apply_oracle_gate(self, target_dict: dict= {}):
        # Perform gate operations
        for opw in self.opw_list:
            opw.gate_apply(self)
        # Set target values
        for key in target_dict.keys():
            target = target_dict[key]
            if isinstance(key, qframe.QFrameVariable):
                target_qv = key.qv
            elif isinstance(key, qrisp.QuantumVariable):
                target_qv = key
            else:
                raise Exception('Target keys must either be of type qframe.QFrameVariable or qrisp.QuantumVariable.')
            for i in range(target.bit_length()):
                if (target & 0b1<<i): qrisp.x(target_qv[i])

    def apply_recip_oracle_gate(self):
        # Initialize ancillary qubits for reciprocal gate
        qrisp.z(qrisp.h(self.phase_anc))
        qrisp.h(self.recip_carry_anc)
        # Perform operations
        for opw in self.opw_list:
            opw.recip_gate_apply(self)

    @property
    def phase_anc(self):
        return self._phase_anc[0]

    @property
    def recip_carry_anc(self):
        return self._recip_carry_anc[0]