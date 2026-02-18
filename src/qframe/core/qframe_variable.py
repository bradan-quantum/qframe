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

class QFrameVariable:
    def __init__(self, size, qfs: QFrameSession=None, name=None):
        if qfs is not None:
            self.qfs = qfs
        else:
            self.qfs = QFrameSession()

        self.qv = None
        self.qfs.register_qfv(self, size)
        self.size = size
        if name is not None:
            self.name = name
