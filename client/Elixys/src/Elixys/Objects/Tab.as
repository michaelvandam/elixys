package Elixys.Objects
{
	import Elixys.JSONObject;
	
	import flash.utils.flash_proxy;
	
	public class Tab extends JSONObject
	{
		// Constructor
		public function Tab(data:String, existingcontent:Object = null)
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
		public function Text():String
		{
			return super.flash_proxy::getProperty("text");
		}
		public function ID():String
		{
			return super.flash_proxy::getProperty("id");
		}
		
		// Type
		static public var TYPE:String = "tab";
	}
}
