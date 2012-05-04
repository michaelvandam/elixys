package Elixys.JSON.Components
{
	import Elixys.Assets.Constants;
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
		
		// Static field details
		public static var FIELDCOUNT:int = 1;
		public static var FIELDLABELS:Array = [
			"MESSAGE"
		];
		public static var FIELDTYPES:Array = [
			Constants.TYPE_MULTILINEINPUT
		];
		public static var FIELDUNITS:Array = [
			""
		];
		public static var FIELDPROPERTIES:Array = [
			"Message"
		];

		// Data wrappers
		public function get Message():String
		{
			return unescape(super.flash_proxy::getProperty("message"));
		}
		public function set Message(value:String):void
		{
			super.flash_proxy::setProperty("message", escape(value));
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

		// Component comparison function.  Returns true if the components are equal, false otherwise.
		public static function CompareComponents(pComponentA:ComponentBase, pComponentB:ComponentBase):Boolean
		{
			var pComponentPromptA:ComponentPrompt = new ComponentPrompt(null, pComponentA);
			var pComponentPromptB:ComponentPrompt = new ComponentPrompt(null, pComponentB);
			if (pComponentPromptA.Message != pComponentPromptB.Message)
			{
				return false;
			}
			return true;
		}

		// Validates the transfer component
		public override function Validate():void
		{
			m_sMessageError = ValidateField(Message, MessageValidation);
		}
		
		// Validation fields
		public function get MessageError():String
		{
			return m_sMessageError;
		}
		
		// Default format
		static public var DEFAULT:String = "{" +
			"\"type\":\"component\"," +
			"\"componenttype\":\"PROMPT\"," +
			"\"id\":0," +
			"\"note\":\"\"," +
			"\"message\":\"\"}";
		
		// Validation errors
		protected var m_sMessageError:String = "";
	}
}
