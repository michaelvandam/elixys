package Elixys.JSON.State
{
	import Elixys.JSON.JSONObject;
	
	import flash.utils.flash_proxy;
	
	public class Button extends JSONObject
	{
		// Constructor
		public function Button(data:String, existingcontent:Object = null)
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
			return "button";
		}

		// Data wrappers
		public function get Text():String
		{
			return super.flash_proxy::getProperty("text");
		}
		public function get ID():String
		{
			return super.flash_proxy::getProperty("id");
		}
	}
}
