package Elixys.JSON.State
{
	import Elixys.JSON.JSONObject;

	import flash.utils.flash_proxy;
	
	public class ReagentRobotPosition extends JSONObject
	{
		// Constructor
		public function ReagentRobotPosition(data:String, existingcontent:Object = null)
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
			return "reagentrobotposition";
		}

		// Data wrappers
		public function get Name1():String
		{
			return super.flash_proxy::getProperty("name1");
		}
		public function get Name2():String
		{
			return super.flash_proxy::getProperty("name2");
		}
	}
}
