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
		public function Position():String
		{
			return super.flash_proxy::getProperty("position");
		}
		public function RawX():String
		{
			return super.flash_proxy::getProperty("rawx");
		}
		public function RawY():String
		{
			return super.flash_proxy::getProperty("rawy");
		}
		public function Actuator():String
		{
			return super.flash_proxy::getProperty("actuator");
		}
		public function Gripper():String
		{
			return super.flash_proxy::getProperty("gripper");
		}
		
		// Type
		static public var TYPE:String = "reagentrobotstate";
	}
}
