package Elixys.Objects
{
	import flash.utils.flash_proxy;
	
	public class ReagentRobotState extends JSONObject
	{
		// Constructor
		public function ReagentRobotState(data:String, existingcontent:Object = null)
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
		public function Gripper():String
		{
			return super.flash_proxy::getProperty("gripper");
		}
		public function Actuator():String
		{
			return super.flash_proxy::getProperty("actuator");
		}
		public function Position():ReagentRobotPosition
		{
			// Parse the reagent robot position
			if (m_pReagentRobotPosition == null)
			{
				m_pReagentRobotPosition = new ReagentRobotPosition(null, super.flash_proxy::getProperty("position"));
			}
			return m_pReagentRobotPosition;
		}
		
		// Type
		static public var TYPE:String = "reagentrobotstate";

		// State components
		private var m_pReagentRobotPosition:ReagentRobotPosition = null;
	}
}
