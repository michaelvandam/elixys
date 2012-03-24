package Elixys.JSON.Components
{
	import Elixys.JSON.JSONObject;
	
	import flash.utils.flash_proxy;
	
	public class ComponentPrompt extends ComponentBase
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
			if ((ComponentType != null) && (ComponentType != COMPONENTTYPE))
			{
				throw new Error("State object mismatch");
			}
		}

		// Static component type and skins
		public static function get COMPONENTTYPE():String
		{
			return "PROMPT";
		}
		public static function get SKINUP():Class
		{
			return tools_prompt_up;
		}
		public static function get SKINDOWN():Class
		{
			return tools_prompt_down;
		}
		public static function get SKINDISABLED():Class
		{
			return tools_prompt_disabled;
		}
		public static function get SKINACTIVE():Class
		{
			return tools_prompt_active;
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

		// Default format
		static public var DEFAULT:String = "{" +
			"\"type\":\"component\"," +
			"\"componenttype\":\"PROMPT\"," +
			"\"id\":0," +
			"\"name\":\"Prompt\"," +
			"\"message\":\"\"}";
	}
}
