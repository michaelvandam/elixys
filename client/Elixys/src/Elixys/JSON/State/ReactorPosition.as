package Elixys.JSON.State
{
	import Elixys.JSON.JSONObject;

	import flash.utils.flash_proxy;
	
	public class ReactorPosition extends JSONObject
	{
		// Constructor
		public function ReactorPosition(data:String, existingcontent:Object = null)
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
			return "reactorposition";
		}

		// Data wrappers
		public function get Horizontal():String
		{
			return super.flash_proxy::getProperty("horizontal");
		}
		public function get Vertical():String
		{
			return super.flash_proxy::getProperty("vertical");
		}
	}
}
