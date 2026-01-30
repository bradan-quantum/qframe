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

def _bit(b, j):
    return ((0b1 << j) & b) >> j

def _rotr(x, n, w):
    """Rotate 'n' bits right"""
    n = n % w
    mask = (0b1 << w) - 1
    return ((x << (w - n)) | (x >> n)) & mask


class Rotr:
    def __init__(self, width:int, rotr_list:list[int], shr_list:list[int]= None):
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
        if self.shr_list is not None:
            for k in range(len(self.shr_list)):
                res ^= x >> self.shr_list[k]
        return res

    def _recip_sigma_z3(self, kappa):
        res = z3.RotateRight(kappa, self.rotr_list[0])
        for k in range(1, len(self.rotr_list)):
            res ^= z3.RotateLeft(kappa, self.rotr_list[k])  # In reciprocal space, RotateRight becomes RotateLeft
        # ToDo: Don't yet know how to code the reciprocal SHR() operation!
        # ...
        return res

    def rotr_function(self, x: int) -> int:
        result = 0
        for k in range(len(self.rotr_list)):
            result ^= _rotr(x, self.rotr_list[k], self.width)
        if self.shr_list is not None:
            for k in range(len(self.shr_list)):
                result ^= (x >> self.shr_list[k])
        return result

    def inv_rotr_function(self, x: int) -> int:
        x_inv = 0
        for i in range(self.width):
            if x & (0b1 << i):
                x_inv ^= self.inv_sigma_table[i]
        return x_inv


