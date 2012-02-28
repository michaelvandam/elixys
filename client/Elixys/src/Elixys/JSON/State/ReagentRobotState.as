package Elixys.JSON.State
{
	import Elixys.JSON.JSONObject;

	import flash.utils.flash_proxy;
	
	public class ReagentRobotState extends JSONObject
	{
		// Constructor
		public function ReagentRobotState(data:String, existingcontent:Object = null)
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
			return "reagentrobotstate";
		}

		// Data wrappers
		public function get Gripper():String
		{
			return super.flash_proxy::getProperty("gripper");
		}
		public function get GripperActuator():String
		{
			return super.flash_proxy::getProperty("gripperactuator");
		}
		public function get GasTransferActuator():String
		{
			return super.flash_proxy::getProperty("gastransferactuator");
		}
		public function get Position():ReagentRobotPosition
		{
			// Parse the reagent robot position
			if (m_pReagentRobotPosition == null)
			{
				m_pReagentRobotPosition = new ReagentRobotPosition(null, super.flash_proxy::getProperty("position"));
			}
			return m_pReagentRobotPosition;
		}
		
		// State components
		protected var m_pReagentRobotPosition:ReagentRobotPosition;
	}
}
