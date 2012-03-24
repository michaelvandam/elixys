package Elixys.JSON.State
{
	import Elixys.JSON.JSONObject;
	
	import flash.utils.flash_proxy;
	
	public class ServerError extends JSONObject
	{
		// Constructor
		public function ServerError(data:String, existingcontent:Object = null)
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
			return "error";
		}
		
		// Data wrappers
		public function get Description():String
		{
			return super.flash_proxy::getProperty("description");
		}
	}
}
