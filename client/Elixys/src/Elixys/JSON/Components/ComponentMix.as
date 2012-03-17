package Elixys.JSON.Components
{
	import Elixys.JSON.JSONObject;
	
	import flash.utils.flash_proxy;
	
	public class ComponentMix extends ComponentBase
	{
		// Constructor
		public function ComponentMix(data:String = null, existingcontent:Object = null)
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
			return "MIX";
		}
		public static function get SKINUP():Class
		{
			return tools_mix_up;
		}
		public static function get SKINDOWN():Class
		{
			return tools_mix_down;
		}
		public static function get SKINDISABLED():Class
		{
			return tools_mix_disabled;
		}
		public static function get SKINACTIVE():Class
		{
			return tools_mix_up;
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
		
		public function get MixTime():uint
		{
			return super.flash_proxy::getProperty("mixtime");
		}
		public function set MixTime(value:uint):void
		{
			super.flash_proxy::setProperty("mixtime", value);
		}

		public function get MixTimeValidation():String
		{
			return super.flash_proxy::getProperty("mixtimevalidation");
		}
	
		public function get StirSpeed():uint
		{
			return super.flash_proxy::getProperty("stirspeed");
		}
		public function set StirSpeed(value:uint):void
		{
			super.flash_proxy::setProperty("stirspeed", value);
		}
	
		public function get StirSpeedValidation():String
		{
			return super.flash_proxy::getProperty("stirespeedvalidation");
		}

		// Format additional component details
		protected override function FormatComponentDetails():String
		{
			var sMixDetails:String = JSONDataObject("reactor", Reactor);
			sMixDetails += JSONDataObject("mixtime", MixTime);
			sMixDetails += JSONDataObject("stirspeed", StirSpeed, false);
			return sMixDetails;
		}

		// Default format
		static public var DEFAULT:String = "{" +
			"\"type\":\"component\"," +
			"\"componenttype\":\"MIX\"," +
			"\"id\":0," +
			"\"name\":\"Mix\"," +
			"\"reactor\":0," +
			"\"mixtime\":0," + 
			"\"stirspeed\":0}";
	}
}
