package Elixys.JSON.State
{
	import Elixys.JSON.JSONObject;
	
	import flash.utils.flash_proxy;
	
	public class RunState extends JSONObject
	{
		// Constructor
		public function RunState(data:String, existingcontent:Object = null)
		{
			// Call the base constructor
			super(data, existingcontent);
			
			// Validate the object type
			if ((Type != null) && (Type != TYPE))
			{
				throw new Error("Object type mismatch");
			}
		}
		
		// Static type
		public static function get TYPE():String
		{
			return "runstate";
		}

		// Data wrappers
		public function get Status():String
		{
			return super.flash_proxy::getProperty("status");
		}
		public function get Description():String
		{
			return super.flash_proxy::getProperty("description");
		}
		public function get Username():String
		{
			return super.flash_proxy::getProperty("username");
		}
		public function get SequenceID():uint
		{
			return super.flash_proxy::getProperty("sequenceid");
		}
		public function get ComponentID():uint
		{
			return super.flash_proxy::getProperty("componentid");
		}
		public function get PromptState():Elixys.JSON.State.PromptState
		{
			// Parse the prompt state
			if (m_pPromptState == null)
			{
				m_pPromptState = new Elixys.JSON.State.PromptState(null, super.flash_proxy::getProperty("prompt"));
			}
			return m_pPromptState;
		}
		public function get Time():String
		{
			return super.flash_proxy::getProperty("time");
		}
		public function get TimeDescription():String
		{
			return super.flash_proxy::getProperty("timedescription");
		}
		public function get UserAlert():String
		{
			return super.flash_proxy::getProperty("useralert");
		}
		public function get UnitOperationButton():Button
		{
			// Parse the button
			if (m_pUnitOperationButton == null)
			{
				m_pUnitOperationButton = new Button(null, super.flash_proxy::getProperty("unitoperationbutton"));
			}
			return m_pUnitOperationButton;
		}
		public function get WaitingForUserInput():Boolean
		{
			return super.flash_proxy::getProperty("waitingforuserinput");
		}
		public function get RunComplete():Boolean
		{
			return super.flash_proxy::getProperty("runcomplete");
		}
		
		// Run state comparison function.  Returns true if the run states are equal, false otherwise.
		public static function CompareRunStates(pRunStateA:RunState, pRunStateB:RunState):Boolean
		{
			if (pRunStateA.Status != pRunStateB.Status)
			{
				return false;
			}
			if (pRunStateA.Description != pRunStateB.Description)
			{
				return false;
			}
			if (pRunStateA.Username != pRunStateB.Username)
			{
				return false;
			}
			if (pRunStateA.SequenceID != pRunStateB.SequenceID)
			{
				return false;
			}
			if (pRunStateA.ComponentID != pRunStateB.ComponentID)
			{
				return false;
			}
			if (!PromptState.ComparePromptStates(pRunStateA.PromptState, pRunStateB.PromptState))
			{
				return false;
			}
			if (pRunStateA.Time != pRunStateB.Time)
			{
				return false;
			}
			if (pRunStateA.TimeDescription != pRunStateB.TimeDescription)
			{
				return false;
			}
			if (pRunStateA.UserAlert != pRunStateB.UserAlert)
			{
				return false;
			}
			if (!Button.CompareButtons(pRunStateA.UnitOperationButton, pRunStateB.UnitOperationButton))
			{
				return false;
			}
			if (pRunStateA.WaitingForUserInput != pRunStateB.WaitingForUserInput)
			{
				return false;
			}
			if (pRunStateA.RunComplete != pRunStateB.RunComplete)
			{
				return false;
			}
			return true;
		}

		// State components
		protected var m_pPromptState:Elixys.JSON.State.PromptState;
		protected var m_pUnitOperationButton:Button;
	}
}
