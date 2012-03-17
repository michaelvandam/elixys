package Elixys.JSON.Components
{
	import Elixys.JSON.JSONObject;
	
	import flash.utils.flash_proxy;
	
	public class ComponentMove extends ComponentBase
	{
		// Constructor
		public function ComponentMove(data:String = null, existingcontent:Object = null)
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
			return "MOVE";
		}
		public static function get SKINUP():Class
		{
			return tools_move_up;
		}
		public static function get SKINDOWN():Class
		{
			return tools_move_down;
		}
		public static function get SKINDISABLED():Class
		{
			return tools_move_disabled;
		}
		public static function get SKINACTIVE():Class
		{
			return tools_move_up;
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

		public function get Position():String
		{
			return super.flash_proxy::getProperty("position");
		}
		public function set Position(value:String):void
		{
			super.flash_proxy::setProperty("position", value);
		}

		public function get PositionValidation():String
		{
			return super.flash_proxy::getProperty("positionvalidation");
		}

		// Format additional component details
		protected override function FormatComponentDetails():String
		{
			var sMoveDetails:String = JSONDataObject("reactor", Reactor);
			sMoveDetails += JSONDataString("position", Position, false);
			return sMoveDetails;
		}

		// Default format
		static public var DEFAULT:String = "{" +
			"\"type\":\"component\"," +
			"\"componenttype\":\"MOVE\"," +
			"\"id\":0," +
			"\"name\":\"Move\"," +
			"\"reactor\":0," +
			"\"position\":0}";
	}
}
