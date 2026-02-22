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
from collections.abc import Callable
import z3

from qframe.core.operation_wrapper import OperationWrapper
from qframe.core.qframe_session import QFrameSession
from qframe.core.qframe_variable import QFrameVariable


def _bit(b, j):
    return ((0b1 << j) & b) >> j

def _rotr(x, n, w):
    """Rotate 'n' bits right"""
    n = n % w
    mask = (0b1 << w) - 1
    return ((x << (w - n)) | (x >> n)) & mask


class Rotr:
    def __init__(self, width:int, rotr_list:list[int], shr_list:list[int]= []):
        self.width = width
        self.rotr_list = rotr_list
        self.shr_list = shr_list
        # Calculate the required inverse functions
        self.inv_sigma_table   = self._solve_for_inverse_func(self._inv_sigma_z3)
        self.recip_sigma_table = self._solve_for_inverse_func(self._recip_sigma_z3)

    def _solve_for_inverse_func(self, sigma_func: Callable) -> list:
        # Set up the system of equations to solve using Microsoft's z3
        z3_solver = z3.Solver()
        inv_x = list()
        for i in range(self.width):
            inv_x.append(z3.BitVec(f'x{i}', self.width))
        for i in range(self.width):
            z3_solver.add(sigma_func(inv_x[i]) == (1 << i))
        z3_solver.check()
        res = z3_solver.model()
        # Initialize the inverter table
        inv_sigma_table = list()
        for i in range(self.width):
            inv_sigma_table.append(res[inv_x[i]].as_long())
        return inv_sigma_table

    def _inv_sigma_z3(self, x: z3.BitVec):
        res = z3.RotateRight(x, self.rotr_list[0])
        for k in range(1, len(self.rotr_list)):
            res ^= z3.RotateRight(x, self.rotr_list[k])
        for k in range(len(self.shr_list)):
            res ^= z3.LShR(x, self.shr_list[k])
        return res

    def _recip_sigma_z3(self, kappa):
        res = z3.RotateLeft(kappa, self.rotr_list[0])  # In reciprocal space, RotateRight becomes RotateLeft
        for k in range(1, len(self.rotr_list)):
            res ^= z3.RotateLeft(kappa, self.rotr_list[k])  # In reciprocal space, RotateRight becomes RotateLeft
        for k in range(len(self.shr_list)):
            res ^= (kappa << self.shr_list[k] )  # In reciprocal space, 'shift right' becomes 'shift left'
        return res

    def rotr_function(self, x: int) -> int:
        result = 0
        for k in range(len(self.rotr_list)):
            result ^= _rotr(x, self.rotr_list[k], self.width)
        for k in range(len(self.shr_list)):
            result ^= (x >> self.shr_list[k])
        return result

    def inv_rotr_function(self, x: int) -> int:
        x_inv = 0
        for i in range(self.width):
            if x & (0b1 << i):
                x_inv ^= self.inv_sigma_table[i]
        return x_inv

    def recip_rotr_function(self, x: int) -> int:
        x_inv = 0
        for i in range(self.width):
            if x & (0b1 << i):
                x_inv ^= self.recip_sigma_table[i]
        return x_inv

    def recip_inv_rotr_function(self, x: int) -> int:
        mask = (0b1 << self.width) - 1
        result = 0
        for k in range(len(self.rotr_list)):
            result ^= _rotr(x, -self.rotr_list[k], self.width)  # Negative rotr()
        for k in range(len(self.shr_list)):
            result ^= (x << self.shr_list[k]) & mask
        return result

    @qrisp.gate_wrap(name='Rotr')
    def rotr_gate(self, x: qrisp.QuantumVariable, anc: qrisp.QuantumVariable, clean_up=True, no_swap=False):
        n_qubit = len(x)
        # Parameter validation
        if n_qubit != self.width:
            raise Exception(f'Size of quantum variable x must equal the bit width of this Rotr instance')
        if len(anc) != self.width:
            raise Exception(f'Size of anc argument must equal the bit width of this Rotr instance')
        # Apply circuit for: rotr_function(x) -> anc
        for j in range(len(x)):
            for k in range(len(self.rotr_list)):
                jj = (j + self.rotr_list[k] ) % n_qubit
                qrisp.cx(x[jj], anc[j])
            for k in range(len(self.shr_list)):
                jj = j + self.shr_list[k]
                if jj < n_qubit:
                    qrisp.cx(x[jj], anc[j])
        if clean_up:
            # Clean up the untransformed value in the 'x' quantum variable (uncompute to 0)
            for i in range(len(anc)):
                xor_layer = self.inv_sigma_table[i]
                for j in range(len(x)):
                    if _bit(xor_layer, j):
                        qrisp.cx(anc[i], x[j])
        if not no_swap:
            # Swap x <--> anc
            qrisp.swap(x, anc)

    @qrisp.gate_wrap(name='rRotr')
    def recip_rotr_gate(self, x: qrisp.QuantumVariable, anc: qrisp.QuantumVariable, clean_up=True, no_swap=False):
        n_qubit = len(x)
        # Parameter validation
        if n_qubit != self.width:
            raise Exception(f'Size of quantum variable x must equal the bit width of this Rotr instance')
        if len(anc) != self.width:
            raise Exception(f'Size of anc argument must equal the bit width of this Rotr instance')
        # Apply circuit for: recip_rotr_function(x) -> anc
        for i in range(len(x)):
            xor_layer = self.recip_sigma_table[i]
            for j in range(len(anc)):
                if _bit(xor_layer, j):
                    qrisp.cx(x[i], anc[j])
        if clean_up:
            # Clean up the untransformed value in the 'x' quantum variable (uncompute to 0)
            for j in range(len(anc)):
                for k in range(len(self.shr_list)):
                    jj = j - self.shr_list[k]
                    if jj >= 0:
                        qrisp.cx(anc[jj], x[j])
                for k in range(len(self.rotr_list)):
                    jj = (j - self.rotr_list[k]) % n_qubit
                    qrisp.cx(anc[jj], x[j])
        if not no_swap:
            # Swap x <--> anc - noting that the reciprocal of 'swap' is 'swap'
            qrisp.swap(x, anc)

    def shift(self, x: QFrameVariable):
        return ShiftOperationWrapper(self, x, conjugate_me=True)

    def shift_inline(self, x: QFrameVariable):
        # Meant to be used on a line by itself, not in a += expression
        opw = ShiftInlineOperationWrapper(self, x, conjugate_me=False)
        x.qfs.append_operation_wrapper(opw)


