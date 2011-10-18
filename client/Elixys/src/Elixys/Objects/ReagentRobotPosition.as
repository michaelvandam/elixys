package Elixys.Objects
{
	import flash.utils.flash_proxy;
	
	public class ReagentRobotPosition extends JSONObject
	{
		// Constructor
		public function ReagentRobotPosition(data:String, existingcontent:Object = null)
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
		public function Delivery():uint
		{
			return super.flash_proxy::getProperty("delivery");
		}
		public function Reagent():uint
		{
			return super.flash_proxy::getProperty("rawy");
		}
		public function Cassette():uint
		{
			return super.flash_proxy::getProperty("cassette");
		}
		
		// Type
		static public var TYPE:String = "reagentrobotposition";
	}
}
