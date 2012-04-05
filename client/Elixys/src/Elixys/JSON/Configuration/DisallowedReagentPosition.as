package Elixys.JSON.Configuration
{
	import Elixys.JSON.JSONObject;
	
	import flash.utils.flash_proxy;
	
	public class DisallowedReagentPosition extends JSONObject
	{
		// Constructor
		public function DisallowedReagentPosition(data:String, existingcontent:Object = null)
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
			return "disallowedreagentposition";
		}

		// Data wrappers
		public function get Cassette():int
		{
			return super.flash_proxy::getProperty("cassette");
		}
		public function get Reagent():int
		{
			return super.flash_proxy::getProperty("reagent");
		}
	}
}