class ShiftOperationWrapper(OperationWrapper):
    def __init__(self, r: Rotr, x_qfv: QFrameVariable, conjugate_me):
        super().__init__(conjugate_me)
        self.r = r
        self.x_qfv: QFrameVariable = x_qfv

    def merge_qfs(self, other_qfs= None):
        if other_qfs is not None:
            self.x_qfv.qfs.merge(other_qfs)

    def check_compatibility(self, other_qfv: QFrameVariable):
        if self.x_qfv == other_qfv:
            raise Exception("Incompatible operands: Cannot combine a quantum variable with a function of itself")

    def gate_apply(self, qfs: QFrameSession) -> None:
        self.r.rotr_gate(self.x_qfv.qv, qfs._register_anc)
        self._gate_result_qfv = self.x_qfv

    def recip_gate_apply(self, qfs: QFrameSession) -> None:
        self.r.recip_rotr_gate(self.x_qfv.qv, qfs._register_anc)
        self._recip_gate_result_qfv = self.x_qfv

    def calculate(self, arg_dict: dict):
        return self.r.rotr_function(arg_dict[self.x_qfv])

class ShiftInlineOperationWrapper(ShiftOperationWrapper):
    def calculate(self, arg_dict: dict):
        arg_dict[self.x_qfv] = self.r.rotr_function(arg_dict[self.x_qfv])
