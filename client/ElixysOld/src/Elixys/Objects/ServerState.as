package Elixys.Objects
{
	import flash.utils.flash_proxy;
	
	public class ServerState extends JSONObject
	{
		// Constructor
		public function ServerState(data:String, existingcontent:Object = null)
		{
			// Call the base constructor
			super(data, existingcontent);
			
			// Validate the object type
			if ((Type() != null) && (Type() != TYPE))
			{
				throw new Error("Object type mismatch");
			}
		}
		
		// Data wrappers
		public function Type():String
		{
			return super.flash_proxy::getProperty("type");
		}
		public function RunState():Elixys.Objects.RunState
		{
			// Parse the run state
			if (m_pRunState == null)
			{
				m_pRunState = new Elixys.Objects.RunState(null, super.flash_proxy::getProperty("runstate"));
			}
			return m_pRunState;
		}
		public function HardwareState():Elixys.Objects.HardwareState
		{
			// Parse the hardware state
			if (m_pHardwareState == null)
			{
				m_pHardwareState = new Elixys.Objects.HardwareState(null, super.flash_proxy::getProperty("hardwarestate"));
			}
			return m_pHardwareState;
		}

		// Type
		static public var TYPE:String = "serverstate";
		
		// State components
		private var m_pRunState:Elixys.Objects.RunState = null;
		private var m_pHardwareState:Elixys.Objects.HardwareState = null;
	}
}
