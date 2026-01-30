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

from qframe.alg_primitives.rotr import Rotr


@pytest.fixture
def rotr_instance():
    pass


class Test_Rotr:
    def test_rotr_inv_func(self):
        r = Rotr(8, [0, 1, 3])
        # for i in range(16):
        #     print(f'{i} : {r.rotr_function(i)}, {r.inv_rotr_function(r.rotr_function(i))}')
        for x in range(2**8):
            assert x == r.inv_rotr_function( r.rotr_function(x) )
