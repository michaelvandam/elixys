# To change this template, choose Tools | Templates
# and open the template in the editor.


    def _setstate(self, state):
        if not isinstance(state,State):
            raise StateMachineError("Invalid State not State Type")
        self.substate.exit()
        self.substate = state
        self.substate.enter()
        self.substate.update()

    def _getstate(self):
        return self._current_state

    substate = property(_getstate,_setstate)