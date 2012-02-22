package Elixys.JSON.State
{
	import Elixys.JSON.JSONObject;

	import flash.utils.flash_proxy;
	
	public class User extends JSONObject
	{
		// Constructor
		public function User(data:String, existingcontent:Object = null)
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
			return "user";
		}

		// Data wrappers
		public function get Username():String
		{
			return super.flash_proxy::getProperty("username");
		}
		public function get FirstName():String
		{
			return super.flash_proxy::getProperty("firstname");
		}
		public function get LastName():String
		{
			return super.flash_proxy::getProperty("lastname");
		}
		public function get AccessLevel():String
		{
			return super.flash_proxy::getProperty("accesslevel");
		}
	}
}

