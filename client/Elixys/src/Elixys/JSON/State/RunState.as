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
		public function get TimerButtons():Array
		{
			// Parse the buttons
			if (m_pTimerButtons == null)
			{
				m_pTimerButtons = new Array();
				var pButtons:Array = super.flash_proxy::getProperty("timerbuttons");
				for each (var pButtonObject:Object in pButtons)
				{
					var pButton:Button = new Button(null, pButtonObject);
					m_pTimerButtons.push(pButton);
				}
			}
			return m_pTimerButtons;
		}
		public function get UnitOperationButtons():Array
		{
			// Parse the buttons
			if (m_pUnitOperationButtons == null)
			{
				m_pUnitOperationButtons = new Array();
				var pButtons:Array = super.flash_proxy::getProperty("unitoperationbuttons");
				for each (var pButtonObject:Object in pButtons)
				{
					var pButton:Button = new Button(null, pButtonObject);
					m_pUnitOperationButtons.push(pButton);
				}
			}
			return m_pUnitOperationButtons;
		}
		
		// State components
		protected var m_pPromptState:Elixys.JSON.State.PromptState;
		protected var m_pTimerButtons:Array;
		protected var m_pUnitOperationButtons:Array;
	}
}
