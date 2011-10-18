package Elixys.Objects
{
	import flash.utils.flash_proxy;
	
	public class ReactorPosition extends JSONObject
	{
		// Constructor
		public function ReactorPosition(data:String, existingcontent:Object = null)
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
		public function Horizontal():String
		{
			return super.flash_proxy::getProperty("horizontal");
		}
		public function Vertical():String
		{
			return super.flash_proxy::getProperty("vertical");
		}
		
		// Type
		static public var TYPE:String = "reactorposition";
	}
}
