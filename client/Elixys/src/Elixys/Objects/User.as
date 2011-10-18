package Elixys.Objects
{
	
	import flash.utils.flash_proxy;
	
	public class User extends JSONObject
	{
		// Constructor
		public function User(data:String, existingcontent:Object = null)
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
		public function Username():String
		{
			return super.flash_proxy::getProperty("username");
		}
		public function FirstName():String
		{
			return super.flash_proxy::getProperty("firstname");
		}
		public function LastName():String
		{
			return super.flash_proxy::getProperty("lastname");
		}
		public function AccessLevel():String
		{
			return super.flash_proxy::getProperty("accesslevel");
		}

		// Type
		static public var TYPE:String = "user";
	}
}

