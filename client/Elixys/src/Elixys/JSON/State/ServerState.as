package Elixys.JSON.State
{
	import Elixys.JSON.JSONObject;

	import flash.utils.flash_proxy;
	
	public class ServerState extends JSONObject
	{
		// Constructor
		public function ServerState(data:String, existingcontent:Object = null)
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
			return "serverstate";
		}

		// Data wrappers
		public function get RunState():Elixys.JSON.State.RunState
		{
			// Parse the run state
			if (m_pRunState == null)
			{
				m_pRunState = new Elixys.JSON.State.RunState(null, super.flash_proxy::getProperty("runstate"));
			}
			return m_pRunState;
		}
		public function get HardwareState():Elixys.JSON.State.HardwareState
		{
			// Parse the hardware state
			if (m_pHardwareState == null)
			{
				m_pHardwareState = new Elixys.JSON.State.HardwareState(null, super.flash_proxy::getProperty("hardwarestate"));
			}
			return m_pHardwareState;
		}

		// State components
		private var m_pRunState:Elixys.JSON.State.RunState;
		private var m_pHardwareState:Elixys.JSON.State.HardwareState;
	}
}
