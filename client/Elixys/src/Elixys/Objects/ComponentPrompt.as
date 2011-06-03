package Elixys.Objects
{
	import flash.utils.flash_proxy;
	
	public class ComponentPrompt extends Component
	{
		// Constructor
		public function ComponentPrompt(data:String = null, existingcontent:Object = null)
		{
			// Call the base constructor
			super(data, existingcontent);
			
			// Validate the object type
			if ((ComponentType != null) && (ComponentType != TYPE))
			{
				throw new Error("State object mismatch");
			}
		}

		// Data wrappers
		public function get Message():String
		{
			return super.flash_proxy::getProperty("message");
		}
		public function set Message(value:String):void
		{
			super.flash_proxy::setProperty("message", value);
		}
		
		public function get MessageDescription():String
		{
			return super.flash_proxy::getProperty("messagedescription");
		}
		public function set MessageDescription(value:String):void
		{
			super.flash_proxy::setProperty("messagedescription", value);
		}

		public function get MessageValidation():String
		{
			return super.flash_proxy::getProperty("messagevalidation");
		}
		public function set MessageValidation(value:String):void
		{
			super.flash_proxy::setProperty("messagevalidation", value);
		}

		// Format additional component details
		protected override function FormatComponentDetails():String
		{
			return JSONDataString("message", Message, false);
		}

		// Type
		static public var TYPE:String = "PROMPT";
	}
}
