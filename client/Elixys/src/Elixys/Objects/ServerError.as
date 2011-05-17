package Elixys.Objects
{
	import Elixys.JSONObject;
	
	import flash.utils.flash_proxy;

	public class ServerError extends JSONObject
	{
		// Constructor
		public function ServerError(data:String = null)
		{
			// Call the base constructor
			super(data);
			
			// Validate the object type
			if (data != null)
			{
				if (Type() != TYPE)
				{
					throw new Error("Object type mismatch");
				}
			}
		}

		// Data wrappers
		public function Type():String
		{
			return super.flash_proxy::getProperty("type");
		}
		public function Description():String
		{
			return super.flash_proxy::getProperty("description");
		}
			
		// Type
		static public var TYPE:String = "error";
	}
}