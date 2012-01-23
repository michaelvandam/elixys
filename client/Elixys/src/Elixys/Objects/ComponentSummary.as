package Elixys.Objects
{
	import flash.utils.flash_proxy;
	
	public class ComponentSummary extends Component
	{
		// Constructor
		public function ComponentSummary(data:String = null, existingcontent:Object = null)
		{
			// Call the base constructor
			if ((data == null) && (existingcontent == null))
			{
				data = DEFAULT;
			}
			super(data, existingcontent);
			
			// Validate the object type
			if ((ComponentType != null) && (ComponentType != TYPE))
			{
				throw new Error("State object mismatch");
			}
		}

		// Data wrappers
		public function get SuccessFlag():uint
		{
			return super.flash_proxy::getProperty("successflag");
		}

		public function get Message():String
		{
			return super.flash_proxy::getProperty("message");
		}

		// Type
		static public var TYPE:String = "SUMMARY";

		// Default format
		static public var DEFAULT:String = "{}";
	}
}
