package Elixys.Objects
{
	import flash.utils.flash_proxy;
	
	public class ComponentPrompt extends Component
	{
		// Constructor
		public function ComponentPrompt(data:String = null, existingcontent:Object = null)
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
		public function get Message():String
		{
			return super.flash_proxy::getProperty("message");
		}
		public function set Message(value:String):void
		{
			super.flash_proxy::setProperty("message", value);
		}
		
		public function get MessageValidation():String
		{
			return super.flash_proxy::getProperty("messagevalidation");
		}

		// Format additional component details
		protected override function FormatComponentDetails():String
		{
			return JSONDataString("message", Message, false);
		}

		// Type
		static public var TYPE:String = "PROMPT";

		// Default format
		static public var DEFAULT:String = "{" +
			"\"type\":\"component\"," +
			"\"componenttype\":\"PROMPT\"," +
			"\"id\":0," +
			"\"name\":\"Prompt\"," +
			"\"message\":\"\"}";
	}
}
