package Elixys.JSON.Components
{
	import Elixys.JSON.JSONObject;
	
	import flash.utils.flash_proxy;
	
	public class ComponentSummary extends ComponentBase
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
			if ((ComponentType != null) && (ComponentType != COMPONENTTYPE))
			{
				throw new Error("State object mismatch");
			}
		}

		// Static component type and skins
		public static function get COMPONENTTYPE():String
		{
			return "SUMMARY";
		}
		public static function get SKINUP():Class
		{
			return tools_summary_up;
		}
		public static function get SKINDOWN():Class
		{
			return tools_summary_down;
		}
		public static function get SKINDISABLED():Class
		{
			return tools_summary_disabled;
		}
		public static function get SKINACTIVE():Class
		{
			return tools_summary_active;
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

		// Default format
		static public var DEFAULT:String = "{}";
	}
}
