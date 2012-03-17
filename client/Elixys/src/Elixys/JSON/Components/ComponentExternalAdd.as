package Elixys.JSON.Components
{
	import Elixys.JSON.JSONObject;
	
	import flash.utils.flash_proxy;
	
	public class ComponentExternalAdd extends ComponentBase
	{
		// Constructor
		public function ComponentExternalAdd(data:String = null, existingcontent:Object = null)
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
			return "EXTERNALADD";
		}
		public static function get SKINUP():Class
		{
			return tools_externalAdd_up;
		}
		public static function get SKINDOWN():Class
		{
			return tools_externalAdd_down;
		}
		public static function get SKINDISABLED():Class
		{
			return tools_externalAdd_disabled;
		}
		public static function get SKINACTIVE():Class
		{
			return tools_externalAdd_up;
		}

		// Data wrappers
		public function get Reactor():uint
		{
			return super.flash_proxy::getProperty("reactor");
		}
		public function set Reactor(value:uint):void
		{
			super.flash_proxy::setProperty("reactor", value);
		}
				
		public function get ReactorValidation():String
		{
			return super.flash_proxy::getProperty("reactorvalidation");
		}

		public function get ReagentName():String
		{
			return super.flash_proxy::getProperty("reagentname");
		}
		public function set ReagentName(value:String):void
		{
			super.flash_proxy::setProperty("reagentname", value);
		}
		
		public function get ReagentNameValidation():String
		{
			return super.flash_proxy::getProperty("reagentnamevalidation");
		}
		
		// Format additional component details
		protected override function FormatComponentDetails():String
		{
			var sExternalAddDetails:String = JSONDataObject("reactor", Reactor);
			sExternalAddDetails += JSONDataString("reagentname", ReagentName, false);
			return sExternalAddDetails;
		}

		// Default format
		static public var DEFAULT:String = "{" +
			"\"type\":\"component\"," +
			"\"componenttype\":\"EXTERNALADD\"," +
			"\"id\":0," +
			"\"name\":\"External Add\"," +
			"\"reactor\":0," +
			"\"reagentname\":\"\"}";
	}
}
