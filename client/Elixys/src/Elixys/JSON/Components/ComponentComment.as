package Elixys.JSON.Components
{
	import Elixys.JSON.JSONObject;
	
	import flash.utils.flash_proxy;
	
	public class ComponentComment extends ComponentBase
	{
		// Constructor
		public function ComponentComment(data:String = null, existingcontent:Object = null)
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
			return "COMMENT";
		}
		public static function get SKINUP():Class
		{
			return tools_comment_up;
		}
		public static function get SKINDOWN():Class
		{
			return tools_comment_down;
		}
		public static function get SKINDISABLED():Class
		{
			return tools_comment_disabled;
		}
		public static function get SKINACTIVE():Class
		{
			return tools_comment_active;
		}

		// Data wrappers
		public function get Comment():String
		{
			return super.flash_proxy::getProperty("comment");
		}
		public function set Comment(value:String):void
		{
			super.flash_proxy::setProperty("comment", value);
		}
		
		public function get CommentValidation():String
		{
			return super.flash_proxy::getProperty("commentvalidation");
		}

		// Format additional component details
		protected override function FormatComponentDetails():String
		{
			return JSONDataString("comment", Comment, false);
		}

		// Default format
		static public var DEFAULT:String = "{" +
			"\"type\":\"component\"," +
			"\"componenttype\":\"COMMENT\"," +
			"\"id\":0," +
			"\"name\":\"Comment\"," +
			"\"comment\":\"\"}";
	}
}
